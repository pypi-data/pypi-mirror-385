# Installation

``` pip install libfcast ```

# Usage

Send message:
```
import fcast

fc = fcast.FCastSession(<IP/Host>)
fc.connect()
fc.send(fcast.message.Ping())
```

Handle received messages:
```
import fcast

def callback(msg: fcast.message.Message):
	<do stuff>

fc = fcast.FCastSession(<IP/Host>)
fc.connect()
fc.subscribe((fcast.message.Ping, callback))
fc.receive()	
```

Run receive loop in a separate thread:
```
import fcast
from threading import Thread

def callback(msg: fcast.message.Message):
    <do stuff>

fc = fcast.FCastSession(<IP/Host>)
fc.connect()
fc.subscribe((fcast.message.Ping,callback))
recv_thread = Thread(target=fc.receive)
recv_thread.start()
<do other stuff>
fc.disconnect()
recv_thread.join()
```
