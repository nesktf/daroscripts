import sys
from dataclasses import dataclass

def on_die(err: str):
    print(err)
    sys.exit(1)

def parse_csv(path, sep, parse_tuple):
    data = []
    def parse_line(line):
        stripped = line.strip()
        if stripped:
            cols = stripped.split(sep)
            t = parse_tuple(cols)
            if t != None:
                data.append(t)

    try:
        first = True
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                if first:
                    first = False
                    continue
                parse_line(line)
        return data, ""
    except FileNotFoundError:
        return None, f"Failed to open {path}"
    except Exception as e:
        return None, f"{e}"

@dataclass
class CsvItem:
    lat: float
    lon: float
    date: str

def clean_coord(coord: str, min: float, max: float):
    digits = "".join(c for c in coord if c.isdigit())
    val = float(digits)
    if (val > 0):
        val = -val
    while (val < min):
        val /= 10
    while (val > max):
        val *= 10
    return round(val, 6)

def parse_tuple(cols, min, max):
    lat = clean_coord(cols[0], min, max)
    if (lat == None):
        return None
    lon = clean_coord(cols[1], min, max)
    if (lon == None):
        return None
    date = cols[5]
    return CsvItem(lat, lon, date)

def make_kml(elems: list[CsvItem], name: str, desc: str, output_path: str):
    header = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{name}</name>
    <description>{desc}</description>
    """
    elem_templ = """
    <Placemark>
      <name>Fuego {id}</name>
      <LookAt>
        <TimeStamp>
          <when>{date}</when>
        </TimeStamp>
        <latitude>{lat}</latitude>
        <longitude>{lon}</longitude>
        <range>500</range>
        <tilt>45</tilt>
        <heading>0</heading>
        <altitudeMode>relativeToGround</altitudeMode>
      </LookAt>
      <Point>
        <coordinates>{lon},{lat},0</coordinates>
      </Point>
    </Placemark>"""
    footer = """
</Document>
</kml>"""
    try:
        with open(output_path, 'w', encoding="utf-8") as f:
            f.write(header)
            for i, elem in enumerate(elems):
                f.write(elem_templ.format(id=i+1, lat=elem.lat, lon=elem.lon, date=elem.date))
            f.write(footer)
            return None
    except Exception as e:
        return f"{e}"


salta_coords = [
    #((-21.627, -68.862), (-26.490, -62.084)), # Salta entero y otros
    ((-24.1870, -68.3840), (-25.2300, -65.8030)), # S.A. de los cobres 1
    ((-23.8230, -67.2530), (-24.0670, -66.9510)), # S.A. de los cobres 2
    ((-23.4360, -66.1900), (-24.1840, -66.0220)), # S.A. de los cobres 3
    ((-23.6770, -66.3490), (-24.2020, -65.9760)), # S.A. de los cobres 4
    ((-24.5570, -66.4890), (-25.6320, -63.5010)), # Centro de Salta 1
    ((-24.3520, -64.2320), (-25.1010, -62.9680)), # Centro de Salta 2
    ((-25.4380, -66.5110), (-26.1850, -64.4570)), # Patitas de Salta 1
    ((-25.7230, -66.8240), (-26.2840, -66.3130)), # Patitas de Salta 2
    ((-22.4360, -64.1300), (-24.7770, -62.6820)), # Cola de Salta 1
    ((-21.2380, -64.1880), (-24.3900, -62.3470)), # Cola de Salta 2
    ((-21.9660, -65.1100), (-23.5060, -63.9870)), # Oran, Iruya, Sta. Victoria 1
    #((-22.4640, -65.3190), (-23.1150, -64.2670)), # Oran, Iruya, Sta. Victoria 2
]

def salta_filter(entries: list[CsvItem]) -> list[CsvItem]:
    out = []
    boxes = []
    for p1, p2 in salta_coords:
        lats = (p1[0], p2[0])
        lons = (p1[1], p2[1])
        boxes.append({
            'lat_min': min(lats),
            'lat_max': max(lats),
            'lon_min': min(lons),
            'lon_max': max(lons)
        })

    out = []
    for entry in entries:
        lat = entry.lat
        lon = entry.lon
        inside = False
        for box in boxes:
            if (box['lat_min'] <= lat <= box['lat_max'] and
                box['lon_min'] <= lon <= box['lon_max']):
                inside = True
                break
        if inside:
            out.append(entry)

    return out

def date_filter(entries: list[CsvItem], min: str, max: str) -> list[CsvItem]:
    out = []
    for entry in entries:
        if (min <= entry.date <= max):
            out.append(entry)
    return out

path =  "./data/modis_2024_Argentina.csv"
sep = ','
outpath = "./data/fuegos_salta.kml"

entries, err = parse_csv(path, sep, lambda c: parse_tuple(c, -65.0, -20.0))
if (entries == None):
    on_die(err)

salta_entries = salta_filter(entries)
date_entries = date_filter(salta_entries, "2024-06-01", "2024-11-30")
err = make_kml(date_entries, "Fuegos en Salta", "Coordenadas de fuegos en Salta", outpath)
if (err != None):
    on_die(err)
