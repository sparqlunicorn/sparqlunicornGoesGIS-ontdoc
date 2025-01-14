import os
import json

class WFSExporter:

    @staticmethod
    def generateFeatureDescriptions(outpath,deploypath,featurecollectionspaths,version,fsresult):
        result="""<schema xmlns:myns="http://www.someserver.example.com/myns" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.w3.org/2001/XMLSchema" xmlns:gml="http://www.opengis.net/gml/3.2" targetNamespace="http://www.someserver.example.com/myns" elementFormDefault="qualified" version="2.0.2">
<import namespace="http://www.opengis.net/gml/3.2" schemaLocation="http://schemas.opengis.net/gml/3.2.1/gml.xsd"/>"""
        os.mkdir(outpath + "/wfs/DescribeFeatureType")
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
                op = outpath + "wfs/DescribeFeatureType/request=DescribeFeatureType&version="+version+"&typeName=" + coll.replace(outpath, "").replace("index.geojson", "")
                os.mkdir(op)
                op = op.replace(".geojson", "")
                op = op.replace("//", "/")
                if not os.path.exists(op):
                    os.makedirs(op)
                opweb = op.replace(outpath, deploypath)
                opwebcoll = opweb
                if opwebcoll.endswith("/"):
                    opwebcoll = opwebcoll[0:-1]
                opwebcoll = opwebcoll.replace("//", "/")
                collid=coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]
                currentcollection = {"title": featurecollectionspaths[coll]["name"],
                                     "id": collid,
                                     "links": [], "itemType": "feature"}
                if "bbox" in curcoll:
                    currentcollection["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                if "crs" in curcoll:
                    currentcollection["crs"] = curcoll["crs"]
                    if "extent" in currentcollection:
                        currentcollection["extent"]["spatial"]["crs"] = curcoll["crs"]
                if "features" in curcoll and len(curcoll["features"])>0:
                    firstfeat=curcoll["features"][0]
                    if "properties" in firstfeat:
                        result+="<complexType name=\""+coll+"\"><complexContent><extension base=\"gml:AbstractFeatureType\"><sequence>"
                        for prop in firstfeat["properties"]:
                            result+=f"""<element name="{prop}" minOccurs="0"/>"""
                        result+="</sequence></extension></complexContent></complexType>"
                f = open(op + "/index.json", "w", encoding="utf-8")
                f.write(json.dumps(currentcollection))
                f.close()
                f = open(op + "/index.html", "w", encoding="utf-8")
                f.write("<html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /></head><body><h1>" + featurecollectionspaths[coll][
                    "name"] + "</h1><table><thead><tr><th>Collection</th><th>Links</th></tr></thead><tbody>" #+ str(curcollrow)
                     + "</tbody></table></html>")
                f.close()


    @staticmethod
    def generateFeatureList(outpath,deploypath,featurecollectionspaths,version,fsresult):
        apijson={}
        collectionshtml = "<html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><link rel=\"stylesheet\" href=\"../style.css\"/><link rel=\"stylesheet\" href=\"https://cdn.datatables.net/2.2.1/css/dataTables.dataTables.css\" /><script src=\"https://code.jquery.com/jquery-3.7.1.js\"></script><script src=\"https://cdn.datatables.net/2.2.1/js/dataTables.js\"></script></head><body><header id=\"header\"><h1 id=\"title\">Collections of " + str(
            deploypath) + "</h1></header>{{collectiontable}}<footer id=\"footer\"><a href=\"../\">Landing page</a>&nbsp;<a href=\"index.json\">This page as JSON</a></footer><script>$(document).ready( function () {$('#collectiontable').DataTable();} );</script></body></html>"
        collectiontable = "<table id=\"collectiontable\"><thead><th>Collection</th><th>#Features</th><th>Links</th></thead><tbody>"
        os.mkdir(outpath+"/wfs/GetFeature")
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
                op = outpath + "wfs/GetFeature/request=GetFeature&version="+version+"&typeName=" + coll.replace(outpath, "").replace("index.geojson", "")
                os.mkdir(op)
                op = op.replace(".geojson", "")
                op = op.replace("//", "/")
                if not os.path.exists(op):
                    os.makedirs(op)
                opweb = op.replace(outpath, deploypath)
                opwebcoll = opweb
                if opwebcoll.endswith("/"):
                    opwebcoll = opwebcoll[0:-1]
                opwebcoll = opwebcoll.replace("//", "/")
                collid=coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]
                currentcollection = {"title": featurecollectionspaths[coll]["name"],
                                     "id": collid,
                                     "links": [], "itemType": "feature"}
                if "bbox" in curcoll:
                    currentcollection["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                if "crs" in curcoll:
                    currentcollection["crs"] = curcoll["crs"]
                    if "extent" in currentcollection:
                        currentcollection["extent"]["spatial"]["crs"] = curcoll["crs"]
                #apijson["paths"]["/collections/" + str(
                #    coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]).rstrip("/")] = {
                #    "get": {"tags": ["Collections"], "summary": "describes collection " + str(
                #        str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:])).rstrip(
                #        "/"), "description": "Describes the collection with the id " + str(
                #        str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:])).rstrip(
                #        "/"), "operationId": "collection-" + str(
                #        coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]),
                #            "parameters": [], "responses": {"default": {"description": "default response", "content": {
                #            "application/json": {"schema": {"$ref": "#/components/schemas/Collections"},"example": None}}}}}}
                #curcollrow = "<tr><td><a href=\"" + opweb.replace(".geojson", "") + "/items/"+collectionhtmlname+"\">" + str(
                #    featurecollectionspaths[coll]["name"]) + "</a></td><td>"+str(len(curcoll["features"]))+"</td><td><a href=\"" + opweb.replace(".geojson",
                #                                                                                       "") + "/items/"+collectionhtmlname+"\">[Collection as HTML]</a>&nbsp;<a href=\"" + opweb.replace(
                #    ".geojson", "") + "/items/\">[Collection as JSON]</a>&nbsp;<a href=\"" + opweb.replace(".geojson",
                #                                                                                           "") + "/items/index.ttl\">[Collection as TTL]</a></td></tr>"
                f = open(op + "/index.json", "w", encoding="utf-8")
                f.write(json.dumps(currentcollection))
                f.close()
                f = open(op + "/index.html", "w", encoding="utf-8")
                f.write("<html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /></head><body><h1>" + featurecollectionspaths[coll][
                    "name"] + "</h1><table><thead><tr><th>Collection</th><th>Links</th></tr></thead><tbody>" #+ str(curcollrow)
                     + "</tbody></table></html>")
                f.close()


    @staticmethod
    def generateWFSPages10(outpath,deploypath,featurecollectionspaths,license):
        getcapabilities = f"""<?xml version="1.0" encoding="UTF-8" ?>
        <wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-capabilities.xsd" version="1.0.0">
            <wfs:Service>
                <wfs:Name>Static WFS 1.0.0</wfs:Name>
                <wfs:Title>Static WFS for {deploypath}</wfs:Title>
                <wfs:Abstract>This Static WFS exposes geodata included in the knowledge grap for the inclusion into GIS applications.</wfs:Abstract>
                <wfs:Keywords>{deploypath}</wfs:Keywords>
                <wfs:OnlineResource>{deploypath}</wfs:OnlineResource>
                <wfs:Fees>none</wfs:Fees>
                <wfs:AccessConstraints>{license}</wfs:AccessConstraints>
            </wfs:Service>
            <wfs:Capability>
                <wfs:Request>
                    <wfs:GetCapabilities>
                        <wfs:DCPType><wfs:HTTP><wfs:Get onlineResource="{deploypath}/wfs?"/></wfs:HTTP></wfs:DCPType>
                        <wfs:DCPType><wfs:HTTP><wfs:Post onlineResource="{deploypath}/wfs?"/></wfs:HTTP></wfs:DCPType>
                    </wfs:GetCapabilities>
                    <wfs:DescribeFeatureType>
                        <wfs:SchemaDescriptionLanguage><wfs:XMLSCHEMA/></wfs:SchemaDescriptionLanguage>
                        <wfs:DCPType><wfs:HTTP><wfs:Get onlineResource="{deploypath}/wfs?"/></wfs:HTTP></wfs:DCPType>
                        <wfs:DCPType><wfs:HTTP><wfs:Post onlineResource="{deploypath}/wfs"/></wfs:HTTP></wfs:DCPType>
                    </wfs:DescribeFeatureType>
                    <wfs:GetFeature>
                        <wfs:ResultFormat><wfs:JSON/></wfs:ResultFormat>
                        <wfs:DCPType><wfs:HTTP><wfs:Get onlineResource="{deploypath}/wfs?"/></wfs:HTTP></wfs:DCPType>
                        <wfs:DCPType><wfs:HTTP><wfs:Post onlineResource="{deploypath}/wfs"/></wfs:HTTP></wfs:DCPType>
                    </wfs:GetFeature>
                </wfs:Request>
            </wfs:Capability>
            <wfs:FeatureTypeList><wfs:Operations><wfs:Query/></wfs:Operations>
                """
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
                curftype = f"""
                            <wfs:FeatureType>
                    <wfs:Name>{str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")).rstrip("/")}</wfs:Name>
                    <wfs:Title>{str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")).rstrip("/")}</wfs:Title>
                    <wfs:Abstract>FeatureCollection {str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")).rstrip("/")}</wfs:Abstract>
                    """
            if "crs" in curcoll:
                curftype += f"""<wfs:SRS>{curcoll["crs"]}</wfs:SRS>"""
            else:
                curftype += "<wfs:SRS>EPSG:4326</wfs:SRS>"
            if "extent" in curcoll:
                bboxcoords = curcoll["extent"]["spatial"]["bbox"][0]
                curftype += f"""<wfs:LatLongBoundingBox minx="{bboxcoords[0]}" miny="{bboxcoords[1]}" maxx="{bboxcoords[2]}" maxy="{bboxcoords[3]}"/>"""
            curftype += "</wfs:FeatureType>"
            getcapabilities += curftype + "\n"
        getcapabilities += f"""</wfs:FeatureTypeList>
            <ogc:Filter_Capabilities></ogc:Filter_Capabilities>
        </wfs:WFS_Capabilities>"""
        print("SAVE WFS GETCAPABILITIES: " + str(outpath + "/wfs?request=GetCapabilities&service=WFS&version=1.0.0"))

        f = open(outpath + "/wfs/index.xml", "w", encoding="utf-8")
        f.write(getcapabilities)
        f.close()

    @staticmethod
    def generateWFSPages11(outpath,deploypath,featurecollectionspaths,license):
        getcapabilities="<wfs:WFS_Capabilities xmlns:ows=\"http://www.opengis.net/ows\" xmlns:ogc=\"http://www.opengis.net/ogc\" xmlns:wfs=\"http://www.opengis.net/wfs\" xmlns:gml=\"http://www.opengis.net/gml\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.3/wfs.xsd\" version=\"1.1.3\" updateSequence=\"0\">"
        getcapabilities+=f"""
        <ows:ServiceIdentification>
            <ows:Title>Static WFS 1.1.0</ows:Title>
            <ows:Abstract>This Static WFS exposes geodata included in the knowledge grap for the inclusion into GIS applications.</ows:Abstract>
            <ows:Keywords>
            <ows:Keyword>{deploypath}</ows:Keyword>
            <ows:Type>String</ows:Type>
            </ows:Keywords>
            <ows:ServiceType>WFS</ows:ServiceType>
            <ows:ServiceTypeVersion>1.1.3</ows:ServiceTypeVersion>
            <ows:ServiceTypeVersion>1.1.2</ows:ServiceTypeVersion>
            <ows:ServiceTypeVersion>1.1.1</ows:ServiceTypeVersion>
            <ows:ServiceTypeVersion>1.1.0</ows:ServiceTypeVersion>
            <ows:Fees>None</ows:Fees>
            <ows:AccessConstraints>{license}</ows:AccessConstraints>
        </ows:ServiceIdentification>
        <ows:OperationsMetadata>
            <ows:Operation name="GetCapabilities">
                <ows:DCP><ows:HTTP><ows:Get xlink:href=\"{deploypath}/wfs/\"/></ows:HTTP></ows:DCP>
                <ows:Parameter name="AcceptVersions">
                    <ows:Value>1.1.0</ows:Value>
                    <ows:Value>1.1.1</ows:Value>
                    <ows:Value>1.1.2</ows:Value>
                    <ows:Value>1.1.3</ows:Value>
                </ows:Parameter>
                <ows:Parameter name="AcceptFormats">
                    <ows:Value>text/xml</ows:Value>
                </ows:Parameter>
            </ows:Operation>
            <ows:Operation name="DescribeFeatureType">
                <ows:DCP><ows:HTTP><ows:Get xlink:href=\"{deploypath}/wfs/DescribeFeatureType/\"/></ows:HTTP></ows:DCP>
                <ows:Parameter name="resultType">
                    <ows:Value>results</ows:Value>
                    <ows:Value>hits</ows:Value>
                </ows:Parameter>
            </ows:Operation>
            <ows:Operation name="GetFeature">
                <ows:DCP><ows:HTTP><ows:Get xlink:href=\"{deploypath}/wfs/GetFeature/\"/></ows:HTTP></ows:DCP>
                <ows:Parameter name="resultType">
                    <ows:Value>results</ows:Value>
                    <ows:Value>hits</ows:Value>
                </ows:Parameter>
            </ows:Operation>
        </ows:OperationsMetadata>
        <wfs:FeatureTypeList>"""
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
                curftype = f"""
                <wfs:FeatureType>
                    <wfs:Name>{str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")).rstrip("/")}</wfs:Name>
                    <wfs:Title>{str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")).rstrip("/")}</wfs:Title>
                    <wfs:Abstract>FeatureCollection {str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")).rstrip("/")}</wfs:Abstract>
                    """
            if "crs" in curcoll:
                curftype += f"""<wfs:DefaultSRS>{curcoll["crs"]}</wfs:DefaultSRS>"""
            else:
                curftype += "<wfs:DefaultSRS>EPSG:4326</wfs:DefaultSRS>"
            if "extent" in curcoll:
                bboxcoords = curcoll["extent"]["spatial"]["bbox"][0]
                curftype += f"""<ows:WGS84BoundingBox><ows:LowerCorner>{bboxcoords[0]}" {bboxcoords[1]}"</ows:LowerCorner><ows:UpperCorner>"{bboxcoords[2]}" "{bboxcoords[3]}"</ows:UpperCorner></ows:WGS84BoundingBox>"""
            curftype += "</wfs:FeatureType>"
            getcapabilities += curftype + "\n"
        getcapabilities += f"""</wfs:FeatureTypeList>
            <ogc:Filter_Capabilities></ogc:Filter_Capabilities>
        </wfs:WFS_Capabilities>"""
        WFSExporter.generateFeatureList(outpath, deploypath, featurecollectionspaths, "1.1.0", "")
        WFSExporter.generateFeatureDescriptions(outpath, deploypath, featurecollectionspaths, "1.1.0", "")
        print("SAVE WFS GETCAPABILITIES: " + str(outpath + "/wfs?request=GetCapabilities&service=WFS&version=1.0.0"))
        f = open(outpath + "/wfs/index.xml", "w", encoding="utf-8")
        f.write(getcapabilities)
        f.close()

    @staticmethod
    def generateWFSPages20(outpath,deploypath,featurecollectionspaths,license):
        getcapabilities="<WFS_Capabilities xmlns=\"http://www.opengis.net/wfs/2.0\" xmlns:gml=\"http://www.opengis.net/gml/3.2\" xmlns:fes=\"http://www.opengis.net/fes/2.0\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xmlns:ows=\"http://www.opengis.net/ows/1.1\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" version=\"2.0.2\" xsi:schemaLocation=\"http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd http://www.opengis.net/ows/1.1 http://schemas.opengis.net/ows/1.1.0/owsAll.xsd\">"
        getcapabilities+=f"""
        <ows:ServiceIdentification>
            <ows:Title>Static WFS 2.0</ows:Title>
            <ows:Abstract>This Static WFS exposes geodata included in the knowledge grap for the inclusion into GIS applications.</ows:Abstract>
            <ows:Keywords>
            <ows:Keyword>{deploypath}</ows:Keyword>
            <ows:Type>String</ows:Type>
            </ows:Keywords>
            <ows:ServiceType>WFS</ows:ServiceType>
            <ows:ServiceTypeVersion>2.0.2</ows:ServiceTypeVersion>
            <ows:ServiceTypeVersion>2.0.1</ows:ServiceTypeVersion>
            <ows:ServiceTypeVersion>2.0.0</ows:ServiceTypeVersion>
            <ows:Fees>None</ows:Fees>
            <ows:AccessConstraints>{license}</ows:AccessConstraints>
        </ows:ServiceIdentification>
        <wfs:FeatureTypeList>"""
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
                curftype = f"""
                            <wfs:FeatureType>
                    <wfs:Name>{str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")).rstrip("/")}</wfs:Name>
                    <wfs:Title>{str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")).rstrip("/")}</wfs:Title>
                    <wfs:Abstract>FeatureCollection {str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")).rstrip("/")}</wfs:Abstract>
                    """
            if "crs" in curcoll:
                curftype += f"""<wfs:SRS>{curcoll["crs"]}</wfs:SRS>"""
            else:
                curftype += "<wfs:SRS>EPSG:4326</wfs:SRS>"
            if "extent" in curcoll:
                bboxcoords = curcoll["extent"]["spatial"]["bbox"][0]
                curftype += f"""<wfs:LatLongBoundingBox minx="{bboxcoords[0]}" miny="{bboxcoords[1]}" maxx="{bboxcoords[2]}" maxy="{bboxcoords[3]}"/>"""
            curftype += "</wfs:FeatureType>"
            getcapabilities += curftype + "\n"
        getcapabilities += f"""</wfs:FeatureTypeList>
            <ogc:Filter_Capabilities></ogc:Filter_Capabilities>
        </wfs:WFS_Capabilities>"""
        f = open(outpath + "/wfs/index.xml", "w", encoding="utf-8")
        f.write(getcapabilities)
        f.close()

    @staticmethod
    def generateWFSPages(outpath,deploypath, featurecollectionspaths,license,wfsversion="1.1.0"):
        os.mkdir(outpath+"/wfs")
        apihtml = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><metaname=\"description\" content=\"SwaggerUI\"/><title>SwaggerUI</title><link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist/swagger-ui.css\" /></head><body><div id=\"swagger-ui\"></div><script src=\"https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js\" crossorigin></script><script>const swaggerUrl = \"" + str(
            deploypath) + "/api/index.json\"; const apiUrl = \"" + str(deploypath) + "/\";  window.onload = () => {let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({spec: j,dom_id: '#swagger-ui'});}));};</script></body></html>"
        apijson = {"openapi": "3.0.1", "info": {"title": str(deploypath) + " Feature Collections",
                                                "description": "Feature Collections of " + str(deploypath)},
                   "servers": [{"url": str(deploypath)}], "paths": {}}
        if wfsversion=="1.0.0":
            WFSExporter.generateWFSPages10(outpath,deploypath,featurecollectionspaths,license)
        elif wfsversion.startswith("1.1"):
            WFSExporter.generateWFSPages11(outpath, deploypath, featurecollectionspaths, license)
        elif wfsversion=="2" or wfsversion.startswith("2."):
            WFSExporter.generateWFSPages20(outpath, deploypath, featurecollectionspaths, license)
