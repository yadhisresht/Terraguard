import argparse, pandas as pd, numpy as np, json

def risk_from_trends(df):
    # Simple toy risk: higher with warming trend + high precip + steep slope
    df['temp_trend'] = df['temp_c'].rolling(3).mean()
    df['precip_trend'] = df['precip_mm'].rolling(3).mean()
    last = df.iloc[-1]
    score = 0.0
    if last['temp_trend'] > 9.0: score += 0.3
    if last['precip_trend'] > 20.0: score += 0.4
    if last['slope_deg'] >= 15: score += 0.2
    score = min(1.0, score)
    level = "INFO"
    if score >= 0.8: level = "WARNING"
    elif score >= 0.6: level = "WATCH"
    elif score >= 0.4: level = "ADVISORY"
    return float(score), level

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, required=True)
    args = ap.parse_args()
    df = pd.read_csv(args.csv, parse_dates=['date'])
    s, lvl = risk_from_trends(df)
    print(json.dumps({"glof_risk": s, "level": lvl}, indent=2))
