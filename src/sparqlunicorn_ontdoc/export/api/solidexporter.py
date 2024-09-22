import os

from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF, RDFS, OWL, FOAF
from doc.docutils import DocUtils


class SolidExporter:

    @staticmethod
    def createSolidSettings(graph,outpath,deploypath,publisher,datasetname,classtree):
        if not os.path.exists(outpath+"/settings/"):
            os.makedirs(outpath + "/settings/")
        if not os.path.exists(outpath+"/profile/"):
            os.makedirs(outpath + "/profile/")
        webidprofilegraph=Graph()
        webidprofilegraph.add((URIRef(outpath+"/profile/card"), RDF.type, URIRef("http://xmlns.com/foaf/0.1/PersonalProfileDocument")))
        preferencesgraph=Graph()
        preferencesgraph.serialize(destination=outpath+"/settings/prefs.ttl", format="ttl")
        publisheruri=publisher.replace(" ","_")
        if not publisher.startswith("http"):
            publisheruri=deploypath+"/profile/card#"+str(publisher).replace(" ","_")
        webidprofilegraph.add((URIRef(outpath + "/profile/card"), URIRef("http://xmlns.com/foaf/0.1/primaryTopic"), URIRef(str(publisheruri))))
        webidprofilegraph.add((URIRef(str(publisheruri)), RDF.type, FOAF.Person))
        webidprofilegraph.add((URIRef(str(publisheruri)), URIRef("http://www.w3.org/ns/pim/space#storage"), URIRef(str(deploypath) + str(datasetname).replace(" ","_"))))
        webidprofilegraph.add((URIRef(str(publisheruri)), URIRef("http://www.w3.org/ns/solid/terms#publicTypeIndex"), URIRef(deploypath + "/settings/publicTypeIndex.ttl")))
        webidprofilegraph.add((URIRef(str(publisheruri)), URIRef("http://www.w3.org/ns/solid/terms#privateTypeIndex"), URIRef(deploypath + "/settings/privateTypeIndex.ttl")))
        webidprofilegraph.serialize(destination=outpath+"/profile/card.ttl", format="ttl")
        typeindexgraph=Graph()
        typeindexgraph.add((URIRef(deploypath + "/settings/publicTypeIndex.ttl"), RDF.type, URIRef("http://www.w3.org/ns/solid/terms#TypeIndex")))
        typeindexgraph.add((URIRef(deploypath + "/settings/publicTypeIndex.ttl"), RDF.type, URIRef("http://www.w3.org/ns/ldp#RDFResource")))
        typeindexgraph.add((URIRef(deploypath + "/settings/publicTypeIndex.ttl"), RDF.type, URIRef("http://www.w3.org/ns/solid/terms#ListedDocument")))
        typeindexgraph.add((URIRef(deploypath + "/settings/publicTypeIndex.ttl"), RDFS.comment, Literal("This Document contains a list of links to other Documents, along with the type of data that is to be included in those Documents",lang="en")))
        typeindexgraph.add((URIRef(deploypath + "/settings/publicTypeIndex.ttl"), RDF.type, Literal("Public Type Index", lang="en")))
        for cls in classtree:
            typeindexgraph.add((URIRef(deploypath + "/settings/publicTypeIndex.ttl"), RDFS.member, URIRef(deploypath + "/settings/publicTypeIndex.ttl#"+DocUtils.shortenURI(cls["id"]))))
            typeindexgraph.add((URIRef(deploypath + "/settings/publicTypeIndex.ttl#"+DocUtils.shortenURI(cls["id"])),URIRef("http://www.w3.org/ns/solid/terms#forClass"), URIRef(cls["parent"])))
            typeindexgraph.add((URIRef(deploypath + "/settings/publicTypeIndex.ttl#"+DocUtils.shortenURI(cls["id"])),URIRef("http://www.w3.org/ns/solid/terms#instance"), URIRef(deploypath+"/"+DocUtils.shortenURI(cls["id"]))))
        for subj,obj in graph.subject_objects(RDFS.subClassOf):
            typeindexgraph.add((subj, RDFS.subClassOf, obj))
            typeindexgraph.add((subj, RDF.type, OWL.Class))
            typeindexgraph.add((obj, RDF.type, OWL.Class))
        for obj in graph.objects(None,RDF.type):
            typeindexgraph.add((obj, RDF.type, OWL.Class))
        typeindexgraph.serialize(destination=outpath+"/settings/publicTypeIndex.ttl", format="ttl")
        typeindexgraph2=Graph()
        typeindexgraph2.add((URIRef(deploypath + "/settings/privateTypeIndex.ttl"), RDF.type, URIRef("http://www.w3.org/ns/solid/terms#TypeIndex")))
        typeindexgraph2.add((URIRef(deploypath + "/settings/privateTypeIndex.ttl"), RDF.type, URIRef("http://www.w3.org/ns/ldp#RDFResource")))
        typeindexgraph2.add((URIRef(deploypath + "/settings/privateTypeIndex.ttl"), RDF.type, URIRef("http://www.w3.org/ns/solid/terms#ListedDocument")))
        typeindexgraph2.add((URIRef(deploypath + "/settings/privateTypeIndex.ttl"), RDFS.comment, Literal("This Document contains a list of links to other Documents, along with the type of data that is to be included in those Documents",lang="en")))
        typeindexgraph2.add((URIRef(deploypath + "/settings/privateTypeIndex.ttl"), RDFS.label, Literal("Private Type Index", lang="en")))
        typeindexgraph2.serialize(destination=outpath+"/settings/privateTypeIndex.ttl", format="ttl")

    @staticmethod
    def prepareSolidPartitions(graph,classtree,properties):
        print("Graph partitioning here")

    @staticmethod
    def addSolidStorage(graph,deploypath,datasetname):
        graph.add((URIRef(str(deploypath) + str(datasetname)),RDF.type,URIRef("http://www.w3.org/ns/pim/space#Storage")))
        graph.add((URIRef(str(deploypath) + str(datasetname)), RDFS.label,
                   Literal("Solid Storage for "+str(datasetname))))

    @staticmethod
    def createSolidDocumentIndex():
        print("Create document index")

    @staticmethod
    def addSolidContainer(graph,deploypath,datasetname,collections):
        for coll in collections:
            graph.add((URIRef(coll),RDF.type,URIRef("http://www.w3.org/ns/iana/media-types/text/ttl#Resource")))
            graph.add((URIRef(coll), RDF.type,
                       URIRef("http://www.w3.org/ns/ldp#Container")))
            graph.add((URIRef(coll), URIRef("http://www.w3.org/ns/pim/space#storage"),
                       URIRef(str(deploypath) + str(datasetname))))