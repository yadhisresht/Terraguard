import math, time
EARTH_R = 6371.0

def haversine(lat1, lon1, lat2, lon2):
    # distance in km
    p = math.pi / 180.0
    a = 0.5 - math.cos((lat2-lat1)*p)/2 + math.cos(lat1*p)*math.cos(lat2*p)*(1-math.cos((lon2-lon1)*p))/2
    return 2*EARTH_R*math.asin(math.sqrt(a))

def quake_intensity_proxy(mag, dist_km, depth_km):
    # Very rough proxy for Modified Mercalli using magnitude/distance/depth
    # I = mag*2 - log10(dist_km+10) - depth_km/300  (toy!)
    import math
    val = mag*2 - math.log10(dist_km+10) - (depth_km/300.0)
    return max(0.0, val)

def p_s_eta_km(dist_km):
    # P-wave ~6 km/s, S-wave ~3.5 km/s
    p_eta_s = dist_km / 6.0
    s_eta_s = dist_km / 3.5
    return p_eta_s, s_eta_s

def tsunami_celerity(depth_m=4000.0, g=9.81):
    # c = sqrt(g*h)
    return (g*depth_m)**0.5  # m/s

def pretty_eta(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h: return f"{h}h {m}m {s}s"
    if m: return f"{m}m {s}s"
    return f"{s}s"
