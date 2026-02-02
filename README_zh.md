# Roketto 羽毛球场次监控工具（中文指南）

这个小脚本会定期刷新 Roketto 的公开预约页面，一旦发现有空档就提醒你。无需浏览器自动化，也不需要了解 conda。

## 1 分钟快速上手（零基础）

1. 安装 Python 3.11（Windows 可在官网 python.org 下载并勾选 “Add Python to PATH”）。
2. 在项目目录打开 PowerShell 或 CMD，创建隔离环境并安装依赖：
   ```bash
   python -m venv .venv
   .\\.venv\\Scripts\\activate      # 若是 PowerShell: .\\.venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt
   ```
3. 试跑一次（单日、仅检查一次就退出）：
   ```bash
   python watch_roketto.py --once --date 2026-02-02
   ```
4. 持续监听（示例：2 月 10–20 日，周五晚 6–10 点，桌面弹窗 + 蜂鸣）：
   ```bash
   python watch_roketto.py ^
     --start-date 2026-02-10 --end-date 2026-02-20 ^
     --from-time 18:00 --to-time 22:00 ^
     --weekday fri --toast --beep
   ```

> 如果你完全不想装 Python，可用 PyInstaller 打包单文件 EXE（见下文），把 exe 发给朋友即可。

## 常用参数（简明）

- 日期与范围  
  - `--date YYYY-MM-DD` 仅看这一天。  
  - `--start-date ... --end-date ...` 指定起止日期（必须成对出现）。  
  - `--days-ahead N` 没指定日期时，默认查未来 7 天，可改为 N。
- 时间过滤  
  - `--time HH:MM` 精确开场时间。  
  - `--from-time HH:MM` 最早开始时间。  
  - `--to-time HH:MM` 最晚开始时间（不含该时刻）。  
  - `--weekday mon|tue|wed|thu|fri|sat|sun` 仅某星期几。
- 轮询频率  
  - `--interval 秒` 基础间隔，默认 180 秒。  
  - `--jitter 秒` 随机抖动，默认 ±25 秒，减少被判定为机器人。
- 通知方式  
  - `--toast` Windows 桌面弹窗。  
  - `--beep` Windows 蜂鸣。  
  - `--webhook-url https://...` 向 Slack/Discord 等发送 JSON `{text: ...}`。
- 时区  
  - `--site-tz` 场馆时区，默认 `Australia/Sydney`。  
  - `--local-tz` 显示你的本地时间，默认用系统时区。
- 其他  
  - `--once` 只检查一遍就退出。

## 工作原理（概要）

1. 访问公开预约页，获取会话。  
2. 请求 `/secure/customer/booking/v1/public/calendar-widget?date=YYYYMMDD`。  
3. 解析表格里标记为 `available` 的单元格，提取场地、日期、起止时间。  
4. 按你的过滤条件去重并提示。

## 不想用 Python？打包成单文件 EXE

```bash
pip install pyinstaller
pyinstaller --onefile watch_roketto.py
# 生成 dist/watch_roketto.exe，双击或命令行运行皆可。
```

## 常见问题与排查

- **一直提示 “Expected session attribute 'BookingFormV1'”**  
  会话过期或网络抖动。脚本会自动重建会话；若频繁发生，增大 `--interval`（如 300–420 秒）并保持 `--jitter`。

- **总是找不到场次**  
  先用 `--once --date YYYY-MM-DD` 不加时间过滤确认解析正常；再逐步加时间/星期过滤。

- **收到 403 或被疑似屏蔽**  
  降低频率、增大间隔，避免同时运行多个实例。

- **Toast/Beep 没反应**  
  仅 Windows 支持；确保在用户桌面会话内运行，且 `win10toast` 已安装。

- **Webhook 没消息**  
  用 curl 手动 POST 测试；某些 Webhook 需要特定字段或鉴权。

- **时区显示不对**  
  显示两种时间：场馆时区 + 你的本地时区。必要时手动设 `--local-tz America/Los_Angeles` 等。

## 使用建议（避免被封）

- 保持较长的轮询间隔（≥180 秒）并开启抖动。  
- 只在需要的时段运行，结束后关闭脚本。  
- 不要多个设备/账号同时高频访问。

## 典型命令速查

- 未来 7 天，每晚 5–10 点：  
  ```bash
  python watch_roketto.py --days-ahead 7 --from-time 17:00 --to-time 22:00 --toast
  ```
- 出门前单次查看：  
  ```bash
  python watch_roketto.py --once --date 2026-02-03 --from-time 18:00 --to-time 21:00
  ```

祝你抢到理想的场地！
