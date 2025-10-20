import os
from datetime import datetime
from typing import Any, Dict, Self, Tuple

import numpy as np
import pandas as pd
from obspy import Stream, Trace, read

from .new_trace import NewTrace


class SDS(NewTrace):
    """The basic directory and file layout is defined as:
    <SDS dir>/Year/NET/STA/CHAN.TYPE/NET.STA.LOC.CHAN.TYPE.YEAR.DAY

    Structure:

        SDS dir 	:  arbitrary base directory
        YEAR 	:  4 digit year
        NET 	:  Network code/identifier, up to 8 characters, no spaces
        STA 	:  Station code/identifier, up to 8 characters, no spaces
        CHAN 	:  Channel code/identifier, up to 8 characters, no spaces
        TYPE 	:  1 characters indicating the data type, recommended types are:
                    'D' - Waveform data
                    'E' - Detection data
                    'L' - Log data
                    'T' - Timing data
                    'C' - Calibration data
                    'R' - Response data
                    'O' - Opaque data
        LOC 	:  Location identifier, up to 8 characters, no spaces
        DAY 	:  3 digit day of year, padded with zeros

    The dots, '.', in the file names must always be present regardless if
    neighboring fields are empty.

    Additional data type flags may be used for extended structure definition
    """

    def __init__(
        self,
        trace: Trace,
        directory_structure: str = None,
        output_dir: str = None,
        date_str: str = None,
        station: str = None,
        channel: str = None,
        network: str = "VG",
        location: str = "00",
        force: bool = False,
    ):

        channel = None if channel == "*" else channel
        station = None if station == "*" else station
        location = "00" if location == "*" else location
        network = "VG" if network == "*" else network

        super().__init__(
            trace,
            directory_structure=directory_structure,
            station=station,
            channel=channel,
            network=network,
            location=location,
        )

        self._results = None
        self.converted_dir = output_dir

        if output_dir is None:
            output_dir = os.path.join(os.getcwd())
            self.converted_dir = output_dir

        output_dir = os.path.join(output_dir, "Converted", "SDS")
        os.makedirs(output_dir, exist_ok=True)

        self.output_dir: str = output_dir

        if date_str is None:
            date_str = trace.stats.starttime.strftime("%Y-%m-%d")
        self.date_str: str = date_str

        self.date_obj: datetime = datetime.strptime(self.date_str, "%Y-%m-%d")
        self.julian_date: str = self.date_obj.strftime("%j")
        self.file_exists: bool = False
        self._force = force

    @property
    def structure(self) -> Dict[str, str]:
        """The basic structure directory and file layout is defined as:
        <SDS dir>/Year/NET/STA/CHAN.TYPE/NET.STA.LOC.CHAN.TYPE.YEAR.DAY

        :return: :class:`Dict[str, str]`
        """
        return dict(
            year=self.trace.stats.starttime.strftime("%Y"),
            network=self.trace.stats.network,
            station=self.trace.stats.station,
            channel=self.trace.stats.channel,
            type="D",
            location=self.trace.stats.location,
            julian_date=self.julian_date,
        )

    @property
    def stations(self) -> Dict[str, Any]:
        """Returns station information to save on database.

        Returns:
            Dict[str, Any]
        """
        nslc: str = f"{self.network}.{self.station}.{self.location}.{self.channel}"
        stations: Dict[str, Any] = {
            "nslc": nslc,
            "network": self.network,
            "station": self.station,
            "channel": self.channel,
            "location": self.location,
        }

        return stations

    @property
    def filename(self) -> str:
        """Returns the trace filename

        :return: :class:`str`
        """
        return ".".join(
            [
                self.structure["network"],
                self.structure["station"],
                self.structure["location"],
                self.structure["channel"],
                self.structure["type"],
                self.structure["year"],
                self.structure["julian_date"],
            ]
        )

    @property
    def path(self) -> str:
        """Returns the relative SDS path

        :return: :class:`str`
        """
        return os.path.join(
            self.output_dir,
            self.structure["year"],
            self.structure["network"],
            self.structure["station"],
            self.structure["channel"] + "." + self.structure["type"],
        )

    @property
    def relative_path(self) -> str:
        """Returns the relative SDS path

        :return: :class:`str`
        """
        return os.path.join(
            self.structure["year"],
            self.structure["network"],
            self.structure["station"],
            self.structure["channel"] + "." + self.structure["type"],
        )

    @property
    def full_path(self) -> str:
        """Returns full path of the trace file

        :return: :class:`str`
        """
        return os.path.join(self.output_dir, self.path, self.filename)

    @property
    def directories(self) -> Tuple[str, str, str, str]:
        """Returns the full path of the SDS directory

        :return: a tuple of string of filename, path, and full_path
        :rtype: (string, string, string)
        """
        return self.filename, self.path, self.full_path, self.relative_path

    @property
    def results(self) -> dict[str, Any]:
        """Get the metadata of the trace.

        Returns:
            dict[str, Any]: Metadata.
        """
        return self._results

    @results.setter
    def results(self, file_location: str = None) -> None:
        """Set the metadata of the new trace.

        Args:
            file_location (str): The location of the trace file
        """
        self._results: dict[str, Any] = dict(
            nslc=self.trace.id,
            date=self.trace.stats.starttime.strftime("%Y-%m-%d"),
            start_time=self.trace.stats.starttime.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=self.trace.stats.endtime.strftime("%Y-%m-%d %H:%M:%S"),
            sampling_rate=self.trace.stats.sampling_rate,
            completeness=self.completeness,
            file_location=file_location,
            relative_path=os.path.join(self.relative_path, self.filename),
            file_exists=self.file_exists,
            file_size=(
                os.stat(file_location).st_size if file_location is not None else None
            ),
        )

    @staticmethod
    def revalidate(
        sds_directory: str,
        station: str,
        channel: str,
        output_directory: str,
        start_date: str,
        end_date: str,
        station_type: str = "D",
        network: str = "VG",
        location: str = "00",
    ) -> None:
        """Revalidate seismic file from existing SDS.

        Args:
            sds_directory (str): The location of the SDS directory
            station (str): The station code
            channel (str): The channel code
            output_directory (str): The output directory
            start_date (str): The start date
            end_date (str): The end date
            station_type (str): Channel type. Default to 'D'
            network (str): The network code. Default to 'VG'
            location (str): The location code.

        Returns:
            None
        """

        dates: pd.DatetimeIndex = pd.date_range(start_date, end_date, freq="D")

        for date_obj in dates:
            date_str = date_obj.strftime("%Y-%m-%d")
            julian_date = date_obj.strftime("%j")
            year = date_obj.strftime("%Y")

            nslc = f"{network}.{station}.{location}.{channel}"
            filename: str = f"{nslc}.{station_type}.{year}.{julian_date}"
            mseed_file = os.path.join(
                sds_directory,
                year,
                network,
                station,
                f"{channel}.{station_type}",
                filename,
            )

            if os.path.exists(mseed_file):
                try:
                    print(f"⌛ {date_str} :: Validating {mseed_file}")
                    stream: Stream = read(mseed_file, format="MSEED")

                    if len(stream) > 0:
                        for trace in stream:
                            trace.data = trace.data.clip(-2e30, 2e30)
                            trace.data = trace.data.astype(np.int32)
                        stream = stream.merge(fill_value=0)

                    sds = SDS(
                        trace=stream[0],
                        output_dir=output_directory,
                        directory_structure="sds",
                        force=True,
                    )
                    if sds.save(min_completeness=5, encoding=3) is True:
                        print(f"✅ {date_str} :: Done!\n" f"======================")

                except Exception as e:
                    print(f"⛔ {date_str} :: Failed to read {mseed_file} : {e}")
            else:
                print(f"⛔ {date_str} :: {mseed_file} Not found")

    def save(
        self, min_completeness: float = 70.0, encoding: str | int = "STEIM2", **kwargs
    ) -> bool:
        """Save into SDS

        Args:
            encoding (str|int): encoding type. Default STEIM2
            min_completeness (float): minimum completeness value to be saved

        Returns:
            Self: Convert class
        """
        self.results = None

        if (os.path.isfile(self.full_path)) and (self._force is False):
            print(
                f"✅ {self.date_str} :: {self.trace.id} already exists: {self.full_path}"
            )
            self.file_exists = True
            self.results = self.full_path
            return True

        if self.completeness > min_completeness:
            os.makedirs(os.path.join(self.output_dir, self.path), exist_ok=True)

            try:
                self.trace.write(
                    self.full_path, format="MSEED", encoding=encoding, **kwargs
                )
                self.results = self.full_path
                print(
                    f"✅ {self.date_str} :: {self.trace.id} completeness: {self.completeness:.2f}% ➡️ {self.full_path}"
                )
                return True
            except Exception as e:
                print(f"⛔ {e}")
                return False

        print(
            f"⛔ {self.date_str} :: {self.trace.id} Not saved. Trace completeness "
            f"{self.completeness:.2f}%! Below {min_completeness}%"
        )
        return False
