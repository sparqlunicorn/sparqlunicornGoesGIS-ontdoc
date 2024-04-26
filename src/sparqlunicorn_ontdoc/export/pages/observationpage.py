from rdflib import URIRef
from doc.docconfig import DocConfig

class ObservationPage:

    @staticmethod
    def collectionConstraint():
        return ["http://www.w3.org/ns/sosa/ObservationCollection"]

    @staticmethod
    def pageWidgetConstraint():
        return ["http://www.w3.org/ns/sosa/Observation"]

    @staticmethod
    def generatePageWidget(graph,memberid,templates,f,pageWidget=False):
        gottime = None
        gotvalue = None
        xLabel=None
        for observ in graph.predicate_objects(memberid, True):
            if observ[0] == URIRef("http://www.w3.org/ns/sosa/hasSimpleResult"):
                gotvalue = str(observ[1])
            if observ[0] == URIRef("http://www.w3.org/ns/sosa/phenomenonTime"):
                for val in graph.predicate_objects(observ[1]):
                    if str(val[0]) in DocConfig.timeproperties:
                        gottime = str(val[1])
            if observ[0] == URIRef("http://www.w3.org/ns/sosa/hasResult"):
                for val in graph.predicate_objects(observ[1]):
                    if str(val[0]) in DocConfig.valueproperties and val[1] is not None and str(val[1]) != "":
                        gotvalue = str(val[1])
                    if str(val[0]) in DocConfig.unitproperties and val[1] is not None and str(val[1]) != "":
                        xLabel = f"Value ({val[1]})"
        if pageWidget:
            f.write(templates["chartviewtemplate"].replace("{{xValues}}", str([gotvalue]))
                    .replace("{{yValues}}",str([gottime])).replace("{{xLabel}}", "Value").replace("{{yLabel}}", "Time"))
        return {"xValue":gotvalue,"timeValue":gottime,"xLabel":xLabel}

    @staticmethod
    def generateCollectionWidget(graph,templates, subject, f):
        memberpred = URIRef("http://www.w3.org/2000/01/rdf-schema#member")
        xValues = []
        xLabel = "Value"
        timeValues = []
        yLabel = "Time"
        for memberid in graph.objects(subject, memberpred, True):
            res=ObservationPage.generatePageWidget(graph,memberid,templates,f,False)
            if res["timeValue"] is not None and res["xValue"] is not None:
                xValues.append(res["xValue"])
                timeValues.append(res["timeValue"])
            if "xLabel" in res:
                xLabel=res["xLabel"]
        f.write(templates["chartviewtemplate"].replace("{{xValues}}", str(xValues))
                .replace("{{yValues}}",str(timeValues)).replace("{{xLabel}}", str(xLabel)).replace("{{yLabel}}", str(yLabel)))

    def generatePageView(self,graph, subject, f):
        print("PageView")