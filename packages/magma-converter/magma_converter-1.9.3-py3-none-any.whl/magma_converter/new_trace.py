import numpy as np
from obspy import Trace


def fix_station(trace: Trace, station: str = None) -> str:
    """Fix station name.

    Args:
        trace (Trace): Trace to fix.
        station (str): Station name.

    Returns:
        str: Station name.
    """
    if station is not None:
        return station

    if trace.stats.station:
        return trace.stats.station


def fix_channel(
    trace: Trace, channel: str = None, directory_structure: str = None
) -> str:
    """Get name and fix channel name.

    Args:
        trace (Trace): Trace to fix.
        channel (str): Channel name.
        directory_structure (str): Directory structure.

    Returns:
        str: Fixed channel name.
    """
    if channel is not None:
        return channel

    if directory_structure == "sds":
        return trace.stats.channel

    if len(trace.stats.channel) == 3:
        if "EH" in trace.stats.channel:
            return trace.stats.channel

        if "HH" in trace.stats.channel:
            return trace.stats.channel

    # For Ijen
    if directory_structure == "ijen":
        if "BH" in trace.stats.channel:
            return "BH{}".format(trace.stats.location)
        return trace.stats.channel + trace.stats.location

    if "Z" in trace.stats.location:
        return "EHZ"
    if "Z" in trace.stats.channel:
        return "EHZ"
    if "N" in trace.stats.channel:
        return "EHN"
    if "E" in trace.stats.channel:
        return "EHE"
    # if self.structure_type == 'win_sinabung':
    #     stations = config['type']['win_sinabung']['stations']
    #     return stations[self.trace.stats.channel]['channel']
    return "EHZ"


class NewTrace:
    def __init__(
        self,
        trace: Trace,
        directory_structure: str = None,
        station: str = None,
        channel: str = None,
        network: str = "VG",
        location: str = "00",
    ):
        """Set a new trace

        Args:
            trace (Trace): trace
            directory_structure (str): Directory structure
            station (str): station code
            channel (str): channel code
            network (str): network code. VG as default
            location (str): location code. 00 as default
        """
        self.directory_structure = directory_structure
        self.station = fix_station(trace, station).upper()
        self.channel = fix_channel(trace, channel, directory_structure).upper()
        self.network = network.upper()
        self.location = location.upper()
        self.trace = self.new_trace(trace)

    def new_trace(self, trace: Trace) -> Trace:
        """Fix trace.

        Args:
            trace (Trace): trace

        Returns:
            Trace
        """
        # Clipping amplitude
        # trace.data = trace.data.clip(-2e30, 2e30)
        trace.data = np.where(trace.data == -(2**31), 0, trace.data)
        trace.data = trace.data.astype(np.int32)
        trace.stats["station"] = self.station
        trace.stats["network"] = self.network
        trace.stats["channel"] = self.channel
        trace.stats["location"] = self.location

        return trace

    @property
    def completeness(self) -> float:
        """Get the non-zero values of completeness of the new trace.

        Returns:
            float: Completeness of the trace.
        """
        return (np.count_nonzero(self.trace.data) / 8640000) * 100
