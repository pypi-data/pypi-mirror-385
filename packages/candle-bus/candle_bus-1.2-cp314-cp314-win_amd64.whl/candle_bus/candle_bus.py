#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""candle_bus.py
Time    :   2022/10/19
Author  :   song 
Version :   1.0
Contact :   zhaosongy@126.com
License :   (C)Copyright 2022, robottime / robodyno

Candle Interface as Python Can plugin
"""

import can
import candle_driver

class CandleBus(can.BusABC):
    def __init__(self, channel, bitrate, can_filters=None, **kwargs,):
        """Init Candle Bus with channel and bitrate
        
        Args:
            channel: candle device index, e.g. 'can0'
            bitrate: CAN network bandwidth (bits/s)
            can_filters: not suupported
        """
        try:
            channel_id = int(channel.replace('can', ''))
            self._device = candle_driver.list_devices()[channel_id]
            self._channel = self._device.channel(0)
        except:
            raise IOError('Failed to find candle device[{}].'.format(channel))
        try:
            self._device.open()
            self._channel.set_bitrate(bitrate)
            self._channel.start()
        except:
            raise RuntimeError('Failed to connect to candle device.')

        super().__init__(channel=channel, can_filters=can_filters, **kwargs)

    def send(self, msg, timeout = None):
        """Transmit a message to th CAN bus.
        
        Args:
            msg: A message object
            timeout: not supported
        """
        can_id = msg.arbitration_id

        if msg.is_extended_id:
            can_id = can_id | candle_driver.CANDLE_ID_EXTENDED

        if msg.is_remote_frame:
            can_id = can_id | candle_driver.CANDLE_ID_RTR

        if msg.is_error_frame:
            can_id = can_id | candle_driver.CANDLE_ID_ERR

        try:
            self._channel.write(can_id, bytes(msg.data))
        except:
            raise RuntimeError("The message could not be sent")

    def _recv_internal(self, timeout):
        """Read a message from the bus and tell whether it was filtered.
        
        Args:
            timeout: seconds to wait for a message.
        
        Returns:
            1.  a message that was read or None on timeout
            2.  a bool that is True if message filtering has already
                been done and else False
        """
        timeout_ms = round(timeout * 1000) if timeout else 0
        frame_type, frame_id, data, extended, timestamp = self._channel.read(timeout_ms)
        if frame_type == candle_driver.CANDLE_FRAMETYPE_RECEIVE:
            msg = can.Message(
                timestamp=timestamp,
                arbitration_id=frame_id,
                is_extended_id=extended,
                is_remote_frame=frame_id & candle_driver.CANDLE_ID_RTR,
                is_error_frame=frame_id & candle_driver.CANDLE_ID_ERR,
                channel=self.channel_info,
                dlc=len(data),
                data=data,
                is_fd=False,
            )
            return msg, False
        else:
            return None, False

    def shutdown(self):
        super().shutdown()
        self._channel.stop()
        self._device.close()
