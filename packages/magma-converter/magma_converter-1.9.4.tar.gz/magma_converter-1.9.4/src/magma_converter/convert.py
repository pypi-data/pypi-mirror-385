from typing import Any, Dict, List, Self

import pandas as pd
from magma_database.database import init, migrate

from .database import DatabaseConverter
from .plot import PlotSeismogram
from .sds import SDS
from .search import Search
from .utilities import validate_date


class Convert(Search):
    def __init__(
        self,
        input_dir: str,
        directory_structure: str,
        network: str = "*",
        station: str = "*",
        channel: str = "*",
        location: str = "*",
        output_directory: str = None,
        min_completeness: float = 70,
        save_to_database: bool = True,
        plot_seismogram: bool = True,
        plot_type: str = "dayplot",
        force: bool = False,
        check_file_integrity: bool = True,
    ):
        """Seismic convert class

        Convert CVGHM various seismic data structure into Seiscomp Data Structure (SDS)

        Args:
            input_dir (str): input directory path
            directory_structure (str): input directory structure
            network (str): input network name
            station (str): input station name
            channel (str): input channel name
            min_completeness (float): minimum data completeness
            location (str): input location name
            save_to_database (bool, optional): if to save to database. Defaults to True.
            plot_seismogram (bool, optional): if to plot the seismogram plots. Defaults to True.
            plot_type (str, optional): type of plot. Defaults to 'dayplot'.
            force (bool, optional): force to overwrite file and plot. Defaults to False.
            check_file_integrity (bool, optional): check file integrity. Will try to fix some broken files.
        """

        super().__init__(
            input_dir=input_dir,
            directory_structure=directory_structure,
            network=network,
            station=station,
            channel=channel,
            location=location,
            check_file_integrity=check_file_integrity,
        )

        """Init database"""
        init(verbose=False)

        self.min_completeness = min_completeness
        self.output_dir = output_directory
        self.new_channel: str | None = None
        self.success: list[Dict[str, Any]] = []
        self.failed: list[Dict[str, Any]] = []

        self.dates: pd.DatetimeIndex | None = None

        self.save_to_database = save_to_database
        if save_to_database is True:
            DatabaseConverter.check_tables()

        self.plot_seismogram = plot_seismogram
        self.plot_type = plot_type
        self.force: bool = force
        self._plot_gaps: bool = False

        self.station_ids: List[int] = []
        self.sds_ids: List[int] = []

        print(f"ℹ️ Input Directory : {input_dir}")
        print(f"ℹ️ Output Directory : {output_directory}")
        print(f"ℹ️ Minimum completeness : {min_completeness}%")
        print(f"ℹ️ Save to database : {save_to_database}")
        print(f"ℹ️ Plot Seismogram/Type : {plot_seismogram}/{plot_type}")

        if check_file_integrity is True:
            print("ℹ️ Check file integrity : On")

        self.overwrite(force_overwrite=force)

    def plot_gaps(self, plot_gaps: True) -> Self:
        """Plot seismogram with gaps.

        This method will take a lot of time to process.
        """
        self._plot_gaps = plot_gaps
        return self

    def overwrite(self, force_overwrite: bool = False) -> Self:
        """Force overwrite file and plot."""
        self.force = force_overwrite
        if force_overwrite is True:
            print("⚠️ Overwrite file : True")
        return self

    def between_dates(self, start_date: str, end_date: str) -> Self:
        """Convert seismic between two range of dates.

        Args:
            start_date (str): start date in yyyy-mm-dd
            end_date (str): end date in yyyy-mm-dd

        Returns:
            Self
        """
        validate_date(start_date)
        validate_date(end_date)

        self.dates: pd.DatetimeIndex = pd.date_range(start_date, end_date)

        return self

    def run(self) -> Self:
        """Run converter.

        Returns:
            Self
        """
        assert isinstance(
            self.dates, pd.DatetimeIndex
        ), "Please set start and end date using between_dates() method."

        for _date in self.dates:
            date_str: str = _date.strftime("%Y-%m-%d")

            # Update self.success and self.failed
            self._run(date_str)

        return self

    def _run(self, date_str: str, **kwargs) -> None:
        """Convert for specific date.

        Args:
            date_str (str): Date format in yyyy-mm-dd
            **kwargs (dict): Keyword arguments save in Obspy

        Returns:
            None
        """
        print(f"⌛ {date_str} :: Converting...")
        min_completeness = self.min_completeness
        stream = self.search(date_str)
        for trace in stream:

            if trace.stats.channel[0] not in ["M", "O"]:
                sds: SDS = SDS(
                    output_dir=self.output_dir,
                    directory_structure=self.directory_structure,
                    trace=trace,
                    date_str=date_str,
                    channel=self.channel,
                    station=self.station,
                    location=self.location,
                    network=self.network,
                    force=self.force,
                )

                if sds.save(min_completeness=min_completeness, **kwargs) is True:
                    self.success.append(sds.results)

                    file_exists: bool = sds.results["file_exists"]

                    if (self.plot_seismogram is True) and (file_exists is False):
                        PlotSeismogram(
                            sds=sds, plot_type=self.plot_type
                        ).plot_with_gaps(plot_gaps=self._plot_gaps).save()

                    if self.save_to_database is True:
                        station_id: int = DatabaseConverter.update_station(
                            station=sds.stations
                        )
                        sds_id: int = DatabaseConverter.update_sds(sds=sds.results)
                        self.station_ids.append(station_id)
                        self.sds_ids.append(sds_id)
                        print(
                            f"💽 {date_str} :: Database updated. Station id: {station_id}. SDS id: {sds_id}"
                        )

                else:
                    self.failed.append(sds.results)

        print(f"✅ {date_str} :: Done!")
        print(f"======================")

    def fix_channel_to(self, new_channel: str) -> Self:
        """Fix channel name

        Args:
            new_channel (str): new channel name

        Returns:
            Self: Convert class
        """
        self.new_channel = new_channel
        return self

    def reset_database(self, reset_db: bool = False) -> Self:
        """Empty database. Use with caution."""
        if reset_db is True:
            migrate(force=reset_db)
        return self
