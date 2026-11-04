
import os
from doc import orjsonutils as json
from pathlib import Path

from doc.docutils import DocUtils


class StacAPIExporter:

    @staticmethod
    def generateOGCAPIFeaturesPages(outpath,deploypath, featurecollectionspaths, prefixnamespace, ogcapi, mergeJSON):
        apihtml = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><metaname="description" content="SwaggerUI"/><title>SwaggerUI</title><link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css" /></head><body><div id="swagger-ui"></div><script src="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js" crossorigin></script><script>const swaggerUrl = "{deploypath}/api/index.json"; const apiUrl = "{deploypath}/";  window.onload = () => {{let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {{j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({{spec: j,dom_id: '#swagger-ui'}});}}));}};</script></body></html>"""
        apijson = {"openapi": "3.0.1", "stac_version":"1.0.0", "info": {"title": f"{deploypath} Feature Collections",
                                                "description": f"Feature Collections of {deploypath}"},
                   "servers": [{"url": str(deploypath)}], "paths": {}}
        conformancejson = {"conformsTo": ["https://api.statspec.org/v1.0.0/core",
                                          "https://api.statspec.org/v1.0.0/ogcapi-features",
                                          "https://api.statspec.org/v1.0.0/collections",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"]}
        if ogcapi:
            apijson["paths"]["/api"] = {
                "get": {"tags": ["Capabilities"], "summary": "api documentation", "description": "api documentation",
                        "operationId": "openApi", "parameters": [], "responses": {
                        "default": {"description": "default response",
                                    "content": {"application/vnd.oai.openapi+json;version=3.0": {},
                                                "application/json": {}, "text/html": {"schema": {}}}}}}}
            apijson["paths"]["/license/dataset"] = {}
            apijson["components"] = {"schemas": {"Conformance": {"type": "object", "properties": {
                "conformsTo": {"type": "array", "items": {"type": "string"}}}, "xml": {"name": "ConformsTo",
                                                                                       "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Collection": {"type": "object", "properties": {
                                                     "id": {"type": "string", "xml": {"name": "Id",
                                                                                      "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "title": {"type": "string", "xml": {"name": "Title",
                                                                                         "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "description": {"type": "string", "xml": {"name": "Description",
                                                                                               "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "links": {"type": "array", "xml": {"name": "link",
                                                                                        "namespace": "http://www.w3.org/2005/Atom"},
                                                               "items": {"$ref": "#/components/schemas/Link"}},
                                                     "extent": {"$ref": "#/components/schemas/Extent"},
                                                     "itemType": {"type": "string"},
                                                     "crs": {"type": "array", "items": {"type": "string"}},
                                                     "storageCrs": {"type": "string"}}, "xml": {"name": "Collection",
                                                                                                "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Collections": {"type": "object", "properties": {
                                                     "links": {"type": "array", "xml": {"name": "link",
                                                                                        "namespace": "http://www.w3.org/2005/Atom"},
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
                                                          "xml": {"name": "link",
                                                                  "namespace": "http://www.w3.org/2005/Atom"}},
                                                 "Spatial": {"type": "object", "properties": {"bbox": {"type": "array",
                                                                                                       "items": {
                                                                                                           "type": "array",
                                                                                                           "items": {
                                                                                                               "type": "number",
                                                                                                               "format": "double"}}},
                                                                                              "crs": {"type": "string",
                                                                                                      "xml": {
                                                                                                          "attribute": True}}},
                                                             "xml": {"name": "SpatialExtent",
                                                                     "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Temporal": {"type": "object", "properties": {
                                                     "interval": {"type": "array",
                                                                  "items": {"type": "string", "format": "date-time"}},
                                                     "trs": {"type": "string", "xml": {"attribute": True}}},
                                                              "xml": {"name": "TemporalExtent",
                                                                      "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "LandingPage": {"type": "object"}}}
            landingpagejson = {"stac_version":"1.0.0","title": "Landing Page", "description": "Landing Page", "conformsTo":conformancejson,"type":"Catalog","links": [{
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
                "href": f"{deploypath}/collections/indexc.html",
                "rel": "data",
                "type": "text/html",
                "title": "Supported Feature Collections as HTML"
            }, {"href": f"{deploypath}/api/index.json", "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0", "title": "API definition"},
                {"href": f"{deploypath}/api", "rel": "service-desc", "type": "text/html",
                 "title": "API definition as HTML"},
                {"href": f"{deploypath}/conformance", "rel": "conformance", "type": "application/json",
                 "title": "OGC API conformance classes as Json"},
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
                {"href": f"{outpath}collections/index.json", "rel": "self", "type": "application/json",
                 "title": "this document as JSON"},
                {"href": f"{outpath}collections/index.html", "rel": "self", "type": "text/html",
                 "title": "this document as HTML"}]}
            collectionshtml = f"<html><head></head><body><header><h1>Collections of {deploypath}</h1></head>{{collectiontable}}<footer><a href=\"index.json\">This page as JSON</a></footer></body></html>"
            collectiontable = "<table><thead><th>Collection</th><th>Links</th></thead><tbody>"
            apijson["paths"]["/collections"] = {"get": {"tags": ["Collections"], "summary": "describes collections",
                    "description": "Describes all collections provided by this service","operationId": "collections", "parameters": [], "responses": {
                    "default": {"description": "default response", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Collections"}},
                        "text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}
            if outpath.endswith("/"):
                outpath = outpath[0:-1]
            DocUtils.createFoldersFromList([
                f"{outpath}/api/", f"{outpath}/license/",
                f"{outpath}/collections/", f"{outpath}/conformance/"
            ])
        result = list()
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
            if ogcapi:
                collection_path = coll.replace(outpath, "").replace("index.geojson", "")
                op = f"{outpath}/collections/{collection_path}/"
                op = op.replace(".geojson", "")
                op = op.replace("//", "/")
                os.makedirs(op, exist_ok=True)
                items_path = f"{op}/items/"
                os.makedirs(items_path, exist_ok=True)
                opweb = op.replace(outpath, deploypath)
                opweb_base = opweb.replace(".geojson", "")
                opweb_link_base = opweb_base.replace("//", "/")
                opweb_link_root = opweb_link_base if opweb_link_base.endswith("/") else f"{opweb_link_base}/"
                opwebcoll = opweb
                if opwebcoll.endswith("/"):
                    opwebcoll = opwebcoll[0:-1]
                opwebcoll = opwebcoll.replace("//", "/")
                collection_id = collection_path.replace(".geojson", "")[1:]
                collectionsjson["collections"].append(
                    {"stac_version":"1.0.0","stac_extensions":[],"id": collection_id,"type":"Collection",
                     "title": featurecollectionspaths[coll]["name"], "links": [
                        {"href": f"{opweb_link_root}index.json",
                         "rel": "collection", "type": "application/json", "title": "Collection as JSON"},
                        {"href": opweb_link_root, "rel": "collection",
                         "type": "text/html", "title": "Collection as HTML"},
                        {"href": f"{opweb_link_root}index.ttl",
                         "rel": "collection", "type": "text/ttl", "title": "Collection as TTL"}]})
                currentcollection = {"title": featurecollectionspaths[coll]["name"],
                                     "id": collection_id,
                                     "links": [
                                         {"href": f"{opwebcoll}/items/index.json", "rel": "items",
                                          "type": "application/json",
                                          "title": "Collection as JSON"},
                                         {"href": f"{opwebcoll}/items/indexc.html", "rel": "items", "type": "text/html",
                                          "title": "Collection as HTML"},
                                         {"href": f"{opwebcoll}/items/index.ttl", "rel": "collection",
                                          "type": "text/ttl",
                                          "title": "Collection as TTL"}], "itemType": "feature"}
                if "bbox" in curcoll:
                    currentcollection["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                    collectionsjson["collections"][-1]["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                if "crs" in curcoll:
                    currentcollection["crs"] = curcoll["crs"]
                    collectionsjson["collections"][-1]["crs"] = curcoll["crs"]
                    if "extent" in currentcollection:
                        currentcollection["extent"]["spatial"]["crs"] = curcoll["crs"]
                        collectionsjson["collections"][-1]["extent"]["spatial"]["crs"] = curcoll["crs"]
                cname = collection_id.rstrip("/")
                apijson["paths"][f"/collections/{cname}"] = {
                    "get": {"tags": ["Collections"], "summary": f"describes collection {cname}", "description": f"Describes the collection with the id {cname}", "operationId": f"collection-{collection_id}",
                            "parameters": [], "responses": {"default": {"description": "default response", "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Collections"},
                                                 "example": None}}}}}}
                curcollrow = f'<tr><td><a href="{opweb_base}/items/indexc.html">{featurecollectionspaths[coll]["name"]}</a></td><td><a href="{opweb_base}/items/indexc.html">[Collection as HTML]</a>&nbsp;<a href="{opweb_base}/items/">[Collection as JSON]</a>&nbsp;<a href="{opweb_base}/items/index.ttl">[Collection as TTL]</a></td></tr>'
                with open(f"{op}index.json", "w", encoding="utf-8") as f:
                    json.dump(currentcollection,f)
                with open(f"{op}indexc.html", "w", encoding="utf-8") as f:
                    f.write(f'<html><head></head><body><h1>{featurecollectionspaths[coll]["name"]}</h1><table><thead><tr><th>Collection</th><th>Links</th></tr></thead><tbody>{curcollrow}</tbody></table></html>')
                collectiontable += curcollrow
                if os.path.exists(coll):
                    try:
                        collection_data_id = featurecollectionspaths[coll]["id"]
                        collection_items_dir = f"{op}/items"
                        normalized_coll_path = coll.replace("//", "/")
                        index_json_path = f"{collection_items_dir}/index.json".replace("//", "/")
                        index_ttl_path = f"{collection_items_dir}/index.ttl".replace("//", "/")
                        index_html_path = f"{collection_items_dir}/indexc.html".replace("//", "/")
                        source_ttl_path = normalized_coll_path.replace("index.geojson", "index.ttl").replace(
                            f"nonns_{collection_data_id}.geojson", f"nonns_{collection_data_id}.ttl")
                        source_html_path = normalized_coll_path.replace("index.geojson", "index.html").replace(
                            f'nonns_{featurecollectionspaths[coll]["id"]}.geojson',
                            f'nonns_{featurecollectionspaths[coll]["id"]}.html')
                        if os.path.exists(normalized_coll_path):
                            targetpath = DocUtils.generateRelativeSymlink(normalized_coll_path, index_json_path, outpath)
                            p = Path(index_json_path)
                            p.symlink_to(targetpath)
                        if os.path.exists(source_ttl_path):
                            targetpath = DocUtils.generateRelativeSymlink(
                                source_ttl_path, index_ttl_path, outpath)
                            p = Path(index_ttl_path)
                            p.symlink_to(targetpath)
                        if os.path.exists(source_html_path):
                            targetpath = DocUtils.generateRelativeSymlink(
                                source_html_path, index_html_path, outpath)
                            with open(index_html_path, "w",encoding="utf-8") as f:
                                f.write(f'<html><head><meta http-equiv="refresh" content="0; url={targetpath}" /></head></html>')
                        #print("symlinks created")
                    except Exception as e:
                        print("symlink creation error")
                        print(e)
                    collection_items_path = f"/collections/{collection_id}/items".replace("//", "/")
                    apijson["paths"][f"{collection_items_path}/index.json"] = {"get": {"tags": ["Data"],
                                                                                   "summary": f"retrieves features of collection {cname}",
                                                                                   "description": f"Retrieves features of collection  {collection_id}",
                                                                                   "operationId": f"features-{collection_id}",
                                                                                   "parameters": [], "responses": {
                            "default": {"description": "default response",
                                        "content": {"application/geo+json": {"example": None}},
                                        "text/ttl": {"schema": {"example": None}, "example": None},
                                        "text/html": {"schema": {"example": None}, "example": None}}}}}
                    apijson["paths"][f"{collection_items_path}/{{featureId}}/index.json"] = {"get": {"tags": ["Data"],
                                                                                               "summary": f"retrieves feature of collection {cname}",
                                                                                               "description": f"Retrieves one single feature of the collection with the id {collection_id}",
                                                                                               "operationId": f"feature-{collection_id}", "parameters": [
                            {"name": "featureId", "in": "path", "required": True, "schema": {"type": "string"}}],
                                                                                               "responses": {
                                                                                                   "default": {
                                                                                                       "description": "default response",
                                                                                                       "content": {
                                                                                                           "application/geo+json": {
                                                                                                               "example": None}},
                                                                                                       "text/ttl": {
                                                                                                           "schema": {
                                                                                                               "example": None},
                                                                                                           "example": None},
                                                                                                       "text/html": {
                                                                                                           "schema": {
                                                                                                               "example": None},
                                                                                                           "example": None}}}}}

                    for feat in curcoll["features"]:
                        feature_id = feat["id"]
                        featpath = feature_id.replace(prefixnamespace, "").replace("//", "/")
                        try:
                            short_feature_id = DocUtils.shortenURI(feature_id)
                            feature_source_path = feature_id.replace(prefixnamespace, f"{outpath}/")
                            normalized_feature_output_path = f'{op}/items/{short_feature_id}'.replace("//", "/")
                            os.makedirs(normalized_feature_output_path)
                            #print("CHECKPATH: " + str(
                            #    str(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.json").replace("//", "/")))
                            if os.path.exists(f"{feature_source_path}/index.json"):
                                targetpath = DocUtils.generateRelativeSymlink(f"{featpath}/index.json", f"{normalized_feature_output_path}/index.json", outpath, True)
                                p = Path(f"{normalized_feature_output_path}/index.json")
                                p.symlink_to(targetpath)
                            if os.path.exists(f"{feature_source_path}/index.ttl"):
                                targetpath = DocUtils.generateRelativeSymlink(f"{featpath}/index.ttl", f"{normalized_feature_output_path}/index.ttl", outpath, True)
                                p = Path(f"{normalized_feature_output_path}/index.ttl")
                                p.symlink_to(targetpath)
                            if os.path.exists(f"{feature_source_path}/index.html"):
                                targetpath = DocUtils.generateRelativeSymlink(f"{featpath}/index.html", f"{normalized_feature_output_path}/index.html", outpath, True)
                                with open(f"{normalized_feature_output_path}/index.html", "w",encoding="utf-8") as f:
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
            with open(f"{outpath}/collections/indexc.html", "w", encoding="utf-8") as f:
                f.write(collectionshtml.replace("{{collectiontable}}", collectiontable))
            with open(f"{outpath}/collections/index.json", "w", encoding="utf-8") as f:
                json.dump(collectionsjson,f)
            with open(f"{outpath}/conformance/index.json", "w", encoding="utf-8") as f:
                json.dump(conformancejson,f)