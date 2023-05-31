# -*- coding: UTF-8 -*-
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib.plugins.sparql import prepareQuery
from urllib.request import urlopen
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
from pathlib import Path
import shapely.wkt
import shapely.geometry
import os
import re
import shutil
import json
import sys

templatepath=os.path.abspath(os.path.join(os.path.dirname(__file__), "resources/html/"))

version="SPARQLing Unicorn QGIS Plugin OntDoc Script 0.15"

versionurl="https://github.com/sparqlunicorn/sparqlunicornGoesGIS-ontdoc"

bibtextypemappings={"http://purl.org/ontology/bibo/Document":"@misc","http://purl.org/ontology/bibo/Article":"@article","http://purl.org/ontology/bibo/Thesis":"@phdthesis","http://purl.org/ontology/bibo/BookSection":"@inbook","http://purl.org/ontology/bibo/Book":"@book","http://purl.org/ontology/bibo/Proceedings":"@inproceedings"}

labelproperties={
    "http://www.w3.org/2004/02/skos/core#prefLabel":"DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#prefSymbol": "DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#altLabel": "DatatypeProperty",
    "https://schema.org/name": "DatatypeProperty",
    "https://schema.org/alternateName": "DatatypeProperty",
    "http://purl.org/dc/terms/title": "DatatypeProperty",
    "http://purl.org/dc/elements/1.1/title":"DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#altSymbol": "DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#hiddenLabel": "DatatypeProperty",
    "http://www.w3.org/2000/01/rdf-schema#label": "DatatypeProperty"
}

baselayers={
    "OpenStreetMap (OSM)":{"url":"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png","default":True,"type":"tile"}
}

metadatanamespaces=["http://purl.org/dc/terms/","http://purl.org/dc/elements/1.1/","http://www.w3.org/ns/prov#","http://www.w3.org/ns/prov-o/","http://creativecommons.org/ns#","http://www.w3.org/ns/dcat#","http://purl.org/cerif/frapo/","http://www.lido-schema.org/"]

collectionclasses=["http://www.opengis.net/ont/geosparql#FeatureCollection","http://www.opengis.net/ont/geosparql#GeometryCollection","http://www.opengis.net/ont/geosparql#SpatialObjectCollection","http://www.w3.org/2004/02/skos/core#Collection","http://www.w3.org/2004/02/skos/core#OrderedCollection","https://www.w3.org/ns/activitystreams#Collection","https://www.w3.org/ns/activitystreams#OrderedCollection"]

geoliteraltypes=["http://www.opengis.net/ont/geosparql#wktLiteral","http://www.opengis.net/ont/geosparql#gmlLiteral","http://www.opengis.net/ont/geosparql#kmlLiteral","http://www.opengis.net/ont/geosparql#geoJSONLiteral","http://www.opengis.net/ont/geosparql#dggsLiteral"]

timeproperties=["http://www.w3.org/2006/time#inXSDDateTime","http://www.w3.org/2006/time#inXSDDate","http://www.w3.org/2006/time#inXSDDateTimeStamp","http://www.w3.org/2006/time#inXSDgYear","http://www.w3.org/2006/time#inXSDgYearMonth"]

timepointerproperties=["http://www.w3.org/2006/time#hasTime", "http://www.w3.org/2006/time#hasDuration","http://www.w3.org/2006/time#hasBeginning","http://www.w3.org/2006/time#hasEnd"]

timeliteraltypes={"http://www.w3.org/2001/XMLSchema#gYear":"http://www.ontology-of-units-of-measure.org/resource/om-2/year",
"http://www.w3.org/2006/time#generalYear":"http://www.w3.org/2006/time#unitYear",
"http://www.w3.org/2001/XMLSchema#gMonth":"http://www.ontology-of-units-of-measure.org/resource/om-2/month",
"http://www.w3.org/TR/owl-time#generalMonth":"http://www.w3.org/2006/time#unitMonth",
"http://www.w3.org/2001/XMLSchema#gDay":"http://www.ontology-of-units-of-measure.org/resource/om-2/day",
"http://www.w3.org/TR/owl-time#generalDay":"http://www.w3.org/2006/time#unitDay",
"http://www.w3.org/2001/XMLSchema#date":"","http://www.w3.org/2001/XMLSchema#dateTime":""}

collectionrelationproperties={
    "http://www.w3.org/2000/01/rdf-schema#member":"ObjectProperty",
    "http://www.w3.org/2004/02/skos/core#member":"ObjectProperty"
}

invcollectionrelationproperties={
    "https://www.w3.org/ns/activitystreams#partOf":"ObjectProperty"
}

valueproperties={
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#value":"DatatypeProperty",
    "http://www.ontology-of-units-of-measure.org/resource/om-2/hasValue":"ObjectProperty",
    "http://www.opengis.net/ont/crs/usesValue":"ObjectProperty",
    "http://www.ontology-of-units-of-measure.org/resource/om-2/hasNumericalValue":"DatatypeProperty"
}

unitproperties={
    "http://www.ontology-of-units-of-measure.org/resource/om-2/hasUnit":"ObjectProperty",
    "https://www.w3.org/ns/activitystreams#units":"DatatypeProperty"
}

commentproperties={
    "http://www.w3.org/2004/02/skos/core#definition":"DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#note": "DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#scopeNote": "DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#historyNote": "DatatypeProperty",
    "https://schema.org/description":"DatatypeProperty",
    "http://www.w3.org/2000/01/rdf-schema#comment": "DatatypeProperty",
    "http://purl.org/dc/terms/description": "DatatypeProperty",
    "http://purl.org/dc/elements/1.1/description": "DatatypeProperty"
}

geopointerproperties={
    "http://www.opengis.net/ont/geosparql#hasGeometry": "ObjectProperty",
    "http://www.opengis.net/ont/geosparql#hasDefaultGeometry": "ObjectProperty",
    "http://www.w3.org/2003/01/geo/wgs84_pos#geometry": "ObjectProperty",
    "http://www.w3.org/2006/vcard/ns#hasGeo": "ObjectProperty",
    "http://schema.org/geo": "ObjectProperty",
    "https://schema.org/geo": "ObjectProperty",
    "http://geovocab.org/geometry#geometry": "ObjectProperty",
    "http://www.w3.org/ns/locn#geometry": "ObjectProperty",
    "http://rdfs.co/juso/geometry": "ObjectProperty"
}

geolatlonproperties={
   "http://www.w3.org/2003/01/geo/wgs84_pos#lat":"DatatypeProperty",
   "http://www.w3.org/2003/01/geo/wgs84_pos#long": "DatatypeProperty",
   "https://www.w3.org/ns/activitystreams#latitude": "DatatypeProperty",
   "https://www.w3.org/ns/activitystreams#longitude": "DatatypeProperty",
   "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude": "DatatypeProperty",
   "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude": "DatatypeProperty",
   "http://schema.org/longitude": "DatatypeProperty",
   "https://schema.org/longitude": "DatatypeProperty",
   "http://schema.org/latitude": "DatatypeProperty",
   "https://schema.org/latitude": "DatatypeProperty",
}

geopairproperties={
    "http://schema.org/longitude":{"type":"DatatypeProperty","pair":"http://schema.org/latitude","islong":False},
    "http://schema.org/latitude": {"type": "DatatypeProperty", "pair": "http://schema.org/longitude","islong":True},
    "https://schema.org/longitude": {"type": "DatatypeProperty", "pair": "https://schema.org/latitude","islong":False},
    "https://schema.org/latitude": {"type": "DatatypeProperty", "pair": "https://schema.org/longitude","islong":True},
    "http://www.w3.org/2003/01/geo/wgs84_pos#lat": {"type": "DatatypeProperty", "pair": "http://www.w3.org/2003/01/geo/wgs84_pos#long","islong":True},
    "http://www.w3.org/2003/01/geo/wgs84_pos#long": {"type": "DatatypeProperty", "pair": "http://www.w3.org/2003/01/geo/wgs84_pos#lat","islong":False},
    "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude": {"type": "DatatypeProperty", "pair": "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude","islong": False},
    "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude": {"type": "DatatypeProperty", "pair": "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude","islong": True}
}


geoproperties={
   "http://www.opengis.net/ont/geosparql#asWKT":"DatatypeProperty",
   "http://www.opengis.net/ont/geosparql#asGML": "DatatypeProperty",
   "http://www.opengis.net/ont/geosparql#asKML": "DatatypeProperty",
   "http://www.opengis.net/ont/geosparql#asGeoJSON": "DatatypeProperty",
   "http://www.opengis.net/ont/geosparql#hasGeometry": "ObjectProperty",
   "http://www.opengis.net/ont/geosparql#hasDefaultGeometry": "ObjectProperty",
   "http://www.w3.org/2003/01/geo/wgs84_pos#geometry": "ObjectProperty",
   "http://www.georss.org/georss/point": "DatatypeProperty",
   "http://www.w3.org/2006/vcard/ns#hasGeo": "ObjectProperty",
   "http://schema.org/geo": "ObjectProperty",
   "https://schema.org/geo": "ObjectProperty",
   "http://purl.org/dc/terms/coverage":"DatatypeProperty",
   "http://purl.org/dc/terms/spatial":"DatatypeProperty",
   "http://schema.org/polygon": "DatatypeProperty",
   "https://schema.org/polygon": "DatatypeProperty",
   "http://geovocab.org/geometry#geometry": "ObjectProperty",
   "http://www.w3.org/ns/locn#geometry": "ObjectProperty",
   "http://rdfs.co/juso/geometry": "ObjectProperty",
   "http://www.wikidata.org/prop/direct/P625":"DatatypeProperty",
   "https://database.factgrid.de/prop/direct/P48": "DatatypeProperty",
   "http://database.factgrid.de/prop/direct/P48":"DatatypeProperty",
   "http://www.wikidata.org/prop/direct/P3896": "DatatypeProperty"
}

imageextensions=[".apng",".bmp",".cur",".ico",".jpg",".jpeg",".png",".gif",".tif",".svg","<svg"]

meshextensions=[".ply",".nxs",".nxz"]

videoextensions=[".avi",".mp4",".ogv"]

audioextensions=[".aac",".mp3",".mkv",".ogg",".opus",".wav"]

fileextensionmap={
    ".apng":"image",
    ".bmp":"image",
    ".cur":"image",
    ".ico":"image",
    ".jpg":"image",
    ".jpeg":"image",
    ".png":"image",
    ".gif":"image",
    ".tif":"image",
    ".svg":"image",
    "<svg":"image",
    ".ply":"mesh",
    ".nxs":"mesh",
    ".nxz":"mesh",
    ".avi":"video",
    ".mp4":"video",
    ".ogv":"video",
    ".aac":"audio",
    ".mp3":"audio",
    ".mkv":"audio",
    ".ogg":"audio",
    ".opus":"audio",
    ".wav":"audio"
}


