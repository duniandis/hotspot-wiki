import os
import json
import csv
import io
import datetime
import urllib.request
import urllib.error
import pathlib

root = pathlib.Path(__file__).resolve().parents[1]
geo = json.loads((root / 'areal.geojson').read_text(encoding='utf-8'))

def coords(g):
    if isinstance(g, list):
        if len(g) >= 2 and all(isinstance(z, (int, float)) for z in g[:2]):
            yield g[:2]
        else:
            for x in g:
                yield from coords(x)

pts = []
for feature in geo['features']:
    pts.extend(coords(feature['geometry']['coordinates']))
if not pts:
    raise SystemExit('No coordinates found in areal.geojson')
west = min(x for x, y in pts) - .12
east = max(x for x, y in pts) + .12
south = min(y for x, y in pts) - .12
north = max(y for x, y in pts) + .12
bbox = f'{west:.5f},{south:.5f},{east:.5f},{north:.5f}'
key = os.getenv('FIRMS_MAP_KEY', '').strip()
if not key:
    raise SystemExit('Set repository secret FIRMS_MAP_KEY')

sources = ['VIIRS_NOAA20_NRT', 'VIIRS_SNPP_NRT', 'VIIRS_NOAA21_NRT']
allrows, errors, succeeded = [], [], []
for source in sources:
    url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{bbox}/5'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CompanyHotspotMonitor/1.0'})
        with urllib.request.urlopen(req, timeout=75) as response:
            data = response.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(data))
        if not reader.fieldnames or 'latitude' not in reader.fieldnames or 'longitude' not in reader.fieldnames:
            raise ValueError('Unexpected FIRMS CSV response: ' + data[:160])
        rows = list(reader)
        for row in rows:
            row['source'] = source
        allrows.extend(rows)
        succeeded.append(source)
        print(f'{source}: {len(rows)} hotspots')
    except urllib.error.HTTPError as exc:
        detail = exc.read(500).decode('utf-8', errors='replace')
        errors.append(f'{source}: HTTP {exc.code}: {detail[:250]}')
    except Exception as exc:
        errors.append(f'{source}: {exc}')

if errors:
    print('FIRMS warnings: ' + '; '.join(errors))
if not succeeded:
    raise SystemExit('FIRMS retrieval failed for all sources; existing hotspots.json was preserved')

# Preserve previous observations for a rolling 7-day display window.
output = root / 'hotspots.json'
oldrows = []
if output.exists():
    try:
        oldrows = json.loads(output.read_text(encoding='utf-8')).get('hotspots', [])
    except (ValueError, OSError):
        pass
cutoff = datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=6)
merged = {}
for row in oldrows + allrows:
    try:
        d = datetime.date.fromisoformat(row['acq_date'])
        if d < cutoff:
            continue
        identity = (row.get('source', row.get('satellite', '')), row.get('latitude'), row.get('longitude'), row.get('acq_date'), row.get('acq_time'))
        merged[identity] = row
    except (ValueError, KeyError, TypeError):
        continue

output.write_text(json.dumps({
    'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='minutes'),
    'hotspots': list(merged.values()),
    'sources_ok': succeeded,
    'sources_failed': errors
}, ensure_ascii=False), encoding='utf-8')
print(f'Saved {len(merged)} hotspots; successful sources: {len(succeeded)}/{len(sources)}')
