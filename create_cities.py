import csv
import gzip
import json

from haversine import haversine
from unidecode import unidecode

cities = []
names = {}

# load the cities from GeoNames
# http://download.geonames.org/export/dump/cities500.zip
with open('cities500.txt', encoding='utf8') as fp:
    reader = csv.reader(fp, delimiter='\t')

    for row in reader:
        ascii_name = unidecode(row[1]).lower()

        city = {'geoname_id': row[0],
                'name': row[1],
                'latitude': float(row[4]),
                'longitude': float(row[5]),
                'country': row[8],
                'population': row[14],
                'wikidata': "",
                'sitelinks': 0}

        cities.append(city)

        if ascii_name not in names:
            names[ascii_name] = [city]
        else:
            names[ascii_name].append(city)

wikidata_counter = 0
matches_counter = 0

with gzip.open('wikidata.json.gz', 'rt') as fp:
    for line in fp:
        if line[0] == '[' or line[0] == ']':
            continue

        line = line.strip()

        if line[-1] == ',':
            line = line[:-1]

        wikidata_counter += 1

        if wikidata_counter % 10000 == 0:
            print("Wikidata entity:", wikidata_counter)

        entity = json.loads(line)

        # the entity must have an English label
        if 'en' not in entity['labels']:
            continue

        # the entity must have geographical coordinates
        if 'P625' not in entity['claims']:
            continue

        try:
            entity_label = unidecode(entity['labels']['en']['value']).lower()
        except KeyError:
            continue

        # find candidate cities
        if entity_label not in names:
            continue

        candidates = names[entity_label]

        try:
            entity_coord = entity['claims']['P625'][0]['mainsnak']['datavalue']['value']
            entity_latitude = float(entity_coord['latitude'])
            entity_longitude = float(entity_coord['longitude'])
        except (KeyError, ValueError):
            continue

        # find the matches
        matches = []

        for city in candidates:
            distance = abs(haversine((city['latitude'], city['longitude']),
                                     (entity_latitude, entity_longitude)))

            # there is a match if the distance is less than 10 km
            if distance < 10:
                matches.append(city)

        # consider only single matches
        if len(matches) == 1:
            sitelinks = len(entity['sitelinks'])

            # consider the entity with more sitelinks
            if matches[0]['sitelinks'] <= sitelinks:
                matches_counter += 1
                matches[0]['wikidata'] = entity['id']
                matches[0]['sitelinks'] = sitelinks

print("Number of cities:", len(cities))
print("Number of matches:", matches_counter)

# save the cities
with open('cities.csv', 'w', encoding='utf8', newline='') as fp:
    writer = csv.writer(fp)
    writer.writerow(["lat", "lon", "name", "admin1", "admin2", "cc"])

    for city in cities:
        writer.writerow([city['latitude'], city['longitude'],
                         city['geoname_id'], city['name'], city['country'], city['wikidata']])

# save the population
with open('population.csv', 'w', encoding='utf8', newline='') as fp:
    writer = csv.writer(fp)

    for city in cities:
        if city['population'] != "0":
            writer.writerow([city['geoname_id'], city['population']])
