
import os
import json
from pathlib import Path

from doc.docutils import DocUtils


class CKANExporter:

    @staticmethod
    def generateCKANCollection(outpath, deploypath, featurecollectionspaths,classtree,license="",version="3"):
        if not os.path.exists(outpath + "/dataset/"):
            os.makedirs(outpath + "/dataset/")
        if not os.path.exists(outpath + "/api/"):
            os.makedirs(outpath + "/api/")
        if not os.path.exists(outpath + "/api/action"):
            os.makedirs(outpath + "/api/action")
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
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/group_list?all_fields=true"):
            p = Path(outpath + "/api/"+str(version)+"/action/group_list?all_fields=true")
            p.symlink_to("./group_list/")
        if not os.path.exists(outpath + "/api/action/package_search/"):
            p = Path(outpath + "/api/action/package_search/")
            p.symlink_to("../"+str(version)+"/action/package_list/")
        if not os.path.exists(outpath + "/api/action/group_list/"):
            p = Path(outpath + "/api/action/group_list/")
            p.symlink_to("../"+str(version)+"/action/group_list/")
        if not os.path.exists(outpath + "/api/action/package_list/"):
            p = Path(outpath + "/api/action/package_list/")
            p.symlink_to("../"+str(version)+"/action/package_list/")
        if not os.path.exists(outpath + "/api/action/tag_list/"):
            p = Path(outpath + "/api/action/tag_list/")
            p.symlink_to("../"+str(version)+"/action/tag_list/")
        f = open(outpath + "/api/"+str(version)+"/index.json", "w")
        f.write(json.dumps({"version": int(version)}))
        f.close()
        f = open(outpath + "/api/"+str(version)+"/action/group_list/index.json", "w")
        if classtree!=None and len(classtree)>0:
            classes=[]
            for item in classtree:
                if item["type"]=="class" or item["type"]=="geoclass":
                    theid=DocUtils.shortenURI(item["id"])
                    classes.append({"description":theid,"display_name":item["text"],"name":item["text"],"title":item["text"],"type":"group"})
                    if not os.path.exists(outpath + "/api/"+str(version)+"/action/group_show?id="+theid):
                        os.makedirs(outpath + "/api/"+str(version)+"/action/group_show?id="+theid)
                    groupdesc={"success":True,"result":{"description":theid,"display_name":item["text"],"name":item["text"],"title":item["text"],"type":"group"}}
                    with open(outpath + "/api/"+str(version)+"/action/group_show?id="+theid+"/index.json", 'w') as fl:
                        fl.write(json.dumps(groupdesc))
            f.write(json.dumps({"success": True, "result": classes}))
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
            dataset={"success":True,"type":"dataset","title":curcollname,"result":{"id":curcollname,"num_resources":3,"license_id":license,"license_title":license,"name":curcollname,"notes":"","tags":[],"groups":[],"resources":[{"name":curcollname+" (text/ttl)","format":"TTL","package_id":curcollname,"mimetype":"text/ttl","resource_type":"file","url":deploypath+"/dataset/"+curcollname+".ttl","state":"active","url_type":""},{"name":curcollname+" (application/json)","format":"JSON","package_id":curcollname,"mimetype":"application/json","resource_type":"file","url":deploypath+"/dataset/"+curcollname+".json","state":"active","url_type":""},{"name":curcollname+" (text/html)","format":"HTML","package_id":curcollname,"mimetype":"text/html","resource_type":"file","url":deploypath+"/dataset/"+curcollname+".html","state":"active","url_type":""}]}}
            f = open(outpath + "/dataset/"+curcollname+"_", "w")
            f.write(json.dumps(dataset))
            f.close()
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
            colls.append(dataset)
        f = open(outpath + "/api/"+str(version)+"/action/package_list/index.json", "w")
        f.write(json.dumps({"success": True, "count": len(colls), "results":colls}))
        f.close()
