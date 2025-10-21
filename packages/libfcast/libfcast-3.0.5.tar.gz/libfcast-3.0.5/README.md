# Installation

``` pip install libfcast ```

# Usage

```
import fcast

def callback(msg: fcast.message.Message):
	<do stuff>

session = fcast.FCastSession(<IP/Host>)
session.connect()
session.subscribe((fcast.message.Ping, callback))
session.receive()	