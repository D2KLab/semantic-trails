import csv
from json.decoder import JSONDecodeError

from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError

geo_names = {}

# load the cities from GeoNames
with open('cities500.txt', encoding='utf8') as fp:
    reader = csv.reader(fp, delimiter='\t')

    for row in reader:
        geo_id = row[0]
        lat = row[4]
        long = row[5]
        geo_names[geo_id] = {'geo_id': geo_id,
                             'lat': lat,
                             'long': long}


print("Number of cities:", len(geo_names))

# download resources with a GeoName identifier from Wikidata
wikidata = {}

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

query = """
SELECT ?geo_id ?item ?country
WHERE 
{
  ?item wdt:P1566 ?geo_id .
  ?item wdt:P17 ?country .
}
"""

offset = 0
limit = 50000

while True:
    try:
        sparql.setQuery(query + " OFFSET " + str(offset) + " LIMIT " + str(limit))
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
    except (EndPointInternalError, JSONDecodeError):
        print("Trying again...")
        continue

    if len(results['results']['bindings']) == 0:
        break

    print("Precessing offset", offset)
    offset += limit

    for result in results['results']['bindings']:
        geo_id = result['geo_id']['value']
        item = result['item']['value']
        country = result['country']['value']

        wikidata[geo_id] = {'geo_id': geo_id,
                            'item': item,
                            'country': country}

print("Downloaded", len(wikidata), "resources")

with open('cities.csv', 'w', encoding='utf8', newline='') as fp:
    writer = csv.writer(fp)
    writer.writerow(["lat", "lon", "name", "admin1", "admin2", "cc"])

    # for all the cities
    for geo_id in geo_names:
        if geo_id in wikidata:
            lat = geo_names[geo_id]['lat']
            long = geo_names[geo_id]['long']
            name = wikidata[geo_id]['item']
            country = wikidata[geo_id]['country']
            writer.writerow([lat, long, name, "", "", country])
