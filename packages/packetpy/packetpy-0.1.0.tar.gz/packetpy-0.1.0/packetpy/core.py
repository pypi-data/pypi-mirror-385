import socket, struct, time, threading
from typing import Dict, Any, Optional

# --- Helpers ---------------------------------------------------------------
def ipv4_addr_raw(x: bytes) -> str:
    return '.'.join(str(b) for b in x)

def hexdump(src: bytes, length:int=16) -> str:
    lines=[]
    for i in range(0,len(src),length):
        chunk=src[i:i+length]
        hex_bytes=' '.join(f'{b:02x}' for b in chunk)
        ascii=''.join((chr(b) if 32<=b<127 else '.') for b in chunk)
        lines.append(f'{i:04x}  {hex_bytes:<{length*3}}  {ascii}')
    return '\n'.join(lines)

# --- Simple parsers (IPv4 -> TCP/UDP) -------------------------------------
def parse_ipv4(pkt: bytes) -> Dict[str,Any]:
    if len(pkt) < 20:
        raise ValueError("truncated_ipv4")
    v_ihl, tos, total_len, ident, flags_frag, ttl, proto, chksum, src, dst = struct.unpack('!BBHHHBBH4s4s', pkt[:20])
    ihl = (v_ihl & 0x0F) * 4
    total_len = min(total_len, len(pkt))
    payload = pkt[ihl:total_len]
    return {'version': v_ihl >> 4, 'ihl': ihl, 'len': total_len, 'proto': proto,
            'src': ipv4_addr_raw(src), 'dst': ipv4_addr_raw(dst), 'payload': payload}

def parse_tcp(seg: bytes) -> Dict[str,Any]:
    if len(seg) < 20:
        raise ValueError("trunc_tcp")
    srcp,dstp,seq,ack,off_flags,win,chks,urg = struct.unpack('!HHLLHHHH', seg[:20])
    offset = (off_flags >> 12) * 4
    offset = max(20, offset)
    payload = seg[offset:]
    return {'src_port':srcp,'dst_port':dstp,'seq':seq,'ack':ack,'offset':offset,'payload':payload}

def parse_udp(seg: bytes) -> Dict[str,Any]:
    if len(seg) < 8:
        raise ValueError("trunc_udp")
    srcp,dstp,length,chksum = struct.unpack('!HHHH', seg[:8])
    length = min(length, len(seg))
    payload = seg[8:length]
    return {'src_port':srcp,'dst_port':dstp,'len':length,'payload':payload}

# ---------------------------------------------------------------------------
## WinRawSniffer Class
# ---------------------------------------------------------------------------
class WinRawSniffer:
    def __init__(self, iface_ip: Optional[str] = None, timeout: Optional[int] = None):
        self.iface_ip = iface_ip or socket.gethostbyname(socket.gethostname())
        self.sock = None
        self.running = False
        self.thread = None
        self.timeout = timeout
        self.match_found = False

    def _create_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        s.bind((self.iface_ip, 0))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        s.settimeout(1.0)
        return s

    def start(self, callback):
        s = self._create_socket()
        try:
            s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        except Exception as e:
            s.close()
            raise RuntimeError(f"Could not enable RCVALL: {e}")

        self.sock = s
        self.running = True
        self.match_found = False

        def loop():
            start_time = time.time()
            while self.running:
                if self.timeout and (time.time() - start_time) > self.timeout:
                    self.running = False
                    break
                try:
                    data, addr = self.sock.recvfrom(65535)
                except (socket.timeout, OSError):
                    continue
                pkt = {'raw_ip': data}
                try:
                    ip = parse_ipv4(data)
                    pkt['ipv4'] = ip
                    if ip.get('proto') == 6:
                        try: pkt['tcp'] = parse_tcp(ip['payload'])
                        except: pass
                    elif ip.get('proto') == 17:
                        try: pkt['udp'] = parse_udp(ip['payload'])
                        except: pass
                except Exception as e:
                    pkt['parse_err'] = str(e)
                try:
                    callback(pkt)
                except Exception:
                    pass
            print("[Thread] Sniffing loop finished.")

        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            try: self.sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            except: pass
            try: self.sock.close()
            except: pass
            self.sock = None
        if self.thread and threading.current_thread() != self.thread:
            self.thread.join(timeout=1.0)
        self.thread = None

# ---------------------------------------------------------------------------
## Callback Factory
# ---------------------------------------------------------------------------
def make_match_callback(sniffer: WinRawSniffer, target_ip: str, target_port: int):
    def callback(pkt: Dict[str,Any]):
        if 'ipv4' not in pkt: return
        ip = pkt['ipv4']
        if ip.get('dst') != target_ip: return

        is_match = False
        proto_str = None
        if 'tcp' in pkt and pkt['tcp'].get('dst_port') == target_port:
            is_match = True; proto_str = "TCP"
        elif 'udp' in pkt and pkt['udp'].get('dst_port') == target_port:
            is_match = True; proto_str = "UDP"

        if is_match:
            print(f"\n=== MATCH FOUND ({proto_str}) ===")
            print(pkt)
            payload = pkt[proto_str.lower()]['payload']
            print(f"\n{proto_str} payload hexdump (first 512 bytes):")
            print(hexdump(payload[:512]))
            sniffer.match_found = True
            sniffer.running = False
    return callback
