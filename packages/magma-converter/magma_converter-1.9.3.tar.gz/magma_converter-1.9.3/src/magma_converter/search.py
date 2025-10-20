import glob
import os
from datetime import datetime, timedelta
from typing import List, Tuple

from obspy import Stream, UTCDateTime, read
from obspy.clients.filesystem.sds import Client

from .utilities import (directory_structures_group, trimming_trace,
                        validate_directory_structure)


class Search:
    def __init__(
        self,
        input_dir: str,
        directory_structure: str,
        network: str = "*",
        station: str = "*",
        channel: str = "*",
        location: str = "*",
        check_file_integrity: bool = True,
    ):
        """Search sesimic files and return as daily seismic Stream

        Args:
            input_dir (str): input directory path
            directory_structure (str): input directory structure
            network (str): input network name
            station (str): input station name
            channel (str): input channel name
            location (str): input location name
            check_file_integrity (bool, optional): check file integrity. Defaults to False.
        """
        self.input_dir = input_dir
        self.directory_structure = (
            validate_directory_structure(directory_structure)
            if directory_structure != "sds"
            else directory_structure
        )
        self.network = network
        self.station = station
        self.channel = channel
        self.location = location
        self.select = {
            "network": network,
            "station": station,
            "location": location,
            "channel": channel,
        }
        self.check_file_integrity = check_file_integrity

    def rename_error_file(
        self,
        error_file: str,
        prefix: str = "ERROR",
        channel: str = None,
        input_dir: str = None,
    ) -> None:
        """Rename error file by adding ERROR prefix

        Args:
            error_file (str): error file path
            prefix (str, optional): error file prefix. Defaults to 'ERROR'.
            channel (str, optional): channel name. Defaults to None.
            input_dir (str, optional): input directory path. Defaults to None.
        """
        basedir: str = os.path.dirname(error_file)
        basename: str = os.path.basename(error_file)

        file_error = f"{prefix}_{basename}"
        if channel is not None:
            file_error = file_error.replace(".", "__")

        if input_dir is not None:
            _basedir: str = self.input_dir

        fix_file: str = os.path.join(basedir, file_error)

        os.rename(error_file, fix_file)
        print(f"⚠️➡️ {error_file} -> {fix_file}")

    def read_from_list(self, seismic_files: List[str]) -> tuple[Stream, List[str]]:
        """Read seismic stream from list of files.

        Args:
            seismic_files (List[str]): list of seismic file

        Returns:
            Tuple[Stream, List[str]]: Stream and list of error files.
        """
        stream = Stream()
        error_files: List[str] = []
        for seismic_file in seismic_files:
            try:
                temp_stream: Stream = read(seismic_file)
                _stream = temp_stream.select(**self.select)
                stream = stream + _stream
            except:
                error_files.append(seismic_file)
                continue
        return stream, error_files

    @staticmethod
    def merged(stream: Stream, date_str: str) -> Stream:
        """Merging seismic data into daily seismic data.

        Args:
            stream (Stream): Stream object
            date_str (str): Date in yyyy-mm-dd format

        Returns:
            Stream: Stream object
        """
        start_time: UTCDateTime = UTCDateTime(date_str)
        end_time: UTCDateTime = UTCDateTime(f"{date_str}T23:59:59")
        return trimming_trace(stream, start_time, end_time)

    def sac(self, date_str: str) -> Stream:
        """Read SAC data structure.

        <earthworm_dir>/ContinuousSAC/YYYYMM/YYYYMMDD_HHMM00_MAN/<per_channel>

        Args:
            date_str (str): Date format in yyyy-mm-dd

        Returns:
            Stream: Stream object
        """
        import warnings

        warnings.filterwarnings("error")

        channels: List[str] = [self.channel]
        if (self.channel == "*") or (self.channel is None):
            channels: List[str] = ["E", "H", "B"]

        _date_str: str = date_str.replace("-", "")
        _date_str = f"{_date_str}*"
        yyyy_mm: str = _date_str[0:6]

        stream: Stream = Stream()

        for channel in channels:
            seismic_dir: str = os.path.join(
                self.input_dir, yyyy_mm, _date_str, f"*.{channel}*"
            )
            seismic_files: List[str] = glob.glob(seismic_dir)
            if len(seismic_files) > 0:
                _stream, error_files = self.read_from_list(seismic_files)
                if len(error_files) > 0:
                    print(
                        f"⛔ {date_str} - self.sac() :: Cannot read {len(error_files)} file(s)"
                    )
                    for error_file in error_files:
                        self.rename_error_file(error_file, channel=channel)
                if len(_stream) > 0:
                    stream.append(_stream)

        return stream

    def seisan(self, date_str: str) -> Stream:
        """Read seisan data structure.

        <earthworm_dir>/Continuous/YYYY-MM-DD-hhmm-00S.MAN__<nunber_of_channels>

        Example data per 10 minutes:
            <earthworm_dir>/Continuous/2021-12-04-1620-00S.MAN___003
            <earthworm_dir>/Continuous/2021-12-04-1630-00S.MAN___003

        Args:
            date_str (str): Date format in yyyy-mm-dd

        Returns:
            Stream: Stream object
        """
        import warnings

        warnings.filterwarnings("error")

        wildcard: str = "{}*".format(date_str)
        seismic_dir: str = os.path.join(self.input_dir, wildcard)
        seismic_files: List[str] = glob.glob(seismic_dir)

        if len(seismic_files) > 0:
            stream, error_files = self.read_from_list(seismic_files)
            if len(error_files) > 0:
                print(
                    f"⛔ {date_str} - self.seisan() :: Cannot read {len(error_files)} file(s)"
                )
                for error_file in error_files:
                    self.rename_error_file(error_file)
            return stream

        return Stream()

    def dieng(self, date_str: str) -> Stream:
        """Read dieng data structure.

        Dieng has 2 format: Seisan and SAC
        1. SAC from 2013-08-12 to 2021-09-15
        2. Seisan from 2021-03-26 to 2023-10-16
        3. SAC 2023-10-16 to 2024-08-15

        Args:
            date_str (str): Date format in yyyy-mm-dd

        Returns:
            Stream: Stream object
        """
        current_date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        sac_dates = [
            ["2013-08-12", "2021-03-25"],
            ["2023-10-16", "2024-08-15"],
        ]

        seisan_dates = [
            ["2023-10-16", "2024-08-15"],
        ]

        for sac_date in sac_dates:
            start_date = datetime.strptime(sac_date[0], "%Y-%m-%d")
            end_date = datetime.strptime(sac_date[1], "%Y-%m-%d")
            if current_date_obj <= start_date <= end_date:
                stream: Stream = self.sac(date_str)
                return stream

        for seisan_date in seisan_dates:
            start_date = datetime.strptime(seisan_date[0], "%Y-%m-%d")
            end_date = datetime.strptime(seisan_date[1], "%Y-%m-%d")
            if current_date_obj <= start_date <= end_date:
                stream: Stream = self.seisan(date_str)
                return stream

        stream: Stream = self.sac(date_str)
        return stream

    def ijen(self, date_str: str) -> Stream:
        """Read Ijen seismic directory

        <seismic_dir>/YYYY/YYYYMMDD/Set00/<per_channel>

        Args:
            date_str (str): Date format in yyyy-mm-dd

        Returns:
            Stream: Stream object
        """
        input_dir = self.input_dir
        stream = Stream()

        current_day_obj = datetime.strptime(date_str, "%Y-%m-%d")
        current_year: str = current_day_obj.strftime("%Y")
        current_yyyymmdd: str = current_day_obj.strftime("%Y%m%d")

        _seismic_dir: str = os.path.join(input_dir, current_year, current_yyyymmdd)

        if os.path.exists(_seismic_dir):
            seismic_dir: str = os.path.join(_seismic_dir, "*", "{}*".format(date_str))
            seismic_files: List[str] = glob.glob(seismic_dir)

            if len(seismic_files) > 0:
                stream, error_files = self.read_from_list(seismic_files)
                if len(error_files) > 0:
                    print(
                        f"⛔ {date_str} - self.ijen() :: Cannot read {len(error_files)} file(s)"
                    )
                    for error_file in error_files:
                        self.rename_error_file(error_file)

        if stream.count() > 0:
            next_day_obj = current_day_obj + timedelta(days=1)
            next_day_year: str = next_day_obj.strftime("%Y")
            next_day_yyyymmdd: str = next_day_obj.strftime("%Y%m%d")

            _seismic_dir: str = os.path.join(
                input_dir,
                next_day_year,
                next_day_yyyymmdd,
                "*",
                "{}-2350-*".format(date_str),
            )
            _seismic_files: List[str] = glob.glob(_seismic_dir)

            if len(_seismic_files) > 0:
                _stream, _error_files = self.read_from_list(_seismic_files)
                if len(_error_files) > 0:
                    print(
                        f"⛔ {date_str} - self.ijen() :: Cannot read {len(_error_files)} file(s)"
                    )
                    for error_file in _error_files:
                        self.rename_error_file(error_file)
                stream: Stream = stream + _stream

        return stream

    def idds(self, date_str: str) -> Stream:
        """Search seismic data based on IDDS format.

        <seismic_dir>/YEAR/NET/STA/CHAN.TYPE/DAY/NET.STA.LOC.CHAN.TYPE.YEAR.DAY.HOUR

        Args:
            date_str (str): Date format in yyyy-mm-dd

        Returns:
            Stream: Stream object
        """
        input_dir = self.input_dir

        date_obj: datetime = datetime.strptime(date_str, "%Y-%m-%d")
        year: str = date_obj.strftime("%Y")
        julian_day: str = date_obj.strftime("%j")

        seismic_dir: str = os.path.join(
            input_dir, year, "*", self.station, "*", julian_day, "*"
        )
        seismic_files: List[str] = glob.glob(seismic_dir)

        if len(seismic_files) > 0:
            stream, error_files = self.read_from_list(seismic_files)
            if len(error_files) > 0:
                print(
                    f"⛔ {date_str} - self.idds() :: Cannot read {len(error_files)} file(s)"
                )
                for error_file in error_files:
                    self.rename_error_file(error_file)
            return stream

        return Stream()

    def sds(self, date_str: str) -> Stream:
        """Read SDS Data structure

        Args:
            date_str: Date string in yyyy-mm-dd

        Returns:
            Stream: Stream object
        """
        start_time: UTCDateTime = UTCDateTime(f"{date_str}T00:00:00")
        end_time: UTCDateTime = UTCDateTime(f"{date_str}T23:59:59")

        client = Client(sds_root=self.input_dir)
        stream: Stream = client.get_waveforms(
            station=self.station,
            channel=self.channel,
            network=self.network,
            location=self.location,
            starttime=start_time,
            endtime=end_time,
        )

        if len(stream) > 0:
            return stream

        return Stream()

    def search(self, date_str: str) -> Stream:
        """Search seismic data structure.

        Args:
            date_str (str): Date format in yyyy-mm-d

        Returns:
            Stream: Stream object
        """
        stream: Stream = Stream()
        directory_structure: str = self.directory_structure.lower()

        if directory_structure == "sds":
            stream = self.sds(date_str)
            return stream

        if (
            directory_structure == "ijen"
            or directory_structure in directory_structures_group["ijen"]
        ):
            stream = self.ijen(date_str)

        if (
            directory_structure == "dieng"
            or directory_structure in directory_structures_group["dieng"]
        ):
            stream = self.dieng(date_str)

        if directory_structure == "idds" or directory_structure in ["idds"]:
            stream = self.idds(date_str)

        if (
            directory_structure == "seisan"
            or directory_structure in directory_structures_group["seisan"]
        ):
            stream = self.seisan(date_str)

        if (
            directory_structure == "sac"
            or directory_structure in directory_structures_group["sac"]
        ):
            stream = self.sac(date_str)

        print(f"👍 {date_str} :: Total {stream.count()} traces found.")

        return self.merged(stream, date_str)
