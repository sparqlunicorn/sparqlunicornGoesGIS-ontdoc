from doc.docutils import DocUtils
from doc.literalutils import LiteralUtils
from doc.docutils import DocConfig
from export.pages.bibpage import BibPage
from export.pages.owltimepage import OWLTimePage
from rdflib import URIRef, Graph, BNode, Literal
import re

class HTMLExporter():





    @staticmethod
    def searchObjectConnectionsForAggregateData(graph, object, pred, geojsonrep, foundmedia, imageannos,
                                                textannos, image3dannos, annobodies, label, unitlabel, nonns, inverse,labellang,typeproperty,prefixes):
        geoprop = False
        annosource = None
        incollection = False
        if pred in DocConfig.geopointerproperties:
            geoprop = True
        if pred in DocConfig.collectionrelationproperties:
            incollection = True
        foundval = None
        foundunit = None
        tempvalprop = None
        onelabel = None
        bibtex = None
        timeobj = None
        for tup in graph.predicate_objects(object):
            if str(tup[0]) in DocConfig.labelproperties:
                if tup[1].language == labellang:
                    label = str(tup[1])
                onelabel = str(tup[1])
            if pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(typeproperty) and (
                    tup[1] == URIRef("http://www.w3.org/ns/oa#SvgSelector") or tup[1] == URIRef(
                    "http://www.w3.org/ns/oa#WKTSelector")):
                for svglit in graph.objects(object, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#value")):
                    if "<svg" in str(svglit):
                        imageannos.append({"value": str(svglit), "bodies": []})
                    elif ("POINT" in str(svglit).upper() or "POLYGON" in str(svglit).upper() or "LINESTRING" in str(
                            svglit).upper()):
                        image3dannos.append({"value": str(svglit), "bodies": []})
            elif pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(
                    typeproperty) and tup[1] == URIRef(
                "http://www.w3.org/ns/oa#TextPositionSelector"):
                curanno = {}
                for txtlit in graph.predicate_objects(object):
                    if str(txtlit[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#value":
                        curanno["exact"] = str(txtlit[1])
                    elif str(txtlit[0]) == "http://www.w3.org/ns/oa#start":
                        curanno["start"] = str(txtlit[1])
                    elif str(txtlit[0]) == "http://www.w3.org/ns/oa#end":
                        curanno["end"] = str(txtlit[1])
                textannos.append(curanno)
            if str(tup[0]) == "http://www.w3.org/ns/oa#hasSource":
                annosource = str(tup[1])
                print(
                    "Found annosource " + str(tup[1]) + " from " + str(object) + " Imageannos: " + str(len(imageannos)))
            if (
                    pred == "http://purl.org/dc/terms/isReferencedBy" or pred == "http://purl.org/spar/cito/hasCitingEntity") and \
                    tup[0] == URIRef(typeproperty) and ("http://purl.org/ontology/bibo/" in str(tup[1])):
                bibtex = BibPage.resolveBibtexReference(graph.predicate_objects(object), object, graph)
            if pred in DocConfig.timepointerproperties:
                timeobj = OWLTimePage.resolveTimeLiterals(pred, object, graph)
            if not nonns:
                geojsonrep = LiteralUtils.resolveGeoLiterals(tup[0], tup[1], graph, geojsonrep, nonns)
            if incollection and "<svg" in str(tup[1]):
                foundmedia["image"][str(tup[1])] = {}
            elif incollection and "http" in str(tup[1]):
                ext = "." + ''.join(filter(str.isalpha, str(tup[1]).split(".")[-1]))
                if ext in DocConfig.fileextensionmap:
                    foundmedia[DocConfig.fileextensionmap[ext]][str(tup[1])] = {}
            if not inverse and str(tup[0]) == "http://www.w3.org/2000/01/rdf-schema#member" and (
            object, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef("http://www.w3.org/ns/sosa/ObservationCollection")) in graph:
                for valtup in graph.predicate_objects(tup[1]):
                    if str(valtup[0]) in DocConfig.unitproperties:
                        foundunit = str(valtup[1])
                    if str(valtup[0]) in DocConfig.valueproperties and isinstance(valtup[1], Literal):
                        foundval = str(valtup[1])
            if str(tup[0]) in DocConfig.valueproperties:
                if tempvalprop == None and str(tup[0]) == "http://www.w3.org/ns/oa#hasSource":
                    tempvalprop = str(tup[0])
                    foundval = str(tup[1])
                if str(tup[0]) != "http://www.w3.org/ns/oa#hasSource" and DocConfig.valueproperties[
                    str(tup[0])] == "DatatypeProperty" and (isinstance(tup[1], Literal) or isinstance(tup[1], URIRef)):
                    tempvalprop = str(tup[0])
                    foundval = str(tup[1])
                elif str(tup[0]) == "http://www.w3.org/ns/oa#hasTarget":
                    tempvalprop = "http://www.w3.org/ns/oa#hasTarget"
                    for inttup in graph.predicate_objects(tup[1]):
                        if str(inttup[0]) == "http://www.w3.org/ns/oa#hasSelector":
                            for valtup in graph.predicate_objects(inttup[1]):
                                if str(valtup[0]) in DocConfig.unitproperties:
                                    foundunit = str(valtup[1])
                                if str(valtup[0]) in DocConfig.valueproperties and (
                                        isinstance(valtup[1], Literal) or isinstance(valtup[1], URIRef)):
                                    foundval = str(valtup[1])
                elif DocConfig.valueproperties[str(tup[0])] == "DatatypeProperty":
                    if str(tup[0]) in DocConfig.valueproperties and isinstance(tup[1], Literal):
                        tempvalprop = str(tup[0])
                        foundval = str(tup[1])
                else:
                    for valtup in graph.predicate_objects(tup[1]):
                        if str(valtup[0]) in DocConfig.unitproperties:
                            foundunit = str(valtup[1])
                        if str(valtup[0]) in DocConfig.valueproperties and isinstance(valtup[1], Literal):
                            foundval = str(valtup[1])
            if str(tup[0]) in DocConfig.unitproperties:
                foundunit = tup[1]
        if foundunit != None and foundval != None:
            if "http" in foundunit:
                thelabel = DocUtils.getLabelForObject(str(foundunit), graph, prefixes)
                unitlabel = str(foundval) + " <a href=\"" + str(foundunit) + "\" target=\"_blank\">" + thelabel + "</a>"
            else:
                unitlabel = str(foundval) + " " + str(foundunit)
            if pred == "http://www.w3.org/ns/oa#hasBody":
                # print("ADD ANNO BODY: "+str({"value":foundval,"unit":foundunit,"type":"TextualBody","format":"text/plain"}))
                annobodies.append({"value": foundval, "unit": foundunit, "type": "TextualBody", "format": "text/plain"})
        if foundunit == None and foundval != None:
            if "http" in foundval:
                thelabel = DocUtils.getLabelForObject(str(foundunit), graph, prefixes)
                unitlabel = "<a href=\"" + str(foundval) + "\" target=\"_blank\">" + thelabel + "</a>"
            else:
                unitlabel = str(foundval)
            if pred == "http://www.w3.org/ns/oa#hasBody":
                # print("ADD ANNO BODY: "+str({"value":foundval,"type":"TextualBody","format":"text/plain"}))
                annobodies.append({"value": foundval, "type": "TextualBody", "format": "text/plain"})
        if annosource != None:
            for textanno in textannos:
                textanno["src"] = annosource
            for imganno in imageannos:
                imganno["src"] = annosource
            for imganno in image3dannos:
                imganno["src"] = annosource
        if label == "" and onelabel != None:
            label = onelabel
        return {"geojsonrep": geojsonrep, "label": label, "unitlabel": unitlabel, "foundmedia": foundmedia,
                "imageannos": imageannos, "textannos": textannos, "image3dannos": image3dannos,
                "annobodies": annobodies, "bibtex": bibtex, "timeobj": timeobj}

    @staticmethod
    def createHTMLTableValueEntry(subject, pred, object, ttlf, graph, baseurl, checkdepth, geojsonrep, foundmedia,
                                  imageannos, textannos, image3dannos, annobodies, dateprops, inverse, nonns,labellang,typeproperty,namespaceshort,generatePagesForNonNS,prefixes):
        tablecontents = ""
        label = ""
        bibtex = None
        timeobj = None
        if isinstance(object, URIRef) or isinstance(object, BNode):
            if ttlf != None:
                ttlf.add((subject, URIRef(pred), object))
            label = ""
            unitlabel = ""
            mydata = HTMLExporter.searchObjectConnectionsForAggregateData(graph, object, pred, geojsonrep, foundmedia,
                                                                  imageannos, textannos, image3dannos, annobodies,
                                                                  label, unitlabel, nonns, inverse,labellang,typeproperty,prefixes)
            label = mydata["label"]
            if label == "":
                label = str(DocUtils.shortenURI(str(object)))
            geojsonrep = mydata["geojsonrep"]
            foundmedia = mydata["foundmedia"]
            imageannos = mydata["imageannos"]
            textannos = mydata["textannos"]
            image3dannos = mydata["image3dannos"]
            unitlabel = mydata["unitlabel"]
            bibtex = mydata["bibtex"]
            timeobj = mydata["timeobj"]
            annobodies = mydata["annobodies"]
            if inverse:
                rdfares = " about=\"" + str(object) + "\" resource=\"" + str(subject) + "\""
                microdatares = " itemref=\"" + str(object) + "\" "
            else:
                rdfares = "resource=\"" + str(object) + "\""
                microdatares = " "
            if baseurl in str(object) or isinstance(object, BNode):
                rellink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, str(object), True)
                tablecontents += "<span><a itemprop=\"" + str(pred) + "\"" + microdatares + "property=\"" + str(
                    pred) + "\" " + rdfares + " href=\"" + rellink + "\">" + label + " <span style=\"color: #666;\">(" + namespaceshort + ":" + str(
                    DocUtils.shortenURI(str(object))) + ")</span></a>"
                if bibtex != None:
                    tablecontents += "<details><summary>[BIBTEX]</summary><pre>" + str(bibtex) + "</pre></details>"
            else:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, str(object))
                if res != None:
                    tablecontents += "<span><a itemprop=\"" + str(pred) + "\"" + microdatares + "property=\"" + str(
                        pred) + "\" " + rdfares + " target=\"_blank\" href=\"" + str(
                        object) + "\">" + label + " <span style=\"color: #666;\">(" + res["uri"] + ")</span></a>"
                else:
                    tablecontents += "<span><a itemprop=\"" + str(pred) + "\"" + microdatares + "property=\"" + str(
                        pred) + "\" " + rdfares + " target=\"_blank\" href=\"" + str(object) + "\">" + label + "</a>"
                if bibtex != None:
                    tablecontents += "<details><summary>[BIBTEX]</summary><pre>" + str(bibtex) + "</pre></details>"
                if generatePagesForNonNS:
                    rellink = DocUtils.generateRelativeLinkFromGivenDepth(str(baseurl), checkdepth,
                                                                          str(baseurl) + "nonns_" + DocUtils.shortenURI(
                                                                              str(object).replace(":", "_")), False)
                    tablecontents += " <a href=\"" + rellink + ".html\">[x]</a>"
            if unitlabel != "":
                tablecontents += " <span style=\"font-weight:bold\">[" + str(unitlabel) + "]</span>"
            if timeobj != None:
                res = str(OWLTimePage.timeObjectToHTML(timeobj, prefixes))
                if res != "None":
                    tablecontents += " <span style=\"font-weight:bold\">[" + str(res) + "]</span>"
                dateprops = timeobj
            tablecontents += "</span>"
        else:
            label = str(object)
            if ttlf != None:
                ttlf.add((subject, URIRef(pred), object))
            if isinstance(object, Literal) and object.datatype != None:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, str(object.datatype))
                objstring = str(object).replace("<", "&lt").replace(">", "&gt;")
                if str(object.datatype) == "http://www.w3.org/2001/XMLSchema#anyURI":
                    objstring = "<a href=\"" + str(object) + "\">" + str(object) + "</a>"
                if str(object.datatype) in DocConfig.timeliteraltypes and dateprops != None and DocUtils.shortenURI(
                        str(pred), True) not in DocConfig.metadatanamespaces and str(pred) not in dateprops:
                    dateprops.append(str(pred))
                if res != None:
                    tablecontents += "<span itemprop=\"" + str(pred) + "\" property=\"" + str(
                        pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + HTMLExporter.truncateValue(
                        objstring) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + res["uri"] + "</a>)</small></span>"
                else:
                    tablecontents += "<span itemprop=\"" + str(pred) + "\" property=\"" + str(
                        pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + HTMLExporter.truncateValue(
                        objstring) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + DocUtils.shortenURI(str(object.datatype)) + "</a>)</small></span>"
                geojsonrep = LiteralUtils.resolveGeoLiterals(URIRef(pred), object, graph, geojsonrep, nonns, subject)
            else:
                if object.language != None:
                    tablecontents += "<span itemprop=\"" + str(pred) + "\" property=\"" + str(
                        pred) + "\" content=\"" + str(object).replace("<", "&lt").replace(">", "&gt;").replace("\"",
                                                                                                               "'") + "\" datatype=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\" xml:lang=\"" + str(
                        object.language) + "\">" + HTMLExporter.truncateValue(str(object).replace("<", "&lt").replace(">",
                                                                                                              "&gt;")) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\">rdf:langString</a>) (<a href=\"http://www.lexvo.org/page/iso639-1/" + str(
                        object.language) + "\" target=\"_blank\">iso6391:" + str(
                        object.language) + "</a>)</small></span>"
                else:
                    tablecontents += HTMLExporter.detectStringLiteralContent(pred, object)
        return {"html": tablecontents, "geojson": geojsonrep, "foundmedia": foundmedia, "imageannos": imageannos,
                "textannos": textannos, "image3dannos": image3dannos, "annobodies": annobodies, "label": label,
                "timeobj": dateprops}



    @staticmethod
    def processLicense(license):
        if license == None or license == "" or license == "No License Statement":
            return ["",None]
        if license.startswith("CC"):
            spl = license.split(" ")
            res = """<span style="float:right;margin-left:auto;margin-right:0px;text-align:right">This work is released under <a rel="license" target="_blank" href="http://creativecommons.org/licenses/""" + str(
                spl[1]).lower() + "/" + str(spl[2]) + """/">
            <img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/""" + str(
                spl[1]).lower() + """/""" + str(spl[2]) + """/80x15.png"/></a></span>"""
            licenseuri = "http://creativecommons.org/licenses/" + str(spl[1]).lower() + "/" + str(spl[2])
            return [res,licenseuri]
        else:
            return ["""All rights reserved.""",None]

    @staticmethod
    def formatPredicate(tup, baseurl, checkdepth, tablecontents, graph, reverse,labellang,prefixes):
        label = DocUtils.getLabelForObject(URIRef(str(tup)), graph, None, labellang)
        tablecontents += "<td class=\"property\">"
        if reverse:
            tablecontents += "Is "
        if baseurl in str(tup):
            rellink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, str(tup), True)
            tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + rellink + "\">" + label + "</a></span>"
        else:
            res = DocUtils.replaceNameSpacesInLabel(prefixes, tup)
            if res != None:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup) + "\">" + label + " <span style=\"color: #666;\">(" + res[
                                     "uri"] + ")</span></a> "
            else:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup) + "\">" + label + "</a> "
            tablecontents += "</span>"
        if reverse:
            tablecontents += " of"
        tablecontents += "</td>"
        return tablecontents

    @staticmethod
    def truncateValue(value, limit=150):
        if len(value) > limit:
            return "<details><summary style=\"list-style-type: none;\">" + value[0:limit] + " (...)</summary>" + str(
                value[limit:]) + "</details>"
        return value

    @staticmethod
    def detectStringLiteralContent(pred, object):
        if object.startswith("http://") or object.startswith("https://"):
            return "<span><a itemprop=\"" + str(pred) + "\" property=\"" + str(
                pred) + "\" target=\"_blank\" href=\"" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        elif object.startswith("www."):
            return "<span><a itemprop=\"" + str(pred) + "\" property=\"" + str(
                pred) + "\" target=\"_blank\" href=\"http://" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">http://" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        elif re.search(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?![%"#? ])\\S)+)', str(object)):
            return "<span><a itemprop=\"" + str(pred) + "\" property=\"" + str(
                pred) + "\" href=\"https://www.doi.org/" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#anyURI\">" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#anyURI\">xsd:anyURI</a>)</small></span>"
        elif re.search(r'[\w.]+\@[\w.]+', object):
            return "<span><a itemprop=\"" + str(pred) + "\" property=\"" + str(pred) + "\" href=\"mailto:" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">mailto:" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        return "<span property=\"" + str(pred) + "\" content=\"" + str(object).replace("<", "&lt").replace(">",
                                                                                                           "&gt;").replace(
            "\"", "'") + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object).replace("<",
                                                                                                          "&lt").replace(
            ">",
            "&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
