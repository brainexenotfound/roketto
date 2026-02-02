# Roketto Badminton Slot Watcher

Light‑weight Python tool that watches the public Roketto booking page and alerts you when a court becomes available. It mimics the same endpoints the browser uses—no Selenium needed—and keeps requests polite to avoid triggering site defences.

## Quick Start (Anaconda)

```bash
conda create -n roketto-bot python=3.11 pip
conda activate roketto-bot
pip install -r requirements.txt
```

Run a single check:

```bash
python watch_roketto.py --once --date 2026-02-02
```

Watch a range with filters:

```bash
# Fridays between 6–10pm from Feb 10–20 (venue time)
python watch_roketto.py \
  --start-date 2026-02-10 --end-date 2026-02-20 \
  --from-time 18:00 --to-time 22:00 \
  --weekday fri --toast --beep
```

## Command Reference

- `--date YYYY-MM-DD` — single day to watch.
- `--start-date YYYY-MM-DD --end-date YYYY-MM-DD` — inclusive range (both required).
- `--days-ahead N` — watch the next N days when no dates are supplied (default 7).
- Time filters:
  - `--time HH:MM` exact start time.
  - `--from-time HH:MM` earliest start.
  - `--to-time HH:MM` latest start (exclusive).
- `--weekday mon|tue|wed|thu|fri|sat|sun` — limit to a weekday.
- `--interval SECONDS` — base poll interval (default 180s, minimum enforced 30s).
- `--jitter SECONDS` — random ± jitter to avoid patterns (default 25s).
- `--once` — single pass then exit.
- Notifications:
  - `--toast` Windows toast (needs win10toast).
  - `--beep` short Windows chime.
  - `--webhook-url https://...` POSTs `{ "text": msg }` for Slack/Discord/etc.
- Time zones:
  - `--site-tz` venue time zone (default `Australia/Sydney`).
  - `--local-tz` your time zone for display; defaults to system zone.

## How It Works (brief)

1) Opens the public booking page to seed a session.  
2) Calls `/secure/customer/booking/v1/public/calendar-widget?date=YYYYMMDD`.  
3) Parses table cells with class `available` and extracts start/end times from the `toggleBooking(...)` handler.  
4) Applies your filters and notifies once per new slot.

## Running Without Conda

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

## Building a Single Executable (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile watch_roketto.py
# Share dist/watch_roketto.exe
```

## Common Issues & Troubleshooting

- **“Expected session attribute 'BookingFormV1'”**  
  Session expired. The script auto-reseeds; if it repeats, increase `--interval` and ensure network is stable.

- **No slots ever found**  
  Verify your time filters aren’t too narrow; try `--once --date YYYY-MM-DD` with no time filters to confirm parsing works.

- **Blocked or 403 responses**  
  Reduce polling: raise `--interval` (e.g., 300–420s) and keep `--jitter` enabled.

- **Toast/beep not working**  
  Only available on Windows. Ensure `win10toast` installed (`pip install win10toast`) and run inside a user session (not as a service).

- **Webhook silent**  
  Test with `curl -X POST -H "Content-Type: application/json" -d '{"text":"test"}' <your webhook>`; some endpoints require authentication or different JSON keys.

- **Timezone confusion**  
  Messages show venue time plus your local time. Set `--local-tz` explicitly (e.g., `America/Los_Angeles`) if your system timezone is incorrect.

- **Too many repeats**  
  The script dedupes by resource + date + start time. If you restart, it will announce slots again; run continuously to avoid repeat alerts.

## Safe-Use Tips

- Keep `--interval` generous (>=180s) and `--jitter` on to stay polite to the site.
- Run only during the window you actually need; stop the watcher when you’re not looking for a slot.
- Avoid running multiple instances with the same account/IP to minimize load.

## Example: Daily Watch for Next Week, Evenings Only

```bash
python watch_roketto.py --days-ahead 7 --from-time 17:00 --to-time 22:00 --toast
```

## Example: Single Check Before Heading Out

```bash
python watch_roketto.py --once --date 2026-02-03 --from-time 18:00 --to-time 21:00
```

Happy hitting!
