#!/usr/bin/env python3
"""Hỏi VNC server trên Pi đang mở những kiểu đăng nhập (security type) nào.

    python vnc_types.py            # máy trong pi.json, cổng 5900
    python vnc_types.py --port 5901

Chỉ bắt tay RFB tới bước liệt kê kiểu rồi ngắt — không đăng nhập, không cần mật khẩu.
"""
import argparse
import socket

import pilib

NAMES = {1: "None", 2: "VNC password", 5: "RSA-AES (RA2)", 6: "RSA-AES không mã hoá (RA2ne)",
         16: "Tight", 19: "VeNCrypt", 30: "Apple ARD", 129: "RSA-AES-256", 130: "RSA-AES-256 không mã hoá"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    pilib.add_common_args(ap)
    ap.add_argument("--port", type=int, default=5900)
    args = ap.parse_args()
    host = pilib.load_config(args)["host"]

    with socket.create_connection((host, args.port), timeout=5) as s:
        version = s.recv(12)
        s.sendall(b"RFB 003.008\n")
        n = s.recv(1)[0]
        types = list(s.recv(n))
    print(f"{host}:{args.port} {version.decode().strip()}")
    for t in types:
        print(f"  {t:>3}  {NAMES.get(t, '?')}")
    if not {6, 30} & set(types):
        print("Trang web noVNC (pi-screen) cần 30 hoặc 6 → thiếu relax_encryption=true trong /etc/wayvnc/config.")


if __name__ == "__main__":
    main()
