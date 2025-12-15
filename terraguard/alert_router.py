import os, csv, time, json, pandas as pd, datetime as dt

LOG_DIR = "artifacts"
os.makedirs(LOG_DIR, exist_ok=True)

def route_alert(event: dict, offline: bool=False):
    # event contains: level, message, contacts[], aoi, source
    ts = dt.datetime.utcnow().isoformat() + "Z"
    event['ts'] = ts
    # Always log to CSV
    path = os.path.join(LOG_DIR, "alerts_log.csv")
    write_header = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sorted(event.keys()))
        if write_header: w.writeheader()
        w.writerow(event)
    # If online: simulate SMS/e-mail/webhook (here we just print)
    if not offline:
        print(f"[{event['level']}] {event['message']} -> {event.get('contacts')}")
    else:
        # Offline siren simulation
        print(f"[OFFLINE SIREN] {event['aoi']}: {event['level']} :: {event['message']}")
