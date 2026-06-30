import urllib.request, json

def ckan(q, rows=8):
    url = f"https://data.nt.gov.au/api/3/action/package_search?q={urllib.parse.quote(q)}&rows={rows}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)

import urllib.parse
for q in ["Sites of Conservation Significance", "Sites of Botanical Significance"]:
    print("="*70)
    print("QUERY:", q)
    res = ckan(q)
    print("count:", res["result"]["count"])
    for pkg in res["result"]["results"][:4]:
        print(f"\n  TITLE: {pkg.get('title')}")
        print(f"  name:  {pkg.get('name')}")
        print(f"  org:   {pkg.get('organization',{}).get('title')}")
        print(f"  lic:   {pkg.get('license_id')}")
        for res_item in pkg.get("resources", []):
            fmt = res_item.get("format")
            if fmt and fmt.upper() in ("SHP","ZIP","GDB","GEOJSON","KML","SHAPEFILE"):
                print(f"    -> [{fmt}] {res_item.get('name')}")
                print(f"       url: {res_item.get('url')}")