startscripts = """var namespaces={"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","xsd":"http://www.w3.org/2001/XMLSchema#","geo":"http://www.opengis.net/ont/geosparql#","rdfs":"http://www.w3.org/2000/01/rdf-schema#","owl":"http://www.w3.org/2002/07/owl#","dc":"http://purl.org/dc/terms/","skos":"http://www.w3.org/2004/02/skos/core#"}
var annotationnamespaces=["http://www.w3.org/2004/02/skos/core#","http://www.w3.org/2000/01/rdf-schema#","http://purl.org/dc/terms/"]
var indexpage=false
var geoproperties={
                   "http://www.opengis.net/ont/geosparql#asWKT":"DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#asGML": "DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#asKML": "DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#asGeoJSON": "DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#hasGeometry": "ObjectProperty",
                   "http://www.opengis.net/ont/geosparql#hasDefaultGeometry": "ObjectProperty",
                   "http://www.w3.org/2003/01/geo/wgs84_pos#geometry": "ObjectProperty",
                   "http://www.georss.org/georss/point": "DatatypeProperty",
                   "http://www.w3.org/2006/vcard/ns#hasGeo": "ObjectProperty",
                   "http://www.w3.org/2003/01/geo/wgs84_pos#lat":"DatatypeProperty",
                   "http://www.w3.org/2003/01/geo/wgs84_pos#long": "DatatypeProperty",
                   "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude": "DatatypeProperty",
                   "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude": "DatatypeProperty",
                   "http://schema.org/geo": "ObjectProperty",
                   "http://schema.org/polygon": "DatatypeProperty",
                   "https://schema.org/geo": "ObjectProperty",
                   "https://schema.org/polygon": "DatatypeProperty",
                   "http://geovocab.org/geometry#geometry": "ObjectProperty",
                   "http://www.w3.org/ns/locn#geometry": "ObjectProperty",
                   "http://rdfs.co/juso/geometry": "ObjectProperty",
                   "http://www.wikidata.org/prop/direct/P625":"DatatypeProperty",
                   "https://database.factgrid.de/prop/direct/P48": "DatatypeProperty",
                   "http://database.factgrid.de/prop/direct/P48":"DatatypeProperty",
                   "http://www.wikidata.org/prop/direct/P3896": "DatatypeProperty"
}

commentproperties={
    "http://www.w3.org/2004/02/skos/core#definition":"DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#note": "DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#scopeNote": "DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#historyNote": "DatatypeProperty",
    "https://schema.org/description":"DatatypeProperty",
    "http://www.w3.org/2000/01/rdf-schema#comment": "DatatypeProperty",
    "http://purl.org/dc/terms/description": "DatatypeProperty",
    "http://purl.org/dc/elements/1.1/description": "DatatypeProperty"
}

labelproperties={
    "http://www.w3.org/2004/02/skos/core#prefLabel":"DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#prefSymbol": "DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#altLabel": "DatatypeProperty",
    "https://schema.org/name": "DatatypeProperty",
    "https://schema.org/alternateName": "DatatypeProperty",
    "http://purl.org/dc/terms/title": "DatatypeProperty",
    "http://purl.org/dc/elements/1.1/title":"DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#altSymbol": "DatatypeProperty",
    "http://www.w3.org/2004/02/skos/core#hiddenLabel": "DatatypeProperty",
    "http://www.w3.org/2000/01/rdf-schema#label": "DatatypeProperty"
}

var baseurl="{{baseurl}}"
  $( function() {
    var availableTags = Object.keys(search)
    $( "#search" ).autocomplete({
      source: availableTags
    });
    console.log(availableTags)
    setupJSTree()
  } );

function openNav() {
  document.getElementById("mySidenav").style.width = "400px";
}

function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
}

function exportGeoJSON(){
    if(typeof(feature) !== "undefined"){
        saveTextAsFile(JSON.stringify(feature),"geojson")
    }
}

function parseWKTStringToJSON(wktstring){
    wktstring=wktstring.substring(wktstring.lastIndexOf('(')+1,wktstring.lastIndexOf(')')-1)
    resjson=[]
    for(coordset of wktstring.split(",")){
        curobject={}
        coords=coordset.trim().split(" ")
        console.log(coordset)
        console.log(coords)
        if(coords.length==3){
            resjson.push({"x":parseFloat(coords[0]),"y":parseFloat(coords[1]),"z":parseFloat(coords[2])})
        }else{
            resjson.push({"x":parseFloat(coords[0]),"y":parseFloat(coords[1])})
        }
    }
    console.log(resjson)
    return resjson
}

function exportCSV(){
    rescsv=""
    if(typeof(feature)!=="undefined"){
        if("features" in feature){
           for(feat of feature["features"]){
                rescsv+="\\""+feat["geometry"]["type"].toUpperCase()+"("
                feat["geometry"].coordinates.forEach(function(p,i){
                //	console.log(p)
                    if(i<feat["geometry"].coordinates.length-1)rescsv =  rescsv + p[0] + ' ' + p[1] + ', ';
                    else rescsv =  rescsv + p[0] + ' ' + p[1] + ')';
                })
                rescsv+=")\\","
                if("properties" in feat){
                    if(gottitle==false){
                       rescsvtitle="\\"the_geom\\","
                       for(prop in feat["properties"]){
                          rescsvtitle+="\\""+prop+"\\","
                       }
                       rescsvtitle+="\\\\n"
                       rescsv=rescsvtitle+rescsv
                       gottitle=true
                    }
                    for(prop in feat["properties"]){
                        rescsv+="\\""+feat["properties"][prop]+"\\","
                    }
                }
                rescsv+="\\\\n"
           }
        }else{
            gottitle=false
            rescsv+="\\""+feature["geometry"]["type"].toUpperCase()+"("
            feature["geometry"].coordinates.forEach(function(p,i){
            //	console.log(p)
                if(i<feature["geometry"].coordinates.length-1)rescsv =  rescsv + p[0] + ' ' + p[1] + ', ';
                else rescsv =  rescsv + p[0] + ' ' + p[1] + ')';
            })
            rescsv+=")\\","
            if("properties" in feature){
                if(gottitle==false){
                   rescsvtitle=""
                   for(prop in feature["properties"]){
                      rescsvtitle+="\\""+prop+"\\","
                   }
                   rescsvtitle+="\\\\n"
                   rescsv=rescsvtitle+rescsv
                   gottitle=true
                }
                for(prop in feature["properties"]){
                    rescsv+="\\""+feature["properties"][prop]+"\\","
                }
            }
        }
        saveTextAsFile(rescsv,".csv")
    }else if(typeof(nongeofeature)!=="undefined"){
        if("features" in nongeofeature){
           for(feat of nongeofeature["features"]){
                if("properties" in feat){
                    if(gottitle==false){
                       rescsvtitle="\\"the_geom\\","
                       for(prop in feat["properties"]){
                          rescsvtitle+="\\""+prop+"\\","
                       }
                       rescsvtitle+="\\\\n"
                       rescsv=rescsvtitle+rescsv
                       gottitle=true
                    }
                    for(prop in feat["properties"]){
                        rescsv+="\\""+feat["properties"][prop]+"\\","
                    }
                }
                rescsv+="\\\\n"
           }
        }else{
            gottitle=false
            if("properties" in nongeofeature){
                if(gottitle==false){
                   rescsvtitle=""
                   for(prop in nongeofeature["properties"]){
                      rescsvtitle+="\\""+prop+"\\","
                   }
                   rescsvtitle+="\\\\n"
                   rescsv=rescsvtitle+rescsv
                   gottitle=true
                }
                for(prop in nongeofeature["properties"]){
                    rescsv+="\\""+nongeofeature["properties"][prop]+"\\","
                }
            }
        }
        saveTextAsFile(rescsv,".csv")
    }
}

function setSVGDimensions(){
    $('svg').each(function(i, obj) {
        console.log(obj)
        console.log($(obj).children().first()[0])
        if($(obj).attr("viewBox") || $(obj).attr("width") || $(obj).attr("height")){
            return
        }
        maxx=Number.MIN_VALUE
        maxy=Number.MIN_VALUE
        minx=Number.MAX_VALUE
        miny=Number.MAX_VALUE
        $(obj).children().each(function(i){
            svgbbox=$(this)[0].getBBox()
            console.log(svgbbox)
            if(svgbbox.x+svgbbox.width>maxx){
                maxx=svgbbox.x+svgbbox.width
            }
            if(svgbbox.y+svgbbox.height>maxy){
                maxy=svgbbox.y+svgbbox.height
            }
            if(svgbbox.y<miny){
                miny=svgbbox.y
            }
            if(svgbbox.x<minx){
                minx=svgbbox.x
            }
        });
        console.log(""+(minx)+" "+(miny-(maxy-miny))+" "+((maxx-minx)+25)+" "+((maxy-miny)+25))
        newviewport=""+((minx))+" "+(miny)+" "+((maxx-minx)+25)+" "+((maxy-miny)+25)
        $(obj).attr("viewBox",newviewport)
        $(obj).attr("width",((maxx-minx))+10)
        $(obj).attr("height",((maxy-miny)+10))
        console.log($(obj).hasClass("svgoverlay"))
        if($(obj).hasClass("svgoverlay")){
            naturalWidth=$(obj).prev().children('img')[0].naturalWidth
            naturalHeight=$(obj).prev().children('img')[0].naturalHeight
            currentWidth=$(obj).prev().children('img')[0].width
            currentHeight=$(obj).prev().children('img')[0].height
            console.log(naturalWidth+" - "+naturalHeight+" - "+currentWidth+" - "+currentHeight)
            overlayposX = (currentWidth/naturalWidth) * minx;
            overlayposY = (currentHeight/naturalHeight) * miny;
            overlayposWidth = ((currentWidth/naturalWidth) * maxx)-overlayposX;
            overlayposHeight = ((currentHeight/naturalHeight) * maxy)-overlayposY;
            console.log(overlayposX+" - "+overlayposY+" - "+overlayposHeight+" - "+overlayposWidth)
            $(obj).css({top: overlayposY+"px", left:overlayposX+"px", position:"absolute"})
            $(obj).attr("height",overlayposHeight)
            $(obj).attr("width",overlayposWidth)
        }
    });
}



function exportWKT(){
    if(typeof(feature)!=="undefined"){
        reswkt=""
        if("features" in feature){
            for(feat of feature["features"]){
                reswkt+=feat["geometry"]["type"].toUpperCase()+"("
                feat["geometry"].coordinates.forEach(function(p,i){
                //	console.log(p)
                    if(i<feat["geometry"].coordinates.length-1)reswkt =  reswkt + p[0] + ' ' + p[1] + ', ';
                    else reswkt =  reswkt + p[0] + ' ' + p[1] + ')';
                })
                reswkt+=")\\\\n"
            }
        }else{
                reswkt+=feature["geometry"]["type"].toUpperCase()+"("
                feature["geometry"].coordinates.forEach(function(p,i){
                    if(i<feature["geometry"].coordinates.length-1)reswkt =  reswkt + p[0] + ' ' + p[1] + ', ';
                    else reswkt =  reswkt + p[0] + ' ' + p[1] + ')';
                })
                reswkt+=")\\\\n"
        }
        saveTextAsFile(reswkt,".wkt")
    }
}

function downloadFile(filePath){
    var link=document.createElement('a');
    link.href = filePath;
    link.download = filePath.substr(filePath.lastIndexOf('/') + 1);
    link.click();
}

function saveTextAsFile(tosave,fileext){
    var a = document.createElement('a');
    a.style = "display: none";
    var blob= new Blob([tosave], {type:'text/plain'});
    var url = window.URL.createObjectURL(blob);
    var filename = "res."+fileext;
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function(){
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }, 1000);
}

function download(){
    format=$('#format').val()
    if(format=="geojson"){
        exportGeoJSON()
    }else if(format=="ttl"){
        downloadFile("index.ttl")
    }else if(format=="json"){
        downloadFile("index.json")
    }else if(format=="wkt"){
        exportWKT()
    }else if(format=="csv"){
        exportCSV()
    }
}

function rewriteLink(thelink){
    if(thelink==null){
        rest=search[document.getElementById('search').value].replace(baseurl,"")
    }else{
        curlocpath=window.location.href.replace(baseurl,"")
        rest=thelink.replace(baseurl,"")
    }
    if(!(rest.endsWith("/"))){
        rest+="/"
    }
    count=0
    if(!indexpage){
        count=rest.split("/").length-1
    }
    console.log(count)
    counter=0
    if (typeof relativedepth !== 'undefined'){
        while(counter<relativedepth){
            rest="../"+rest
            counter+=1
        }
    }else{
        while(counter<count){
            rest="../"+rest
            counter+=1
        }
    }
    rest+="index.html"
    console.log(rest)
    return rest
}

function followLink(thelink=null){
    rest=rewriteLink(thelink)
    location.href=rest
}

function changeDefLink(){
	$('#formatlink').attr('href',definitionlinks[$('#format').val()]);
}

function changeDefLink2(){
	$('#formatlink2').attr('href',definitionlinks[$('#format2').val()]);
}

var definitionlinks={
"covjson":"https://covjson.org",
"csv":"https://tools.ietf.org/html/rfc4180",
"cipher":"https://neo4j.com/docs/cypher-manual/current/",
"esrijson":"https://doc.arcgis.com/de/iot/ingest/esrijson.htm",
"geohash":"http://geohash.org",
"json":"https://geojson.org",
"gdf":"https://www.cs.nmsu.edu/~joemsong/software/ChiNet/GDF.pdf",
"geojsonld":"http://geojson.org/geojson-ld/",
"geojsonseq":"https://tools.ietf.org/html/rfc8142",
"geouri":"https://tools.ietf.org/html/rfc5870",
"gexf":"https://gephi.org/gexf/format/",
"gml":"https://www.ogc.org/standards/gml",
"gml2":"https://gephi.org/users/supported-graph-formats/gml-format/",
"gpx":"https://www.topografix.com/gpx.asp",
"graphml":"http://graphml.graphdrawing.org",
"gxl":"http://www.gupro.de/GXL/Introduction/intro.html",
"hdt":"https://www.w3.org/Submission/2011/03/",
"hextuples":"https://github.com/ontola/hextuples",
"html":"https://html.spec.whatwg.org",
"jsonld":"https://json-ld.org",
"jsonn":"",
"jsonp":"http://jsonp.eu",
"jsonseq":"https://tools.ietf.org/html/rfc7464",
"kml":"https://www.ogc.org/standards/kml",
"latlon":"",
"mapml":"https://maps4html.org/MapML/spec/",
"mvt":"https://docs.mapbox.com/vector-tiles/reference/",
"n3":"https://www.w3.org/TeamSubmission/n3/",
"nq":"https://www.w3.org/TR/n-quads/",
"nt":"https://www.w3.org/TR/n-triples/",
"olc":"https://github.com/google/open-location-code/blob/master/docs/specification.md",
"osm":"https://wiki.openstreetmap.org/wiki/OSM_XML",
"osmlink":"",
"rdfxml":"https://www.w3.org/TR/rdf-syntax-grammar/",
"rdfjson":"https://www.w3.org/TR/rdf-json/",
"rt":"https://afs.github.io/rdf-thrift/rdf-binary-thrift.html",
"svg":"https://www.w3.org/TR/SVG11/",
"tgf":"https://docs.yworks.com/yfiles/doc/developers-guide/tgf.html",
"tlp":"https://tulip.labri.fr/TulipDrupal/?q=tlp-file-format",
"trig":"https://www.w3.org/TR/trig/",
"trix":"https://www.hpl.hp.com/techreports/2004/HPL-2004-56.html",
"ttl":"https://www.w3.org/TR/turtle/",
"wkb":"https://www.iso.org/standard/40114.html",
"wkt":"https://www.iso.org/standard/40114.html",
"xls":"http://www.openoffice.org/sc/excelfileformat.pdf",
"xlsx":"http://www.openoffice.org/sc/excelfileformat.pdf",
"xyz":"https://gdal.org/drivers/raster/xyz.html",
"yaml":"https://yaml.org"
}

function shortenURI(uri){
	prefix=""
	if(typeof(uri)!="undefined"){
		for(namespace in namespaces){
			if(uri.includes(namespaces[namespace])){
				prefix=namespace+":"
				break
			}
		}
	}
	if(typeof(uri)!= "undefined" && uri.includes("#")){
		return prefix+uri.substring(uri.lastIndexOf('#')+1)
	}
	if(typeof(uri)!= "undefined" && uri.includes("/")){
		return prefix+uri.substring(uri.lastIndexOf("/")+1)
	}
	return uri
}

var presenter = null;
function setup3dhop(meshurl,meshformat) {
  presenter = new Presenter("draw-canvas");
  presenter.setScene({
    meshes: {
			"mesh_1" : { url: meshurl}
		},
		modelInstances : {
			"model_1" : {
				mesh  : "mesh_1",
				color : [0.8, 0.7, 0.75]
			}
		}
  });
}

function start3dhop(meshurl,meshformat){
    init3dhop();
	setup3dhop(meshurl,meshformat);
	resizeCanvas(640,480);
  	moveToolbar(20,20);
}


let camera, scene, renderer,controls;

function viewGeometry(geometry) {
  const material = new THREE.MeshPhongMaterial({
    color: 0xffffff,
    flatShading: true,
    vertexColors: THREE.VertexColors,
    wireframe: false
  });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
}

function initThreeJS(domelement,verts,meshurls) {
    scene = new THREE.Scene();
    minz=Number.MAX_VALUE
    maxz=Number.MIN_VALUE
    miny=Number.MAX_VALUE
    maxy=Number.MIN_VALUE
    minx=Number.MAX_VALUE
    maxx=Number.MIN_VALUE
	vertarray=[]
    console.log(verts)
    var svgShape = new THREE.Shape();
    first=true
    for(vert of verts){
        if(first){
            svgShape.moveTo(vert["x"], vert["y"]);
           first=false
        }else{
            svgShape.lineTo(vert["x"], vert["y"]);
        }
        vertarray.push(vert["x"])
        vertarray.push(vert["y"])
        vertarray.push(vert["z"])
        if(vert["z"]>maxz){
            maxz=vert["z"]
        }
        if(vert["z"]<minz){
            minz=vert["z"]
        }
        if(vert["y"]>maxy){
            maxy=vert["y"]
        }
        if(vert["y"]<miny){
            miny=vert["y"]
        }
        if(vert["x"]>maxx){
            maxy=vert["x"]
        }
        if(vert["x"]<minx){
            miny=vert["x"]
        }
    }
    if(meshurls.length>0){
        var loader = new THREE.PLYLoader();
        loader.load(meshurls[0], viewGeometry);
    }
    camera = new THREE.PerspectiveCamera(90,window.innerWidth / window.innerHeight, 0.1, 150 );
    scene.add(new THREE.AmbientLight(0x222222));
    var light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(20, 20, 0);
    scene.add(light);
    var axesHelper = new THREE.AxesHelper( Math.max(maxx, maxy, maxz)*4 );
    scene.add( axesHelper );
    console.log("Depth: "+(maxz-minz))
    var extrudedGeometry = new THREE.ExtrudeGeometry(svgShape, {depth: maxz-minz, bevelEnabled: false});
    extrudedGeometry.computeBoundingBox()
    centervec=new THREE.Vector3()
    extrudedGeometry.boundingBox.getCenter(centervec)
    console.log(centervec)
    const material = new THREE.MeshBasicMaterial( { color: 0xFFFFFF, wireframe:true } );
    const mesh = new THREE.Mesh( extrudedGeometry, material );
    scene.add( mesh );
    renderer = new THREE.WebGLRenderer( { antialias: false } );
	renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( 480, 500 );
    document.getElementById(domelement).appendChild( renderer.domElement );
	controls = new THREE.OrbitControls( camera, renderer.domElement );
    controls.target.set( centervec.x,centervec.y,centervec.z );
    camera.position.x= centervec.x
    camera.position.y= centervec.y
    camera.position.z = centervec.z+10;
    controls.maxDistance= Math.max(maxx, maxy, maxz)*5
    controls.update();
    animate()
}

function animate() {
    requestAnimationFrame( animate );
    controls.update();
    renderer.render( scene, camera );
}

function getTextAnnoContext(){
$('span.textanno').each(function(i, obj) {
    startindex=$(obj).attr("start").val()
    endindex=$(obj).attr("end").val()
    exact=$(obj).attr("exact").val()
    if($(obj).attr("src")){
        source=$(obj).attr("src").val()
        $.get( source, function( data ) {
            markarea=data.substring(start,end)
            counter=0
            startindex=0
            endindex=data.indexOf("\\\\n",end)
            for(line in data.split("\\\\n")){
                counter+=line.length
                if(counter>start){
                    startindex=counter-line.length
                    break
                }
            }
            $(obj).html(data.substring(startindex,endindex)+"</span>".replace(markarea,"<mark>"+markarea+"</mark>"))
        });
    }
  });
}

function labelFromURI(uri,label){
        if(uri.includes("#")){
        	prefix=uri.substring(0,uri.lastIndexOf('#')-1)
        	if(label!=null){
        		return label+" ("+prefix.substring(prefix.lastIndexOf("/")+1)+":"+uri.substring(uri.lastIndexOf('#')+1)+")"

        	}else{
				return uri.substring(uri.lastIndexOf('#')+1)+" ("+prefix.substring(uri.lastIndexOf("/")+1)+":"+uri.substring(uri.lastIndexOf('#')+1)+")"
        	}
       	}
        if(uri.includes("/")){
            prefix=uri.substring(0,uri.lastIndexOf('/')-1)
            if(label!=null){
            	return label+" ("+prefix.substring(prefix.lastIndexOf("/")+1)+":"+uri.substring(uri.lastIndexOf('/')+1)+")"
            }else{
        		return uri.substring(uri.lastIndexOf('/')+1)+" ("+prefix.substring(uri.lastIndexOf("/")+1)+":"+uri.substring(uri.lastIndexOf('/')+1)+")"
            }
       	}
        return uri
}

function formatHTMLTableForPropertyRelations(propuri,result,propicon){
    dialogcontent="<h3><img src=\\""+propicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+propuri.replace('/index.json','/index.html')+"\\" target=\\"_blank\\"> "+shortenURI(propuri)+"</a></h3><table border=1 id=classrelationstable><thead><tr><th>Incoming Concept</th><th>Relation</th><th>Outgoing Concept</th></tr></thead><tbody>"
    console.log(result)
    for(instance in result["from"]){
//
            if(result["from"][instance]=="instancecount"){
                continue;
            }
            dialogcontent+="<tr><td><img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+result["from"][instance]+"\\" target=\\"_blank\\">"+shortenURI(result["from"][instance])+"</a></td>"
            dialogcontent+="<td><img src=\\""+propicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+propuri+"\\" target=\\"_blank\\">"+shortenURI(propuri)+"</a></td><td></td></tr>"
       // }
    }
    for(instance in result["to"]){
        //for(instance in result["to"][res]){
            if(result["to"][instance]=="instancecount"){
                continue;
            }
            dialogcontent+="<tr><td></td><td><img src=\\""+propicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+propuri+"\\" target=\\"_blank\\">"+shortenURI(propuri)+"</a></td>"
            dialogcontent+="<td><img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+result["to"][instance]+"\\" target=\\"_blank\\">"+shortenURI(result["to"][instance])+"</a></td></tr>"
       // }
    }
    dialogcontent+="</tbody></table>"
    dialogcontent+="<button style=\\"float:right\\" id=\\"closebutton\\" onclick='document.getElementById(\\"classrelationdialog\\").close()'>Close</button>"
    return dialogcontent
}

function determineTableCellLogo(uri){
    result="<td><a href=\\""+uri+"\\" target=\\"_blank\\">"
    logourl=""
    finished=false
    if(uri in labelproperties){
        result+="<img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/labelannotationproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Label Property\\"/>"
        logourl="https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/labelannotationproperty.png"
        finished=true
    }
    if(!finished){
        for(ns in annotationnamespaces){
            if(uri.includes(annotationnamespaces[ns])){
                result+="<img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/annotationproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Annotation Property\\"/>"
                logourl="https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/annotationproperty.png"
                finished=true
            }
        }
    }
    if(!finished && uri in geoproperties && geoproperties[uri]=="ObjectProperty"){
        result+="<img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoobjectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Geo Object Property\\"/>"
        logourl="https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoobjectproperty.png"
    }else if(!finished && uri in geoproperties && geoproperties[uri]=="DatatypeProperty"){
        result+="<img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geodatatypeproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Geo Datatype Property\\"/>"
        logourl="https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geodatatypeproperty.png"
    }else if(!finished){
        result+="<img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/objectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Object Property\\"/>"
        logourl="https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/objectproperty.png"
    }
    result+=shortenURI(uri)+"</a></td>"
    return [result,logourl]
}

function formatHTMLTableForClassRelations(result,nodeicon,nodelabel,nodeid){
    dialogcontent=""
    if(nodelabel.includes("[")){
        nodelabel=nodelabel.substring(0,nodelabel.lastIndexOf("[")-1)
    }
    dialogcontent="<h3><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid.replace('/index.json','/index.html')+"\\" target=\\"_blank\\"> "+nodelabel+"</a></h3><table border=1 id=classrelationstable><thead><tr><th>Incoming Concept</th><th>Incoming Relation</th><th>Concept</th><th>Outgoing Relation</th><th>Outgoing Concept</th></tr></thead><tbody>"
    for(res in result["from"]){
        for(instance in result["from"][res]){
            if(instance=="instancecount"){
                continue;
            }
            dialogcontent+="<tr><td><img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+instance+"\\" target=\\"_blank\\">"+shortenURI(instance)+"</a></td>"
            dialogcontent+=determineTableCellLogo(res)[0]
            dialogcontent+="<td><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid+"\\" target=\\"_blank\\">"+nodelabel+"</a></td><td></td><td></td></tr>"
        }
    }
    for(res in result["to"]){
        for(instance in result["to"][res]){
            if(instance=="instancecount"){
                continue;
            }
            dialogcontent+="<tr><td></td><td></td><td><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid+"\\" target=\\"_blank\\">"+nodelabel+"</a></td>"
            dialogcontent+=determineTableCellLogo(res)[0]
            dialogcontent+="<td><img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+instance+"\\" target=\\"_blank\\">"+shortenURI(instance)+"</a></td></tr>"
        }
    }
    dialogcontent+="</tbody></table>"
    dialogcontent+="<button style=\\"float:right\\" id=\\"closebutton\\" onclick='document.getElementById(\\"classrelationdialog\\").close()'>Close</button>"
    return dialogcontent
}

function formatHTMLTableForResult(result,nodeicon){
    dialogcontent=""
    dialogcontent="<h3><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid.replace('/index.json','/index.html')+"\\" target=\\"_blank\\"> "+nodelabel+"</a></h3><table border=1 id=dataschematable><thead><tr><th>Type</th><th>Relation</th><th>Value</th></tr></thead><tbody>"
    for(res in result){
        console.log(result)
        console.log(result[res])
        console.log(result[res].size)
        dialogcontent+="<tr>"
        detpropicon=""
        if(res in geoproperties && geoproperties[res]=="ObjectProperty"){
            dialogcontent+="<td><img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoobjectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Geo Object Property\\"/>Geo Object Property</td>"
            detpropicon="https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoobjectproperty.png"
        }else if((result[res][0]+"").startsWith("http")){
            dialogcontent+="<td><img src=\\"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/objectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Object Property\\"/>Object Property</td>"
            detpropicon="https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/objectproperty.png"
        }else{
            finished=false
            ress=determineTableCellLogo(res)
            dialogcontent+=ress[0]
            detpropicon=ress[1]
        }
        dialogcontent+="<td><a href=\\""+res+"\\" target=\\"_blank\\">"+shortenURI(res)+"</a> <a href=\\"#\\" onclick=\\"getPropRelationDialog('"+res+"','"+detpropicon+"')\\">[x]</a></td>"
        if(Object.keys(result[res]).length>1){
            dialogcontent+="<td><ul>"
            for(resitem in result[res]){
                if((resitem+"").startsWith("http")){
                    dialogcontent+="<li><a href=\\""+rewriteLink(resitem)+"\\" target=\\"_blank\\">"+shortenURI(resitem)+"</a> ["+result[res][resitem]+"]</li>"
                }else if(resitem!="instancecount"){
                    dialogcontent+="<li>"+resitem+"</li>"
                }
            }
            dialogcontent+="</ul></td>"
        }else if((Object.keys(result[res])[0]+"").startsWith("http")){
            dialogcontent+="<td><a href=\\""+rewriteLink(Object.keys(result[res])[0]+"")+"\\" target=\\"_blank\\">"+shortenURI(Object.keys(result[res])[0]+"")+"</a></td>"
        }else if(Object.keys(result[res])[0]!="instancecount"){
            dialogcontent+="<td>"+Object.keys(result[res])[0]+"</td>"
        }else{
            dialogcontent+="<td></td>"
        }
        dialogcontent+="</tr>"
    }
    dialogcontent+="</tbody></table>"
    dialogcontent+="<button style=\\"float:right\\" id=\\"closebutton\\" onclick='document.getElementById(\\"dataschemadialog\\").close()'>Close</button>"
    return dialogcontent
}

function getClassRelationDialog(node){
     nodeid=rewriteLink(node.id).replace(".html",".json")
     nodelabel=node.text
     nodetype=node.type
     nodeicon=node.icon
     props={}
     if("data" in node){
        props=node.data
     }
     console.log(nodetype)
     if(nodetype=="class" || nodetype=="geoclass" || nodetype=="collectionclass" || nodetype=="halfgeoclass"){
        console.log(props)
        dialogcontent=formatHTMLTableForClassRelations(props,nodeicon,nodelabel,nodeid)
        document.getElementById("classrelationdialog").innerHTML=dialogcontent
        $('#classrelationstable').DataTable();
        document.getElementById("classrelationdialog").showModal();
     }
}

function getPropRelationDialog(propuri,propicon){
     dialogcontent=formatHTMLTableForPropertyRelations(propuri,proprelations[propuri],propicon)
     console.log(dialogcontent)
     document.getElementById("classrelationdialog").innerHTML=dialogcontent
     $('#classrelationstable').DataTable();
     document.getElementById("classrelationdialog").showModal();
}

function getDataSchemaDialog(node){
     nodeid=rewriteLink(node.id).replace(".html",".json")
     nodelabel=node.text
     nodetype=node.type
     nodeicon=node.icon
     props={}
     if("data" in node){
        props=node.data
     }
     console.log(nodetype)
     if(nodetype=="class" || nodetype=="halfgeoclass" || nodetype=="geoclass" || node.type=="collectionclass"){
        console.log(props)
        dialogcontent=formatHTMLTableForResult(props["to"],nodeicon)
        document.getElementById("dataschemadialog").innerHTML=dialogcontent
        $('#dataschematable').DataTable();
        document.getElementById("dataschemadialog").showModal();
     }else{
         $.getJSON(nodeid, function(result){
            dialogcontent=formatHTMLTableForResult(result,nodeicon)
            document.getElementById("dataschemadialog").innerHTML=dialogcontent
            $('#dataschematable').DataTable();
            document.getElementById("dataschemadialog").showModal();
          });
    }
}

function setupJSTree(){
    console.log("setupJSTree")
    tree["contextmenu"]={}
    tree["core"]["check_callback"]=true
    tree["sort"]=function(a, b) {
        a1 = this.get_node(a);
        b1 = this.get_node(b);
        if (a1.icon == b1.icon){
            return (a1.text > b1.text) ? 1 : -1;
        } else {
            return (a1.icon > b1.icon) ? 1 : -1;
        }
    }
    /*for(typee in tree["types"]){
        if("icon" in tree["types"][typee]){
            tree["types"][typee]["icon"]=tree["types"][typee]["icon"].replace("https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/",baseurl+"icons/")
        }
    }
    console.log(tree["types"])
    */
    tree["contextmenu"]["items"]=function (node) {
        nodetype=node.type
        thelinkpart="class"
        if(nodetype=="instance" || nodetype=="geoinstance"){
            thelinkpart="instance"
        }
        contextmenu={
            "lookupdefinition": {
                "separator_before": false,
                "separator_after": false,
                "label": "Lookup definition",
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/searchclass.png",
                "action": function (obj) {
                    newlink=rewriteLink(node.id)
                    var win = window.open(newlink, '_blank');
                    win.focus();
                }
            },
            "copyuriclipboard":{
                "separator_before": false,
                "separator_after": false,
                "label": "Copy URI to clipboard",
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/"+thelinkpart+"link.png",
                "action":function(obj){
                    copyText=node.id
                    navigator.clipboard.writeText(copyText);
                }
            },
            "discoverrelations":{
                "separator_before": false,
                "separator_after": false,
                "label": "Discover "+node.type+" relations",
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/"+thelinkpart+"link.png",
                "action":function(obj){
                    console.log("class relations")
                    if(node.type=="class" || node.type=="geoclass" || node.type=="collectionclass"){
                        getClassRelationDialog(node)
                    }
                }
            },
            "loaddataschema": {
                "separator_before": false,
                "separator_after": false,
                "icon":"https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/"+node.type+"schema.png",
                "label": "Load dataschema for "+node.type,
                "action": function (obj) {
                    console.log(node)
                    console.log(node.id)
                    console.log(baseurl)
                    if(node.id.includes(baseurl)){
                        getDataSchemaDialog(node)
                    }else if(node.type=="class" || node.type=="geoclass" || node.type=="collectionclass"){
                        getDataSchemaDialog(node)
                    }
                }
            }
        }
        return contextmenu
    }
    $('#jstree').jstree(tree);
    $('#jstree').bind("dblclick.jstree", function (event) {
        var node = $(event.target).closest("li");
        var data = node[0].id
        if(data.includes(baseurl)){
            followLink(data)
        }else{
            window.open(data, '_blank');
        }
    });
    var to = false;
	$('#classsearch').keyup(function () {
        if(to) { clearTimeout(to); }
        to = setTimeout(function () {
            var v = $('#classsearch').val();
            $('#jstree').jstree(true).search(v,false,true);
        });
    });
}
"""

