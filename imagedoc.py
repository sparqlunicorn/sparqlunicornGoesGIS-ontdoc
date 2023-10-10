from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from PIL import Image
import requests
from io import BytesIO

imageproperties=["http://xmlns.com/foaf/0.1/image"]
imageextensions=[".apng",".bmp",".cur",".ico",".jpg",".jpeg",".png",".gif",".tif",".svg","<svg"]
imagetoURI={}
inputfile="test.ttl"

def getImageMetadataFromURL(imgpath):
    height=480
    width=640
    print("Adding image metadata for "+str(imgpath))
    if imgpath not in imagetoURI or "width" not in imagetoURI[imgpath]:
        imagetoURI[imgpath]={}
        try:
            #print("Loading image for "+str(imgpath))
            response = requests.get(imgpath)
            im = Image.open(BytesIO(response.content))
            #print(im.size)
            #print(type(im.size))
            w, h = im.size
            width=w
            height=h
            imagetoURI[imgpath]["width"]=w
            imagetoURI[imgpath]["height"]=h
        except Exception as e:
            imagetoURI[imgpath]["width"]=640
            imagetoURI[imgpath]["height"]=480
    else:
        height=imagetoURI[imgpath]["height"]
        width=imagetoURI[imgpath]["width"]
    print("Found width "+str(width)+" and height "+str(height))
    return {"height":height,"width":width}

lg=Graph()
lg.parse(inputfile)
g=Graph()
for s, p, o in lg:
    #print(str(o))
    if isinstance(o,URIRef) or isinstance(o,Literal):
        if str(o)[o.rfind("."):] in imageextensions:
            res=getImageMetadataFromURL(str(o))
            g.add((URIRef(str(o)),URIRef("http://www.w3.org/2003/12/exif/ns#width"),Literal(res["width"])))
            g.add((URIRef(str(o)),URIRef("http://www.w3.org/2003/12/exif/ns#height"),Literal(res["height"])))
g.serialize("img_metadata.ttl")
lg.parse("img_metadata.ttl")
lg.serialize("test_mod.ttl")

        