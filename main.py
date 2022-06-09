import json

import requests

p = {"@id":"test/5fcceff2336552256032"}

url = "https://sandbox.dissco.tech/search?query=7cbd969d1ef34a51a8ec"

#r = requests.get(url, params=p)
r2 = requests.get(url).json()['results']
print(r2)


# CURATED_OBJECT_ID = r["results"][0]["content"]["ods:authoritative"]["ods:physicalSpecimenId"]
# CURATED_OBJECT_ID_TYPE = "Physical Specimen ID"

#print(json.dumps(r, indent=4, sort_keys=False))
