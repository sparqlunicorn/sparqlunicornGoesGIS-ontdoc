from rdflib import URIRef
from rdflib.namespace import RDFS
from doc import orjsonutils as json

class VOWLExporter:

    def __init__(self):
        print("init")

    @staticmethod
    def getTypeForProperty(prop,graph,typeproperty):
        for tup in graph.objects(URIRef(prop),URIRef(typeproperty)):
            #print(tup)
            if str(tup)!="http://www.w3.org/1999/02/22-rdf-syntax-ns#Property":
                return VOWLExporter.normalizeNS(str(tup))
        return "rdf:Property"

    @staticmethod
    def getBaseIRI(iri):
        if "#" in iri:
            return iri[0:iri.rfind("#")]
        return iri[0:iri.rfind("/")]

    @staticmethod
    def getIRILabel(iri):
        if "#" in iri:
            return iri[iri.rfind("#")+1:]
        return iri[iri.rfind("/")+1:]

    @staticmethod
    def normalizeNS(prop):
        return prop.replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdf:").replace("http://www.w3.org/2000/01/rdf-schema#","rdfs:").replace("http://www.w3.org/2002/07/owl#","owl:")

    #def inferDomainRanges(self,g,typeproperty):
    #    for subj in g.subjects():
    #        subjclasses=set()
    #        for tuppred in g.objects(subj,URIRef(typeproperty)):
    #            subjclasses.add(tuppred)

    @staticmethod
    def convertOWL2MiniVOWL(g,outpath,outfile=None,predicates=[],typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",labelproperty="http://www.w3.org/2000/01/rdf-schema#label"):
        minivowlresult={"info": [{"description": "Created with pyowl2vowl (version 0.1) as part of the SPARQLing Unicorn QGIS Plugin"}],"nodes": [],"links": []}
        nodes,links=[],[]
        nodeuriToId={}
        iri_label_cache={}
        def iri_label(iri):
            if iri not in iri_label_cache:
                iri_label_cache[iri] = VOWLExporter.getIRILabel(iri)
            return iri_label_cache[iri]
        nodecounter=0
        for _, class_type in g.subject_objects(URIRef(typeproperty)):
            predstr=str(class_type)
            if predstr not in nodeuriToId:
                nodeuriToId[predstr]=nodecounter
                nodecounter+=1
                nodes.append({"name": iri_label(predstr), "type": "class", "uri": predstr})
        if predicates:
            for pred in predicates:
                if "from" in predicates[pred] and "to" in predicates[pred]:
                    predstr = str(pred)
                    for fromsub in predicates[pred]["from"]:
                        fromsub_str = str(fromsub)
                        if fromsub_str in nodeuriToId:
                            if predicates[pred]["to"]!=[]:
                                for topred in predicates[pred]["to"]:
                                    topred_str = str(topred)
                                    if "http://www.w3.org/1999/02/22-rdf-syntax-ns#" not in topred_str and "http://www.w3.org/2002/07/owl#" not in topred_str:
                                        links.append({"source": nodeuriToId[fromsub_str],
                                                      "target": nodeuriToId[topred_str],
                                                      "valueTo": iri_label(predstr),
                                                      "propertyTo": "class",
                                                      "uriTo": predstr})
        else:
            outgoing_by_subject = {}
            for subject, predicate, object in g:
                subject_str = str(subject)
                if subject_str in nodeuriToId:
                    outgoing_by_subject.setdefault(subject_str, []).append((predicate, object))
            for node in nodeuriToId:
                for predicate, object in outgoing_by_subject.get(node, ()):
                    object_str = str(object)
                    predicate_str = str(predicate)
                    if object_str in nodeuriToId and predicate_str!=typeproperty:
                        is_uri_ref = object.__class__ is URIRef
                        links.append({"source":nodeuriToId[node],"target":nodeuriToId[object_str],"valueTo": iri_label(predicate_str), "propertyTo":("class" if is_uri_ref else "datatype"), "uriTo":(object_str if is_uri_ref else object.datatype)})
        minivowlresult["nodes"]=nodes
        minivowlresult["links"] = links
        with open(f'{outpath}/{outfile}', "w",encoding="utf-8") as f:
            f.write("var minivowlresult=")
            json.dump(minivowlresult,f)
        return minivowlresult

    @staticmethod
    def convertOWL2VOWL(g,outpath,typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",labelproperty="http://www.w3.org/2000/01/rdf-schema#label"):
        vowlresult = {"_comment": "Created with pyowl2vowl (version 0.1) as part of the SPARQLing Unicorn QGIS Plugin",
                      "header": {"prefixList": {}, "baseIris": [], "languages": []}, "namespace": [], "class": [],
                      "classAttribute": [], "property": [], "propertyAttribute": []}
        props,propAttributes,classes,classAttributes=[],[],[],[]
        classiriToProdId,propiriToProdId={},{}
        idcounter=0
        tprop=URIRef(typeproperty)
        lprop=URIRef(labelproperty)
        typed_triples = list(g.subject_objects(tprop))
        types_by_subject = {}
        for subject, object in typed_triples:
            types_by_subject.setdefault(str(subject), []).append(object)
        range_triples = list(g.subject_objects(RDFS.range))
        subjects_to_index = {str(subject) for subject, _ in typed_triples}
        subjects_to_index.update(str(object) for _, object in range_triples)
        outgoing_by_subject = {}
        for subject, predicate, object in g:
            subject_str = str(subject)
            if subject_str in subjects_to_index:
                outgoing_by_subject.setdefault(subject_str, []).append((predicate, object))
        iri_label_cache={}
        base_iri_cache={}
        def iri_label(iri):
            if iri not in iri_label_cache:
                iri_label_cache[iri] = VOWLExporter.getIRILabel(iri)
            return iri_label_cache[iri]
        def base_iri(iri):
            if iri not in base_iri_cache:
                base_iri_cache[iri] = VOWLExporter.getBaseIRI(iri)
            return base_iri_cache[iri]
        for nstup in g.namespaces():
            vowlresult["header"]["prefixList"][str(nstup[0])]=str(nstup[1])
            vowlresult["header"]["baseIris"].append(str(nstup[1]))
        for pred in typed_triples:
            #print(pred)
            predsubstr = str(pred[0])
            predobjstr = str(pred[1])
            if predobjstr=="http://www.w3.org/2002/07/owl#Class" or predobjstr=="http://www.w3.org/2000/01/rdf-schema#Class" or predobjstr=="http://www.w3.org/2000/01/rdf-schema#Datatype":
                classes.append({"id":idcounter,"type":predobjstr})
                classiriToProdId[predsubstr]={"id":idcounter,"attid":len(classAttributes)-1}
                classAttributes.append({"id":idcounter,"iri":predsubstr,"baseIRI":base_iri(predsubstr), "instances":0, "label":{"IRI-based":iri_label(predsubstr)}, "annotations":{}, "subClasses":[], "superClasses":[]})
                idcounter+=1
            else:
                property_type = "rdf:Property"
                for type_object in types_by_subject.get(predsubstr, ()):
                    if str(type_object)!="http://www.w3.org/1999/02/22-rdf-syntax-ns#Property":
                        property_type = VOWLExporter.normalizeNS(str(type_object))
                        break
                props.append({"id":idcounter,"type":property_type})
                propiriToProdId[predsubstr]={"id":idcounter,"attid":len(propAttributes)-1}
                propAttributes.append({"id":idcounter,"iri":predsubstr,"baseIRI":base_iri(predsubstr), "instances":0, "label":{"IRI-based":iri_label(predsubstr)}, "annotations":{}, "range":[], "domain":[], "subProperties":[], "superProperties":[]})
                idcounter+=1

        for pred in range_triples:
            predstr=str(pred[1])
            if predstr not in classiriToProdId:
                classes.append({"id":idcounter,"type":"http://www.w3.org/2000/01/rdf-schema#Datatype"})
                classiriToProdId[predstr]={"id":idcounter,"attid":len(classAttributes)-1}
                classAttributes.append({"id":idcounter,"iri":predstr,"baseIRI":base_iri(predstr), "instances":0, "label":{"IRI-based":iri_label(predstr)}, "annotations":{}, "subClasses":[], "superClasses":[]})
                idcounter+=1

        for iri in classiriToProdId:
            #print(iri)
            for predicate, object in outgoing_by_subject.get(iri, ()):
                clsatt = (predicate, object)
                #print(clsatt)
                clsattstr0=str(clsatt[0])
                clsattstr1 = str(clsatt[1])
                if clsattstr0 != typeproperty:
                    if clsattstr0 == str(RDFS.subClassOf):
                        if clsattstr1 in classiriToProdId:
                            classAttributes[classiriToProdId[iri]["attid"]]["superClasses"].append(str(classiriToProdId[clsattstr1]["id"]))
                            classAttributes[classiriToProdId[clsattstr1]["attid"]]["subClasses"].append(str(classiriToProdId[iri]["id"]))
                    elif clsattstr0 == labelproperty:
                        classAttributes[classiriToProdId[iri]["attid"]]["label"]=clsattstr1
                    else:
                        classAttributes[classiriToProdId[iri]["attid"]]["annotations"][clsattstr0]=[]
                        if clsattstr1.startswith("http"):
                            classAttributes[classiriToProdId[iri]["attid"]]["annotations"][clsattstr0].append({"identifier":clsattstr0,"language":"undefined","value":clsattstr1,"type":"iri"})
                        else:
                            classAttributes[classiriToProdId[iri]["attid"]]["annotations"][clsattstr0].append({"identifier":clsattstr0,"language":"undefined","value":clsattstr1,"type":"label"})

        for iri in propiriToProdId:
            #print(iri)
            for predicate, object in outgoing_by_subject.get(iri, ()):
                propatt = (predicate, object)
                #print(propatt)
                propattpred = str(propatt[0])
                propattobj=str(propatt[1])
                if propattpred!=typeproperty:
                    if propattpred=="http://www.w3.org/2000/01/rdf-schema#subPropertyOf":
                        if propattobj in propiriToProdId:
                            propAttributes[propiriToProdId[iri]["attid"]]["superProperties"].append(str(propiriToProdId[propattobj]["id"]))
                            propAttributes[propiriToProdId[propattobj]["attid"]]["subProperties"].append(str(propiriToProdId[iri]["id"]))
                    elif propattpred=="http://www.w3.org/2000/01/rdf-schema#range" and propattobj in propiriToProdId:
                        propAttributes[propiriToProdId[iri]["attid"]]["range"].append(str(classiriToProdId[propattobj]["id"]))
                    elif propattpred=="http://www.w3.org/2000/01/rdf-schema#domain" and propattobj in propiriToProdId:
                        propAttributes[propiriToProdId[iri]["attid"]]["domain"].append(str(classiriToProdId[propattobj]["id"]))
                    elif propattpred==labelproperty:
                        propAttributes[propiriToProdId[iri]["attid"]]["label"]=propattobj
                    else:
                        propAttributes[propiriToProdId[iri]["attid"]]["annotations"][propattpred]=[]
                        if propattobj.startswith("http"):
                            propAttributes[propiriToProdId[iri]["attid"]]["annotations"][propattpred].append({"identifier":propattpred,"language":"undefined","value":propattobj,"type":"iri"})
                        else:
                            propAttributes[propiriToProdId[iri]["attid"]]["annotations"][propattpred].append({"identifier":propattpred,"language":"undefined","value":propattobj,"type":"label"})

        vowlresult["property"]=props
        vowlresult["propertyAttribute"]=propAttributes
        vowlresult["class"]=classes
        vowlresult["classAttribute"]=classAttributes
        with open(f"{outpath}/vowl_result.js","w",encoding="utf-8") as f:
            f.write("var vowlresult=")
            json.dump(vowlresult,f)
        return vowlresult