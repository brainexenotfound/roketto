# Roketto Badminton Slot Watcher / 场次监控工具

Light‑weight Python tool that watches the public Roketto booking page and alerts you when a court becomes available. 下方附中文指南，方便不熟悉 conda 的用户。

---
## Quick Start (English)

### With conda
```bash
conda create -n roketto-bot python=3.11 pip
conda activate roketto-bot
pip install -r requirements.txt
```

Single check:
```bash
python watch_roketto.py --once --date 2026-02-02
```

Watch range with filters:
```bash
python watch_roketto.py \
  --start-date 2026-02-10 --end-date 2026-02-20 \
  --from-time 18:00 --to-time 22:00 \
  --weekday fri --toast --beep
```

### Without conda (plain venv)
```bash
python -m venv .venv
. .venv/Scripts/activate   # PowerShell: .\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

### Pack single EXE (Windows)
```bash
pip install pyinstaller
pyinstaller --onefile watch_roketto.py
# exe at dist/watch_roketto.exe
```

## Commands (English)
- `--date YYYY-MM-DD` single day.
- `--start-date ... --end-date ...` inclusive range (both required).
- `--days-ahead N` default 7 when no dates.
- Time: `--time HH:MM` exact; `--from-time`; `--to-time` (exclusive).
- `--weekday mon|tue|wed|thu|fri|sat|sun`
- `--interval` seconds (default 180) + `--jitter` (default 25).
- Notifications: `--toast`, `--beep`, `--webhook-url https://...`
- TZ: `--site-tz` (default Australia/Sydney); `--local-tz` for display.
- `--once` run one pass.

## How it works
Seeds a session on the public page, fetches `/calendar-widget?date=YYYYMMDD`, parses `td.available` slots, filters, and notifies once per new slot.

## Troubleshooting
- “Expected session attribute 'BookingFormV1'”: session expired; auto‑reseed; if repeated, increase `--interval`.
- No slots: loosen time filters; try `--once --date ...` without filters.
- 403/blocked: lower frequency (e.g., 300–420s) keep jitter.
- Toast/beep: Windows only; ensure `win10toast` installed.
- Webhook silent: POST test with curl; some hooks need auth/fields.
- Timezone: set `--local-tz America/Los_Angeles` if system TZ is off.
- Repeats: dedupe per resource+date+start; restarting will re-announce.

## Safe use
Keep intervals generous (≥180s) with jitter, stop when not needed, avoid multiple high-frequency instances.

## Examples
- Evenings next 7 days:  
  `python watch_roketto.py --days-ahead 7 --from-time 17:00 --to-time 22:00 --toast`
- One-off before heading out:  
  `python watch_roketto.py --once --date 2026-02-03 --from-time 18:00 --to-time 21:00`

---
## 中文快速指南（不懂 conda 也能用）

1. 安装 Python 3.11（Windows 勾选 “Add Python to PATH”）。  
2. 在项目目录打开 PowerShell 或 CMD：
   ```bash
   python -m venv .venv
   .\\.venv\\Scripts\\activate      # PowerShell 可用 .\\.venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt
   ```
3. 试跑一次（单日、检查一次就退出）：
   ```bash
   python watch_roketto.py --once --date 2026-02-02
   ```
4. 持续监听示例（2/10–2/20，周五晚 6–10 点，桌面弹窗+蜂鸣）：
   ```bash
   python watch_roketto.py ^
     --start-date 2026-02-10 --end-date 2026-02-20 ^
     --from-time 18:00 --to-time 22:00 ^
     --weekday fri --toast --beep
   ```

### 常用参数（中文速查）
- 日期：`--date` 单日；或 `--start-date ... --end-date ...` 范围；未指定则 `--days-ahead` 默认 7 天。
- 时间：`--time` 精确；`--from-time` 最早；`--to-time` 最晚（不含）。`--weekday` 限定星期几。
- 频率：`--interval` 基础间隔（秒，默认 180），`--jitter` 抖动（默认 ±25）。
- 通知：`--toast` 桌面弹窗；`--beep` 蜂鸣；`--webhook-url` 推送到 Slack/Discord 等。
- 时区：`--site-tz` 场馆时区（默认 Australia/Sydney）；`--local-tz` 显示你的本地时间。
- `--once` 只跑一遍。

### 常见问题
- **“Expected session attribute 'BookingFormV1'”**：会话过期，脚本会重建；频繁出现请增大 `--interval`。
- **找不到场次**：先不用时间过滤跑一次确认解析正常。
- **403/被怀疑机器人**：降低频率，增大间隔并保留抖动。
- **Toast/Beep 无响应**：仅 Windows 支持，确保 `win10toast` 安装且在桌面会话内运行。
- **Webhook 没消息**：用 curl 先测试；有些需要鉴权或特定字段。
- **时区显示不对**：显式设置 `--local-tz`。

### 打包成单文件 EXE
```bash
pip install pyinstaller
pyinstaller --onefile watch_roketto.py
# 生成 dist/watch_roketto.exe，可直接双击或命令行运行
```

保持较长间隔、开启抖动，避免对站点造成压力。祝你顺利抢到场地！
