#!/bin/bash
echo "The udev rule installation script is currently running..."
# 将 VID 和 PID 替换为实际的设备供应商 ID 和产品 ID
VID="04b4"
PID="00f5"

DVSLumeVID="04b5"
DVSLumePID="0001"
# 创建 udev 规则文件路径
UDEV_RULES_FILE="/etc/udev/rules.d/dvsense.rules"

# 写入 udev 规则内容
echo "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"$VID\", ATTR{idProduct}==\"$PID\", MODE=\"0666\"" >> $UDEV_RULES_FILE
echo "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"$DVSLumeVID\", ATTR{idProduct}==\"$DVSLumePID\", MODE=\"0666\"" >> $UDEV_RULES_FILE

# 重新加载 udev 规则
udevadm control --reload-rules
udevadm trigger
echo "The udev rule installation is complete."