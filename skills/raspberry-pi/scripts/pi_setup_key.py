#!/usr/bin/env python3
"""Cài khoá SSH của máy này lên Pi để lần sau khỏi gõ mật khẩu đăng nhập.

    python pi_setup_key.py --dry-run   # chỉ xem sẽ làm gì
    python pi_setup_key.py

Tạo ~/.ssh/id_ed25519 bằng ssh-keygen nếu chưa có, rồi thêm khoá công khai vào
~/.ssh/authorized_keys trên Pi (không thêm trùng). Đăng nhập lần này cần mật khẩu.
sudo trên Pi vẫn cần mật khẩu như cũ — script không đụng tới sudoers.
"""
import argparse
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pilib


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    pilib.add_common_args(ap)
    ap.add_argument("--dry-run", action="store_true", help="không tạo khoá, không ghi lên Pi")
    args = ap.parse_args()
    cfg = pilib.load_config(args)

    key = Path(cfg.get("key") or Path.home() / ".ssh" / "id_ed25519")
    pub = key.with_name(key.name + ".pub")
    if not pub.exists():
        if args.dry_run:
            print(f"[dry-run] sẽ tạo khoá {key}")
        else:
            if not shutil.which("ssh-keygen"):
                sys.exit("Không thấy ssh-keygen (Windows: Settings → Optional features → OpenSSH Client).")
            key.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(key),
                            "-C", f"pi-toolkit@{Path.home().name}"], check=True)
    pubkey = pub.read_text().strip() if pub.exists() else "<khoá mới>"

    client = pilib.connect(cfg)
    q = shlex.quote(pubkey)
    check = f"grep -qxF {q} ~/.ssh/authorized_keys 2>/dev/null && echo CO || echo CHUA"
    _, out, _ = client.exec_command(check)
    state = out.read().decode().strip()
    if state == "CO":
        print(f"Khoá {pub} đã có trên {cfg['user']}@{cfg['host']}.")
    elif args.dry_run:
        print(f"[dry-run] sẽ thêm {pub} vào ~/.ssh/authorized_keys của {cfg['user']}@{cfg['host']}")
    else:
        add = ("umask 077; mkdir -p ~/.ssh && touch ~/.ssh/authorized_keys && "
               f"printf '%s\\n' {q} >> ~/.ssh/authorized_keys && echo OK")
        _, out, err = client.exec_command(add)
        if out.read().decode().strip() != "OK":
            sys.exit("Ghi authorized_keys thất bại: " + err.read().decode())
        print(f"Đã thêm khoá. Thử: ssh {cfg['user']}@{cfg['host']}")
    client.close()


if __name__ == "__main__":
    main()
