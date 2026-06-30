import urllib.request, urllib.parse, json, textwrap

def ckan_show(name):
    url = f"https://data.nt.gov.au/api/3/action/package_show?id={urllib.parse.quote(name)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)["result"]

pkg = ckan_show("sites-of-conservation-significance")
print("TITLE:", pkg.get("title"), "| license:", pkg.get("license_id"))
notes = (pkg.get("notes") or "").replace("\r"," ")
print("\nNOTES:\n", textwrap.fill(notes[:1200], 90))

print("\nALL RESOURCES (no filter):")
for r in pkg.get("resources", []):
    print(f"\n  name:   {r.get('name')}")
    print(f"  format: {r.get('format')!r}")
    print(f"  url:    {r.get('url')}")
