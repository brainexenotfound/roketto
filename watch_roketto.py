#!/usr/bin/env python3
"""
Light‑weight monitor for Roketto badminton court availability.

Features
- Polls the public calendar widget HTML (same as the browser) with a persisted session.
- You can watch a single date/time or a date range with optional time windows or weekdays.
- Safe polling defaults (3 minutes + jitter) to avoid triggering DDoS protection.
- Console-only notifications (one concise summary per polling cycle to avoid OS toast issues).

This script is intentionally dependency‑light and avoids browser automation.
"""
from __future__ import annotations

import argparse
import datetime as dt
import random
import re
import sys
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore


SHOW_URL = (
    "https://roketto.sportlogic.net.au/secure/customer/booking/v1/public/show"
    "?readOnly=false&popupMsgDisabled=false&hideTopSiteBar=false"
)
CAL_URL = (
    "https://roketto.sportlogic.net.au/secure/customer/booking/v1/public/"
    "calendar-widget?date={date}"
)
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
)


@dataclass(frozen=True)
class Slot:
    resource_id: str
    resource_label: str
    date: dt.date  # site local date
    start: dt.time
    end: dt.time

    @property
    def key(self) -> Tuple[str, dt.date, dt.time]:
        return (self.resource_id, self.date, self.start)


def parse_date(value: str) -> dt.date:
    for fmt in ("%Y-%m-%d", "%Y%m%d", "%d/%m/%Y"):
        try:
            return dt.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"Date '{value}' must be YYYY-MM-DD or YYYYMMDD.")


def parse_time(value: str) -> dt.time:
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return dt.datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"Time '{value}' must be HH:MM or HH:MM:SS.")


def build_date_span(args: argparse.Namespace) -> List[dt.date]:
    if args.start_date or args.end_date:
        if not (args.start_date and args.end_date):
            raise ValueError("Use both --start-date and --end-date when specifying a range.")
    if args.date:
        return [args.date]
    if args.start_date and args.end_date:
        if args.start_date > args.end_date:
            raise ValueError("--start-date must be <= --end-date")
        return [
            args.start_date + dt.timedelta(days=i)
            for i in range((args.end_date - args.start_date).days + 1)
        ]
    # Default: watch the next 7 days
    today = dt.date.today()
    return [today + dt.timedelta(days=i) for i in range(args.days_ahead)]


def new_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    # Prime session so that calendar calls succeed.
    s.get(SHOW_URL, timeout=20)
    return s


def extract_slots(html: str, tz_site: ZoneInfo) -> List[Slot]:
    """Parse the calendar widget HTML and return available slots."""
    soup = BeautifulSoup(html, "html.parser")
    slots: List[Slot] = []
    for td in soup.select("td.available"):
        onclick = td.get("onclick", "")
        # toggleBooking('RID', 'YYYYMMDD', 'HH:MM:SS', 'HH:MM:SS', ...)
        m = re.search(
            r"toggleBooking\('([^']+)',\s*'(\d{8})',\s*'(\d{2}:\d{2}:\d{2})',\s*'(\d{2}:\d{2}:\d{2})'",
            onclick,
        )
        if not m:
            continue
        rid, date_str, start_str, end_str = m.groups()
        try:
            date = dt.datetime.strptime(date_str, "%Y%m%d").date()
            start = dt.datetime.strptime(start_str, "%H:%M:%S").time()
            end = dt.datetime.strptime(end_str, "%H:%M:%S").time()
        except ValueError:
            continue
        label = td.find_previous("td", class_="calendar-resource-label")
        slots.append(
            Slot(
                resource_id=rid,
                resource_label=(label.text.strip() if label else rid),
                date=date,
                start=start,
                end=end,
            )
        )
    return slots


def fetch_slots_for_date(
    session: requests.Session, date: dt.date
) -> Tuple[List[Slot], requests.Session]:
    """Fetch slots for one date, renewing the session if it expires."""
    date_token = date.strftime("%Y%m%d")
    url = CAL_URL.format(date=date_token)
    resp = session.get(url, timeout=25)
    if resp.status_code != 200 or "Expected session attribute" in resp.text:
        # Session expired or not primed; renew and retry once.
        session = new_session()
        resp = session.get(url, timeout=25)
    if resp.status_code != 200:
        raise RuntimeError(f"Calendar fetch failed ({resp.status_code}) for {date_token}")
    return extract_slots(resp.text, tz_site=ZoneInfo("Australia/Sydney")), session


def slot_matches(slot: Slot, args: argparse.Namespace) -> bool:
    if args.weekdays and slot.date.weekday() not in args.weekdays:
        return False
    if args.time_exact and slot.start != args.time_exact:
        return False
    if args.time_from and slot.start < args.time_from:
        return False
    if args.time_to and slot.start >= args.time_to:
        return False
    return True


def filter_by_min_block(slots: List[Slot], min_hours: int) -> List[Slot]:
    """
    Keep only slots that begin a consecutive available block of at least min_hours.
    Slots are 1-hour increments in the calendar; we look for sequential hours on the same court and date.
    """
    if min_hours <= 1:
        return slots

    result: List[Slot] = []
    # Group by (resource_id, date)
    by_group: dict[tuple[str, dt.date], List[Slot]] = {}
    for s in slots:
        by_group.setdefault((s.resource_id, s.date), []).append(s)

    for (_, _), group in by_group.items():
        group_sorted = sorted(group, key=lambda s: s.start)
        # Find runs of consecutive hours
        run: List[Slot] = []
        for slot in group_sorted:
            if not run:
                run = [slot]
                continue
            prev = run[-1]
            prev_end_dt = dt.datetime.combine(prev.date, prev.end)
            cur_start_dt = dt.datetime.combine(slot.date, slot.start)
            if (cur_start_dt - prev_end_dt) == dt.timedelta(0):
                run.append(slot)
            else:
                if len(run) >= min_hours:
                    result.append(run[0])
                run = [slot]
        if run and len(run) >= min_hours:
            result.append(run[0])
    return result


