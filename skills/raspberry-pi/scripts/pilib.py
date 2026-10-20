"""Phần dùng chung: đọc cấu hình, mở SSH tới Pi.

Cấu hình (theo thứ tự ưu tiên, cái sau đè cái trước):
  1. ~/.pi-toolkit/pi.json  (hoặc đường dẫn trong biến PI_CONFIG)
  2. biến môi trường PI_HOST, PI_USER, PI_PORT, PI_KEY
  3. tham số --host / --user trên dòng lệnh

Mật khẩu KHÔNG nằm trong file cấu hình: lấy từ biến PI_PW, nếu không có
và đang chạy trong terminal thì hỏi bằng getpass.
"""
import getpass
import json
import os
import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    sys.exit("Thiếu paramiko: chạy  python -m pip install paramiko")

# Console Windows mặc định cp1252/cp437: chữ có dấu làm print() vỡ khi đầu ra bị chuyển hướng.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

CONFIG_PATH = Path(os.environ.get("PI_CONFIG", Path.home() / ".pi-toolkit" / "pi.json"))


def add_common_args(parser):
    parser.add_argument("--host", help="tên hoặc IP của Pi (mặc định lấy từ pi.json)")
    parser.add_argument("--user", help="tài khoản Linux trên Pi")


def load_config(args=None):
    cfg = {"host": "raspberrypi.local", "user": "pi", "port": 22, "key": None}
    if CONFIG_PATH.exists():
        cfg.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    for key in ("host", "user", "port", "key"):
        env = os.environ.get("PI_" + key.upper())
        if env:
            cfg[key] = env
    if args is not None:
        if getattr(args, "host", None):
            cfg["host"] = args.host
        if getattr(args, "user", None):
            cfg["user"] = args.user
    cfg["port"] = int(cfg["port"])
    return cfg


def password(required=False):
    pw = os.environ.get("PI_PW")
    if pw:
        return pw
    if sys.stdin.isatty():
        return getpass.getpass("Mật khẩu Pi: ")
    if required:
        sys.exit("Cần mật khẩu: đặt biến PI_PW hoặc chạy trong terminal để được hỏi.")
    return None


def _client():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return client


def connect(cfg, timeout=10):
    """Thử khoá SSH trước, không được mới dùng mật khẩu."""
    common = dict(hostname=cfg["host"], port=cfg["port"], username=cfg["user"], timeout=timeout)
    client = _client()
    try:
        client.connect(**common, key_filename=cfg.get("key"), look_for_keys=True, allow_agent=True)
        return client
    except paramiko.AuthenticationException:
        pass
    except paramiko.SSHException as e:
        # Máy chưa có khoá nào: paramiko báo "No authentication methods available".
        if "authentication methods" not in str(e):
            sys.exit(f"Không nối được {cfg['host']}:{cfg['port']} — {e}")
    except OSError as e:
        sys.exit(f"Không nối được {cfg['host']}:{cfg['port']} — {e}")
    client.close()

    pw = password(required=True)
    client = _client()
    try:
        client.connect(**common, password=pw, look_for_keys=False, allow_agent=False)
    except paramiko.AuthenticationException:
        sys.exit(f"Sai tài khoản hoặc mật khẩu cho {cfg['user']}@{cfg['host']}")
    except (OSError, paramiko.SSHException) as e:
        sys.exit(f"Không nối được {cfg['host']}:{cfg['port']} — {e}")
    return client


def write_out(text):
    """In UTF-8 thẳng ra stdout, tránh lỗi bảng mã của console Windows."""
    sys.stdout.buffer.write(text.encode("utf-8"))
    sys.stdout.flush()
