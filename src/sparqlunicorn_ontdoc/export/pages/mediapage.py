

class MediaPage:
    def generatePageWidget(self, graph, templates, subject, f, onlybody=False):
        print("PageWidget")

    def generateCollectionWidget(self, graph, templates, subject, f):
        print("CollectionWidget")

    def generatePageView(self, headertemplate, footertemplate, g, f):
        f.write(str(headertemplate))
        print("PageView")