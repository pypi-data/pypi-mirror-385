# Copyright (c) 2021-2022, Ora Lassila & So Many Aircraft
# All rights reserved.
#
# See LICENSE for licensing information
#
# This module implements XMP support for RDFLib, and provides some useful helper
# functionality for reading, writing, and manipulating XMP metadata.
#
# Some code was copied from rdflib.plugins.parsers.xmlrdf.RDFXMLHandler and subsequently
# modified because RDFLib did not provide suitable extension points. That code is
# Copyright (c) 2002-2020, RDFLib Team and is distributed under a similar 3-clause BSD
# License; see this file: https://github.com/RDFLib/rdflib/blob/master/LICENSE
import csv
from base64 import b64decode
import gzip
from rdflib import RDF, URIRef, Literal, Namespace, Graph, plugin
from rdflib.exceptions import Error
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.parsers.rdfxml import RDFXMLHandler, ErrorHandler
from rdflib.plugins.serializers.rdfxml import PrettyXMLSerializer
from xml.sax import make_parser, handler, SAXParseException
import io
import re
from datetime import date, datetime, tzinfo, timedelta
import os.path
import pathlib
from urllib.parse import urlparse, unquote_plus
import rdfhelpers
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
import PIL.Image

TOOLNAME = "So Many Aircraft xmptools 0.4"
XMP_NS = "adobe:ns:meta/"
XMP_NAME = "xmpmeta"
XMP_TAG_OPEN = '<x:{0}'.format(XMP_NAME).encode('utf-8')
XMP_TAG_CLOSE = '</x:{0}>'.format(XMP_NAME).encode('utf-8')
XMP_TAG_OPEN_FULL = \
    '<x:{0} xmlns:x="{1}" x:xmptk="{2}">\n'.format(XMP_NAME, XMP_NS, TOOLNAME).encode('utf-8')

class FileTypeError(Error):
    def __init__(self, message, path, original=None):
        super().__init__(message.format(path, original))
        self.path = path
        self.original = original

class XMPHandler(RDFXMLHandler):
    def reset(self):
        super().reset()
        e = self.stack[1]
        e.start = self.envelope_element_start

    def envelope_element_start(self, name, qname, attrs):
        if name[0] == XMP_NS and name[1] == XMP_NAME:
            nxt = getattr(self, "next")
            nxt.start = self.document_element_start
            nxt.end = lambda n, qn: None
        else:
            raise FileTypeError("This is not XMP", None)

    def node_element_end(self, name, qname):
        # copied from rdflib.plugins.parsers.xmlrdf.RDFXMLHandler and
        # modified because there is now an extra element in the stack
        if self.parent.object and self.current != self.stack[3]:
            self.error("Repeated node-elements: %s" % "".join(name))
        self.parent.object = self.current.subject

class XMPParser(Parser):
    def __init__(self):
        self._parser = None
        super().__init__()

    def parse(self, source, sink, **args):
        parser = make_parser()
        parser.setFeature(handler.feature_namespaces, 1)
        xmp = XMPHandler(sink)
        xmp.setDocumentLocator(source)
        parser.setContentHandler(xmp)
        parser.setErrorHandler(ErrorHandler())
        content_handler = parser.getContentHandler()
        self._parser = parser
        preserve_bnode_ids = args.get("preserve_bnode_ids", None)
        if preserve_bnode_ids is not None:
            content_handler.preserve_bnode_ids = preserve_bnode_ids
        try:
            self._parser.parse(source)
        except SAXParseException as e:
            raise FileTypeError('Possibly not XMP because "{1}"', None, original=e)

