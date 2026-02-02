# Roketto Badminton Slot Watcher / 场次监控工具

This is a tiny watcher for the Roketto badminton booking site. It can be run as a **standalone EXE** (no Python knowledge needed). English and Chinese instructions are included below.

---
## English: Get & Run (No Coding Needed)

### 1) Download the files
- If on GitHub: click the green **Code** button → **Download ZIP**, then unzip (e.g., to `C:\Users\<you>\Downloads\roketto`).
- If you already have the folder, just open it in File Explorer.

### 2) Run the standalone app
1. Open the `dist` folder inside `roketto`.
2. Double-click `watch_roketto.exe`. A black window opens (that’s normal).
3. Type a command and press Enter, for example:
   ```
   dist\watch_roketto.exe --once --date 2026-02-02
   ```
4. Leave the window open to keep watching. Close it to stop.

#### Handy examples
- Single check on a date:  
  `dist\watch_roketto.exe --once --date 2026-02-02`
- Watch a date range, evenings, Fridays only, min 2-hour blocks:  
  `dist\watch_roketto.exe --start-date 2026-02-10 --end-date 2026-02-20 --from-time 18:00 --to-time 22:00 --weekday fri --min-hours 2`

#### Shortcut (double-click)
1. Right-click `dist\watch_roketto.exe` → **Create shortcut**.  
2. Right-click the shortcut → **Properties** → in **Target**, append your options, e.g.  
   `"C:\Users\<you>\Downloads\roketto\dist\watch_roketto.exe" --once --date 2026-02-02`  
3. Double-click the shortcut to run with those options.

### 3) If `watch_roketto.exe` is missing (build it yourself)
You only need to do this once; afterwards share the EXE with friends.
```
pip install pyinstaller
pyinstaller --onefile watch_roketto.py
```
The file appears at `dist/watch_roketto.exe`.

---
## For Coders: Run from Source (conda or venv)

### Clone / download
```bash
git clone <repo-url> roketto
cd roketto
# or download ZIP and unzip here
```

### Option A: conda
```bash
conda create -n roketto-bot python=3.11 pip
conda activate roketto-bot
pip install -r requirements.txt
python watch_roketto.py --once --date 2026-02-02
```

### Option B: plain venv
```bash
python -m venv .venv
. .venv/Scripts/activate   # PowerShell: .\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python watch_roketto.py --start-date 2026-02-10 --end-date 2026-02-20 --from-time 18:00 --to-time 22:00 --weekday fri --min-hours 2
```

### Option C: build EXE yourself
```bash
pip install pyinstaller
pyinstaller --onefile watch_roketto.py
```

---
## 中文：下载与运行（零编程）

### 1) 获取文件
- 如果在 GitHub：点击绿色 **Code** → **Download ZIP**，解压到任意文件夹（如 `C:\Users\<你>\Downloads\roketto`）。
- 已经有文件夹的话，直接打开即可。

### 2) 运行独立程序
1. 打开 `roketto` 里的 `dist` 文件夹。
2. 双击 `watch_roketto.exe`，会弹出黑色窗口（正常现象）。
3. 在窗口里输入命令并回车，例如：
   ```
   dist\watch_roketto.exe --once --date 2026-02-02
   ```
4. 需要持续监听就让窗口保持打开，关闭窗口即停止。

#### 常用示例
- 单次查看某天：  
  `dist\watch_roketto.exe --once --date 2026-02-02`
- 2/10–2/20，周五晚 6–10 点监听（至少连续 2 小时）：  
  `dist\watch_roketto.exe --start-date 2026-02-10 --end-date 2026-02-20 --from-time 18:00 --to-time 22:00 --weekday fri --min-hours 2`

#### 建立双击快捷方式
1. 右键 `dist\watch_roketto.exe` → **Create shortcut**。  
2. 右键快捷方式 → **属性** → 在 “目标” 后加上参数，例如  
   `"C:\Users\<你>\Downloads\roketto\dist\watch_roketto.exe" --once --date 2026-02-02`  
3. 双击快捷方式即可按预设参数运行。

### 3) 没有 EXE 时自行打包（只做一次）
```
pip install pyinstaller
pyinstaller --onefile watch_roketto.py
```
生成的文件在 `dist\watch_roketto.exe`，可直接分享给朋友。

---
## 给开发者：源代码运行（conda 或 venv）

### 获取代码
```bash
git clone <repo-url> roketto
cd roketto
# 或下载 ZIP 解压
```

### 方案 A：conda
```bash
conda create -n roketto-bot python=3.11 pip
conda activate roketto-bot
pip install -r requirements.txt
python watch_roketto.py --once --date 2026-02-02
```

### 方案 B：原生 venv
```bash
python -m venv .venv
. .venv/Scripts/activate   # PowerShell: .\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python watch_roketto.py --start-date 2026-02-10 --end-date 2026-02-20 --from-time 18:00 --to-time 22:00 --weekday fri --min-hours 2
```

### 方案 C：自行打包 EXE
```bash
pip install pyinstaller
pyinstaller --onefile watch_roketto.py
```

---
## Quick Option Hints
- `--date YYYY-MM-DD` single day / 单日
- `--start-date ... --end-date ...` date range (pair required) / 日期范围（必须成对）
- `--from-time HH:MM` earliest; `--to-time HH:MM` latest (exclusive); `--weekday fri` limit to Friday / 最早最晚时间、限定星期几
- `--min-hours N` require N consecutive hours on the same court/date (default 1) / 要求连续 N 小时（默认 1）
- Notifications are console-only now (no toast/beep) / 现在仅控制台输出（移除弹窗/蜂鸣）
- Default polling every 180s with jitter to stay polite / 默认 180 秒轮询并带抖动，避免对站点造成压力

If something looks wrong, increase `--interval` (e.g., 300–420), keep `--jitter` on, and try a single check with `--once` to confirm it works. Happy hitting!
