# -*- coding: UTF-8 -*-
from sys import prefix

from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib.namespace import RDF
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
from export.data.vowlexporter import VOWLExporter
from export.api.iiifexporter import IIIFAPIExporter
from export.api.ogcapifeaturesexporter import OGCAPIFeaturesExporter
from export.api.ckanexporter import CKANExporter
from export.api.wfsexporter import WFSExporter
from export.api.solidexporter import SolidExporter

import argparse
import shutil
import json
import time
from collections import OrderedDict, defaultdict

templatepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/html/"))
resourcepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/"))

templates = DocDefaults.templates

class OntDocGeneration:

    def __init__(self, prefixes, modtime, outpath, apis, graph, pubconfig, exports=["json", "ttl"]):
        self.exectimes=OrderedDict()
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
        self.subclassproperty = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        keyprops=GraphUtils.determineKeyProperties(graph)
        if len(keyprops["typeproperty"])>0:
            self.typeproperty=keyprops["typeproperty"][0]
        if len(keyprops["subclassproperty"])>0:
            self.subclassproperty=keyprops["subclassproperty"][0]
        self.graph = graph
        self.htmlexporter=HTMLExporter(pubconfig,templates,self.typeproperty)
        for nstup in self.graph.namespaces():
            prefixes["reversed"].setdefault(str(nstup[1]),str(nstup[0]))
        self.preparedclassquery = prepareQuery(DocConfig.classtreequery.replace("%%typeproperty%%",f"<{self.typeproperty}>").replace("%%subclassproperty%%",f"<{self.subclassproperty}>"))
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
            vowlinstance = VOWLExporter()
            vowlinstance.convertOWL2VOWL(self.graph, outpath)
        tmp=HTMLExporter.processLicense(self.pubconfig["license"])
        curlicense=tmp[0]
        self.licensehtml = tmp[0]
        self.pubconfig["licenseuri"]=tmp[1]
        voidds = prefixnamespace + self.pubconfig["datasettitle"].replace(" ","_")
        if self.pubconfig["createCollections"]:
            start=time.time()
            ccls=self.pubconfig["collectionClass"]
            self.graph = GraphUtils.createCollections(self.graph, prefixnamespace,self.typeproperty,ccls)
            end=time.time()
            self.exectimes["Create Collections"] = {"time": end - start}
        if self.pubconfig["logourl"] is not None and self.pubconfig["logourl"] != "" and not self.pubconfig["logourl"].startswith("http"):
            logoname=self.pubconfig["logourl"]
            if not os.path.isdir(outpath + "/logo/"):
                os.mkdir(outpath + "/logo/")
            shutil.copy(logoname, f'{outpath}/logo/logo.{logoname[logoname.rfind("."):]}')
            self.pubconfig["logourl"] = f'{outpath}/logo/logo.{logoname[logoname.rfind("."):]}'
        DocUtils.updateProgressBar(0, 1, "Creating classtree and search index")
        start=time.time()
        res=GraphUtils.analyzeGraph(self.graph, prefixnamespace, self.typeproperty, voidds, labeltouri, uritolabel, self.pubconfig["outpath"], self.pubconfig["createvowl"])
        subjectstorender=res["subjectstorender"]
        end=time.time()
        self.exectimes["Graph Analysis"]={"time":end-start}
        if not self.pubconfig["apis"]["iiif"]:
            self.pubconfig["apis"]["iiif"]=res["iiif"]
        searchjspath=f'{outpath}{self.pubconfig["corpusid"]}_search.js'
        classtreepath=f'{outpath}{self.pubconfig["corpusid"]}_classtree.js'
        if os.path.exists(searchjspath):
            try:
                with open(searchjspath, 'r', encoding='utf-8') as f:
                    data = json.loads(f.read().replace("var search=", ""))
                    for key in data:
                        labeltouri[key] = data[key]
            except Exception as e:
                print("Exception occurred " + str(e))
                print(traceback.format_exc())
        with open(searchjspath, 'w', encoding='utf-8') as f:
            f.write("var search=")
            json.dump(labeltouri,f, indent=2, sort_keys=True)
        if self.pubconfig["offlinecompat"]:
            if os.path.exists(outpath + "icons/"):
                shutil.rmtree(outpath + "icons/")
            shutil.copytree(f"{templatepath}/{self.templatename}/icons/", outpath + "icons/")
        prevtree = []
        if os.path.exists(classtreepath):
            try:
                with open(classtreepath, 'r', encoding='utf-8') as f:
                    prevtree = json.loads(f.read().replace("var tree=", ""))["core"]["data"]
            except Exception as e:
                print("Exception occurred " + str(e))
        #classidset = set()
        start=time.time()
        clsress = ClassTreeUtils.getClassTree(self.graph, uritolabel, uritotreeitem,self.typeproperty,self.pubconfig["prefixes"],self.preparedclassquery,res["instancecount"],self.pubconfig["outpath"],self.pubconfig)
        end=time.time()
        self.exectimes["Class Tree Generation"]={"time":end-start,"items":clsress[2]}
        print(f"Class Tree Generation time for {clsress[2]} classes: {end-start} seconds")
        tree,uritotreeitem,numclasses=clsress
        #print(str(tree))
        tree["core"]["data"]+=[tr for tr in prevtree if tr["id"] not in uritotreeitem]
        #for tr in prevtree:
        #    if tr["id"] not in uritotreeitem:
        #        tree["core"]["data"].append(tr)
        res["voidstats"]["http://rdfs.org/ns/void#classes"] = numclasses
        res["voidstats"]["http://rdfs.org/ns/void#triples"] = len(self.graph)
        start=time.time()
        voidgraph = VoidExporter.createVoidDataset(self.pubconfig, self.pubconfig["licenseuri"],
                                                   res["voidstats"], subjectstorender,
                                                   tree, res["predmap"], res["nonnscount"], res["nscount"], res["instancecount"])
        self.voidstatshtml = VoidExporter.toHTML(res["voidstats"], self.pubconfig["deploypath"])
        self.graph += voidgraph["graph"]
        subjectstorender = voidgraph["subjects"]
        end=time.time()
        self.exectimes["Void stats generation"]={"time":end-start,"items":numclasses}
        print(f"Void stats generation time for {numclasses} classes: {end-start} seconds")
        with open(outpath + "style.css", 'w', encoding='utf-8') as f:
            f.write(templates["style"])
        with open(outpath + "startscripts.js", 'w', encoding='utf-8') as f:
            f.write(templates["startscripts"].replace("{{baseurl}}", prefixnamespace))
        with open(outpath + "epsgdefs.js", 'w', encoding='utf-8') as f:
            f.write(templates["epsgdefs"])
        paths = defaultdict(list)
        nonnsmap = {}
        postprocessing = Graph()
        subtorencounter = 0
        start=time.time()
        for subj in subjectstorender:
            path=DocUtils.replaceColonFromWinPath(subj.replace(prefixnamespace, ""))
            # try:
            paths = DocUtils.processSubjectPath(outpath, paths, path, self.graph)
            #if os.path.exists(outpath + path + "/index.ttl"):
            #    try:
            #        self.graph.parse(outpath + path + "/index.ttl")
            #    except Exception as e:
            #        print(e)
            #        print(traceback.format_exc())
            res = self.htmlexporter.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace,
                                  self.graph.subject_predicates(subj),
                                  self.graph, f'{self.pubconfig["corpusid"]}_search.js', f'{self.pubconfig["corpusid"]}_classtree.js',
                                  uritotreeitem, curlicense, subjectstorender, postprocessing, nonnsmap)
            postprocessing,nonnsmap = res
            subtorencounter += 1
            if subtorencounter % 250 == 0:
                subtorenderlen = len(subjectstorender) + len(postprocessing)
                DocUtils.updateProgressBar(subtorencounter, subtorenderlen, "Processing Subject URIs")
            # except Exception as e:
            #    print("Create HTML Exception: "+str(e))
            #    print(traceback.format_exc())
        end=time.time()
        self.exectimes["HTML Generation"]={"time":end-start,"items":len(subjectstorender)}
        print(f"HTML generation time for {len(subjectstorender)} pages: {end-start} seconds, about {(end-start)/len(subjectstorender)} seconds per page")
        print("Postprocessing " + str(len(postprocessing)))
        subtorenderlen = len(subjectstorender) + len(postprocessing)
        for subj in postprocessing.subjects(None, None, True):
            path = str(subj).replace(prefixnamespace, "")
            paths = DocUtils.processSubjectPath(outpath, paths, path, self.graph)
            #if os.path.exists(outpath + path + "/index.ttl"):
            #    try:
            #        self.graph.parse(outpath + path + "/index.ttl")
            #    except Exception as e:
            #        print(e)
            #        print(traceback.format_exc())
            self.htmlexporter.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace,
                            self.graph.subject_predicates(subj),
                            self.graph, f'{self.pubconfig["corpusid"]}_search.js', f'{self.pubconfig["corpusid"]}_classtree.js', uritotreeitem,
                            curlicense, subjectstorender, postprocessing)
            subtorencounter += 1
            if subtorencounter % 250 == 0:
                DocUtils.updateProgressBar(subtorencounter, subtorenderlen, "Processing Subject URIs")
        start=time.time()
        ClassTreeUtils.checkGeoInstanceAssignment(uritotreeitem)
        classlist = ClassTreeUtils.assignGeoClassesToTree(tree)
        end=time.time()
        self.exectimes["Finalize Classtree"]={"time":end-start}
        print(f"Finalizing class tree done in {end-start} seconds")
        if self.pubconfig["nonnspages"]:
            start = time.time()
            labeltouri = self.getSubjectPagesForNonGraphURIs(nonnsmap, self.graph, prefixnamespace, self.pubconfig["corpusid"], outpath,
                                                             self.licensehtml, prefixnamespace, uritotreeitem, labeltouri)
            end=time.time()
            self.exectimes["NonNS Pages"] = {"time": end - start,"items":len(nonnsmap)}
            print(f"NonNS Page Generation time {end-start} seconds")
        with open(classtreepath, 'w', encoding='utf-8') as f:
            f.write("var tree=")
            json.dump(tree,f, indent=2)
        with open(searchjspath, 'w', encoding='utf-8') as f:
            f.write("var search=")
            json.dump(labeltouri,f, indent=2, sort_keys=True)
        if self.htmlexporter.has3d:
            if not os.path.exists(outpath + "/js"):
                os.makedirs(outpath + "/js")
            with open(outpath + "/js/corto.em.js", 'w', encoding='utf-8') as f:
                f.write(templates["corto.em"])
            with open(outpath + "/js/nexus.js", 'w', encoding='utf-8') as f:
                f.write(templates["nexus"])
        if self.pubconfig["apis"]["iiif"]:
            IIIFAPIExporter.generateIIIFAnnotations(outpath, self.htmlexporter.imagetoURI)
        if self.pubconfig["createIndexPages"]:
            start = time.time()
            IndexViewPage.createIndexPages(self.pubconfig,templates,self.pubconfig["apis"],paths,subjectstorender,uritotreeitem,voidds,tree,classlist,self.graph,self.voidstatshtml,curlicense)
            end=time.time()
            print(f"Index Page Creation time: {end-start} seconds")
            self.exectimes["Index Page Creation"] = {"time": end - start}
        if "layouts" in templates:
            for template in templates["layouts"]:
                if template!="main":
                    templates["layouts"][template]=TemplateUtils.resolveIncludes(template,templates)
        if "sparqltemplate" in templates:
            with open(outpath + "sparql.html", 'w', encoding='utf-8') as f:
                SPARQLPage().generatePageView(templates, self.pubconfig, curlicense, self.voidstatshtml,self.graph, f)
        relpath = DocUtils.generateRelativePathFromGivenDepth(0)
        if len(self.htmlexporter.iiifmanifestpaths["default"]) > 0:
            start=time.time()
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
            end=time.time()
            print(f"IIIF Collection Generation time: {end-start} seconds")
            self.exectimes["IIIF Collection Generation"] = {"time": end - start}
        if len(self.htmlexporter.featurecollectionspaths) > 0 and self.pubconfig["apis"]["ckan"]:
            start=time.time()
            CKANExporter.generateCKANCollection(outpath, self.pubconfig["deploypath"], self.htmlexporter.featurecollectionspaths, tree["core"]["data"],
                                                self.pubconfig["license"])
            end=time.time()
            print(f"CKAN API Generation time: {end-start} seconds")
            self.exectimes["CKAN API Generation"] = {"time": end - start}
        if self.pubconfig["apis"]["solidexport"]:
            start=time.time()
            SolidExporter.createSolidSettings(self.graph, outpath, self.pubconfig["deploypath"], self.pubconfig["publisher"], self.pubconfig["datasettitle"],
                                              tree["core"]["data"])
            end=time.time()
            print(f"Solid API Generation time: {end-start} seconds")
            self.exectimes["Solid API Generation"] = {"time": end - start}
        if len(self.htmlexporter.featurecollectionspaths) > 0:
            start=time.time()
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
            WFSExporter.generateWFSPages(outpath,self.pubconfig["deploypath"], self.htmlexporter.featurecollectionspaths,self.licenseuri)
            with open(outpath + "featurecollections.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.write("<p>This page shows feature collections present in the linked open data export</p><script src=\"features.js\"></script>")
                f.write(templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace(
                    "var featurecolls = {{myfeature}}", "").replace("{{relativepath}}",
                                                                    DocUtils.generateRelativePathFromGivenDepth(0)).replace(
                    "{{baselayers}}",
                    json.dumps(DocConfig.baselayers).replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{dateatt}}", "")))
                tempfoot = DocUtils.replaceStandardVariables(templates["footer"], "", "0", "true",self.pubconfig).replace("{{license}}",
                                                                                                         curlicense).replace(
                    "{{subject}}", "").replace("{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "").replace(
                    "{{stats}}", self.voidstatshtml)
                tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, self.pubconfig["apis"]["ogcapifeatures"], self.pubconfig["apis"]["iiif"], self.pubconfig["apis"]["ckan"]],
                                                            [
                                                                f'<a href=\"sparql.html?endpoint={self.pubconfig["deploypath"]}">[SPARQL]</a>&nbsp;',
                                                                "<a href=\"api/api.html\">[OGC API Features]</a>&nbsp;",
                                                                "<a href=\"iiif/\">[IIIF]</a>&nbsp;",
                                                                "<a href=\"api/3/\">[CKAN]</a>"
                                                            ], "{{apis}}")
                f.write(tempfoot)
            end=time.time()
            print(f"OGC API Features Generation time: {end-start} seconds")
            self.exectimes["OGC API Features Generation"] = {"time": end - start}
        return subjectstorender


    def getSubjectPagesForNonGraphURIs(self, uristorender, graph, prefixnamespace, corpusid, outpath, curlicense, baseurl,
                                       uritotreeitem, labeltouri):
        nonnsuris = len(uristorender)
        counter = 0
        # print("NONS URIS TO RENDER: "+str(uristorender))
        for uri in uristorender:
            theuri=URIRef(uri)
            label = ""
            if prefixnamespace not in uri:
                # print("URI: " + str(uri))
                for tup in graph.predicate_objects(theuri):
                    if str(tup[0]) in DocConfig.labelproperties:
                        label = str(tup[1])
                        break
                suri = DocUtils.shortenURI(uri)
                if uri in uritotreeitem:
                    res = DocUtils.replaceNameSpacesInLabel(self.pubconfig["prefixes"], uri)
                    label = DocUtils.getLabelForObject(URIRef(str(uri)), graph, None, self.pubconfig["labellang"])
                    if res is not None and label != "":
                        uritotreeitem[uri][-1]["text"] = f'{label} ({res["uri"]})'
                    elif label != "":
                        uritotreeitem[uri][-1]["text"] = f'{label} ({suri})'
                    else:
                        uritotreeitem[uri][-1]["text"] = suri
                    uritotreeitem[uri][-1]["id"] = f'{prefixnamespace}nonns_{suri}.html'
                    labeltouri[label] = f'{prefixnamespace}nonns_{suri}.html'
                if counter % 10 == 0:
                    DocUtils.updateProgressBar(counter, nonnsuris, "NonNS URIs")
                self.htmlexporter.createHTML(f'{outpath}nonns_{suri}.html', None, theuri, baseurl,
                                graph.subject_predicates(theuri, True), graph, f"{corpusid}_search.js",
                                f"{corpusid}_classtree.js", None, curlicense, None, Graph(), uristorender, True,
                                label)
                counter += 1
        return labeltouri

    def polygonToPath(self, svg):
        svg = svg.replace("<polygon", "<path").replace("points=\"", "d=\"M").replace("\"></polygon>", " Z\"></polygon>")
        return svg.replace("<svg>","<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">")

def main():
    prefixes = {"reversed": {}}
    rpath=resourcepath + '/prefixes.json'
    print(f'PREFIX EXISTS? {rpath} {os.path.exists(resourcepath)}/prefixes.json')
    if os.path.exists(rpath):
        with open(rpath, encoding="utf-8") as f:
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
    parser.add_argument("-cc", "--createCollections", help="create collections?", default=True,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))
    parser.add_argument("-ccls", "--collectionClass", help="collection class?", action="store",default="http://www.w3.org/2004/02/skos/core#Collection")
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
    parser.add_argument("-ckan", "--ckanapi", help="create static ckan api docs?", action="store", default=False,
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
    if args.input is None or args.input[0] == "None" or args.input == "":
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
            outpath+=[itemm for itemm in path.split(" ")]
            #for itemm in path.split(" "):
            #    outpath.append(itemm)
        else:
            outpath.append(path)

    print("ARG EXPORTS: " + str(args.exports))
    for expo in args.exports:
        if " " in expo:
            dataexports+=[ex for ex in expo.split(" ") if ex not in dataexports]
            #for ex in expo.split(" "):
            #    if ex not in dataexports:
            #        dataexports.append(ex)
        elif expo not in dataexports:
            dataexports.append(expo)
    print("EXPORTS: "+str(dataexports))
    print(os.listdir(os.getcwd()))
    if args.templatepath is not None:
        templatepath=args.templatepath
        if templatepath.startswith("http") and templatepath.endswith(".zip"):
            with urlopen(templatepath) as zipresp:
                with ZipFile(BytesIO(zipresp.read())) as zfile:
                    subfoldername = zfile.namelist()[0][0:zfile.namelist()[0].rfind('/')]
                    zfile.extractall(resourcepath+'/html/')
                    templatepath = f'{resourcepath}/html/{subfoldername}'
                    if subfoldername.endswith("/"):
                        subfoldername = subfoldername[0:-1]
                    templatepath = f'{resourcepath}/html/{subfoldername[0:subfoldername.rfind("/") + 1]}'
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
                print(f"Detected {args.prefixns} as data namespace")
            apis={"iiif":args.iiifmanifest,"ogcapifeatures":args.ogcapifeatures,"ckan":args.ckanapi,"solidexport":args.solidexport,"stac":args.stacapi}
            #print("Args: "+str(vars(args)))
            if fcounter < len(outpath):
                docgen = OntDocGeneration(prefixes, modtime, outpath[fcounter],apis, g, vars(args),dataexports)
                curpath=outpath[fcounter]
            else:
                docgen = OntDocGeneration(prefixes, modtime, outpath[-1],apis, g, vars(args),dataexports)
                curpath=outpath[-1]
            subrend = docgen.generateOntDocForNameSpace(args.prefixns, dataformat="HTML")
            DocUtils.printExecutionStats(docgen.exectimes)
            DocUtils.writeExecutionStats(docgen.exectimes,curpath+"/buildlog.txt")
        except Exception as inst:
            print("Could not parse " + str(fp))
            print(inst)
            print(traceback.format_exc())
        fcounter += 1
    curlicense = license
    if docgen is not None:
        curlicense = docgen.licensehtml
    print(f'Path exists? {outpath[0]}/index.html {os.path.exists(outpath[0] + "/index.html")}')
    if not os.path.exists(outpath[0] + '/index.ttl') and subrend is not None:
        resg = Graph()
        for sub in subrend:
            for predobj in g.predicate_objects(sub):
                resg.add((sub, predobj[0], predobj[1]))
            if args.solidexport:
                resg.add((sub, RDF.type,
                          URIRef("http://www.w3.org/ns/ldp#Container")))
                resg.add((sub, RDF.type,
                          URIRef("http://www.w3.org/ns/ldp#BasicContainer")))
                resg.add((sub, RDF.type,
                          URIRef("http://www.w3.org/ns/ldp#Resource")))
        resg.serialize(outpath[0] + '/index.ttl')
    manifest={
        "lang": "en-us",
        "name": "SPARQLing Unicorn Ontology Documentation Script: "+args.prefixnsshort,
        "short_name": args.prefixnsshort,
        "description": "HTML Deployment produced by the SPARQLing Unicorn Ontology Documentation Script",
        "start_url": "/",
        "background_color": "#2f3d58",
        "theme_color": "#2f3d58",
        "orientation": "any",
        "display": "standalone"
    }
    with open(outpath[0] + "/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest,f)
    if not os.path.exists(outpath[0] + '/index.html'):
        with open(outpath[0] + "/index.html", "w", encoding="utf-8") as indexf:
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
            indexf.write(indexhtml)
            indexf.write("<p>This page shows information about linked data resources in HTML. Choose the classtree navigation or search to browse the data</p>")
            indexf.write("<table class=\"description\" border=1 id=indextable><thead><tr><th>Dataset</th></tr></thead><tbody>")
            subfolders = [f.path for f in os.scandir(outpath[0]) if f.is_dir()]
            #print(subfolders)
            indexf.write("".join(f'<tr><td><a href="{path.replace(outpath[0] + "/", "")}/index.html">{path.replace(outpath[0] + "/", "")}</a></td></tr>' for path in subfolders))
            #for path in subfolders:
            #    indexf.write(f'<tr><td><a href="{path.replace(outpath[0] + "/", "")}/index.html">{path.replace(outpath[0] + "/", "")}</a></td></tr>')
            indexf.write("</tbody></table><script>$('#indextable').DataTable();</script>")
            indexf.write(DocUtils.replaceStandardVariables(templates["footer"], "", "0", "true",docgen.pubconfig).replace("{{license}}", curlicense).replace("{{exports}}",
                                                                                        templates["nongeoexports"]).replace(
                "{{bibtex}}", "").replace("{{stats}}", ""))
            # print(indexhtml)
            indexf.write(indexhtml)


if __name__ == "__main__":
    main()