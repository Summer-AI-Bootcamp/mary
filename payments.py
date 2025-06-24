from pathlib import Path, PurePosixPath
import json, datetime as dt

OUTBOX = Path(__file__).with_name("outbox")
OUTBOX.mkdir(exist_ok=True)


def enqueue_payment(record: dict) -> None:
    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    file = OUTBOX / f"{ts}-{record['vendor_name']}.json"
    file.write_text(json.dumps(record, indent=2))
    print(f"🟢 queued → {PurePosixPath(file)}")