class XMPSerializer(PrettyXMLSerializer):
    # We must subclass PrettyXMLSerializer, because the Adobe XMP toolkit expects
    # blank nodes to be serialized "in line" and not as separate Descriptions. The
    # plain XMLSerializer does not do this. :-(
    def __init__(self, store):
        super().__init__(store)
        self.xmpfile = None
        self.__serialized = None

    def serialize(self, stream, base=None, encoding=None, xmpfile=None, **args):
        self.xmpfile = URIRef(xmpfile)
        self.__serialized = {}
        stream.write(XMP_TAG_OPEN_FULL)
        xmlstream = io.BytesIO()
        super().serialize(xmlstream, base=base, encoding=encoding, **args)
        rdf = io.BytesIO(xmlstream.getvalue())
        rdf.readline()  # this is all ugly code, but we must skip the initial XML declaration
        for line in rdf.readlines():
            stream.write(line)
        stream.write(XMP_TAG_CLOSE)

    def relativize(self, uri):
        if uri == self.xmpfile:
            return URIRef("")  # this is here so we do not need to insert a misleading xml:base
        else:
            return super().relativize(uri)

    RDFLI = str(RDF) + "li"  # We cannot use RDF.li because RDF is a closed namespace

    def predicate(self, pred, obj, depth=1):
        # Replace actual container item predicates with <rdf:li> as per the XMP spec
        super().predicate(self.RDFLI if rdfhelpers.isContainerItemPredicate(pred) else pred,
                          obj, depth)

plugin.register("xmp", Parser, "xmptools", "XMPParser")
plugin.register("xmp", Serializer, "xmptools", "XMPSerializer")

XMP = Namespace("http://ns.adobe.com/xap/1.0/")
EXIF = Namespace("http://ns.adobe.com/exif/1.0/")
CRS = Namespace("http://ns.adobe.com/camera-raw-settings/1.0/")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCT = Namespace("http://purl.org/dc/terms/")
PHOTOSHOP = Namespace("http://ns.adobe.com/photoshop/1.0/")
XMPGIMG = Namespace("http://ns.adobe.com/xap/1.0/g/img/")
XMPMM = Namespace("http://ns.adobe.com/xap/1.0/mm/")

class DataNotFound(Error):
    pass

def makeFileURI(path):
    if isinstance(path, URIRef):
        return path
    else:
        return URIRef(pathlib.Path(os.path.abspath(path)).as_uri())

def makeFilePath(uri, scheme="file"):
    u = urlparse(uri)
    if u.scheme == scheme:
        return unquote_plus(u.path)
    else:
        raise ValueError("URI does not have '{}' scheme: {}".format(scheme, str(uri)))

def ensureFilePath(uri_or_path, scheme="file"):
    if uri_or_path.startswith(scheme):
        return makeFilePath(uri_or_path, scheme=scheme)
    else:
        # We'll take our chances
        return uri_or_path

def adjustTriple(triple, node_map, check_predicates=False):
    s, p, o = triple
    for node in node_map:
        if s == node:
            s = node_map[node]
        if check_predicates and p == node:
            p = node_map[node]
        if o == node:
            o = node_map[node]
    return s, p, o

def adjustNodes(node_map, source_graph, destination_graph=None, check_predicates=False):
    if destination_graph is None:
        destination_graph = type(source_graph)()
    for triple in source_graph:
        destination_graph.add(adjustTriple(triple, node_map, check_predicates=check_predicates))
    if isinstance(destination_graph, XMPMetadata):
        destination_graph.url = node_map[source_graph.url]
        destination_graph.sourceIsXMP = False
    return destination_graph

def adjustNodesInPlace(node_map, graph, check_predicates=False):
    for triple in list(graph.triples((None, None, None))):
        new_triple = adjustTriple(triple, node_map, check_predicates=check_predicates)
        if new_triple != triple:
            graph.add(new_triple)
            graph.remove(triple)
    if isinstance(graph, XMPMetadata):
        graph.url = node_map[graph.url]
    return graph

