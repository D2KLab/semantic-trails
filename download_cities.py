from SPARQLWrapper import SPARQLWrapper, JSON
import csv


def download(rdf_type, file):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")

    query = """
    select ?item ?lat ?long ?country { 
    ?item rdf:type """ + rdf_type + """ .
    ?item geo:lat ?lat .
    ?item geo:long ?long .
    ?item dbo:country ?country .
    }
    """

    offset = 0
    limit = 10000

    fp = open(file, 'w', encoding='utf8', newline='')
    writer = csv.writer(fp)
    writer.writerow(["lat", "lon", "name", "admin1", "admin2", "cc"])

    while True:
        sparql.setQuery(query + " offset " + str(offset) + " limit " + str(limit))
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if len(results['results']['bindings']) == 0:
            break

        print("Precessing offset", offset)
        offset += limit

        for result in results['results']['bindings']:
            name = result['item']['value']
            lat = result['lat']['value']
            long = result['long']['value']
            country = result['country']['value']
            writer.writerow([lat, long, name, "", "", country])


if __name__ == '__main__':
    download("dbo:City", "cities.csv")
