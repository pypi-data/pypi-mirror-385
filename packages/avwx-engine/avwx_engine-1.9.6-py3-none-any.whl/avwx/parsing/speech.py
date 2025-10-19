"""Contains functions for converting translations into a speech string.
Currently only supports METAR.
"""

# stdlib
from __future__ import annotations

import re
from typing import TYPE_CHECKING

# module
import avwx.parsing.translate.base as translate_base
import avwx.parsing.translate.taf as translate_taf
from avwx.parsing import core
from avwx.static.core import SPOKEN_UNITS

if TYPE_CHECKING:
    from avwx.structs import Code, MetarData, Number, TafData, TafLineData, Timestamp, Units


def ordinal(n: int) -> str | None:
    """Convert an int to it spoken ordinal representation."""
    if n < 0:
        return None
    return str(n) + "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4]


def _format_plural_unit(value: str, unit: str) -> str:
    spoken = SPOKEN_UNITS.get(unit, unit)
    value = re.sub(r"(?<=\b1)" + unit, f" {spoken}", value)  # 1 knot
    return re.sub(r"(?<=\d)+" + unit, f" {spoken}s", value)  # 2 knots


def wind(
    direction: Number,
    speed: Number,
    gust: Number | None,
    vardir: list[Number] | None = None,
    unit: str = "kt",
) -> str:
    """Format wind details into a spoken word string."""
    val = translate_base.wind(direction, speed, gust, vardir, unit, cardinals=False, spoken=True)
    if val and unit in SPOKEN_UNITS:
        val = _format_plural_unit(val, unit)
    return "Winds " + (val or "unknown")


def temperature(header: str, temp: Number | None, unit: str = "C") -> str:
    """Format temperature details into a spoken word string."""
    if not temp or temp.value is None:
        return f"{header} unknown"
    unit = SPOKEN_UNITS.get(unit, unit)
    use_s = "" if temp.spoken in ("one", "minus one") else "s"
    return " ".join((header, temp.spoken, f"degree{use_s}", unit))


def visibility(vis: Number | None, unit: str = "m") -> str:
    """Format visibility details into a spoken word string."""
    if not vis:
        return "Visibility unknown"
    if vis.value is None or "/" in vis.repr:
        ret_vis = vis.spoken
    else:
        ret_vis = translate_base.visibility(vis, unit=unit)
        if unit == "m":
            unit = "km"
        ret_vis = ret_vis[: ret_vis.find(" (")].lower().replace(unit, "").strip()
        ret_vis = core.spoken_number(core.remove_leading_zeros(ret_vis))
    ret = f"Visibility {ret_vis}"
    if unit in SPOKEN_UNITS:
        if "/" in vis.repr and "half" not in ret:
            ret += " of a"
        ret += f" {SPOKEN_UNITS[unit]}"
        if ("one half" not in ret or " and " in ret) and "of a" not in ret:
            ret += "s"
    else:
        ret += unit
    return ret


def altimeter(alt: Number | None, unit: str = "inHg") -> str:
    """Format altimeter details into a spoken word string."""
    ret = "Altimeter "
    if not alt:
        ret += "unknown"
    elif unit == "inHg":
        ret += core.spoken_number(str(alt.value).ljust(5, "0"), literal=True)
    elif unit == "hPa":
        ret += core.spoken_number(str(alt.value).zfill(4), literal=True)
    return ret


def wx_codes(codes: list[Code]) -> str:
    """Format wx codes into a spoken word string."""
    ret = []
    for code in codes:
        item = code.value
        if item.startswith("Vicinity"):
            item = item.removeprefix("Vicinity ") + " in the Vicinity"
        ret.append(item)
    return ". ".join(ret)


def type_and_times(
    type: str | None,  # noqa: A002
    start: Timestamp | None,
    end: Timestamp | None,
    probability: Number | None = None,
) -> str:
    """Format line type and times into the beginning of a spoken line string."""
    if not type:
        return ""
    start_time = start.dt.hour if start and start.dt else "an unknown start time"
    end_time = end.dt.hour if end and end.dt else "an unknown end time"
    if type == "BECMG":
        return f"At {start_time or 'midnight'} zulu becoming"
    ret = f"From {start_time or 'midnight'} to {end_time or 'midnight'} zulu,"
    if probability and probability.value:
        ret += f" there's a {probability.value}% chance for"
    if type == "INTER":
        ret += " intermittent"
    elif type == "TEMPO":
        ret += " temporary"
    return ret


def wind_shear(shear: str, unit_alt: str = "ft", unit_wind: str = "kt") -> str:
    """Format wind shear string into a spoken word string."""
    value = translate_taf.wind_shear(shear, unit_alt, unit_wind, spoken=True)
    if not value:
        return "Wind shear unknown"
    for unit in (unit_alt, unit_wind):
        if unit in SPOKEN_UNITS:
            value = _format_plural_unit(value, unit)
    return value


def metar(data: MetarData, units: Units) -> str:
    """Convert MetarData into a string for text-to-speech."""
    speech = []
    if data.wind_direction and data.wind_speed:
        speech.append(
            wind(
                data.wind_direction,
                data.wind_speed,
                data.wind_gust,
                data.wind_variable_direction,
                units.wind_speed,
            )
        )
    if data.visibility:
        speech.append(visibility(data.visibility, units.visibility))
    speech.append(translate_base.clouds(data.clouds, units.altitude).replace(" - Reported AGL", ""))
    if data.wx_codes:
        speech.append(wx_codes(data.wx_codes))
    if data.temperature:
        speech.append(temperature("Temperature", data.temperature, units.temperature))
    if data.dewpoint:
        speech.append(temperature("Dew point", data.dewpoint, units.temperature))
    if data.altimeter:
        speech.append(altimeter(data.altimeter, units.altimeter))
    return (". ".join([el for el in speech if el])).replace(",", ".")


def taf_line(line: TafLineData, units: Units) -> str:
    """Convert TafLineData into a string for text-to-speech."""
    speech = []
    start = type_and_times(line.type, line.start_time, line.end_time, line.probability)
    if line.wind_direction and line.wind_speed:
        speech.append(
            wind(
                line.wind_direction,
                line.wind_speed,
                line.wind_gust,
                line.wind_variable_direction,
                unit=units.wind_speed,
            )
        )
    if line.wind_shear:
        speech.append(wind_shear(line.wind_shear, units.altitude, units.wind_speed))
    if line.visibility:
        speech.append(visibility(line.visibility, units.visibility))
    if line.altimeter:
        speech.append(altimeter(line.altimeter, units.altimeter))
    if line.wx_codes:
        speech.append(wx_codes(line.wx_codes))
    speech.append(translate_base.clouds(line.clouds, units.altitude).replace(" - Reported AGL", ""))
    if line.turbulence:
        speech.append(translate_taf.turb_ice(line.turbulence, units.altitude))
    if line.icing:
        speech.append(translate_taf.turb_ice(line.icing, units.altitude))
    return f"{start} " + (". ".join([el for el in speech if el])).replace(",", ".")


def taf(data: TafData, units: Units) -> str:
    """Convert TafData into a string for text-to-speech."""
    try:
        month = data.start_time.dt.strftime(r"%B")  # type: ignore
        day = ordinal(data.start_time.dt.day) or "Unknown"  # type: ignore
        ret = f"Starting on {month} {day} - "
    except AttributeError:
        ret = ""
    return ret + ". ".join([taf_line(line, units) for line in data.forecast])