class iso8601:
    patterns =\
        {'iso8601': (("(?P<y>[0-9]{4})-(?P<mo>[0-9]{2})-(?P<d>[0-9]{2})"
                      "(?:T(?P<h>[0-9]{2}):(?P<m>[0-9]{2}):(?P<s>[0-9]{2})(?:[.](?P<f>[0-9]+))?"
                      "(?P<z>[-+Z](?:(?P<oh>[0-9]{2}):(?P<om>[0-9]{2}))?)?)?$"),
                     True),
         'exif':    (("(?P<y>[0-9]{4}):(?P<mo>[0-9]{2}):(?P<d>[0-9]{2})"
                      "(?:[ ](?P<h>[0-9]{2}):(?P<m>[0-9]{2}):(?P<s>[0-9]{2}))?"),
                     False)}

    def __init__(self):
        self.re = dict()
        self.tz = dict()
        for key in self.patterns:
            (pattern, self.tz[key]) = self.patterns[key]
            self.re[key] = re.compile(pattern)

    def parse(self, string):
        for key in self.re:
            match = self.re[key].match(string)
            if match:
                (y, mo, d, h, m, s, f) = match.group("y", "mo", "d", "h", "m", "s", "f")
                if not h:
                    return date(int(y), int(mo), int(d))
                else:
                    fraction = 0
                    if f:
                        n = len(f)
                        if n > 6:
                            raise ValueError("At most microsecond precision is allowed: ." + f)
                        else:
                            fraction = int(f) * 10 ** (6 - n)
                    if self.tz[key]:
                        (z, oh, om) = match.group("z", "oh", "om")
                        return datetime(int(y), int(mo), int(d), int(h), int(m), int(s), fraction,
                                        timezone(0 if z[0] == 'Z' else oh,
                                                 0 if z[0] == 'Z' else om,
                                                 z[0] == '-'))
                    else:
                        return datetime(int(y), int(mo), int(d), int(h), int(m), int(s), fraction,
                                        timezone())
        return None

class timezone(tzinfo):
    def __init__(self, oh=0, om=0, negative=False):
        m = (int(oh) if oh else 0) * 60 + (int(om) if om else 0)
        self.offset = timedelta(minutes=(-m if negative else m))

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return None

JPEG_EXTENSIONS = [".jpg", ".jpeg", ".JPG", ".JPEG"]
TIFF_EXTENSIONS = [".tif", ".tiff", ".TIF", ".TIFF"]
DNG_EXTENSIONS = [".dng", ".DNG"]
RAW_EXTENSIONS = [".cr2", ".CR2", ".cr3", ".CR3"]  # obviously wholly incomplete still
XMP_EXTENSIONS = [".xmp", ".XMP"]
PDF_EXTENSIONS = [".pdf", ".PDF"]

