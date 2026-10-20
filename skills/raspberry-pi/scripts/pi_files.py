#!/usr/bin/env python3
"""Chép file giữa máy này và Pi qua SFTP.

    python pi_files.py get /tmp/a.png /home/pi/b.txt  ./tai-ve
    python pi_files.py put ./app.py ./style.css       /home/pi/app

Đối số cuối là THƯ MỤC đích. Chỉ chép file mà tài khoản SSH đọc/ghi được
(file của root thì chép ra /tmp bằng pi.py trước).
Trong Git Bash, đường dẫn bắt đầu bằng "/" bị đổi thành đường dẫn Windows:
đặt MSYS_NO_PATHCONV=1 trước lệnh.
"""
import argparse
import os
import posixpath

import pilib


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    pilib.add_common_args(ap)
    ap.add_argument("mode", choices=["get", "put"])
    ap.add_argument("paths", nargs="+", help="các file nguồn rồi tới thư mục đích")
    args = ap.parse_args()
    if len(args.paths) < 2:
        ap.error("cần ít nhất một file nguồn và một thư mục đích")
    *sources, dest = args.paths

    for p in sources if args.mode == "get" else [dest]:
        if ":/" in p or p.startswith("C:"):
            ap.error(f"'{p}' trông như đường dẫn Windows — Git Bash đã đổi nó? Đặt MSYS_NO_PATHCONV=1.")

    client = pilib.connect(pilib.load_config(args))
    sftp = client.open_sftp()
    if args.mode == "get":
        os.makedirs(dest, exist_ok=True)
        for remote in sources:
            local = os.path.join(dest, posixpath.basename(remote))
            sftp.get(remote, local)
            print(os.path.abspath(local))
    else:
        for local in sources:
            remote = posixpath.join(dest, os.path.basename(local))
            sftp.put(local, remote)
            print(remote)
    sftp.close()
    client.close()


if __name__ == "__main__":
    main()
