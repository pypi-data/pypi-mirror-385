# Candle Interface as Python Can plugin

A plugin developed for [python-can](https://python-can.readthedocs.io/en/3.3.4/interfaces/socketcan.html) with [candle-driver](https://github.com/chemicstry/candle_driver)

## Install
`pip install candle-bus`

## Usage
```python
import can
bus = can.interface.Bus(bitrate=1000000, bustype='candle')

# send
msg = can.Message(arbitration_id=0x202, data=[0,1,2,3,4,5,6,7])
bus.send(msg)

#receive
message = bus.recv()
```