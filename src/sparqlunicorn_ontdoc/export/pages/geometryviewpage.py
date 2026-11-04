from rdflib import URIRef, Literal
from rdflib.namespace import RDFS
from doc.docconfig import DocConfig
from doc.docutils import DocUtils
from doc.literalutils import LiteralUtils

import shapely.wkt
import shapely.geometry
from doc import orjsonutils as json

from export.pages.owltimepage import OWLTimePage


class GeometryViewPage:

    def createSVGFromWKT(self,templates,features,f):
        thepath="<svg>"
        geomcoll= shapely.geometry.GeometryCollection([shapely.geometry.shape(feature["geometry"]) for feature in features["features"]])
        svgpath=geomcoll.svg()
        #print(svgpath)
        thepath+=svgpath
        thepath+="</svg>"
        #print(thepath)
        f.write(templates["imagestemplatesvg"].replace("{{carousel}}","image").replace("{{image}}", str(thepath.replace("<svg>","<svg class=\"svgview\">"))))


    def generatePageWidget(self,graph,subject,templates,f,uritotreeitem,geojsonrep,predobjmap,geocache,parameters={},onlybody=False):
        substr=str(subject)
        if uritotreeitem is not None and substr in uritotreeitem:
            uritotreeitem[substr][-1]["type"] = "geoinstance"
        props = predobjmap
        dateprops = parameters["dateprops"] if "dateprops" in parameters else []
        epsgcode = parameters["epsgcode"] if "epsgcode" in parameters else ""
        timeobj = parameters["timeobj"] if "timeobj" in parameters else None
        if timeobj is not None:
            dateprops += [item for item in timeobj]
        foundlabel = parameters["foundlabel"] if "foundlabel" in parameters else ""
        jsonfeat = {"type": "Feature", 'id': substr, 'name': foundlabel, 'dateprops': dateprops,'properties': props, "geometry": geojsonrep}
        if epsgcode == "" and "crs" in geojsonrep:
            epsgcode = f"EPSG:{geojsonrep['crs']}"
            jsonfeat["crs"]=epsgcode
        hasnonnslen = parameters["hasnonnslen"] if "hasnonnslen" in parameters else 0
        if hasnonnslen > 0:
            geocache[substr] = jsonfeat
        geom=shapely.geometry.shape(jsonfeat["geometry"])
        if geom.has_z and len(str(shapely.get_coordinates(geom)[0, 0]).split(".")[1])<6:
            self.createSVGFromWKT(templates, {"type":"FeatureCollection","features":[jsonfeat]}, f)
        else:
            checkdepth = parameters["checkdepth"] if "checkdepth" in parameters else 0
            epsgdefslink = parameters["epsgdefslink"] if "epsgdefslink" in parameters else ""
            f.write(templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace("{{myfeature}}", f'[{json.dumps(jsonfeat)}]').replace(
                "{{relativepath}}", DocUtils.generateRelativePathFromGivenDepth(checkdepth)).replace("{{epsg}}",epsgcode).replace(
                "{{baselayers}}", json.dumps(DocConfig.baselayers)).replace("{{epsgdefsPath}}", epsgdefslink).replace(
                "{{dateatt}}", str(dateprops)))
        return geocache

    def generateCollectionWidget(self,graph,subject,templates,f,uritotreeitem,featurecollectionspaths,parameters={"foundlabel":""}):
        subjectstr = str(subject)
        foundlabel = parameters["foundlabel"] if "foundlabel" in parameters else None
        if foundlabel is not None and foundlabel != "":
            featcoll = {"type": "FeatureCollection", "id": subject, "name": str(foundlabel),"features": []}
        else:
            featcoll = {"type": "FeatureCollection", "id": subject, "name": DocUtils.shortenURI(subjectstr),"features": []}
        geocache = parameters["geocache"] if "geocache" in parameters else {}
        nonns = parameters["nonns"] if "nonns" in parameters else False
        hasnonns = parameters["hasnonns"] if "hasnonns" in parameters else {}
        hasnonnslen = parameters["hasnonnslen"] if "hasnonnslen" in parameters else 0
        checkdepth = parameters["checkdepth"] if "checkdepth" in parameters else 0
        epsgdefslink = parameters["epsgdefslink"] if "epsgdefslink" in parameters else ""
        completesavepath = parameters["completesavepath"] if "completesavepath" in parameters else ""
        local_optimized = parameters["localOptimized"] if "localOptimized" in parameters else False
        thecrs = set()
        dateatt = ""
        if not nonns:
            for memberid in graph.objects(subject, RDFS.member, True):
                memberidstr=str(memberid)
                geojsonrep = None
                timeobj={}
                dateatt=[]
                properties = {}
                for geoinstance in graph.predicate_objects(memberid, True):
                    geoinstance0str = str(geoinstance[0])
                    geoinstance1str = str(geoinstance[1])
                    geoinstanceobject = geoinstance[1]
                    geoinstancetype = (
                        str(geoinstanceobject.datatype)
                        if geoinstanceobject.__class__ is Literal else None
                    )
                    if geoinstance[1].__class__ is Literal and (
                            geoinstance0str in DocConfig.GEO_PROPERTIES or
                            geoinstancetype in DocConfig.geoliteraltypes):
                        geojsonrep = LiteralUtils.processLiteral(
                            geoinstance1str, geoinstancetype, "")
                        uritotreeitem[subjectstr][-1]["type"] = "geocollection"
                    elif geoinstance0str in DocConfig.GEO_POINTER_PROPERTIES:
                        uritotreeitem[subjectstr][-1]["type"] = "featurecollection"
                        for geotup in graph.predicate_objects(geoinstance[1], True):
                            geotupobject = geotup[1]
                            geotuptype = (
                                str(geotupobject.datatype)
                                if geotupobject.__class__ is Literal else None
                            )
                            if geotupobject.__class__ is Literal and (
                                    str(geotup[0]) in DocConfig.GEO_PROPERTIES or
                                    geotuptype in DocConfig.geoliteraltypes):
                                geotupobjectstr = str(geotupobject)
                                geojsonrep = LiteralUtils.processLiteral(
                                    geotupobjectstr, geotuptype, "")
                                break
                    else:
                        if geoinstance0str in DocConfig.TIME_POINTER_PREDICATES:
                            timeobj=OWLTimePage.resolveTimeLiterals(geoinstance[0],geoinstance[1],graph)
                            for key in timeobj:
                                dateatt.append(key)
                                properties[key] = str(timeobj[key])
                        elif geoinstance[1].__class__ is URIRef:
                            foundunit=None
                            foundval=None
                            #print("RESOLVE UNIT FROM: "+str(geoinstance[1]))
                            res=DocUtils.resolveUnitValue(graph,geoinstance[1],None,geoinstance1str,foundunit,foundval)
                            foundval=res[0]
                            foundunit=res[1]
                            #print("FOUNDVAL: "+str(foundval)+" FOUNDUNIT: "+str(foundunit))
                            if foundval is not None:
                                properties[f"{geoinstance0str}.value"]=foundval
                            if foundunit is not None:
                                properties[f"{geoinstance0str}.unit"] = foundunit
                        else:
                            properties[geoinstance0str]=geoinstance1str
                    #print(geojsonrep)
                if geojsonrep is not None and geojsonrep != "" and geojsonrep.__class__ is dict and "coordinates" in geojsonrep and len(geojsonrep["coordinates"]) > 0:
                    if uritotreeitem is not None and memberidstr in uritotreeitem:
                        feature = {"type": "Feature", 'id': memberidstr,
                                   'name': uritotreeitem[memberidstr][-1]["text"],
                                   'dateprops': list(timeobj.keys()), 'properties': properties,
                                   "geometry": geojsonrep}
                    else:
                        feature = {"type": "Feature", 'id': memberidstr, 'name': memberidstr,
                                   'dateprops': list(timeobj.keys()),
                                   'properties': properties, "geometry": geojsonrep}
                    featcoll["features"].append(feature)
                    if feature["dateprops"]:
                        dateatt = feature["dateprops"][0]
                    if "crs" in geojsonrep:
                        thecrs.add(geojsonrep["crs"])
                        #break
            if hasnonnslen > 0:
                geocache[subjectstr] = featcoll
        else:
            for item in hasnonns:
                if item in geocache:
                    featcoll["features"].append(geocache[item])
                    if len(geocache[item]["dateprops"]) > 0:
                        dateatt = geocache[item]["dateprops"][0]
                    if "crs" in geocache[item]:
                        thecrs.add(geocache[item]["crs"])
        if len(featcoll["features"]) > 0:
            featcoll["numberMatched"] = len(featcoll["features"])
            featcoll["numberReturned"] = len(featcoll["features"])
            geomcoll=shapely.geometry.GeometryCollection([shapely.geometry.shape(feature["geometry"]) for feature in featcoll["features"]])
            featcoll["bbox"]=geomcoll.bounds
            if geomcoll.has_z and len(str(shapely.get_coordinates(geomcoll)[0, 0]).split(".")[1])<6:
                self.createSVGFromWKT(templates,featcoll,f)
            else:
                firstcrs = "4326"
                featcoll["crs"] = "http://www.opengis.net/def/crs/EPSG/0/4326"
                if len(thecrs) > 0:
                    firstcrs = str(next(iter(thecrs)))
                    featcoll["crs"] = f"http://www.opengis.net/def/crs/EPSG/0/{firstcrs}"
                epsgcode = f"EPSG:{firstcrs}"
                if len(dateatt)>0:
                    for feat in featcoll["features"]:
                        if dateatt not in feat["properties"]:
                            feat["properties"][dateatt] = ""
                if local_optimized:
                    f.write(templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace("{{myfeature}}",f'[{json.dumps(featcoll)}]').replace(
                        "{{relativepath}}",DocUtils.generateRelativePathFromGivenDepth(checkdepth)).replace("{{epsg}}",epsgcode).replace(
                        "{{baselayers}}", json.dumps(DocConfig.baselayers)).replace("{{epsgdefsPath}}",epsgdefslink).replace("{{dateatt}}",str(dateatt)))
                else:
                    f.write(templates["maptemplate"].replace("{{myfeature}}", f'["{DocUtils.shortenURI(str(completesavepath.replace(".html", ".geojson")))}"]').replace(
                        "{{relativepath}}",DocUtils.generateRelativePathFromGivenDepth(checkdepth)).replace("{{baselayers}}", json.dumps(DocConfig.baselayers)).replace("{{epsg}}",epsgcode).replace("{{epsgdefsPath}}",epsgdefslink).replace("{{dateatt}}", str(dateatt)))
                spath=completesavepath.replace(".html", ".geojson")
                with open(spath, 'w',encoding='utf-8') as fgeo:
                    featurecollectionspaths[spath] = {"name": featcoll["name"],"id": featcoll["id"]}
                    json.dump(featcoll,fgeo)
        return geocache

    def generatePageView(self,headertemplate,footertemplate,g,f):
        f.write(str(headertemplate))
