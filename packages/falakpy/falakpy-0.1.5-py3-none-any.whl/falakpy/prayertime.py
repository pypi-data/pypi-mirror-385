def subuh(lat,long,ele,tz,y,m,d,deg):
  from datetime import datetime, timedelta, date
  from skyfield.api import load, wgs84
  from skyfield import almanac
  import numpy as np

  # -------- Settings --------
  lat_location = lat
  long_location = long
  ele = ele
  timezone = tz                 # UTC+8 (Malaysia)
  year = y
  month = m
  day = d

  the_day = date(year, month, day)

  target_alt_deg = deg       # e.g., astronomical twilight
  tolerance_alt = 0.01          # ± degrees around target altitude


  # -------- Skyfield setup --------
  ts = load.timescale()
  eph = load('de440s.bsp')
  earth, sun = eph['earth'], eph['sun']
  location = earth + wgs84.latlon(lat_location, long_location, elevation_m=ele)

  def make_altitude_predicate(target_alt_deg: float, tolerance_alt: float):
    """True when Sun altitude is within [target - tol, target + tol]."""
    lo = target_alt_deg - tolerance_alt
    hi = target_alt_deg + tolerance_alt

    def in_alt_band(t):
        alt, az, _ = location.at(t).observe(sun).apparent().altaz()
        return (alt.degrees >= lo) & (alt.degrees <= hi)

    # hints for Skyfield’s search
    in_alt_band.step_days = 0.00001
    in_alt_band.rough_period = 0.5    # ≈12 h between crossings
    return in_alt_band

  pred = make_altitude_predicate(target_alt_deg, tolerance_alt)

  def local_from_utc(dt_utc):
    return dt_utc + timedelta(hours=timezone)

  def sun_altitude_intervals_for_day(d: date):
    """Return [(entry_time_utc, exit_time_utc)] for one local day where altitude is in band."""
    t0 = ts.utc(year, month, day, 0 - timezone, 0, 0)
    t1 = ts.utc(year, month, day, 12 - timezone, 0, 0)

    times, states = almanac.find_discrete(t0, t1, pred)
    intervals = []

    # if we start inside True state, prepend opening time
    is_true_at_start = bool(pred(t0)) if np.isscalar(pred(t0)) else bool(pred(t0).any())
    if is_true_at_start:
        times = ts.tt_jd(np.insert(times.tt, 0, t0.tt))
        states = np.insert(states, 0, True)

    # build [entry, exit) pairs for True segments
    for i in range(len(times) - 1):
        if states[i]:
            intervals.append((times[i], times[i + 1]))

    # if last state continues to t1
    if len(times) > 0 and states[-1]:
        intervals.append((times[-1], t1))

    return intervals

  # -------- Run for one day --------
  intervals = sun_altitude_intervals_for_day(the_day)

  #print(f"Sun altitude windows for {the_day.isoformat()} (local UTC{timezone:+d}), "
  #    f"alt ≈ {target_alt_deg}° ±{tolerance_alt}°")

  if not intervals:
    return None
  else:
    for idx, (entry, exit_) in enumerate(intervals, start=1):
        utc_entry = entry.utc_datetime()
        utc_exit  = exit_.utc_datetime()
        loc_entry = local_from_utc(utc_entry)
        loc_exit  = local_from_utc(utc_exit)
        duration_min = (utc_exit - utc_entry).total_seconds() / 60.0

        # optional: altitude & azimuth at entry
        alt_e, az_e, _ = location.at(entry).observe(sun).apparent().altaz()

  #      print(f"  #{idx}: {loc_entry.strftime('%H:%M:%S')} → {loc_exit.strftime('%H:%M:%S')}"
   #           f"  | duration: {duration_min:.2f} min"
   #           f"  | alt_entry: {alt_e.degrees:.2f}°  az: {az_e.degrees:.2f}°")
        z=loc_entry.strftime('%H:%M:%S')
  return z






