import os
from typing import TYPE_CHECKING, Any, Dict, List, Self, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
from magma_database import Sds
from matplotlib import pyplot as plt
from obspy import Stream, Trace
from obspy.clients.filesystem.sds import Client
from pandas.errors import EmptyDataError
from PIL import Image
from plotly import graph_objects as go

from .plotly_calplot import calplot

if TYPE_CHECKING:
    from .sds import SDS

sns.set_style("whitegrid")


class PlotSeismogram:
    types: List[str] = ["normal", "dayplot", "relative", "section"]

    def __init__(self, sds: "SDS", plot_type: str = "dayplot"):
        """Plot daily seismogram

        Args:
            sds: SDS object
            plot_type: Plot type must be between 'normal', 'dayplot', 'relative', 'section'.
        """
        assert (
            type not in self.types
        ), f"Plot type must be between 'normal', 'dayplot', 'relative', 'section'."

        self.sds = sds
        self.completeness = sds.results["completeness"]
        self.trace: Trace = sds.trace
        self.sampling_rate = sds.results["sampling_rate"]
        self.date = sds.results["date"]
        self.filename: str = f"{sds.filename}.jpg"
        self.plot_type = plot_type
        self.plot_gaps: bool = False

        output_dir: str = os.path.dirname(sds.path).replace(
            "Converted\\SDS", "Seismogram"
        )
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir: str = output_dir

        thumbnail_dir: str = os.path.join(output_dir, "thumbnail")
        os.makedirs(thumbnail_dir, exist_ok=True)
        self.thumbnail_dir: str = thumbnail_dir

    def plot_with_gaps(self, plot_gaps: bool = False) -> Self:
        """Plot with gaps.

        Args:
            plot_gaps: Plot gaps between traces.

        Returns:
            Self: Plot with gaps.
        """
        self.plot_gaps = plot_gaps
        return self

    @property
    def title(self):
        """Plot title

        Returns:
            title (str)
        """
        return (
            f"{self.date} | {self.trace.id} | {self.sampling_rate} Hz | "
            f"{self.trace.stats.npts} samples ({self.completeness:.2f})%"
        )

    def thumbnail(self, seismogram: str) -> str:
        """Generate thumbnail of seismogram.

        Args:
            seismogram (str): Seismogram image path
        """
        outfile = os.path.join(self.thumbnail_dir, self.filename)

        image = Image.open(seismogram)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.thumbnail((320, 180))
        image.save(outfile)

        return outfile

    def replace_zeros_with_gaps(self, trace: Trace) -> Stream | Trace:
        """Replace zeros with gaps.

        Args:
            trace (Trace): Trace to replace zeros with gaps.

        Returns:
            Stream | Trace: Stream or trace with zeros replaced with gaps.
        """
        if self.plot_gaps is True:
            trace.data = np.ma.masked_equal(trace.data, 0)
            stream: Stream = trace.split()
            return stream

        return trace.split()

    @staticmethod
    def replot_from_sds(
        sds_directory: str,
        start_date: str,
        end_date: str,
    ) -> None:

        client = Client(sds_root=sds_directory)
        nslc_list = client.get_all_nslc()

        for nslc in nslc_list:
            network, station, location, channel = nslc

    def save(self) -> Tuple[str, str]:
        """Save plot to file.

        Returns:
            seismogram, thumbnail (str, str): seismogram_image_path (str), thumbnail_image_path (str)
        """
        seismogram = os.path.join(self.output_dir, self.filename)

        stream = self.replace_zeros_with_gaps(self.trace.copy())

        try:
            stream.plot(
                type="dayplot",
                interval=60,
                one_tick_per_line=True,
                color=["k"],
                outfile=seismogram,
                number_of_ticks=13,
                size=(1600, 900),
                title=self.title,
            )

            plt.close("all")

            thumbnail = self.thumbnail(seismogram)

            print(f"🏞️ {self.date} :: Seismogram saved to : {seismogram}")

            return seismogram, thumbnail
        except Exception as e:
            print(f"❌ Error save plot in: {seismogram}. {e}")


