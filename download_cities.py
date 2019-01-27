import csv
import pickle as pkl
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
SELECT ?geo_id ?item ?country ?population
WHERE
{
  ?item wdt:P1566 ?geo_id .
  ?item wdt:P17 ?country .
  OPTIONAL { ?item wdt:P1082 ?population }
}
"""

offset = 0
limit = 50000

while True:
    try:
        sparql.setQuery(query + " OFFSET " + str(offset) +
                        " LIMIT " + str(limit))
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
        try:
            population = result['population']['value']
        except KeyError:
            population = None

        # consider only the first result
        if geo_id not in wikidata:
            wikidata[geo_id] = {'geo_id': geo_id,
                                'item': item,
                                'country': country,
                                'population': population}

print("Downloaded", len(wikidata), "resources")

with open('wikidata.pkl', 'wb') as fp:
    pkl.dump(wikidata, fp, protocol=pkl.HIGHEST_PROTOCOL)

with open('cities.csv', 'w', encoding='utf8', newline='') as fp:
    writer = csv.writer(fp)
    writer.writerow(["lat", "lon", "name", "admin1", "admin2", "cc"])

    # for all the cities
    for geo_id in geo_names:
        if geo_id in wikidata:
            lat = geo_names[geo_id]['lat']
            long = geo_names[geo_id]['long']
            name = wikidata[geo_id]['item'].replace(
                "http://www.wikidata.org/entity/", "wd:")
            country = wikidata[geo_id]['country'].replace(
                "http://www.wikidata.org/entity/", "wd:")
            writer.writerow([lat, long, name, "", "", country])

with open('population.csv', 'w', encoding='utf8', newline='') as fp:
    writer = csv.writer(fp)

    # for all the cities
    for geo_id in geo_names:
        if geo_id in wikidata:
            name = wikidata[geo_id]['item'].replace(
                "http://www.wikidata.org/entity/", "wd:")
            population = wikidata[geo_id]['population']

            if isinstance(population, str):
                population = population.replace(".", "")

            if population is not None:
                writer.writerow([name, population])
