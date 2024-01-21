from rdflib import URIRef, Literal, Graph
from doc.docconfig import DocConfig

from doc.docutils import DocUtils


class VoidExporter:

    @staticmethod
    def createVoidDataset(dsname,prefixnamespace,deploypath,outpath,licenseuri,modtime,stats,startconcept=None):
        g=Graph()
        if dsname==None or dsname=="":
            dsname="theds"
        voidds=prefixnamespace+dsname
        g.add((URIRef(voidds),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://rdfs.org/ns/void#Dataset")))
        g.add((URIRef(voidds), URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
              Literal(dsname,lang="en")))
        g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/title"),
              Literal(dsname,lang="en")))
        g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/modified"),
              Literal(modtime,datatype="http://www.w3.org/2001/XMLSchema#dateTime")))
        if licenseuri!=None:
            g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/license"),
                  URIRef(licenseuri)))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#dataDump"),
              URIRef(deploypath+"/index.ttl")))
        g.add((URIRef(voidds), URIRef("http://xmlns.com/foaf/0.1/homepage"),
              URIRef(deploypath)))
        g.add((URIRef(voidds), URIRef("http://xmlns.com/foaf/0.1/page"),
              URIRef(deploypath+"/index.html")))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#dataDump"),
              URIRef(deploypath+"/index.ttl")))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#feature"),
              URIRef("http://www.w3.org/ns/formats/Turtle")))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#feature"),
              URIRef("http://www.w3.org/ns/formats/RDFa")))
        if startconcept!=None:
            g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#rootResource"),
                  URIRef(startconcept)))
            g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#exampleResource"),
                  URIRef(startconcept)))
        for stat in stats:
            g.add((URIRef(voidds),URIRef(stat),Literal(stats[stat],datatype="http://www.w3.org/2001/XMLSchema#integer")))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#uriSpace"),
              Literal(prefixnamespace,datatype="http://www.w3.org/2001/XMLSchema#string")))
        for ns_prefix, namespace in g.namespaces():
            g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#vocabulary"),
                  URIRef(namespace)))
            if str(namespace) in DocConfig.namespaceToTopic:
                for entry in DocConfig.namespaceToTopic[str(namespace)]:
                    g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/subject"),
                           URIRef(entry)))
        g.serialize(outpath+"/void.ttl", encoding="utf-8")
        return g

    @staticmethod
    def toHTML(stats):
        result="<details>"
        result+="<table><thead><th>Property</th><th>Value</th></thead><tbody>"
        for stat in stats:
            result+="<tr><td><a href=\""+str(stat)+"\" target=\"_blank\">"+str(DocUtils.shortenURI(stat))+"</a></td><td>"+str(stats[stat])+"<a href=\"http://www.w3.org/2001/XMLSchema#integer\" style=\"color:#666;\">(xsd:integer)</a></td></tr>"
        result+="</tbody></table></details>"
        return result