stylesheet = """
html { margin: 0; padding: 0; }
body { font-family: sans-serif; font-size: 80%; margin: 0; padding: 1.2em 2em; }
#rdficon { float: right; position: relative; top: -28px; }
#header { border-bottom: 2px solid #696; margin: 0 0 1.2em; padding: 0 0 0.3em; }
#footer { border-top: 2px solid #696; margin: 1.2em 0 0; padding: 0.3em 0 0; }
#homelink { display: inline; }
#homelink, #homelink a { color: #666; }
#homelink a { font-weight: bold; text-decoration: none; }
#homelink a:hover { color: red; text-decoration: underline; }
h1 { display: inline; font-weight: normal; font-size: 200%; margin: 0; text-align: left; }
h2 { font-weight: normal; font-size: 124%; margin: 1.2em 0 0.2em; }
.page-resource-uri { font-size: 116%; margin: 0.2em 0; }
.page-resource-uri a { color: #666; text-decoration: none; }
.page-resource-uri a:hover { color: red; text-decoration: underline; }
img { border: none; }
table.description { border-collapse: collapse; clear: left; font-size: 100%; margin: 0 0 1em; width: 100%; }
table.description th { background: white; text-align: left; }
table.description td, table.description th { line-height: 1.2em; padding: 0.3em 0.5em; vertical-align: top; }
table.description ul { margin: 0; padding-left: 1.4em; }
table.description li { list-style-position: outside; list-style-type: square; margin-left: 0; padding-left: 0; }
table.description .property-column { width: 13em; }
.ui-autocomplete {
    max-height: 100px;
    overflow-y: auto;
    /* prevent horizontal scrollbar */
    overflow-x: hidden;
  }
.uri { white-space: nowrap; }
.uri a, a.uri { text-decoration: none; }
.unbound { color: #888; }
table.description a small, .metadata-table a small  { font-size: 100%; color: #55a; }
table.description small, .metadata-table a small  { font-size: 100%; color: #666; }
table.description .property { white-space: nowrap; padding-right: 1.5em; }
h1, h2 { color: #810; }
body { background: #cec; }
table.description .container > td { background: #c0e2c0; padding: 0.2em 0.8em; }
table.description .even td { background: #d4f6d4; }
table.description .odd td { background: #f0fcf0; }
.image { background: white; float: left; margin: 0 1.5em 1.5em 0; padding: 2px; }
a.expander { text-decoration: none; }

.metadata-label {
	font-size: 100%;
	background: #f0fcf0;
	padding: 3px;
}

.metadata-table {
	font-size: 100%;
	border-left: 3px solid #f0fcf0;
	border-bottom: 3px solid #f0fcf0;
	border-right: 3px solid #f0fcf0;
	background: #d4f6d4;
	border-top: 0px solid none;
	margin: 0px;
}

.metadata-table td {
	padding: 3px;
}
body {
  font-family: "Lato", sans-serif;
}

.sidenav {
  height: 100%;
  width: 0;
  position: fixed;
  z-index: 1;
  top: 0;
  right: 0;
  background-color: #FFF;
  overflow-x: hidden;
  transition: 0.5s;
}

.sidenav a {
  text-decoration: none;
  font-size: 12px;
  color: #818181;
  transition: 0.3s;
}

.sidenav .closebtn {
  position: absolute;
  top: 0;
  right: 25px;
  font-size: 36px;
  margin-left: 50px;
}

#jstree {
	font-size: 12px;
	background-color:white;
	z-index: 2;
}

.jstree-contextmenu {
z-index: 10;
}

@media screen and (max-height: 450px) {
  .sidenav {padding-top: 15px;}
  .sidenav a {font-size: 18px;}
}"""

htmltemplate = """<html about=\"{{subject}}\"><head><title>{{toptitle}}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.5.1/dist/leaflet.css" integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ==" crossorigin="">
<link href='https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/leaflet.fullscreen.css' rel='stylesheet' />
<link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"/>
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.12.1/css/jquery.dataTables.min.css"/>
<link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>
<link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.1.1/themes/default/style.min.css" />
<link rel="stylesheet" type="text/css" href="{{stylepath}}"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
<script src="https://cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three/examples/js/controls/TrackballControls.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three/examples/js/loaders/PLYLoader.js"></script>
<script src="{{scriptfolderpath}}"></script><script src="{{classtreefolderpath}}"></script><script src="{{proprelationpath}}"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/jstree.min.js"></script>
<script type="text/javascript" src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.bundle.min.js"></script>
<script src="{{startscriptpath}}"></script>
</head>
<div id="mySidenav" class="sidenav" style="overflow:auto;">
  <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
  GeoClasses: <input type="checkbox" id="geoclasses"/><br/>
  Search:<input type="text" id="classsearch"><br/><div id="jstree"></div>
</div><script>var indexpage={{indexpage}}
var relativedepth={{relativedepth}}</script>
<body><div id="header"><h1 id="title">{{title}}</h1></div><div class="page-resource-uri"><a href="{{baseurl}}">{{baseurl}}</a> <b>powered by Static GeoPubby</b> generated using the <a style="color:blue;font-weight:bold" target="_blank" href="{{versionurl}}">{{version}}</a></div>
</div><div id="rdficon"><span style="font-size:30px;cursor:pointer" onclick="openNav()">&#9776;</span></div> <div class="search"><div class="ui-widget">Search: <input id="search" size="50"><button id="gotosearch" onclick="followLink()">Go</button><b>Download Options:</b>&nbsp;Format:<select id="format" onchange="changeDefLink()">	
{{exports}}
</select><a id="formatlink" href="#" target="_blank"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg></a>&nbsp;
<button id="downloadButton" onclick="download()">Download</button>{{bibtex}}<br/></div></div><dialog id="classrelationdialog" width="500" height="500" modal="true"></dialog><dialog id="dataschemadialog" width="500" height="500" modal="true"></dialog>
<div class="container-fluid"><div class="row-fluid" id="main-wrapper">
"""


imagecarouselheader="""<div id="imagecarousel" class="carousel slide" data-ride="carousel"><div class="carousel-inner">"""

imagecarouselfooter="""</div> <a class="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
    <span class="sr-only">Previous</span>
  </a>
  <a class="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
    <span class="carousel-control-next-icon" aria-hidden="true"></span>
    <span class="sr-only">Next</span>
  </a></div>"""

imagestemplate="""<div class="{{carousel}}" width="100%">
<a href="{{image}}" target=\"_blank\"><img src="{{image}}" style="max-width:485px;max-height:500px" alt="{{image}}" title="{{imagetitle}}" /></a>
</div>
"""

imageswithannotemplate="""<div class="{{carousel}}" width="100%">
<a href=\"{{image}}\" target=\"_blank\"><img src="{{image}}" style="max-width:485px;max-height:500px" alt="{{image}}" title="{{imagetitle}}" /></a>
{{svganno}}
</div>
"""


imagestemplatesvg="""<div class="{{carousel}}" style="max-width:485px;max-height:500px">
{{image}}
</div>
"""

videotemplate="""
<div class="video">
<video width="320" height="240" controls>
  <source src="{{video}}">
Your browser does not support the video tag.
</video>
</div>
"""

audiotemplate="""
<div class="audio">
<audio controls>
  <source src="{{audio}}">
Your browser does not support the audio element.
</audio>
</div>
"""

threejstemplate="""
<div id="threejs" class="threejscontainer" style="max-width:485px;max-height:500px">
</div>
<script>$(document).ready(function(){initThreeJS('threejs',parseWKTStringToJSON("{{wktstring}}"),{{meshurls}})})</script>
"""

image3dtemplate="""<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/stylesheet/3dhop.css"/>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/spidergl.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/corto.em.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/corto.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/presenter.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/nexus.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/ply.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/trackball_sphere.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/trackball_turntable.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/trackball_turntable_pan.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/trackball_pantilt.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/init.js"></script>
<div id="3dhop" class="tdhop" onmousedown="if (event.preventDefault) event.preventDefault()"><div id="tdhlg"></div>
<div id="toolbar"><img id="home"     title="Home"                  src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/home.png"            /><br/>
<img id="zoomin"   title="Zoom In"               src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/zoomin.png"          /><br/>
<img id="zoomout"  title="Zoom Out"              src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/zoomout.png"         /><br/>
<img id="light_on" title="Disable Light Control" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/lightcontrol_on.png" style="position:absolute; visibility:hidden;"/>
<img id="light"    title="Enable Light Control"  src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/lightcontrol.png"    /><br/>
<img id="full_on"  title="Exit Full Screen"      src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/full_on.png"         style="position:absolute; visibility:hidden;"/>
<img id="full"     title="Full Screen"           src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/full.png"            />
</div><canvas id="draw-canvas" style="background-color:white"></canvas></div><script>$(document).ready(function(){
start3dhop("{{meshurl}}","{{meshformat}}")});</script>"""

nongeoexports="""
<option value="csv">Comma Separated Values (CSV)</option>
<option value="geojson">(Geo)JSON</option>
<option value="json">JSON-LD</option>
<option value="ttl" selected>Turtle (TTL)</option>
"""

geoexports="""
<option value="csv">Comma Separated Values (CSV)</option>
<option value="geojson">(Geo)JSON</option>
<option value="ttl" selected>Turtle (TTL)</option>
<option value="wkt">Well-Known-Text (WKT)</option>
"""

maptemplate="""
<script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.0.6/dist/leaflet.markercluster-src.js"></script>
<script src="https://unpkg.com/leaflet.featuregroup.subgroup@1.0.2/dist/leaflet.featuregroup.subgroup.js"></script>
<script src="https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/Leaflet.fullscreen.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/dwilhelm89/LeafletSlider@master/dist/leaflet.SliderControl.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.8.1/proj4.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/albburtsev/Leaflet.geojsonCSS/leaflet.geojsoncss.min.js"></script>
<script src="{{epsgdefspath}}"></script>
<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/0.4.0/MarkerCluster.css" />
<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/0.4.0/MarkerCluster.Default.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css">
<link href='https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/leaflet.fullscreen.css' rel='stylesheet' />
<div id="map" style="height:500px;z-index: 0;"></div><script>
var rangesByAttribute={}
var overlayMaps={}
var baselayers={{baselayers}}
var featurecolls = {{myfeature}}
var epsg="{{epsg}}"
var dateatt="{{dateatt}}"
var map = L.map('map',{fullscreenControl: true,fullscreenControlOptions: {position: 'topleft'}}).setView([51.505, -0.09], 13);
var baseMaps = {};
props={}
setupLeaflet(baselayers,epsg,baseMaps,overlayMaps,map,dateatt)
</script>
"""

vowltemplate=""

htmlcommenttemplate="""<p class="comment"><b>Description:</b> {{comment}}</p>"""

htmltabletemplate="""<div style="overflow-x:auto;"><table border=1 width=100% class=description><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>{{tablecontent}}</tbody></table></div>"""

htmlfooter="""<div id="footer"><div class="container-fluid"><b>Download Options:</b>&nbsp;Format:<select id="format" onchange="changeDefLink()">	
{{exports}}
</select><a id="formatlink2" href="#" target="_blank"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg></a>&nbsp;
<button id="downloadButton" onclick="download()">Download</button>{{license}}{{bibtex}}</div></div></body><script>$(document).ready(function(){setSVGDimensions()})</script></html>"""

licensetemplate=""""""

