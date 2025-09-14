from doc.docconfig import DocConfig
from doc.docutils import DocUtils
from rdflib import URIRef, Literal
from collections import OrderedDict



class SHACLPage:

    @staticmethod
    def pageWidgetConstraint():
        return ["http://www.w3.org/ns/shacl#NodeShape","http://www.w3.org/ns/shacl#Shape","http://www.w3.org/ns/shacl#PropertyShape"]

    @staticmethod
    def collectionConstraint():
        return DocConfig.collectionclasses

    @staticmethod
    def processPropertyShape(graph,subject,f):
        resmapprop={}
        resmapprop["http://www.w3.org/ns/shacl#minCount"]=None
        resmapprop["http://www.w3.org/ns/shacl#maxCount"]=None
        resmapprop["http://www.w3.org/ns/shacl#minLength"]=None
        resmapprop["http://www.w3.org/ns/shacl#maxLength"]=None
        resmapprop["http://www.w3.org/ns/shacl#languageIn"]=None
        resmapprop["http://www.w3.org/ns/shacl#datatype"]=None
        resmapprop["http://www.w3.org/ns/shacl#pattern"]=None
        resmapprop["http://www.w3.org/ns/shacl#path"] = None
        for predobj in graph.predicate_objects(subject):
            if str(predobj[0]) in resmapprop:
                if isinstance(predobj[1], URIRef):
                    resmapprop[str(predobj[0])] = f"<a href=\"{predobj[1]}\">{DocUtils.shortenURI(str(predobj[1]))}</a>"
                else:
                    resmapprop[str(predobj[0])] = str(predobj[1])
        f.write(f'<td><a href="{subject}">{DocUtils.shortenURI(str(subject))}</a></td><td><a href="http://www.w3.org/ns/shacl#PropertyShape">sh:PropertyShape</a></td><td>')
        if "http://www.w3.org/ns/shacl#path" in resmapprop and resmapprop["http://www.w3.org/ns/shacl#path"] is not None:
            f.write(resmapprop["http://www.w3.org/ns/shacl#path"])
        f.write("</td><td>")
        for val in resmapprop:
            if resmapprop[val] is not None:
                f.write(f'<a href="{val}">{DocUtils.shortenURI(val)}</a>:{resmapprop[val]}<br/>')
        f.write("</td>")

    @staticmethod
    def generatePageWidget(graph,subject,type,f,onlybody=False):
        resmapprop={}
        resmapprop["http://www.w3.org/ns/shacl#minCount"]=None
        resmapprop["http://www.w3.org/ns/shacl#maxCount"]=None
        resmapprop["http://www.w3.org/ns/shacl#minLength"]=None
        resmapprop["http://www.w3.org/ns/shacl#maxLength"]=None
        resmapprop["http://www.w3.org/ns/shacl#languageIn"]=None
        resmapprop["http://www.w3.org/ns/shacl#datatype"]=None
        resmapprop["http://www.w3.org/ns/shacl#pattern"]=None
        resmapprop["http://www.w3.org/ns/shacl#path"] = None
        resmap=OrderedDict()
        resmap["http://www.w3.org/ns/shacl#targetNode"]=""
        resmap["http://www.w3.org/ns/shacl#targetClass"]=None
        resmap["http://www.w3.org/ns/shacl#minCount"]=None
        resmap["http://www.w3.org/ns/shacl#maxCount"]=None
        resmap["http://www.w3.org/ns/shacl#minLength"]=None
        resmap["http://www.w3.org/ns/shacl#maxLength"]=None
        resmap["http://www.w3.org/ns/shacl#languageIn"]=None
        resmap["http://www.w3.org/ns/shacl#datatype"]=None
        resmap["http://www.w3.org/ns/shacl#property"]=None
        resmap["http://www.w3.org/ns/shacl#deactivated"]=None
        resmap["http://www.w3.org/ns/shacl#description"]=None
        resmap["http://www.w3.org/ns/shacl#name"]=None
        resmap["http://www.w3.org/ns/shacl#group"]=None
        resmap["http://www.w3.org/ns/shacl#pattern"]=None
        f.write("<table><thead><tr><th>Name</th><th>Type</th><th>Target</th><th>Contraints</th></tr></thead><tbody><tr>")
        if type=="http://www.w3.org/ns/shacl#PropertyShape":
            SHACLPage.processPropertyShape(graph,subject,f)
        elif type=="http://www.w3.org/ns/shacl#NodeShape":
            print("TODO NodeShape")
            for predobj in graph.predicate_objects(subject):
                if str(predobj[0])=="http://www.w3.org/ns/shacl#property":
                    SHACLPage.processPropertyShape(graph,predobj[1],f)
        f.write("</tr></tbody></table>")

    @staticmethod
    def generateCollectionWidget(graph,subject,type,templates,f):
        print("CollectionWidget")
        if type=="http://www.w3.org/ns/shacl#PropertyGroup":
            f.write("<table><thead><tr><th>Name</th><th>Type</th><th>Target</th><th>Contraints</th></tr></thead><tbody>")
            for prop in graph.objects(subject, URIRef("http://www.w3.org/ns/shacl#property"), True):
                f.write("<tr>")
                SHACLPage.processPropertyShape(graph,prop,f)
                f.write("</tr>")
            f.write("</tbody></table>")

    @staticmethod
    def generatePageView(templates,g,f):
        print("PageView")