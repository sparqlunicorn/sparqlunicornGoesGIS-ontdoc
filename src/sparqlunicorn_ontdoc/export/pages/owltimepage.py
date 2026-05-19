from doc.docconfig import DocConfig
from doc.docutils import DocUtils
from rdflib import URIRef, Literal
from rdflib.namespace import TIME, SOSA

class OWLTimePage:

    @staticmethod
    def resolveTimeObject(pred, obj, graph, timeobj):
        if pred == TIME.hasBeginning:
            if str(obj) in DocConfig.timecalendarinstances:
                timeobj["begin"] = obj
            else:
                for tobj2 in graph.predicate_objects(obj):
                    if str(tobj2[0]) in DocConfig.timeproperties: 
                        timeobj["begin"] = tobj2[1]
                        break
        elif pred == TIME.hasEnd:
            if str(obj) in DocConfig.timecalendarinstances:
                timeobj["end"] = obj
            else:
                for tobj2 in graph.predicate_objects(obj):
                    if str(tobj2[0]) in DocConfig.timeproperties or str(tobj2[1]) in DocConfig.timecalendarinstances:
                        timeobj["end"] = tobj2[1]
                        break
        elif pred == TIME.hasTime or pred == SOSA.phenomenonTime or pred == SOSA.resultTime:
            if str(obj) in DocConfig.timecalendarinstances:
                timeobj["timepoint"] = obj
            else:
                for tobj2 in graph.predicate_objects(obj):
                    if str(tobj2[0]) in DocConfig.timeproperties or str(tobj2[1]) in DocConfig.timecalendarinstances:
                        timeobj["timepoint"] = tobj2[1]
        return timeobj

    @staticmethod
    def timeObjectToHTML(timeobj,prefixes):
        timeres = ""
        print("TOBJ to HTML"+str(timeobj))
        if "begin" in timeobj:
            if "end" in timeobj:
                if str(timeobj["begin"]) in DocConfig.timecalendarinstances:
                    timeres += DocUtils.createURILink(prefixes,str(timeobj["begin"]))
                elif str(timeobj["begin"].datatype) in DocConfig.timeliteraltypes:
                    timeres = str(timeobj["begin"]) + " "
                    timeres += DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["begin"].datatype)])
                timeres += " - " 
                if str(timeobj["end"]) in DocConfig.timecalendarinstances:
                    timeres += DocUtils.createURILink(prefixes,str(timeobj["end"]))
                elif str(timeobj["end"].datatype) in DocConfig.timeliteraltypes:
                    timeres += str(timeobj["end"])+DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["end"].datatype)])
            else:
                if str(timeobj["begin"]) in DocConfig.timecalendarinstances:
                    timeres += DocUtils.createURILink(prefixes,str(timeobj["begin"]))
                elif str(timeobj["begin"].datatype) in DocConfig.timeliteraltypes:
                    timeres += str(timeobj["begin"])+DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["begin"].datatype)])
        elif "end" in timeobj:
            if str(timeobj["end"]) in DocConfig.timecalendarinstances:
                timeres += DocUtils.createURILink(prefixes,str(timeobj["end"]))
            elif str(timeobj["end"].datatype) in DocConfig.timeliteraltypes:
                timeres += str(timeobj["end"])+DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["end"].datatype)])
        elif "timepoint" in timeobj:
            if str(timeobj["timepoint"]) in DocConfig.timecalendarinstances:
                timeres += DocUtils.createURILink(prefixes,str(timeobj["timepoint"]))
            elif str(timeobj["timepoint"].datatype) in DocConfig.timeliteraltypes:
                timeres += timeobj["timepoint"]+DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["timepoint"].datatype)])
        return timeres

    @staticmethod
    def resolveTimeLiterals(pred, obj, graph):
        timeobj = {}
        if isinstance(obj, URIRef):
            if str(pred) in DocConfig.timepointerproperties:
                timeobj = OWLTimePage.resolveTimeObject(pred, obj, graph, timeobj)
            if pred == TIME.hasTime or pred == SOSA.phenomenonTime or pred == SOSA.resultTime:
                for tobj in graph.predicate_objects(obj):
                    timeobj = OWLTimePage.resolveTimeObject(tobj[0], tobj[1], graph, timeobj)
        elif isinstance(obj, Literal):
            timeobj = OWLTimePage.resolveTimeObject(pred, obj, graph, timeobj)
        return timeobj
