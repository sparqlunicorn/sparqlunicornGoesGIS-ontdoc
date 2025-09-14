
import os
import json
from pathlib import Path

from doc.docutils import DocUtils


class PrezExporter:

    @staticmethod
    def generatePrezPages(outpath,deploypath, featurecollectionspaths, prefixnamespace, ogcapi, mergeJSON, contentnegotiation=False):
        if not os.path.exists(outpath+"/prefixes"):
            os.mkdir(outpath+"/prefixes")
        if not os.path.exists(outpath+"/search"):
            os.mkdir(outpath+"/search")