classtreequery="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
        SELECT DISTINCT ?subject ?label ?supertype\n
        WHERE {\n
           { ?individual rdf:type ?subject . } UNION { ?subject rdf:type owl:Class . } UNION { ?subject rdf:type rdfs:Class . } .\n
           OPTIONAL { ?subject rdfs:subClassOf ?supertype } .\n
           OPTIONAL { ?subject rdfs:label ?label. filter(langMatches(lang(?label),\"en\")) }
           OPTIONAL { ?subject rdfs:label ?label }.\n
            FILTER (\n
                (\n
                ?subject != owl:Class &&\n
                ?subject != rdf:List &&\n
                ?subject != rdf:Property &&\n
                ?subject != rdfs:Class &&\n
                ?subject != rdfs:Datatype &&\n
                ?subject != rdfs:ContainerMembershipProperty &&\n
                ?subject != owl:DatatypeProperty &&\n
                ?subject != owl:AnnotationProperty &&\n
                ?subject != owl:Restriction &&\n
                ?subject != owl:ObjectProperty &&\n
                ?subject != owl:NamedIndividual &&\n
                ?subject != owl:Ontology) )\n
        }"""

featurecollectionspaths={}
iiifmanifestpaths={"default":[]}

def resolveTemplate(templatename):
    print(templatepath+"/"+templatename)
    if os.path.exists(templatepath+"/"+templatename):
        if os.path.exists(templatepath+"/"+templatename+"/css/style.css"):
            with open(templatepath+"/"+templatename+"/css/style.css", 'r') as file:
                global stylesheet
                stylesheet=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/js/startscripts.js"):
            with open(templatepath+"/"+templatename+"/js/startscripts.js", 'r') as file:
                global startscripts
                startscripts=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/js/epsgdefs.js"):
            with open(templatepath+"/"+templatename+"/js/epsgdefs.js", 'r') as file:
                global epsgdefs
                epsgdefs=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/header.html"):
            with open(templatepath+"/"+templatename+"/templates/header.html", 'r') as file:
                global htmltemplate
                htmltemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/footer.html"):
            with open(templatepath+"/"+templatename+"/templates/footer.html", 'r') as file:
                global htmlfooter
                htmlfooter=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/3dtemplate.html"):
            with open(templatepath+"/"+templatename+"/templates/3dtemplate.html", 'r') as file:
                global image3dtemplate
                image3dtemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/vowlwrapper.html"):
            with open(templatepath+"/"+templatename+"/templates/vowlwrapper.html", 'r') as file:
                global vowltemplate
                vowltemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/audiotemplate.html"):
            with open(templatepath+"/"+templatename+"/templates/audiotemplate.html", 'r') as file:
                global audiotemplate
                audiotemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/videotemplate.html"):
            with open(templatepath+"/"+templatename+"/templates/videotemplate.html", 'r') as file:
                global videotemplate
                videotemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/maptemplate.html"):
            with open(templatepath+"/"+templatename+"/templates/maptemplate.html", 'r') as file:
                global maptemplate
                maptemplate=file.read()
        return True
    return False

class OntDocGeneration:

    def __init__(self, prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath,graph,createIndexPages,createColl,metadatatable,generatePagesForNonNS,createVOWL,ogcapifeatures,localOptimized=False,startconcept=None,deploypath="",logoname="",templatename="default"):
        self.prefixes=prefixes
        self.prefixnamespace = prefixnamespace
        self.namespaceshort = prefixnsshort.replace("/","")
        self.outpath=outpath
        self.logoname=logoname
        self.startconcept=startconcept
        self.createVOWL=createVOWL
        self.ogcapifeatures=ogcapifeatures
        self.localOptimized=localOptimized
        self.geocache={}
        self.deploypath=deploypath
        self.generatePagesForNonNS=generatePagesForNonNS
        self.geocollectionspaths=[]
        self.metadatatable=metadatatable
        resolveTemplate(templatename)
        self.license=license
        self.licenseuri=None
        self.licensehtml=None
        self.createColl=createColl
        self.labellang=labellang
        self.typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        self.createIndexPages=createIndexPages
        self.graph=graph
        for nstup in self.graph.namespaces():
            if str(nstup[1]) not in prefixes["reversed"]:
                prefixes["reversed"][str(nstup[1])]=str(nstup[0])
        self.preparedclassquery=prepareQuery(classtreequery)
        if prefixnamespace==None or prefixnsshort==None or prefixnamespace=="" or prefixnsshort=="":
            self.namespaceshort = "suni"
            self.prefixnamespace = "http://purl.org/suni/"
        if not prefixnamespace.endswith("/") and not prefixnamespace.endswith("#"):
            self.prefixnamespace += "/"
        if outpath==None:
            self.outpath = "suni_htmls/"
        else:
            self.outpath = self.outpath.replace("\\", "/")
            if not outpath.endswith("/"):
                self.outpath += "/"
        self.outpath=self.outpath.replace("//","/")
        self.prefixnamespace=self.prefixnamespace.replace("//","/")
	#prefixes["reversed"]["http://purl.org/suni/"] = "suni"

    def processLiteral(self,literal, literaltype, reproject,currentlayergeojson=None,triplestoreconf=None):     
        #print("Process literal: " + str(literal) + " --- " + str(literaltype))
        try:
            if "wkt" in literaltype.lower(): 
                crsuri=""
                curcrs=None
                if "http" in literal:
                    crsuri=literal[0:literal.rfind('>')].replace("<","")
                    curcrs=crsuri[crsuri.rfind('/'):]
                    literal=literal[literal.rfind('>')+1:].strip()
                shapelygeom=shapely.wkt.loads(literal)
                thejson=json.loads(json.dumps(shapely.geometry.mapping(shapelygeom),indent=2))
                if curcrs!=None:
                    thejson["crs"]=curcrs               
                return thejson
            if "geojson" in literaltype.lower():
                return literal
        except Exception as e:
            print(e)
        return None

    def convertOWL2MiniVOWL(self,g,outpath,predicates=[],typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",labelproperty="http://www.w3.org/2000/01/rdf-schema#label"):
        minivowlresult={"info": [{
            "description": "Created with pyowl2vowl (version 0.1) as part of the SPARQLing Unicorn QGIS Plugin"}],
            "nodes": [],"links": []}
        nodes=[]
        nodeuriToId={}
        links=[]
        nodecounter=0
        for pred in g.subject_objects(URIRef(typeproperty)):
            if str(pred[1]) not in nodeuriToId:
                nodeuriToId[str(pred[1])]=nodecounter
                nodecounter+=1
                if str(pred[1])=="http://www.w3.org/2002/07/owl#Class" or str(pred[1])=="http://www.w3.org/2000/01/rdf-schema#Class" or str(pred[1])=="http://www.w3.org/2000/01/rdf-schema#Datatype":
                    nodes.append({"name":self.shortenURI(str(pred[1])),"type":"class","uri":str(pred[1])})
                else:
                    nodes.append({"name": self.shortenURI(str(pred[1])), "type": "class", "uri": str(pred[1])})
        if predicates!=[]:
            for pred in predicates:
                if "from" in predicates[pred] and "to" in predicates[pred]:
                    for fromsub in predicates[pred]["from"]:
                        if str(fromsub) in nodeuriToId:
                            if predicates[pred]["to"]!=[]:
                                for topred in predicates[pred]["to"]:
                                    if "http://www.w3.org/1999/02/22-rdf-syntax-ns#" not in str(topred) and "http://www.w3.org/2002/07/owl#" not in str(topred):
                                        links.append({"source": nodeuriToId[str(fromsub)],
                                                      "target": nodeuriToId[str(topred)],
                                                      "valueTo": self.shortenURI(str(pred)),
                                                      "propertyTo": "class",
                                                      "uriTo": str(pred)})
        else:
            for node in nodeuriToId:
                for predobj in g.predicate_objects(URIRef(node)):
                    if node in nodeuriToId and str(predobj[1]) in nodeuriToId and str(predobj[0])!=typeproperty:
                        links.append({"source":nodeuriToId[node],"target":nodeuriToId[str(predobj[1])],"valueTo": self.shortenURI(str(predobj[0])),"propertyTo":("class" if isinstance(predobj[1],URIRef) else "datatype"), "uriTo":(str(predobj[1]) if isinstance(predobj[1],URIRef) else predobj[1].datatype)})
        minivowlresult["nodes"]=nodes
        minivowlresult["links"] = links
        #print("MINIVOWL")
        #print(minivowlresult)
        f = open(outpath + "/minivowl_result.js", "w")
        f.write("var minivowlresult=" + json.dumps(minivowlresult, indent=1))
        f.close()

    def processLicense(self):
        if self.license==None or self.license=="" or self.license=="No License Statement":
            return ""
        if self.license.startswith("CC"):
            spl=self.license.split(" ")
            res= """<span style="float:right;margin-left:auto;margin-right:0px;text-align:right">This work is released under <a rel="license" target="_blank" href="http://creativecommons.org/licenses/"""+str(spl[1]).lower()+"/"+str(spl[2])+"""/">
            <img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/"""+str(spl[1]).lower()+"""/"""+str(spl[2])+"""/80x15.png"/></a></span>"""
            self.licenseuri="http://creativecommons.org/licenses/"+str(spl[1]).lower()+"/"+str(spl[2])
            return res
        else:
            return """All rights reserved."""

    def addAdditionalTriplesForInd(self,graph,ind,tobeaddedPerInd):
        for prop in tobeaddedPerInd:
            if "value" in tobeaddedPerInd[prop] and "uri" in tobeaddedPerInd[prop]:
                graph.add((ind, URIRef(prop), URIRef(str(tobeaddedPerInd[prop]["value"]))))
                graph.add((URIRef(str(tobeaddedPerInd[prop]["value"])),
                           URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                           URIRef(str(tobeaddedPerInd[prop]["uri"]))))
                graph.add((URIRef(str(tobeaddedPerInd[prop]["value"]).replace(" ", "_")),
                           URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                           URIRef(str(tobeaddedPerInd[prop]["value"]))))
            elif "value" in tobeaddedPerInd[prop] and not tobeaddedPerInd[prop]["value"].startswith("http"):
                if "type" in tobeaddedPerInd[prop]:
                    graph.add((ind,URIRef(prop),Literal(tobeaddedPerInd[prop]["value"],datatype=tobeaddedPerInd[prop]["type"])))
                elif "value" in tobeaddedPerInd[prop]:
                    graph.add((ind, URIRef(prop), Literal(tobeaddedPerInd[prop]["value"])))
            elif "value" in tobeaddedPerInd[prop] and not "uri" in tobeaddedPerInd[prop]:
                graph.add((ind, URIRef(prop), URIRef(str(tobeaddedPerInd[prop]["value"]))))



    def processSubjectPath(self,outpath,paths,path):
        if "/" in path:
            addpath = ""
            for pathelem in path.split("/"):
                addpath += pathelem + "/"
                if not os.path.isdir(outpath + addpath):
                    os.mkdir(outpath + addpath)
            if outpath + path[0:path.rfind('/')] + "/" not in paths:
                paths[outpath + path[0:path.rfind('/')] + "/"] = []
            paths[outpath + path[0:path.rfind('/')] + "/"].append(addpath[0:addpath.rfind('/')])
        else:
            if not os.path.isdir(outpath + path):
                os.mkdir(outpath + path)
            if outpath not in paths:
                paths[outpath] = []
            paths[outpath].append(path + "/index.html")
        if os.path.exists(outpath + path + "/index.ttl"):
            try:
                self.graph.parse(outpath + path + "/index.ttl")
            except Exception as e:
                print(e)
        return paths

    def generateOntDocForNameSpace(self, prefixnamespace,dataformat="HTML"):
        outpath=self.outpath
        corpusid=self.namespaceshort.replace("#","")
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        labeltouri = {}
        uritolabel = {}
        uritotreeitem={}
        curlicense=self.processLicense()
        self.licensehtml=curlicense
        self.getPropertyRelations(self.graph, outpath)
        if self.createColl:
            self.graph=self.createCollections(self.graph,prefixnamespace)
        if self.logoname!=None and self.logoname!="" and not self.logoname.startswith("http"):
            if not os.path.isdir(outpath+"/logo/"):
                os.mkdir(outpath+"/logo/")
            shutil.copy(self.logoname,outpath+"/logo/logo."+self.logoname[self.logoname.rfind("."):])
            self.logoname=outpath+"/logo/logo."+self.logoname[self.logoname.rfind("."):]
        subjectstorender = set()
        for sub in self.graph.subjects(None,None,True):
            if prefixnamespace in sub and (isinstance(sub,URIRef) or isinstance(sub,BNode)):
                subjectstorender.add(sub)
                for tup in self.graph.predicate_objects(sub):
                    if str(tup[0]) in labelproperties:
                        labeltouri[str(tup[1])] = str(sub)
                        uritolabel[str(sub)] = {"label":str(tup[1])}
                        break
        if os.path.exists(outpath + corpusid + '_search.js'):
            try:
                with open(outpath + corpusid + '_search.js', 'r', encoding='utf-8') as f:
                    data = json.loads(f.read().replace("var search=",""))
                    for key in data:
                        labeltouri[key]=data[key]
            except Exception as e:
                print("Exception occured " + str(e))
        with open(outpath + corpusid + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        prevtree=[]
        if os.path.exists(outpath + corpusid + '_classtree.js'):
            try:
                with open(outpath + corpusid + '_classtree.js', 'r', encoding='utf-8') as f:
                    prevtree = json.loads(f.read().replace("var tree=",""))["core"]["data"]
            except Exception as e:
                print("Exception occurred " + str(e))
        classidset=set()
        tree=self.getClassTree(self.graph, uritolabel,classidset,uritotreeitem)
        for tr in prevtree:
            if tr["id"] not in classidset:
                tree["core"]["data"].append(tr)
        with open(outpath + "style.css", 'w', encoding='utf-8') as f:
            f.write(stylesheet)
            f.close()
        with open(outpath + "startscripts.js", 'w', encoding='utf-8') as f:
            f.write(startscripts.replace("{{baseurl}}",prefixnamespace))
            f.close()
        with open(outpath + "epsgdefs.js", 'w', encoding='utf-8') as f:
            f.write(epsgdefs)
            f.close()
        pathmap = {}
        paths = {}
        nonnsmap={}
        postprocessing=Graph()
        subtorenderlen = len(subjectstorender)
        subtorencounter = 0
        for subj in subjectstorender:
            path = subj.replace(prefixnamespace, "")
            #try:
            paths=self.processSubjectPath(outpath,paths,path)
            if os.path.exists(outpath + path+"/index.ttl"):
                try:
                    self.graph.parse(outpath + path+"/index.ttl")
                except Exception as e:
                    print(e)
            res=self.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace, self.graph.subject_predicates(subj),
                       self.graph,str(corpusid) + "_search.js", str(corpusid) + "_classtree.js",uritotreeitem,curlicense,subjectstorender,postprocessing,nonnsmap)
            postprocessing=res[0]
            nonnsmap=res[1]
            subtorencounter += 1
            if subtorencounter%250==0:
                subtorenderlen=len(subjectstorender)+len(postprocessing)
                print(str(subtorencounter) + "/" + str(subtorenderlen) + " " + str(outpath + path))
            #except Exception as e:
            #    print("Create HTML Exception: "+str(e))
        print("Postprocessing " + str(len(postprocessing)))
        for subj in postprocessing.subjects(None,None,True):
            path = str(subj).replace(prefixnamespace, "")
            paths=self.processSubjectPath(outpath,paths,path)
            if os.path.exists(outpath + path+"/index.ttl"):
                try:
                    self.graph.parse(outpath + path+"/index.ttl")
                except Exception as e:
                    print(e)
            self.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace, self.graph.subject_predicates(subj),
                       self.graph,str(corpusid) + "_search.js", str(corpusid) + "_classtree.js",uritotreeitem,curlicense,subjectstorender,postprocessing)
            subtorencounter += 1
            if subtorencounter%250==0:
                subtorenderlen=len(subjectstorender)+len(postprocessing)
                print(str(subtorencounter) + "/" + str(subtorenderlen) + " " + str(outpath + path))
        self.checkGeoInstanceAssignment(uritotreeitem)
        self.assignGeoClassesToTree(tree)
        if self.generatePagesForNonNS:
            #self.detectURIsConnectedToSubjects(subjectstorender, self.graph, prefixnamespace, corpusid, outpath, self.license,prefixnamespace)
            labeltouri=self.getSubjectPagesForNonGraphURIs(nonnsmap, self.graph, prefixnamespace, corpusid, outpath, self.license,prefixnamespace,uritotreeitem,labeltouri)
        with open(outpath + corpusid + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=2))
            f.close()
        with open(outpath + corpusid + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        if self.createIndexPages:
            for path in paths:
                subgraph=Graph(bind_namespaces="rdflib")
                checkdepth = self.checkDepthFromPath(path, outpath, path)-1
                sfilelink=self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,corpusid + '_search.js',False)
                classtreelink = self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,corpusid + "_classtree.js",False)
                stylelink =self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,"style.css",False)
                scriptlink = self.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "startscripts.js", False)
                epsgdefslink = self.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "epsgdefs.js", False)
                vowllink = self.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "vowl_result.js", False)
                nslink=prefixnamespace+str(self.getAccessFromBaseURL(str(outpath),str(path)))
                for sub in subjectstorender:
                    if nslink in sub:
                        for tup in self.graph.predicate_objects(sub):
                            subgraph.add((sub, tup[0], tup[1]))
                subgraph.serialize(path + "index.ttl",encoding="utf-8")
                indexhtml = htmltemplate.replace("{{logo}}","").replace("{{baseurl}}", prefixnamespace).replace("{{relativedepth}}",str(checkdepth)).replace("{{toptitle}}","Index page for " + nslink).replace("{{title}}","Index page for " + nslink).replace("{{startscriptpath}}", scriptlink).replace("{{stylepath}}", stylelink).replace("{{vowlpath}}", vowllink)\
                    .replace("{{classtreefolderpath}}",classtreelink).replace("{{baseurlhtml}}", nslink).replace("{{nonnslink}}","").replace("{{scriptfolderpath}}", sfilelink).replace("{{exports}}",nongeoexports).replace("{{versionurl}}",versionurl).replace("{{version}}",version).replace("{{bibtex}}","")
                if nslink==prefixnamespace:
                    indexhtml=indexhtml.replace("{{indexpage}}","true")
                else:
                    indexhtml = indexhtml.replace("{{indexpage}}", "false")
                indexhtml+="<p>This page shows information about linked data resources in HTML. Choose the classtree navigation or search to browse the data</p>"+vowltemplate.replace("{{vowlpath}}", "minivowl_result.js")
                if startconcept!=None and path==outpath and startconcept in uritotreeitem:
                    if self.createColl:
                        indexhtml+="<p>Start exploring the graph here: <img src=\""+tree["types"][uritotreeitem[startconcept][-1]["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+uritotreeitem[startconcept][-1]["type"]+"\"/><a href=\""+self.generateRelativeLinkFromGivenDepth(prefixnamespace,0,str(startconcept),True)+"\">"+self.shortenURI(startconcept)+"</a></p>"                    
                    else:
                        indexhtml+="<p>Start exploring the graph here: <img src=\""+tree["types"][uritotreeitem[startconcept][-1]["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+uritotreeitem[startconcept][-1]["type"]+"\"/><a href=\""+self.generateRelativeLinkFromGivenDepth(prefixnamespace,0,str(startconcept),True)+"\">"+self.shortenURI(startconcept)+"</a></p>"
                indexhtml+="<table class=\"description\" style =\"height: 100%; overflow: auto\" border=1 id=indextable><thead><tr><th>Class</th><th>Number of instances</th><th>Instance Example</th></tr></thead><tbody>"
                for item in tree["core"]["data"]:
                    if (item["type"]=="geoclass" or item["type"]=="class" or item["type"]=="featurecollection" or item["type"]=="geocollection") and "instancecount" in item and item["instancecount"]>0:
                        exitem=None
                        for item2 in tree["core"]["data"]:
                            if item2["parent"]==item["id"] and (item2["type"]=="instance" or item2["type"]=="geoinstance") and nslink in item2["id"]:
                                checkdepth = self.checkDepthFromPath(path, prefixnamespace, item2["id"])-1
                                exitem="<td><img src=\""+tree["types"][item2["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+item2["type"]+"\"/><a href=\""+self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,str(re.sub("_suniv[0-9]+_","",item2["id"])),True)+"\">"+str(item2["text"])+"</a></td>"
                                break
                        if exitem!=None:
                            if self.createColl:
                                indexhtml+="<tr><td><img src=\""+tree["types"][item["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+item["type"]+"\"/><a href=\""+self.shortenURI(str(item["id"]))+"_collection/index.html\" target=\"_blank\">"+str(item["text"])+"</a></td>"
                            else:
                                indexhtml+="<tr><td><img src=\""+tree["types"][item["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+item["type"]+"\"/><a href=\""+str(item["id"])+"\" target=\"_blank\">"+str(item["text"])+"</a></td>"                       
                            indexhtml+="<td>"+str(item["instancecount"])+"</td>"+exitem+"</tr>"
                indexhtml += "</tbody></table><script>$('#indextable').DataTable();</script>"
                indexhtml+=htmlfooter.replace("{{license}}",curlicense).replace("{{exports}}",nongeoexports).replace("{{bibtex}}","")
                #print(path)
                with open(path + "index.html", 'w', encoding='utf-8') as f:
                    f.write(indexhtml)
                    f.close()
        if len(iiifmanifestpaths["default"])>0:
            self.generateIIIFCollections(self.outpath,iiifmanifestpaths["default"],prefixnamespace)
        if len(featurecollectionspaths)>0:
            indexhtml = htmltemplate.replace("{{logo}}",self.logoname).replace("{{relativedepth}}","0").replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}","Feature Collection Overview").replace("{{title}}","Feature Collection Overview").replace("{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{vowlpath}}", "vowl_result.js")\
                    .replace("{{classtreefolderpath}}",corpusid + "_classtree.js").replace("{{proprelationpath}}","proprelations.js").replace("{{nonnslink}}","").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}", corpusid + '_search.js').replace("{{exports}}",nongeoexports).replace("{{versionurl}}",versionurl).replace("{{version}}",version).replace("{{bibtex}}","")
            indexhtml = indexhtml.replace("{{indexpage}}", "true")
            self.generateOGCAPIFeaturesPages(outpath,featurecollectionspaths,prefixnamespace,self.ogcapifeatures,True)
            indexhtml += "<p>This page shows feature collections present in the linked open data export</p>"
            indexhtml+="<script src=\"features.js\"></script>"
            indexhtml+=maptemplate.replace("var ajax=true","var ajax=false").replace("var featurecolls = {{myfeature}}","").replace("{{baselayers}}",json.dumps(baselayers).replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{dateatt}}", ""))
            indexhtml += htmlfooter.replace("{{license}}", curlicense).replace("{{exports}}", nongeoexports).replace("{{bibtex}}","")
            with open(outpath + "featurecollections.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()
                    
    def getPropertyRelations(self,graph,outpath):
        predicates= {}
        predicatecounter=0
        for pred in graph.predicates(None,None,True):
            predicates[pred]={"from":set(),"to":set()}
            for tup in graph.subject_objects(pred):
                for item in graph.objects(tup[0],URIRef(self.typeproperty),True):
                    predicates[pred]["from"].add(item)
                for item in graph.objects(tup[1], URIRef(self.typeproperty),True):
                    predicates[pred]["to"].add(item)
            predicates[pred]["from"]=list(predicates[pred]["from"])
            predicates[pred]["to"] = list(predicates[pred]["to"])
            predicatecounter+=1
        if self.createVOWL:
            self.convertOWL2MiniVOWL(graph,outpath,predicates)
        with open(outpath+"proprelations.js", 'w', encoding='utf-8') as f:
            f.write("var proprelations="+json.dumps(predicates))
            f.close()

    def createCollections(self,graph,namespace):
        classToInstances={}
        classToGeoColl = {}
        classToFColl = {}
        for tup in graph.subject_objects(URIRef(self.typeproperty)):
            if namespace in str(tup[0]):
                if str(tup[1]) not in classToInstances:
                    classToInstances[str(tup[1])]=set()
                    classToFColl[str(tup[1])]=0
                    classToGeoColl[str(tup[1])] = 0
                classToInstances[str(tup[1])].add(str(tup[0]))
                isgeo=False
                isfeature = False
                for geotup in graph.predicate_objects(tup[0]):
                    if str(geotup[0]) in geopointerproperties:
                        isfeature=True
                    elif str(geotup[0]) in geoproperties:
                        isgeo=True
                if isgeo:
                    classToGeoColl[str(tup[1])]+=1
                if isfeature:
                    classToFColl[str(tup[1])]+=1
        for cls in classToInstances:
            colluri=namespace+self.shortenURI(cls)+"_collection"
            if classToFColl[cls]==len(classToInstances[cls]):
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection"),URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection"), URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection")))
                graph.add((URIRef(colluri), URIRef(self.typeproperty),URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection")))
            elif classToGeoColl[cls]==len(classToInstances[cls]):
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection"),URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection"), URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection")))
                graph.add((URIRef(colluri), URIRef(self.typeproperty),URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection")))
            else:
                graph.add((URIRef(colluri),URIRef(self.typeproperty),URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
            graph.add((URIRef(colluri),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(str(self.shortenURI(cls))+" Instances Collection")))
            for instance in classToInstances[cls]:
                graph.add((URIRef(colluri),URIRef("http://www.w3.org/2000/01/rdf-schema#member"),URIRef(instance)))
        return graph

    def getClassTree(self,graph, uritolabel,classidset,uritotreeitem):
        results = graph.query(self.preparedclassquery)
        tree = {"plugins": ["defaults","search", "sort", "state", "types", "contextmenu"], "search": {"show_only_matches":True}, "types": {
            "class": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/class.png"},
            "geoclass": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoclass.png"},
            "halfgeoclass": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/halfgeoclass.png"},
            "collectionclass": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/collectionclass.png"},
            "geocollection": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geometrycollection.png"},
            "featurecollection": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/featurecollection.png"},
            "instance": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/instance.png"},
            "geoinstance": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoinstance.png"}
        },
        "core": {"themes":{"responsive":True},"check_callback": True, "data": []}}
        result = []
        ress = {}
        for res in results:
            #print(res)
            if "_:" not in str(res["subject"]) and str(res["subject"]).startswith("http"):
                ress[str(res["subject"])] = {"super": res["supertype"], "label": res["label"]}
        #print(ress)
        for cls in ress:
            for obj in graph.subjects(URIRef(self.typeproperty), URIRef(cls),True):
                res = self.replaceNameSpacesInLabel(str(obj))
                if str(obj) in uritolabel:
                    restext= uritolabel[str(obj)]["label"] + " (" + self.shortenURI(str(obj)) + ")"
                    if res!=None:
                        restext=uritolabel[str(obj)]["label"] + " (" + res["uri"] + ")"
                else:
                    restext= self.shortenURI(str(obj))
                    if res!=None:
                        restext+= " (" + res["uri"] + ")"
                if str(obj) not in collectionclasses:
                    result.append({"id": str(obj), "parent": cls,"type": "instance","text": restext, "data":{}})
                else:
                    result.append({"id": str(obj), "parent": cls, "type": "class", "text": restext, "data": {}})
                if str(obj) not in uritotreeitem:
                    uritotreeitem[str(obj)]=[]
                uritotreeitem[str(obj)].append(result[-1])
                classidset.add(str(obj))
            res = self.replaceNameSpacesInLabel(str(cls))
            if ress[cls]["super"] == None:
                restext = self.shortenURI(str(cls))
                if res != None:
                    restext += " (" + res["uri"] + ")"
                if cls not in uritotreeitem:
                    result.append({"id": cls, "parent": "#","type": "class","text": restext,"data":{}})
                    uritotreeitem[str(cls)] = []
                    uritotreeitem[str(cls)].append(result[-1])
            else:
                if "label" in cls and cls["label"] != None:
                    restext = ress[cls]["label"] + " (" + self.shortenURI(str(cls)) + ")"
                    if res != None:
                        restext = ress[cls]["label"] + " (" + res["uri"] + ")"
                else:
                    restext = self.shortenURI(str(cls))
                    if res != None:
                        restext += " (" + res["uri"] + ")"
                if cls not in uritotreeitem:
                    result.append({"id": cls, "parent": ress[cls]["super"],"type": "class","text": restext,"data":{}})
                    if str(cls) not in uritotreeitem:
                        uritotreeitem[str(cls)] = []
                        uritotreeitem[str(cls)].append(result[-1])
                else:
                    uritotreeitem[cls][-1]["parent"]=ress[cls]["super"]
                if str(ress[cls]["super"]) not in uritotreeitem:
                    uritotreeitem[str(ress[cls]["super"])]=[]
                    clsres = self.replaceNameSpacesInLabel(str(ress[cls]["super"]))
                    if clsres!=None:
                        theitem = {"id": str(ress[cls]["super"]), "parent": "#", "type": "class",
                                   "text": self.shortenURI(str(ress[cls]["super"]))+" (" + clsres["uri"] + ")", "data": {}}
                    else:
                        theitem={"id": str(ress[cls]["super"]), "parent": "#","type": "class","text": self.shortenURI(str(ress[cls]["super"])),"data":{}}
                    uritotreeitem[str(ress[cls]["super"])].append(theitem)
                    result.append(theitem)
                classidset.add(str(ress[cls]["super"]))
            classidset.add(str(cls))
        tree["core"]["data"] = result
        return tree

    def assignGeoClassesToTree(self,tree):
        classlist={}
        for item in tree["core"]["data"]:
            if item["type"]=="class":
                classlist[item["id"]]={"items":0,"geoitems":0,"item":item}
        for item in tree["core"]["data"]:
            if item["type"]=="instance" and item["parent"] in classlist:
                classlist[item["parent"]]["items"]+=1
            elif (item["type"] == "geoinstance" or item["type"]=="featurecollection" or item["type"]=="geocollection") and item["parent"] in classlist:
                classlist[item["parent"]]["items"]+=1
                classlist[item["parent"]]["geoitems"]+=1
        for item in classlist:
            if classlist[item]["items"]>0:
                if classlist[item]["item"]["text"].endswith("]"):
                    classlist[item]["item"]["text"]=classlist[item]["item"]["text"][0:classlist[item]["item"]["text"].rfind("[")-1]+" ["+str(classlist[item]["items"])+"]"
                else:
                    classlist[item]["item"]["text"]=classlist[item]["item"]["text"]+" ["+str(classlist[item]["items"])+"]"
            if item in collectionclasses:
                classlist[item]["item"]["type"] = "collectionclass"
            elif classlist[item]["items"]==classlist[item]["geoitems"] and classlist[item]["items"]>0 and classlist[item]["geoitems"]>0:
                classlist[item]["item"]["type"]="geoclass"
            elif classlist[item]["items"]>classlist[item]["geoitems"] and classlist[item]["geoitems"]>0:
                classlist[item]["item"]["type"]="halfgeoclass"
            else:
                classlist[item]["item"]["type"] = "class"

    def checkGeoInstanceAssignment(self,uritotreeitem):
        for uri in uritotreeitem:
            if len(uritotreeitem[uri])>1:
                thetype="instance"
                counter=0
                if uritotreeitem[uri]!=None:
                    for item in uritotreeitem[uri]:
                        if item["type"]!="instance" or item["type"]!="class":
                            thetype=item["type"]
                        if item["type"]!="class":
                            item["id"]=item["id"]+"_suniv"+str(counter)+"_"
                        counter+=1
                    if thetype!="instance" or thetype!="class":
                        for item in uritotreeitem[uri]:
                            item["type"]=thetype


    def shortenURI(self,uri,ns=False):
        if uri!=None and "#" in uri and ns:
            return uri[0:uri.rfind('#')+1]
        if uri!=None and "/" in uri and ns:
            return uri[0:uri.rfind('/')+1]
        if uri!=None and uri.endswith("/"):
            uri = uri[0:-1]
        if uri!=None and "#" in uri and not ns:
            return uri[uri.rfind('#')+1:]
        if uri!=None and "/" in uri and not ns:
            return uri[uri.rfind('/')+1:]
        return uri

    def replaceNameSpacesInLabel(self,uri):
        for ns in self.prefixes["reversed"]:
            if ns in uri:
                return {"uri": str(self.prefixes["reversed"][ns]) + ":" + str(uri.replace(ns, "")),
                        "ns": self.prefixes["reversed"][ns]}
        return None

    def generateRelativeLinkFromGivenDepth(self,baseurl,checkdepth,item,withindex):
        rellink = str(item).replace(baseurl, "")
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        if withindex:
            rellink += "/index.html"
        return rellink

    def resolveBibtexReference(self,predobjs,item,graph):	
        bibtexmappings={"http://purl.org/dc/elements/1.1/title":"title",	
                      "http://purl.org/dc/elements/1.1/created":"year",	
                      "http://purl.org/ontology/bibo/number":"number",	
                      "http://purl.org/ontology/bibo/publisher":"publisher",	
                      "http://purl.org/ontology/bibo/issuer": "journal",	
                      "http://purl.org/ontology/bibo/volume":"volume",	
                      "http://purl.org/ontology/bibo/doi": "doi",	
                      "http://purl.org/ontology/bibo/eissn": "eissn",	
                      "http://purl.org/ontology/bibo/eprint": "eprint",	
                      "http://purl.org/ontology/bibo/url": "url",	
                      "http://purl.org/ontology/bibo/issn": "issn",	
                      "http://purl.org/ontology/bibo/isbn": "isbn",	
                      "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":"type"	
                      }	
        bibtexitem={"type":"@misc"}	
        for tup in predobjs:	
            if str(tup[0])=="http://purl.org/dc/elements/1.1/creator":	
                if "author" not in bibtexitem:	
                    bibtexitem["author"]=[]	
                if isinstance(tup[1],URIRef):	
                    bibtexitem["author"].append(self.getLabelForObject(tup[1],graph))	
                else:	
                    bibtexitem["author"].append(str(tup[1]))	
            elif str(tup[0]) == "http://purl.org/ontology/bibo/pageStart":
                if "pages" not in bibtexitem:	
                    bibtexitem["pages"]={}	
                bibtexitem["pages"]["start"]=str(tup[1])	
            elif str(tup[0]) == "http://purl.org/ontology/bibo/pageEnd":
                if "pages" not in bibtexitem:	
                    bibtexitem["pages"]={}	
                bibtexitem["pages"]["end"]=str(tup[1])	
            elif str(tup[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and str(tup[1]) in bibtextypemappings:	
                bibtexitem["type"]=bibtextypemappings[str(tup[1])]	             
            elif str(tup[0]) in bibtexmappings:	
                if isinstance(tup[1],URIRef):	
                    bibtexitem[bibtexmappings[str(tup[0])]]=self.getLabelForObject(tup[1],graph)	
                else:	
                    bibtexitem[bibtexmappings[str(tup[0])]]=str(tup[1])          	
        res=bibtexitem["type"]+"{"+self.shortenURI(item)+",\n"	
        for bibpart in sorted(bibtexitem):
            if bibpart=="type":
                continue
            res += bibpart + "={"
            if bibpart=="author":
                first=True	
                for author in bibtexitem["author"]:	
                    if first:	
                        res+=author+" "	
                        first=False	
                    else:	
                        res+="and "+author+" "	
                res=res[0:-1]
                res+="},\n"	
            elif bibpart=="pages":	
                res+=bibtexitem[bibpart]["start"]+"--"+bibtexitem[bibpart]["end"]+"},\n"
            else:	
                res+=str(bibtexitem[bibpart])+"},\n"
        res=res[0:-2]
        res+="\n}"
        return res

    def resolveTimeObject(self,pred,obj,graph,timeobj):
        if str(pred)=="http://www.w3.org/2006/time#hasBeginning":
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in timeproperties:
                    timeobj["begin"]=tobj2[1]
        elif str(pred)=="http://www.w3.org/2006/time#hasEnd":
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in timeproperties:
                    timeobj["end"]=tobj2[1]
        elif str(pred)=="http://www.w3.org/2006/time#hasTime":
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in timeproperties:
                    timeobj["timepoint"]=tobj2[1]
        return timeobj
    
    def createURILink(self,uri):
        res=self.replaceNameSpacesInLabel(uri)
        if res!=None:
           return " <a href=\""+str(uri)+"\" target=\"_blank\">"+str(res["uri"])+"</a>"
        else:
            return " <a href=\""+str(uri)+"\" target=\"_blank\">"+self.shortenURI(uri)+"</a>"

    def timeObjectToHTML(self,timeobj):
        timeres=None
        if "begin" in timeobj and "end" in timeobj:
            timeres=str(timeobj["begin"])+" "
            if str(timeobj["begin"].datatype) in timeliteraltypes:
                timeres+=self.createURILink(timeliteraltypes[str(timeobj["begin"].datatype)])
            timeres+=" - "+str(timeobj["end"])
            if str(timeobj["end"].datatype) in timeliteraltypes:
                timeres+=self.createURILink(timeliteraltypes[str(timeobj["end"].datatype)])
        elif "begin" in timeobj and not "end" in timeobj:
            timeres=str(timeobj["begin"])
            if str(timeobj["begin"].datatype) in timeliteraltypes:
                timeres+=self.createURILink(timeliteraltypes[str(timeobj["begin"].datatype)])
        elif "begin" not in timeobj and "end" in timeobj:
            timeres=str(timeobj["end"])
            if str(timeobj["end"].datatype) in timeliteraltypes:
                timeres+=self.createURILink(timeliteraltypes[str(timeobj["end"].datatype)])
        elif "timepoint" in timeobj:
            timeres=timeobj["timepoint"]
            if str(timeobj["timepoint"].datatype) in timeliteraltypes:
                timeres+=self.createURILink(timeliteraltypes[str(timeobj["timepoint"].datatype)])
        return timeres

    def resolveTimeLiterals(self,pred,obj,graph):
        timeobj={}
        if isinstance(obj,URIRef) and str(pred)=="http://www.w3.org/2006/time#hasTime":         
            for tobj in graph.predicate_objects(obj):
                timeobj=self.resolveTimeObject(tobj[0],tobj[1],graph,timeobj)
        elif isinstance(obj,URIRef) and str(pred) in timepointerproperties: 
            timeobj=self.resolveTimeObject(pred,obj,graph,timeobj)
        elif isinstance(obj,Literal):
            timeobj=self.resolveTimeObject(pred,obj,graph,timeobj)
        return timeobj

    def resolveGeoLiterals(self,pred,object,graph,geojsonrep,nonns,subject=None):
        if subject!=None and isinstance(object, Literal) and (str(pred) in geopairproperties):
            pairprop = geopairproperties[str(pred)]["pair"]
            latorlong = geopairproperties[str(pred)]["islong"]
            othervalue = ""
            for obj in graph.objects(subject, URIRef(pairprop)):
                othervalue = str(obj)
            if latorlong:
                geojsonrep = {"type": "Point", "coordinates": [float(str(othervalue)), float(str(object))]}
            else:
                geojsonrep = {"type": "Point", "coordinates": [float(str(object)), float(str(othervalue))]}
        elif isinstance(object, Literal) and (
                str(pred) in geoproperties or str(object.datatype) in geoliteraltypes):
            geojsonrep = self.processLiteral(str(object), str(object.datatype), "")
        elif isinstance(object, URIRef) and nonns:
            for pobj in graph.predicate_objects(object):
                if isinstance(pobj[1], Literal) and (
                        str(pobj[0]) in geoproperties or str(
                    pobj[1].datatype) in geoliteraltypes):
                    geojsonrep = self.processLiteral(str(pobj[1]), str(pobj[1].datatype), "")
        return geojsonrep

    def getLabelForObject(self,obj,graph,labellang=None):	
        label=""	
        onelabel=self.shortenURI(str(obj))
        for tup in graph.predicate_objects(obj):	
            if str(tup[0]) in labelproperties:	
                # Check for label property	
                if tup[1].language==labellang:
                    label=str(tup[1])	
                onelabel=str(tup[1])	
        if label=="" and onelabel!=None:	
            label=onelabel	
        return label

    def searchObjectConnectionsForAggregateData(self,graph,object,pred,geojsonrep,foundmedia,imageannos,textannos,image3dannos,label,unitlabel,nonns):
        geoprop=False
        annosource=False
        incollection=False
        if pred in geopointerproperties:
            geoprop=True
        if pred in collectionrelationproperties:
            incollection=True
        foundval=None
        foundunit=None
        tempvalprop=None
        onelabel=None
        bibtex=None
        timeobj=None
        for tup in graph.predicate_objects(object):
            if str(tup[0]) in labelproperties:
                if tup[1].language==self.labellang:
                    label=str(tup[1])
                onelabel=str(tup[1])
            if pred=="http://www.w3.org/ns/oa#hasSelector" and tup[0]==URIRef(self.typeproperty) and (tup[1]==URIRef("http://www.w3.org/ns/oa#SvgSelector") or tup[1]==URIRef("http://www.w3.org/ns/oa#WKTSelector")):
                for svglit in graph.objects(object,URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#value")):
                    if "<svg" in str(svglit):
                        imageannos.add(str(svglit))
                    elif ("POINT" in str(svglit).upper() or "POLYGON" in str(svglit).upper() or "LINESTRING" in str(svglit).upper()):
                        image3dannos.add(str(svglit))
            if pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(
                    self.typeproperty) and tup[1] == URIRef(
                    "http://www.w3.org/ns/oa#TextPositionSelector"):
                curanno = {}
                for txtlit in graph.predicate_objects(object):
                    if str(txtlit[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#value":
                        curanno["exact"] = str(txtlit[1])
                    elif str(txtlit[0]) == "http://www.w3.org/ns/oa#start":
                        curanno["start"] = str(txtlit[1])
                    elif str(txtlit[0]) == "http://www.w3.org/ns/oa#end":
                        curanno["end"] = str(txtlit[1])
                textannos.append(curanno)
            if pred == "http://www.w3.org/ns/oa#hasSource":
                annosource = str(tup[1])
            if pred == "http://purl.org/dc/terms/isReferencedBy" and tup[0] == URIRef(self.typeproperty) and ("http://purl.org/ontology/bibo/" in str(tup[1])):	
                bibtex=self.resolveBibtexReference(graph.predicate_objects(object),object,graph)
            if pred in timepointerproperties:
                timeobj=self.resolveTimeLiterals(pred,object,graph)
            if not nonns:
                geojsonrep=self.resolveGeoLiterals(tup[0], tup[1], graph, geojsonrep,nonns)
            if incollection and "<svg" in str(tup[1]):
                foundmedia["image"].add(str(tup[1]))
            elif incollection and "http" in str(tup[1]):
                ext="."+''.join(filter(str.isalpha,str(tup[1]).split(".")[-1]))
                if ext in fileextensionmap:
                    foundmedia[fileextensionmap[ext]].add(str(tup[1]))
            if str(tup[0]) in valueproperties:
                if tempvalprop == None and str(tup[0]) == "http://www.w3.org/ns/oa#hasSource":
                    tempvalprop = str(tup[0])
                    foundval = str(tup[1])
                if str(tup[0]) != "http://www.w3.org/ns/oa#hasSource" and valueproperties[
                    str(tup[0])] == "DatatypeProperty" and (isinstance(tup[1], Literal) or isinstance(tup[1], URIRef)):
                    tempvalprop = str(tup[0])
                    foundval = str(tup[1])
                elif str(tup[0]) == "http://www.w3.org/ns/oa#hasTarget":
                    tempvalprop = "http://www.w3.org/ns/oa#hasTarget"
                    for inttup in graph.predicate_objects(tup[1]):
                        if str(inttup[0]) == "http://www.w3.org/ns/oa#hasSelector":
                            for valtup in graph.predicate_objects(inttup[1]):
                                if str(valtup[0]) in unitproperties:
                                    foundunit = str(valtup[1])
                                if str(valtup[0]) in valueproperties and (
                                        isinstance(valtup[1], Literal) or isinstance(valtup[1], URIRef)):
                                    foundval = str(valtup[1])
                else:
                    for valtup in graph.predicate_objects(tup[1]):
                        if str(valtup[0]) in unitproperties:
                            foundunit=str(valtup[1])
                        if str(valtup[0]) in valueproperties and isinstance(valtup[1],Literal):
                            foundval=str(valtup[1])
            if str(tup[0]) in unitproperties:
                foundunit=tup[1]
        if foundunit!=None and foundval!=None:
            res=None
            if "http" in foundunit:
                unitlabel=self.createURILink(str(foundunit))
            else:
                unitlabel=str(foundval)+" "+str(foundunit)
        if foundunit == None and foundval != None:
            if "http" in foundval:
                unitlabel = "<a href=\"" + str(foundval) + "\">" + str(self.shortenURI(foundval)) + "</a>"
            else:
                unitlabel = str(foundval)
        if annosource != None:
            for textanno in textannos:
                textanno["src"] = annosource
        if label=="" and onelabel!=None:
            label=onelabel
        return {"geojsonrep":geojsonrep,"label":label,"unitlabel":unitlabel,"foundmedia":foundmedia,"imageannos":imageannos,"textannos":textannos,"image3dannos":image3dannos,"bibtex":bibtex,"timeobj":timeobj}


    def createHTMLTableValueEntry(self,subject,pred,object,ttlf,graph,baseurl,checkdepth,geojsonrep,foundmedia,imageannos,textannos,image3dannos,dateprops,inverse,nonns):
        tablecontents=""
        label=""
        bibtex=None
        timeobj=None
        if isinstance(object,URIRef) or isinstance(object,BNode):
            if ttlf != None:
                ttlf.add((subject,URIRef(pred),object))
            label = ""
            unitlabel=""
            mydata=self.searchObjectConnectionsForAggregateData(graph,object,pred,geojsonrep,foundmedia,imageannos,textannos,image3dannos,label,unitlabel,nonns)
            label=mydata["label"]
            if label=="":
                label=str(self.shortenURI(str(object)))
            geojsonrep=mydata["geojsonrep"]
            foundmedia=mydata["foundmedia"]
            imageannos=mydata["imageannos"]
            textannos=mydata["textannos"]
            image3dannos=mydata["image3dannos"]
            unitlabel=mydata["unitlabel"]
            bibtex=mydata["bibtex"]
            timeobj=mydata["timeobj"]
            if inverse:
                rdfares = " about=\"" + str(object) + "\" resource=\"" + str(subject) + "\""
            else:
                rdfares = "resource=\"" + str(object) + "\""
            if baseurl in str(object) or isinstance(object,BNode):
                rellink = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,str(object),True)
                tablecontents += "<span><a property=\"" + str(pred) + "\" "+rdfares+" href=\"" + rellink + "\">"+ label + " <span style=\"color: #666;\">(" + self.namespaceshort + ":" + str(self.shortenURI(str(object))) + ")</span></a>"
                if bibtex!=None:
                    tablecontents+="<details><summary>[BIBTEX]</summary><pre>"+str(bibtex)+"</pre></details>"
            else:
                res = self.replaceNameSpacesInLabel(str(object))
                if res != None:
                    tablecontents += "<span><a property=\"" + str(pred) + "\" "+rdfares+" target=\"_blank\" href=\"" + str(object) + "\">" + label + " <span style=\"color: #666;\">(" + res["uri"] + ")</span></a>"                                     
                else:
                    tablecontents += "<span><a property=\"" + str(pred) + "\" "+rdfares+" target=\"_blank\" href=\"" + str(object) + "\">" + label + "</a>"
                if bibtex!=None:
                    tablecontents+="<details><summary>[BIBTEX]</summary><pre>"+str(bibtex)+"</pre></details>"
                if self.generatePagesForNonNS:
                    rellink = self.generateRelativeLinkFromGivenDepth(str(baseurl), checkdepth,
                                                                      str(baseurl) + "nonns_" + self.shortenURI(
                                                                          str(object).replace(":","_")), False)
                    tablecontents+=" <a href=\""+rellink+".html\">[x]</a>"
            if unitlabel!="":
                tablecontents+=" <span style=\"font-weight:bold\">["+str(unitlabel)+"]</span>"
            if timeobj!=None:
                tablecontents+=" <span style=\"font-weight:bold\">["+str(self.timeObjectToHTML(timeobj))+"]</span>"
                dateprops=timeobj
            tablecontents+="</span>"
        else:
            label=str(object)
            if ttlf != None:
                ttlf.add((subject,URIRef(pred),object))
            if isinstance(object, Literal) and object.datatype != None:
                res = self.replaceNameSpacesInLabel(str(object.datatype))
                objstring=str(object).replace("<", "&lt").replace(">", "&gt;")
                if str(object.datatype)=="http://www.w3.org/2001/XMLSchema#anyURI":
                    objstring="<a href=\""+str(object)+"\">"+str(object)+"</a>"
                if str(object.datatype) in timeliteraltypes and dateprops!=None and self.shortenURI(str(pred),True) not in metadatanamespaces and str(pred) not in dateprops:
                    dateprops.append(str(pred))
                if res != None:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + objstring + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + res["uri"]+ "</a>)</small></span>"
                else:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + objstring + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + self.shortenURI(str(object.datatype)) + "</a>)</small></span>"
                geojsonrep=self.resolveGeoLiterals(URIRef(pred), object, graph, geojsonrep,nonns,subject)
            else:
                if object.language != None:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(object).replace("<", "&lt").replace(">", "&gt;").replace("\"","'") + "\" datatype=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\" xml:lang=\"" + str(object.language) + "\">" + str(object).replace("<", "&lt").replace(">", "&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\">rdf:langString</a>) (<a href=\"http://www.lexvo.org/page/iso639-1/"+str(object.language)+"\" target=\"_blank\">iso6391:" + str(object.language) + "</a>)</small></span>"
                else:
                    tablecontents += self.detectStringLiteralContent(pred,object)
        return {"html":tablecontents,"geojson":geojsonrep,"foundmedia":foundmedia,"imageannos":imageannos,"textannos":textannos,"image3dannos":image3dannos,"label":label,"timeobj":dateprops}

    def detectStringLiteralContent(self,pred,object):
        if object.startswith("http://") or object.startswith("https://"):
            return "<span><a property=\"" + str(pred) + "\" target=\"_blank\" href=\"" + str(
                        object)+ "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object)+ "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        elif object.startswith("www."):
            return "<span><a property=\"" + str(pred) + "\" target=\"_blank\" href=\"http://" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">http://" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        elif re.search(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?![%"#? ])\\S)+)',str(object)):
            return "<span><a property=\"" + str(pred) + "\" href=\"https://www.doi.org/" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#anyURI\">" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#anyURI\">xsd:anyURI</a>)</small></span>"        
        elif re.search(r'[\w.]+\@[\w.]+', object):
            return "<span><a property=\"" + str(pred) + "\" href=\"mailto:" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">mailto:" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        return "<span property=\"" + str(pred) + "\" content=\"" + str(object).replace("<","&lt").replace(">","&gt;").replace("\"","'") + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object).replace("<","&lt").replace(">","&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"

    def formatPredicate(self,tup,baseurl,checkdepth,tablecontents,graph,reverse):
        label=self.getLabelForObject(URIRef(str(tup)), graph,self.labellang)
        tablecontents += "<td class=\"property\">"
        if reverse:
            tablecontents+="Is "
        if baseurl in str(tup):
            rellink = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth,str(tup),True)
            tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + rellink + "\">" + label + "</a></span>"
        else:
            res = self.replaceNameSpacesInLabel(tup)
            if res != None:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup) + "\">" + label + " <span style=\"color: #666;\">(" + res[
                                     "uri"] + ")</span></a> "
            else:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup) + "\">" + label + "</a> "
            tablecontents+="</span>"
        if reverse:
            tablecontents+=" of"
        tablecontents += "</td>"
        return tablecontents

    def getSubjectPagesForNonGraphURIs(self,uristorender,graph,prefixnamespace,corpusid,outpath,nonnsmap,baseurl,uritotreeitem,labeltouri):
        nonnsuris=len(uristorender)	
        counter=0	
        for uri in uristorender:	
            label=""	
            for tup in graph.predicate_objects(URIRef(uri)):
                if str(tup[0]) in labelproperties:	
                    label = str(tup[1])	
            if uri in uritotreeitem:
                res = self.replaceNameSpacesInLabel(str(uri))
                label=self.getLabelForObject(URIRef(str(uri)), graph,self.labellang)
                if res!=None and label!="":
                    uritotreeitem[uri][-1]["text"]=label+" (" + res["uri"] + ")"
                elif label!="":
                    uritotreeitem[uri][-1]["text"]=label+" ("+self.shortenURI(uri)+")"
                else:
                    uritotreeitem[uri][-1]["text"]=self.shortenURI(uri)
                uritotreeitem[uri][-1]["id"]=prefixnamespace+"nonns_"+self.shortenURI(uri)+".html"
                labeltouri[label]=prefixnamespace+"nonns_"+self.shortenURI(uri)+".html"
            if counter%50==0:
                print("NonNS Counter " +str(counter)+"/"+str(nonnsuris)+" "+ str(uri))	
            self.createHTML(outpath+"nonns_"+self.shortenURI(uri)+".html", None, URIRef(uri), baseurl, graph.subject_predicates(URIRef(uri),True), graph, str(corpusid) + "_search.js", str(corpusid) + "_classtree.js", None, self.license, None, Graph(),uristorender,True,label)	
            counter+=1	
        return labeltouri

    def generateRelativeSymlink(self,linkpath,targetpath,outpath,items=False):
        if "nonns" in targetpath and not items:
            checkdepthtarget=3
        elif "nonns" in targetpath and items:
            checkdepthtarget=4
        else:
            checkdepthtarget=targetpath.count("/")-1
        print("Checkdepthtarget: "+str(checkdepthtarget))
        targetrellink=self.generateRelativeLinkFromGivenDepth(targetpath,checkdepthtarget,linkpath,False)
        print("Target Rellink: "+str(targetrellink))
        print("Linkpath: "+str(linkpath))
        targetrellink=targetrellink.replace(outpath,"")
        return targetrellink.replace("//","/")

    def generateIIIFManifest(self,outpath,imgpaths,curind,prefixnamespace,label="",summary="",thetypes=None,predobjmap=None):
        print("GENERATE IIIF Manifest for "+str(self.outpath)+" "+str(curind)+" "+str(label)+" "+str(summary)+" "+str(predobjmap))
        if not os.path.exists(self.outpath+"/iiif/mf/"+self.shortenURI(curind)+"/manifest.json"):
            if not os.path.exists(self.outpath + "/iiif/mf/"):
                os.makedirs(self.outpath + "/iiif/mf/")
            if not os.path.exists(self.outpath + "/iiif/images/"):
                os.makedirs(self.outpath + "/iiif/images/")
            print(label)
            if label!="":
                curiiifmanifest={"@context": "http://iiif.io/api/presentation/3/context.json","id":self.deploypath+"/iiif/mf/"+self.shortenURI(curind)+"/manifest.json", "type": "Manifest","label":{"en":[str(label)+" ("+self.shortenURI(curind)+")"]},"homepage":[{"id":"","type":"Text","label":{"en":[str(self.deploypath)+"/"+str(curind)]},"format": "text/html", "language":["en"]}],"metadata":[],"items":[]}
            else:
                curiiifmanifest={"@context": "http://iiif.io/api/presentation/3/context.json","id":self.deploypath+"/iiif/mf/"+self.shortenURI(curind)+"/manifest.json", "type": "Manifest","label":{"en":[self.shortenURI(curind)]},"homepage":[{"id":"","type":"Text","label":{"en":[str(self.deploypath)+"/"+str(curind)]},"format": "text/html", "language":["en"]}],"metadata":[],"homepage":[],"items":[]}
            pagecounter=0
            for imgpath in imgpaths:
                curiiifmanifest["items"].append({"id":imgpath+"/canvas/p"+str(pagecounter),"type":"Canvas","label":{"en":[str(label)+" Image "+str(pagecounter+1)]},"height":100,"width":100,"items":[{"id":imgpath+"/canvas/p"+str(pagecounter)+"/1","type":"AnnotationPage","items":[{"id":imgpath+"/annotation/p"+str(pagecounter)+"/1","type":"Annotation","motivation":"painting","body":{"id":imgpath,"type":"Image","format":"image/png"},"target":imgpath+"/canvas/p"+str(pagecounter)}]}],"annotations":[{"id":imgpath+"/canvas/p"+str(pagecounter)+"/annopage-2","type":"AnnotationPage","items":[{"id":imgpath+"/canvas/p"+str(pagecounter)+"/anno-1","type":"Annotation","motivation":"commenting","body":{"type":"TextualBody","language":"en","format":"text/html","value":"<a href=\""+str(curind)+"\">"+str(self.shortenURI(curind))+"</a>"},"target":imgpath+"/canvas/p"+str(pagecounter)}]}]})
                pagecounter+=1
            for pred in predobjmap:
                for objs in predobjmap[pred]:
                    print(str(pred)+" "+str(objs))
                    if isinstance(objs,URIRef):
                        curiiifmanifest["metadata"].append({"label":{"en":[self.shortenURI(str(pred))]},"value":{"en":["<a href=\""+str(objs)+"\">"+str(objs)+"</a>"]}})
                    else:
                        curiiifmanifest["metadata"].append({"label":{"en":[self.shortenURI(str(pred))]},"value":{"en":[str(objs)]}})
                    print(curiiifmanifest["metadata"])
            if summary!=None and summary!="" and summary!={}:
                curiiifmanifest["summary"]={"en":[str(summary)]}
            #os.makedirs(self.outpath + "/iiif/images/"+self.shortenURI(imgpath)+"/full/")
            #os.makedirs(self.outpath + "/iiif/images/"+self.shortenURI(imgpath)+"/full/full/")
            #os.makedirs(self.outpath + "/iiif/images/"+self.shortenURI(imgpath)+"/full/full/0/")
            os.makedirs(self.outpath + "/iiif/mf/"+self.shortenURI(curind))
            f=open(self.outpath+"/iiif/mf/"+self.shortenURI(curind)+"/manifest.json","w",encoding="utf-8")
            f.write(json.dumps(curiiifmanifest))
            f.close()
        if thetypes!=None and len(thetypes)>0:
            return {"url":self.outpath+"/iiif/mf/"+self.shortenURI(curind)+"/manifest.json","label":str(label),"class":next(iter(thetypes))}
        return {"url":self.outpath+"/iiif/mf/"+self.shortenURI(curind)+"/manifest.json","label":str(label),"class":""}


    def generateIIIFCollections(self,outpath,imagespaths,prefixnamespace):
        iiifcollection={"@context":"http://iiif.io/api/presentation/3/context.json","id":outpath+"/iiif/collection/iiifcoll.json","type": "Collection", "label": {"en":["Collection: "+self.shortenURI(str(prefixnamespace))]},"items": []}
        if not os.path.exists(outpath + "/iiif/collection/"):
            os.makedirs(outpath + "/iiif/collection/")
        seenurls=set()
        collections={"main":{"@context":"http://iiif.io/api/presentation/3/context.json","id":outpath+"/iiif/collection/iiifcoll.json","type": "Collection", "label": {"en":["Collection: "+self.shortenURI(str(prefixnamespace))]},"items": []}}
        for imgpath in  sorted(imagespaths, key=lambda k: k['label'], reverse=False):
            curclass="main"
            if "class" in imgpath and imgpath["class"]!="":
                curclass=imgpath["class"]
                if curclass not in collections:
                    collections[curclass]={"@context":"http://iiif.io/api/presentation/3/context.json","id":outpath+"/iiif/collection/"+curclass+".json","type": "Collection", "label": {"en":["Collection: "+str(curclass)]},"items": []}
            if imgpath["url"] not in seenurls:
                if imgpath["label"]!="":
                    collections[curclass]["items"].append({"full":outpath + "/iiif/images/"+self.shortenURI(imgpath["url"].replace("/manifest.json",""))+"/full/full/0/default.jpg","id":imgpath["url"].replace(self.outpath,self.deploypath),"type": "Manifest","label":{"en":[imgpath["label"]+" ("+self.shortenURI(imgpath["url"].replace("/manifest.json","")[0:imgpath["url"].replace("/manifest.json","").rfind(".")])+")"]}})
                else:
                    collections[curclass]["items"].append({"full":outpath + "/iiif/images/"+self.shortenURI(imgpath["url"].replace("/manifest.json",""))+"/full/full/0/default.jpg","id":imgpath["url"].replace(self.outpath,self.deploypath),"type": "Manifest","label":{"en":[self.shortenURI(imgpath["url"].replace("/manifest.json",""))]}})
            seenurls=imgpath["url"]
        for coll in collections:
            if coll!="main":
                collections["main"]["items"].append(collections[coll])
        f=open(outpath+"/iiif/collection/iiifcoll.json","w",encoding="utf-8")
        f.write(json.dumps(collections["main"]))
        f.close()
        iiifindex="""<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://unpkg.com/mirador@latest/dist/mirador.min.js"></script></head><body><link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500"><div id="my-mirador"/><script type="text/javascript">var mirador = Mirador.viewer({"id": "my-mirador","manifests": {"collection/iiifcoll.json": {"provider": "Harvard University"}},"windows": [{"loadedManifest": "collection/iiifcoll.json","canvasIndex": 2,"thumbnailNavigationPosition": 'far-bottom'}]});</script></body></html>"""
        f=open(outpath+"/iiif/index.html","w",encoding="utf-8")
        f.write(iiifindex)
        f.close()

    def generateOGCAPIFeaturesPages(self,outpath,featurecollectionspaths,prefixnamespace,ogcapi,mergeJSON):
        if ogcapi:
            apihtml="<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><metaname=\"description\" content=\"SwaggerUI\"/><title>SwaggerUI</title><link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css\" /></head><body><div id=\"swagger-ui\"></div><script src=\"https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js\" crossorigin></script><script>const swaggerUrl = \""+str(self.deploypath)+"/api/index.json\"; const apiUrl = \""+str(self.deploypath)+"/\";  window.onload = () => {let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({spec: j,dom_id: '#swagger-ui'});}));};</script></body></html>"
            apijson={"openapi":"3.0.1","info":{"title":str(self.deploypath)+" Feature Collections","description":"Feature Collections of "+str(self.deploypath)},"servers":[{"url":str(self.deploypath)}],"paths":{}}
            apijson["paths"]["/api"]={"get": {"tags": ["Capabilities"],"summary": "api documentation","description": "api documentation","operationId": "openApi","parameters": [],"responses": {"default": {"description": "default response","content": {"application/vnd.oai.openapi+json;version=3.0": {},"application/json": {},"text/html": {"schema": {}}}}}}}
            apijson["paths"]["/license/dataset"]={}      
            apijson["components"]={"schemas":{"Conformance":{"type":"object","properties":{"conformsTo":{"type":"array","items":{"type":"string"}}},"xml":{"name":"ConformsTo","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"}},"Collection":{"type":"object","properties":{"id":{"type":"string","xml":{"name":"Id","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"}},"title":{"type":"string","xml":{"name":"Title","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"}},"description":{"type":"string","xml":{"name":"Description","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"}},"links":{"type":"array","xml":{"name":"link","namespace":"http://www.w3.org/2005/Atom"},"items":{"$ref":"#/components/schemas/Link"}},"extent":{"$ref":"#/components/schemas/Extent"},"itemType":{"type":"string"},"crs":{"type":"array","items":{"type":"string"}},"storageCrs":{"type":"string"}},"xml":{"name":"Collection","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"}},"Collections":{"type":"object","properties":{"links":{"type":"array","xml":{"name":"link","namespace":"http://www.w3.org/2005/Atom"},"items":{"$ref":"#/components/schemas/Link"}},"collections":{"type":"array","xml":{"name":"Collection","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"},"items":{"$ref":"#/components/schemas/Collection"}}},"xml":{"name":"Collections","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"}},"Extent":{"type":"object","properties":{"spatial":{"$ref":"#/components/schemas/Spatial"},"temporal":{"$ref":"#/components/schemas/Temporal"}},"xml":{"name":"Extent","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"}},"Link":{"type":"object","properties":{"href":{"type":"string","xml":{"attribute":True}},"rel":{"type":"string","xml":{"attribute":True}},"type":{"type":"string","xml":{"attribute":True}},"title":{"type":"string","xml":{"attribute":True}}},"xml":{"name":"link","namespace":"http://www.w3.org/2005/Atom"}},"Spatial":{"type":"object","properties":{"bbox":{"type":"array","items":{"type":"array","items":{"type":"number","format":"double"}}},"crs":{"type":"string","xml":{"attribute":True}}},"xml":{"name":"SpatialExtent","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"}},"Temporal":{"type":"object","properties":{"interval":{"type":"array","items":{"type":"string","format":"date-time"}},"trs":{"type":"string","xml":{"attribute":True}}},"xml":{"name":"TemporalExtent","namespace":"http://www.opengis.net/ogcapi-features-1/1.0"}},"LandingPage":{"type":"object"}}}
            landingpagejson={"title":"Landing Page","description":"Landing Page","links":[{
                "href": str(self.deploypath)+"/index.json",
                "rel": "self",
                "type": "application/json",
                "title": "this document as JSON"
            }, {
                "href": str(self.deploypath)+"/index.html",
                "rel": "alternate",
                "type": "text/html",
                "title": "this document as HTML"
            }, {
                "href": str(self.deploypath)+"/collections/",
                "rel": "data",
                "type": "application/json",
                "title": "Supported Feature Collections as JSON"
            }, {
                "href": str(self.deploypath)+"/collections/indexc.html",
                "rel": "data",
                "type": "text/html",
                "title": "Supported Feature Collections as HTML"
            },{"href":str(self.deploypath)+"/api/index.json","rel":"service-desc","type":"application/vnd.oai.openapi+json;version=3.0","title":"API definition"},{"href":str(self.deploypath)+"/api","rel":"service-desc","type":"text/html","title":"API definition as HTML"},{"href":str(self.deploypath)+"/conformance","rel":"conformance","type":"application/json","title":"OGC API conformance classes as Json"},{"href":str(self.deploypath)+"/conformance","rel":"conformance","type":"text/html","title":"OGC API conformance classes as HTML"}]}
            conformancejson={"conformsTo":["http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core","http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html","http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"]}
            apijson["paths"]["/"]={"get": {"tags": ["Capabilities"],"summary": "landing page","description": "Landing page of this dataset","operationId": "landingPage","parameters": [],"responses": {"default": {"description": "default response","content": {"application/json": {"schema": {"$ref": "#/components/schemas/LandingPage"}},"text/html": {"schema": {}}}}}}}
            apijson["paths"]["/conformance"]={"get": {"tags": ["Capabilities"],"summary": "supported conformance classes","description": "Retrieves the supported conformance classes","operationId": "conformance","parameters": [],"responses": {"default": {"description": "default response","content": {"application/json": {"schema": {"$ref": "#/components/schemas/Conformance"}},"text/ttl": {"schema":{}},"text/html": {"schema":{}}}}}}}
            collectionsjson={"collections":[],"links":[{"href":outpath+"collections/index.json","rel":"self","type":"application/json","title":"this document as JSON"},{"href":outpath+"collections/index.html","rel":"self","type":"text/html","title":"this document as HTML"}]}
            collectionshtml="<html><head></head><body><header><h1>Collections of "+str(self.deploypath)+"</h1></head>{{collectiontable}}<footer><a href=\"index.json\">This page as JSON</a></footer></body></html>"
            collectiontable="<table><thead><th>Collection</th><th>Links</th></thead><tbody>"
            apijson["paths"]["/collections"]={"get": {"tags": ["Collections"],"summary": "describes collections","description": "Describes all collections provided by this service","operationId": "collections","parameters": [],"responses":{"default": {"description": "default response","content": {"application/json": {"schema": {"$ref": "#/components/schemas/Collections"}},"text/ttl": {"schema": {}},"text/html": {"schema": {}}}}}}}
            if outpath.endswith("/"):
                outpath=outpath[0:-1]
            if not os.path.exists(outpath+"/api/"):
                os.makedirs(outpath + "/api/")
            if not os.path.exists(outpath+"/license/"):
                os.makedirs(outpath + "/license/")
            if not os.path.exists(outpath+"/collections/"):
                os.makedirs(outpath+"/collections/")
            if not os.path.exists(outpath+"/conformance/"):
                os.makedirs(outpath + "/conformance/")
        result = list()
        for coll in featurecollectionspaths:
            curcoll=None
            if os.path.exists(coll):
                with open(coll, 'r',encoding="utf-8") as infile:
                    curcoll=json.load(infile)
            if ogcapi:
                op=outpath+"/collections/"+coll.replace(outpath,"").replace("index.geojson","")+"/"
                op=op.replace(".geojson","")
                op=op.replace("//","/")
                if not os.path.exists(op):
                    os.makedirs(op)
                if not os.path.exists(op+"/items/"):
                    os.makedirs(op+"/items/")
                opweb=op.replace(outpath,self.deploypath)
                opwebcoll=opweb
                if opwebcoll.endswith("/"):
                    opwebcoll=opwebcoll[0:-1]
                opwebcoll=opwebcoll.replace("//","/")
                collectionsjson["collections"].append({"id":coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:],"title":featurecollectionspaths[coll]["name"],"links":[{"href":str(opweb.replace(".geojson","")+"/index.json").replace("//","/"),"rel":"collection","type":"application/json","title":"Collection as JSON"},{"href":str(opweb.replace(".geojson","")+"/").replace("//","/"),"rel":"collection","type":"text/html","title":"Collection as HTML"},{"href":str(opweb.replace(".geojson","")+"/index.ttl").replace("//","/"),"rel":"collection","type":"text/ttl","title":"Collection as TTL"}]})
                currentcollection={"title":featurecollectionspaths[coll]["name"],"id":coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:],"links":[],"itemType":"feature"}
                currentcollection["links"]=[{"href":opwebcoll+"/items/index.json","rel":"items","type":"application/json","title":"Collection as JSON"},{"href":opwebcoll+"/items/indexc.html","rel":"items","type":"text/html","title":"Collection as HTML"},{"href":opwebcoll+"/items/index.ttl","rel":"collection","type":"text/ttl","title":"Collection as TTL"}]
                if "bbox" in curcoll:
                    currentcollection["extent"]={"spatial":{"bbox":curcoll["bbox"]}}
                    collectionsjson["collections"][-1]["extent"]={"spatial":{"bbox":curcoll["bbox"]}}
                if "crs" in curcoll:
                    currentcollection["crs"]=curcoll["crs"]
                    collectionsjson["collections"][-1]["crs"]=curcoll["crs"]
                    currentcollection["extent"]["spatial"]["crs"]=curcoll["crs"]
                    collectionsjson["collections"][-1]["extent"]["spatial"]["crs"]=curcoll["crs"]
                apijson["paths"]["/collections/"+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:]).rstrip("/")]={"get":{"tags":["Collections"],"summary": "describes collection "+str(str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:])).rstrip("/"),"description": "Describes the collection with the id "+str(str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:])).rstrip("/"),"operationId": "collection-"+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:]),"parameters":[],"responses": {"default": {"description": "default response","content": {"application/json": {"schema": {"$ref": "#/components/schemas/Collections"},"example": None}}}}}}
                curcollrow="<tr><td><a href=\""+opweb.replace(".geojson","")+"/items/indexc.html\">"+str(featurecollectionspaths[coll]["name"])+"</a></td><td><a href=\""+opweb.replace(".geojson","")+"/items/indexc.html\">[Collection as HTML]</a>&nbsp;<a href=\""+opweb.replace(".geojson","")+"/items/\">[Collection as JSON]</a>&nbsp;<a href=\""+opweb.replace(".geojson","")+"/items/index.ttl\">[Collection as TTL]</a></td></tr>"
                f=open(op+"index.json","w",encoding="utf-8")
                f.write(json.dumps(currentcollection))
                f.close()
                f=open(op+"indexc.html","w",encoding="utf-8")
                f.write("<html><head></head><body><h1>"+featurecollectionspaths[coll]["name"]+"</h1><table><thead><tr><th>Collection</th><th>Links</th></tr></thead><tbody>"+str(curcollrow)+"</tbody></table></html>")
                f.close()
                collectiontable+=curcollrow
                if os.path.exists(coll):
                    try:
                        if os.path.exists(coll.replace("//","/")):
                            targetpath=self.generateRelativeSymlink(coll.replace("//","/"),str(op+"/items/index.json").replace("//","/"),outpath)
                            p = Path( str(op+"/items/index.json").replace("//","/") )
                            p.symlink_to(targetpath)
                        if os.path.exists(coll.replace("//","/").replace("index.geojson","index.ttl").replace("nonns_"+featurecollectionspaths[coll]["id"]+".geojson","nonns_"+featurecollectionspaths[coll]["id"]+".ttl")):
                            targetpath=self.generateRelativeSymlink(coll.replace("//","/").replace("index.geojson","index.ttl").replace("nonns_"+featurecollectionspaths[coll]["id"]+".geojson","nonns_"+featurecollectionspaths[coll]["id"]+".ttl"),str(op+"/items/index.ttl").replace("//","/"),outpath)
                            p = Path( str(op+"/items/index.ttl").replace("//","/") )
                            p.symlink_to(targetpath)
                        if os.path.exists(coll.replace("//","/").replace("index.geojson","index.html").replace("nonns_"+featurecollectionspaths[coll]["id"]+".geojson","nonns_"+featurecollectionspaths[coll]["id"]+".html")):
                            targetpath=self.generateRelativeSymlink(coll.replace("//","/").replace("index.geojson","index.html").replace("nonns_"+featurecollectionspaths[coll]["id"]+".geojson","nonns_"+featurecollectionspaths[coll]["id"]+".html"),str(op+"/items/indexc.html").replace("//","/"),outpath)
                            f=open(str(op+"/items/indexc.html"),"w")
                            f.write("<html><head><meta http-equiv=\"refresh\" content=\"0; url="+targetpath+"\" /></head></html>")
                            f.close()
                        print("symlinks created")
                    except Exception as e:
                        print("symlink creation error")
                        print(e)
                    apijson["paths"][str("/collections/"+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:])+"/items/index.json").replace("//","/")]={"get":{"tags":["Data"],"summary": "retrieves features of collection "+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:]).rstrip("/"),"description": "Retrieves features of collection  "+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:]),"operationId": "features-"+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:]),"parameters":[],"responses": {"default": {"description": "default response","content": {"application/geo+json": {"example": None }},"text/ttl": {"schema": {"example": None},"example": None},"text/html": {"schema": {"example": None},"example": None}}}}}
                    apijson["paths"][str("/collections/"+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:])+"/items/{featureId}/index.json").replace("//","/")]={"get":{"tags":["Data"],"summary": "retrieves feature of collection "+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:]).rstrip("/"),"description": "Retrieves one single feature of the collection with the id "+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:]),"operationId": "feature-"+str(coll.replace(outpath,"").replace("index.geojson","").replace(".geojson","")[1:]),"parameters":[{"name":"featureId","in": "path","required": True,"schema": {"type": "string"}}],"responses": {"default": {"description": "default response","content": {"application/geo+json": {"example": None }},"text/ttl": {"schema": {"example": None},"example": None},"text/html": {"schema": {"example": None},"example": None}}}}}
                    for feat in curcoll["features"]:
                        featpath=feat["id"].replace(prefixnamespace,"").replace("//","/")
                        try:
                            os.makedirs(str(op+"/items/"+str(self.shortenURI(feat["id"]))))
                            print("CHECKPATH: "+str(str(feat["id"].replace(prefixnamespace,outpath+"/")+"/index.json").replace("//","/")))
                            if os.path.exists(feat["id"].replace(prefixnamespace,outpath+"/")+"/index.json"):
                                targetpath=self.generateRelativeSymlink(featpath+"/index.json",str(op+"/items/"+str(self.shortenURI(feat["id"]))+"/index.json").replace("//","/"),outpath,True)
                                p = Path( str(op+"/items/"+str(self.shortenURI(feat["id"]))+"/index.json").replace("//","/") )
                                p.symlink_to(targetpath)
                            if os.path.exists(feat["id"].replace(prefixnamespace,outpath+"/")+"/index.ttl"):
                                targetpath=self.generateRelativeSymlink(featpath+"/index.ttl",str(op+"/items/"+str(self.shortenURI(feat["id"]))+"/index.ttl").replace("//","/"),outpath,True)
                                p = Path( str(op+"/items/"+str(self.shortenURI(feat["id"]))+"/index.ttl").replace("//","/") )
                                p.symlink_to(targetpath)
                            if os.path.exists(feat["id"].replace(prefixnamespace,outpath+"/")+"/index.html"):
                                targetpath=self.generateRelativeSymlink(featpath+"/index.html",str(op+"/items/"+str(self.shortenURI(feat["id"]))+"/index.html").replace("//","/"),outpath,True)
                                f=open(str(op+"/items/"+str(self.shortenURI(feat["id"])))+"/index.html","w")
                                f.write("<html><head><meta http-equiv=\"refresh\" content=\"0; url="+targetpath+"\" /></head></html>")
                                f.close()
                            print("symlinks created")
                        except Exception as e:
                            print("symlink creation error")
                            print(e)
                    if mergeJSON:
                        result.append(curcoll)
        collectiontable+="</tbody></table>"
        if mergeJSON:
            with open(outpath+"/features.js", 'w',encoding="utf-8") as output_file:
                output_file.write("var featurecolls="+json.dumps(result))
                #shutil.move(coll, op+"/items/index.json")
        if ogcapi:
            f=open(outpath + "/index.json","w",encoding="utf-8")
            f.write(json.dumps(landingpagejson))
            f.close()
            f=open(outpath + "/api/index.json","w",encoding="utf-8")
            f.write(json.dumps(apijson))
            f.close()
            f=open(outpath + "/api/api.html","w",encoding="utf-8")
            f.write(apihtml)
            f.close()
            f=open(outpath + "/collections/indexc.html","w",encoding="utf-8")
            f.write(collectionshtml.replace("{{collectiontable}}",collectiontable))
            f.close()
            f=open(outpath + "/collections/index.json","w",encoding="utf-8")
            f.write(json.dumps(collectionsjson))
            f.close()
            f=open(outpath + "/conformance/index.json","w",encoding="utf-8")
            f.write(json.dumps(conformancejson))
            f.close()
            
            
    def detectURIsConnectedToSubjects(self,subjectstorender,graph,prefixnamespace,corpusid,outpath,curlicense,baseurl):
        uristorender={}
        uritolabel={}
        for sub in subjectstorender:
            onelabel=""
            label=None
            added=[]
            for tup in graph.predicate_objects(sub):
                if str(tup[0]) in labelproperties:
                    if tup[1].language == self.labellang:
                        label = str(tup[1])
                        break
                    onelabel = str(tup[1])
                if isinstance(tup[1],URIRef) and prefixnamespace not in str(tup[1]) and "http://www.w3.org/1999/02/22-rdf-syntax-ns#" not in str(tup[1]):
                    if str(tup[1]) not in uristorender:
                        uristorender[str(tup[1])]={}
                    if str(tup[0]) not in uristorender[str(tup[1])]:
                        uristorender[str(tup[1])][str(tup[0])]=[]
                    for objtup in graph.predicate_objects(tup[1]):
                        if str(objtup[0]) in labelproperties:
                            uritolabel[str(tup[1])] = str(objtup[1])
                    toadd={"sub":sub,"label":onelabel}
                    added.append(toadd)
                    uristorender[str(tup[1])][str(tup[0])].append(toadd)
            for item in added:
                if label!=None:
                    item["label"]=label
                else:
                    item["label"]=onelabel
        #print(uristorender)
        for uri in uristorender:
            self.createHTML(outpath+"nonns_"+self.shortenURI(uri)+".html", None, URIRef(uri), baseurl, graph.subject_predicates(URIRef(uri)), graph, str(corpusid) + "_search.js", str(corpusid) + "_classtree.js", None, self.license, subjectstorender, Graph(),None,True,thelabel)


    def checkDepthFromPath(self,savepath,baseurl,subject):
        if savepath.endswith("/"):
            checkdepth = subject.replace(baseurl, "").count("/")
        else:
            checkdepth = subject.replace(baseurl, "").count("/")
        checkdepth+=1
        #print("Checkdepth: " + str(checkdepth))
        return checkdepth

    def getAccessFromBaseURL(self,baseurl,savepath):
        return savepath.replace(baseurl, "")


    def createHTML(self,savepath, predobjs, subject, baseurl, subpreds, graph, searchfilename, classtreename,uritotreeitem,curlicense,subjectstorender,postprocessing,nonnsmap=None,nonns=False,foundlabel=""):
        tablecontents = ""
        metadatatablecontents=""
        isodd = False
        geojsonrep=None
        epsgcode=""
        foundmedia={"audio":set(),"video":set(),"image":set(),"mesh":set()}
        savepath = savepath.replace("\\", "/")
        checkdepth=0
        if not nonns:
            checkdepth=self.checkDepthFromPath(savepath, baseurl, subject)
        logo=""
        if self.logoname!=None and self.logoname!="":
                logo="<img src=\""+self.logoname+"\" alt=\"logo\" width=\"25\" height=\"25\"/>&nbsp;&nbsp;"
        textannos = []
        foundvals=set()
        imageannos=set()
        image3dannos=set()
        predobjmap={}
        isgeocollection=False
        comment={}
        parentclass=None
        inverse=False
        dateprops=[]
        timeobj=None
        tablecontentcounter=-1
        metadatatablecontentcounter=-1
        if uritotreeitem!=None and str(subject) in uritotreeitem and uritotreeitem[str(subject)][-1]["parent"].startswith("http"):
            parentclass=str(uritotreeitem[str(subject)][-1]["parent"])
            if parentclass not in uritotreeitem:
                uritotreeitem[parentclass]=[{"id": parentclass, "parent": "#","type": "class","text": self.shortenURI(str(parentclass)),"data":{}}]
            #print(uritotreeitem[parentclass])
            uritotreeitem[parentclass][-1]["instancecount"]=0
        ttlf = Graph(bind_namespaces="rdflib")
        #ttlf = open(savepath + "/index.ttl", "w", encoding="utf-8")
        if parentclass!=None:
            uritotreeitem[parentclass][-1]["data"]["to"]={}
            uritotreeitem[parentclass][-1]["data"]["from"]={}
        hasnonns=set()
        thetypes=set()
        itembibtex=""
        if predobjs!=None:
            for tup in sorted(predobjs,key=lambda tup: tup[0]):
                if str(tup[0]) not in predobjmap:
                    predobjmap[str(tup[0])]=[]
                predobjmap[str(tup[0])].append(tup[1])
                if parentclass!=None and str(tup[0]) not in uritotreeitem[parentclass][-1]["data"]["to"]:
                    uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]={}
                    uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]["instancecount"] = 0
                if parentclass!=None:
                    uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]["instancecount"]+=1
                    uritotreeitem[parentclass][-1]["instancecount"]+=1
                if isinstance(tup[1],URIRef):
                    for item in graph.objects(tup[1],URIRef(self.typeproperty)):
                        thetypes.add(str(item))
                        if parentclass!=None:
                            if item not in uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]:
                                uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])][item] = 0
                            uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])][item]+=1
                    if baseurl not in str(tup[1]) and str(tup[0])!=self.typeproperty:	
                        hasnonns.add(str(tup[1]))	
                        if str(tup[1]) not in nonnsmap:
                            nonnsmap[str(tup[1])]=set()	
                        nonnsmap[str(tup[1])].add(subject)
            for tup in sorted(predobjmap):
                if self.metadatatable and tup not in labelproperties and self.shortenURI(str(tup),True) in metadatanamespaces:
                    thetable=metadatatablecontents
                    metadatatablecontentcounter+=1
                    if metadatatablecontentcounter%2==0:
                        thetable += "<tr class=\"odd\">"
                    else:
                        thetable += "<tr class=\"even\">"
                else:
                    thetable=tablecontents
                    tablecontentcounter+=1
                    if tablecontentcounter%2==0:
                        thetable += "<tr class=\"odd\">"
                    else:
                        thetable += "<tr class=\"even\">"
                if str(tup)==self.typeproperty and URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection") in predobjmap[tup]:
                    isgeocollection=True
                    uritotreeitem["http://www.opengis.net/ont/geosparql#FeatureCollection"][-1]["instancecount"] += 1
                elif str(tup)==self.typeproperty and URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection") in predobjmap[tup]:
                    isgeocollection=True
                    uritotreeitem["http://www.opengis.net/ont/geosparql#GeometryCollection"][-1]["instancecount"] += 1
                elif str(tup)==self.typeproperty:
                    for tp in predobjmap[tup]:
                        if str(tp) in bibtextypemappings:
                            itembibtex="<details><summary>[BIBTEX]</summary><pre>"+str(self.resolveBibtexReference(graph.predicate_objects(subject),subject,graph))+"</pre></details>"
                            break
                thetable=self.formatPredicate(tup, baseurl, checkdepth, thetable, graph,inverse)
                if str(tup) in labelproperties:
                    for lab in predobjmap[tup]:
                        if lab.language==self.labellang:
                            foundlabel=lab
                    if foundlabel=="":
                        foundlabel = str(predobjmap[tup][0])
                if str(tup) in commentproperties:
                    comment[str(tup)]=str(predobjmap[tup][0])
                if len(predobjmap[tup]) > 0:
                    thetable+="<td class=\"wrapword\">"
                    if len(predobjmap[tup])>1:
                        thetable+="<ul>"
                    labelmap={}
                    for item in predobjmap[tup]:
                        if ("POINT" in str(item).upper() or "POLYGON" in str(item).upper() or "LINESTRING" in str(item).upper()) and tup in valueproperties and self.typeproperty in predobjmap and URIRef("http://www.w3.org/ns/oa#WKTSelector") in predobjmap[self.typeproperty]:
                            image3dannos.add(str(item))
                        elif "<svg" in str(item):
                            foundmedia["image"].add(str(item))
                        elif "http" in str(item):
                            if isinstance(item,Literal):
                                ext = "." + ''.join(filter(str.isalpha, str(item.value).split(".")[-1]))
                            else:
                                ext = "." + ''.join(filter(str.isalpha, str(item).split(".")[-1]))
                            if ext in fileextensionmap:
                                foundmedia[fileextensionmap[ext]].add(str(item))
                        elif tup in valueproperties:
                            foundvals.add(str(item))
                        res=self.createHTMLTableValueEntry(subject, tup, item, ttlf, graph,
                                              baseurl, checkdepth,geojsonrep,foundmedia,imageannos,textannos,image3dannos,dateprops,inverse,nonns)
                        geojsonrep = res["geojson"]
                        foundmedia = res["foundmedia"]
                        imageannos=res["imageannos"]
                        textannos=res["textannos"]
                        image3dannos=res["image3dannos"]
                        if res["timeobj"]!=None and res["timeobj"]!=[]:
                            #print("RESTIMEOBJ: "+str(timeobj))
                            timeobj=res["timeobj"]
                        if res["label"] not in labelmap:
                            labelmap[res["label"]]=""
                        if len(predobjmap[tup]) > 1:
                            labelmap[res["label"]]+="<li>"+str(res["html"])+"</li>"
                        else:
                            labelmap[res["label"]] += str(res["html"])
                    for lab in sorted(labelmap):
                        thetable+=str(labelmap[lab])
                    if len(predobjmap[tup])>1:
                        thetable+="</ul>"
                    thetable+="</td>"
                else:
                    thetable += "<td class=\"wrapword\"></td>"
                thetable += "</tr>"
                if self.metadatatable and tup not in labelproperties and self.shortenURI(str(tup), True) in metadatanamespaces:
                    metadatatablecontents=thetable
                else:
                    tablecontents=thetable
                isodd = not isodd
        subpredsmap={}
        if subpreds!=None:
            for tup in sorted(subpreds,key=lambda tup: tup[1]):
                if str(tup[1]) not in subpredsmap:
                    subpredsmap[str(tup[1])]=[]
                subpredsmap[str(tup[1])].append(tup[0])
                if parentclass!=None and str(tup[1]) not in uritotreeitem[parentclass][-1]["data"]["from"]:
                    uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])]={}
                    uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])]["instancecount"] = 0
                if isinstance(tup[0],URIRef):
                    for item in graph.objects(tup[0],URIRef(self.typeproperty)):
                        if parentclass!=None:
                            if item not in uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])]:
                                uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])][item] = 0
                            uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])][item]+=1
            for tup in subpredsmap:
                if isodd:
                    tablecontents += "<tr class=\"odd\">"
                else:
                    tablecontents += "<tr class=\"even\">"
                tablecontents=self.formatPredicate(tup, baseurl, checkdepth, tablecontents, graph,True)
                if len(subpredsmap[tup]) > 0:
                    tablecontents += "<td class=\"wrapword\">"
                    if len(subpredsmap[tup]) > 1:
                        tablecontents += "<ul>"
                    labelmap={}
                    for item in subpredsmap[tup]:
                        if subjectstorender!=None and item not in subjectstorender and baseurl in str(item):
                            QgsMessageLog.logMessage("Postprocessing: " + str(item)+" - "+str(tup)+" - "+str(subject))
                            postprocessing.add((item,URIRef(tup),subject))
                        res = self.createHTMLTableValueEntry(subject, tup, item, None, graph,
                                                             baseurl, checkdepth, geojsonrep,foundmedia,imageannos,textannos,image3dannos,None,True,nonns)
                        foundmedia = res["foundmedia"]
                        imageannos=res["imageannos"]
                        image3dannos=res["image3dannos"]
                        if nonns and str(tup) != self.typeproperty:	
                            hasnonns.add(str(item))
                        if nonns:
                            geojsonrep=res["geojson"]
                        if res["label"] not in labelmap:
                            labelmap[res["label"]]=""
                        if len(subpredsmap[tup]) > 1:
                            labelmap[res["label"]]+="<li>"+str(res["html"])+"</li>"
                        else:
                            labelmap[res["label"]] += str(res["html"])
                    for lab in sorted(labelmap):
                        tablecontents+=str(labelmap[lab])
                    if len(subpredsmap[tup])>1:
                        tablecontents+="</ul>"
                    tablecontents += "</td>"
                else:
                    tablecontents += "<td class=\"wrapword\"></td>"
                tablecontents += "</tr>"
                isodd = not isodd
        if self.licenseuri!=None:
             ttlf.add((subject, URIRef("http://purl.org/dc/elements/1.1/license"), URIRef(self.licenseuri)))
        nonnslink=""
        if nonns:
            completesavepath = savepath.replace(":","_")
            nonnslink="<div>This page describes linked instances to the concept  <a target=\"_blank\" href=\"" + str(subject) + "\">" + str(foundlabel) + " ("+str(self.shortenURI(subject))+") </a> in this knowledge graph. It is defined <a target=\"_blank\" href=\""+str(subject)+"\">here</a></div>"
        else:
            completesavepath=savepath.replace(":","_") + "/index.html"
        if not nonns:
            ttlf.serialize(savepath + "/index.ttl", encoding="utf-8")
            with open(savepath + "/index.json", 'w', encoding='utf-8') as f:
                f.write(json.dumps(predobjmap))
                f.close()
        try:
            with open(completesavepath, 'w', encoding='utf-8') as f:
                rellink=self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,searchfilename,False)
                rellink2 = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,classtreename,False)
                rellink3 =self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,"style.css",False)
                rellink4 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "startscripts.js", False)
                rellink5 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "proprelations.js", False)
                epsgdefslink = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "epsgdefs.js", False)
                rellink7 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "vowl_result.js", False)
                if geojsonrep != None:
                    myexports=geoexports
                else:
                    myexports=nongeoexports
                if foundlabel != "":
                    f.write(htmltemplate.replace("{{logo}}",logo).replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{toptitle}}", foundlabel).replace(
                        "{{startscriptpath}}", rellink4).replace("{{versionurl}}",versionurl).replace("{{version}}",version).replace("{{bibtex}}",itembibtex).replace("{{vowlpath}}", rellink7).replace("{{proprelationpath}}", rellink5).replace("{{stylepath}}", rellink3).replace("{{indexpage}}","false").replace("{{title}}",
                                                                                                    "<a href=\"" + str(subject) + "\">" + str(foundlabel) + "</a>").replace(
                        "{{baseurl}}", baseurl).replace("{{tablecontent}}", tablecontents).replace("{{description}}","").replace(
                        "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{nonnslink}}",str(nonnslink)).replace("{{subject}}",str(subject)))
                else:
                    f.write(htmltemplate.replace("{{logo}}",logo).replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{indexpage}}","false").replace("{{toptitle}}", self.shortenURI(str(subject))).replace(
                        "{{startscriptpath}}", rellink4).replace("{{versionurl}}",versionurl).replace("{{version}}",version).replace("{{bibtex}}",itembibtex).replace("{{vowlpath}}", rellink7).replace("{{proprelationpath}}", rellink5).replace("{{stylepath}}", rellink3).replace("{{title}}","<a href=\"" + str(subject) + "\">" + self.shortenURI(str(subject)) + "</a>").replace(
                        "{{baseurl}}", baseurl).replace("{{description}}","").replace(
                        "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{nonnslink}}",str(nonnslink)).replace("{{subject}}",str(subject)))
                for comm in comment:
                    f.write(htmlcommenttemplate.replace("{{comment}}", self.shortenURI(comm) + ":" + comment[comm]))
                for fval in foundvals:
                    f.write(htmlcommenttemplate.replace("{{comment}}", "<b>Value:<mark>" + str(fval) + "</mark></b>"))
                if len(foundmedia["mesh"])>0 and len(image3dannos)>0:
                    for anno in image3dannos:
                        if ("POINT" in anno.upper() or "POLYGON" in anno.upper() or "LINESTRING" in anno.upper()):
                            f.write(threejstemplate.replace("{{wktstring}}",anno).replace("{{meshurls}}",str(list(foundmedia["mesh"]))))
                elif len(foundmedia["mesh"])>0 and len(image3dannos)==0:
                    print("Found 3D Model: "+str(foundmedia["mesh"]))
                    for curitem in foundmedia["mesh"]:
                        format="ply"
                        if ".nxs" in curitem or ".nxz" in curitem:
                            format="nexus"
                        f.write(image3dtemplate.replace("{{meshurl}}",curitem).replace("{{meshformat}}",format))
                        break                
                elif len(foundmedia["mesh"])==0 and len(image3dannos)>0:
                    for anno in image3dannos:
                        if ("POINT" in anno.upper() or "POLYGON" in anno.upper() or "LINESTRING" in anno.upper()):
                            f.write(threejstemplate.replace("{{wktstring}}",anno).replace("{{meshurls}}","[]"))
                carousel="image"
                if len(foundmedia["image"])>3:
                    carousel="carousel-item active"
                    f.write(imagecarouselheader)
                if len(imageannos)>0 and len(foundmedia["image"])>0:
                    iiifmanifestpaths["default"].append(self.generateIIIFManifest(outpath,foundmedia["image"],str(subject),prefixnamespace,foundlabel,comment,thetypes,predobjmap))
                    for image in foundmedia["image"]:
                        annostring=""
                        for anno in imageannos:
                            annostring+=anno.replace("<svg>","<svg style=\"position: absolute;top: 0;left: 0;\" class=\"svgview svgoverlay\" fill=\"#044B94\" fill-opacity=\"0.4\">")
                        f.write(imageswithannotemplate.replace("{{carousel}}",carousel+"\" style=\"position: relative;display: inline-block;").replace("{{image}}",str(image)).replace("{{svganno}}",annostring).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                        if len(foundmedia["image"])>3:
                            carousel="carousel-item"                  
                elif len(foundmedia["image"])>0:
                    iiifmanifestpaths["default"].append(self.generateIIIFManifest(outpath,foundmedia["image"],str(subject),prefixnamespace,foundlabel,comment,thetypes,predobjmap))
                    for image in foundmedia["image"]:                
                        if image=="<svg width=":
                            continue
                        if "<svg" in image:
                            if "<svg>" in image:
                                f.write(imagestemplatesvg.replace("{{carousel}}",carousel).replace("{{image}}", str(image.replace("<svg>","<svg class=\"svgview\">"))))
                            else:
                                f.write(imagestemplatesvg.replace("{{carousel}}",carousel).replace("{{image}}",str(image)))
                        else:
                            f.write(imagestemplate.replace("{{carousel}}",carousel).replace("{{image}}",str(image)).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                        if len(foundmedia["image"])>3:
                            carousel="carousel-item"
                if len(foundmedia["image"])>3:
                    f.write(imagecarouselfooter)
                if len(textannos) > 0:
                    for textanno in textannos:
                        if isinstance(textanno, dict):
                            if "src" in textanno:
                                f.write("<span style=\"font-weight:bold\" class=\"textanno\" start=\"" + str(
                                    textanno["start"]) + "\" end=\"" + str(textanno["end"]) + "\" exact=\"" + str(
                                    textanno["exact"]) + "\" src=\"" + str(textanno["src"]) + "\"><mark>" + str(textanno["exact"]) + "</mark></span>")
                            else:
                                f.write("<span style=\"font-weight:bold\" class=\"textanno\" start=\"" + str(
                                    textanno["start"]) + "\" end=\"" + str(textanno["end"]) + "\" exact=\"" + str(
                                    textanno["exact"]) + "\"><mark>" + str(textanno["exact"]) + "</mark></span>")
                for audio in foundmedia["audio"]:
                    f.write(audiotemplate.replace("{{audio}}",str(audio)))
                for video in foundmedia["video"]:
                    f.write(videotemplate.replace("{{video}}",str(video)))
                if geojsonrep!=None and not isgeocollection:
                    if uritotreeitem!=None and str(subject) in uritotreeitem:
                        uritotreeitem[str(subject)][-1]["type"]="geoinstance"
                    props=predobjmap
                    if timeobj!=None:
                        for item in timeobj:
                            dateprops.append(item)
                            props[item]=str(timeobj[item])
                    jsonfeat={"type": "Feature", 'id':str(subject),'name':foundlabel,'dateprops':dateprops, 'properties': props, "geometry": geojsonrep}
                    if epsgcode=="" and "crs" in geojsonrep:
                        epsgcode="EPSG:"+geojsonrep["crs"]
                    if len(hasnonns)>0:
                        self.geocache[str(subject)]=jsonfeat
                    f.write(maptemplate.replace("var ajax=true","var ajax=false").replace("{{myfeature}}","["+json.dumps(jsonfeat)+"]").replace("{{epsg}}",epsgcode).replace("{{baselayers}}",json.dumps(baselayers)).replace("{{epsgdefspath}}", epsgdefslink).replace("{{dateatt}}", ""))
                elif isgeocollection or nonns:
                    if foundlabel!=None and foundlabel!="":
                        featcoll={"type":"FeatureCollection", "id":subject,"name":str(foundlabel), "features":[]}
                    else:
                        featcoll={"type":"FeatureCollection", "id":subject,"name":self.shortenURI(subject), "features":[]}
                    thecrs=set()
                    dateatt=""
                    if isgeocollection and not nonns:
                        memberpred=URIRef("http://www.w3.org/2000/01/rdf-schema#member")
                        for memberid in graph.objects(subject,memberpred,True):
                            for geoinstance in graph.predicate_objects(memberid,True):
                                geojsonrep=None
                                if geoinstance!=None and isinstance(geoinstance[1], Literal) and (str(geoinstance[0]) in geoproperties or str(geoinstance[1].datatype) in geoliteraltypes):
                                    geojsonrep = self.processLiteral(str(geoinstance[1]), str(geoinstance[1].datatype), "")
                                    uritotreeitem[str(subject)][-1]["type"] = "geocollection"
                                elif geoinstance!=None and str(geoinstance[0]) in geopointerproperties:
                                    uritotreeitem[str(subject)][-1]["type"] = "featurecollection"
                                    for geotup in graph.predicate_objects(geoinstance[1],True):
                                        if isinstance(geotup[1], Literal) and (str(geotup[0]) in geoproperties or str(geotup[1].datatype) in geoliteraltypes):
                                            geojsonrep = self.processLiteral(str(geotup[1]), str(geotup[1].datatype), "")
                                if geojsonrep!=None:
                                    if uritotreeitem !=None and str(memberid) in uritotreeitem:
                                        featcoll["features"].append({"type": "Feature", 'id': str(memberid), 'name': uritotreeitem[str(memberid)][-1]["text"], 'dateprops':dateprops, 'properties': {},"geometry": geojsonrep})
                                    else:
                                        featcoll["features"].append({"type": "Feature", 'id': str(memberid), 'name': str(memberid),'dateprops':dateprops, 'properties': {}, "geometry": geojsonrep})
                                    if len(featcoll["features"][-1]["dateprops"])>0:
                                        dateatt=featcoll["features"][-1]["dateprops"][0]                             
                        if len(hasnonns)>0:
                            self.geocache[str(subject)]=featcoll
                    elif nonns:
                        for item in hasnonns:
                            if item in self.geocache:
                                featcoll["features"].append(self.geocache[item])
                                if len(self.geocache[item]["dateprops"])>0:
                                    dateatt=self.geocache[item]["dateprops"][0]
                                if "crs" in self.geocache[item]:
                                    thecrs.add(self.geocache[item]["crs"])
                    if len(featcoll["features"])>0:
                        featcoll["numberMatched"]=len(featcoll["features"])
                        featcoll["numberReturned"]=len(featcoll["features"])
                        featcoll["bbox"]=shapely.geometry.GeometryCollection([shapely.geometry.shape(feature["geometry"]) for feature in featcoll["features"]]).bounds
                        if len(thecrs)>0:
                            featcoll["crs"]="http://www.opengis.net/def/crs/EPSG/0/"+str(next(iter(thecrs)))
                        else:
                            featcoll["crs"]="http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                        if dateatt!="":
                            for feat in featcoll["features"]:
                                if dateatt not in feat["properties"]:
                                    feat["properties"][dateatt]=""
                        if self.localOptimized:
                            f.write(maptemplate.replace("var ajax=true","var ajax=false").replace("{{myfeature}}","["+json.dumps(featcoll)+"]").replace("{{baselayers}}",json.dumps(baselayers)).replace("{{epsgdefspath}}", epsgdefslink).replace("{{dateatt}}", dateatt))
                        else:
                            f.write(maptemplate.replace("{{myfeature}}","[\""+self.shortenURI(str(completesavepath.replace(".html",".geojson")))+"\"]").replace("{{baselayers}}",json.dumps(baselayers)).replace("{{epsgdefspath}}", epsgdefslink).replace("{{dateatt}}", dateatt))
                        with open(completesavepath.replace(".html",".geojson"), 'w', encoding='utf-8') as fgeo:
                            featurecollectionspaths[completesavepath.replace(".html",".geojson")]={"name":featcoll["name"],"id":featcoll["id"]}
                            fgeo.write(json.dumps(featcoll))
                            fgeo.close()
                f.write(htmltabletemplate.replace("{{tablecontent}}", tablecontents))	
                if metadatatablecontentcounter>=0:	
                    f.write("<h5>Metadata</h5>")	
                    f.write(htmltabletemplate.replace("{{tablecontent}}", metadatatablecontents))	
                f.write(htmlfooter.replace("{{exports}}",myexports).replace("{{license}}",curlicense).replace("{{bibtex}}",""))
                f.close()
        except Exception as inst:
            print("Could not write "+str(completesavepath))
            print(inst)            
        return [postprocessing,nonnsmap]

def resolveWildcardPath(thepath):
    result=[]
    if "/*" not in thepath:
        result.append(thepath)
        return result
    print(thepath)
    normpath=thepath.replace("*","")
    if os.path.exists(normpath):
        files=os.listdir(normpath)
        for file in files:
            print(file)
            if file.endswith(".ttl") or file.endswith(".owl") or file.endswith(".ttl") or file.endswith("n3") or file.endswith(".nt"):
                result.append(normpath+file)
    return result
            
prefixes={"reversed":{}}
if os.path.exists('prefixes.json'):
    with open('prefixes.json', encoding="utf-8") as f:
        prefixes = json.load(f)
   
prefixes["reversed"]["http://purl.org/cuneiform/"]="cunei"
prefixes["reversed"]["http://purl.org/graphemon/"]="graphemon"
prefixes["reversed"]["http://www.opengis.net/ont/crs/"]="geocrs"
prefixes["reversed"]["http://www.ontology-of-units-of-measure.org/resource/om-2/"]="om"
prefixes["reversed"]["http://purl.org/meshsparql/"]="msp"
prefixnsshort="suni"
prefixnamespace="http://purl.org/cuneiform/"
license=""
metadatatable=False
logourl=""
outpath=[]
nonnspages=False
labellang="en"
templatepath="resources/html/"
templatename="default"
createColl=False
createIndexPages=True
createVOWL=False
localOptimized=False
startconcept=None
ogcapifeatures=False
filestoprocess=[]
if len(sys.argv)<=1:
    print("No TTL file to process has been given as a parameter")
    exit()
if len(sys.argv)>1:
    if " " in sys.argv[1]:
        for itemm in sys.argv[1].split(" "):
            filestoprocess+=resolveWildcardPath(itemm)
    else:
        filestoprocess+=resolveWildcardPath(sys.argv[1])
print("Files to process: "+str(filestoprocess))
if len(sys.argv)>2:
    if " " in sys.argv[2]:
        for itemm in sys.argv[2].split(" "):
            outpath.append(itemm)
    else:
        outpath.append(sys.argv[2])
if len(sys.argv)>3:
    prefixnamespace=sys.argv[3]
if len(sys.argv)>4:
    prefixnsshort=sys.argv[4]
if len(sys.argv)>5:
    indexp=sys.argv[5]
    if indexp.lower()=="false":
        createIndexPages=False
if len(sys.argv)>6:
    indexp=sys.argv[6]
    if indexp.lower()=="true":
        createColl=True
if len(sys.argv)>7:
    labellang=sys.argv[7]
if len(sys.argv)>8:
    license=sys.argv[8]
if len(sys.argv)>9:
    logourl=sys.argv[9]
if len(sys.argv)>10:
    metap=sys.argv[10]
    if metap.lower()=="true":
        metadatatable=True
if len(sys.argv)>11:
    nonnsp=sys.argv[11]
    if nonnsp.lower()=="true":
        nonnspages=True
if len(sys.argv)>12:
    crvowl=sys.argv[12]
    if crvowl.lower()=="true":
        createVOWL=True
if len(sys.argv)>13:
    ogcapi=sys.argv[13]
    if ogcapi.lower()=="true":
        ogcapifeatures=True
if len(sys.argv)>14:
    startconcept=sys.argv[14]
if len(sys.argv)>15:
    deploypath=sys.argv[15]
if len(sys.argv)>16:
    templatepath=sys.argv[16]
    if templatepath.startswith("http") and templatepath.endswith(".zip"):
        with urlopen(templatepath) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                subfoldername=zfile.namelist()[0][0:zfile.namelist()[0].rfind('/')]
                zfile.extractall('mydownloadedtemplate/')
                templatepath="mydownloadedtemplate/"+subfoldername
                if subfoldername.endswith("/"):
                    subfoldername=subfoldername[0:-1]
                templatepath="mydownloadedtemplate/"+subfoldername[0:subfoldername.rfind('/')+1]
                templatename=subfoldername
                if templatepath.endswith("/"):
                    templatepath=templatepath[0:-1]
                print(templatepath)
                print(subfoldername)
                print(templatename)
if len(sys.argv)>17:
    templatename=sys.argv[17]
fcounter=0
for fp in filestoprocess:
    try:
        g = Graph()
        g.parse(fp)
        if fcounter<len(outpath):
            docgen=OntDocGeneration(prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath[fcounter],g,createIndexPages,createColl,metadatatable,nonnspages,createVOWL,ogcapifeatures,localOptimized,startconcept,deploypath,logourl,templatename)
        else:
            docgen=OntDocGeneration(prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath[-1],g,createIndexPages,createColl,metadatatable,nonnspages,createVOWL,ogcapifeatures,localOptimized,startconcept,deploypath,logourl,templatename)
        docgen.generateOntDocForNameSpace(prefixnamespace,dataformat="HTML")
    except Exception as inst:
     	print("Could not parse "+str(fp))
     	print(inst)
    fcounter+=1
curlicense=license
if docgen!=None:
    curlicense=docgen.licensehtml
print("Path exists? "+outpath[0]+'/index.html '+str(os.path.exists(outpath[0]+'/index.html')))
if not os.path.exists(outpath[0]+'/index.html'):
    indexf=open(outpath[0]+"/index.html","w",encoding="utf-8")
    nonnslink=""
    indexhtml = htmltemplate.replace("{{logo}}",logourl).replace("{{baseurl}}", prefixnamespace).replace("{{relativedepth}}","0").replace("{{toptitle}}","Index page").replace("{{title}}","Index page").replace("{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css")\
        .replace("{{classtreefolderpath}}",prefixnsshort + "_classtree.js").replace("{{baseurlhtml}}", ".").replace("{{nonnslink}}",str(nonnslink)).replace("{{proprelationpath}}", "proprelations.js").replace("{{scriptfolderpath}}", prefixnsshort+ '_search.js').replace("{{exports}}",nongeoexports).replace("{{versionurl}}",versionurl).replace("{{version}}",version).replace("{{bibtex}}","")
    indexhtml=indexhtml.replace("{{indexpage}}","true")	
    indexhtml+="<p>This page shows information about linked data resources in HTML. Choose the classtree navigation or search to browse the data</p>"
    indexhtml+="<table class=\"description\" border=1 id=indextable><thead><tr><th>Dataset</th></tr></thead><tbody>"
    subfolders= [f.path for f in os.scandir(outpath[0]) if f.is_dir()]
    print(subfolders)
    for path in subfolders:
        indexhtml+="<tr><td><a href=\""+path.replace(outpath[0]+"/","")+"/index.html\">"+path.replace(outpath[0]+"/","")+"</a></td></tr>"
    indexhtml+="</tbody></table>"
    indexhtml+=htmlfooter.replace("{{license}}",curlicense).replace("{{exports}}",nongeoexports).replace("{{bibtex}}","")
    #print(indexhtml)
    indexf.write(indexhtml)
    indexf.close()
