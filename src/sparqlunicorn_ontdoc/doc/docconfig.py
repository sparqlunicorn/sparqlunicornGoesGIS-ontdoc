
class DocConfig:

    rdfformats = ["ttl", "trix", "trig", "n3", "nquads", "nt", "xml"]

    version="SPARQLing Unicorn QGIS Plugin OntDoc Script 0.17"

    versionurl="https://github.com/sparqlunicorn/sparqlunicornGoesGIS-ontdoc"

    bibtextypemappings={"http://purl.org/ontology/bibo/Document":"@misc","http://purl.org/ontology/bibo/Article":"@article",
                        "http://purl.org/ontology/bibo/AcademicArticle": "@article",
                        "http://purl.org/ontology/bibo/Thesis":"@phdthesis","http://purl.org/ontology/bibo/BookSection":"@inbook",
                        "http://purl.org/ontology/bibo/EditedBook": "@book","http://purl.org/ontology/bibo/Report": "@report",
                        "http://purl.org/ontology/bibo/Book":"@book","http://purl.org/ontology/bibo/Proceedings":"@inproceedings"}

    baselayers={
        "OpenStreetMap (OSM)":{"url":"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png","default":True,"type":"tile"}
    }

    lexicontypes = {
        "http://www.w3.org/ns/lemon/lexicog#Entry": "","http://www.w3.org/ns/lemon/ontolex#Entry": "",
        "http://www.w3.org/ns/lemon/lexicog#LexicalEntry": "","http://www.w3.org/ns/lemon/ontolex#LexicalEntry": "",
        "http://www.w3.org/ns/lemon/ontolex#Word": "","http://www.w3.org/ns/lemon/lexicog#Word": ""
    }

    #,"http://www.w3.org/ns/lemon/ontolex#Form":""

    metadatanamespaces=["http://purl.org/dc/terms/","http://purl.org/dc/elements/1.1/","http://www.w3.org/ns/prov#","http://www.w3.org/ns/prov-o/","http://creativecommons.org/ns#","http://www.w3.org/ns/dcat#","http://purl.org/cerif/frapo/","http://www.lido-schema.org/"]

    collectionclasses = {
                         "http://www.w3.org/2006/vcard/ns#Group":"personcollection",
                         "http://purl.org/ontology/bibo/Collection":"bibcollection",
                         "http://www.w3.org/ns/dcat#Catalog":"datasetcollection",
                         "http://www.opengis.net/ont/geosparql#FeatureCollection": "geocollection",
                         "http://www.w3.org/ns/lemon/lime#Lexicon": "lexicon",
                         "http://www.w3.org/ns/sosa/ObservationCollection": "observationcollection",
                         "http://www.opengis.net/ont/geosparql#GeometryCollection": "geocollection",
                         "http://www.opengis.net/ont/geosparql#SpatialObjectCollection": "geocollection",
                         "http://www.w3.org/2004/02/skos/core#Collection": "collection",
                         "http://www.w3.org/2004/02/skos/core#OrderedCollection": "collection",
                         "https://www.w3.org/ns/activitystreams#Collection": "collection",
                         "https://www.w3.org/ns/activitystreams#OrderedCollection": "collection"
    }

    classToCollectionClass={
        "http://www.opengis.net/ont/geosparql#SpatialObject": {"class": "http://www.opengis.net/ont/geosparql#SpatialObjectCollection","prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/geosparql#Feature":{"class":"http://www.opengis.net/ont/geosparql#FeatureCollection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.opengis.net/ont/geosparql#Geometry": {"class":"http://www.opengis.net/ont/geosparql#GeometryCollection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://www.w3.org/2006/vcard/ns#Individual": {"class":"http://www.w3.org/2006/vcard/ns#Group","prop":"http://www.w3.org/2006/vcard/ns#hasMember"},
        "http://xmlns.com/foaf/0.1/Person": {"class":"http://www.w3.org/2006/vcard/ns#Group","prop":"http://www.w3.org/2006/vcard/ns#hasMember"},
        "http://www.w3.org/ns/lemon/ontolex#LexicalEntry": {"class":"http://www.w3.org/ns/lemon/lime#Lexicon","prop":"http://www.w3.org/ns/lemon/lexicog#entry"},
        "http://www.w3.org/ns/dcat#Dataset": {"class":"http://www.w3.org/ns/dcat#Catalog","prop":"http://www.w3.org/ns/dcat#dataset"},
        "http://www.w3.org/ns/sosa/Observation":{"class":"http://www.w3.org/ns/sosa/ObservationCollection","prop":"http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Document": {"class": "http://purl.org/ontology/bibo/Collection",
                                                   "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Article": {"class": "http://purl.org/ontology/bibo/Collection",
                                                  "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/AcademicArticle": {"class": "http://purl.org/ontology/bibo/Collection",
                                                          "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Thesis": {"class": "http://purl.org/ontology/bibo/Collection",
                                                 "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/BookSection": {"class": "http://purl.org/ontology/bibo/Collection",
                                                      "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/EditedBook": {"class": "http://purl.org/ontology/bibo/Collection",
                                                     "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Report": {"class": "http://purl.org/ontology/bibo/Collection",
                                                 "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Book": {"class": "http://purl.org/ontology/bibo/Collection",
                                               "prop": "http://www.w3.org/2000/01/rdf-schema#member"},
        "http://purl.org/ontology/bibo/Proceedings": {"class": "http://purl.org/ontology/bibo/Collection",
                                                      "prop": "http://www.w3.org/2000/01/rdf-schema#member"}
    }

    geoliteraltypes=["http://www.opengis.net/ont/geosparql#wktLiteral","http://www.opengis.net/ont/geosparql#gmlLiteral","http://www.opengis.net/ont/geosparql#kmlLiteral","http://www.opengis.net/ont/geosparql#geoJSONLiteral","http://www.opengis.net/ont/geosparql#dggsLiteral"]

    timeproperties=["http://www.cidoc-crm.org/cidoc-crm/P79_beginning_is_qualified_by","http://www.cidoc-crm.org/cidoc-crm/P80_end_is_qualified_by","http://www.w3.org/2006/time#inXSDDateTime","http://www.w3.org/2006/time#inXSDDate","http://www.w3.org/2006/time#inXSDDateTimeStamp","http://www.w3.org/2006/time#inXSDgYear","http://www.w3.org/2006/time#inXSDgYearMonth"]

    timepointerproperties=["http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span","http://www.w3.org/2006/time#hasTime", "http://www.w3.org/2006/time#hasDuration", "http://www.w3.org/2006/time#hasBeginning", "http://www.w3.org/2006/time#hasEnd", "http://www.w3.org/ns/sosa/phenomenonTime", "http://www.w3.org/ns/sosa/resultTime"]

    timeliteraltypes={
    "http://www.w3.org/2001/XMLSchema#gYear":"http://www.ontology-of-units-of-measure.org/resource/om-2/year",
    "http://www.w3.org/2006/time#generalYear":"http://www.w3.org/2006/time#unitYear",
    "http://www.w3.org/2001/XMLSchema#gMonth":"http://www.ontology-of-units-of-measure.org/resource/om-2/month",
    "http://www.w3.org/TR/owl-time#generalMonth":"http://www.w3.org/2006/time#unitMonth",
    "http://www.w3.org/2001/XMLSchema#gDay":"http://www.ontology-of-units-of-measure.org/resource/om-2/day",
    "http://www.w3.org/TR/owl-time#generalDay":"http://www.w3.org/2006/time#unitDay",
    "http://www.w3.org/2001/XMLSchema#date":"","http://www.w3.org/2001/XMLSchema#dateTime":""}

    collectionrelationproperties={
        "http://www.w3.org/2000/01/rdf-schema#member":"ObjectProperty",
        "http://www.w3.org/2004/02/skos/core#member":"ObjectProperty",
        "http://www.w3.org/ns/lemon/lexicog#entry": "ObjectProperty",
        "http://www.w3.org/2006/vcard/ns#hasMember":"ObjectProperty",
        "http://www.w3.org/ns/dcat#dataset":"ObjectProperty",
        "http://www.w3.org/ns/dcat#resource":"ObjectProperty",
        "http://www.w3.org/ns/dcat#service":"ObjectProperty"
    }

    invcollectionrelationproperties={
        "https://www.w3.org/ns/activitystreams#partOf":"ObjectProperty"
    }

    valueproperties={
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value":"DatatypeProperty",
        "http://www.ontology-of-units-of-measure.org/resource/om-2/hasValue":"ObjectProperty",
        "http://www.opengis.net/ont/crs/usesValue":"ObjectProperty",
        "http://www.ontology-of-units-of-measure.org/resource/om-2/hasNumericalValue":"DatatypeProperty",
        "http://www.w3.org/ns/sosa/hasResult": "ObjectProperty",
        "http://www.w3.org/ns/sosa/hasSimpleResult":"DatatypeProperty"
    }

    unitproperties={
        "http://www.ontology-of-units-of-measure.org/resource/om-2/hasUnit":"ObjectProperty",
        "https://www.w3.org/ns/activitystreams#units":"DatatypeProperty"
    }

    labelproperties = {
        "http://www.w3.org/2004/02/skos/core#prefLabel": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#prefSymbol": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#altLabel": "DatatypeProperty",
        "https://schema.org/name": "DatatypeProperty",
        "https://schema.org/alternateName": "DatatypeProperty",
        "http://purl.org/dc/terms/title": "DatatypeProperty",
        "http://purl.org/dc/elements/1.1/title": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#altSymbol": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#hiddenLabel": "DatatypeProperty",
        "http://www.w3.org/2000/01/rdf-schema#label": "DatatypeProperty"
    }

    commentproperties={
        "http://www.w3.org/2004/02/skos/core#definition":"DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#note": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#scopeNote": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#historyNote": "DatatypeProperty",
        "https://schema.org/description":"DatatypeProperty",
        "http://www.w3.org/2000/01/rdf-schema#comment": "DatatypeProperty",
        "http://purl.org/dc/terms/description": "DatatypeProperty",
        "http://purl.org/dc/elements/1.1/description": "DatatypeProperty"
    }

    geopointerproperties={
        "http://www.opengis.net/ont/geosparql#hasGeometry": "ObjectProperty",
        "http://www.opengis.net/ont/geosparql#hasDefaultGeometry": "ObjectProperty",
        "http://www.w3.org/2003/01/geo/wgs84_pos#geometry": "ObjectProperty",
        "http://www.w3.org/2006/vcard/ns#hasGeo": "ObjectProperty",
        "http://schema.org/geo": "ObjectProperty",
        "https://schema.org/geo": "ObjectProperty",
        "http://geovocab.org/geometry#geometry": "ObjectProperty",
        "http://www.w3.org/ns/locn#geometry": "ObjectProperty",
        "http://rdfs.co/juso/geometry": "ObjectProperty"
    }

    geolatlonproperties={
       "http://www.w3.org/2003/01/geo/wgs84_pos#lat":"DatatypeProperty",
       "http://www.w3.org/2003/01/geo/wgs84_pos#long": "DatatypeProperty",
       "https://www.w3.org/ns/activitystreams#latitude": "DatatypeProperty",
       "https://www.w3.org/ns/activitystreams#longitude": "DatatypeProperty",
       "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude": "DatatypeProperty",
       "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude": "DatatypeProperty",
       "http://schema.org/longitude": "DatatypeProperty",
       "https://schema.org/longitude": "DatatypeProperty",
       "http://schema.org/latitude": "DatatypeProperty",
       "https://schema.org/latitude": "DatatypeProperty",
    }

    geopairproperties={
        "http://schema.org/longitude":{"type":"DatatypeProperty","pair":"http://schema.org/latitude","islong":False},
        "http://schema.org/latitude": {"type": "DatatypeProperty", "pair": "http://schema.org/longitude","islong":True},
        "https://schema.org/longitude": {"type": "DatatypeProperty", "pair": "https://schema.org/latitude","islong":False},
        "https://schema.org/latitude": {"type": "DatatypeProperty", "pair": "https://schema.org/longitude","islong":True},
        "http://www.w3.org/2003/01/geo/wgs84_pos#lat": {"type": "DatatypeProperty", "pair": "http://www.w3.org/2003/01/geo/wgs84_pos#long","islong":True},
        "http://www.w3.org/2003/01/geo/wgs84_pos#long": {"type": "DatatypeProperty", "pair": "http://www.w3.org/2003/01/geo/wgs84_pos#lat","islong":False},
        "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude": {"type": "DatatypeProperty", "pair": "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude","islong": False},
        "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude": {"type": "DatatypeProperty", "pair": "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude","islong": True}
    }


    geoproperties={
       "http://www.opengis.net/ont/geosparql#asWKT":"DatatypeProperty",
       "http://www.opengis.net/ont/geosparql#asGML": "DatatypeProperty",
       "http://www.opengis.net/ont/geosparql#asKML": "DatatypeProperty",
       "http://www.opengis.net/ont/geosparql#asGeoJSON": "DatatypeProperty",
       "http://www.opengis.net/ont/geosparql#hasGeometry": "ObjectProperty",
       "http://www.opengis.net/ont/geosparql#hasDefaultGeometry": "ObjectProperty",
       "http://www.w3.org/2003/01/geo/wgs84_pos#geometry": "ObjectProperty",
       "http://www.georss.org/georss/point": "DatatypeProperty",
       "http://www.w3.org/2006/vcard/ns#hasGeo": "ObjectProperty",
       "http://schema.org/geo": "ObjectProperty",
       "https://schema.org/geo": "ObjectProperty",
       "http://purl.org/dc/terms/coverage":"DatatypeProperty",
       "http://purl.org/dc/terms/spatial":"DatatypeProperty",
       "http://schema.org/polygon": "DatatypeProperty",
       "https://schema.org/polygon": "DatatypeProperty",
       "http://geovocab.org/geometry#geometry": "ObjectProperty",
       "http://www.w3.org/ns/locn#geometry": "ObjectProperty",
       "http://rdfs.co/juso/geometry": "ObjectProperty",
       "http://www.wikidata.org/prop/direct/P625":"DatatypeProperty",
       "https://database.factgrid.de/prop/direct/P48": "DatatypeProperty",
       "http://database.factgrid.de/prop/direct/P48":"DatatypeProperty",
       "http://www.wikidata.org/prop/direct/P3896": "DatatypeProperty"
    }

    imageextensions=[".apng",".bmp",".cur",".ico",".jpg",".jpeg",".png",".gif",".tif",".svg","<svg"]

    meshextensions=[".gltf",".obj",".ply",".nxs",".nxz"]

    videoextensions=[".avi",".mp4",".ogv"]

    audioextensions=[".aac",".mp3",".mkv",".ogg",".opus",".wav"]

    fileextensionmap={
        ".apng":"image",
        ".bmp":"image",
        ".cur":"image",
        ".ico":"image",
        ".jpg":"image",
        ".jpeg":"image",
        ".png":"image",
        ".gif":"image",
        ".tif":"image",
        ".svg":"image",
        "<svg":"image",
        ".ply":"mesh",
        ".nxs":"mesh",
        ".nxz":"mesh",
        ".gltf":"mesh",
        ".obj":"mesh",
        ".avi":"video",
        ".mp4":"video",
        ".ogv":"video",
        ".aac":"audio",
        ".mp3":"audio",
        ".mkv":"audio",
        ".ogg":"audio",
        ".opus":"audio",
        ".wav":"audio"
    }




    classtreequery="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
            SELECT DISTINCT ?subject ?label ?supertype\n
            WHERE {\n
               { ?individual rdf:type ?subject . } UNION { ?subject rdf:type owl:Class . } UNION { ?subject rdf:type rdfs:Class . } .\n
               OPTIONAL { ?subject rdfs:subClassOf ?supertype } .\n
               OPTIONAL { ?subject rdfs:label ?label. filter(langMatches(lang(?label),\"en\")) }
               OPTIONAL { ?subject rdfs:label ?label }.\n
                FILTER (\n
                    (\n
                    ?subject != owl:Class &&\n
                    ?subject != rdf:List &&\n
                    ?subject != rdf:Property &&\n
                    ?subject != rdfs:Class &&\n
                    ?subject != rdfs:Datatype &&\n
                    ?subject != rdfs:ContainerMembershipProperty &&\n
                    ?subject != owl:DatatypeProperty &&\n
                    ?subject != owl:AnnotationProperty &&\n
                    ?subject != owl:Restriction &&\n
                    ?subject != owl:ObjectProperty &&\n
                    ?subject != owl:NamedIndividual &&\n
                    ?subject != owl:Ontology) )\n
            }"""