def syuruk(lat, lon, ele, tz, y, m, d):
    """
    Syuruk (sunrise) for the local calendar morning.
    Returns 'HH:MM:SS' (local time) or None when sunrise doesn't occur (polar day/night).
    """
    from datetime import timedelta
    from skyfield.api import load, wgs84
    from skyfield import almanac
    from skyfield.units import Angle
    from skyfield.earthlib import refraction
    from numpy import arccos
    import numpy as np

    # --- Setup ---
    ts = load.timescale()
    eph = load('de440s.bsp')
    earth, sun = eph['earth'], eph['sun']
    location = earth + wgs84.latlon(lat, lon, elevation_m=ele)

    # Morning window (local 00:00 → 12:00) expressed in UTC
    t0 = ts.utc(y, m, d, 0 - tz, 0, 0)
    t1 = ts.utc(y, m, d, 12 - tz, 0, 0)

    # Corrected horizon (refraction + Sun SD + observer height)
    earth_radius_m = 6378136.6
    dip = Angle(radians=-arccos(earth_radius_m / (earth_radius_m + ele)))
    solar_sd_deg = 16.0 / 60.0
    r = refraction(0.0, temperature_C=15.0, pressure_mbar=1013.25)  # degrees
    horizon_deg = float(-r + dip.degrees - solar_sd_deg)

    # Predicate: Sun above corrected horizon? (vectorized)
    def above_horizon(t):
        alt, az, _ = location.at(t).observe(sun).apparent().altaz()
        alt_deg = np.asarray(alt.degrees)     # scalar or array
        return alt_deg >= horizon_deg         # bool or bool array

    # Hints for the root finder
    above_horizon.step_days = 0.001
    above_horizon.rough_period = 0.5

    # Find transitions (night<->day) over the morning
    times, states = almanac.find_discrete(t0, t1, above_horizon)

    # State at the very start (ensure scalar bool)
    start_state = bool(np.atleast_1d(above_horizon(t0))[0])

    # If no transitions in the morning window:
    if len(times) == 0:
        # always night → no sunrise; always day → already daytime (midnight sun)
        return None

    # Include the start state so we can inspect the first transition
    seq_times  = [t0] + list(times)
    seq_states = [start_state] + list(states.astype(bool))

    # Sunrise = night → day = False → True
    for i in range(len(seq_states) - 1):
        if (not seq_states[i]) and seq_states[i + 1]:
            t_rise = seq_times[i + 1]
            sunrise_local = t_rise.utc_datetime() + timedelta(hours=tz)
            return sunrise_local.strftime('%H:%M:%S')

    # No night→day transition in this morning window
    return None

def zuhur(lat,long,ele,tz,y,m,d):
  from datetime import datetime, timedelta, date
  from skyfield.api import load, wgs84
  from skyfield import almanac
  import numpy as np

  # -------- Settings --------
  lat_location = lat
  long_location = long
  ele = ele
  timezone = tz                 # UTC+8 (Malaysia)
  year = y
  month = m
  day = d

  ts = load.timescale()
  eph = load('de440s.bsp')
  planets = load('de440s.bsp')
  earth = planets['earth']
  sun = planets['sun']
  location = earth + wgs84.latlon(lat_location, long_location, elevation_m=ele)

  t0 = ts.utc(year, month, day,0-timezone)
  t1 = ts.utc(year, month, day,24-timezone)

  from skyfield.units import Angle
  from numpy import arccos
  from skyfield.earthlib import refraction

  t = almanac.find_transits(location, sun, t0, t1)
  h = t.utc.hour
  m = t.utc.minute
  s = t.utc.second

  #print(hour_solar_transit)
  #print(minutes_solar_transit )
  #print(second_solar_transit)
  #zuhur_time = hour_solar_transit + (minutes_solar_transit / 60) + (second_solar_transit / 3600 ) + timezone + 0.017778
  zuhur_time = float(np.array(h).item() + np.array(m).item()/60 + np.array(s).item()/3600 + timezone+ 0.017778)


  zuhur_time = float(zuhur_time)
  degrees = int(zuhur_time )
  decimal_part = zuhur_time  - degrees
  minutes_total = decimal_part * 60
  minutes = int(minutes_total)

  seconds = round((minutes_total - minutes) * 60)
  #print(f"{degrees}° {minutes}′ {seconds}″")

  sun_astro = location.at(ts.utc(year, month, day, h, m, s)).observe(sun)
  sun_alt, _, _ = sun_astro.apparent().altaz()
  alt_deg = float(np.atleast_1d(sun_alt.degrees)[0])   # <- force scalar

  # Check if the sun is above the horizon at zuhur time
  if sun_alt.degrees <= 0:
      zuhur = None
      altitude_zuhur = None
      #return None
  else:
      zuhur = f"{degrees}:{minutes}:{seconds}"
      altitude_zuhur = alt_deg

  return zuhur,altitude_zuhur

