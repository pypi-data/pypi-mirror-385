import datetime
from math import acos, asin, atan2, cos, degrees, radians, sin, tan, sqrt

def julianday(date_or_dt: datetime.date | datetime.datetime) -> float:
    """
    Calculate the Julian Day number for a date or datetime (UTC).
    Handles both date (midnight UTC) and datetime (exact time).
    """
    if isinstance(date_or_dt, datetime.datetime):
        year = date_or_dt.year
        month = date_or_dt.month
        day = date_or_dt.day
        hour = date_or_dt.hour
        minute = date_or_dt.minute
        second = date_or_dt.second
    else:
        year = date_or_dt.year
        month = date_or_dt.month
        day = date_or_dt.day
        hour = minute = second = 0

    if month <= 2:
        year -= 1
        month += 12

    a = year // 100
    b = 2 - a + (a // 4)
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    return jd + (hour + minute/60 + second/3600) / 24.0

def julianday_to_juliancentury(jd: float) -> float:
    """Convert a Julian Day number to a Julian Century."""
    return (jd - 2451545.0) / 36525.0

def geom_mean_long_sun(jc: float) -> float:
    """Calculate the geometric mean longitude of the sun."""
    l0 = 280.46646 + jc * (36000.76983 + 0.0003032 * jc)
    return l0 % 360.0

def geom_mean_anomaly_sun(jc: float) -> float:
    """Calculate the geometric mean anomaly of the sun."""
    return 357.52911 + jc * (35999.05029 - 0.0001537 * jc)

def eccentric_location_earth_orbit(jc: float) -> float:
    """Calculate the eccentricity of Earth's orbit."""
    return 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc)

def sun_eq_of_center(jc: float) -> float:
    """Calculate the equation of the center of the sun."""
    m = geom_mean_anomaly_sun(jc)
    mrad = radians(m)
    sinm = sin(mrad)
    sin2m = sin(2 * mrad)
    sin3m = sin(3 * mrad)
    c = (sinm * (1.914602 - jc * (0.004817 + 0.000014 * jc)) +
         sin2m * (0.019993 - 0.000101 * jc) +
         sin3m * 0.000289)
    return c

def sun_true_long(jc: float) -> float:
    """Calculate the sun's true longitude."""
    l0 = geom_mean_long_sun(jc)
    c = sun_eq_of_center(jc)
    return l0 + c

def sun_apparent_long(jc: float) -> float:
    """Calculate the sun's apparent longitude with nutation correction (Meeus Ch. 25)."""
    l0 = geom_mean_long_sun(jc)
    m = geom_mean_anomaly_sun(jc)
    c = sun_eq_of_center(jc)
    lambda_geo = l0 + c
    omega = 125.04 - 1934.136 * jc
    nutation_long = -0.0048 * sin(radians(2 * omega))  # Nutation correction
    return (lambda_geo + nutation_long - 0.00569) % 360.0

def sun_distance(jc: float) -> float:
    """Calculate the distance to the Sun in astronomical units (AU)."""
    e = eccentric_location_earth_orbit(jc)
    m = geom_mean_anomaly_sun(jc)
    c = sun_eq_of_center(jc)
    v = m + c  # Anomalía verdadera
    vrad = radians(v)
    r = 1.000001018 * (1 - e**2) / (1 + e * cos(vrad))  # Distancia en AU
    return r

def mean_obliquity_of_ecliptic(jc: float) -> float:
    """Calculate the mean obliquity of the ecliptic."""
    seconds = 21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813))
    return 23.0 + (26.0 + (seconds / 60.0)) / 60.0

def obliquity_correction(jc: float) -> float:
    """Calculate the corrected obliquity of the ecliptic."""
    e0 = mean_obliquity_of_ecliptic(jc)
    omega = 125.04 - 1934.136 * jc
    return e0 + 0.00256 * cos(radians(omega))

def sun_declination(jc: float) -> float:
    """Calculate the sun's declination."""
    e = obliquity_correction(jc)
    lambd = sun_apparent_long(jc)
    sint = sin(radians(e)) * sin(radians(lambd))
    return degrees(asin(sint))

def eq_of_time(jc: float) -> float:
    """Calculate the equation of time (in minutes)."""
    l0 = geom_mean_long_sun(jc)
    e = eccentric_location_earth_orbit(jc)
    m = geom_mean_anomaly_sun(jc)
    y = tan(radians(obliquity_correction(jc)) / 2.0) ** 2

    sin2l0 = sin(2.0 * radians(l0))
    sinm = sin(radians(m))
    cos2l0 = cos(2.0 * radians(l0))
    sin4l0 = sin(4.0 * radians(l0))
    sin2m = sin(2.0 * radians(m))

    etime = (y * sin2l0 - 2.0 * e * sinm +
             4.0 * e * y * sinm * cos2l0 -
             0.5 * y * y * sin4l0 -
             1.25 * e * e * sin2m)
    return degrees(etime) * 4.0

