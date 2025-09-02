from export.pages.bibpage import BibPage
from export.pages.geometryviewpage import GeometryViewPage
from export.pages.graphviewerpage import GraphViewerPage
from export.pages.lexiconpage import LexiconPage



class PageUtils:

    vocabToPage={}

    classtoPages={}

    pageTypes={"bibpage":BibPage(),"geometry":GeometryViewPage(),"graph":GraphViewerPage(),"lexicon":LexiconPage()}

    widgetConstraints={}

    collectionConstraints={}

    def retrieveCollectionConstraints(self):
        for typ in self.pageTypes:
            try:
                if self.pageTypes[typ]:
                    for const in self.pageTypes[typ].collectionConstraint():
                        self.collectionConstraints[const]=self.pageTypes[typ]
                    for const in self.pageTypes[typ].pageWidgetConstraint():
                        self.widgetConstraints[const]=self.pageTypes[typ]
            except:
                print("PageType Constraints parsing failed")

    def detectCollectionPages(self,subject,predobjs,typeproperty):
        print("Check Eligible pages")
