"""
GUI factory for Kiwistron IP configuration.
This module builds a Tkinter UI but keeps most logic in core.py for testability.
The GUI is configurable via DEFAULT_UI_CONFIG and parameters to GuiFactory.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Callable
from .core import SerialManager, NetworkScanner, StreamInfo

DEFAULT_UI_CONFIG: Dict[str, Any] = {
    "title": "Kiwistron IP Setup",
    "geometry": "550x400",
    "resizable": (False, False),
    "labels": {
        "com_port": "Select COM Port:",
        "wifi_network": "Select Wi-Fi Network:",
        "wifi_password": "Wi-Fi Password:",
        "status": "Status:",
        "ip_address": "IP Address:",
        "live_url": "Live Stream URL:"
    }
}

class GuiFactory:
    """
    Build and run the configurable Tkinter GUI.
    The class keeps the SerialManager and NetworkScanner accessible for programmatic control.
    """

    def __init__(self, ui_config: Optional[Dict[str, Any]] = None):
        self.ui_config = ui_config or DEFAULT_UI_CONFIG
        self.root = tk.Tk()
        self.root.title(self.ui_config.get("title", "Kiwistron IP Setup"))
        geom = self.ui_config.get("geometry")
        if geom:
            self.root.geometry(geom)
        res = self.ui_config.get("resizable", (False, False))
        self.root.resizable(*res)

        # Core components
        self.serial = SerialManager()
        self.scanner = NetworkScanner()

        # Tk variables
        self.selected_network = tk.StringVar(self.root)
        self.password_var = tk.StringVar(self.root)
        self.com_var = tk.StringVar(self.root)
        self.status_var = tk.StringVar(self.root)
        self.ip_var = tk.StringVar(self.root)
        self.stream_url_var = tk.StringVar(self.root)

        # Build UI
        self._build_ui()
        # connect core callbacks
        self.serial.line_callback = self._on_serial_line

    # ---------- UI building ----------
    def _build_ui(self):
        frame = tk.Frame(self.root, padx=10, pady=10, relief="groove", bd=2)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        labels = self.ui_config.get("labels", {})

        # COM Port
        tk.Label(frame, text=labels.get("com_port", "Select COM Port:")).grid(row=0, column=0, sticky="w")
        self.com_dropdown = ttk.Combobox(frame, textvariable=self.com_var, width=25, state="readonly")
        self.com_dropdown.grid(row=0, column=1)
        btn_refresh = tk.Button(frame, text="Refresh", command=self.list_com_ports)
        btn_refresh.grid(row=0, column=2)
        btn_connect = tk.Button(frame, text="Connect COM", command=self.connect_serial)
        btn_connect.grid(row=0, column=3)

        # Wi-Fi Selection
        tk.Label(frame, text=labels.get("wifi_network", "Select Wi-Fi Network:")).grid(row=1, column=0, sticky="w", pady=10)
        self.net_dropdown = ttk.Combobox(frame, textvariable=self.selected_network, width=25, state="readonly")
        self.net_dropdown.grid(row=1, column=1, columnspan=2)
        self.btn_scan = tk.Button(frame, text="Scan Networks", command=self.start_scan, state="disabled")
        self.btn_scan.grid(row=1, column=3)

        # Password
        tk.Label(frame, text=labels.get("wifi_password", "Wi-Fi Password:")).grid(row=2, column=0, sticky="w")
        password_entry = ttk.Entry(frame, textvariable=self.password_var, width=25, show="*")
        password_entry.grid(row=2, column=1, columnspan=2)
        # Manual Connect Button
        self.btn_connect_wifi = tk.Button(frame, text="Connect to Wi-Fi", command=self.connect_to_wifi, state="disabled")
        self.btn_connect_wifi.grid(row=2, column=3)

        # Status and IP
        tk.Label(frame, text=labels.get("status", "Status:")).grid(row=3, column=0, sticky="w", pady=10)
        tk.Label(frame, textvariable=self.status_var, fg="blue").grid(row=3, column=1, columnspan=3, sticky="w")

        tk.Label(frame, text=labels.get("ip_address", "IP Address:")).grid(row=4, column=0, sticky="w")
        tk.Label(frame, textvariable=self.ip_var, fg="green").grid(row=4, column=1, columnspan=2, sticky="w")
        btn_copy_ip = tk.Button(frame, text="Copy IP", command=self.copy_ip)
        btn_copy_ip.grid(row=4, column=3, sticky="w", padx=2)

        # Live Stream URL
        tk.Label(frame, text=labels.get("live_url", "Live Stream URL:")).grid(row=5, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.stream_url_var, width=35, state="readonly").grid(row=5, column=1, columnspan=2)
        btn_copy_url = tk.Button(frame, text="Copy URL", command=self.copy_stream_url)
        btn_copy_url.grid(row=5, column=3, sticky="w", padx=2)

        # populate ports initially
        self.list_com_ports()

    # ---------- Actions ----------
    def list_com_ports(self):
        ports = self.serial.list_ports()
        self.com_dropdown['values'] = ports
        if ports:
            self.com_dropdown.current(0)
            self.com_var.set(ports[0])

    def connect_serial(self):
        port = self.com_var.get()
        if not port:
            messagebox.showerror("Error", "Select a COM port!")
            return
        try:
            self.serial.open(port)
            self.status_var.set(f"Connected to {port}")
            self.btn_scan.config(state="normal")
            self.btn_connect_wifi.config(state="normal")
        except Exception as exc:
            messagebox.showerror("Error", f"Cannot open {port}\n{exc}")

    def _on_serial_line(self, line: str):
        # feed into scanner for parsing
        evt, payload = self.scanner.parse_line(line)
        # update GUI responsively
        if evt == "network_found":
            # update dropdown - ensure values set on main thread
            current = list(self.net_dropdown['values'])
            if payload not in current:
                current.append(payload)
                self.net_dropdown['values'] = current
        elif evt == "ip_found":
            self.ip_var.set(self.scanner.stream_info.ip or "")
            self.stream_url_var.set(self.scanner.stream_info.stream_url or "")
            self.status_var.set(f"IP: {payload}")
        else:
            # other line -> show as status for short time
            self.status_var.set(payload)

    def start_scan(self):
        # clear list and send trigger through serial
        self.net_dropdown['values'] = []
        self.selected_network.set("")
        if self.serial.is_open():
            self.serial.write_line("")  # send newline to trigger device scan

    def connect_to_wifi(self):
        if not self.serial.is_open():
            messagebox.showerror("Error", "Serial port not open.")
            return
        network = self.selected_network.get()
        if network not in self.scanner.networks:
            messagebox.showerror("Error", "Select a valid network from dropdown!")
            return
        idx = self.scanner.networks.index(network)
        # send index & password
        self.serial.write_line(str(idx))
        self.serial.write_line(self.password_var.get())
        self.status_var.set("Connecting...")

    def copy_ip(self):
        ip = self.ip_var.get()
        if ip:
            self.root.clipboard_clear()
            self.root.clipboard_append(ip)
            messagebox.showinfo("Copied", f"IP address copied: {ip}")

    def copy_stream_url(self):
        url = self.stream_url_var.get()
        if url:
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            messagebox.showinfo("Copied", f"Live stream URL copied: {url}")

    # ---------- Running ----------
    def mainloop(self):
        self.root.mainloop()

    def run(self):
        """Shortcut to start the GUI loop."""
        self.mainloop()
