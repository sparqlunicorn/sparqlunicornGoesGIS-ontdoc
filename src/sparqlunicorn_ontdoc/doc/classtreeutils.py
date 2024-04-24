from doc.docconfig import DocConfig
from doc.docutils import DocUtils
from rdflib import URIRef
import json

class ClassTreeUtils:


    @staticmethod
    def getClassTree(graph, uritolabel, classidset, uritotreeitem,typeproperty,prefixes,preparedclassquery,outpath,pubconfig):
        results = graph.query(preparedclassquery)
        ldcontext = {"@context": {
            "@version": 1.1,
            "foaf": "http://xmlns.com/foaf/0.1/",
            "ct": "http://purl.org/vocab/classtree#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "icon": "foaf:image",
            "id": "@id",
            "parent": "rdfs:subClassOf",
            "halfgeoclass": "ct:HalfGeoClass",
            "geoclass": {"@type": "ct:icontype", "@id": "ct:GeoClass"},
            "collectionclass": {"@type": "ct:icontype", "@id": "ct:CollectionClass"},
            "featurecollectionclass": {"@type": "ct:icontype", "@id": "ct:FeatureCollectionClass"},
            "class": "owl:Class",
            "instance": "owl:NamedIndividual",
            "geoinstance": {"@type": "ct:Icontype", "@id": "ct:GeoNamedIndividual"},
            "text": "rdfs:label",
            "type": "ct:icontype",
            "types": "ct:icontypes",
            "core": {"@type": "ct:TreeConfig", "@id": "@nest"},
            "data": {"@id": "ct:treeitem", "@type": "ct:TreeItem"}
        }}
        tree = {"plugins": ["defaults", "search", "sort", "state", "types", "contextmenu"],
                "search": {"show_only_matches": True}, "types": {
                "class": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/class.png"},
                "geoclass": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoclass.png"},
                "halfgeoclass": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/halfgeoclass.png"},
                "collectionclass": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/collectionclass.png"},
                "geocollection": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geometrycollection.png"},
                "featurecollection": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/featurecollection.png"},
                "instance": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/instance.png"},
                "geoinstance": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoinstance.png"}
            },
                "core": {"themes": {"responsive": True}, "check_callback": True, "data": []}}
        tree["@context"] = ldcontext["@context"]
        result = []
        ress = {}
        for res in results:
            # print(res)
            substr=str(res["subject"])
            supstr = str(res["supertype"])
            if "_:" not in substr and substr.startswith("http"):
                if "_:" not in supstr and supstr.startswith("http"):
                    if substr in ress and ress[substr]["super"] is None:
                        ress[substr]["super"]=supstr
                    else:
                        ress[substr] = {"super": supstr, "label": res["label"]}
                    if supstr not in ress:
                        ress[supstr] = {"super": None, "label": DocUtils.shortenURI(supstr)}
                else:
                    ress[substr] = {"super": None, "label": res["label"]}
        print(ress)
        for cls in ress:
            clsstr=str(cls)
            for obj in graph.subjects(URIRef(typeproperty), URIRef(cls), True):
                objstr=str(obj)
                res = DocUtils.replaceNameSpacesInLabel(prefixes, objstr)
                if objstr in uritolabel:
                    restext = f"{uritolabel[objstr]['label']} ({DocUtils.shortenURI(objstr)})"
                    if res is not None:
                        restext = uritolabel[objstr]["label"] + " (" + res["uri"] + ")"
                else:
                    restext = DocUtils.shortenURI(objstr)
                    if res is not None:
                        restext += f" ({res['uri']})"
                if objstr not in DocConfig.collectionclasses:
                    result.append({"id": objstr, "parent": cls, "type": "instance", "text": restext, "data": {}})
                else:
                    result.append({"id": objstr, "parent": cls, "type": "class", "text": restext, "data": {}})
                if objstr not in uritotreeitem:
                    uritotreeitem[objstr] = []
                uritotreeitem[objstr].append(result[-1])
                # classidset.add(str(obj))
            #print(ress[cls])
            res = DocUtils.replaceNameSpacesInLabel(prefixes, clsstr)
            if ress[cls]["super"] is None:
                restext = DocUtils.shortenURI(clsstr)
                if res is not None:
                    restext += " (" + res["uri"] + ")"
                if cls not in uritotreeitem:
                    #print("SUPER NOT NONE: " + str({"id": cls, "parent": "#", "type": "class", "text": restext, "data": {}}))
                    result.append({"id": cls, "parent": "#", "type": "class", "text": restext, "data": {}})
                    uritotreeitem[clsstr] = []
                    uritotreeitem[clsstr].append(result[-1])
            else:
                if "label" in cls and ress[cls]["label"] is not None:
                    restext = f"{ress[cls]['label']} ({DocUtils.shortenURI(clsstr)})"
                    if res is not None:
                        restext = f"{ress[cls]['label']} ({res['uri']})"
                else:
                    restext = DocUtils.shortenURI(clsstr)
                    if res is not None:
                        restext += " (" + res["uri"] + ")"
                if cls not in uritotreeitem:
                    result.append({"id": cls, "parent": ress[cls]["super"], "type": "class", "text": restext, "data": {}})
                    if clsstr not in uritotreeitem:
                        uritotreeitem[clsstr] = []
                        uritotreeitem[clsstr].append(result[-1])
                else:
                    uritotreeitem[cls][-1]["parent"] = ress[cls]["super"]
                if str(ress[cls]["super"]) not in uritotreeitem:
                    #print("SUPER NOT IN URITOTREEITEM: "+str(ress[cls]["super"])+" ... adding with empty superclass statement...")
                    uritotreeitem[str(ress[cls]["super"])] = []
                    clsres = DocUtils.replaceNameSpacesInLabel(prefixes, str(ress[cls]["super"]))
                    if clsres is not None:
                        theitem = {"id": str(ress[cls]["super"]), "parent": "#", "type": "class","text": DocUtils.shortenURI(str(ress[cls]["super"])) + " (" + clsres["uri"] + ")","data": {}}
                    else:
                        theitem = {"id": str(ress[cls]["super"]), "parent": "#", "type": "class","text": DocUtils.shortenURI(str(ress[cls]["super"])), "data": {}}
                    uritotreeitem[str(ress[cls]["super"])].append(theitem)
                    result.append(theitem)
                classidset.add(str(ress[cls]["super"]))
            classidset.add(clsstr)
        tree["core"]["data"] = result
        with open(outpath + pubconfig["corpusid"] + "_classtree_raw.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=2))
            f.close()
        return [tree,uritotreeitem,classidset]

    @staticmethod
    def assignGeoClassesToTree(tree):
        classlist = {}
        for item in tree["core"]["data"]:
            if item["type"] == "class":
                classlist[item["id"]] = {"items": 0, "geoitems": 0, "item": item}
        for item in tree["core"]["data"]:
            if item["type"] == "instance" and item["parent"] in classlist:
                classlist[item["parent"]]["items"] += 1
            elif (item["type"] == "geoinstance" or item["type"] == "featurecollection" or item[
                "type"] == "geocollection") and item["parent"] in classlist:
                classlist[item["parent"]]["items"] += 1
                classlist[item["parent"]]["geoitems"] += 1
        for item in classlist:
            if classlist[item]["items"] > 0:
                if classlist[item]["item"]["text"].endswith("]"):
                    classlist[item]["item"]["text"] = classlist[item]["item"]["text"][
                                                      0:classlist[item]["item"]["text"].rfind("[") - 1] + " [" + str(
                        classlist[item]["items"]) + "]"
                else:
                    classlist[item]["item"]["text"] = classlist[item]["item"]["text"] + " [" + str(
                        classlist[item]["items"]) + "]"
            if item in DocConfig.collectionclasses:
                classlist[item]["item"]["type"] = "collectionclass"
            elif classlist[item]["items"] == classlist[item]["geoitems"] and classlist[item]["items"] > 0 and \
                    classlist[item]["geoitems"] > 0:
                classlist[item]["item"]["type"] = "geoclass"
            elif classlist[item]["items"] > classlist[item]["geoitems"] and classlist[item]["geoitems"] > 0:
                classlist[item]["item"]["type"] = "halfgeoclass"
            else:
                classlist[item]["item"]["type"] = "class"
        return classlist

    @staticmethod
    def checkGeoInstanceAssignment(uritotreeitem):
        for uri in uritotreeitem:
            if len(uritotreeitem[uri]) > 1:
                thetype = "instance"
                counter = 0
                if uritotreeitem[uri] is not None:
                    for item in uritotreeitem[uri]:
                        if item["type"] != "instance" or item["type"] != "class":
                            thetype = item["type"]
                        if item["type"] != "class":
                            item["id"] = item["id"] + "_suniv" + str(counter) + "_"
                        counter += 1
                    if thetype != "instance" or thetype != "class":
                        for item in uritotreeitem[uri]:
                            item["type"] = thetype