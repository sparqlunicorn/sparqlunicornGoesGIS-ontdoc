
import os
import json
from pathlib import Path

from doc.docutils import DocUtils


class OGCAPIFeaturesExporter:

    @staticmethod
    def generateOGCAPIFeaturesPages(outpath,deploypath, featurecollectionspaths, prefixnamespace, ogcapi, mergeJSON, contentnegotiation=False):
        apihtml = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><metaname="description" content="SwaggerUI"/><title>SwaggerUI</title><link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" /></head><body><div id="swagger-ui"></div><script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js" crossorigin></script><script>const swaggerUrl = "{deploypath}/api/index.json"; const apiUrl = "{deploypath}/";  window.onload = () => {{let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {{j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({{spec: j,dom_id: '#swagger-ui'}});}}));}};</script></body></html>"""
        collectionhtmlname,collectiontable,collectionsjson="indexc.html","",{}
        if contentnegotiation:
            collectionhtmlname="index.html"
        apijson = {"openapi": "3.0.1", "info": {"title": f"{deploypath} Feature Collections",
                                                "description": f"Feature Collections of {deploypath}","version":"1.0"},
                   "servers": [{"url": str(deploypath)}], "paths": {}}
        conformancejson = {"conformsTo": ["http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"]}
        if ogcapi:
            apijson["paths"]["/api"] = {
                "get": {"tags": ["Capabilities"], "summary": "api documentation", "description": "api documentation",
                        "operationId": "openApi", "parameters": [], "responses": {
                        "default": {"description": "default response","content": {"application/vnd.oai.openapi+json;version=3.0": {},
                                                "application/json": {}, "text/html": {"schema": {}}}}}}}
            apijson["paths"]["/license/dataset"] = {}
            apijson["components"] = {"schemas": {"Conformance": {"type": "object", "properties": {
                "conformsTo": {"type": "array", "items": {"type": "string"}}}, "xml": {"name": "ConformsTo","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Collection": {"type": "object", "properties": {
                                                     "id": {"type": "string", "xml": {"name": "Id","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "title": {"type": "string", "xml": {"name": "Title","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "description": {"type": "string", "xml": {"name": "Description","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "links": {"type": "array", "xml": {"name": "link","namespace": "http://www.w3.org/2005/Atom"},
                                                               "items": {"$ref": "#/components/schemas/Link"}},
                                                     "extent": {"$ref": "#/components/schemas/Extent"},
                                                     "itemType": {"type": "string"},
                                                     "crs": {"type": "array", "items": {"type": "string"}},
                                                     "storageCrs": {"type": "string"}}, "xml": {"name": "Collection",
                                                                                                "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Collections": {"type": "object", "properties": {
                                                     "links": {"type": "array", "xml": {"name": "link","namespace": "http://www.w3.org/2005/Atom"},
                                                               "items": {"$ref": "#/components/schemas/Link"}},
                                                     "collections": {"type": "array", "xml": {"name": "Collection",
                                                                                              "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"},
                                                                     "items": {
                                                                         "$ref": "#/components/schemas/Collection"}}},
                                                                 "xml": {"name": "Collections",
                                                                         "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Extent": {"type": "object", "properties": {
                                                     "spatial": {"$ref": "#/components/schemas/Spatial"},
                                                     "temporal": {"$ref": "#/components/schemas/Temporal"}},
                                                            "xml": {"name": "Extent",
                                                                    "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Link": {"type": "object", "properties": {
                                                     "href": {"type": "string", "xml": {"attribute": True}},
                                                     "rel": {"type": "string", "xml": {"attribute": True}},
                                                     "type": {"type": "string", "xml": {"attribute": True}},
                                                     "title": {"type": "string", "xml": {"attribute": True}}},
                                                          "xml": {"name": "link","namespace": "http://www.w3.org/2005/Atom"}},
                                                 "Spatial": {"type": "object", "properties": {"bbox": {"type": "array",
                                                                                                       "items": {
                                                                                                           "type": "array",
                                                                                                           "items": {
                                                                                                               "type": "number",
                                                                                                               "format": "double"}}},
                                                                                              "crs": {"type": "string",
                                                                                                      "xml": {"attribute": True}}},
                                                             "xml": {"name": "SpatialExtent","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Temporal": {"type": "object", "properties": {
                                                     "interval": {"type": "array","items": {"type": "string", "format": "date-time"}},
                                                     "trs": {"type": "string", "xml": {"attribute": True}}},
                                                              "xml": {"name": "TemporalExtent","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "LandingPage": {"type": "object"}}}
            landingpagejson = {"title": "Landing Page", "description": "Landing Page", "links": [{
                "href": f"{deploypath}/index.json",
                "rel": "self",
                "type": "application/json",
                "title": "this document as JSON"
            }, {
                "href": f"{deploypath}/index.html",
                "rel": "alternate",
                "type": "text/html",
                "title": "this document as HTML"
            }, {
                "href": f"{deploypath}/collections/",
                "rel": "data",
                "type": "application/json",
                "title": "Supported Feature Collections as JSON"
            }, {
                "href": f"{deploypath}/collections/{collectionhtmlname}",
                "rel": "data",
                "type": "text/html",
                "title": "Supported Feature Collections as HTML"
            }, {"href": f"{deploypath}/api/index.json", "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0", "title": "API definition"},
                {"href": f"{deploypath}/api", "rel": "service-desc", "type": "text/html",
                 "title": "API definition as HTML"},
                {"href": f"{deploypath}/conformance", "rel": "conformance", "type": "application/json",
                 "title": "OGC API conformance classes as JSON"},
                {"href": f"{deploypath}/conformance", "rel": "conformance", "type": "text/html",
                 "title": "OGC API conformance classes as HTML"}]}

            apijson["paths"]["/"] = {"get": {"tags": ["Capabilities"], "summary": "landing page",
                                             "description": "Landing page of this dataset",
                                             "operationId": "landingPage", "parameters": [], "responses": {
                    "default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/LandingPage"}},
                        "text/html": {"schema": {}}}}}}}
            apijson["paths"]["/conformance"] = {
                "get": {"tags": ["Capabilities"], "summary": "supported conformance classes",
                        "description": "Retrieves the supported conformance classes", "operationId": "conformance",
                        "parameters": [], "responses": {"default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Conformance"}},
                        "text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}
            collectionsjson = {"collections": [], "links": [
                {"href": f"{deploypath}collections/index.json", "rel": "self", "type": "application/json",
                 "title": "this document as JSON"},
                {"href": f"{deploypath}collections/index.html", "rel": "self", "type": "text/html",
                 "title": "this document as HTML"}]}
            collectionshtml = f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1" /><link rel="stylesheet" href="../style.css"/><link rel="stylesheet" href="https://cdn.datatables.net/2.2.1/css/dataTables.dataTables.css" /><script src="https://code.jquery.com/jquery-3.7.1.js"></script><script src="https://cdn.datatables.net/2.2.1/js/dataTables.js"></script></head><body><header id="header"><h1 id="title">Collections of {deploypath}</h1></header>{{{{collectiontable}}}}<footer id="footer"><a href="../">Landing page</a>&nbsp;<a href="index.json">This page as JSON</a></footer><script>$(document).ready( function () {{$('#collectiontable').DataTable();}} );</script></body></html>"""
            collectiontable = "<table id=\"collectiontable\"><thead><th>Collection</th><th>#Features</th><th>Links</th></thead><tbody>"
            apijson["paths"]["/collections"] = {"get": {"tags": ["Collections"], "summary": "describes collections",
                                                        "description": "Describes all collections provided by this service",
                                                        "operationId": "collections", "parameters": [], "responses": {
                    "default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Collections"}},
                        "text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}
            if outpath.endswith("/"):
                outpath = outpath[0:-1]
            DocUtils.createFoldersFromList([f"{outpath}/api/", f"{outpath}/license/", f"{outpath}/collections/", f"{outpath}/conformance/"])
        result = list()
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
            if ogcapi:
                collection_path = coll.replace(outpath, "").replace("index.geojson", "")
                collection_path_without_extension = collection_path.replace(".geojson", "")
                collection_id = collection_path_without_extension[1:]
                op = f'{outpath}/collections/{collection_path}/'
                op = op.replace(".geojson", "")
                op = op.replace("//", "/")
                os.makedirs(op,exist_ok=True)
                os.makedirs(f"{op}/items/",exist_ok=True)
                opweb = deploypath[0:-1]+f'{deploypath[-1:]}/collections/{collection_path}/'.replace("//", "/")
                opweb_base = opweb.replace(".geojson", "")
                opwebcoll = opweb
                if opwebcoll.endswith("/"):
                    opwebcoll = opwebcoll[0:-1]
                collid = collection_id
                collectionsjson["collections"].append(
                    {"id": collid,"title": featurecollectionspaths[coll]["name"], "links": [
                        {"href": f"{opweb_base}/index.json",
                         "rel": "collection", "type": "application/json", "title": "Collection as JSON"},
                        {"href": f"{opweb_base}/", "rel": "collection",
                         "type": "text/html", "title": "Collection as HTML"},
                        {"href": f"{opweb_base}/index.ttl",
                         "rel": "collection", "type": "text/ttl", "title": "Collection as TTL"}]})
                currentcollection = {"title": featurecollectionspaths[coll]["name"], "id": collid, "links": [
                    {"href": f"{opwebcoll}/items/index.json", "rel": "items", "type": "application/json",
                     "title": "Collection as JSON"},
                    {"href": f"{opwebcoll}/items/{collectionhtmlname}", "rel": "items", "type": "text/html",
                     "title": "Collection as HTML"},
                    {"href": f"{opwebcoll}/items/index.ttl", "rel": "collection", "type": "text/ttl",
                     "title": "Collection as TTL"}], "itemType": "feature"}
                currentcollection["itemCount"]=len(curcoll["features"])
                collectionsjson["collections"][-1]["itemCount"]=len(curcoll["features"])
                if "bbox" in curcoll:
                    currentcollection["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                    collectionsjson["collections"][-1]["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                if "crs" in curcoll:
                    currentcollection["crs"] = curcoll["crs"]
                    currentcollection["storageCrs"] = curcoll["crs"]
                    collectionsjson["collections"][-1]["crs"] = curcoll["crs"]
                    collectionsjson["collections"][-1]["storageCrs"] = curcoll["crs"]
                    if "extent" in currentcollection:
                        currentcollection["extent"]["spatial"]["crs"] = curcoll["crs"]
                        collectionsjson["collections"][-1]["extent"]["spatial"]["crs"] = curcoll["crs"]
                cname = collection_id.rstrip("/")
                apijson["paths"][f"/collections/{cname}"] = {
                    "get": {"tags": ["Collections"], "summary": f"describes collection {cname}",
                            "description": f"Describes the collection with the id {cname}",
                            "operationId": f"collection-{collection_id}",
                            "parameters": [], "responses": {"default": {"description": "default response", "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Collections"},"example": None}}}}}}
                opwebrep = opweb_base
                curcollrow = f'<tr><td><a href="{opwebrep}/items/{collectionhtmlname}">{featurecollectionspaths[coll]["name"]}</a></td><td>{len(curcoll["features"])}</td><td><a href="{opwebrep}/items/{collectionhtmlname}">[Collection as HTML]</a>&nbsp;<a href="{opwebrep}/items/">[Collection as JSON]</a>&nbsp;<a href="{opwebrep}/items/index.ttl">[Collection as TTL]</a></td></tr>'
                with open(f"{op}index.json", "w", encoding="utf-8") as f:
                    json.dump(currentcollection,f)
                with open(op + collectionhtmlname, "w", encoding="utf-8") as f:
                    f.write(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1" /></head><body><h1>{featurecollectionspaths[coll]["name"]}</h1><table><thead><tr><th>Collection</th><th>Links</th></tr></thead><tbody>{curcollrow}</tbody></table></html>')
                collectiontable += curcollrow
                if os.path.exists(coll):
                    try:
                        normalized_coll_path = coll.replace("//", "/")
                        index_json_path = f"{op}/items/index.json".replace("//", "/")
                        index_ttl_path = f"{op}/items/index.ttl".replace("//", "/")
                        index_html_path = f"{op}/items/{collectionhtmlname}".replace("//", "/")
                        if os.path.exists(normalized_coll_path):
                            targetpath = DocUtils.generateRelativeSymlink(normalized_coll_path,index_json_path,outpath)
                            p = Path(index_json_path)
                            p.symlink_to(targetpath)
                        source_ttl_path = normalized_coll_path.replace("index.geojson", "index.ttl").replace(
                                f'nonns_{featurecollectionspaths[coll]["id"]}.geojson',
                                f'nonns_{featurecollectionspaths[coll]["id"]}.ttl')
                        if os.path.exists(source_ttl_path):
                            targetpath = DocUtils.generateRelativeSymlink(source_ttl_path,index_ttl_path, outpath)
                            p = Path(index_ttl_path)
                            p.symlink_to(targetpath)
                        source_html_path = normalized_coll_path.replace("index.geojson", "index.html").replace(
                            f'nonns_{featurecollectionspaths[coll]["id"]}.geojson',
                            f'nonns_{featurecollectionspaths[coll]["id"]}.html')
                        if os.path.exists(source_html_path):
                            targetpath = DocUtils.generateRelativeSymlink(source_html_path,index_html_path, outpath)
                            with open(f'{op}/items/{collectionhtmlname}', "w",encoding="utf-8") as f:
                                if "nonns" in collid:
                                    f.write(f'<html><head><meta http-equiv="refresh" content="0; url={deploypath}/{collid}.html" /></head></html>')
                                else:
                                    f.write(f'<html><head><meta http-equiv="refresh" content="0; url={deploypath}/{collid}/" /></head></html>')
                        #print("symlinks created")
                    except Exception as e:
                        print("symlink creation error")
                        print(e)
                    cname = collection_id
                    collection_items_api_path = f'/collections/{cname}/items'.replace("//", "/")
                    apijson["paths"][f'{collection_items_api_path}/index.json'] = {"get": {"tags": ["Data"],
                                                                                   "summary": f"retrieves features of collection {cname.rstrip('/')}",
                                                                                   "description": f"Retrieves features of collection  {cname}",
                                                                                   "operationId": f"features-{cname}",
                                                                                   "parameters": [], "responses": {
                            "default": {"description": "default response",
                                        "content": {"application/geo+json": {"example": None}},
                                        "text/ttl": {"schema": {"example": None}, "example": None},
                                        "text/html": {"schema": {"example": None}, "example": None}}}}}
                    apijson["paths"][f'{collection_items_api_path}/{{featureId}}/index.json'] = {"get": {"tags": ["Data"],
                                                                                               "summary": f"retrieves feature of collection {cname.rstrip('/')}",
                                                                                               "description": f"Retrieves one single feature of the collection with the id {cname}",
                                                                                               "operationId": f"feature-{cname}", "parameters": [
                            {"name": "featureId", "in": "path", "required": True, "schema": {"type": "string"}}],
                                                                                               "responses": {
                                                                                                   "default": {
                                                                                                       "description": "default response",
                                                                                                       "content": {
                                                                                                           "application/geo+json": {
                                                                                                               "example": None}},
                                                                                                       "text/ttl": {
                                                                                                           "schema": {"example": None},
                                                                                                           "example": None},
                                                                                                       "text/html": {
                                                                                                           "schema": {"example": None},
                                                                                                           "example": None}}}}}

                    for feat in curcoll["features"]:
                        feature_id = feat["id"]
                        featpath = feature_id.replace(prefixnamespace, "").replace("//", "/")
                        try:
                            basepath=f'{op}/items/{DocUtils.shortenURI(feat["id"])}'.replace("//", "/")
                            feature_source_path = feature_id.replace(prefixnamespace, f"{outpath}/")
                            os.makedirs(basepath)
                            #print("CHECKPATH: " + str(
                            #    str(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.json").replace("//", "/")))
                            if os.path.exists(f"{feature_source_path}/index.json"):
                                targetpath = DocUtils.generateRelativeSymlink(f"{featpath}/index.json", f"{basepath}/index.json", outpath, True)
                                p = Path(f"{basepath}/index.json")
                                p.symlink_to(targetpath)
                            if os.path.exists(f"{feature_source_path}/index.ttl"):
                                targetpath = DocUtils.generateRelativeSymlink(f"{featpath}/index.ttl", f"{basepath}/index.ttl", outpath, True)
                                p = Path(f"{basepath}/index.ttl")
                                p.symlink_to(targetpath)
                            if os.path.exists(f"{feature_source_path}/index.html"):
                                targetpath = DocUtils.generateRelativeSymlink(f"{featpath}/index.html", f"{basepath}/index.html", outpath, True)
                                with open(f"{basepath}/index.html", "w",encoding="utf-8") as f:
                                    f.write(f'<html><head><meta http-equiv="refresh" content="0; url={targetpath}" /></head></html>')
                                #print("symlinks created")
                        except Exception as e:
                            print("symlink creation error")
                            print(e)
                    if mergeJSON:
                        result.append(curcoll)
        collectiontable += "</tbody></table>"
        if mergeJSON:
            with open(f"{outpath}/features.js", 'w', encoding="utf-8") as output_file:
                output_file.write("var featurecolls=")
                json.dump(result,output_file)
                # shutil.move(coll, op+"/items/index.json")
        if ogcapi:
            with open(f"{outpath}/index.json", "w", encoding="utf-8") as f:
                json.dump(landingpagejson,f)
            with open(f"{outpath}/api/index.json", "w", encoding="utf-8") as f:
                json.dump(apijson,f)
            with open(f"{outpath}/api/api.html", "w", encoding="utf-8") as f:
                f.write(apihtml)
            with open(f"{outpath}/collections/{collectionhtmlname}", "w", encoding="utf-8") as f:
                f.write(collectionshtml.replace("{{collectiontable}}", collectiontable))
            with open(f"{outpath}/collections/index.json", "w", encoding="utf-8") as f:
                json.dump(collectionsjson,f)
            with open(f"{outpath}/conformance/index.json", "w", encoding="utf-8") as f:
                json.dump(conformancejson,f)