def asar(latitude, longitude, elevation, tz, y, m, d, length):
    """
    Compute Asar start time given 'length' = shadow multiplier
    (1 for Shafi'i/Maliki/Hanbali; 2 for Hanafi).
    Returns 'HH:MM:SS' local time or None when not defined (e.g., polar night).
    """
    from datetime import timedelta, date
    from skyfield.api import load, wgs84
    from skyfield import almanac
    import numpy as np
    import math

    timezone = tz
    the_day = date(y, m, d)

    # --- Get Sun altitude at true noon from your helper ---
    z = zuhur(latitude, longitude, elevation, tz, y, m, d)

    if z is None:
        # No valid zuhur (e.g., polar night/day or your helper failed) → no Asar
        return None
    elif isinstance(z, tuple):
        # Expecting (dt, altitude_deg)
        if len(z) < 2 or z[1] is None:
            return None
        altitude_zuhur = z[1]
    else:
        # If your helper returns just the altitude
        altitude_zuhur = z

    # Safety: if noon altitude is not a number (or below horizon all day), exit
    try:
        altitude_zuhur = float(altitude_zuhur)
    except (TypeError, ValueError):
        return None

    # If Sun is far below horizon at transit, Asar won’t occur
    if altitude_zuhur < 0:
        return None

    # ---- Asar target altitude from noon shadow relation ----
    s0 = 1.0 / math.tan(math.radians(altitude_zuhur))
    h_asar = math.degrees(math.atan(1.0 / (length + s0)))  # target altitude (deg)

    target_alt_deg = h_asar
    tolerance_alt = 0.01  # widen to 0.05 if needed

    # -------- Skyfield setup --------
    ts = load.timescale()
    eph = load('de440s.bsp')
    earth, sun = eph['earth'], eph['sun']
    location = earth + wgs84.latlon(latitude, longitude, elevation_m=elevation)

    def make_altitude_predicate(target_alt_deg: float, tolerance_alt: float):
        lo = target_alt_deg - tolerance_alt
        hi = target_alt_deg + tolerance_alt
        def in_alt_band(t):
            alt, az, _ = location.at(t).observe(sun).apparent().altaz()
            return (alt.degrees >= lo) & (alt.degrees <= hi)
        in_alt_band.step_days = 0.00001
        in_alt_band.rough_period = 0.5
        return in_alt_band

    pred = make_altitude_predicate(target_alt_deg, tolerance_alt)

    def to_local(dt_utc):
        return dt_utc + timedelta(hours=timezone)

    # Search from local noon to midnight (afternoon only)
    t0 = ts.utc(y, m, d, 12 - timezone, 0, 0)
    t1 = ts.utc(y, m, d, 24 - timezone, 0, 0)

    times, states = almanac.find_discrete(t0, t1, pred)
    intervals = []

    start_true = bool(pred(t0))
    if start_true:
        times = ts.tt_jd(np.insert(times.tt, 0, t0.tt))
        states = np.insert(states, 0, True)

    for i in range(len(times) - 1):
        if states[i]:
            intervals.append((times[i], times[i + 1]))

    if len(times) > 0 and states[-1]:
        intervals.append((times[-1], t1))

    if not intervals:
        return None

    entry_tt, _ = intervals[0]
    return to_local(entry_tt.utc_datetime()).strftime('%H:%M:%S')

def maghrib(lat, lon, ele, tz, y, m, d):
    """
    Maghrib (sunset) for the local calendar day.
    Returns 'HH:MM:SS' (local time) or None when Sun never sets/rises that day.
    """
    from datetime import timedelta
    from skyfield.api import load, wgs84
    from skyfield import almanac
    from skyfield.units import Angle
    from skyfield.earthlib import refraction
    from numpy import arccos
    import numpy as np

    # --- Setup ---
    ts = load.timescale()
    eph = load('de440s.bsp')
    earth, sun = eph['earth'], eph['sun']
    location = earth + wgs84.latlon(lat, lon, elevation_m=ele)

    # Local-day window expressed in UTC
    t0 = ts.utc(y, m, d, 12 - tz, 0, 0)   # local 00:00
    t1 = ts.utc(y, m, d, 24 - tz, 0, 0)  # local 24:00

    # --- Corrected horizon (refraction + Sun SD + observer height) ---
    earth_radius_m = 6378136.6
    dip = Angle(radians=-arccos(earth_radius_m / (earth_radius_m + ele)))
    solar_sd_deg = 16.0 / 60.0
    r = refraction(0.0, temperature_C=15.0, pressure_mbar=1013.25)  # degrees
    horizon_deg = float(-r + dip.degrees - solar_sd_deg)

    # --- Predicate: is Sun above corrected horizon? (vectorized) ---
    def above_horizon(t):
        alt, az, _ = location.at(t).observe(sun).apparent().altaz()
        alt_deg = np.asarray(alt.degrees)   # works for scalar or vector
        return alt_deg >= horizon_deg       # returns bool or bool array

    # Hints for the root finder
    above_horizon.step_days = 0.001
    above_horizon.rough_period = 0.5

    # Find transitions (night<->day) over the local day
    times, states = almanac.find_discrete(t0, t1, above_horizon)

    # Determine state at the very start (ensure scalar bool)
    start_state = bool(np.atleast_1d(above_horizon(t0))[0])

    # If no transitions occurred all day:
    if len(times) == 0:
        # Always night → polar night → no Maghrib
        if not start_state:
            return None
        # Always day → polar day → no Maghrib
        else:
            return None

    # Build sequence including start state to find day->night (sunset)
    seq_times = [t0] + list(times)
    seq_states = [start_state] + list(states.astype(bool))

    # First True->False transition within local day is Maghrib
    for i in range(len(seq_states) - 1):
        if seq_states[i] and not seq_states[i + 1]:
            t_set = seq_times[i + 1]
            maghrib_local = t_set.utc_datetime() + timedelta(hours=tz)
            return maghrib_local.strftime('%H:%M:%S')

    # No day->night transition within this local day
    return None

