from src.sparqlunicorn_ontdoc.doc.docconfig import DocConfig


class PersonPage:

    vcardprops=["http://www.w3.org/2006/vcard/ns#hasGender","http://www.w3.org/2006/vcard/ns#bday","http://www.w3.org/2006/vcard/ns#hasPhoto","http://www.w3.org/2006/vcard/ns#given-name","http://www.w3.org/2006/vcard/ns#hasName","http://www.w3.org/2006/vcard/ns#family-name"]

    def extractPersonMetadata(self,subject,graph):
        thevcard={}
        for pprop in graph.predicate_objects(subject, True):
            if str(pprop[0]) in self.vcardprops:
                thevcard[str(pprop[0])]=str(pprop[1])
        return thevcard

    def vcardToHTML(self,vcard):
        result=""
        return result


    def collectionConstraint(self):
        return DocConfig.collectionclasses

    def pageWidgetConstraint(self):
        return ["http://xmlns.com/foaf/0.1/Person","http://www.w3.org/2006/vcard/ns#Individual","http://schema.org/Person","http://dbpedia.org/ontology/Person","http://www.wikidata.org/entity/Q5"]

    def generatePageWidget(self, graph, subject, templates, f=None, pageWidget=False):
        print("PageWidget")
        vcard=self.extractPersonMetadata(subject,graph)
        if pageWidget and f!=None:
            f.write(self.vcardToHTML(vcard))
        return vcard



    def generateCollectionWidget(self, graph, templates, subject, f=None):
        print("CollectionWidget")
        vcards=[]
        for person in graph.predicate_objects(subject):
            if str(person[0]) in DocConfig.collectionrelationproperties:
                vcards.append(self.generatePageWidget(graph,person[1],templates,f,True))
        return vcards