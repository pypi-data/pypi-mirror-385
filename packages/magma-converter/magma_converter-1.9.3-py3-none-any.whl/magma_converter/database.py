import datetime
import os
import time
from typing import Any, List, Self

import numpy as np
import pandas as pd
from magma_database import Sds, Station, Volcano
from magma_database.database import db
from obspy import Trace, read
from obspy.clients.filesystem.sds import Client
from tqdm.notebook import tqdm


class DatabaseConverter:
    def __init__(self, sds_results: List[dict[str, Any]]):
        """
        sds_results: SDS success results
            examples:
            {'nslc': 'VG.INFR.00.EHZ',
              'date': '2018-01-01',
              'start_time': '2018-01-01 00:00:00',
              'end_time': '2018-01-01 23:59:59',
              'sampling_rate': 100.0,
              'completeness': 99.99770833333334,
              'file_location': 'L:\\converted\\SDS\\2018\\VG\\INFR\\EHZ.D\\VG.INFR.00.EHZ.D.2018.001',
              'file_size': 1024, # In byte
              }

        Args:
            sds_results: SDS success results. Can be accessed through SDS `results` property
        """
        self.sds_results = sds_results
        self.station_ids: List[int] = []
        self.sds_ids: List[int] = []

    @staticmethod
    def check_tables():
        db.connect(reuse_if_open=True)
        db.create_tables([Station, Sds, Volcano])
        if Volcano.select().count() == 0:
            Volcano.fill_database()
        db.close()

    @staticmethod
    def rescan_all_stations(
        sds_directory: str,
        start_date: str,
        end_date: str,
        quick_scan: bool = False,
        verbose: bool = False,
    ) -> None:
        """Rescan all stations and update database.

        Args:
            sds_directory (str): SDS root directory
            start_date: Start date.
            end_date: End date.
            quick_scan (bool, optional): Scan data availability without validate zero data. Defaults to False.:
            verbose (bool, optional): Print verbose output. Defaults to False.

        Returns:
            None
        """
        client = Client(sds_root=sds_directory)

        if verbose is True:
            print(f"🏃‍♂️‍➡️ Getting all stations information from {sds_directory}.")

        nslc_list = client.get_all_nslc()

        if verbose is True:
            print(f"🏃‍♂️‍➡️ Starting rescan for {len(nslc_list)} stations.")

        for nslc in tqdm(nslc_list):
            network, station, location, channel = nslc
            if "M" in channel:
                if verbose is True:
                    print(f"🐕‍🦺 Skipping {nslc}")
                continue
            results = DatabaseConverter.rescan(
                sds_directory=sds_directory,
                station=station,
                channel=channel,
                start_date=start_date,
                end_date=end_date,
                quick_scan=quick_scan,
                verbose=verbose,
            )

        print(f"🏁 Done.")

    @staticmethod
    def rescan(
        sds_directory: str,
        station: str,
        channel: str,
        start_date: str,
        end_date: str,
        network: str = "VG",
        location: str = "00",
        quick_scan: bool = False,
        verbose: bool = False,
    ) -> List[dict[str, Any]]:
        """Rescan SDS directory an update database.

        Args:
            sds_directory (str): SDS directory.
            station (str): Station name.
            channel (str): Channel name.
            start_date (str): Start date.
            end_date (str): End date.
            network (str, optional): Network name.
            location (str, optional): Location name.
            quick_scan (bool, optional): Scan data availability without validate zero data. Defaults to False.:
            verbose (bool, optional): Print detailed information. Default False.

        Returns:
            List[dict[str, Any]]

            Examples list of:
            -----------------
            {'nslc': 'VG.INFR.00.EHZ',
              'date': '2018-01-01',
              'start_time': '2018-01-01 00:00:00',
              'end_time': '2018-01-01 23:59:59',
              'sampling_rate': 100.0,
              'completeness': 99.99770833333334,
              'file_location': 'L:\\converted\\SDS\\2018\\VG\\INFR\\EHZ.D\\VG.INFR.00.EHZ.D.2018.001',
              'relative_path': '2018\\VG\\INFR\\EHZ.D\\VG.INFR.00.EHZ.D.2018.001',
              'file_size': 1024, # In byte
              }
        """

        sds_results: List[dict[str, Any]] = []

        dates: pd.DatetimeIndex = pd.date_range(start_date, end_date, freq="D")

        nslc: str = f"{network}.{station}.{location}.{channel}"

        __station: dict[str, Any] = {
            "nslc": nslc,
            "network": network,
            "station": station,
            "channel": channel,
            "location": location,
        }

        DatabaseConverter.check_tables()

        station_id = DatabaseConverter.update_station(station=__station)

        if verbose is True:
            print(f"📌 Station {nslc} updated : id={station_id}")

        for date_obj in dates:
            year = date_obj.strftime("%Y")
            julian_day = date_obj.strftime("%j")
            date_str = date_obj.strftime("%Y-%m-%d")

            filename: str = (
                f"{network}.{station}.{location}.{channel}.D.{year}.{julian_day}"
            )
            relative_path: str = os.path.join(
                year, network, station, f"{channel}.D", filename
            )
            file_location: str = os.path.join(sds_directory, relative_path)

            if os.path.exists(file_location):
                try:
                    stream = read(file_location, headonly=quick_scan)
                    if quick_scan is False and len(stream) > 1:
                        stream = stream.merge(fill_value=0)
                except Exception as e:
                    if verbose is True:
                        print(f"{e} : {file_location}")
                else:
                    npts = 0
                    trace: Trace = stream[0]
                    total_sample_per_day = trace.stats.sampling_rate * 60 * 60 * 24

                    if quick_scan is True:
                        for _tr in stream:
                            npts = _tr.stats.npts + npts
                    else:
                        npts = np.count_nonzero(trace.data)

                    completeness: float = (npts / total_sample_per_day) * 100

                    # Validate npts when completeness is more than 100%
                    if completeness > 100:
                        if verbose is True:
                            print(
                                f"⚠️ {trace.id} :: Completeness is {completeness}%. Trying to fix it."
                            )
                        stream = read(file_location)
                        stream = stream.merge(fill_value=0)
                        trace = stream[0]
                        completeness: float = (
                            np.count_nonzero(trace.data) / total_sample_per_day
                        ) * 100
                        if verbose is True:
                            print(
                                f"⚠️ {trace.id} :: New completeness: {completeness:.2f}%."
                            )

                    __sds: dict[str, Any] = {
                        "nslc": trace.id,
                        "date": date_str,
                        "start_time": trace.stats.starttime.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "end_time": trace.stats.endtime.strftime("%Y-%m-%d %H:%M:%S"),
                        "completeness": completeness,
                        "sampling_rate": trace.stats.sampling_rate,
                        "file_location": file_location,
                        "relative_path": relative_path,
                        "file_size": os.stat(file_location).st_size,
                    }

                    retries = 0
                    while retries <= 9:
                        try:
                            __sds["id"] = DatabaseConverter.update_sds(sds=__sds)
                            sds_results.append(__sds)
                            if verbose is True:
                                print(
                                    f"✅ {date_str} :: {nslc} {completeness}% ➡️ {file_location}"
                                )
                        except Exception as e:
                            if retries == 9:
                                ValueError(
                                    f"❌ Failed to connect to database. After 10 attempts."
                                )

                            print(
                                f"❌ Failed to connect to database. Attempt no {retries + 1}. Retry in 30s."
                            )
                            time.sleep(30)
                            retries += 1
                        else:
                            retries = 10

            else:
                if verbose is True:
                    print(f"⛔ {date_str} :: {nslc} Not exists ➡️ {file_location}")

        return sds_results

    @property
    def stations(self) -> List[dict[str, Any]]:
        _nslc: List[str] = []
        _stations: List[dict[str, Any]] = []

        for result in self.sds_results:
            nslc = result["nslc"]

            if nslc not in _nslc:
                network, station, channel, location = nslc.split(".")
                __stations: dict[str, Any] = {
                    "nslc": result["nslc"],
                    "network": network,
                    "station": station,
                    "channel": channel,
                    "location": location,
                }
                _nslc.append(nslc)
                _stations.append(__stations)

        return _stations

    @property
    def sds(self) -> List[dict[str, Any]]:
        """Map sds results to list of dict (collection)

        Returns:
            List[dict[str, Any]]
        """
        _sds: List[dict[str, Any]] = []

        for result in self.sds_results:
            __sds: dict[str, Any] = {
                "nslc": result["nslc"],
                "date": result["date"],
                "start_time": result["start_time"],
                "end_time": result["end_time"],
                "completeness": result["completeness"],
                "sampling_rate": result["sampling_rate"],
                "file_location": result["file_location"],
                "file_size": result["file_size"],
            }
            _sds.append(__sds)

        return _sds

    @staticmethod
    def update_station(station: dict[str, Any]) -> int:
        """Update stations table

        Args:
            station (dict[str, Any]): Station data

        Returns:
            int: id of the updated station
        """
        _station, created = Station.get_or_create(
            nslc=station["nslc"],
            defaults={
                "network": station["network"],
                "station": station["station"],
                "channel": station["channel"],
                "location": station["location"],
            },
        )

        station_id = _station.get_id()

        if created is True:
            return station_id

        _station.nslc = station["nslc"]
        _station.network = station["network"]
        _station.station = station["station"]
        _station.location = station["location"]
        _station.channel = station["channel"]
        _station.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)
        _station.save()

        return station_id

    @staticmethod
    def update_sds(sds: dict[str, Any]) -> int:
        """Update sds table.

        Args:
            sds: SDS success results. Can be accessed through SDS `results` property

        Returns:
            int: id of sds model
        """
        _sds, created = Sds.get_or_create(
            nslc=sds["nslc"],
            date=sds["date"],
            defaults={
                "start_time": sds["start_time"],
                "end_time": sds["end_time"],
                "sampling_rate": sds["sampling_rate"],
                "completeness": sds["completeness"],
                "file_location": sds["file_location"],
                "relative_path": sds["relative_path"],
                "file_size": sds["file_size"],
                "updated_at": datetime.datetime.now(tz=datetime.timezone.utc),
            },
        )

        sds_id = _sds.get_id()

        if created is True:
            return sds_id

        _sds.nslc = sds["nslc"]
        _sds.date = sds["date"]
        _sds.start_time = sds["start_time"]
        _sds.end_time = sds["end_time"]
        _sds.completeness = sds["completeness"]
        _sds.sampling_rate = sds["sampling_rate"]
        _sds.file_location = sds["file_location"]
        _sds.file_size = sds["file_size"]
        _sds.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)
        _sds.save()

        return sds_id

    def update(self) -> Self:
        """
        Bulk update:
        https://docs.peewee-orm.com/en/latest/peewee/querying.html#bulk-inserts

        Upsert:
        https://docs.peewee-orm.com/en/latest/peewee/querying.html#upsert

        Returns:
            Self
        """
        for station in self.stations:
            station_id: int = self.update_station(station)
            if station_id not in self.station_ids:
                self.station_ids.append(station_id)

        for sds in self.sds:
            sds_id: int = self.update_sds(sds)
            if sds_id not in self.sds_ids:
                self.sds_ids.append(sds_id)

        return self
