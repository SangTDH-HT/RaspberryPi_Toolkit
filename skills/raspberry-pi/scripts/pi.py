#!/usr/bin/env python3
"""Chạy một lệnh shell trên Raspberry Pi qua SSH, in kết quả, trả về mã thoát của lệnh.

    python pi.py 'uptime; systemctl is-active wayvnc'
    PI_PW=... python pi.py 'sudo systemctl restart wayvnc'

Lệnh chạy bằng bash trên Pi. Có chữ "sudo" thì mật khẩu được đưa cho sudo qua
SUDO_ASKPASS (file tạm 700, xoá khi xong), nên `echo x | sudo tee file` vẫn chạy
đúng vì sudo không đọc mật khẩu từ stdin. stdin của lệnh luôn là /dev/null.
"""
import argparse
import shlex
import sys

import pilib

SUDO_WRAP = r"""IFS= read -r __PI_PW
export __PI_PW
__PI_ASK=$(mktemp)
trap 'rm -f "$__PI_ASK"' EXIT
cat > "$__PI_ASK" <<'EOF'
#!/bin/sh
printf '%s\n' "$__PI_PW"
EOF
chmod 700 "$__PI_ASK"
export SUDO_ASKPASS="$__PI_ASK"
sudo() { command sudo -A "$@"; }
export -f sudo
exec </dev/null
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    pilib.add_common_args(ap)
    ap.add_argument("--timeout", type=float, default=600, help="giây chờ lệnh (mặc định 600)")
    ap.add_argument("command", help="lệnh bash chạy trên Pi (đặt trong nháy đơn)")
    args = ap.parse_args()

    cfg = pilib.load_config(args)
    client = pilib.connect(cfg)

    pw = pilib.password() if "sudo" in args.command else None
    script = (SUDO_WRAP if pw else "exec </dev/null\n") + args.command
    stdin, stdout, stderr = client.exec_command("bash -c " + shlex.quote(script), timeout=args.timeout)
    if pw:
        stdin.write(pw + "\n")
        stdin.flush()
    stdin.channel.shutdown_write()

    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    code = stdout.channel.recv_exit_status()
    client.close()

    pilib.write_out(out)
    if err.strip():
        pilib.write_out("--- stderr ---\n" + err)
    sys.exit(code)


if __name__ == "__main__":
    main()
