import csv

geonames = []

# load the cities from GeoNames
# http://download.geonames.org/export/dump/cities500.zip
with open('cities500.txt', encoding='utf8') as fp:
    reader = csv.reader(fp, delimiter='\t')

    for row in reader:
        geonames.append({'geoname_id': row[0],
                         'name': row[1],
                         'latitude': row[4],
                         'longitude': row[5],
                         'country': row[8],
                         'population': row[14]})

print("Number of cities:", len(geonames))

with open('cities.csv', 'w', encoding='utf8', newline='') as fp:
    writer = csv.writer(fp)
    writer.writerow(["lat", "lon", "name", "admin1", "admin2", "cc"])

    # for all the cities
    for city in geonames:
        writer.writerow([city['latitude'], city['longitude'],
                         city['geoname_id'], city['name'], city['country'], ""])

with open('population.csv', 'w', encoding='utf8', newline='') as fp:
    writer = csv.writer(fp)

    # for all the cities
    for city in geonames:
        if city['population'] != "0":
            writer.writerow([city['geoname_id'], city['population']])
