import argparse, json, pandas as pd
from .utils import haversine, tsunami_celerity, pretty_eta

# Simple tsunami heuristic based on quake parameters
def tsunami_flag(quake, coastal_point):
    # quake: dict with mag, depth_km, lat, lon
    # coastal_point: dict with lat, lon
    mag = quake["mag"]; depth = quake["depth_km"]; 
    # Very rough screening: Mw>=7.5 and depth<70km near subduction zones (not modeled here).
    if mag >= 7.5 and (depth is None or depth < 70):
        return True
    return False

def eta_to_coast_km(quake, coast_lat, coast_lon):
    dist_km = haversine(quake["lat"], quake["lon"], coast_lat, coast_lon)
    c = tsunami_celerity(4000.0) # m/s
    eta_s = (dist_km*1000.0)/c
    return dist_km, eta_s

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quake_json", type=str, required=True)
    ap.add_argument("--coast_lat", type=float, default=13.0)
    ap.add_argument("--coast_lon", type=float, default=80.3)
    args = ap.parse_args()
    q = json.loads(args.quake_json)
    flag = tsunami_flag(q, {"lat": args.coast_lat, "lon": args.coast_lon})
    dist_km, eta_s = eta_to_coast_km(q, args.coast_lat, args.coast_lon)
    level = "INFO"
    if flag:
        level = "WATCH" if q["mag"] < 8.0 else "WARNING"
    print(json.dumps({
        "tsunami_possible": flag,
        "level": level,
        "dist_km": round(dist_km,1),
        "eta": pretty_eta(eta_s)
    }, indent=2))
