import csv
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, SKOS, XSD
import hashlib
import math
import os
import sys

Schema = Namespace("http://schema.org/")
CategoryNS = Namespace("http://std.eurecom.fr/category/")
FoursquareNS = Namespace("http://www.foursquare.com/v/")
WDNS = Namespace("http://www.wikidata.org/entity/")
DBONS = Namespace("http://dbpedia.org/ontology/")

def read_categories(file):
    categories = []

    with open(file, encoding="utf-8") as fp:
        # Parse CSV
        reader = csv.reader(fp, delimiter=",")
        for row in reader:
            categories.append({
                "id": row[0],
                "label": {
                    "en": row[1],
                    "fr": row[2],
                    "it": row[3]
                }
            })
    fp.close()

    return categories

def create_graph():
    g = Graph()
    g.bind("cat", CategoryNS)
    g.bind("schema", Schema)
    g.bind("foursquare", FoursquareNS)
    g.bind("wd", WDNS)
    g.bind("dbo", DBONS)
    g.bind("skos", SKOS)
    return g

def process_categories(categoriesFile):
    print("Processing categories file: " + categoriesFile)
    g = create_graph()
    categories = read_categories(categoriesFile)
    for cat in categories:
        uri = CategoryNS[cat["id"]]
        g.add( (uri, RDF.type, SKOS.Concept) )
        for lang in cat["label"]:
            g.add( (uri, RDFS.label, Literal(cat["label"][lang], lang=lang)) )
            g.add( (uri, RDFS.isDefinedBy, URIRef("https://developer.foursquare.com/docs/resources/categories")) )
    g.serialize(destination="categories.ttl", format="turtle")
    return g

def process_dataset(datasetFile):
    print("Processing dataset file: " + datasetFile)
    g = create_graph()
    with open(datasetFile + ".csv", encoding="utf-8") as fp:
        # Skip first line (if any)
        next(fp, None)

        print("Calculating total rows...")
        totalRows = sum(1 for line in fp)
        print("Found " + str(totalRows) + " rows")
        fp.seek(0)
        next(fp, None)

        currentFileIndex = 0
        foursquareCache = {}

        # Parse CSV
        reader = csv.reader(fp, delimiter=",")
        for row in reader:
            # trail_id,user_id,venue_id,venue_category,venue_schema,venue_city,venue_country,timestamp
            # 1,1,foursquare:597190d44b78c57f67ddd616,4bf58dd8d48988d198941735,schema:CivicStructure,wd:Q894012,wd:Q43,2017-10-03T14:44:00+03:00
            print("Processing row " + str(reader.line_num) + "/" + str(totalRows) + " (" + str(math.floor(reader.line_num / totalRows * 100)) + "%)")

            # Write current data if needed, to clear memory
            fileIndex = math.floor(reader.line_num / 100000)

            data = {
                "trail_id": row[0],
                "user_id": row[1],
                "venue_id": row[2],
                "venue_category": row[3],
                "venue_schema": row[4],
                "venue_city": row[5],
                "venue_country": row[6],
                "timestamp": row[7]
            }

            if os.path.isfile(datasetFile + "_" + str(fileIndex) + ".ttl"):
                # Skip
                print("Skipping because turtle file already exists")
                continue

            if fileIndex != currentFileIndex:
                g.serialize(destination=datasetFile + "_" + str(currentFileIndex) + ".ttl", format="turtle")
                g = create_graph()
            currentFileIndex = fileIndex

            # Process data
            if data["venue_id"].startswith("foursquare:"):
                data["venue_uri"] = FoursquareNS[data["venue_id"].split(":")[1]]
            else:
                data["venue_uri"] = URIRef(data["venue_id"])

            if data["venue_schema"].startswith("schema:"):
                data["venue_schema"] = Schema[data["venue_schema"].split(":")[1]]
            else:
                data["venue_schema"] = URIRef(data["venue_schema"])

            if data["venue_city"].startswith("wd:"):
                data["venue_city"] = WDNS[data["venue_city"].split(":")[1]]
            else:
                data["venue_city"] = URIRef(data["venue_city"])

            if data["venue_country"].startswith("wd:"):
                data["venue_country"] = WDNS[data["venue_country"].split(":")[1]]
            else:
                data["venue_country"] = URIRef(data["venue_country"])

            #print(data)

            checkinID = "user" + data["user_id"] + "checkin" + data["timestamp"]
            checkinUUID = hashlib.sha1(checkinID.encode("utf8")).hexdigest()
            checkin = URIRef("http://std.eurecom.fr/checkin/" + checkinUUID)
            user = URIRef("http://std.eurecom.fr/user/" + data["user_id"])
            venue = data["venue_uri"]
            category = CategoryNS[data["venue_category"]]

            # Checkin
            g.add( (checkin, RDF.type, Schema.CheckInAction) )
            g.add( (checkin, Schema.agent, user) )
            g.add( (checkin, Schema.location, venue) )
            g.add( (checkin, Schema.startTime, Literal(data["timestamp"], datatype=XSD.dateTime)) )
            g.add( (checkin, Schema.result, URIRef("http://std.eurecom.fr/trail/" + data["trail_id"])) )

            # User
            g.add( (user, RDF.type, Schema.Person) )

            # Venue
            if data["venue_id"] not in foursquareCache:
                foursquareCache[data["venue_id"]] = True

                if data["venue_schema"] != Schema.Place:
                    g.add( (venue, RDF.type, Schema.Place) )
                g.add( (venue, RDF.type, data["venue_schema"]) )
                g.add( (venue, DBONS.category, category) )
                address = BNode()
                g.add( (address, RDF.type, Schema.PostalAddress) )
                g.add( (address, Schema.addressLocality, data["venue_city"]) )
                g.add( (address, Schema.addressCountry, data["venue_country"]) )
                g.add( (venue, Schema.address, address) )

        # end for
        currentFileIndex = currentFileIndex + 1
        g.serialize(destination=datasetFile + "_" + str(currentFileIndex) + ".ttl", format="turtle")

    # end with
    fp.close()

process_categories("categories.csv")
process_dataset(sys.argv[1])