class PlotAvailability:
    def __init__(
        self,
        station: str,
        channel: str,
        network: str = "VG",
        location: str = "00",
    ):
        self.station: str = station
        self.channel: str = channel
        self.network: str = network
        self.location: str = location
        self.nslc: str = f"{network}.{station}.{location}.{channel}"
        self._df: pd.DataFrame = pd.DataFrame.from_records(self.sds_list, index="id")
        self.start_date: pd.Timestamp = self.df["date"].min()
        self.end_date: pd.Timestamp = self.df["date"].max()

    @property
    def unique_years(self) -> List[int]:
        """Get list of unique years

        Returns:
            List[int]
        """
        return list(self.df["date"].dt.year.unique())

    @property
    def df(self) -> pd.DataFrame:
        """Get plot dataframe

        Returns:
            pd.DataFrame
        """
        df = self._df
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values(by=["date"], inplace=True)
        return df

    @property
    def output_dir(self) -> str:
        """Output directory

        Returns:
            str
        """
        output_dir: str = os.path.join(os.getcwd(), "output", "figures")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    @property
    def sds_list(self) -> List[Dict[str, Any]]:
        """Get list of SDS from database

        Returns:
            List[Dict[str, Any]]
        """
        sds_list = []

        sds_dicts = Sds.select().where(Sds.nslc == self.nslc)
        _sds_list = [dict(sds_dict) for sds_dict in sds_dicts.dicts()]

        if len(_sds_list) == 0:
            raise EmptyDataError(
                f"⛔ No data for {self.nslc}. Check your station parameters."
            )

        for sds in _sds_list:
            _sds = {
                "id": sds["id"],
                "nslc": sds["nslc"],
                "date": str(sds["date"]),
                "start_time": str(sds["start_time"]),
                "end_time": str(sds["end_time"]),
                "completeness": float(sds["completeness"]),
                "sampling_rate": float(sds["sampling_rate"]),
                "file_location": sds["file_location"],
                "file_size": sds["file_size"],
                "created_at": str(sds["created_at"]),
                "updated_at": str(sds["updated_at"]),
            }
            sds_list.append(_sds)

        return sds_list

    @property
    def figure(self) -> go.Figure:
        """Plotly graph_object figure

        Returns:
            go.Figure
        """
        title = f"{self.nslc} {self.start_date}-{self.end_date}"

        figure: go.Figure = (
            calplot(
                data=self.df,
                x="date",
                y="completeness",
                colorscale=px.colors.diverging.RdYlGn,
            )
            .update_layout(
                self.axis,
                title=title,
            )
            .update_traces(
                showscale=True,
                selector=dict(type="heatmap"),
                zmax=100,
                zmin=0,
            )
        )

        return figure

    @property
    def axis(self) -> Dict[str, Dict[str, str]]:
        """Update all axis values

        Returns:
            Dict[str, Dict[str, str]]
        """
        axes = self.yaxis
        axes.update(self.xaxis)

        return axes

    @property
    def yaxis(self) -> Dict[str, Dict[str, str]]:
        """Set label for yaxis

        Returns:
            Dict[str, Dict[str, str]]
        """
        years = self.unique_years
        y_axes = {}

        for index, year in enumerate(years):
            key = "yaxis" if index == 0 else f"yaxis{index + 1}"
            y_axes[key] = {}
            y_axes[key]["title"] = f"{year}"

        return y_axes

    @property
    def xaxis(self) -> Dict[str, Dict[str, str]]:
        """Xaxis ticktext values

        Returns:
            Dict[str, Dict[str, str]]
        """
        years = self.unique_years
        ticktext = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sept",
            "Okt",
            "Nov",
            "Dec",
        ]
        x_axes = {}

        for index, year in enumerate(years):
            key = "xaxis" if index == 0 else f"xaxis{index + 1}"
            x_axes[key] = {}
            x_axes[key]["ticktext"] = ticktext

        return x_axes

    def filter(self, start_date: str, end_date: str) -> Self:
        """Filter data by start and end dates.

        Args:
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.

        Returns:
            Self
        """
        df = self.df
        self._df = df[(df["date"] > start_date) & (df["date"] < end_date)]
        self.start_date = start_date
        self.end_date = end_date
        return self

    def show(self) -> None:
        """Show figure

        Returns:
            None
        """
        self.figure.show()

    def save(self, filename: str = None, filetype: str = "jpg") -> bool:
        """Save figure

        Args:
            filename: Filename
            filetype: File type

        Returns:
            bool
        """
        if filename is None:
            start_date = self.start_date.strftime("%Y-%m-%d")
            end_date = self.end_date.strftime("%Y-%m-%d")
            filename = f"availability_{self.nslc}_{start_date}-{end_date}.{filetype}"

        filepath = os.path.join(self.output_dir, filename)

        try:
            self.figure.write_image(filepath)
            print(f"🏞️ Saved to: {filepath}")
            return True
        except Exception as e:
            print(f"⛔ {e}")
            return False
