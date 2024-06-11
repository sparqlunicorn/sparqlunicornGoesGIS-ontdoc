import os
import json

class WFSExporter:

    @staticmethod
    def generateWFSPages(outpath,deploypath, featurecollectionspaths,license):
        #os.mkdir(outpath+"/wfs")
        apihtml = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><metaname=\"description\" content=\"SwaggerUI\"/><title>SwaggerUI</title><link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist/swagger-ui.css\" /></head><body><div id=\"swagger-ui\"></div><script src=\"https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js\" crossorigin></script><script>const swaggerUrl = \"" + str(
            deploypath) + "/api/index.json\"; const apiUrl = \"" + str(
            deploypath) + "/\";  window.onload = () => {let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({spec: j,dom_id: '#swagger-ui'});}));};</script></body></html>"
        apijson = {"openapi": "3.0.1", "info": {"title": str(deploypath) + " Feature Collections",
                                                "description": "Feature Collections of " + str(deploypath)},
                   "servers": [{"url": str(deploypath)}], "paths": {}}
        getcapabilities=f"""
        <wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs" xmlns:ogc="http://www.opengis.net/ogc" xmlns:BAYSIS_Strassennetz="https://www.baysis.bayern.de/gis/admin/services/BAYSIS_Strassennetz/MapServer/WFSServer" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.0.0/WFS-capabilities.xsd https://www.baysis.bayern.de/gis/admin/services/BAYSIS_Strassennetz/MapServer/WFSServer https://www.baysis.bayern.de/gis/services/wfs/BAYSIS_Strassennetz/MapServer/WFSServer?service=wfs%26version=1.0.0%26request=DescribeFeatureType" version="1.0.0">
            <wfs:Service>
            <wfs:Name>Static WFS</wfs:Name>
            <wfs:Title>Static WFS for {deploypath}</wfs:Title>
            <wfs:Abstract>This Static WFS exposes geodata included in the knowledge grap for the inclusion into GIS applications.</wfs:Abstract>
            <wfs:Keywords>{deploypath}</wfs:Keywords>
            <wfs:OnlineResource>{deploypath}</wfs:OnlineResource>
            <wfs:Fees>none</wfs:Fees>
            <wfs:AccessConstraints>{license}</wfs:AccessConstraints>
            </wfs:Service>
            <wfs:Capability>
            <wfs:Request>
            <wfs:GetCapabilities><wfs:DCPType><wfs:HTTP><wfs:Get onlineResource="{deploypath}/wfs?"/></wfs:HTTP></wfs:DCPType>
                        <wfs:DCPType><wfs:HTTP><wfs:Post onlineResource="{deploypath}/wfs?"/></wfs:HTTP></wfs:DCPType>
            </wfs:GetCapabilities>
            <wfs:DescribeFeatureType><wfs:SchemaDescriptionLanguage><wfs:XMLSCHEMA/></wfs:SchemaDescriptionLanguage>
                        <wfs:DCPType><wfs:HTTP><wfs:Get onlineResource="{deploypath}/wfs?"/></wfs:HTTP></wfs:DCPType>
                        <wfs:DCPType><wfs:HTTP><wfs:Post onlineResource="{deploypath}/wfs"/></wfs:HTTP></wfs:DCPType>
            </wfs:DescribeFeatureType>
            <wfs:GetFeature><wfs:ResultFormat><wfs:JSON/></wfs:ResultFormat>
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

                curftype=f"""
                    <wfs:FeatureType>
            <wfs:Name>{str(coll.replace(outpath,"").replace("index.geojson", "").replace(".geojson", "")[1:]).rstrip("/")}</wfs:Name>
            <wfs:Title>{str(coll.replace(outpath,"").replace("index.geojson", "").replace(".geojson", "")[1:]).rstrip("/")}</wfs:Title>
            <wfs:Abstract>FeatureCollection {str(coll.replace(outpath,"").replace("index.geojson", "").replace(".geojson", "")[1:]).rstrip("/")}</wfs:Abstract>
            """
            if "crs" in curcoll:
                curftype+=f"""<wfs:SRS>{curcoll["crs"]}</wfs:SRS>"""
            else:
                curftype+="<wfs:SRS>EPSG:4326</wfs:SRS>"
            if "extent" in curcoll:
                bboxcoords=curcoll["extent"]["spatial"]["bbox"][0]
                curftype+=f"""<wfs:LatLongBoundingBox minx="{bboxcoords[0]}" miny="{bboxcoords[1]}" maxx="{bboxcoords[2]}" maxy="{bboxcoords[3]}"/>"""
            curftype+="</wfs:FeatureType>"
            getcapabilities+=curftype+"\n"
        getcapabilities += f"""</wfs:FeatureTypeList><ogc:Filter_Capabilities></ogc:Filter_Capabilities><wfs:WFS_Capabilities>"""
        f = open(outpath + "/wfs?request=GetCapabilities&service=WFS&version=1.0.0", "w", encoding="utf-8")
        f.write(json.dumps(getcapabilities))
        f.close()