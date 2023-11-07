
import os
import json
from pathlib import Path

from doc.docutils import DocUtils


class CKANExporter:

    @staticmethod
    def generateCKANCollection(outpath, featurecollectionspaths,classtree,version="3"):
        if not os.path.exists(outpath + "/dataset/"):
            os.makedirs(outpath + "/dataset/")
        if not os.path.exists(outpath + "/api/"):
            os.makedirs(outpath + "/api/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/"):
            os.makedirs(outpath + "/api/"+str(version)+"/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/"):
            os.makedirs(outpath + "/api/"+str(version)+"/action/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/group_list/"):
            os.makedirs(outpath + "/api/"+str(version)+"/action/group_list/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/package_list/"):
            os.makedirs(outpath + "/api/"+str(version)+"/action/package_list/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/tag_list/"):
            os.makedirs(outpath + "/api/"+str(version)+"/action/tag_list/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/package_search"):
            p = Path(str(outpath + "/api/"+str(version)+"/action/package_search"))
            p.symlink_to("./package_list/")
        f = open(outpath + "/api/"+str(version)+"/index.json", "w")
        f.write(json.dumps({"version": int(version)}))
        f.close()
        f = open(outpath + "/api/"+str(version)+"/action/group_list/index.json", "w")
        if classtree!=None and len(classtree)>0:
            classes=set()
            for item in classtree:
                if item["type"]=="class" or item["type"]=="geoclass":
                    classes.add(DocUtils.shortenURI(item["type"]))
            f.write(json.dumps({"success": True, "result": list(classes)}))
        else:
            f.write(json.dumps({"success": True, "result": []}))
        f.close()
        f = open(outpath + "/api/"+str(version)+"/action/tag_list/index.json", "w")
        f.write(json.dumps({"success": True, "result": ["ttl", "json", "geojson", "html"]}))
        f.close()
        colls = []
        for coll in featurecollectionspaths:
            op = outpath + "/dataset/" + coll.replace(outpath, "").replace("index.geojson", "")
            op = op.replace(".geojson", "")
            op = op.replace("//", "/")
            curcollname=coll.replace(outpath, "").replace("index.geojson", "")
            if curcollname.endswith("/"):
                curcollname=curcollname[0:-1]
            curcollname=curcollname.replace(".geojson","")
            if op.endswith("/"):
                op = op[0:-1]
            if not os.path.exists(op):
                os.makedirs(op)
            if not os.path.exists(str(op + ".json").replace("//", "/")):
                targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"), str(op + ".json"),
                                                          outpath)
                p = Path(str(op + ".json").replace("//", "/"))
                p.symlink_to(targetpath)
                p = Path(outpath + "/api/"+str(version)+"/action/package_show?id="+str(curcollname)+".json")
                p.symlink_to("../../"+targetpath)
            if not os.path.exists(str(op + ".ttl").replace("//", "/")):
                targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"), str(op + ".ttl"),
                                                          outpath)
                p = Path(str(op + ".ttl").replace("//", "/"))
                p.symlink_to(targetpath)
                p = Path(outpath + "/api/"+str(version)+"/action/package_show?id="+str(curcollname)+".ttl")
                p.symlink_to("../../"+targetpath)
            if not os.path.exists(str(op + ".html").replace("//", "/")):
                targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"), str(op + ".html"),
                                                          outpath)
                p = Path(str(op + ".html").replace("//", "/"))
                p.symlink_to(targetpath)
                p = Path(outpath + "/api/"+str(version)+"/action/package_show?id="+str(curcollname)+".html")
                p.symlink_to("../../"+targetpath)
            colls.append(op[op.rfind('/') + 1:])
        f = open(outpath + "/api/"+str(version)+"/action/package_list/index.json", "w")
        f.write(json.dumps({"success": True, "result":{ "count": len(colls), "results":colls}}))
        f.close()
