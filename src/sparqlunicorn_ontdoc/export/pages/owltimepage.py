from doc.docconfig import DocConfig
from doc.docutils import DocUtils
from rdflib import URIRef, Literal
from rdflib.namespace import TIME, SOSA

_TIME_HAS_BEGINNING = str(TIME.hasBeginning)
_TIME_HAS_END = str(TIME.hasEnd)
_TIME_HAS_TIME = str(TIME.hasTime)
_SOSA_PHENOMENON_TIME = str(SOSA.phenomenonTime)
_SOSA_RESULT_TIME = str(SOSA.resultTime)


class OWLTimePage:

    @staticmethod
    def resolveTimeObject(pred, obj, graph, timeobj):
        pred_uri = str(pred)
        if pred_uri == _TIME_HAS_BEGINNING:
            if str(obj) in DocConfig.TIME_CALENDAR_INSTANCES:
                timeobj["begin"] = obj
            else:
                for tobj2 in graph.predicate_objects(obj):
                    if str(tobj2[0]) in DocConfig.TIME_PREDICATES:
                        timeobj["begin"] = tobj2[1]
                        break
        elif pred_uri == _TIME_HAS_END:
            if str(obj) in DocConfig.TIME_CALENDAR_INSTANCES:
                timeobj["end"] = obj
            else:
                for tobj2 in graph.predicate_objects(obj):
                    if (str(tobj2[0]) in DocConfig.TIME_PREDICATES or
                            str(tobj2[1]) in DocConfig.TIME_CALENDAR_INSTANCES):
                        timeobj["end"] = tobj2[1]
                        break
        elif pred_uri in (
                _TIME_HAS_TIME, _SOSA_PHENOMENON_TIME, _SOSA_RESULT_TIME):
            if str(obj) in DocConfig.TIME_CALENDAR_INSTANCES:
                timeobj["timepoint"] = obj
            else:
                for tobj2 in graph.predicate_objects(obj):
                    if (str(tobj2[0]) in DocConfig.TIME_PREDICATES or
                            str(tobj2[1]) in DocConfig.TIME_CALENDAR_INSTANCES):
                        timeobj["timepoint"] = tobj2[1]
        return timeobj

    @staticmethod
    def timeObjectToHTML(timeobj,prefixes):
        timeres = ""
        if "begin" in timeobj:
            if "end" in timeobj:
                if str(timeobj["begin"]) in DocConfig.timecalendarinstances:
                    timeres += DocUtils.createURILink(prefixes,str(timeobj["begin"]))
                elif str(timeobj["begin"].datatype) in DocConfig.timeliteraltypes:
                    timeres = f'{timeobj["begin"]} '
                    timeres += DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["begin"].datatype)])
                timeres += " - " 
                if str(timeobj["end"]) in DocConfig.timecalendarinstances:
                    timeres += DocUtils.createURILink(prefixes,str(timeobj["end"]))
                elif str(timeobj["end"].datatype) in DocConfig.timeliteraltypes:
                    timeres += f'{timeobj["end"]}{DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["end"].datatype)])}'
            else:
                if str(timeobj["begin"]) in DocConfig.timecalendarinstances:
                    timeres += DocUtils.createURILink(prefixes,str(timeobj["begin"]))
                elif str(timeobj["begin"].datatype) in DocConfig.timeliteraltypes:
                    timeres += f'{timeobj["begin"]}{DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["begin"].datatype)])}'
        elif "end" in timeobj:
            if str(timeobj["end"]) in DocConfig.timecalendarinstances:
                timeres += DocUtils.createURILink(prefixes,str(timeobj["end"]))
            elif str(timeobj["end"].datatype) in DocConfig.timeliteraltypes:
                timeres += f'{timeobj["end"]}{DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["end"].datatype)])}'
        elif "timepoint" in timeobj:
            if str(timeobj["timepoint"]) in DocConfig.timecalendarinstances:
                timeres += DocUtils.createURILink(prefixes,str(timeobj["timepoint"]))
            elif str(timeobj["timepoint"].datatype) in DocConfig.timeliteraltypes:
                timeres += f'{timeobj["timepoint"]}{DocUtils.createURILink(prefixes,DocConfig.timeliteraltypes[str(timeobj["timepoint"].datatype)])}'
        return timeres.strip()

    @staticmethod
    def resolveTimeLiterals(pred, obj, graph):
        timeobj = {}
        if isinstance(obj, URIRef):
            if str(pred) in DocConfig.TIME_POINTER_PREDICATES:
                timeobj = OWLTimePage.resolveTimeObject(pred, obj, graph, timeobj)
            if str(pred) in (
                    _TIME_HAS_TIME, _SOSA_PHENOMENON_TIME, _SOSA_RESULT_TIME):
                for tobj in graph.predicate_objects(obj):
                    timeobj = OWLTimePage.resolveTimeObject(tobj[0], tobj[1], graph, timeobj)
        elif isinstance(obj, Literal):
            timeobj = OWLTimePage.resolveTimeObject(pred, obj, graph, timeobj)
        return timeobj
