from rdflib import URIRef, Literal
import os
import re
import shutil
from doc import orjsonutils as json
import urllib.request

from collections import defaultdict
from doc.docconfig import DocConfig
from datetime import date


class DocUtils:

    @staticmethod
    def zero_div(x,y):
        return y and x/y or 0

    @staticmethod
    def updateProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█',printEnd="\r"):
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
        percent = f"{100 * (iteration / float(total)):.{decimals}f}"
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()

    @staticmethod
    def createFoldersFromList(flist):
        for fl in flist:
            os.makedirs(fl, exist_ok=True)

    @staticmethod
    def polygonToPath(svg):
        svg = svg.replace("<polygon", "<path").replace("points=\"", "d=\"M").replace("\"></polygon>", " Z\"></polygon>")
        return svg.replace("<svg>","<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">")

    @staticmethod
    def replaceStandardVariables(template, subject, checkdepth, indexpage,pubconfig):
        template = template.replace("{{indexpage}}", str(indexpage)).replace("{{subject}}", str(subject)).replace(
            "{{relativedepth}}", str(checkdepth)) \
            .replace("{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace(
            "{{deploypath}}", pubconfig["deploypath"]) \
            .replace("{{publishingorg}}", pubconfig["publishingorg"]).replace("{{publisher}}", pubconfig["publisher"]).replace(
            "{{datasettitle}}", pubconfig["datasettitle"]) \
            .replace("{{logo}}", pubconfig["logourl"])
        return template

    @staticmethod
    def replaceCitationLink(template, foundlabel, uri, pubconfig):
        return template.replace("{{citationlink}}",f'<details><summary>[CITE]</summary><pre>@misc{{{DocUtils.shortenURI(uri)}\nauthor={pubconfig["datasettitle"]} Contributors",\ntitle="{foundlabel}",\n"url="{uri}",\nnote="[Online; documentation generated at {date.today()}]"}}</pre></details>')

    @staticmethod
    def getLDFilesFromFolder(folder):
        directory = os.fsencode(folder)
        return [os.fsdecode(file) for file in os.listdir(directory) if str(file).endswith((".ttl",".owl",".n3",".nt"))]
        #for file in os.listdir(directory):
        #    filename = os.fsdecode(file)
        #    if filename.endswith((".ttl",".owl",".n3",".nt")):
        #        files.append(filename)
        #return files

    @staticmethod
    def getDataNamespace(g):
        print("Automatic data namespace detection")
        namespacecounts = defaultdict(int)
        maxns=None
        maxnsnum=-1
        for sub in g.subjects(None, None, True):
            ns=DocUtils.instanceToNS(sub)
            namespacecounts[ns] += 1
            if namespacecounts[ns] > maxnsnum:
                maxnsnum=namespacecounts[ns]
                maxns=ns
        print(f"Automatically detected datanamespace {maxns}")
        return maxns

    @staticmethod
    def resolveWildcardPath(thepath):
        result = []
        if "/*" not in thepath:
            result.append(thepath)
            return result
        #print(thepath)
        normpath = thepath.replace("*", "")
        if os.path.exists(normpath):
            files = os.listdir(normpath)
            result=[normpath + file for file in files if file.endswith((".ttl",".owl",".n3",".nt"))]
            #for file in files:
                #print(file)
            #    if file.endswith((".ttl",".owl",".n3",".nt")):
            #        result.append(normpath + file)
        return result


    @staticmethod
    def instanceToNS(uri):
        if not uri.startswith("http"):
            return uri
        separator = uri.rfind("#")
        if separator >= 0:
            return uri[:separator + 1]
        separator = uri.rfind("/")
        if separator >= 0:
            return uri[:separator + 1]
        return uri


    @staticmethod
    def checkDepthFromPath(savepath,baseurl,subject):
        return subject.replace(baseurl, "").count("/")+1
        """
        if savepath.endswith("/"):
            checkdepth = subject.replace(baseurl, "").count("/")
        else:
            checkdepth = subject.replace(baseurl, "").count("/")
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth), "OntdocGeneration", Qgis.Info)
        #checkdepth+=1
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth))
        return checkdepth+1
        """

    @staticmethod
    def printExecutionStats(timeexec):
        print(f"Selected Execution Statistics in order of execution:")
        totaltime=0
        for entry in timeexec:
            print(f"{entry}: {timeexec[entry]['time']} seconds", end='')
            totaltime+=timeexec[entry]['time']
            if "items" in timeexec[entry]:
                print(f" for {timeexec[entry]['items']} items, about {timeexec[entry]['time']/timeexec[entry]['items']} seconds per item", end='')
            print("\n",end="")
        print(f"Total measured execution time: {totaltime} seconds")

    @staticmethod
    def getExecutionStats(timeexec):
        res=f"\nSelected Execution Statistics in order of execution:\n"
        totaltime=0
        for entry in timeexec:
            res+=f"{entry}: {timeexec[entry]['time']} seconds\n"
            totaltime+=timeexec[entry]['time']
            if "items" in timeexec[entry]:
                res+=f" for {timeexec[entry]['items']} items, about {timeexec[entry]['time']/timeexec[entry]['items']} seconds per item\n"
            #print("\n",end="")
        return f"{res} Total measured execution time: {totaltime} seconds"

    @staticmethod
    def getExecutionStatsHTML(timeexec):
        res=f"<html><head></head><body><h3 align=center>Selected Execution Statistics in order of execution</h3><table border=1><thead><tr><th>Process</th><th>Time</th><th>Comment</th></tr></thead><tbody>"
        totaltime=0
        for entry in timeexec:
            res+=f"<tr><td><b>{entry}:</b></td><td>{timeexec[entry]['time']} seconds</td><td>"
            totaltime+=timeexec[entry]['time']
            if "items" in timeexec[entry]:
                res+=f" for <b>{timeexec[entry]['items']}</b> items, about <b>{timeexec[entry]['time']/timeexec[entry]['items']} seconds</b> per item\n"
            res+="</td></tr>"
            #print("\n",end="")
        return f"{res}<tr><td><b>Total measured execution time:</b></td><td>{totaltime} seconds</td></tr></tbody></table></body></html>"

    @staticmethod
    def writeExecutionStats(timeexec,filename="buildlog.json"):
        if filename.endswith(".json"):
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(timeexec,f)
        elif filename.endswith(".js"):
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"var buildlog={json.dumps(timeexec)}")
        elif filename.endswith(".csv"):
            with open(filename,"w",encoding="utf-8") as f:
                f.write(f"Task;ExecutionTime (seconds);Items Processed;TimePerItem (seconds);Comment\n")
                totaltime=0
                for entry in timeexec:
                    f.write(f"{entry};{timeexec[entry]['time']};")
                    totaltime+=timeexec[entry]['time']
                    if "items" in timeexec[entry]:
                        f.write(f"{timeexec[entry]['items']};{timeexec[entry]['time']/timeexec[entry]['items']};")
                    else:
                        f.write(";;")
                    f.write("\n")
                f.write(f"Total;{totaltime};;;")
        else:
            with open(filename,"w",encoding="utf-8") as f:
                f.write(f"Selected Execution Statistics in order of execution:\n")
                totaltime=0
                for entry in timeexec:
                    f.write(f"{entry}: {timeexec[entry]['time']} seconds")
                    totaltime+=timeexec[entry]['time']
                    if "items" in timeexec[entry]:
                        f.write(f" for {timeexec[entry]['items']} items, about {timeexec[entry]['time']/timeexec[entry]['items']} seconds per item")
                    f.write("\n")
                f.write(f"Total measured execution time: {totaltime} seconds")

    @staticmethod
    def shortenURI(uri,ns=False):
        if uri is None:
            return ""
        if ns:
            separator = uri.rfind("#")
            if separator >= 0:
                return uri[:separator + 1]
            separator = uri.rfind("/")
            if separator >= 0:
                return uri[:separator + 1]
            return uri
        if uri.endswith("/"):
            uri = uri[:-1]
        separator = uri.rfind("#")
        if separator >= 0:
            return uri[separator + 1:]
        separator = uri.rfind("/")
        if separator >= 0:
            return uri[separator + 1:]
        return uri

    @staticmethod
    def createURILink(prefixes,uri):
        res = DocUtils.replaceNameSpacesInLabel(prefixes,uri)
        return f" <a href=\"{uri}\" target=\"_blank\">{res['uri'] if res is not None else DocUtils.shortenURI(uri)}</a>"

    @staticmethod
    def generateRelativeLinkFromGivenDepth(baseurl,checkdepth,item,withindex):
        rellink = f'{"../" * checkdepth}{item}'.replace(baseurl, "")
        #for i in range(0, checkdepth):
        #    rellink = "../" + rellink
        if withindex:
            return f'{rellink}/index.html'
        #QgsMessageLog.logMessage("Relative Link from Given Depth: " + rellink,"OntdocGeneration", Qgis.Info)
        return rellink

    @staticmethod
    def resolveUnitValue(graph,obj,tuppredstr,tupobjstr,foundval,foundunit):
        #print("RESOLVE UNIT VALUE: "+str(obj))
        if tuppredstr == "http://www.w3.org/ns/oa#hasSource":
            foundval = tupobjstr
        elif tuppredstr == "http://www.w3.org/ns/oa#hasTarget":
            for selector in graph.objects(obj, DocConfig.OA_HAS_SELECTOR):
                for value_predicate, value in graph.predicate_objects(selector):
                    if value_predicate in DocConfig.UNIT_PREDICATES:
                        foundunit = str(value)
                    elif value_predicate in DocConfig.VALUE_PROPERTIES and (
                            isinstance(value, Literal) or isinstance(value, URIRef)):
                        foundval = str(value)
        elif tuppredstr is not None and DocConfig.valueproperties.get(tuppredstr) == "DatatypeProperty":
            if isinstance(obj, (Literal, URIRef)):
                foundval = tupobjstr
            # Keep datatype-property handling from falling through to linked-node lookup.
        else:
            for value_predicate, value in graph.predicate_objects(obj):
                if value_predicate in DocConfig.UNIT_PREDICATES:
                    foundunit = str(value)
                elif value_predicate in DocConfig.VALUE_PROPERTIES and isinstance(value, Literal):
                    foundval = str(value)
                elif value_predicate in DocConfig.STRICT_VALUE_PREDICATES and isinstance(value, URIRef):
                    for nested_predicate, nested_value in graph.predicate_objects(value):
                        if nested_predicate in DocConfig.UNIT_PREDICATES:
                            foundunit = str(nested_value)
                        elif nested_predicate in DocConfig.VALUE_PROPERTIES:
                            foundval=str(nested_value)
        return [foundval,foundunit]


    @staticmethod
    def checkImgMetadataRDF(g,uri):
        res={}
        image_uri = URIRef(uri)
        for obj in g.objects(image_uri, DocConfig.EXIF_WIDTH):
            res["width"]=str(obj)
        for obj in g.objects(image_uri, DocConfig.EXIF_HEIGHT):
            res["height"]=str(obj)
        return res

    @staticmethod
    def generateRelativeSymlink(linkpath, targetpath, outpath, items=False):
        if "nonns" in targetpath:
            if targetpath.count("/")<3:
                checkdepthtarget= 1
            elif not items:
                checkdepthtarget = 3
            elif items:
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
        onelabel=None
        for predicate, value in graph.predicate_objects(obj):
            if predicate in DocConfig.LABEL_PREDICATES:
                value_str = str(value)
                # Check for label property
                if value.language==labellang:
                    label=value_str
                onelabel=value_str
        if label=="":
            if onelabel is None:
                onelabel=DocUtils.shortenURI(str(obj))
            if onelabel is not None and onelabel!="":
                if prefixes is not None:
                    res = DocUtils.replaceNameSpacesInLabel(prefixes, str(obj))
                    label=res["uri"]
                else:
                    label = onelabel
            elif prefixes is not None:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, str(obj))
                label=res["uri"]
        return label

    @staticmethod
    def processSubjectPath(outpath,paths,path,graph):
        if "/" in path:
            addpath = ""
            #try:
            os.makedirs(outpath+path,exist_ok=True)
            #for pathelem in path.split("/"):
            #    addpath += pathelem + "/"
            #    if not os.path.exists(outpath + addpath):
            #        os.mkdir(outpath + addpath)
            ppath=path[0:path.rfind('/')]
            paths[f"{outpath}{ppath}/"].append(ppath)
            #if outpath + path[0:path.rfind('/')] + "/" not in paths:
            #    paths[outpath + path[0:path.rfind('/')] + "/"] = []
            #paths[outpath + path[0:path.rfind('/')] + "/"].append(addpath[0:addpath.rfind('/')])
            #except Exception as e:
            #    print(e)
        else:
            #try:
            os.makedirs(outpath+path,exist_ok=True)
            #if not os.path.exists(outpath + path):
            #    os.mkdir(outpath + path)
            paths[outpath].append(f"{path}/index.html")
            #if outpath not in paths:
            #    paths[outpath] = []
            #paths[outpath].append(path + "/index.html")
            #except Exception as e:
            #    print(e)
        if os.path.exists(f"{outpath}{path}/index.ttl"):
            try:
                graph.parse(f"{outpath}{path}/index.ttl")
            except Exception as e:
                print(e)
        return paths

    @staticmethod
    def replaceNameSpacesInLabel(prefixes,uri):
        nsuri=DocUtils.shortenURI(uri,True)
        if nsuri in prefixes["reversed"]:
            if nsuri==uri and nsuri in prefixes["nstolabel"]:
                return {"uri": f'{prefixes["nstolabel"][nsuri]} ({prefixes["reversed"][nsuri]}:)',"ns": prefixes["reversed"][nsuri]}
            else:
                return {"uri": f'{prefixes["reversed"][nsuri]}:{uri.replace(nsuri, "")}',"ns": prefixes["reversed"][nsuri]}
        return {"uri": DocUtils.shortenURI(uri),"ns": ""}

    @staticmethod
    def generateRelativePathFromGivenDepth(checkdepth):
        #rellink =
        #for i in range(0, checkdepth):
        #    rellink = "../" + rellink
        result="../"*checkdepth
        if result=="":
            return "."
        return result

    @staticmethod
    def createOfflineCompatibleVersion(outpath, myhtmltemplate, templatepath, templatename):
        os.makedirs(outpath, exist_ok=True)
        os.makedirs(f"{outpath}/js", exist_ok=True)
        os.makedirs(f"{outpath}/css", exist_ok=True)
        matched = re.findall(r'src="(http.*)"', myhtmltemplate)
        for match in matched:
            # download the library
            matchl = match[match.rfind("/") + 1:]
            if "</script>" in match:
                for m in match.split("></script><script src="):
                    m = m.replace("\"", "").replace("/>", "")
                    m = m.replace(">", "")
                    ml=m[m.rfind('/') + 1:]
                    try:
                        g = urllib.request.urlopen(m.replace("\"", ""))
                        with open(f'{outpath}{os.sep}js{os.sep}{ml}', 'b+w') as f:
                            f.write(g.read())
                    except Exception as e:
                        print(e)
                        thepath=f"{templatepath}/{templatename}/js/lib/{ml}"
                        if os.path.exists(thepath):
                            shutil.copy(thepath,f'{outpath}{os.sep}js{os.sep}{ml}')
                    myhtmltemplate = myhtmltemplate.replace(m, f"{{{{relativepath}}}}js/{ml}")
            else:
                match = match.replace("\"", "")
                try:
                    g = urllib.request.urlopen(match.replace("\"", ""))
                    with open(f'{outpath}{os.sep}js{os.sep}{matchl}', 'b+w') as f:
                        f.write(g.read())
                except Exception as e:
                    print(e)
                    thepath=f"{templatepath}/{templatename}/js/lib/{matchl}"
                    if os.path.exists(thepath):
                        shutil.copy(thepath,f'{outpath}{os.sep}js{os.sep}{matchl}')
                myhtmltemplate = myhtmltemplate.replace(match, f"{{{{relativepath}}}}js/{matchl}")
        matched = re.findall(r'href="(http.*.css)"', myhtmltemplate)
        for match in matched:
            #print(match.replace("\"", ""))
            match = match.replace("\"", "").replace("/>", "")
            match = match.replace(">", "")
            matchl=match[match.rfind("/") + 1:]
            try:
                g = urllib.request.urlopen(match.replace("\"", ""))
                with open(f'{outpath}{os.sep}css{os.sep}{matchl}', 'b+w') as f:
                    f.write(g.read())
            except Exception as e:
                thepath=f"{templatepath}/{templatename}/css/lib/{matchl}"
                if os.path.exists(thepath):
                    shutil.copy(thepath,f'{outpath}{os.sep}css{os.sep}{matchl}')
            myhtmltemplate = myhtmltemplate.replace(match, f"{{{{relativepath}}}}css/{matchl}")
        return myhtmltemplate

    @staticmethod
    def conditionalArrayReplace(string,conds,replace,what):
        #counter=0
        #result=""
        result="".join(replace[counter] for counter, cond in enumerate(conds) if cond)
        #for cond in conds:
        #    if cond:
        #        result+=replace[counter]
        #    counter+=1
        return string.replace(what,result)

    @staticmethod
    def conditionalReplace(string,cond,what,replace):
        if cond:
            return string.replace(what,replace)
        return string

    @staticmethod
    def resolveOWLImports(graph):
        for obj in graph.objects(None,"http://www.w3.org/2002/07/owl#imports"):
            try:
                graph.parse(str(obj))
            except Exception as e:
                print(e)
        return graph

    @staticmethod
    def replaceColonFromWinPath(thepath):
        if ":/" in thepath and re.search("^[A-Z]:[\/\\\\]",thepath) is not None:
            return thepath[0:2]+thepath[3:].replace(":","_")        
        else:
            return thepath.replace(":","_")