# Kết nối tới Pi

## Thứ tự xác thực trong `pilib.connect`

1. Khoá SSH: `key` trong pi.json, ssh-agent, hoặc `~/.ssh/id_*`.
2. Không có khoá hoặc khoá bị từ chối thì dùng mật khẩu: biến `PI_PW`, hoặc `getpass` khi chạy
   trong terminal.

Host key mới được tự thêm (AutoAddPolicy). Pi được cài lại hệ điều hành thì host key đổi, và
paramiko báo `BadHostKeyException`. Khi đó xoá dòng của Pi trong `~/.ssh/known_hosts`.

## sudo không tương tác

Raspberry Pi OS cài bằng Imager hoặc cloud-init thường **cần mật khẩu** cho sudo. Kiểm bằng
`sudo -n true`.

`pi.py` xử lý sudo như sau:
- đọc mật khẩu từ stdin của kênh SSH,
- ghi một file askpass tạm `mktemp` (quyền 700, xoá bằng `trap EXIT`),
- định nghĩa hàm `sudo() { command sudo -A "$@"; }` và `export -f`,
- chuyển stdin của lệnh về `/dev/null`.

Hệ quả:
- `echo x | sudo tee f` chạy được, vì sudo không đọc mật khẩu từ ống dẫn.
- `sudo sh -c "..."` chạy được. Bên trong đã là root, không cần sudo nữa.
- `xargs sudo ...` hoặc script gọi `/usr/bin/sudo` trực tiếp thì không qua hàm. Khi đó dùng
  `sudo -A` (biến `SUDO_ASKPASS` đã được export).

Không dùng cách `sudo -S` rồi ghi mật khẩu nhiều lần vào stdin. Lệnh có ống dẫn sẽ bị lẫn mật
khẩu vào dữ liệu.

## Bẫy phía Windows

| Bẫy | Cách tránh |
|---|---|
| Git Bash đổi `/tmp/a.png` thành `C:/Program Files/Git/tmp/a.png` | `MSYS_NO_PATHCONV=1` trước lệnh. `pi_files.py` tự báo lỗi khi gặp |
| PowerShell thay `$f`, `$(cat ...)` trước khi gửi | Dùng Bash tool, lệnh Pi đặt trong nháy đơn |
| `python` trong venv dự án không có paramiko | Gọi đúng Python đã cài paramiko, hoặc `pip install paramiko` vào venv đó |
| Console cp1252 làm vỡ chữ có dấu | `pilib` tự ép stdout UTF-8 |
| `<tên>.local` không phân giải (mDNS) | Dùng IP. Tìm IP trong trang quản lý router, hoặc `ping -4 <tên>.local` |

## Dò nhanh khi "không vào được"

```bash
# trên Windows (PowerShell)
Test-NetConnection <host> -Port 22     # SSH
Test-NetConnection <host> -Port 5900   # VNC
Test-NetConnection <host> -Port 6080   # trang web pi-screen
```

Ping được mà cổng 22 đóng thì Pi đang khởi động, hoặc sshd chết. Ping không được thì xem
[wifi-va-he-thong.md](wifi-va-he-thong.md).
