from .geoexporter import GeoExporter
from .graphexporter import GraphExporter
from .miscexporter import MiscExporter

class ExporterUtils:

    rdfformats = ["TTL", "TRIX", "TRIG", "N3", "NQ", "NT", "XML", "JSON-LD"]

    exportToFunction = {"CYPHER": GraphExporter.convertTTLToCypher, "GML": GraphExporter.convertTTLToGML,
                        "GEXF": GraphExporter.convertTTLToGEXF,
                        "GDF": GraphExporter.convertTTLToTGF, "DOT": GraphExporter.convertTTLToDOT,
                        "NET": GraphExporter.convertTTLToNET,
                        "GRAPHML": GraphExporter.convertTTLToGraphML, "GeoJSON": GeoExporter.convertTTLToGeoJSON,
                        "JGF": GraphExporter.convertTTLToJGF, "TGF": GraphExporter.convertTTLToTGF,
                        "TLP": GraphExporter.convertTTLToTLP,
                        "TTL": GraphExporter.serializeRDF, "TRIG": GraphExporter.serializeRDF,
                        "xml": GraphExporter.serializeRDF,
                        "TRIX": GraphExporter.serializeRDF, "NT": GraphExporter.serializeRDF,
                        "N3": GraphExporter.serializeRDF,
                        "NQ": GraphExporter.serializeRDF, "CSV": MiscExporter.convertTTLToCSV,
                        "TSV": MiscExporter.convertTTLToCSV}