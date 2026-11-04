
import os

from doc.docutils import DocUtils


class PrezExporter:

    @staticmethod
    def generatePrezPages(outpath,deploypath, featurecollectionspaths, prefixnamespace, ogcapi, mergeJSON, contentnegotiation=False):
        os.makedirs(f"{outpath}/prefixes", exist_ok=True)
        os.makedirs(f"{outpath}/search", exist_ok=True)
