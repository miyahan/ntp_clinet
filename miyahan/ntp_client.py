"""Python NTP Client module.

These codes are licensed under CC0.
http://creativecommons.org/publicdomain/zero/1.0/deed.ja
"""
from datetime import datetime
from math import modf
from socket import AF_INET
from socket import SOCK_DGRAM
from socket import socket
from struct import pack
from struct import unpack


class NtpClient(object):
    """Python NTP Client class."""

    LEAP_ATR = {
        0: "no warning",
        1: "last minute of the day has 61 seconds",
        2: "last minute of the day has 59 seconds",
        3: "unknown (clock unsynchronized)"
    }

    MODE_ATR = {
        0: "reserved",
        1: "symmetric active",
        2: "symmetric passive",
        3: "client",
        4: "server",
        5: "broadcast",
        6: "reserved for NTP control messages",
        7: "reserved for private use",
    }

    def _ntptime2datetime(self, int_val, fract_val):
        ntptime = int_val + fract_val / 4294967296
        return datetime.fromtimestamp(ntptime - 2208988800)

    def _datetime2ntptime(self, dt):
        ntp_ts_frac, ntp_ts_int = modf(dt.timestamp() + 2208988800)
        ntp_ts_frac = int(ntp_ts_frac * 4294967296)
        ntp_ts_int = int(ntp_ts_int)
        return ntp_ts_frac, ntp_ts_int

    def __init__(self, server, port=123):
        """NTP Client.

        :param str server: NTP server name (ex: 'ntp.nict.jp')
        :param int port: NTP server port (ex: 123)
        """
        """make request content."""
        own_ts_frac, own_ts_int = self._datetime2ntptime(datetime.now())
        ref_ts = pack(
            '!4B11I',
            int('11011011', 2),  # LI=11(unknown), VN=011(v3), MODE=011(client)
            0,  # Stratum
            0,  # Poll Interval
            0,  # Precision
            0,  # Root Delay
            0,  # Root Dispersion
            0,  # Reference Identifier
            0,  # Reference Timestamp (integer part)
            0,  # Reference Timestamp (fraction part)
            own_ts_int,  # Originate Timestamp (integer part)
            own_ts_frac,  # Originate Timestamp (fraction part)
            0,  # Receive Timestamp (integer part)
            0,  # Receive Timestamp (fraction part)
            own_ts_int,  # Transmit Timestamp (integer part)
            own_ts_frac,  # Transmit Timestamp (fraction part)
        )

        """send request to NTP server."""
        self.local_transmit_ts = datetime.now()
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.sendto(ref_ts, (server, port))
            response = s.recvfrom(1024)[0]
        self.local_recieve_ts = datetime.now()

        """parse response."""
        if response:
            unpk = unpack('!4B11I', response)
            first_oct = format(unpk[0], 'b').zfill(8)

            leap = int(first_oct[0:2], 2)
            self.leap_indicator = leap
            self.leap_indicator_atr = self.LEAP_ATR[leap] if leap in self.LEAP_ATR else 'unknown'
            self.version_number = int(first_oct[2:5], 2)
            mode = int(first_oct[5:8], 2)
            self.mode = mode
            self.mode_atr = self.MODE_ATR[mode] if mode in self.MODE_ATR else 'unknown'
            self.stratum = unpk[1]
            self.poll_interval = unpk[2]
            self.precision = unpk[3]
            self.root_delay = unpk[4]
            self.root_dispersion = unpk[5]
            self.reference_identifier = unpk[6]
            self.reference_ts = self._ntptime2datetime(unpk[7], unpk[8])
            self.originate_ts = self._ntptime2datetime(unpk[9], unpk[10])
            self.receive_ts = self._ntptime2datetime(unpk[11], unpk[12])
            self.transmit_ts = self._ntptime2datetime(unpk[13], unpk[14])
            self.rtt = (self.local_recieve_ts - self.local_transmit_ts).total_seconds() - (self.transmit_ts - self.receive_ts).total_seconds()
            self.offset = ((self.transmit_ts - self.local_recieve_ts).total_seconds() + (self.receive_ts - self.local_transmit_ts).total_seconds()) * 0.5
        else:
            None


if __name__ == '__main__':
    ntp = NtpClient('ntp.nict.jp')
    print('NTP: {}\nLOC: {} (rtt: {:.0f}ms, offset: {:.0f}ms)'.format(
        ntp.local_transmit_ts,
        ntp.transmit_ts,
        ntp.rtt * 1000,
        ntp.offset * 1000
    ))
