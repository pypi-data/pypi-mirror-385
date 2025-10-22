# PyPacket

Windows raw packet sniffer (TCP/UDP) module.

## Example

## python
import pypacket

sniffer = pypacket.WinRawSniffer("192.168.1.1", timeout=10)
callback = pypacket.make_match_callback(sniffer, "8.8.8.8", 443)
sniffer.start(callback)
while sniffer.running:
    pass
sniffer.stop()