class XMPMetadata(rdfhelpers.TemplatedQueryMixin, Graph):
    iso8601 = iso8601()

    def __init__(self, url=None):
        self.initialized = False
        if url is None:
            self.url = None
            self.sourceIsXMP = False  # signals that content didn't come from an XMP sidecar file
            self.segment_count = 0
        else:
            self.url = rdfhelpers.URI(url)
            self.sourceIsXMP = True
            self.segment_count = 1
        super().__init__(identifier=self.url)
        if url is not None:
            self.read()

    @classmethod
    def fromFile(cls, path, ignore_sidecar_if_pdf=True):
        # LOGIC:
        #   1) Try a corresponding XMP sidecar file
        #   2) Try the image file itself
        #   3) Nothing
        base, extension = os.path.splitext(path)
        if ignore_sidecar_if_pdf and (extension in PDF_EXTENSIONS):
            return cls.fromPDF(path), path
        else:
            xmppath = base + ".xmp"
            try:
                # Make a valid URI, plain strings *could* be (partial, relative) URIs but having a
                # URI scheme ensures it actually is a URI
                return cls(makeFileURI(xmppath)), xmppath
            except (FileNotFoundError, FileTypeError):
                try:
                    return cls.fromImageFile(path), path
                except FileTypeError:
                    try:
                        return cls.fromPDF(path), path
                    except FileTypeError:
                        return None, None

    @classmethod
    def fromImageFile(cls, path):
        (_, extension) = os.path.splitext(path)
        if extension in JPEG_EXTENSIONS:
            return cls.fromJPEG(path)
        elif extension in TIFF_EXTENSIONS or extension in DNG_EXTENSIONS:
            with open(path, "rb") as file:
                # we'll take our chances...
                return cls.attemptToReadXMP(path, file)
        elif extension in RAW_EXTENSIONS:
            raise FileTypeError("Try reading from the sidecar file of {0}", path)
        else:
            raise FileTypeError("Unrecognized file type: {0}", path)

    @classmethod
    def fromJPEG(cls, path):
        with open(path, "rb") as file:
            if file.read(3) == b"\xff\xd8\xff":
                return cls.attemptToReadXMP(path, file)
            else:
                raise FileTypeError("Not a JPEG file: {0}", path)

    @classmethod
    def fromPDF(cls, path):
        (_, extension) = os.path.splitext(path)
        if extension in PDF_EXTENSIONS:
            with open(path, "rb") as file:
                doc = PDFDocument(PDFParser(file))
                if "Metadata" in doc.catalog:
                    xmp = cls()  # empty graph
                    xmp.url = makeFileURI(os.path.abspath(path))
                    xmp.parse(resolve1(doc.catalog["Metadata"]).get_data(),
                              format="xmp", publicID=xmp.url)
                    return xmp
                else:
                    return None
        else:
            raise FileTypeError("Probably not a PDF file: {0}", path)

    @classmethod
    def attemptToReadXMP(cls, path, file):
        stuff = file.read()
        xmp = None
        j = 0
        while True:
            try:
                i = stuff.index(XMP_TAG_OPEN, j)
            except ValueError:
                return xmp
            try:
                j = stuff.index(XMP_TAG_CLOSE, i) + len(XMP_TAG_CLOSE)
            except ValueError:
                return xmp
            if xmp is None:
                xmp = cls()  # empty graph
                xmp.url = makeFileURI(os.path.abspath(path))
            xmp.parse(io.BytesIO(stuff[i:j]), format="xmp", publicID=makeFileURI(path))
            xmp.initialized = True
            xmp.segment_count += 1

    def read(self):
        if self.sourceIsXMP:
            self.parse(self.url, format="xmp")
            self.initialized = True
        else:
            raise NotImplementedError("Use of read() with embedded metadata is not supported")

    def write(self, destination=None):
        if destination:
            # If destination is specified, it must be a pathname ending in ".xmp", or a stream
            if isinstance(destination, str):
                if not destination.endswith(".xmp"):
                    raise FileTypeError("Only XMP files can be written, not {0}", destination)
            elif not isinstance(destination, io.IOBase):
                raise ValueError("Unsupported destination: " + destination)
        elif not self.sourceIsXMP:
            raise NotImplementedError("Cannot write metadata back to " + str(self.url))
        else:
            destination = self.url
        self.serialize(destination=destination, format="xmp", xmpfile=self.url)

    @classmethod
    def fileModificationDate(cls, path):
        # Logic:
        #  - if path designates an XMP file, check only that
        #  - if path designates a media file, check that *and* the corresponding XMP file, return
        #    the newest modification date
        plain_path, ext = os.path.splitext(path)
        if ext in XMP_EXTENSIONS:
            ts = os.path.getmtime(path)
        else:
            try:
                ts = os.path.getmtime(plain_path + ".xmp")
                ts = max(os.path.getmtime(path), ts)
            except FileNotFoundError:
                ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts)

    def getOneStatement(self, predicate):
        for statement in self.triples((self.url, predicate, None)):
            return statement
        return None

    def getValue(self, predicate):
        statement = self.getOneStatement(predicate)
        return statement[2] if statement else None

    def getDate(self, predicate=XMP.MetadataDate):
        value = self.getValue(predicate)
        if value:
            date_candidate = value.value
            return (self.iso8601.parse(date_candidate)
                    if isinstance(date_candidate, str) else date_candidate)
        else:
            return None

    def setDate(self, timestamp=datetime.utcnow(), predicate=XMP.MetadataDate):
        self.set((self.url, predicate, Literal(timestamp)))

    def findDateCreated(self, predicates=None, error=DataNotFound):
        for p in predicates or [XMP.CreateDate, EXIF.DateTimeOriginal, PHOTOSHOP.DateCreated]:
            dt = self.getDate(p)
            if dt:
                return dt, p
        if error:
            raise error("Date not found")
        else:
            return None, None

    def getContainerItems(self, predicate):
        return rdfhelpers.getContainerItems(self, self.url, predicate)

    def setContainerItems(self, predicate, values, newtype=RDF.Seq):
        rdfhelpers.setContainerItems(self, self.url, predicate, values, newtype=newtype)

    def container2repeated(self, predicate,
                           new_predicate=None, value_mapper=rdfhelpers.identity,
                           remove_predicate=False, target_graph=None):
        # We understand that this messes with ordering
        if new_predicate is None:
            new_predicate = predicate
        if target_graph is None:
            target_graph = self
        items = self.getContainerItems(predicate)
        if items:
            if remove_predicate:
                self.setContainerItems(predicate, [])
            for item in items:
                target_graph.add((self.url, new_predicate, value_mapper(item)))
        return target_graph

    def repeated2container(self, predicate,
                           new_predicate=None, newtype=RDF.Seq, value_mapper=rdfhelpers.identity,
                           remove_predicate=False, source_graph=None):
        # We understand that this messes with ordering
        if new_predicate is None:
            new_predicate = predicate
        if source_graph is None:
            source_graph = self
        statements = source_graph.triples((self.url, predicate, None))
        if statements:
            if remove_predicate:
                for statement in statements:
                    self.remove(statement)
            self.setContainerItems(new_predicate, [value_mapper(o) for _, _, o in statements],
                                   newtype=newtype)

    def findOriginalImageURI(self, new_extension=None):
        original = (rdfhelpers.getvalue(self, self.url, CRS.RawFileName) or
                    rdfhelpers.getvalue(self, self.url, XMPMM.PreservedFileName))
        if new_extension is None:
            if original is None:
                raise ValueError("No new extension specified for {0}", self.url)
            else:
                url = urlparse(str(self.url))
                path, ext = os.path.splitext(url.path)
                _, new_extension = os.path.splitext(str(original))
                new_uri = url._replace(path=(path + new_extension)).geturl()
        else:
            base, _ = os.path.splitext(str(self.url))
            new_uri = base + new_extension
        return new_uri

    def adjustImageURI(self, new_extension=None, destination_graph=None, uri_mapper=None):
        # Logic:
        #   1. If no new extension specified, use crs:RawFileName value for the new extension
        #      - if no RawFileName found, signal an error
        #   2. Otherwise, replace old extension with the new extension provided
        new_uri = self.findOriginalImageURI(new_extension=new_extension)
        if uri_mapper:
            new_uri = uri_mapper(new_uri)
        node_map = {self.url: URIRef(new_uri)}
        if destination_graph is self:
            return adjustNodesInPlace(node_map, self)
        else:
            return adjustNodes(node_map, self, destination_graph=destination_graph)

    def cbd(self, resource=None, target=None, context=None):
        # Does not support reified statements (yet)
        return rdfhelpers.cbd(self, resource or self.url, target=target or Graph(), context=context)

    def archive(self, pathname):
        _, ext = os.path.splitext(pathname)
        with gzip.open((pathname + ".xmp.gz") if ext == '' else (pathname + ".gz"), "wb") as f:
            self.write(f)

    def getThumbnails(self, predicate=XMP.Thumbnails):
        thumbs = self.getContainerItems(predicate)
        if thumbs:
            thumbnails = list()
            for thumb in thumbs:
                with io.BytesIO(b64decode(rdfhelpers.getvalue(self, thumb, XMPGIMG.image))) as f:
                    with PIL.Image.open(f) as image:
                        # Must call load() here, because the byte stream is no longer open when the
                        # image is later accessed; PIL operations are lazy
                        image.load()
                        thumbnails.append(image)
            return thumbnails
        else:
            return None

def makeXMPfromCSV(input_csv, individual_files=True, file_key="file"):
    with open(input_csv, newline='') as file:
        graph = Graph() if individual_files else None
        for data in csv.DictReader(file):
            xmp = XMPMetadata()
            xmp.url = makeFileURI(data[file_key])
            for prop in data.keys():
                if prop != file_key:
                    # TODO: Should we use rdfhelpers.expandQName?
                    predicate = xmp.namespace_manager.expand_curie(prop)
                    xmp.add((xmp.url, predicate, Literal(data[prop])))
            if individual_files:
                xmp.write()
            else:
                graph += xmp
        return graph
