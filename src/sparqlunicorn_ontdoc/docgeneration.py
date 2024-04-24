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

from export.data.htmlexporter import HTMLExporter
from export.data.voidexporter import VoidExporter
from export.pages.indexviewpage import IndexViewPage
from export.pages.sparqlpage import SPARQLPage

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
from export.api.iiifexporter import IIIFAPIExporter
from export.api.ogcapifeaturesexporter import OGCAPIFeaturesExporter
from export.api.ckanexporter import CKANExporter
from export.api.solidexporter import SolidExporter

import argparse
import shutil
import json

templatepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/html/"))
resourcepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/"))

templates = DocDefaults.templates

class OntDocGeneration:

    def __init__(self, prefixes, modtime, outpath, apis, graph, pubconfig, exports=["json", "ttl"]):

        self.pubconfig=pubconfig
        self.pubconfig["namespaceshort"]=pubconfig["prefixnsshort"].replace("/","")
        self.pubconfig["outpath"]=outpath
        self.pubconfig["apis"]=apis
        self.pubconfig["modtime"]=modtime
        self.pubconfig["prefixes"]=prefixes
        self.pubconfig["exports"]=exports
        self.geocache={}
        self.geocollectionspaths=[]
        self.templatename=pubconfig["templatename"]
        templates = TemplateUtils.resolveTemplate(pubconfig["templatename"], templatepath)
        if pubconfig["offlinecompat"]:
            templates["htmltemplate"] = DocUtils.createOfflineCompatibleVersion(outpath, templates["htmltemplate"],
                                                                            templatepath, pubconfig["templatename"])
            templates["maptemplate"] = DocUtils.createOfflineCompatibleVersion(outpath, templates["maptemplate"],
                                                                           templatepath, pubconfig["templatename"])
            templates["sparqltemplate"] = DocUtils.createOfflineCompatibleVersion(outpath, templates["sparqltemplate"],
                                                                              templatepath, pubconfig["templatename"])
        self.licenseuri = None
        self.licensehtml = None
        self.typeproperty = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        self.subclassproperty = "http://www.w3.org/2000/01/rdf-schema#subClassO"
        keyprops=GraphUtils.determineKeyProperties(graph)
        if len(keyprops["typeproperty"])>0:
            self.typeproperty=keyprops["typeproperty"][0]
        if len(keyprops["subclassproperty"])>0:
            self.suclassproperty=keyprops["subclassproperty"][0]
        self.graph = graph
        self.htmlexporter=HTMLExporter(pubconfig,templates,self.typeproperty)
        for nstup in self.graph.namespaces():
            if str(nstup[1]) not in prefixes["reversed"]:
                prefixes["reversed"][str(nstup[1])] = str(nstup[0])
        self.preparedclassquery = prepareQuery(DocConfig.classtreequery.replace("%%typeproperty%%","<"+self.typeproperty+">").replace("%%subclassproperty%%","<"+self.subclassproperty+">"))
        if self.pubconfig["prefixns"] is None or pubconfig["prefixnsshort"] is None or self.pubconfig["prefixns"] == "" or pubconfig["prefixnsshort"] == "":
            self.pubconfig["namespaceshort"] = "suni"
            self.pubconfig["prefixns"] = "http://purl.org/suni/"
        if not self.pubconfig["prefixns"].endswith("/") and not self.pubconfig["prefixns"].endswith("#"):
            self.pubconfig["prefixns"] += "/"
        if self.pubconfig["outpath"] is None:
            self.pubconfig["outpath"] = "suni_htmls/"
        else:
            self.pubconfig["outpath"] = self.pubconfig["outpath"].replace("\\", "/")
            if not self.pubconfig["outpath"].endswith("/"):
                self.pubconfig["outpath"] += "/"
        self.pubconfig["outpath"] = self.pubconfig["outpath"].replace("//", "/")
        #self.pubconfig["prefixns"] = self.pubconfig["prefixns"].replace("//", "/")
        # prefixes["reversed"]["http://purl.org/suni/"] = "suni"


    def generateOntDocForNameSpace(self, prefixnamespace,dataformat="HTML"):
        outpath=self.pubconfig["outpath"]
        self.pubconfig["corpusid"]=self.pubconfig["namespaceshort"].replace("#","")
        if self.pubconfig["datasettitle"] is None or self.pubconfig["datasettitle"]== "":
            self.pubconfig["datasettitle"]=self.pubconfig["corpusid"].replace(" ","_")+"_dataset"
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        labeltouri = {}
        uritolabel = {}
        uritotreeitem = {}
        if self.pubconfig["createvowl"]:
            vowlinstance = OWL2VOWL()
            vowlinstance.convertOWL2VOWL(self.graph, outpath)
        tmp=HTMLExporter.processLicense(self.pubconfig["license"])
        curlicense=tmp[0]
        self.licensehtml = tmp[0]
        self.pubconfig["licenseuri"]=tmp[1]
        voidds = prefixnamespace + self.pubconfig["datasettitle"].replace(" ","_")
        if self.pubconfig["createCollections"]:
            self.graph = GraphUtils.createCollections(self.graph, prefixnamespace,self.typeproperty)
        if self.pubconfig["logourl"] is not None and self.pubconfig["logourl"] != "" and not self.pubconfig["logourl"].startswith("http"):
            logoname=self.pubconfig["logourl"]
            if not os.path.isdir(outpath + "/logo/"):
                os.mkdir(outpath + "/logo/")
            shutil.copy(logoname, outpath + "/logo/logo." + logoname[logoname.rfind("."):])
            self.pubconfig["logourl"] = outpath + "/logo/logo." + logoname[logoname.rfind("."):]
        DocUtils.updateProgressBar(0, 1, "Creating classtree and search index")
        res=GraphUtils.analyzeGraph(self.graph, prefixnamespace, self.typeproperty, voidds, labeltouri, uritolabel, self.pubconfig["outpath"], self.pubconfig["createvowl"])
        subjectstorender=res["subjectstorender"]
        if not self.pubconfig["apis"]["iiif"]:
            self.pubconfig["apis"]["iiif"]=res["iiif"]
        if os.path.exists(outpath + self.pubconfig["corpusid"] + '_search.js'):
            try:
                with open(outpath + self.pubconfig["corpusid"] + '_search.js', 'r', encoding='utf-8') as f:
                    data = json.loads(f.read().replace("var search=", ""))
                    for key in data:
                        labeltouri[key] = data[key]
            except Exception as e:
                print("Exception occurred " + str(e))
                print(traceback.format_exc())
        with open(outpath + self.pubconfig["corpusid"] + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        if self.pubconfig["offlinecompat"]:
            if os.path.exists(outpath + "icons/"):
                shutil.rmtree(outpath + "icons/")
            shutil.copytree(templatepath + "/" + self.templatename + "/icons/", outpath + "icons/")
        prevtree = []
        if os.path.exists(outpath + self.pubconfig["corpusid"] + '_classtree.js'):
            try:
                with open(outpath + self.pubconfig["corpusid"] + '_classtree.js', 'r', encoding='utf-8') as f:
                    prevtree = json.loads(f.read().replace("var tree=", ""))["core"]["data"]
            except Exception as e:
                print("Exception occurred " + str(e))
        classidset = set()
        clsress = ClassTreeUtils.getClassTree(self.graph, uritolabel, classidset, uritotreeitem,self.typeproperty,self.pubconfig["prefixes"],self.preparedclassquery)
        tree=clsress[0]
        uritotreeitem=clsress[1]
        classidset=clsress[2]
        with open(outpath + self.pubconfig["corpusid"] + "_classtree_raw.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=2))
            f.close()
        #print(str(tree))
        for tr in prevtree:
            if tr["id"] not in classidset:
                tree["core"]["data"].append(tr)
        res["voidstats"]["http://rdfs.org/ns/void#classes"] = len(classidset)
        res["voidstats"]["http://rdfs.org/ns/void#triples"] = len(self.graph)
        voidgraph = VoidExporter.createVoidDataset(self.pubconfig, self.pubconfig["licenseuri"],
                                                   res["voidstats"], subjectstorender,
                                                   tree, res["predmap"], res["nonnscount"], res["nscount"], res["instancecount"])
        self.voidstatshtml = VoidExporter.toHTML(res["voidstats"], self.pubconfig["deploypath"])
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
                                  self.graph, str(self.pubconfig["corpusid"]) + "_search.js", str(self.pubconfig["corpusid"]) + "_classtree.js",
                                  uritotreeitem, curlicense, subjectstorender, postprocessing, nonnsmap)
            postprocessing = res[0]
            nonnsmap = res[1]
            subtorencounter += 1
            if subtorencounter % 250 == 0:
                subtorenderlen = len(subjectstorender) + len(postprocessing)
                DocUtils.updateProgressBar(subtorencounter, subtorenderlen, "Processing Subject URIs")
            # except Exception as e:
            #    print("Create HTML Exception: "+str(e))
            #    print(traceback.format_exc())
        print("Postprocessing " + str(len(postprocessing)))
        subtorenderlen = len(subjectstorender) + len(postprocessing)
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
                            self.graph, str(self.pubconfig["corpusid"]) + "_search.js", str(self.pubconfig["corpusid"]) + "_classtree.js", uritotreeitem,
                            curlicense, subjectstorender, postprocessing)
            subtorencounter += 1
            if subtorencounter % 250 == 0:
                DocUtils.updateProgressBar(subtorencounter, subtorenderlen, "Processing Subject URIs")
        ClassTreeUtils.checkGeoInstanceAssignment(uritotreeitem)
        classlist = ClassTreeUtils.assignGeoClassesToTree(tree)
        if self.pubconfig["nonnspages"]:
            labeltouri = self.getSubjectPagesForNonGraphURIs(nonnsmap, self.graph, prefixnamespace, self.pubconfig["corpusid"], outpath,
                                                             self.pubconfig["license"], prefixnamespace, uritotreeitem, labeltouri)
        with open(outpath + self.pubconfig["corpusid"] + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=2))
            f.close()
        with open(outpath +  self.pubconfig["corpusid"] + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        if self.htmlexporter.has3d:
            if not os.path.exists(outpath + "/js"):
                os.makedirs(outpath + "/js")
            with open(outpath + "/js/corto.em.js", 'w', encoding='utf-8') as f:
                f.write(templates["corto.em"])
                f.close()
            with open(outpath + "/js/nexus.js", 'w', encoding='utf-8') as f:
                f.write(templates["nexus"])
                f.close()
        if self.pubconfig["apis"]["iiif"]:
            IIIFAPIExporter.generateIIIFAnnotations(outpath, self.htmlexporter.imagetoURI)
        if self.pubconfig["createIndexPages"]:
            IndexViewPage.createIndexPages(self.pubconfig,templates,self.pubconfig["apis"],paths,subjectstorender,uritotreeitem,voidds,tree,classlist,self.graph,self.voidstatshtml,curlicense)
        if "layouts" in templates:
            for template in templates["layouts"]:
                if template!="main":
                    templates["layouts"][template]=TemplateUtils.resolveIncludes(template,templates)
        if "sparqltemplate" in templates:
            with open(outpath + "sparql.html", 'w', encoding='utf-8') as f:
                SPARQLPage().generatePageView(templates, self.pubconfig, curlicense, self.voidstatshtml,self.graph, f)
                f.close()
        relpath = DocUtils.generateRelativePathFromGivenDepth(0)
        if len(self.htmlexporter.iiifmanifestpaths["default"]) > 0:
            IIIFAPIExporter.generateIIIFCollections(self.pubconfig["outpath"], self.pubconfig["deploypath"], self.htmlexporter.iiifmanifestpaths["default"],
                                                    prefixnamespace)
            indexhtml = DocUtils.replaceStandardVariables(templates["htmltemplate"], "", "0", "true",self.pubconfig)
            indexhtml = indexhtml.replace("{{iconprefixx}}",
                                          (relpath + "icons/" if self.pubconfig["offlinecompat"] else "")).replace("{{baseurl}}",
                                                                                                      self.pubconfig["prefixns"]).replace(
                "{{relativepath}}", relpath).replace("{{toptitle}}", "Feature Collection Overview").replace("{{title}}",
                                                                                                            "Image Grid View").replace(
                "{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{vowlpath}}",
                                                                                                        "vowl_result.js") \
                .replace("{{classtreefolderpath}}", self.pubconfig["corpusid"] + "_classtree.js").replace("{{proprelationpath}}",
                                                                                        "proprelations.js").replace(
                "{{nonnslink}}", "").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}",
                                                                            self.pubconfig["corpusid"] + '_search.js').replace(
                "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "")
            IIIFAPIExporter.generateImageGrid(self.pubconfig["outpath"], self.pubconfig["deploypath"], self.htmlexporter.iiifmanifestpaths["default"],
                                              templates["imagegrid"], indexhtml,
                                              DocUtils.replaceStandardVariables(templates["footer"], "", "0",
                                                                            "true",self.pubconfig).replace("{{license}}",
                                                                                            curlicense).replace(
                                                  "{{subject}}", "").replace("{{exports}}",
                                                                             templates["nongeoexports"]).replace(
                                                  "{{bibtex}}", "").replace("{{stats}}", self.voidstatshtml),
                                              outpath + "imagegrid.html")
        if len(self.htmlexporter.featurecollectionspaths) > 0 and self.pubconfig["apis"]["ckan"]:
            CKANExporter.generateCKANCollection(outpath, self.pubconfig["deploypath"], self.htmlexporter.featurecollectionspaths, tree["core"]["data"],
                                                self.pubconfig["license"])
        if self.pubconfig["apis"]["solidexport"]:
            SolidExporter.createSolidSettings(self.graph, outpath, self.pubconfig["deploypath"], self.pubconfig["publisher"], self.pubconfig["datasettitle"],
                                              tree["core"]["data"])
        if len(self.htmlexporter.featurecollectionspaths) > 0:
            indexhtml = DocUtils.replaceStandardVariables(templates["htmltemplate"], "", "0", "true",self.pubconfig)
            indexhtml = indexhtml.replace("{{iconprefixx}}",
                                          (relpath + "icons/" if self.pubconfig["offlinecompat"] else "")).replace("{{baseurl}}",
                                                                                                      self.pubconfig["prefixns"]).replace(
                "{{relativepath}}", relpath).replace("{{toptitle}}", "Feature Collection Overview").replace("{{title}}",
                                                                                                            "Feature Collection Overview").replace(
                "{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{vowlpath}}",
                                                                                                        "vowl_result.js") \
                .replace("{{classtreefolderpath}}", self.pubconfig["corpusid"] + "_classtree.js").replace("{{proprelationpath}}",
                                                                                        "proprelations.js").replace(
                "{{nonnslink}}", "").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}",
                                                                            self.pubconfig["corpusid"] + '_search.js').replace(
                "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "")
            OGCAPIFeaturesExporter.generateOGCAPIFeaturesPages(outpath, self.pubconfig["deploypath"], self.htmlexporter.featurecollectionspaths,
                                                               self.pubconfig["prefixns"], self.pubconfig["apis"]["ogcapifeatures"], True)
            indexhtml += "<p>This page shows feature collections present in the linked open data export</p>"
            indexhtml += "<script src=\"features.js\"></script>"
            indexhtml += templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace(
                "var featurecolls = {{myfeature}}", "").replace("{{relativepath}}",
                                                                DocUtils.generateRelativePathFromGivenDepth(0)).replace(
                "{{baselayers}}",
                json.dumps(DocConfig.baselayers).replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{dateatt}}", ""))
            tempfoot = DocUtils.replaceStandardVariables(templates["footer"], "", "0", "true",self.pubconfig).replace("{{license}}",
                                                                                                     curlicense).replace(
                "{{subject}}", "").replace("{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "").replace(
                "{{stats}}", self.voidstatshtml)
            tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, self.pubconfig["apis"]["ogcapifeatures"], self.pubconfig["apis"]["iiif"], self.pubconfig["apis"]["ckan"]],
                                                        [
                                                            "<a href=\"sparql.html?endpoint=" + str(
                                                                self.pubconfig["deploypath"]) + "\">[SPARQL]</a>&nbsp;",
                                                            "<a href=\"api/api.html\">[OGC API Features]</a>&nbsp;",
                                                            "<a href=\"iiif/\">[IIIF]</a>&nbsp;",
                                                            "<a href=\"api/3/\">[CKAN]</a>"
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
                    res = DocUtils.replaceNameSpacesInLabel(self.pubconfig["prefixes"], str(uri))
                    label = DocUtils.getLabelForObject(URIRef(str(uri)), graph, None, self.pubconfig["labellang"])
                    if res is not None and label != "":
                        uritotreeitem[uri][-1]["text"] = label + " (" + res["uri"] + ")"
                    elif label != "":
                        uritotreeitem[uri][-1]["text"] = label + " (" + DocUtils.shortenURI(uri) + ")"
                    else:
                        uritotreeitem[uri][-1]["text"] = DocUtils.shortenURI(uri)
                    uritotreeitem[uri][-1]["id"] = prefixnamespace + "nonns_" + DocUtils.shortenURI(uri) + ".html"
                    labeltouri[label] = prefixnamespace + "nonns_" + DocUtils.shortenURI(uri) + ".html"
                if counter % 10 == 0:
                    DocUtils.updateProgressBar(counter, nonnsuris, "NonNS URIs")
                self.htmlexporter.createHTML(outpath + "nonns_" + DocUtils.shortenURI(uri) + ".html", None, URIRef(uri), baseurl,
                                graph.subject_predicates(URIRef(uri), True), graph, str(corpusid) + "_search.js",
                                str(corpusid) + "_classtree.js", None, self.pubconfig["license"], None, Graph(), uristorender, True,
                                label)
                counter += 1
        return labeltouri

    def polygonToPath(self, svg):
        svg = svg.replace("<polygon", "<path").replace("points=\"", "d=\"M").replace("\"></polygon>", " Z\"></polygon>")
        return svg.replace("<svg>",
                           "<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">")

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
    #print(args)
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
            if args.prefixns is None or args.prefixns == "None":
                print("No Datanamespace defined. Trying to detect it...")
                pres = DocUtils.getDataNamespace(g)
                if pres is None:
                    args.prefixns = "http://www.sparqlunicorn.link/data/"
                else:
                    args.prefixns = pres
                print("Detected " + args.prefixns + " as data namespace")
            apis={"iiif":args.iiifmanifest,"ogcapifeatures":args.ogcapifeatures,"ckan":args.ckanapi,"solidexport":args.solidexport,"stac":args.stacapi}
            #print("Args: "+str(vars(args)))
            if fcounter < len(outpath):
                docgen = OntDocGeneration(prefixes, modtime, outpath[fcounter],apis, g, vars(args),dataexports)
            else:
                docgen = OntDocGeneration(prefixes, modtime, outpath[-1],apis, g, vars(args),dataexports)
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
        indexhtml = DocUtils.replaceStandardVariables(templates["htmltemplate"], "", "0", "true",docgen.pubconfig)
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
        #print(subfolders)
        for path in subfolders:
            indexhtml += "<tr><td><a href=\"" + path.replace(outpath[0] + "/", "") + "/index.html\">" + path.replace(
                outpath[0] + "/", "") + "</a></td></tr>"
        indexhtml += "</tbody></table><script>$('#indextable').DataTable();</script>"
        indexhtml += DocUtils.replaceStandardVariables(templates["footer"], "", "0", "true",docgen.pubconfig).replace("{{license}}", curlicense).replace("{{exports}}",
                                                                                    templates["nongeoexports"]).replace(
            "{{bibtex}}", "").replace("{{stats}}", "")
        # print(indexhtml)
        indexf.write(indexhtml)
        indexf.close()


if __name__ == "__main__":
    main()