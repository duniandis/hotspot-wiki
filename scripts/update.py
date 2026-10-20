import os,json,csv,io,datetime,urllib.request,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
geo=json.loads((root/'areal.geojson').read_text())
def coords(g):
 if isinstance(g,list):
  if len(g)>=2 and all(isinstance(z,(int,float)) for z in g[:2]):yield g[:2]
  else:
   for x in g:yield from coords(x)
pts=list(coords(geo['features'][0]['geometry']['coordinates']))
west=min(x for x,y in pts)-.12;east=max(x for x,y in pts)+.12;south=min(y for x,y in pts)-.12;north=max(y for x,y in pts)+.12
key=os.getenv('FIRMS_MAP_KEY','').strip()
if not key:raise SystemExit('Set repository secret FIRMS_MAP_KEY')
allrows=[];errors=[]
for source in ['VIIRS_NOAA20_NRT','VIIRS_SNPP_NRT','VIIRS_NOAA21_NRT']:
 url=f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{west:.5f},{south:.5f},{east:.5f},{north:.5f}/7'
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'CompanyHotspotMonitor/1.0'})
  with urllib.request.urlopen(req,timeout=75) as r: data=r.read().decode('utf-8-sig')
  rows=list(csv.DictReader(io.StringIO(data)))
  if rows and 'latitude' not in rows[0]:raise ValueError(data[:160])
  allrows.extend(rows)
 except Exception as e:errors.append(f'{source}: {e}')
if errors:raise SystemExit('FIRMS retrieval failed: '+'; '.join(errors))
(root/'hotspots.json').write_text(json.dumps({'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='minutes'),'hotspots':allrows},ensure_ascii=False))
print('Saved',len(allrows),'hotspots')
