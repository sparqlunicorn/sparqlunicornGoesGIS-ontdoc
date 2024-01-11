from rdflib import URIRef, Literal
import os
import json
import shapely
import traceback

from doc.docutils import DocUtils
from doc.docconfig import DocConfig

class LiteralUtils:

    @staticmethod
    def resolveGeoLiterals(pred, object, graph, geojsonrep, nonns, subject=None):
        if subject != None and isinstance(object, Literal) and (str(pred) in DocConfig.geopairproperties):
            pairprop = DocConfig.geopairproperties[str(pred)]["pair"]
            latorlong = DocConfig.geopairproperties[str(pred)]["islong"]
            othervalue = ""
            for obj in graph.objects(subject, URIRef(pairprop)):
                othervalue = str(obj)
            if latorlong:
                geojsonrep = {"type": "Point", "coordinates": [float(str(othervalue)), float(str(object))]}
            else:
                geojsonrep = {"type": "Point", "coordinates": [float(str(object)), float(str(othervalue))]}
        elif isinstance(object, Literal) and (
                str(pred) in DocConfig.geoproperties or str(object.datatype) in DocConfig.geoliteraltypes):
            geojsonrep = DocUtils.processLiteral(str(object), str(object.datatype), "")
        elif isinstance(object, URIRef) and nonns:
            for pobj in graph.predicate_objects(object):
                if isinstance(pobj[1], Literal) and (
                        str(pobj[0]) in DocConfig.geoproperties or str(
                    pobj[1].datatype) in DocConfig.geoliteraltypes):
                    geojsonrep = DocUtils.processLiteral(str(pobj[1]), str(pobj[1].datatype), "")
        return geojsonrep

    @staticmethod
    def processLiteral(literal, literaltype, reproject, currentlayergeojson=None, triplestoreconf=None):
        # print("Process literal: " + str(literal) + " --- " + str(literaltype))
        try:
            if "wkt" in literaltype.lower():
                crsuri = ""
                curcrs = None
                if "http" in literal:
                    crsuri = literal[0:literal.rfind('>')].replace("<", "")
                    curcrs = crsuri[crsuri.rfind('/') + 1:]
                    literal = literal[literal.rfind('>') + 1:].strip()
                shapelygeom = shapely.wkt.loads(literal)
                thejson = json.loads(json.dumps(shapely.geometry.mapping(shapelygeom), indent=2))
                if curcrs != None:
                    thejson["crs"] = curcrs
                return thejson
            if "geojson" in literaltype.lower():
                return literal
        except Exception as e:
            print("Literal: " + str(literal) + " " + str(literaltype))
            print(e)
            print(traceback.format_exc())
        return None