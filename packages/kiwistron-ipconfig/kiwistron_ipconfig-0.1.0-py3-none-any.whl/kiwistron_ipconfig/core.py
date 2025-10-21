"""
Core serial handling and parsing logic for Kiwistron IP configuration.
This module intentionally contains no GUI code so it can be used headless.
"""

from typing import Callable, List, Optional
import serial
import serial.tools.list_ports
import threading
import re

class StreamInfo:
    """Simple container for discovered IP/stream URL."""
    def __init__(self, ip: Optional[str] = None, stream_url: Optional[str] = None):
        self.ip = ip
        self.stream_url = stream_url

class SerialManager:
    """
    Manages a serial.Serial instance and reading thread.
    Provide a callback to receive lines: callback(line: str).
    """
    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, timeout: float = 0.1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._ser: Optional[serial.Serial] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self.line_callback: Optional[Callable[[str], None]] = None

    def list_ports(self) -> List[str]:
        return [p.device for p in serial.tools.list_ports.comports()]

    def open(self, port: str):
        self.close()
        self._ser = serial.Serial(port, self.baudrate, timeout=self.timeout)
        self.port = port
        self._start_reader()

    def close(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.2)
        if self._ser and self._ser.is_open:
            try:
                self._ser.close()
            except Exception:
                pass
        self._ser = None
        self._thread = None

    def is_open(self) -> bool:
        return bool(self._ser and self._ser.is_open)

    def write_line(self, text: str):
        if self.is_open():
            if not text.endswith("\n"):
                text = text + "\n"
            self._ser.write(text.encode())

    def _start_reader(self):
        if not self._ser:
            return
        self._running = True
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def _reader_loop(self):
        buffer = ""
        while self._running and self._ser and self._ser.is_open:
            try:
                if self._ser.in_waiting:
                    ch = self._ser.read().decode(errors="ignore")
                    buffer += ch
                    if ch == "\n":
                        line = buffer.strip()
                        buffer = ""
                        if line and self.line_callback:
                            try:
                                self.line_callback(line)
                            except Exception:
                                # swallow callback exceptions
                                pass
            except Exception:
                # keep loop alive in case of intermittent serial errors
                pass

class NetworkScanner:
    """
    Helper that accepts serial lines and extracts networks and IP info.
    Use NetworkScanner.parse_line(line) to feed incoming lines.
    """
    IP_RE = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})")
    def __init__(self):
        self.networks: List[str] = []
        self.stream_info = StreamInfo()

    def parse_line(self, line: str):
        """
        Inspect line for network list patterns and ip addresses.
        Returns:
            tuple(event_type, payload)
            event_type can be: "network_found", "ip_found", "other"
        """
        # Example network line pattern: "[1] MyWifiSSID (RSSI -50)" or similar
        if "[" in line and "]" in line and "(" in line:
            # crude extraction - take text between ] and (
            try:
                net_name = line.split("]")[1].split("(")[0].strip()
            except Exception:
                net_name = line
            if net_name and net_name not in self.networks:
                self.networks.append(net_name)
                return ("network_found", net_name)
            return ("other", line)

        if "IP address:" in line or "IP:" in line:
            m = self.IP_RE.search(line)
            if m:
                ip_addr = m.group(1)
                self.stream_info.ip = ip_addr
                self.stream_info.stream_url = f"http://{ip_addr}:81/stream"
                return ("ip_found", ip_addr)
        # fallback: detect any plain ip in line
        m = self.IP_RE.search(line)
        if m:
            ip_addr = m.group(1)
            self.stream_info.ip = ip_addr
            self.stream_info.stream_url = f"http://{ip_addr}:81/stream"
            return ("ip_found", ip_addr)

        return ("other", line)
