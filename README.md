# RaspberryPi_Toolkit

Bộ công cụ để **Claude Code điều khiển Raspberry Pi** từ máy Windows. Anh/chị chỉ cần nói bằng
lời, ví dụ "bật VNC cho Pi rồi đưa link", "chụp màn Pi xem", "Pi rớt wifi à", "bật taskbar
cho Pi"; Claude tự vào Pi qua SSH, làm, rồi tự kiểm lại.

Gồm:

| Phần | Nội dung |
|---|---|
| Skill `raspberry-pi` | Cách làm việc với Pi: dò trước, sao lưu, sửa, kiểm bằng ảnh chụp màn hình. Kèm các bẫy đã gặp |
| `skills/raspberry-pi/scripts/` | Script Python: chạy lệnh có sudo, chép file, chụp mọi màn, xem kiểu đăng nhập VNC, cài khoá SSH |
| `skills/raspberry-pi/references/` | Ghi chú chi tiết: kết nối, VNC và trang web, màn hình và taskbar, wifi và hệ thống |
| `pi-screen/` | *(đang bổ sung)* Trang web xem và điều khiển màn Pi từ trình duyệt (`http://<pi>:6080`) kèm trình cài |

Đã chạy thật trên Pi 4 với Raspberry Pi OS Trixie 64-bit (desktop labwc/Wayland, wayvnc).

## Cần có

- Windows có **Claude Code** và **Python 3.10+**
- Pi chạy Raspberry Pi OS **bản desktop**, đã bật SSH, cùng mạng LAN với máy Windows
- Tên đăng nhập và mật khẩu tài khoản Linux trên Pi

## Cài đặt (một lần)

```powershell
# 1. Thư viện SSH cho Python
python -m pip install paramiko

# 2. Plugin cho Claude Code
claude plugin marketplace add SangTDH-HT/RaspberryPi_Toolkit
claude plugin install raspberry-pi@raspberrypi-toolkit

# 3. Khai báo Pi của mình (sửa host/user cho đúng)
mkdir $HOME\.pi-toolkit -Force
@'
{ "host": "raspberrypi.local", "user": "pi", "port": 22 }
'@ | Set-Content $HOME\.pi-toolkit\pi.json -Encoding utf8
```

`host` là tên mạng (`<hostname>.local`) hoặc IP của Pi. Nếu tên `.local` không phân giải được,
dùng IP lấy từ trang quản lý router.

Cài xong thì thoát rồi mở lại Claude Code.

## Dùng

Mở Claude Code rồi nói việc cần làm. Lần đầu Claude sẽ hỏi mật khẩu Pi. Mật khẩu chỉ dùng
trong lệnh đó, **không** được lưu vào file nào.

Muốn khỏi gõ mật khẩu mỗi lần đăng nhập, bảo Claude "cài khoá SSH cho Pi" (chạy
`pi_setup_key.py`). Riêng `sudo` vẫn cần mật khẩu.

Chạy tay, không qua Claude:

```bash
cd <thư mục plugin>/skills/raspberry-pi/scripts
PI_PW='mật-khẩu' python pi.py 'uptime; sudo systemctl status wayvnc --no-pager'
python pi_shot.py ./anh            # chụp mọi màn của Pi
python vnc_types.py                # VNC đang mở những kiểu đăng nhập nào
```

## Xem màn hình Pi

Có hai cách:

1. **RealVNC Viewer / RealVNC Connect** (cài trên Windows): gõ `<host>` rồi đăng nhập bằng tài
   khoản Pi. Mã hoá đầy đủ, không cần cấu hình thêm.
2. **Trình duyệt**: `http://<host>:6080`, dùng trang `pi-screen`. Mã nguồn trang đang được bổ
   sung vào repo. Xem ở phone hay máy khác đều được, có chọn màn, toàn màn hình, đặt thời gian
   tự tắt màn, khởi động lại Pi. Trang này cần
   thêm `relax_encryption=true` trong `/etc/wayvnc/config`; xem
   [references/vnc-va-trang-web.md](skills/raspberry-pi/references/vnc-va-trang-web.md).
   Chỉ dùng trong mạng nội bộ.

## Lưu ý an toàn

- Repo không chứa mật khẩu, IP hay khoá. `pi.json` nằm ở thư mục người dùng, ngoài git.
- Ở **auto mode**, Claude Code tự chặn các lệnh nới bảo mật (ví dụ `relax_encryption`). Khi đó,
  hoặc tự chạy dòng lệnh Claude đưa, hoặc tắt auto mode rồi bấm **Allow** khi Claude hỏi.
- Claude được dặn hỏi trước khi khởi động lại hay tắt Pi, đổi băng tần wifi, hay đè lên thay đổi
  của người khác.

## Giấy phép

MIT. Xem [LICENSE](LICENSE).
