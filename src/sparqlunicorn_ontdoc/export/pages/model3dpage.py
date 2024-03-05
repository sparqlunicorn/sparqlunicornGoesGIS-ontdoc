
class Model3DPage:

    def generatePageWidget(self,graph,templates,foundmedia,subject,f,onlybody=False):
        print("PageWidget")
        if len(foundmedia["mesh"]) > 0 and len(image3dannos) > 0:
            if self.iiif:
                iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, self.outpath, self.deploypath, foundmedia["mesh"],
                                                         image3dannos, annobodies, str(subject), self.prefixnamespace,
                                                         imagetoURI, self.imagemetadata, DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Model"))
            for anno in image3dannos:
                if ("POINT" in anno["value"].upper() or "POLYGON" in anno["value"].upper() or "LINESTRING" in anno[
                    "value"].upper()):
                    f.write(templates["threejstemplate"].replace("{{wktstring}}", anno["value"]).replace("{{meshurls}}",
                                                                                                         str(list(
                                                                                                             foundmedia[
                                                                                                                 "mesh"]))))
        elif len(foundmedia["mesh"]) > 0 and len(image3dannos) == 0:
            print("Found 3D Model: " + str(foundmedia["mesh"]))
            if self.iiif:
                iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, self.outpath, self.deploypath, foundmedia["mesh"],
                                                         image3dannos, annobodies, str(subject), self.prefixnamespace,
                                                         imagetoURI, self.imagemetadata, DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Model"))
            for curitem in foundmedia["mesh"]:
                format = "ply"
                if ".nxs" in curitem or ".nxz" in curitem:
                    format = "nexus"
                elif format == "gltf":
                    f.write(templates["threejstemplate"].replace("{{wktstring}}", "").replace("{{meshurls}}", "[]"))
                f.write(templates["3dtemplate"].replace("{{meshurl}}", curitem).replace("{{meshformat}}", format))
                break
        elif len(foundmedia["mesh"]) == 0 and len(image3dannos) > 0:
            for anno in image3dannos:
                if ("POINT" in anno["value"].upper() or "POLYGON" in anno["value"].upper() or "LINESTRING" in anno[
                    "value"].upper()):
                    f.write(templates["threejstemplate"].replace("{{wktstring}}", anno["value"]).replace("{{meshurls}}",
                                                                                                         "[]"))

    def generateCollectionWidget(self,graph,templates,subject,f):
        print("CollectionWidget")

    def generatePageView(self,headertemplate,footertemplate,g,f):
        f.write(str(headertemplate))
        print("PageView")