def notify_summary(new_slots: List[Slot], local_tz: ZoneInfo, site_tz: ZoneInfo) -> None:
    """Print a concise summary when new slots are found."""
    if not new_slots:
        return
    print(f"Found {len(new_slots)} new slot(s):", flush=True)
    for slot in new_slots:
        print(f"  - {format_slot(slot, local_tz, site_tz)}", flush=True)


def format_slot(slot: Slot, local_tz: ZoneInfo, site_tz: ZoneInfo) -> str:
    site_dt = dt.datetime.combine(slot.date, slot.start, tzinfo=site_tz)
    local_dt = site_dt.astimezone(local_tz)
    return (
        f"{slot.resource_label}: {slot.date.isoformat()} "
        f"{slot.start.strftime('%H:%M')}–{slot.end.strftime('%H:%M')} "
        f"(local: {local_dt.strftime('%a %Y-%m-%d %I:%M %p %Z')})"
    )


def jittered_interval(base: int, jitter: int) -> float:
    if jitter <= 0:
        return float(base)
    return base + random.uniform(-jitter, jitter)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Watch Roketto badminton court availability safely."
    )
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--date", type=parse_date, help="Single date to watch (YYYY-MM-DD).")
    grp.add_argument("--start-date", type=parse_date, help="Start date for range (inclusive).")
    parser.add_argument("--end-date", type=parse_date, help="End date for range (inclusive).")
    parser.add_argument(
        "--days-ahead",
        type=int,
        default=7,
        help="If no dates supplied, watch the next N days (default: 7).",
    )
    parser.add_argument(
        "--time",
        dest="time_exact",
        type=parse_time,
        help="Exact start time to match (HH:MM).",
    )
    parser.add_argument(
        "--from-time", dest="time_from", type=parse_time, help="Earliest start time to match."
    )
    parser.add_argument(
        "--to-time", dest="time_to", type=parse_time, help="Latest start time (exclusive)."
    )
    parser.add_argument(
        "--weekday",
        dest="weekday",
        choices=["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        help="Limit to a weekday (e.g. --weekday wed).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=180,
        help="Base polling interval in seconds (default: 180). Keep this high to be polite.",
    )
    parser.add_argument(
        "--jitter",
        type=int,
        default=25,
        help="Random jitter (+/- seconds) added to interval to avoid patterns (default: 25).",
    )
    parser.add_argument("--once", action="store_true", help="Run a single check and exit.")
    parser.add_argument(
        "--min-hours",
        type=int,
        default=1,
        help="Minimum consecutive hours on the same court/date to notify (default: 1).",
    )
    # Notifications simplified to console output only (toast/beep removed for stability).
    parser.add_argument(
        "--site-tz",
        default="Australia/Sydney",
        help="Time zone of the venue (default: Australia/Sydney).",
    )
    parser.add_argument(
        "--local-tz",
        default=None,
        help="Your local TZ for display. Defaults to your system zoneinfo name.",
    )
    args = parser.parse_args()

    # Normalise weekday filter to integers if provided.
    wd_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    args.weekdays: Optional[Set[int]] = None
    if args.weekday:
        args.weekdays = {wd_map[args.weekday]}

    site_tz = ZoneInfo(args.site_tz)
    local_tz = ZoneInfo(args.local_tz) if args.local_tz else dt.datetime.now().astimezone().tzinfo

    try:
        dates = build_date_span(args)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Watching {len(dates)} day(s): {[d.isoformat() for d in dates]}")
    if args.time_exact:
        print(f"Target start time: {args.time_exact.strftime('%H:%M')}")
    if args.time_from or args.time_to:
        print(
            f"Time window: {args.time_from.strftime('%H:%M') if args.time_from else 'any'}"
            f" to {args.time_to.strftime('%H:%M') if args.time_to else 'any'}"
        )
    if args.min_hours > 1:
        print(f"Minimum consecutive hours: {args.min_hours}")
    if args.interval < 90:
        print("[warn] Interval < 90s may annoy the site; consider raising it.", file=sys.stderr)

    session = new_session()
    seen: Set[Tuple[str, dt.date, dt.time]] = set()
    consecutive_errors = 0

    while True:
        try:
            matched_slots: List[Slot] = []
            for d in dates:
                slots, session = fetch_slots_for_date(session, d)
                for slot in slots:
                    if slot.key in seen:
                        continue
                    if slot_matches(slot, args):
                        matched_slots.append(slot)
            # Apply min-block filter across all matched slots
            filtered_slots = filter_by_min_block(matched_slots, args.min_hours)
            for s in filtered_slots:
                seen.add(s.key)
            if filtered_slots:
                notify_summary(filtered_slots, local_tz, site_tz)
            consecutive_errors = 0
        except Exception as exc:
            consecutive_errors += 1
            backoff = min(600, args.interval * (consecutive_errors + 1))
            print(f"[error] {exc} — backing off {backoff}s", file=sys.stderr)
            time.sleep(backoff)

        if args.once:
            break

        sleep_for = max(30, jittered_interval(args.interval, args.jitter))
        time.sleep(sleep_for)


if __name__ == "__main__":
    main()
