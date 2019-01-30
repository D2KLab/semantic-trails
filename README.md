# Semantic Trails Datasets

This repository contains the code used to generate the Semantic Trails Datasets (STDs). You can download the actual datasets from [figshare](https://doi.org/10.6084/m9.figshare.7429076), while you can query their RDF version at http://std.eurecom.fr/sparql.

## Cities

We first downloaded from [Wikidata](https://www.wikidata.org) the URIs of all the cities and the associated countries available on [GeoNames](https://www.geonames.org), as well as their population, if available. To this purpose, we exploited the `download_cities.py` script.

The input file `cities500.txt` can be obtained [here](http://download.geonames.org/export/dump/), while the output files `cities.csv` and `population.csv` are already available in the repository. If necessary, they can be updated by running `python download_cities.py`.

The format of `cities.csv` is the one required by the library [reverse_geocoder](https://github.com/thampiman/reverse-geocoder). This file will be exploited by the `create_std.py` script.

## Mapping

We mapped the categories of the [Foursquare taxonomy](https://developer.foursquare.com/docs/resources/categories) with the [Schema.org](https://schema.org) vocabulary.

The script `download_categories.py` was used to download the identifiers of such categories from Foursquare, as well as their translations in English, French, and Italian. The obtained categories are listed in the file `categories.csv`. If necessary, it can be updated by running `python download_categories.py`.

The result of the mapping process is available in the `mapping.csv` file. The first column represents the Foursquare category identifier, the second one its English translation, while the third one the corresponding Schema.org URI. This file also contains some category names that were previously used by Foursquare, which we merged with the current identifier. The `mapping.csv` file will be exploited by the `create_std.py` script.

## Datasets

We constructed the STDs by means of the `create_std.py` script. It requires two input files, `checkins.csv` and `venues.csv`, in the same format of the [Global-Scale Check-in Dataset](https://sites.google.com/site/yangdingqi/home/foursquare-dataset), and the previously mentioned `cities.csv`  and `mapping.csv` files. The resulting file can be created by simply running `python create_std.py`.

The resulting datasets are available on [figshare](https://doi.org/10.6084/m9.figshare.7429076), together with a description of the output format.

## RDF Conversion

We converted the CSV datasets into RDF by using the `convert_rdf.py` script. The script takes one parameter, that is the name of the dataset without the extension. For example, `python convert_rdf.py std_2013` will parse `std_2013.csv` and export it to `std_2013.ttl`. If a `categories.csv` file exists, it will also automatically attempt to open and parse it, process the categories, and then export it as `categories.ttl`.

In the following, we provide an example of our [RDF model](rdf_model.svg).

```
<http://std.eurecom.fr/checkin/75d2860eb8ad49789ef63e69e898d03237c67df4> a schema:CheckInAction ;
    schema:agent <http://std.eurecom.fr/user/1> ;
    schema:location <http://www.foursquare.com/v/597190d44b78c57f67ddd616> ;
    schema:result <http://std.eurecom.fr/trail/1> ;
    schema:startTime "2017-10-03T14:44:00+03:00"^^xsd:dateTime .

<http://std.eurecom.fr/user/1> a schema:Person .

<http://www.foursquare.com/v/597190d44b78c57f67ddd616> a schema:CivicStructure,
        schema:Place ;
    dbo:category <http://std.eurecom.fr/category/4bf58dd8d48988d198941735> ;
    schema:address [ a schema:PostalAddress ;
            schema:addressCountry wd:Q43 ;
            schema:addressLocality wd:Q894012 ] .

<http://std.eurecom.fr/category/4bf58dd8d48988d198941735> a skos:Concept ;
    rdfs:label "College Academic Building"@en,
        "Bâtiment universitaire"@fr,
        "Edificio universitario accademico"@it ;
    rdfs:isDefinedBy <https://developer.foursquare.com/docs/resources/categories> .
```

## Team

- Diego Monti <diego.monti@polito.it>
- Enrico Palumbo <enrico.palumbo@ismb.it>
- Giuseppe Rizzo <giuseppe.rizzo@ismb.it>
- Raphaël Troncy <raphael.troncy@eurecom.fr>
- Thibault Ehrhart <thibault.ehrhart@eurecom.fr>
- Maurizio Morisio <maurizio.morisio@polito.it>