def isyak(lat,long,ele,tz,y,m,d,deg):
  from datetime import datetime, timedelta, date
  from skyfield.api import load, wgs84
  from skyfield import almanac
  import numpy as np

  # -------- Settings --------
  lat_location = lat
  long_location = long
  ele = ele
  timezone = tz                 # UTC+8 (Malaysia)
  year = y
  month = m
  day = d

  the_day = date(year, month, day)

  target_alt_deg = deg       # e.g., astronomical twilight
  tolerance_alt = 0.01          # ± degrees around target altitude


  # -------- Skyfield setup --------
  ts = load.timescale()
  eph = load('de440s.bsp')
  earth, sun = eph['earth'], eph['sun']
  location = earth + wgs84.latlon(lat_location, long_location, elevation_m=ele)

  def make_altitude_predicate(target_alt_deg: float, tolerance_alt: float):
    """True when Sun altitude is within [target - tol, target + tol]."""
    lo = target_alt_deg - tolerance_alt
    hi = target_alt_deg + tolerance_alt

    def in_alt_band(t):
        alt, az, _ = location.at(t).observe(sun).apparent().altaz()
        return (alt.degrees >= lo) & (alt.degrees <= hi)

    # hints for Skyfield’s search
    in_alt_band.step_days = 0.00001
    in_alt_band.rough_period = 0.5    # ≈12 h between crossings
    return in_alt_band

  pred = make_altitude_predicate(target_alt_deg, tolerance_alt)

  def local_from_utc(dt_utc):
    return dt_utc + timedelta(hours=timezone)

  def sun_altitude_intervals_for_day(d: date):
    """Return [(entry_time_utc, exit_time_utc)] for one local day where altitude is in band."""
    t0 = ts.utc(year, month, day, 12 - timezone, 0, 0)
    t1 = ts.utc(year, month, day, 24 - timezone, 0, 0)

    times, states = almanac.find_discrete(t0, t1, pred)
    intervals = []

    # if we start inside True state, prepend opening time
    is_true_at_start = bool(pred(t0)) if np.isscalar(pred(t0)) else bool(pred(t0).any())
    if is_true_at_start:
        times = ts.tt_jd(np.insert(times.tt, 0, t0.tt))
        states = np.insert(states, 0, True)

    # build [entry, exit) pairs for True segments
    for i in range(len(times) - 1):
        if states[i]:
            intervals.append((times[i], times[i + 1]))

    # if last state continues to t1
    if len(times) > 0 and states[-1]:
        intervals.append((times[-1], t1))

    return intervals

  # -------- Run for one day --------
  intervals = sun_altitude_intervals_for_day(the_day)

  #print(f"Sun altitude windows for {the_day.isoformat()} (local UTC{timezone:+d}), "
  #    f"alt ≈ {target_alt_deg}° ±{tolerance_alt}°")

  if not intervals:
    return None
  else:
    for idx, (entry, exit_) in enumerate(intervals, start=1):
        utc_entry = entry.utc_datetime()
        utc_exit  = exit_.utc_datetime()
        loc_entry = local_from_utc(utc_entry)
        loc_exit  = local_from_utc(utc_exit)
        duration_min = (utc_exit - utc_entry).total_seconds() / 60.0

        # optional: altitude & azimuth at entry
        alt_e, az_e, _ = location.at(entry).observe(sun).apparent().altaz()

  #      print(f"  #{idx}: {loc_entry.strftime('%H:%M:%S')} → {loc_exit.strftime('%H:%M:%S')}"
   #           f"  | duration: {duration_min:.2f} min"
   #           f"  | alt_entry: {alt_e.degrees:.2f}°  az: {az_e.degrees:.2f}°")
        z=loc_entry.strftime('%H:%M:%S')
  return z








