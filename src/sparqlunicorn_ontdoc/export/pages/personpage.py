from src.sparqlunicorn_ontdoc.doc.docconfig import DocConfig


class PersonPage:

    vcardprops=["http://www.w3.org/2006/vcard/ns#hasGender","http://www.w3.org/2006/vcard/ns#bday","http://www.w3.org/2006/vcard/ns#hasPhoto","http://www.w3.org/2006/vcard/ns#given-name","http://www.w3.org/2006/vcard/ns#hasName","http://www.w3.org/2006/vcard/ns#family-name"]

    def extractPersonMetadata(self,subject,graph):
        for pprop in graph.predicate_objects(subject, True):
            if str(pprop) in self.vcardprops:
                print("Vcardprop")



    def collectionConstraint(self):
        return DocConfig.collectionclasses

    def pageWidgetConstraint(self):
        return ["http://xmlns.com/foaf/0.1/Person","http://www.w3.org/2006/vcard/ns#Individual","http://schema.org/Person","http://dbpedia.org/ontology/Person","http://www.wikidata.org/entity/Q5"]

    def generatePageWidget(self, graph, memberid, templates, f, pageWidget=False):
        print("PageWidget")


    def generateCollectionWidget(self, graph, templates, subject, f):
        print("CollectionWidget")

