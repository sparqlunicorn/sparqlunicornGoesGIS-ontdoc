
from rdflib import URIRef
from rdflib import Literal

class SolidExporter:

    @staticmethod
    def addSolidStorage(graph,deploypath,datasetname):
        graph.add((URIRef(str(deploypath) + str(datasetname)),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/ns/pim/space#Storage")))
        graph.add((URIRef(str(deploypath) + str(datasetname)), URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                   Literal("Solid Storage for "+str(datasetname))))