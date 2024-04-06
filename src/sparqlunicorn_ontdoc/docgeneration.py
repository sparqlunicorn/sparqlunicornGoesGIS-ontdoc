# -*- coding: UTF-8 -*-
from sys import prefix

from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib.plugins.sparql import prepareQuery
from urllib.request import urlopen

from io import BytesIO
from zipfile import ZipFile
import os
import sys
import traceback

from export.pages.bibpage import BibPage
from export.pages.lexiconpage import LexiconPage
from export.pages.observationpage import ObservationPage
from export.pages.geometryviewpage import GeometryViewPage
from export.pages.personpage import PersonPage
from export.data.htmlexporter import HTMLExporter
from export.data.voidexporter import VoidExporter

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
print(sys.path)
print(os.path.dirname(os.path.realpath(__file__)))
print(os.listdir(os.getcwd()))
from datetime import datetime
from doc.docutils import DocUtils
from doc.graphutils import GraphUtils
from doc.classtreeutils import ClassTreeUtils
from doc.docdefaults import DocDefaults
from doc.docconfig import DocConfig
from doc.templateutils import TemplateUtils
from export.data.vowlexporter import OWL2VOWL
from export.data.exporterutils import ExporterUtils
from export.api.iiifexporter import IIIFAPIExporter
from export.api.ogcapifeaturesexporter import OGCAPIFeaturesExporter
from export.api.ckanexporter import CKANExporter
from export.api.solidexporter import SolidExporter

import urllib.parse
import argparse
import re
import shutil
import json

listthreshold = 5
maxlistthreshold = 1500

templatepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/html/"))
resourcepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/"))

featurecollectionspaths = {}
iiifmanifestpaths = {"default": []}
imagetoURI = {}

templates = DocDefaults.templates


