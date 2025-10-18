# Copyright (c) 2021, Ora Lassila & So Many Aircraft
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

from xmptools.xmptools import makeFileURI, makeFilePath, ensureFilePath, XMPMetadata
from xmptools.xmptools import DC, DCT, XMP, EXIF, CRS, PHOTOSHOP, XMPGIMG, XMPMM
from xmptools.xmptools import JPEG_EXTENSIONS, TIFF_EXTENSIONS, RAW_EXTENSIONS, DNG_EXTENSIONS
from xmptools.xmptools import XMP_EXTENSIONS, PDF_EXTENSIONS
from xmptools.xmptools import FileTypeError, XMPParser, XMPSerializer

__all__ = [
    'makeFileURI', 'makeFilePath', 'ensureFilePath', 'XMPMetadata',
    'DC', 'DCT', 'XMP', 'EXIF', 'CRS', 'PHOTOSHOP', 'XMPGIMG', "XMPMM",
    'JPEG_EXTENSIONS', 'TIFF_EXTENSIONS', 'RAW_EXTENSIONS', 'DNG_EXTENSIONS',
    'XMP_EXTENSIONS', 'PDF_EXTENSIONS',
    'FileTypeError', 'XMPParser', 'XMPSerializer'
]
