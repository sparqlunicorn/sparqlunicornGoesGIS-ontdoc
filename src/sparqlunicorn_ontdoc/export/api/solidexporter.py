import os

from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF, RDFS, OWL, FOAF
from doc.docutils import DocUtils
from doc.docconfig import DocConfig


_TYPE_INDEX_COMMENT = Literal(
    "This Document contains a list of links to other Documents, along with the type of data that is to be included in those Documents",
    lang="en",
)


class SolidExporter:

    @staticmethod
    def createSolidSettings(graph,outpath,deploypath,publisher,datasetname,classtree):
        os.makedirs(f"{outpath}/settings/", exist_ok=True)
        os.makedirs(f"{outpath}/profile/", exist_ok=True)
        webidprofilegraph=Graph()
        profile_uri = URIRef(f"{outpath}/profile/card")
        webidprofilegraph.add((profile_uri, RDF.type, DocConfig.PERSONAL_PROFILE_DOCUMENT))
        preferencesgraph=Graph()
        preferencesgraph.serialize(destination=f"{outpath}/settings/prefs.ttl", format="ttl")
        publisheruri=publisher.replace(" ","_")
        if not publisher.startswith("http"):
            publisheruri=f'{deploypath}/profile/card#{str(publisher).replace(" ","_")}'
        puburi=URIRef(str(publisheruri))
        ptypeindex = URIRef(f"{deploypath}/settings/publicTypeIndex.ttl")
        webidprofilegraph.add((profile_uri, FOAF.primaryTopic, puburi))
        webidprofilegraph.add((puburi, RDF.type, FOAF.Person))
        webidprofilegraph.add((puburi, DocConfig.PIM_STORAGE, URIRef(f'{deploypath}{str(datasetname).replace(" ", "_")}')))
        webidprofilegraph.add((puburi, DocConfig.PUBLIC_TYPE_INDEX, ptypeindex))
        webidprofilegraph.add((puburi, DocConfig.PRIVATE_TYPE_INDEX, URIRef(f"{deploypath}/settings/privateTypeIndex.ttl")))
        webidprofilegraph.serialize(destination=f"{outpath}/profile/card.ttl", format="ttl")
        typeindexgraph=Graph()
        typeindexgraph.add((ptypeindex, RDF.type, DocConfig.TYPE_INDEX))
        typeindexgraph.add((ptypeindex, RDF.type, DocConfig.LDP_RDF_RESOURCE))
        typeindexgraph.add((ptypeindex, RDF.type, DocConfig.LISTED_DOCUMENT))
        typeindexgraph.add((ptypeindex, RDFS.comment, _TYPE_INDEX_COMMENT))
        typeindexgraph.add((ptypeindex, RDF.type, Literal("Public Type Index", lang="en")))
        for cls in classtree:
            ptyeindexhash=URIRef(f'{deploypath}/settings/publicTypeIndex.ttl#{DocUtils.shortenURI(cls["id"])}')
            typeindexgraph.add((ptypeindex, RDFS.member, ptyeindexhash))
            typeindexgraph.add((ptyeindexhash, DocConfig.FOR_CLASS, URIRef(cls["parent"])))
            typeindexgraph.add((ptyeindexhash, DocConfig.INSTANCE, URIRef(f'{deploypath}/{DocUtils.shortenURI(cls["id"])}')))
        for subj,obj in graph.subject_objects(RDFS.subClassOf):
            typeindexgraph.add((subj, RDFS.subClassOf, obj))
            typeindexgraph.add((subj, RDF.type, OWL.Class))
            typeindexgraph.add((obj, RDF.type, OWL.Class))
        for obj in graph.objects(None,RDF.type):
            typeindexgraph.add((obj, RDF.type, OWL.Class))
        typeindexgraph.serialize(destination=f"{outpath}/settings/publicTypeIndex.ttl", format="ttl")
        typeindexgraph2=Graph()
        ptypeindex = URIRef(f"{deploypath}/settings/privateTypeIndex.ttl")
        typeindexgraph2.add((ptypeindex, RDF.type, DocConfig.TYPE_INDEX))
        typeindexgraph2.add((ptypeindex, RDF.type, DocConfig.LDP_RDF_RESOURCE))
        typeindexgraph2.add((ptypeindex, RDF.type, DocConfig.LISTED_DOCUMENT))
        typeindexgraph2.add((ptypeindex, RDFS.comment, _TYPE_INDEX_COMMENT))
        typeindexgraph2.add((ptypeindex, RDFS.label, Literal("Private Type Index", lang="en")))
        typeindexgraph2.serialize(destination=f"{outpath}/settings/privateTypeIndex.ttl", format="ttl")

    @staticmethod
    def prepareSolidPartitions(graph,classtree,properties):
        print("Graph partitioning here")

    @staticmethod
    def addSolidStorage(graph,deploypath,datasetname):
        storage_uri = URIRef(f"{deploypath}{datasetname}")
        graph.add((storage_uri,RDF.type,DocConfig.SOLID_STORAGE))
        graph.add((storage_uri, RDFS.label, Literal(f"Solid Storage for {datasetname}")))

    @staticmethod
    def createSolidDocumentIndex():
        print("Create document index")

    @staticmethod
    def addSolidContainer(graph,deploypath,datasetname,collections):
        storage_uri = URIRef(f'{deploypath}{datasetname}')
        for coll in collections:
            colluri=URIRef(coll)
            graph.add((colluri,RDF.type, DocConfig.TURTLE_RESOURCE))
            graph.add((colluri, RDF.type, DocConfig.LDP_CONTAINER))
            graph.add((colluri, DocConfig.PIM_STORAGE, storage_uri))