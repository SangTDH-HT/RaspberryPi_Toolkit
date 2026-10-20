#!/usr/bin/env python3
"""Chụp từng màn hình đang cắm vào Pi (desktop Wayland/labwc) và tải ảnh về.

    python pi_shot.py               # ảnh về ./pi-shots
    python pi_shot.py D:/anh-pi     # ảnh về thư mục khác

In ra đường dẫn từng ảnh PNG (mỗi màn một ảnh, đặt theo tên cổng HDMI-A-1...).
Cần gói grim và wlr-randr trên Pi (Raspberry Pi OS bản desktop có sẵn).
Màn đang tắt (swayidle/wlopm) thì grim vẫn chụp được nội dung desktop.
"""
import argparse
import os
import shlex
import sys

import pilib

LIST_AND_SHOOT = r"""set -e
export XDG_RUNTIME_DIR=/run/user/$(id -u)
sock=$(ls "$XDG_RUNTIME_DIR" | grep -E '^wayland-[0-9]+$' | head -n 1)
[ -n "$sock" ] || { echo "KHONG_CO_WAYLAND"; exit 3; }
export WAYLAND_DISPLAY=$sock
dir=$(mktemp -d /tmp/pi-shot.XXXXXX)
for out in $(wlr-randr | grep -E '^[^ ]' | cut -d' ' -f1); do
  grim -o "$out" "$dir/$out.png" && echo "$dir/$out.png"
done
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    pilib.add_common_args(ap)
    ap.add_argument("dest", nargs="?", default="pi-shots", help="thư mục lưu ảnh (mặc định ./pi-shots)")
    args = ap.parse_args()

    client = pilib.connect(pilib.load_config(args))
    _, stdout, stderr = client.exec_command("bash -c " + shlex.quote(LIST_AND_SHOOT), timeout=60)
    remote = [line.strip() for line in stdout.read().decode().splitlines() if line.strip()]
    code = stdout.channel.recv_exit_status()
    if code or not remote or remote == ["KHONG_CO_WAYLAND"]:
        sys.exit("Không chụp được: chưa có phiên desktop Wayland đang chạy, hoặc thiếu grim/wlr-randr.\n"
                 + stderr.read().decode("utf-8", "replace"))

    os.makedirs(args.dest, exist_ok=True)
    sftp = client.open_sftp()
    for path in remote:
        local = os.path.join(args.dest, os.path.basename(path))
        sftp.get(path, local)
        print(os.path.abspath(local))
    client.exec_command("rm -rf " + shlex.quote(os.path.dirname(remote[0])))
    sftp.close()
    client.close()


if __name__ == "__main__":
    main()
