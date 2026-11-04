
import os
from doc import orjsonutils as json
from pathlib import Path

from doc.docutils import DocUtils


class CKANExporter:


    @staticmethod
    def generateCKANCollection(outpath, deploypath, featurecollectionspaths,classtree,license="",version="3"):
        ckanapihtml = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><metaname="description" content="SwaggerUI"/><title>SwaggerUI</title><link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" /></head><body><div id="swagger-ui"></div><script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js" crossorigin></script><script>const swaggerUrl = "{deploypath}/api/3/api.json"; const apiUrl = "{deploypath}/";  window.onload = () => {{let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {{j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({{spec: j,dom_id: '#swagger-ui'}});}}));}};</script></body></html>"""
        os.makedirs(f"{outpath}/dataset/", exist_ok=True)
        os.makedirs(f"{outpath}/api/", exist_ok=True)
        os.makedirs(f"{outpath}/api/action", exist_ok=True)
        os.makedirs(f"{outpath}/api/{version}/", exist_ok=True)
        os.makedirs(f"{outpath}/api/{version}/action/", exist_ok=True)
        os.makedirs(f"{outpath}/api/{version}/action/group_list/", exist_ok=True)
        os.makedirs(f"{outpath}/api/{version}/action/package_list/", exist_ok=True)
        os.makedirs(f"{outpath}/api/{version}/action/tag_list/", exist_ok=True)
        try:
            if not os.path.exists(f"{outpath}/api/{version}/action/package_search"):
                p = Path(f"{outpath}/api/{version}/action/package_search")
                p.symlink_to("./package_list/")
            if not os.path.exists(f"{outpath}/api/{version}/action/group_list?all_fields=true"):
                p = Path(f"{outpath}/api/{version}/action/group_list?all_fields=true")
                p.symlink_to("./group_list/")
            if not os.path.exists(f"{outpath}/api/action/package_search/"):
                p = Path(f"{outpath}/api/action/package_search/")
                p.symlink_to(f"../{version}/action/package_list/")
            if not os.path.exists(f"{outpath}/api/action/group_list/"):
                p = Path(f"{outpath}/api/action/group_list/")
                p.symlink_to(f"../{version}/action/group_list/")
            if not os.path.exists(f"{outpath}/api/action/package_list/"):
                p = Path(f"{outpath}/api/action/package_list/")
                p.symlink_to(f"../{version}/action/package_list/")
            if not os.path.exists(f"{outpath}/api/action/tag_list/"):
                p = Path(f"{outpath}/api/action/tag_list/")
                p.symlink_to(f"../{version}/action/tag_list/")
        except Exception as e:
            print(e)
            print("Symlink creation might not be allowed")
        with open(f"{outpath}/api/{version}/index.json", "w",encoding="utf-8") as f:
            json.dump({"version": int(version)},f)
        ckanopenapi = {"openapi": "3.0.1", "info": {"title": f"{deploypath} CKAN API", "version": str(version)},
                       "servers": [{"url": f"{deploypath}/api/3/"}], "paths": {
                f"/api/{version}/action/group_list/": {"get": {"tags": ["CKAN"],
                       "summary": "Retrieves the group list of this CKAN API",
                       "description": "Retrieves the group list of this CKAN API",
                       "operationId": "actionapi-group_list",
                       "parameters": [], "responses": {
                        "200": {"description": "Success",
                                    "content": {"text/plain": {"example": None}},
                                    "application/json": {"schema": {"example": None}, "example": None},
                                    "text/json": {"schema": {"example": None}, "example": None}}}}},
                f"/api/{version}/action/tag_list/":{"get": {"tags": ["CKAN"],
                        "summary": "Retrieves the tag list of this CKAN API",
                        "description": "Retrieves the tag list of this CKAN API",
                        "operationId": "actionapi-tag_list",
                        "parameters": [], "responses": {
                        "200": {"description": "Success",
                                "content": {"text/plain": {"example": None}},
                                "application/json": {"schema": {"example": None}, "example": None},
                                "text/json": {"schema": {"example": None}, "example": None}}}}},
                f"/api/{version}/action/package_list/": {"get": {"tags": ["CKAN"],
                       "summary": "Retrieves the package list of this CKAN API",
                       "description": "Retrieves the package list of this CKAN API",
                       "operationId": "actionapi-package_list",
                       "parameters": [], "responses": {
                        "200": {"description": "Success",
                                "content": {"text/plain": {"example": None}},
                                "application/json": {"schema": {"example": None}, "example": None},
                                "text/json": {"schema": {"example": None}, "example": None}}}}}
        }}
        with open(f"{outpath}/api/{version}/api.json", "w",encoding="utf-8") as f:
            json.dump(ckanopenapi,f)
        with open(f"{outpath}/api/{version}/index.html", "w",encoding="utf-8") as f:
            f.write(ckanapihtml)
        with open(f"{outpath}/api/{version}/action/group_list/index.json", "w",encoding="utf-8") as f:
            if classtree is not None and len(classtree)>0:
                classes=[]
                for item in classtree:
                    if item["type"]=="class" or item["type"]=="geoclass":
                        theid=DocUtils.shortenURI(item["id"])
                        classes.append({"description":theid,"display_name":item["text"],"name":item["text"],"title":item["text"],"type":"group"})
                        thepath=f"{outpath}/api/{version}/action/group_show?id={DocUtils.replaceColonFromWinPath(theid)}"
                        try:
                            os.makedirs(thepath, exist_ok=True)
                        except OSError:
                            thepath=thepath.replace("?","_")
                            os.makedirs(thepath, exist_ok=True)
                        groupdesc={"success":True,"result":{"description":theid,"display_name":item["text"],"name":item["text"],"title":item["text"],"type":"group"}}
                        with open(f"{thepath}/index.json", 'w') as fl:
                            json.dump(groupdesc,fl)
                json.dump({"success": True, "result": classes},f)
                #f.write(json.dumps({"success": True, "result": classes}))
            else:
                json.dump({"success": True, "result": []},f)
                #f.write(json.dumps({"success": True, "result": []}))
        with open(f"{outpath}/api/{version}/action/tag_list/index.json", "w",encoding="utf-8") as f:
            json.dump({"success": True, "result": ["ttl", "json", "geojson", "html"]},f)
        colls = []
        for coll in featurecollectionspaths:
            op = f'{outpath}/dataset/{DocUtils.replaceColonFromWinPath(coll).replace(outpath, "").replace("index.geojson", "")}'
            op = op.replace(".geojson", "")
            op = op.replace("//", "/")
            curcollname=coll.replace(outpath, "").replace("index.geojson", "")
            if curcollname.endswith("/"):
                curcollname=curcollname[0:-1]
            curcollname=curcollname.replace(".geojson","")
            if op.endswith("/"):
                op = op[0:-1]
            try:
                os.makedirs(op, exist_ok=True)
                dataset = {
                    "success": True,
                    "result": {
                        "id": curcollname, "type": "dataset", "num_resources": 3,
                        "title": curcollname, "license_id": license, "license_title": license,
                        "name": curcollname, "notes": "", "tags": [], "groups": [],
                        "resources": [
                            {"name": f"{curcollname} (text/ttl)", "format": "TTL", "id": curcollname,
                             "package_id": curcollname, "mimetype": "text/ttl", "resource_type": "file",
                             "url": f"{deploypath}/dataset/{curcollname}.ttl", "state": "active", "url_type": ""},
                            {"name": f"{curcollname} (application/json)", "id": curcollname, "format": "JSON",
                             "package_id": curcollname, "mimetype": "application/json", "resource_type": "file",
                             "url": f"{deploypath}/dataset/{curcollname}.json", "state": "active", "url_type": ""},
                            {"name": f"{curcollname} (text/html)", "id": curcollname, "format": "HTML",
                             "package_id": curcollname, "mimetype": "text/html", "resource_type": "file",
                             "url": f"{deploypath}/dataset/{curcollname}.html", "state": "active", "url_type": ""}
                        ]
                    }
                }
                with open(f"{outpath}/dataset/{curcollname}_", "w",encoding="utf-8") as f:
                    json.dump(dataset,f)
                cpath=f"{op}.json".replace("//", "/")
                if not os.path.exists(cpath):
                    targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"), f"{op}.json",outpath)
                    p = Path(cpath)
                    p.symlink_to(targetpath)
                    p = Path(f"{outpath}/api/{version}/action/package_show?id={curcollname}.json")
                    p.symlink_to(f"../../{targetpath}")
                cpath = f"{op}.ttl".replace("//", "/")
                if not os.path.exists(cpath):
                    targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"), f"{op}.ttl",
                                                              outpath)
                    p = Path(cpath)
                    p.symlink_to(targetpath)
                    p = Path(f"{outpath}/api/{version}/action/package_show?id={curcollname}.ttl")
                    p.symlink_to(f"../../{targetpath}")
                cpath = f"{op}.html".replace("//", "/")
                if not os.path.exists(cpath):
                    targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"), f"{op}.html",
                                                              outpath)
                    p = Path(cpath)
                    p.symlink_to(targetpath)
                    p = Path(f"{outpath}/api/{version}/action/package_show?id={curcollname}.html")
                    p.symlink_to(f"../../{targetpath}")
            except Exception as e:
                print(e)
                print("Symlink creation might not be allowed")
            colls.append(dataset["result"])
        with open(f"{outpath}/api/{version}/action/package_list/index.json", "w", encoding="utf-8") as f:
            json.dump({"success": True, "result":{"count": len(colls), "results":colls}},f)
