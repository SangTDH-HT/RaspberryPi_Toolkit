---
name: raspberry-pi
description: >
  Điều khiển Raspberry Pi (Raspberry Pi OS desktop, Wayland/labwc) từ máy Windows qua SSH:
  chạy lệnh, sudo, chép file, chụp màn hình, bật/tắt VNC (wayvnc), trang web xem màn hình
  noVNC, taskbar (wf-panel-pi), tự tắt màn (swayidle), wifi (NetworkManager), khởi động lại.
  Dùng khi người dùng nói "raspberry", "pi", "vào pi", "bật vnc", "link xem màn hình pi",
  "taskbar pi", "màn pi tắt", "pi rớt wifi", "chụp màn pi", hoặc đưa ảnh trang pi-screen.
license: MIT
---

# raspberry-pi

Mọi thao tác đi qua script trong `scripts/` (Python + paramiko), chạy trên máy Windows của
người dùng. Không cần PuTTY hay ssh tương tác.

## Chuẩn bị (một lần)

1. `python -m pip install paramiko`
2. Tạo `~/.pi-toolkit/pi.json` theo mẫu `pi.example.json` ở gốc repo: `host`, `user`.
   Có thể thay bằng biến `PI_HOST`, `PI_USER`.
3. Mật khẩu **không** ghi vào file. Hỏi người dùng rồi truyền qua biến `PI_PW` trong lệnh.
   Không lưu mật khẩu vào bộ nhớ hay ghi chú.
4. Tuỳ chọn: `python scripts/pi_setup_key.py` để cài khoá SSH, lần sau đăng nhập khỏi cần
   mật khẩu. `sudo` vẫn cần mật khẩu. Chạy `--dry-run` trước, và hỏi người dùng trước khi cài.

`SCRIPTS` dưới đây là thư mục `scripts/` cạnh file này.

## Các lệnh

| Việc | Lệnh |
|---|---|
| Chạy lệnh, có sudo | `PI_PW=... python SCRIPTS/pi.py 'sudo systemctl restart wayvnc'` |
| Chụp mọi màn | `python SCRIPTS/pi_shot.py <thư-mục>` → đọc ảnh PNG được in ra |
| Chép file | `MSYS_NO_PATHCONV=1 python SCRIPTS/pi_files.py get /tmp/a.log <thư-mục>` (hoặc `put`) |
| Kiểu đăng nhập VNC | `python SCRIPTS/vnc_types.py` |
| Cài khoá SSH | `python SCRIPTS/pi_setup_key.py [--dry-run]` |

`pi.py` trả về đúng mã thoát của lệnh trên Pi. Có chữ `sudo` trong lệnh thì mật khẩu được
đưa qua `SUDO_ASKPASS`, nên `echo x | sudo tee file` vẫn chạy được.

## Cách làm việc

1. **Dò trước, sửa sau.** Bắt đầu bằng `uptime`, `systemctl is-active ...` và đọc file cấu hình.
   Pi rớt mạng thì thử TCP tới cổng 22/5900/6080 trước khi kết luận.
2. **Sao lưu trước khi sửa**: `cp -n file file.bak-<ngày>`. Báo người dùng đường dẫn bản lưu.
3. **Kiểm sau khi sửa** bằng chính trạng thái máy: cổng nghe (`ss -ltn`), `systemctl is-active`,
   và ảnh `pi_shot.py` với thay đổi nhìn thấy được trên màn. Chỉ báo xong khi đã thấy kết quả.
4. Thấy file cấu hình bị đổi lại sau khi mình sửa (xem mtime) thì có người đang chỉnh trên Pi.
   **Không đè lại**; hỏi người dùng muốn giữ bản nào.
5. Viết lệnh bằng **Bash tool với nháy đơn**. PowerShell nuốt `$f`, `$(...)` trước khi lệnh
   tới được Pi.

## Đọc thêm khi cần

| Chủ đề | File |
|---|---|
| Kết nối, sudo, khoá SSH, bẫy phía Windows | [references/ket-noi.md](references/ket-noi.md) |
| VNC (wayvnc), trang web noVNC, kiểu đăng nhập | [references/vnc-va-trang-web.md](references/vnc-va-trang-web.md) |
| Màn hình, taskbar, tự tắt màn, chụp màn | [references/man-hinh-va-desktop.md](references/man-hinh-va-desktop.md) |
| Wifi, rớt mạng, khởi động lại, nguồn | [references/wifi-va-he-thong.md](references/wifi-va-he-thong.md) |

## Giới hạn quyền của Claude Code

Ở **auto mode**, bộ kiểm an toàn chặn mọi lệnh nới mã hoá hoặc xác thực, ví dụ thêm
`relax_encryption=true` cho wayvnc. Người dùng có đồng ý trong chat thì vẫn bị chặn. Đừng lách
bằng lệnh khác. Có hai cách:
- người dùng tự chạy lệnh (đưa họ đúng một dòng lệnh), hoặc
- người dùng tắt auto mode, gọi lại, rồi bấm **Allow** ở hộp xin phép.