def singleday(lat, lon, ele, tz, y, m, d, csv_filename="prayer_times.csv",deg_subuh = -18,deg_isha=-18,asar_shadow_lenght = 1):

    import csv
    from datetime import date
    """
    Generate prayer times for one date, print as table, and also save as CSV.
    """
    # --- get each prayer time ---
    subuh_time    = subuh(lat, lon, ele, tz, y, m, d,deg_subuh)
    syuruk_time   = syuruk(lat, lon, ele, tz, y, m, d)
    zuhur_time, _ = zuhur(lat, lon, ele, tz, y, m, d)
    asar_time     = asar(lat, lon, ele, tz, y, m, d,asar_shadow_lenght)
    maghrib_time  = maghrib(lat, lon, ele, tz, y, m, d)
    isyak_time    = isyak(lat, lon, ele, tz, y, m, d,deg_isha)


    #print(subuh_time )


    # --- Prepare data row ---
    date_str = date(y, m, d).strftime("%Y-%m-%d")
    header = ["Date", "Subuh", "Syuruk", "Zuhur", "Asar", "Maghrib", "Isyak"]
    row = [date_str, subuh_time, syuruk_time, zuhur_time, asar_time, maghrib_time, isyak_time]


    # --- Handle None safely ---
    def fmt(t):
        """Format prayer time or show placeholder if None."""
        return t if t is not None else "--:--:--"

    # --- Print table to screen ---
    print("\n+------------+----------+----------+----------+----------+----------+----------+")
    print("|    Date    |  Subuh   |  Syuruk  |  Zuhur   |   Asar   | Maghrib  |  Isyak   |")
    print("+------------+----------+----------+----------+----------+----------+----------+")

    print(f"| {date_str} | {fmt(subuh_time):8} | {fmt(syuruk_time):8} | {fmt(zuhur_time):8} | "
          f"{fmt(asar_time):8} | {fmt(maghrib_time):8} | {fmt(isyak_time):8} |")

    print("+------------+----------+----------+----------+----------+----------+----------+")

    # --- Write to CSV file ---
    with open(csv_filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow([
            date_str,
            fmt(subuh_time),
            fmt(syuruk_time),
            fmt(zuhur_time),
            fmt(asar_time),
            fmt(maghrib_time),
            fmt(isyak_time),
        ])

    print(f"\n✅ Saved to CSV file: {csv_filename}")


def multiday(lat, lon, ele, tz, y, m, d_start, num_days,
              csv_filename="prayer_times_multi.csv",
              deg_subuh=-18, deg_isha=-18, asar_shadow_length=1):
    """
    Generate prayer times for a sequence of days starting from a given date.
    Saves all to one CSV and prints to screen.
    """

    import csv
    from datetime import date, timedelta

    # --- Prepare CSV ---
    header = ["Date", "Subuh", "Syuruk", "Zuhur", "Asar", "Maghrib", "Isyak"]
    with open(csv_filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

    # --- Loop over each day ---
    for i in range(num_days):
        this_date = date(y, m, d_start) + timedelta(days=i)
        yy, mm, dd = this_date.year, this_date.month, this_date.day

        # Compute each time
        subuh_time   = subuh(lat, lon, ele, tz, yy, mm, dd, deg_subuh)
        syuruk_time  = syuruk(lat, lon, ele, tz, yy, mm, dd)
        zuhur_time,_ = zuhur(lat, lon, ele, tz, yy, mm, dd)
        asar_time    = asar(lat, lon, ele, tz, yy, mm, dd, asar_shadow_length)
        maghrib_time = maghrib(lat, lon, ele, tz, yy, mm, dd)
        isyak_time   = isyak(lat, lon, ele, tz, yy, mm, dd, deg_isha)

        # Format for None
        def fmt(t): return t if t is not None else "--:--:--"

        # Print one line per day
        print(f"{this_date} | {fmt(subuh_time):8} | {fmt(syuruk_time):8} | "
              f"{fmt(zuhur_time):8} | {fmt(asar_time):8} | "
              f"{fmt(maghrib_time):8} | {fmt(isyak_time):8}")

        # Append to CSV
        with open(csv_filename, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                this_date.strftime("%Y-%m-%d"),
                fmt(subuh_time),
                fmt(syuruk_time),
                fmt(zuhur_time),
                fmt(asar_time),
                fmt(maghrib_time),
                fmt(isyak_time),
            ])

    print(f"\n✅ Saved multi-day prayer times to {csv_filename}")
