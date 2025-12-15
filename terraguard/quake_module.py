import argparse, json, requests, pandas as pd, time
from .utils import haversine, quake_intensity_proxy, p_s_eta_km

USGS_ENDPOINT = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def fetch_quakes(hours=24, min_mag=3.0):
    try:
        r = requests.get(USGS_ENDPOINT, timeout=10)
        r.raise_for_status()
        data = r.json()
        rows = []
        for f in data.get("features", []):
            props = f.get("properties", {})
            geom = f.get("geometry", {})
            coords = geom.get("coordinates", [None, None, None])
            mag = props.get("mag")
            if mag is None or mag < min_mag: continue
            row = {
                "time": pd.to_datetime(props.get("time"), unit="ms", utc=True).tz_convert("UTC").isoformat(),
                "place": props.get("place"),
                "mag": mag,
                "depth_km": coords[2] if len(coords)>2 else None,
                "lon": coords[0],
                "lat": coords[1]
            }
            rows.append(row)
        return pd.DataFrame(rows)
    except Exception as e:
        # Offline fallback: one synthetic event near Andaman
        return pd.DataFrame([{
            "time": pd.Timestamp.utcnow().isoformat(),
            "place": "Synthetic: Andaman Sea",
            "mag": 7.5,
            "depth_km": 20,
            "lon": 92.1,
            "lat": 10.5
        }])

def scan_aoi(quakes_df, aoi_csv, pga_threshold=4.0):
    aoi = pd.read_csv(aoi_csv)
    alerts = []
    for _, q in quakes_df.iterrows():
        for _, a in aoi.iterrows():
            dist = haversine(q.lat, q.lon, a.lat, a.lon)
            intensity = quake_intensity_proxy(q.mag, dist, q.depth_km or 10)
            p_eta, s_eta = p_s_eta_km(dist)
            level = "INFO"
            if intensity >= 6.0: level = "WARNING"
            elif intensity >= 5.0: level = "WATCH"
            elif intensity >= 4.0: level = "ADVISORY"
            alerts.append({
                "aoi": a["name"],
                "time_utc": q["time"],
                "place": q["place"],
                "mag": q["mag"],
                "depth_km": q["depth_km"],
                "dist_km": round(dist,1),
                "p_eta_s": int(p_eta),
                "s_eta_s": int(s_eta),
                "intensity_proxy": round(float(intensity),2),
                "level": level,
                "contact_ndrf": a["contact_ndrf"],
                "contact_local": a["contact_local"],
                "coastal": int(a["coastal"])==1
            })
    return pd.DataFrame(alerts)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--min_mag", type=float, default=4.5)
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--aoi", type=str, default="data/aoi.csv")
    args = ap.parse_args()
    q = fetch_quakes(hours=args.hours, min_mag=args.min_mag)
    out = scan_aoi(q, args.aoi)
    print(out.head().to_string(index=False))
