from collections import defaultdict

from doc.docconfig import DocConfig
from doc.docutils import DocUtils
from rdflib import URIRef


_GEO_INSTANCE_TYPES = frozenset({"geoinstance", "featurecollection", "geocollection"})


class ClassTreeUtils:

    @staticmethod
    def getClassTree(graph, uritolabel, uritotreeitem, typeproperty, prefixes, preparedclassquery, instancecount, outpath,
                     pubconfig):
        results = graph.query(preparedclassquery)
        classidset=set()
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
            }, "core": {"themes": {"responsive": True}, "check_callback": True, "data": []},
                "@context": ldcontext["@context"]}
        result = []
        ress = {}
        for res in results:
            # print(res)
            if isinstance(res["subject"], URIRef):
                if isinstance(res["supertype"], URIRef):
                    ress[str(res["subject"])] = {"super": res["supertype"], "label": res["label"]}
                else:
                    ress[str(res["subject"])] = {"super": None, "label": res["label"]}
            # if "_:" not in str(res["subject"]) and str(res["subject"]).startswith("http"):
            #    if "_:" not in str(res["supertype"]) and str(res["supertype"]).startswith("http"):
            #        ress[str(res["subject"])] = {"super": res["supertype"], "label": res["label"]}
            #    else:
            #        ress[str(res["subject"])] = {"super": None, "label": res["label"]}
        # print(ress)
        type_uri = URIRef(typeproperty)
        class_uris = {cls: URIRef(cls) for cls in ress}
        class_uri_set = set(class_uris.values())
        instances_by_class = defaultdict(list)
        for obj, class_uri in graph.subject_objects(type_uri):
            if class_uri in class_uri_set:
                instances_by_class[class_uri].append(obj)

        for cls in ress:
            clsstr = str(cls)
            class_uri = class_uris[cls]
            for obj in instances_by_class[class_uri]:
                objstr = str(obj)
                res = DocUtils.replaceNameSpacesInLabel(prefixes, objstr)
                if objstr in uritolabel:
                    if res is not None:
                        restext = f"{uritolabel[objstr]['label']} ({res['uri']})"
                    else:
                        restext = f"{uritolabel[objstr]['label']} ({DocUtils.shortenURI(objstr)})"
                else:
                    if res is not None:
                        restext = f" ({res['uri']})"
                    else:
                        restext = DocUtils.shortenURI(objstr)
                result.append({"id": objstr, "parent": cls, "type": f'{"instance" if objstr not in DocConfig.collectionclasses else "class"}', "text": restext, "data": {"from": {}, "to": {}}})
                #if objstr not in DocConfig.collectionclasses:
                #    result.append({"id": objstr, "parent": cls, "type": "instance", "text": restext, "data": {"from":{},"to":{}}})
                #else:
                #    result.append({"id": objstr, "parent": cls, "type": "class", "text": restext, "data": {"from":{},"to":{}}})
                uritotreeitem[objstr].append(result[-1])
            # print(ress[cls])
            res = DocUtils.replaceNameSpacesInLabel(prefixes, clsstr)
            if ress[cls]["super"] is None:
                restext = DocUtils.shortenURI(clsstr)
                if res is not None:
                    restext += f" ({res['uri']})"
                if cls not in uritotreeitem:
                    # print("SUPER NOT NONE: " + str({"id": cls, "parent": "#", "type": "class", "text": restext, "data": {}}))
                    if cls in instancecount:
                        result.append({"id": cls, "parent": "#", "type": "class","instancecount":instancecount[cls], "text": restext,
                                       "data": {"from": defaultdict(lambda: defaultdict(int)), "to": defaultdict(lambda: defaultdict(int))}})
                    else:
                        result.append({"id": cls, "parent": "#", "type": "class", "text": restext, "data": {"from":defaultdict(lambda: defaultdict(int)),"to":defaultdict(lambda: defaultdict(int))}})
                    uritotreeitem[cls].append(result[-1])
            else:
                if "label" in cls and ress[cls]["label"] is not None:
                    if res is not None:
                        restext = f"{ress[cls]['label']} ({res['uri']})"
                    else:
                        restext = f"{ress[cls]['label']} ({DocUtils.shortenURI(clsstr)})"
                else:
                    if res is not None:
                        restext = f" ({res['uri']})"
                    else:
                        restext = DocUtils.shortenURI(clsstr)
                if cls not in uritotreeitem:
                    if cls in instancecount:
                        result.append({"id": cls, "parent": ress[cls]["super"],"instancecount":instancecount[cls], "type": "class", "text": restext,
                                       "data": {"from": defaultdict(lambda: defaultdict(int)), "to": defaultdict(lambda: defaultdict(int))}})
                    else:
                        result.append({"id": cls, "parent": ress[cls]["super"], "type": "class", "text": restext, "data": {"from":defaultdict(lambda: defaultdict(int)),"to":defaultdict(lambda: defaultdict(int))}})
                    uritotreeitem[cls].append(result[-1])
                else:
                    uritotreeitem[cls][-1]["parent"] = ress[cls]["super"]
                ressuperstr = str(ress[cls]["super"])
                if ressuperstr not in uritotreeitem:
                    # print("SUPER NOT IN URITOTREEITEM: "+str(ress[cls]["super"])+" ... adding with empty superclass statement...")
                    uritotreeitem[ressuperstr] = []
                    clsres = DocUtils.replaceNameSpacesInLabel(prefixes, ressuperstr)
                    if clsres is not None:
                        theitem = {"id": ressuperstr, "parent": "#", "type": "class",
                                   "text": f'{DocUtils.shortenURI(ressuperstr)} ({clsres["uri"]})', "data": {"from":defaultdict(lambda: defaultdict(int)),"to":defaultdict(lambda: defaultdict(int))}}
                    else:
                        theitem = {"id": ressuperstr, "parent": "#", "type": "class",
                                   "text": DocUtils.shortenURI(ressuperstr), "data": {"from":defaultdict(lambda: defaultdict(int)),"to":defaultdict(lambda: defaultdict(int))}}
                    uritotreeitem[ressuperstr].append(theitem)
                    result.append(theitem)
                classidset.add(ressuperstr)
            classidset.add(clsstr)
        tree["core"]["data"] = result
        return [tree, uritotreeitem, len(classidset)]

    @staticmethod
    def assignGeoClassesToTree(tree):
        classlist = {}
        classcounts = defaultdict(lambda: [0, 0])
        for item in tree["core"]["data"]:
            item_type = item["type"]
            if item_type == "class":
                classlist[item["id"]] = {"items": 0, "geoitems": 0, "item": item}
            elif item_type == "instance":
                classcounts[item["parent"]][0] += 1
            elif item_type in _GEO_INSTANCE_TYPES:
                counts = classcounts[item["parent"]]
                counts[0] += 1
                counts[1] += 1

        for class_id, class_data in classlist.items():
            class_data["items"], class_data["geoitems"] = classcounts[class_id]
            class_item = class_data["item"]
            if class_data["items"] > 0:
                if class_item["text"].endswith("]"):
                    class_item["text"] = f'{class_item["text"][0:class_item["text"].rfind("[") - 1]} [{class_data["items"]}]'
                else:
                    class_item["text"] = f'{class_item["text"]} [{class_data["items"]}]'
            if class_id in DocConfig.collectionclasses:
                class_item["type"] = "collectionclass"
            elif class_data["items"] == class_data["geoitems"] and class_data["items"] > 0 and class_data["geoitems"] > 0:
                class_item["type"] = "geoclass"
            elif class_data["items"] > class_data["geoitems"] > 0:
                class_item["type"] = "halfgeoclass"
            else:
                class_item["type"] = "class"
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
                            item["id"] = f'{item["id"]}_suniv{counter}_'
                        counter += 1
                    if thetype != "instance" or thetype != "class":
                        for item in uritotreeitem[uri]:
                            item["type"] = thetype