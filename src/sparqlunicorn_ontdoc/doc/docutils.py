from rdflib import URIRef, Literal
import os
import json
import shapely
import traceback

from doc.docconfig import DocConfig


class DocUtils:

    @staticmethod
    def zero_div(x,y):
        return y and x/y or 0

    @staticmethod
    def getLDFilesFromFolder(folder):
        directory = os.fsencode(folder)
        files=[]
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".ttl") or filename.endswith(".owl") or filename.endswith(".ttl") or filename.endswith(
                    "n3") or filename.endswith(".nt"):
                files.append(filename)
        return files

    @staticmethod
    def getDataNamespace(g):
        print("Automatic data namespace detection")
        namespacetosub = {}
        for sub in g.subjects(None, None, True):
            ns = DocUtils.instanceToNS(sub)
            if ns not in namespacetosub:
                namespacetosub[ns] = set()
            namespacetosub[ns].add(sub)
        maxns=None
        maxnsnum=-1
        for ns in namespacetosub:
            if len(namespacetosub[ns])>maxnsnum:
                maxnsnum=len(namespacetosub[ns])
                maxns=ns
        print("Automatically detected datanamespace "+str(maxns))
        return maxns

    @staticmethod
    def resolveWildcardPath(thepath):
        result = []
        if "/*" not in thepath:
            result.append(thepath)
            return result
        print(thepath)
        normpath = thepath.replace("*", "")
        if os.path.exists(normpath):
            files = os.listdir(normpath)
            for file in files:
                print(file)
                if file.endswith(".ttl") or file.endswith(".owl") or file.endswith(".ttl") or file.endswith(
                        "n3") or file.endswith(".nt"):
                    result.append(normpath + file)
        return result


    @staticmethod
    def instanceToNS(uri):
        if not uri.startswith("http"):
            return uri
        if "#" in uri:
            return uri[:uri.rfind("#") + 1]
        if "/" in uri:
            return uri[:uri.rfind("/") + 1]
        return uri


    @staticmethod
    def checkDepthFromPath(savepath,baseurl,subject):
        if savepath.endswith("/"):
            checkdepth = subject.replace(baseurl, "").count("/")
        else:
            checkdepth = subject.replace(baseurl, "").count("/")
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth), "OntdocGeneration", Qgis.Info)
        checkdepth+=1
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth))
        return checkdepth

    @staticmethod
    def shortenURI(uri,ns=False):
        if uri!=None and "#" in uri and ns:
            return uri[0:uri.rfind('#')+1]
        if uri!=None and "/" in uri and ns:
            return uri[0:uri.rfind('/')+1]
        if uri!=None and uri.endswith("/"):
            uri = uri[0:-1]
        if uri!=None and "#" in uri and not ns:
            return uri[uri.rfind('#')+1:]
        if uri!=None and "/" in uri and not ns:
            return uri[uri.rfind('/')+1:]
        return uri

    @staticmethod
    def createURILink(prefixes,uri):
        res = DocUtils.replaceNameSpacesInLabel(prefixes,uri)
        if res != None:
            return " <a href=\"" + str(uri) + "\" target=\"_blank\">" + str(res["uri"]) + "</a>"
        else:
            return " <a href=\"" + str(uri) + "\" target=\"_blank\">" + DocUtils.shortenURI(uri) + "</a>"

    @staticmethod
    def generateRelativeLinkFromGivenDepth(baseurl,checkdepth,item,withindex):
        rellink = str(item).replace(baseurl, "")
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        if withindex:
            rellink += "/index.html"
        #QgsMessageLog.logMessage("Relative Link from Given Depth: " + rellink,"OntdocGeneration", Qgis.Info)
        return rellink

    @staticmethod
    def checkImgMetadataRDF(g,uri):
        res={}
        for obj in g.objects(URIRef(uri),URIRef("http://www.w3.org/2003/12/exif/ns#width")):
            res["width"]=str(obj)
        for obj in g.objects(URIRef(uri),URIRef("http://www.w3.org/2003/12/exif/ns#height")):
            res["height"]=str(obj)
        return res

    @staticmethod
    def generateRelativeSymlink(linkpath, targetpath, outpath, items=False):
        if "nonns" in targetpath and targetpath.count("/")<3:
            checkdepthtarget= 1
        elif "nonns" in targetpath and not items:
            checkdepthtarget = 3
        elif "nonns" in targetpath and items:
            checkdepthtarget = 4
        else:
            checkdepthtarget = targetpath.count("/") - 1
        #print("Checkdepthtarget: " + str(checkdepthtarget))
        targetrellink = DocUtils.generateRelativeLinkFromGivenDepth(targetpath, checkdepthtarget, linkpath, False)
        #print("Target Rellink: " + str(targetrellink))
        #print("Linkpath: " + str(linkpath))
        targetrellink = targetrellink.replace(outpath, "")
        return targetrellink.replace("//", "/")

    @staticmethod
    def getLabelForObject(obj,graph,prefixes=None,labellang=None):
        label=""
        onelabel=DocUtils.shortenURI(str(obj))
        for tup in graph.predicate_objects(obj):
            if str(tup[0]) in DocConfig.labelproperties:
                # Check for label property
                if tup[1].language==labellang:
                    label=str(tup[1])
                onelabel=str(tup[1])
        if label=="" and onelabel!=None and onelabel!="":
            if prefixes!=None:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, str(obj))
                label=res["uri"]
            else:
                label = onelabel
        elif label=="" and (onelabel==None or onelabel=="") and prefixes!=None:
            res = DocUtils.replaceNameSpacesInLabel(prefixes, str(obj))
            if res!=None:
                label=res["uri"]
        return label

    @staticmethod
    def processSubjectPath(outpath,paths,path,graph):
        if "/" in path:
            addpath = ""
            try:
                for pathelem in path.split("/"):
                    addpath += pathelem + "/"
                    if not os.path.exists(outpath + addpath):
                        os.mkdir(outpath + addpath)
                if outpath + path[0:path.rfind('/')] + "/" not in paths:
                    paths[outpath + path[0:path.rfind('/')] + "/"] = []
                paths[outpath + path[0:path.rfind('/')] + "/"].append(addpath[0:addpath.rfind('/')])
            except Exception as e:
                print(e)
        else:
            try:
                if not os.path.exists(outpath + path):
                    os.mkdir(outpath + path)
                if outpath not in paths:
                    paths[outpath] = []
                paths[outpath].append(path + "/index.html")
            except Exception as e:
                print(e)
        if os.path.exists(outpath + path + "/index.ttl"):
            try:
                graph.parse(outpath + path + "/index.ttl")
            except Exception as e:
                print(e)
        return paths

    @staticmethod
    def replaceNameSpacesInLabel(prefixes,uri):
        nsuri=DocUtils.shortenURI(uri,True)
        if nsuri in prefixes["reversed"]:
            if nsuri==uri and nsuri in prefixes["nstolabel"]:
                return {"uri": prefixes["nstolabel"][nsuri]+" ("+str(prefixes["reversed"][nsuri])+":)",
                        "ns": prefixes["reversed"][nsuri]}
            else:
                return {"uri": str(prefixes["reversed"][nsuri]) + ":" + str(uri.replace(nsuri, "")),
                    "ns": prefixes["reversed"][nsuri]}
        return {"uri": DocUtils.shortenURI(uri),"ns": ""}

    @staticmethod
    def generateRelativePathFromGivenDepth(checkdepth):
        rellink = ""
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        return rellink

    @staticmethod
    def resolveOWLImports(graph):
        for obj in graph.objects(None,"http://www.w3.org/2002/07/owl#imports"):
            try:
                graph.parse(str(obj))
            except Exception as e:
                print(e)
        return graph
