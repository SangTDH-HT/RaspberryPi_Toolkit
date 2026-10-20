# Wifi, rớt mạng, khởi động lại, nguồn

## Wifi (NetworkManager)

```bash
nmcli -t device status
nmcli -t -f NAME,TYPE,DEVICE,AUTOCONNECT connection show
nmcli -t -f IN-USE,SSID,CHAN,SIGNAL,SECURITY device wifi list --rescan yes
sudo nmcli connection up "<SSID>"        # nối lại
```

- **Kênh 5 GHz DFS (52–144)**: router dò thấy radar sẽ đổi kênh, và Pi rớt vài phút. Cùng SSID
  mà có cả bản 2,4 GHz sóng mạnh hơn thì có thể khoá Pi vào 2,4 GHz:
  `sudo nmcli connection modify "<SSID>" 802-11-wireless.band bg`. Hỏi người dùng trước khi làm.
- Kernel báo `Firmware rejected country setting` với chip CYW43455 là bình thường.
- Wifi onboard của Pi 4 chỉ chạy trên Linux. Windows on ARM không có driver cho nó.

## Pi vừa khởi động lại: vì sao?

```bash
uptime; journalctl --list-boots
vcgencmd get_throttled      # 0x0 = ổn từ lúc boot; 0x1 = đang thiếu điện; 0x10000 = đã từng thiếu điện
```

Raspberry Pi OS mặc định **không lưu journal qua lần khởi động** (`journalctl -b -1` báo "no
persistent journal"). Muốn lần sau tra được thì bật lưu (hỏi người dùng trước):

```bash
sudo mkdir -p /var/log/journal && sudo systemctl restart systemd-journald
```

Ai đã tắt hay sửa dịch vụ thì xem các lệnh sudo trong journal:
`sudo journalctl --since "<giờ>" | grep COMMAND=`.

## Khởi động lại, tắt máy

```bash
sudo systemctl reboot        # SSH rớt ngay. Đợi khoảng 60–90 giây rồi thử cổng 22
sudo systemctl poweroff      # phải rút điện cắm lại mới lên
```

Hỏi người dùng trước khi chạy hai lệnh này, nhất là khi Pi đang điều khiển máy.
