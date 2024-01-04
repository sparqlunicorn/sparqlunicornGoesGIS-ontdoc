from doc.docconfig import DocConfig


class GraphViewerPage:

    def pageWidgetConstraint(self):
        print("PageWidgetConstraint")
        return []

    def collectionConstraint(self):
        return DocConfig.collectionclasses

    def generatePageWidget(self,graph,subject,f,onlybody=False):
        print("PageWidget")

    def generateCollectionWidget(self,graph,templates,subject,f):
        print("CollectionWidget")

    def generatePageView(self,headertemplate,footertemplate,g,f):
        f.write(str(headertemplate))
        print("PageView")