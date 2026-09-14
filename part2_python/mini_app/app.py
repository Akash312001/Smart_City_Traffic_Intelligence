"""Command-line traffic analytics application."""
import argparse
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


def configure_logging(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, filename=path, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date_time"] = pd.to_datetime(df["date_time"])
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Traffic analytics mini application")
    parser.add_argument("--data", type=Path, default=Path("../outputs/featured_traffic.csv"))
    parser.add_argument("--log", type=Path, default=Path("app.log"))
    sub = parser.add_subparsers(dest="command", required=True)
    p1 = sub.add_parser("traffic-at"); p1.add_argument("datetime")
    sub.add_parser("high-periods")
    sub.add_parser("weekday-weekend")
    p4 = sub.add_parser("recommend"); p4.add_argument("day_type", choices=["weekday", "weekend"])
    args = parser.parse_args()
    configure_logging(args.log)
    logger.info("CLI command invoked: %s arguments=%s", args.command, vars(args))
    try:
        df = load(args.data)
        if args.command == "traffic-at":
            ts = pd.to_datetime(args.datetime, errors="raise")
            rows = df[df.date_time == ts]
            if rows.empty:
                print(f"No record found for {ts}.")
            else:
                r = rows.iloc[0]
                print(f"{ts}: traffic={int(r.traffic_volume)}, weather={r.weather_main}, temperature={r.temp_c:.1f}°C")
        elif args.command == "high-periods":
            x = df.groupby("hour")["traffic_volume"].mean().sort_values(ascending=False).head(5)
            print("Top five hourly traffic periods:")
            for h, v in x.items(): print(f"{int(h):02d}:00 — {v:.0f} vehicles/hour")
        elif args.command == "weekday-weekend":
            x = df.assign(day_type=df.date_time.dt.dayofweek.map(lambda d: "Weekday" if d < 5 else "Weekend")).groupby("day_type").traffic_volume.mean()
            print(f"Weekday average: {x.get('Weekday', float('nan')):.0f}")
            print(f"Weekend average: {x.get('Weekend', float('nan')):.0f}")
        elif args.command == "recommend":
            target = "Weekday" if args.day_type == "weekday" else "Weekend"
            x = df.assign(day_type=df.date_time.dt.dayofweek.map(lambda d: "Weekday" if d < 5 else "Weekend"))
            hourly = x[x.day_type == target].groupby("hour").traffic_volume.mean().sort_values().head(3)
            hours = ", ".join(f"{int(h):02d}:00" for h in hourly.index)
            print(f"For a {args.day_type} journey, consider lower-traffic periods around {hours}.")
    except (OSError, ValueError, KeyError) as exc:
        logger.error("Invalid CLI input or data: %s", exc)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
