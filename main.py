import asyncio
import os

from checkin import Credentials, Report, parse_targets, run

LOG_PATH = "checkin.log"


def emit_record(report: Report) -> bool:
    """Print the run record and append it to LOG_PATH; returns whether it was saved."""
    line = report.to_line()
    print(line, end="")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(line)
    except OSError:
        print("Error: submission summary could not be saved.")
        return False
    return True


async def main() -> int:
    credentials = Credentials(
        api_id=int(os.environ["API_ID"]),
        api_hash=os.environ["API_HASH"],
        session_string=os.environ["SESSION_STRING"],
    )
    targets = parse_targets(os.environ.get("BOT_CONFIG", ""))
    report = Report(len(targets))
    saved = True
    try:
        await run(targets, report, credentials)
    finally:
        saved = emit_record(report)
    return int(report.failed or not saved)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
