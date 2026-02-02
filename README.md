# Roketto Badminton Slot Watcher / 羽毛球场次监控工具

A lightweight, dependency-light tool to monitor court availability at the Roketto badminton booking site. It checks the public calendar for open slots and notifies you on the command line.

这是一个轻量级、低依赖的工具，用于监控 Roketto 羽毛球馆的场地预订情况。它会检查公开的日历，并在命令行中通知您可用的时间段。

---

## English Instructions

This tool can be used by anyone, with or without programming experience.

### For Non-Coders: How to Use

#### 1. Download the Tool
- If you see a green **`< > Code`** button on this page, click it and select **Download ZIP**.
- Unzip the downloaded file to a memorable location (e.g., your `Downloads` folder).

#### 2. Run the Watcher
The watcher runs in a terminal window. You give it commands to tell it what dates and times you're interested in.

1.  Open the folder where you unzipped the files.
2.  You should find a file named `watch_roketto.py`.
3.  You will need to run it from your terminal. On Windows, you can open the Command Prompt (search for `cmd` in the Start Menu) or PowerShell.
4.  Navigate to the directory where you saved the files. For example:
    ```sh
    cd C:\Users\YourName\Downloads\roketto
    ```
5.  Before running, you need to install the dependencies. Run this command once:
    ```sh
    pip install -r requirements.txt
    ```
    If `pip` is not found, you may need to [install Python](https://www.python.org/downloads/).
6.  Now, run the watcher with your desired options.

#### Examples
- To check for any available slots on February 28, 2026, just once:
  ```sh
  python watch_roketto.py --date 2026-02-28 --once
  ```

- To continuously watch for slots on Friday evenings between 6 PM and 10 PM for the next 7 days:
  ```sh
  python watch_roketto.py --weekday fri --from-time 18:00 --to-time 22:00
  ```

- To watch for a 2-hour consecutive block on weekends in March 2026:
  ```sh
  python watch_roketto.py --start-date 2026-03-01 --end-date 2026-03-31 --weekday sat --weekday sun --min-hours 2
  ```

When a slot is found, it will print a message like this:
```
Found 1 new slot(s):
  - Court 1: 2026-02-28 19:00–20:00 (local: Fri 2026-02-28 07:00 PM EST)
```

Leave the terminal window open to keep watching. **To stop, close the window or press `Ctrl+C`**.

### For Coders: How to Use

1.  Clone or download the repository.
2.  It's recommended to use a virtual environment.
    ```sh
    # Create and activate a virtual environment
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```
3.  Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4.  Run the script with desired arguments. See the options table below for details.
    ```sh
    python watch_roketto.py --help
    ```

### Command-Line Options

| Option | Argument | Description |
| :--- | :--- | :--- |
| `--date` | `YYYY-MM-DD` | Watch a single specific date. |
| `--start-date`| `YYYY-MM-DD` | Start of a date range to watch. Must be used with `--end-date`. |
| `--end-date` | `YYYY-MM-DD` | End of a date range to watch. Must be used with `--start-date`. |
| `--days-ahead`| `N` | Watch for the next `N` days. Defaults to 7. |
| `--time` | `HH:MM` | Match an exact start time. |
| `--from-time` | `HH:MM` | The earliest start time to match. |
| `--to-time` | `HH:MM` | The latest start time to match (exclusive). |
| `--weekday` | `mon`...`sun`| Restrict the search to a specific day of the week. Can be used multiple times. |
| `--min-hours` | `N` | Find slots with at least `N` consecutive hours available on the same court. Default is 1. |
| `--interval` | `Seconds` | How often to check for availability in seconds. Default is 180. |
| `--jitter` | `Seconds` | Adds randomness to the interval to avoid detection. Default is 25. |
| `--once` | (none) | Run the check only one time and exit. |

---

## 中文说明

本工具适用于所有用户，无论您有无编程经验。

### 为非程序员设计：如何使用

#### 1. 下载工具
- 如果您在此页面上看到一个绿色的 **`< > Code`** 按钮，请点击它，然后选择 **Download ZIP**。
- 将下载的 ZIP 文件解压到一个您记得住的位置（例如，您的 `下载` 文件夹）。

#### 2. 运行监控脚本
监控器在一个终端窗口中运行。您通过命令告诉它您感兴趣的日期和时间。

1.  打开您解压文件的文件夹。
2.  您应该能找到一个名为 `watch_roketto.py` 的文件。
3.  您需要从终端运行它。在 Windows 上，您可以打开命令提示符（在开始菜单中搜索 `cmd`）或 PowerShell。
4.  导航到您保存文件的目录。例如：
    ```sh
    cd C:\Users\您的用户名\Downloads\roketto
    ```
5.  在运行之前，您需要安装依赖项。运行一次此命令：
    ```sh
    pip install -r requirements.txt
    ```
    如果找不到 `pip`，您可能需要[安装 Python](https://www.python.org/downloads/)。
6.  现在，使用您想要的选项运行监控器。

#### 示例
- 只检查一次 2026 年 2 月 28 日是否有空场：
  ```sh
  python watch_roketto.py --date 2026-02-28 --once
  ```

- 在接下来的 7 天内，持续监控周五晚上 6 点到 10 点的场次：
  ```sh
  python watch_roketto.py --weekday fri --from-time 18:00 --to-time 22:00
  ```

- 监控 2026 年 3 月的周末，要求至少有连续 2 小时的空场：
  ```sh
  python watch_roketto.py --start-date 2026-03-01 --end-date 2026-03-31 --weekday sat --weekday sun --min-hours 2
  ```

当找到空场时，它会打印如下消息：
```
Found 1 new slot(s):
  - Court 1: 2026-02-28 19:00–20:00 (local: Fri 2026-02-28 07:00 PM EST)
```

保持终端窗口打开以继续监控。**要停止，请关闭窗口或按 `Ctrl+C`**。

### 为程序员设计：如何使用

1.  克隆或下载此代码库。
2.  建议使用虚拟环境。
    ```sh
    # 创建并激活虚拟环境
    python -m venv .venv
    # 在 Windows 上
    .venv\Scripts\activate
    # 在 macOS/Linux 上
    source .venv/bin/activate
    ```
3.  安装依赖：
    ```sh
    pip install -r requirements.txt
    ```
4.  使用所需的参数运行脚本。详细信息请参见下方的选项表。
    ```sh
    python watch_roketto.py --help
    ```

### 命令行选项

| 选项 | 参数 | 描述 |
| :--- | :--- | :--- |
| `--date` | `YYYY-MM-DD` | 监控一个特定的日期。 |
| `--start-date`| `YYYY-MM-DD` | 要监控的日期范围的开始。必须与 `--end-date` 一起使用。 |
| `--end-date` | `YYYY-MM-DD` | 要监控的日期范围的结束。必须与 `--start-date` 一起使用。 |
| `--days-ahead`| `N` | 监控未来 `N` 天。默认为 7。 |
| `--time` | `HH:MM` | 匹配确切的开始时间。 |
| `--from-time` | `HH:MM` | 要匹配的最早开始时间。 |
| `--to-time` | `HH:MM` | 要匹配的最晚开始时间（不含）。 |
| `--weekday` | `mon`...`sun`| 将搜索限制在特定的星期几。可多次使用。 |
| `--min-hours` | `N` | 查找在同一球场上至少有 `N` 个连续小时的空场。默认为 1。 |
| `--interval` | `秒` | 每隔多少秒检查一次可用性。默认为 180。 |
| `--jitter` | `秒` | 为检查间隔增加随机性，以避免被网站屏蔽。默认为 25。 |
| `--once` | (无) | 只运行一次检查然后退出。 |