def refraction_at_zenith(zenith: float) -> float:
    """Calculate the atmospheric refraction correction for the given zenith angle (in degrees)."""
    if zenith < 0 or zenith > 90:
        return 0.0
    # Convert zenith to radians
    zenith_rad = radians(zenith)
    # Refraction formula (Bennett 1982, used in Astral)
    tan_zenith = tan(zenith_rad)
    if zenith > 85.0:
        # For high zenith angles, use a more complex formula
        refraction = (
            58.294 / tan_zenith
            - 0.0668 / (tan_zenith ** 3)
            + 0.000087 / (tan_zenith ** 5)
        ) / 3600.0
    else:
        refraction = (58.276 / tan_zenith) / 3600.0
    return refraction

def adjust_to_horizon(elevation: float) -> float:
    """Calculate the extra degrees of depression due to the observer's elevation."""
    if elevation <= 0:
        return 0.0
    r = 6356900  # Radius of the Earth in meters
    a1 = r
    h1 = r + elevation
    theta1 = acos(a1 / h1)
    return degrees(theta1)

def hour_angle(latitude: float, declination: float, zenith: float, direction: str) -> float:
    """Calculate the hour angle of the sun for sunrise or sunset."""
    latitude_rad = radians(latitude)
    declination_rad = radians(declination)
    zenith_rad = radians(zenith)

    h = (cos(zenith_rad) - sin(latitude_rad) * sin(declination_rad)) / (
        cos(latitude_rad) * cos(declination_rad)
    )
    if abs(h) > 1:
        raise ValueError("Sun does not reach the specified zenith angle.")
    hour_angle = acos(h)
    if direction == "setting":
        hour_angle = -hour_angle
    return hour_angle

def sunrise_sunset(
    latitude: float,
    longitude: float,
    date: datetime.date,
    elevation: float = 0.0,
    timezone: datetime.timezone = datetime.timezone.utc,
    with_refraction: bool = True
) -> tuple[datetime.datetime, datetime.datetime]:
    """Calculate sunrise and sunset times for a given location, date, and elevation."""
    SUN_APPARENT_RADIUS = 959.63 / 3600.0  # ≈ 0.2665639 degrees
    zenith = 90.0 + SUN_APPARENT_RADIUS  # Base zenith angle for sunrise/sunset

    # Adjust zenith for elevation
    adjustment_for_elevation = adjust_to_horizon(elevation)
    adjusted_zenith = zenith + adjustment_for_elevation

    # Adjust zenith for refraction if enabled
    if with_refraction:
        adjusted_zenith += refraction_at_zenith(adjusted_zenith)

    # Limit latitude to avoid numerical issues
    if latitude > 89.8:
        latitude = 89.8
    elif latitude < -89.8:
        latitude = -89.8

    jd = julianday(date)
    jc = julianday_to_juliancentury(jd)
    declination = sun_declination(jc)
    eqtime = eq_of_time(jc)

    # Calculate hour angles for sunrise and sunset
    try:
        ha_rising = hour_angle(latitude, declination, adjusted_zenith, "rising")
        ha_setting = hour_angle(latitude, declination, adjusted_zenith, "setting")
    except ValueError:
        return None, None

    # Time offset in minutes
    delta_rising = -longitude - degrees(ha_rising)
    delta_setting = -longitude - degrees(ha_setting)

    time_utc_rising = 720.0 + (delta_rising * 4.0) - eqtime
    time_utc_setting = 720.0 + (delta_setting * 4.0) - eqtime

    # Adjust for negative or large values
    if time_utc_rising < -720.0:
        time_utc_rising += 1440
    if time_utc_setting < -720.0:
        time_utc_setting += 1440

    # Convert to datetime
    sunrise_utc = datetime.datetime(date.year, date.month, date.day, tzinfo=datetime.timezone.utc)
    sunrise_utc += datetime.timedelta(minutes=time_utc_rising)
    sunset_utc = datetime.datetime(date.year, date.month, date.day, tzinfo=datetime.timezone.utc)
    sunset_utc += datetime.timedelta(minutes=time_utc_setting)

    # Convert to local timezone
    sunrise_local = sunrise_utc.astimezone(timezone)
    sunset_local = sunset_utc.astimezone(timezone)
    return sunrise_local, sunset_local

def noon(
    longitude: float,
    date: datetime.date,
    timezone: datetime.timezone = datetime.timezone.utc,
) -> datetime.datetime:
    """Calculate solar noon time for a given location and date."""
    jd = julianday(date)
    jc = julianday_to_juliancentury(jd)
    eqtime = eq_of_time(jc)
    time_utc = (720.0 - (4 * longitude) - eqtime)  # minutos
    noon_utc = datetime.datetime(date.year, date.month, date.day, tzinfo=datetime.timezone.utc) \
        + datetime.timedelta(minutes=time_utc)
    return noon_utc.astimezone(timezone)