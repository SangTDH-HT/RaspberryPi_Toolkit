# VNC (wayvnc) và trang web xem màn hình

Raspberry Pi OS desktop mới (labwc/Wayland) dùng **wayvnc** chứ không còn RealVNC Server.

## Bật / tắt

```bash
sudo raspi-config nonint do_vnc 0      # bật + enable lúc boot   (1 = tắt)
systemctl is-active wayvnc; ss -ltn | grep :5900
```

Đăng nhập bằng tài khoản Linux qua PAM. Trong log có dòng
`pam_unix(wayvnc:account): setuid failed` là **bình thường**, không phải lỗi đăng nhập.

## File cấu hình `/etc/wayvnc/config`

```
use_relative_paths=true
address=::
enable_auth=true
enable_pam=true
private_key_file=tls_key.pem
certificate_file=tls_cert.pem
rsa_private_key_file=rsa_key.pem
relax_encryption=true        # chỉ cần cho trang web noVNC, xem dưới
```

Sửa xong thì `sudo systemctl restart wayvnc`. Không chép các file `*.pem` ra khỏi Pi.

## Kiểu đăng nhập (security type)

`python scripts/vnc_types.py` liệt kê những kiểu server đang mở:

| Có relax_encryption? | wayvnc mở | Ai vào được |
|---|---|---|
| Không | 19 VeNCrypt, 129 RSA-AES-256, 5 RSA-AES | RealVNC Viewer / RealVNC Connect, TigerVNC |
| Có | thêm 30 Apple ARD (và 6, tuỳ bản) | thêm noVNC trên trình duyệt |

noVNC **không** nói được VeNCrypt-X509 hay RSA-AES 5/129. Trên trang `http://` (không có
`crypto.subtle`) nó chỉ dùng được ARD (30). ARD cần AES-ECB, nên trang pi-screen tự mang theo
file `aes-ecb.js`.

**Triệu chứng thiếu relax_encryption:** trang web đăng nhập được (trang tự kiểm tài khoản bằng
VeNCrypt), nhưng ô màn hình hiện "Mất kết nối với Pi" và cứ 5 giây nối lại một lần. Trong
`journalctl -u pi-screen` có hàng loạt dòng `connecting to: 127.0.0.1:5900`.

Thêm `relax_encryption=true` là **nới mã hoá**: các phiên ARD trên http không được bảo vệ như
VeNCrypt. Chỉ bật trong mạng nội bộ, và nói rõ điều này với người dùng.

## Trang web pi-screen (cổng 6080)

Mã nguồn và trình cài đang được bổ sung vào thư mục `pi-screen/` của repo. Trên Pi đã cài:

| Thứ | Ở đâu |
|---|---|
| Mã | `/opt/pi-screen/server.py` (websockify + đăng nhập), `/opt/pi-screen/www/` |
| Dịch vụ | `pi-screen.service`, chạy bằng user `vnc` |
| Việc cần root (tự tắt màn, bật/tắt màn, khởi động lại) | `/usr/local/sbin/pi-screen-helper`, được phép qua `/etc/sudoers.d/pi-screen` |

```bash
sudo systemctl enable --now pi-screen
curl -s -o /dev/null -w '%{http_code}\n' http://<host>:6080/     # 200
```

Hai tab cùng mở trang thì cả hai cùng giữ phiên VNC. Bảo người dùng đóng bớt tab.

## Khi người dùng muốn "link xem màn hình"

1. Kiểm `wayvnc`, `pi-screen` có active và enabled không.
   `journalctl | grep COMMAND=` cho biết ai đã tắt chúng.
2. Chạy `vnc_types.py`. Thiếu 30 thì xử lý relax_encryption như trên. Ở auto mode bước này sẽ
   bị chặn; xem mục "Giới hạn quyền" trong SKILL.md.
3. Đưa link `http://<host>:6080`, kèm IP dự phòng.
4. Kiểm phiên thật: `ss -tn state established '( sport = :5900 )'` có kết nối từ 127.0.0.1,
   và trong 15 giây không còn dòng `connecting to` mới.
