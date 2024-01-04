import os
from ..pages.personpage import PersonPage

class CardDAVExporter:

    def generateCardDAVCollection(outpath, deploypath, graph,license="",version="3"):
        if not os.path.exists(outpath + "/addressbook/"):
            os.makedirs(outpath + "/addressbook/")
        PersonPage().generateCollectionWidget()
