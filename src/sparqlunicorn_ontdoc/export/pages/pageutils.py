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
        for type in self.pageTypes:
            try:
                if self.pageTypes[type]:
                    for const in self.pageTypes[type].collectionConstraint():
                        self.collectionConstraints[const]=self.pageTypes[type]
                    for const in self.pageTypes[type].pageWidgetConstraint():
                        self.widgetConstraints[const]=self.pageTypes[type]
            except:
                print("PageType Constraints parsing failed")

    def detectCollectionPages(self,subject,predobjs,typeproperty):
        print("Check Eligible pages")
