from rdflib import URIRef, Literal
from doc.docutils import DocUtils
from doc.docconfig import DocConfig
from export.pages.page import Page


class LexiconPage(Page):

    tableheader="<thead><th>Lemma</th><th>Lexical Category</th><th>Language</th><th>Forms</th><th>Senses</th></thead>"

    @staticmethod
    def collectionConstraint():
        return ["http://www.w3.org/ns/lemon/lime#Lexicon","http://www.w3.org/ns/lemon/lexicog#LexicographicResource"]

    @staticmethod
    def pageWidgetConstraint():
        return DocConfig.lexicontypes


    @staticmethod
    def extractLexEntry(graph,subject):
        forms = []
        senses = []
        lemma = DocUtils.shortenURI(subject)
        lexcat = "N/A"
        language = ""
        for lexprop in graph.predicate_objects(subject, True):
            lexpredstr=str(lexprop[0])
            lexobjstr = str(lexprop[1])
            if lexpredstr == "http://www.w3.org/ns/lemon/ontolex#sense":
                label=None
                senseref=""
                for senseprop in graph.predicate_objects(lexprop[1], True):
                    if str(senseprop[0]) in DocConfig.labelproperties and isinstance(senseprop[1],Literal):
                        label=senseprop[1]
                    if str(senseprop[0])=="http://www.w3.org/ns/lemon/ontolex#reference":
                        senseref=senseprop[1]
                senses.append({"uri":lexobjstr,"label":label,"reference":str(senseref)})
            elif lexpredstr == "http://www.w3.org/ns/lemon/ontolex#lexicalForm" or lexpredstr == "http://www.w3.org/ns/lemon/ontolex#form":
                label=None
                for formprop in graph.predicate_objects(lexprop[1], True):
                    if str(formprop[0]) in DocConfig.labelproperties and isinstance(formprop[1], Literal):
                        label = formprop[1]
                forms.append({"uri": lexobjstr, "label": label})
            elif lexpredstr == "http://www.w3.org/ns/lemon/ontolex#lemma" or lexpredstr == "http://www.w3.org/ns/lemon/ontolex#canonicalForm":
                lemma = lexobjstr
            elif lexpredstr == "http://purl.org/dc/terms/" or lexpredstr == "http://www.w3.org/ns/lemon/lime#language":
                language = lexobjstr
            elif lexpredstr == "http://www.w3.org/ns/lemon/ontolex#lexicalCategory":
                lexcat = lexobjstr
        return {"lemma":lemma,"lexcat":lexcat,"language":language,"forms":forms,"senses":senses}

    @staticmethod
    def generatePageWidget(graph,subject,f,onlybody=False):
        lexentry=LexiconPage.extractLexEntry(graph,subject)
        if not onlybody:
            f.write(f"<table id=\"lexicon\">{LexiconPage.tableheader}<tbody>")
        f.write("<tr><td><a href=\""+str(subject)+"\" target=\"_blank\">"+str(lexentry["lemma"])+"</a></td><td>"+str(lexentry["lexcat"])+"</td><td>"+str(lexentry["language"])+"</td><td>")
        for form in lexentry["forms"]:
            f.write(f"<a href=\"{form['uri']}\" target=\"_blank\">{form['label']}</a> ")
        f.write("</td><td>")
        for sense in lexentry["senses"]:
            if sense["reference"]!="":
                f.write("<a href=\"" + str(sense["uri"]) + "\" target=\"_blank\">" + str(sense["label"]) + "</a> <a href=\""+str(sense["reference"])+"\" target=\"_blank\">["+DocUtils.shortenURI(str(sense["reference"]))+"]</a>")
            else:
                f.write(f"<a href=\"{sense['uri']}\" target=\"_blank\">{sense['label']}</a> ")
        f.write("</td></tr>")
        if not onlybody:
            f.write("</tbody></table><script>$('#lexicon').DataTable();</script>")

    @staticmethod
    def generateCollectionWidget(graph,subject,templates,f):
        f.write(f"<table id=\"lexicon\">{LexiconPage.tableheader}<tbody>")
        count=0
        for lexentry in graph.objects(subject, URIRef("http://www.w3.org/ns/lemon/lexicog#entry"), True):
            LexiconPage.generatePageWidget(graph,lexentry,f,True)
            count+=1
        if count==0:
            for lexentry in graph.objects(subject, URIRef("http://www.w3.org/ns/lemon/lime#entry"), True):
                LexiconPage.generatePageWidget(graph,lexentry,f,True)
                count+=1
        f.write("</tbody></table>")

    def generatePageView(self,templates,g,f):
        print("PageView")