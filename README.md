Python NTP Client
-----

## Install

`pip3 install git+https://github.com/miyahan/ntp_clinet.git`


## Usage

```Python
from miyahan.ntp_client import NtpClient
ntp = NtpClient('time.google.com')
print(ntp.transmit_ts)
```


## License

These codes are licensed under CC0.

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)