class OntDocGeneration:

    def __init__(self, prefixes, modtime, prefixnamespace, prefixnsshort, license, labellang, outpath, graph,
                 createIndexPages, createColl, metadatatable, generatePagesForNonNS, createVOWL, apis, localOptimized=False, imagemetadata=None, startconcept=None,
                 repository="", deploypath="", logoname="", templatename="default", offlinecompat=False,
                 exports=["json", "ttl"], datasettitle="", publisher="", publishingorg=""):
        self.prefixes = prefixes
        self.prefixnamespace = prefixnamespace
        self.modtime=modtime
        self.namespaceshort = prefixnsshort.replace("/","")
        self.outpath=outpath
        self.exports=exports
        self.datasettitle=str(datasettitle).replace(" ","_")
        self.logoname=logoname
        self.apis=apis
        self.has3d=False
        self.repository=repository
        self.publisher=publisher
        self.publishingorg=publishingorg
        self.startconcept=startconcept
        self.createVOWL=createVOWL
        self.imagemetadata=imagemetadata
        self.localOptimized=localOptimized
        self.geocache={}
        self.deploypath=deploypath
        self.generatePagesForNonNS=generatePagesForNonNS
        self.geocollectionspaths=[]
        self.metadatatable=metadatatable
        self.templatename=templatename
        #if os.path.exists("ontdocscript"):
        #    templatepath=os.path.abspath(os.path.join(os.path.dirname(__file__), "ontdocscript/resources/html/"))
        # else:
        #    templatepath=os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/html/"))
        templates = TemplateUtils.resolveTemplate(templatename, templatepath)
        self.offlinecompat = offlinecompat
        if offlinecompat:
            templates["htmltemplate"] = DocUtils.createOfflineCompatibleVersion(outpath, templates["htmltemplate"],
                                                                            templatepath, templatename)
            templates["maptemplate"] = DocUtils.createOfflineCompatibleVersion(outpath, templates["maptemplate"],
                                                                           templatepath, templatename)
            templates["sparqltemplate"] = DocUtils.createOfflineCompatibleVersion(outpath, templates["sparqltemplate"],
                                                                              templatepath, templatename)
        self.license = license
        self.licenseuri = None
        self.licensehtml = None
        self.createColl = createColl
        self.labellang = labellang
        self.typeproperty = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        self.createIndexPages = createIndexPages
        self.graph = graph
        self.htmlexporter=HTMLExporter(prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath,metadatatable,generatePagesForNonNS,apis,templates,self.namespaceshort,self.typeproperty,imagemetadata,localOptimized,deploypath,logoname,offlinecompat)
        for nstup in self.graph.namespaces():
            if str(nstup[1]) not in prefixes["reversed"]:
                prefixes["reversed"][str(nstup[1])] = str(nstup[0])
        self.preparedclassquery = prepareQuery(DocConfig.classtreequery)
        if prefixnamespace == None or prefixnsshort == None or prefixnamespace == "" or prefixnsshort == "":
            self.namespaceshort = "suni"
            self.prefixnamespace = "http://purl.org/suni/"
        if not prefixnamespace.endswith("/") and not prefixnamespace.endswith("#"):
            self.prefixnamespace += "/"
        if outpath == None:
            self.outpath = "suni_htmls/"
        else:
            self.outpath = self.outpath.replace("\\", "/")
            if not outpath.endswith("/"):
                self.outpath += "/"
        self.outpath = self.outpath.replace("//", "/")
        self.prefixnamespace = self.prefixnamespace.replace("//", "/")
        # prefixes["reversed"]["http://purl.org/suni/"] = "suni"

    def updateProgressBar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█',
                          printEnd="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()


    def replaceStandardVariables(self, template, subject, checkdepth, indexpage):
        template = template.replace("{{indexpage}}", str(indexpage)).replace("{{subject}}", str(subject)).replace(
            "{{relativedepth}}", str(checkdepth)) \
            .replace("{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace(
            "{{deploypath}}", self.deploypath) \
            .replace("{{publishingorg}}", self.publishingorg).replace("{{publisher}}", self.publisher).replace(
            "{{datasettitle}}", self.datasettitle) \
            .replace("{{logo}}", self.logoname)
        return template

    def generateOntDocForNameSpace(self, prefixnamespace,dataformat="HTML"):
        outpath=self.outpath
        corpusid=self.namespaceshort.replace("#","")
        if self.datasettitle==None or self.datasettitle=="":
            self.datasettitle=corpusid.replace(" ","_")+"_dataset"
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        labeltouri = {}
        uritolabel = {}
        uritotreeitem = {}
        if self.createVOWL:
            vowlinstance = OWL2VOWL()
            vowlinstance.convertOWL2VOWL(self.graph, outpath)
        tmp=HTMLExporter.processLicense(self.license)
        curlicense=tmp[0]
        self.licensehtml = tmp[0]
        self.licenseuri=tmp[1]
        voidds = prefixnamespace + self.datasettitle
        if self.createColl:
            self.graph = GraphUtils.createCollections(self.graph, prefixnamespace,self.typeproperty)
        if self.logoname is not None and self.logoname != "" and not self.logoname.startswith("http"):
            if not os.path.isdir(outpath + "/logo/"):
                os.mkdir(outpath + "/logo/")
            shutil.copy(self.logoname, outpath + "/logo/logo." + self.logoname[self.logoname.rfind("."):])
            self.logoname = outpath + "/logo/logo." + self.logoname[self.logoname.rfind("."):]
        self.updateProgressBar(0, 1, "Creating classtree and search index")
        res=GraphUtils.analyzeGraph(self.graph, prefixnamespace, self.typeproperty, voidds, labeltouri, uritolabel, outpath, self.createVOWL)
        subjectstorender=res["subjectstorender"]
        self.apis["iiif"]=res["iiif"]
        if os.path.exists(outpath + corpusid + '_search.js'):
            try:
                with open(outpath + corpusid + '_search.js', 'r', encoding='utf-8') as f:
                    data = json.loads(f.read().replace("var search=", ""))
                    for key in data:
                        labeltouri[key] = data[key]
            except Exception as e:
                print("Exception occurred " + str(e))
                print(traceback.format_exc())
        with open(outpath + corpusid + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        if self.offlinecompat:
            if os.path.exists(outpath + "icons/"):
                shutil.rmtree(outpath + "icons/")
            shutil.copytree(templatepath + "/" + self.templatename + "/icons/", outpath + "icons/")
        prevtree = []
        if os.path.exists(outpath + corpusid + '_classtree.js'):
            try:
                with open(outpath + corpusid + '_classtree.js', 'r', encoding='utf-8') as f:
                    prevtree = json.loads(f.read().replace("var tree=", ""))["core"]["data"]
            except Exception as e:
                print("Exception occurred " + str(e))
        classidset = set()
        tree = ClassTreeUtils.getClassTree(self.graph, uritolabel, classidset, uritotreeitem,self.typeproperty,self.prefixes,self.preparedclassquery)
        for tr in prevtree:
            if tr["id"] not in classidset:
                tree["core"]["data"].append(tr)
        res["voidstats"]["http://rdfs.org/ns/void#classes"] = len(classidset)
        res["voidstats"]["http://rdfs.org/ns/void#triples"] = len(self.graph)
        voidgraph = VoidExporter.createVoidDataset(self.datasettitle, prefixnamespace, self.namespaceshort,
                                                   self.repository, self.deploypath, self.outpath, self.licenseuri,
                                                   self.modtime, self.labellang, res["voidstats"], subjectstorender,
                                                   self.prefixes, tree, res["predmap"], res["nonnscount"], res["nscount"], res["instancecount"],
                                                   self.startconcept)
        self.voidstatshtml = VoidExporter.toHTML(res["voidstats"], self.deploypath)
        self.graph += voidgraph["graph"]
        subjectstorender = voidgraph["subjects"]
        with open(outpath + "style.css", 'w', encoding='utf-8') as f:
            f.write(templates["style"])
            f.close()
        with open(outpath + "startscripts.js", 'w', encoding='utf-8') as f:
            f.write(templates["startscripts"].replace("{{baseurl}}", prefixnamespace))
            f.close()
        with open(outpath + "epsgdefs.js", 'w', encoding='utf-8') as f:
            f.write(templates["epsgdefs"])
            f.close()
        paths = {}
        nonnsmap = {}
        postprocessing = Graph()
        subtorencounter = 0
        for subj in subjectstorender:
            path = subj.replace(prefixnamespace, "")
            # try:
            paths = DocUtils.processSubjectPath(outpath, paths, path, self.graph)
            if os.path.exists(outpath + path + "/index.ttl"):
                try:
                    self.graph.parse(outpath + path + "/index.ttl")
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
            res = self.htmlexporter.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace,
                                  self.graph.subject_predicates(subj),
                                  self.graph, str(corpusid) + "_search.js", str(corpusid) + "_classtree.js",
                                  uritotreeitem, curlicense, subjectstorender, postprocessing, nonnsmap)
            postprocessing = res[0]
            nonnsmap = res[1]
            if res[3]:
                self.has3d=True
            subtorencounter += 1
            if subtorencounter % 250 == 0:
                subtorenderlen = len(subjectstorender) + len(postprocessing)
                self.updateProgressBar(subtorencounter, subtorenderlen, "Processing Subject URIs")
            # except Exception as e:
            #    print("Create HTML Exception: "+str(e))
            #    print(traceback.format_exc())
        print("Postprocessing " + str(len(postprocessing)))
        for subj in postprocessing.subjects(None, None, True):
            path = str(subj).replace(prefixnamespace, "")
            paths = DocUtils.processSubjectPath(outpath, paths, path, self.graph)
            if os.path.exists(outpath + path + "/index.ttl"):
                try:
                    self.graph.parse(outpath + path + "/index.ttl")
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
            self.htmlexporter.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace,
                            self.graph.subject_predicates(subj),
                            self.graph, str(corpusid) + "_search.js", str(corpusid) + "_classtree.js", uritotreeitem,
                            curlicense, subjectstorender, postprocessing)
            subtorencounter += 1
            if subtorencounter % 250 == 0:
                subtorenderlen = len(subjectstorender) + len(postprocessing)
                self.updateProgressBar(subtorencounter, subtorenderlen, "Processing Subject URIs")
        ClassTreeUtils.checkGeoInstanceAssignment(uritotreeitem)
        classlist = ClassTreeUtils.assignGeoClassesToTree(tree)
        if self.generatePagesForNonNS:
            labeltouri = self.getSubjectPagesForNonGraphURIs(nonnsmap, self.graph, prefixnamespace, corpusid, outpath,
                                                             self.license, prefixnamespace, uritotreeitem, labeltouri)
        with open(outpath + corpusid + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=2))
            f.close()
        with open(outpath + corpusid + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        if self.has3d:
            if not os.path.exists(outpath + "/js"):
                os.makedirs(outpath + "/js")
            with open(outpath + "/js/corto.em.js", 'w', encoding='utf-8') as f:
                f.write(templates["corto.em"])
                f.close()
            with open(outpath + "/js/nexus.js", 'w', encoding='utf-8') as f:
                f.write(templates["nexus"])
                f.close()
        if self.apis["iiif"]:
            IIIFAPIExporter.generateIIIFAnnotations(outpath, imagetoURI)
        if self.createIndexPages:
            indpcounter = 0
            for path in paths:
                if indpcounter % 10 == 0:
                    self.updateProgressBar(indpcounter, len(paths), "Creating Index Pages")
                subgraph = Graph(bind_namespaces="rdflib")
                checkdepth = DocUtils.checkDepthFromPath(path, outpath, path) - 1
                sfilelink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth,
                                                                        corpusid + '_search.js', False)
                classtreelink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth,
                                                                            corpusid + "_classtree.js", False)
                stylelink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "style.css", False)
                scriptlink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "startscripts.js",
                                                                         False)
                proprelations = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth,
                                                                            "proprelations.js", False)
                epsgdefslink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "epsgdefs.js",
                                                                           False)
                vowllink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "vowl_result.js",
                                                                       False)
                nslink = prefixnamespace + str(self.getAccessFromBaseURL(str(outpath), str(path)))
                for sub in subjectstorender:
                    if nslink in sub:
                        for tup in self.graph.predicate_objects(sub):
                            subgraph.add((sub, tup[0], tup[1]))
                            if self.apis["solidexport"]:
                                subgraph.add((URIRef(sub.replace("nslink", "")),
                                              URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                                              URIRef("http://www.w3.org/ns/ldp#Container")))
                                subgraph.add((URIRef(sub.replace("nslink", "")),
                                              URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                                              URIRef("http://www.w3.org/ns/ldp#BasicContainer")))
                                subgraph.add((URIRef(sub.replace("nslink", "")),
                                              URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                                              URIRef("http://www.w3.org/ns/ldp#Resource")))
                for ex in self.exports:
                    if ex in ExporterUtils.exportToFunction:
                        if ex not in ExporterUtils.rdfformats:
                            with open(path + "index." + str(ex), 'w', encoding='utf-8') as f:
                                ExporterUtils.exportToFunction[ex](subgraph, f, subjectstorender, classlist, ex)
                                f.close()
                        else:
                            ExporterUtils.exportToFunction[ex](subgraph, path + "index." + str(ex), subjectstorender,
                                                               classlist, ex)
                relpath = DocUtils.generateRelativePathFromGivenDepth(checkdepth)
                indexhtml = self.replaceStandardVariables(templates["htmltemplate"], voidds, checkdepth,
                                                          str(nslink == prefixnamespace).lower())
                indexhtml = indexhtml.replace("{{iconprefixx}}",
                                              (relpath + "icons/" if self.offlinecompat else "")).replace("{{baseurl}}",
                                                                                                          prefixnamespace).replace(
                    "{{relativedepth}}", str(checkdepth)).replace("{{relativepath}}", relpath).replace("{{toptitle}}",
                                                                                                       "Index page for " + nslink).replace(
                    "{{title}}", "Index page for <span property=\"http://rdfs.org/ns/void#uriSpace\" content=\"" + str(
                        nslink) + "\">" + str(nslink) + "</span>").replace("{{startscriptpath}}", scriptlink).replace(
                    "{{stylepath}}", stylelink).replace("{{vowlpath}}", vowllink) \
                    .replace("{{classtreefolderpath}}", classtreelink).replace("{{baseurlhtml}}", nslink).replace(
                    "{{proprelationpath}}", proprelations).replace("{{nonnslink}}", "").replace("{{scriptfolderpath}}",
                                                                                                sfilelink).replace(
                    "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "").replace("{{subjectencoded}}",
                                                                                                 urllib.parse.quote(
                                                                                                     str(voidds)))
                indexhtml += "<p property=\"http://rdfs.org/ns/void#feature\" resource=\"http://www.w3.org/ns/formats/Turtle\">This page shows information about linked data resources in <span property=\"http://rdfs.org/ns/void#feature\" resource=\"http://www.w3.org/ns/formats/RDFa\">HTML</span>. Choose the classtree navigation or search to browse the data</p>" + \
                             templates["vowltemplate"].replace("{{vowlpath}}", "minivowl_result.js")
                if self.startconcept != None and path == outpath and self.startconcept in uritotreeitem:
                    if self.createColl:
                        indexhtml += "<p>Start exploring the graph here: <img src=\"" + \
                                     tree["types"][uritotreeitem[self.startconcept][-1]["type"]][
                                         "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + \
                                     uritotreeitem[self.startconcept][-1][
                                         "type"] + "\"/><a property=\"http://rdfs.org/ns/void#rootResource\" resource=\"" + str(
                            self.startconcept) + "\" href=\"" + DocUtils.generateRelativeLinkFromGivenDepth(
                            prefixnamespace, 0, str(self.startconcept), True) + "\">" + DocUtils.shortenURI(
                            self.startconcept) + "</a></p>"
                    else:
                        indexhtml += "<p>Start exploring the graph here: <img src=\"" + \
                                     tree["types"][uritotreeitem[self.startconcept][-1]["type"]][
                                         "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + \
                                     uritotreeitem[self.startconcept][-1][
                                         "type"] + "\"/><a property=\"http://rdfs.org/ns/void#rootResource\" resource=\"" + str(
                            self.startconcept) + "\" href=\"" + DocUtils.generateRelativeLinkFromGivenDepth(
                            prefixnamespace, 0, str(self.startconcept), True) + "\">" + DocUtils.shortenURI(
                            self.startconcept) + "</a></p>"
                indexhtml += "<table about=\"" + str(
                    voidds) + "\" typeof=\"http://rdfs.org/ns/void#Dataset\" property=\"http://rdfs.org/ns/void#dataDump\" resource=\"" + str(
                    self.deploypath + "/index.ttl") + "\" class=\"description\" style =\"height: 100%; overflow: auto\" border=1 id=indextable><thead><tr><th>Class</th><th>Number of instances</th><th>Instance Example</th></tr></thead><tbody>"
                for item in tree["core"]["data"]:
                    if (item["type"] == "geoclass" or item["type"] == "class" or item["type"] == "featurecollection" or
                        item["type"] == "geocollection") and "instancecount" in item and item["instancecount"] > 0:
                        exitem = None
                        for item2 in tree["core"]["data"]:
                            if item2["parent"] == item["id"] and (
                                    item2["type"] == "instance" or item2["type"] == "geoinstance") and nslink in item2[
                                "id"]:
                                checkdepth = DocUtils.checkDepthFromPath(path, prefixnamespace, item2["id"]) - 1
                                exitem = "<td><img src=\"" + tree["types"][item2["type"]][
                                    "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + item2[
                                             "type"] + "\"/><a property=\"http://rdfs.org/ns/void#exampleResource\" resource=\"" + str(
                                    DocUtils.shortenURI(
                                        str(item2["id"]))) + "\" href=\"" + DocUtils.generateRelativeLinkFromGivenDepth(
                                    prefixnamespace, checkdepth, str(re.sub("_suniv[0-9]+_", "", item2["id"])),
                                    True) + "\">" + str(item2["text"]) + "</a></td>"
                                break
                        if exitem != None:
                            if self.createColl:
                                indexhtml += "<tr><td><img src=\"" + tree["types"][item["type"]][
                                    "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + item[
                                                 "type"] + "\"/><a property=\"http://rdfs.org/ns/void#exampleResource\" resource=\"" + str(
                                    DocUtils.shortenURI(
                                        str(item["id"])) + "_collection/") + "\" href=\"" + DocUtils.shortenURI(
                                    str(item["id"])) + "_collection/index.html\" target=\"_blank\">" + str(
                                    item["text"]) + "</a></td>"
                            else:
                                indexhtml += "<tr><td><img src=\"" + tree["types"][item["type"]][
                                    "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + item[
                                                 "type"] + "\"/><a  href=\"" + str(
                                    item["id"]) + "\" target=\"_blank\">" + str(item["text"]) + "</a></td>"
                            indexhtml += "<td property=\"http://rdfs.org/ns/void#classPartition\" typeof=\"http://rdfs.org/ns/void#Dataset\" resource=\"" + str(
                                voidds) + "_" + str(DocUtils.shortenURI(item["id"])) + "\"><span about=\"" + str(
                                voidds) + "_" + str(DocUtils.shortenURI(
                                item["id"])) + "\" property=\"http://rdfs.org/ns/void#class\" resource=\"" + str(
                                item["id"]) + "\"></span><span about=\"" + str(voidds) + "_" + str(DocUtils.shortenURI(
                                item["id"])) + "\" property=\"http://rdfs.org/ns/void#entities\" content=\"" + str(item[
                                                                                                                       "instancecount"]) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#integer\">" + str(
                                item["instancecount"]) + "</td>" + exitem + "</tr>"
                indexhtml += "</tbody></table><script property=\"http://purl.org/dc/terms/modified\" content=\"" + str(
                    self.modtime) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#dateTime\">$('#indextable').DataTable();</script>"
                tempfoot = self.replaceStandardVariables(templates["footer"], "", checkdepth,
                                                           str(nslink == prefixnamespace).lower()).replace(
                    "{{license}}", curlicense).replace("{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}",
                                                                                                          "").replace(
                    "{{stats}}", self.voidstatshtml)
                tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, self.apis["ogcapifeatures"], self.apis["iiif"], self.apis["ckan"]],
                                                            [
                                                                "<a href=\"" + str(
                                                                    self.deploypath) + "/sparql.html?endpoint=" + str(
                                                                    self.deploypath) + "\">[SPARQL]</a>&nbsp;",
                                                                "<a href=\"" + str(
                                                                    self.deploypath) + "/api/api.html\">[OGC API Features]</a>&nbsp;",
                                                                "<a href=\"" + str(
                                                                    self.deploypath) + "/iiif/\">[IIIF]</a>&nbsp;",
                                                                "<a href=\"" + str(
                                                                    self.deploypath) + "/api/3/\">[CKAN]</a>"
                                                            ], "{{apis}}")
                indexhtml+=tempfoot
                # print(path)
                with open(path + "index.html", 'w', encoding='utf-8') as f:
                    f.write(indexhtml)
                    f.close()
        if "layouts" in templates:
            for template in templates["layouts"]:
                if template!="main":
                    templates["layouts"][template]=TemplateUtils.resolveIncludes(template,templates)
        if "sparqltemplate" in templates:
            sparqlhtml = self.replaceStandardVariables(templates["htmltemplate"], "", "0", "false")
            sparqlhtml = sparqlhtml.replace("{{iconprefixx}}", ("icons/" if self.offlinecompat else "")).replace(
                "{{baseurl}}", prefixnamespace).replace("{{relativedepth}}", "0").replace("{{relativepath}}",
                                                                                          ".").replace("{{toptitle}}",
                                                                                                       "SPARQL Query Editor").replace(
                "{{title}}", "SPARQL Query Editor").replace("{{startscriptpath}}", "startscripts.js").replace(
                "{{stylepath}}", "style.css") \
                .replace("{{classtreefolderpath}}", corpusid + "_classtree.js").replace("{{baseurlhtml}}", "").replace(
                "{{nonnslink}}", "").replace("{{scriptfolderpath}}", corpusid + "_search.js").replace("{{exports}}",
                                                                                                      templates[
                                                                                                          "nongeoexports"]).replace(
                "{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace("{{bibtex}}",
                                                                                                          "").replace(
                "{{proprelationpath}}", "proprelations.js")
            sparqlhtml += templates["sparqltemplate"]
            tempfoot = self.replaceStandardVariables(templates["footer"], "", "0", "false").replace("{{license}}",
                                                                                                       curlicense).replace(
                "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "").replace("{{stats}}",
                                                                                             self.voidstatshtml)
            tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, self.apis["ogcapifeatures"], self.apis["iiif"], self.apis["ckan"]],
                                                        [
                                                            "APIs: <a href=\"" + str(
                                                                self.deploypath) + "/sparql.html?endpoint=" + str(
                                                                self.deploypath) + "\">[SPARQL]</a>&nbsp;",
                                                            "<a href=\"" + str(
                                                                self.deploypath) + "/api/api.html\">[OGC API Features]</a>&nbsp;",
                                                            "<a href=\"" + str(self.deploypath) + "/iiif/\">[IIIF]</a>&nbsp;",
                                                            "<a href=\"" + str(self.deploypath) + "/api/3/\">[CKAN]</a>"
                                                        ], "{{apis}}")
            sparqlhtml += tempfoot
            with open(outpath + "sparql.html", 'w', encoding='utf-8') as f:
                f.write(sparqlhtml)
                f.close()
        relpath = DocUtils.generateRelativePathFromGivenDepth(0)
        if len(iiifmanifestpaths["default"]) > 0:
            IIIFAPIExporter.generateIIIFCollections(self.outpath, self.deploypath, iiifmanifestpaths["default"],
                                                    prefixnamespace)
            indexhtml = self.replaceStandardVariables(templates["htmltemplate"], "", "0", "true")
            indexhtml = indexhtml.replace("{{iconprefixx}}",
                                          (relpath + "icons/" if self.offlinecompat else "")).replace("{{baseurl}}",
                                                                                                      prefixnamespace).replace(
                "{{relativepath}}", relpath).replace("{{toptitle}}", "Feature Collection Overview").replace("{{title}}",
                                                                                                            "Image Grid View").replace(
                "{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{vowlpath}}",
                                                                                                        "vowl_result.js") \
                .replace("{{classtreefolderpath}}", corpusid + "_classtree.js").replace("{{proprelationpath}}",
                                                                                        "proprelations.js").replace(
                "{{nonnslink}}", "").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}",
                                                                            corpusid + '_search.js').replace(
                "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "")
            IIIFAPIExporter.generateImageGrid(self.outpath, self.deploypath, iiifmanifestpaths["default"],
                                              templates["imagegrid"], indexhtml,
                                              self.replaceStandardVariables(templates["footer"], "", "0",
                                                                            "true").replace("{{license}}",
                                                                                            curlicense).replace(
                                                  "{{subject}}", "").replace("{{exports}}",
                                                                             templates["nongeoexports"]).replace(
                                                  "{{bibtex}}", "").replace("{{stats}}", self.voidstatshtml),
                                              outpath + "imagegrid.html")
        if len(featurecollectionspaths) > 0 and self.apis["ckan"]:
            CKANExporter.generateCKANCollection(outpath, self.deploypath, featurecollectionspaths, tree["core"]["data"],
                                                self.license)
        if self.apis["solidexport"]:
            SolidExporter.createSolidSettings(self.graph, outpath, self.deploypath, self.publisher, self.datasettitle,
                                              tree["core"]["data"])
        if len(featurecollectionspaths) > 0:
            indexhtml = self.replaceStandardVariables(templates["htmltemplate"], "", "0", "true")
            indexhtml = indexhtml.replace("{{iconprefixx}}",
                                          (relpath + "icons/" if self.offlinecompat else "")).replace("{{baseurl}}",
                                                                                                      prefixnamespace).replace(
                "{{relativepath}}", relpath).replace("{{toptitle}}", "Feature Collection Overview").replace("{{title}}",
                                                                                                            "Feature Collection Overview").replace(
                "{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{vowlpath}}",
                                                                                                        "vowl_result.js") \
                .replace("{{classtreefolderpath}}", corpusid + "_classtree.js").replace("{{proprelationpath}}",
                                                                                        "proprelations.js").replace(
                "{{nonnslink}}", "").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}",
                                                                            corpusid + '_search.js').replace(
                "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "")
            OGCAPIFeaturesExporter.generateOGCAPIFeaturesPages(outpath, self.deploypath, featurecollectionspaths,
                                                               prefixnamespace, self.apis["ogcapifeatures"], True)
            indexhtml += "<p>This page shows feature collections present in the linked open data export</p>"
            indexhtml += "<script src=\"features.js\"></script>"
            indexhtml += templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace(
                "var featurecolls = {{myfeature}}", "").replace("{{relativepath}}",
                                                                DocUtils.generateRelativePathFromGivenDepth(0)).replace(
                "{{baselayers}}",
                json.dumps(DocConfig.baselayers).replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{dateatt}}", ""))
            tempfoot = self.replaceStandardVariables(templates["footer"], "", "0", "true").replace("{{license}}",
                                                                                                     curlicense).replace(
                "{{subject}}", "").replace("{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "").replace(
                "{{stats}}", self.voidstatshtml)
            tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, self.apis["ogcapifeatures"], self.apis["iiif"], self.apis["ckan"]],
                                                        [
                                                            "<a href=\"" + str(
                                                                self.deploypath) + "/sparql.html?endpoint=" + str(
                                                                self.deploypath) + "\">[SPARQL]</a>&nbsp;",
                                                            "<a href=\"" + str(
                                                                self.deploypath) + "/api/api.html\">[OGC API Features]</a>&nbsp;",
                                                            "<a href=\"" + str(self.deploypath) + "/iiif/\">[IIIF]</a>&nbsp;",
                                                            "<a href=\"" + str(self.deploypath) + "/api/3/\">[CKAN]</a>"
                                                        ], "{{apis}}")
            indexhtml+=tempfoot
            with open(outpath + "featurecollections.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()
        return subjectstorender


    def getSubjectPagesForNonGraphURIs(self, uristorender, graph, prefixnamespace, corpusid, outpath, nonnsmap, baseurl,
                                       uritotreeitem, labeltouri):
        nonnsuris = len(uristorender)
        counter = 0
        # print("NONS URIS TO RENDER: "+str(uristorender))
        for uri in uristorender:
            label = ""
            if prefixnamespace not in uri:
                # print("URI: " + str(uri))
                for tup in graph.predicate_objects(URIRef(uri)):
                    if str(tup[0]) in DocConfig.labelproperties:
                        label = str(tup[1])
                if uri in uritotreeitem:
                    res = DocUtils.replaceNameSpacesInLabel(self.prefixes, str(uri))
                    label = DocUtils.getLabelForObject(URIRef(str(uri)), graph, None, self.labellang)
                    if res != None and label != "":
                        uritotreeitem[uri][-1]["text"] = label + " (" + res["uri"] + ")"
                    elif label != "":
                        uritotreeitem[uri][-1]["text"] = label + " (" + DocUtils.shortenURI(uri) + ")"
                    else:
                        uritotreeitem[uri][-1]["text"] = DocUtils.shortenURI(uri)
                    uritotreeitem[uri][-1]["id"] = prefixnamespace + "nonns_" + DocUtils.shortenURI(uri) + ".html"
                    labeltouri[label] = prefixnamespace + "nonns_" + DocUtils.shortenURI(uri) + ".html"
                if counter % 10 == 0:
                    self.updateProgressBar(counter, nonnsuris, "NonNS URIs")
                self.htmlexporter.createHTML(outpath + "nonns_" + DocUtils.shortenURI(uri) + ".html", None, URIRef(uri), baseurl,
                                graph.subject_predicates(URIRef(uri), True), graph, str(corpusid) + "_search.js",
                                str(corpusid) + "_classtree.js", None, self.license, None, Graph(), uristorender, True,
                                label)
                counter += 1
        return labeltouri

    def polygonToPath(self, svg):
        svg = svg.replace("<polygon", "<path").replace("points=\"", "d=\"M").replace("\"></polygon>", " Z\"></polygon>")
        return svg.replace("<svg>",
                           "<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">")

    def getAccessFromBaseURL(self, baseurl, savepath):
        return savepath.replace(baseurl, "")

def main():
    prefixes = {"reversed": {}}
    print("PREFIX EXISTS? " + resourcepath + '/prefixes.json ' + str(os.path.exists(resourcepath + '/prefixes.json')))
    if os.path.exists(resourcepath + '/prefixes.json'):
        with open(resourcepath + '/prefixes.json', encoding="utf-8") as f:
            prefixes = json.load(f)
    prefixes["reversed"]["http://purl.org/cuneiform/"] = "cunei"
    prefixes["reversed"]["http://purl.org/graphemon/"] = "graphemon"
    prefixes["reversed"]["http://www.opengis.net/ont/crs/"] = "geocrs"
    prefixes["reversed"]["http://www.ontology-of-units-of-measure.org/resource/om-2/"] = "om"
    prefixes["reversed"]["http://purl.org/meshsparql/"] = "msp"
    outpath = []
    filestoprocess = []
    dataexports = []
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs='*', help="the input TTL file(s) to parse", action="store",
                        required=True)
    parser.add_argument("-o", "--output", nargs='*', help="the output path(s)", action="store", required=True)
    parser.add_argument("-pxns", "--prefixns", help="the prefixnamespace", action="store", default=None)
    parser.add_argument("-px", "--prefixnsshort", help="the prefix", action="store", default="suni")
    parser.add_argument("-ip", "--createIndexPages", help="create index pages?", default=True,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-cc", "--createCollections", help="create collections?", default=False,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-ll", "--labellang", help="preferred label language (default: en)", action="store",
                        default="en")
    parser.add_argument("-li", "--license", help="license under which this data is published", action="store",
                        default="")
    parser.add_argument('-ex', '--exports', nargs='+',
                        help="choose script exports to be generated next to HTML ['graphml', 'json', 'n3', 'nq', 'nt' 'tgf', 'trig', 'trix', 'ttl']",
                        action="store", default="ttl json")
    parser.add_argument("-lgu", "--logourl", help="URL of an optional page logo", action="store", default="")
    parser.add_argument("-dt", "--datasettitle", help="The title of this dataset to use in HTML templates",
                        action="store", default="")
    parser.add_argument("-pb", "--publisher", help="The publisher of this dataset", action="store", default="")
    parser.add_argument("-pbo", "--publishingorg", help="The organization responsible for publishing this dataset",
                        action="store", default="")
    parser.add_argument("-lo", "--localOptimized", help="build a version for local deployment", action="store",
                        default=False, type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-mdt", "--metadatatable", help="create metadata table?", action="store", default=False,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-nnsp", "--nonnspages", help="create nonns pages?", action="store", default=False,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-vowl", "--createvowl", help="create vowl graph view?", action="store", default=False,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-of", "--offlinecompat", help="built-result is offline compatible", default=False,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-ogc", "--ogcapifeatures", help="create ogc api features collections?", action="store",
                        default=False, type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-stac", "--stacapi", help="create stac api collections?", action="store", default=False,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-iiif", "--iiifmanifest", help="create iiif manifests?", action="store", default=True,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-solid", "--solidexport", help="create solid pod deployment?", action="store", default=True,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-imgmd", "--imagemetadata", help="resolve image metadata?", action="store", default=False,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-ckan", "--ckanapi", help="create static ckan api docs?", action="store", default=True,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-sc", "--startconcept", help="the concept suggested for browsing the HTML documentation",
                        action="store", default=None)
    parser.add_argument("-rp", "--repository", help="the repository where the dataset is stored", action="store",
                        default="")
    parser.add_argument("-dp", "--deploypath", help="the deploypath where the documentation will be hosted",
                        action="store", default="")
    parser.add_argument("-tp", "--templatepath", help="the path of the HTML template", action="store",
                        default="resources/html/")
    parser.add_argument("-tn", "--templatename", help="the name of the HTML template", action="store",
                        default="default")
    args, unknown = parser.parse_known_args()
    print(args)
    print("The following arguments were not recognized: " + str(unknown))
    if args.input == None or args.input[0] == "None" or args.input == "":
        print("No input files specified... trying to find files in the script folder")
        args.input = DocUtils.getLDFilesFromFolder(".")
        print("Found " + str(args.input))
    for path in args.input:
        if " " in path:
            for itemm in path.split(" "):
                filestoprocess += DocUtils.resolveWildcardPath(itemm)
        else:
            filestoprocess += DocUtils.resolveWildcardPath(path)
    print("Files to process: " + str(filestoprocess))
    for path in args.output:
        if " " in path:
            for itemm in path.split(" "):
                outpath.append(itemm)
        else:
            outpath.append(path)

    print("ARG EXPORTS: " + str(args.exports))
    for expo in args.exports:
        if " " in expo:
            for ex in expo.split(" "):
                if ex not in dataexports:
                    dataexports.append(ex)
        elif expo not in dataexports:
            dataexports.append(expo)
    print("EXPORTS: "+str(dataexports))
    print(os.listdir(os.getcwd()))
    if args.templatepath!=None:
        templatepath=args.templatepath
        if templatepath.startswith("http") and templatepath.endswith(".zip"):
            with urlopen(templatepath) as zipresp:
                with ZipFile(BytesIO(zipresp.read())) as zfile:
                    subfoldername = zfile.namelist()[0][0:zfile.namelist()[0].rfind('/')]
                    zfile.extractall('ontdocscript/src/sparqlunicorn_ontdoc/resources/html/')
                    templatepath = "ontdocscript/src/sparqlunicorn_ontdoc/resources/html/" + subfoldername
                    if subfoldername.endswith("/"):
                        subfoldername = subfoldername[0:-1]
                    templatepath = "ontdocscript/src/sparqlunicorn_ontdoc/resources/html/" + subfoldername[0:subfoldername.rfind('/') + 1]
                    args.templatename = subfoldername
                    if templatepath.endswith("/"):
                        templatepath = templatepath[0:-1]
                    print(templatepath)
                    print(subfoldername)
                    print(args.templatename)
    fcounter = 0
    docgen = None
    g = Graph()
    subrend = None
    for fp in filestoprocess:
        try:
            g = Graph()
            g.parse(fp)
            g=DocUtils.resolveOWLImports(g)
            modtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%dT%H:%M:%S")
            if args.prefixns == None or args.prefixns == "None":
                print("No Datanamespace defined. Trying to detect it...")
                pres = DocUtils.getDataNamespace(g)
                if pres == None:
                    args.prefixns = "http://www.sparqlunicorn.link/data/"
                else:
                    args.prefixns = pres
                print("Detected " + args.prefixns + " as data namespace")
            apis={"iiif":args.iiifmanifest,"ogcapifeatures":args.ogcapifeatures,"ckan":args.ckanapi,"solidexport":args.solidexport,"stac":args.stacapi}
            if fcounter < len(outpath):
                docgen = OntDocGeneration(prefixes, modtime, args.prefixns, args.prefixnsshort, args.license,
                                          args.labellang, outpath[fcounter], g, args.createIndexPages,
                                          args.createCollections, args.metadatatable, args.nonnspages, args.createvowl,
                                          apis,
                                          args.localOptimized, args.imagemetadata, args.startconcept, args.repository,
                                          args.deploypath, args.logourl, args.templatename, args.offlinecompat,
                                          dataexports, args.datasettitle, args.publisher, args.publishingorg)
            else:
                docgen = OntDocGeneration(prefixes, modtime, args.prefixns, args.prefixnsshort, args.license,
                                          args.labellang, outpath[-1], g, args.createIndexPages, args.createCollections,
                                          args.metadatatable, args.nonnspages, args.createvowl, apis, args.localOptimized,
                                          args.imagemetadata, args.startconcept, args.repository, args.deploypath,
                                          args.logourl, args.templatename, args.offlinecompat, dataexports,
                                          args.datasettitle, args.publisher, args.publishingorg)
            subrend = docgen.generateOntDocForNameSpace(args.prefixns, dataformat="HTML")
        except Exception as inst:
            print("Could not parse " + str(fp))
            print(inst)
            print(traceback.format_exc())
        fcounter += 1
    curlicense = license
    if docgen != None:
        curlicense = docgen.licensehtml
    print("Path exists? " + outpath[0] + '/index.html ' + str(os.path.exists(outpath[0] + '/index.html')))
    if not os.path.exists(outpath[0] + '/index.ttl') and subrend != None:
        resg = Graph()
        for sub in subrend:
            for predobj in g.predicate_objects(sub):
                resg.add((sub, predobj[0], predobj[1]))
                if args.solidexport:
                    resg.add((sub, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                              URIRef("http://www.w3.org/ns/ldp#Container")))
                    resg.add((sub, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                              URIRef("http://www.w3.org/ns/ldp#BasicContainer")))
                    resg.add((sub, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                              URIRef("http://www.w3.org/ns/ldp#Resource")))
        resg.serialize(outpath[0] + '/index.ttl')
    if not os.path.exists(outpath[0] + '/index.html'):
        indexf = open(outpath[0] + "/index.html", "w", encoding="utf-8")
        nonnslink = ""
        relpath = ""
        indexhtml = docgen.replaceStandardVariables(templates["htmltemplate"], "", "0", "true")
        indexhtml = indexhtml.replace("{{iconprefixx}}", (relpath + "icons/" if args.offlinecompat else "")).replace(
            "{{baseurl}}", args.prefixns).replace("{{relativepath}}", relpath).replace("{{relativedepth}}",
                                                                                       "0").replace("{{toptitle}}",
                                                                                                    "Index page").replace(
            "{{title}}", "Index page").replace("{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}",
                                                                                                 "style.css") \
            .replace("{{classtreefolderpath}}", args.prefixnsshort + "_classtree.js").replace("{{baseurlhtml}}",
                                                                                              ".").replace(
            "{{nonnslink}}", str(nonnslink)).replace("{{proprelationpath}}", "proprelations.js").replace(
            "{{scriptfolderpath}}", args.prefixnsshort + '_search.js').replace("{{exports}}",
                                                                               templates["nongeoexports"]).replace(
            "{{bibtex}}", "")
        indexhtml += "<p>This page shows information about linked data resources in HTML. Choose the classtree navigation or search to browse the data</p>"
        indexhtml += "<table class=\"description\" border=1 id=indextable><thead><tr><th>Dataset</th></tr></thead><tbody>"
        subfolders = [f.path for f in os.scandir(outpath[0]) if f.is_dir()]
        print(subfolders)
        for path in subfolders:
            indexhtml += "<tr><td><a href=\"" + path.replace(outpath[0] + "/", "") + "/index.html\">" + path.replace(
                outpath[0] + "/", "") + "</a></td></tr>"
        indexhtml += "</tbody></table><script>$('#indextable').DataTable();</script>"
        indexhtml += templates["footer"].replace("{{license}}", curlicense).replace("{{exports}}",
                                                                                    templates["nongeoexports"]).replace(
            "{{bibtex}}", "").replace("{{stats}}", "")
        # print(indexhtml)
        indexf.write(indexhtml)
        indexf.close()


if __name__ == "__main__":
    main()