# Màn hình, taskbar, tự tắt màn

Desktop của Raspberry Pi OS (Bookworm, Trixie) gồm: compositor **labwc**, taskbar
**wf-panel-pi**, nền desktop **pcmanfm**, cấu hình màn **kanshi**. Lệnh chạy qua SSH muốn chạm
tới desktop phải có:

```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u) WAYLAND_DISPLAY=wayland-0
```

## Xem có màn nào, đang bật hay tắt

```bash
wlr-randr                                           # tên cổng, độ phân giải, vị trí
for f in /sys/class/drm/card1-HDMI-A-*; do echo $f $(cat $f/status $f/enabled $f/dpms); done
```

Khi có người đang xem VNC, wayvnc **giữ quyền nguồn** của màn đang chia sẻ. Lúc đó `wlopm`
bị từ chối mà vẫn in "off" dù màn đang sáng. Trạng thái thật đọc ở `/sys/class/drm/.../dpms`.

## Chụp màn

`python scripts/pi_shot.py <thư-mục>` chụp mỗi cổng một ảnh, dùng `grim -o <cổng>`. Đây là
cách kiểm chắc nhất sau khi sửa giao diện.

## Taskbar: `~/.config/wf-panel-pi/wf-panel-pi.ini`

Có thể có hai mục:

```ini
[panel]            ; khay hệ thống, đồng hồ, wifi...
position=top
autohide=false
monitor=HDMI-A-1
widgets_left=smenu spacing0 spacing4 launchers spacing8 window-list   ; trống = không có nút menu
[dock]             ; menu + launcher + danh sách cửa sổ
autohide=false
monitor=HDMI-A-2
```

Mặc định hệ thống nằm ở `/etc/xdg/wf-panel-pi/wf-panel-pi.ini`.

- Control Centre → Taskbar ghi vào file này, và thanh **tự nạp lại**, không cần khởi động lại.
- Sửa tay bằng `sed` thì nên khởi động lại thanh: `pkill -x wf-panel-pi`. `lwrespawn` sẽ tự
  chạy lại nó.
- `autohide=true` trên màn cảm ứng nghĩa là gần như không bao giờ thấy thanh, vì không có
  chuột rê lên mép màn.
- Thanh "biến mất" thì kiểm theo thứ tự: tiến trình còn chạy không, `autohide`, `monitor`
  (thanh có thể đang nằm ở màn khác), rồi mtime của file (có người vừa sửa không).

## Tự tắt màn: dòng swayidle

Nằm ở `~/.config/labwc/autostart`. Control Centre → Display → Screen Blanking ghi vào đây,
mặc định 600 giây:

```bash
swayidle -w timeout 600 'wlopm --off \*' resume 'wlopm --on \*' &
```

Đổi số giây bằng `sed`, rồi chạy lại swayidle (`pkill swayidle` rồi chạy lại dòng trên với
`setsid`), không cần khởi động lại Pi. Trang pi-screen cũng đổi được giá trị này qua
`pi-screen-helper idle-set <giây>`.
