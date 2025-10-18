# XMP Tools

[![version](https://img.shields.io/pypi/v/xmptools)](https://pypi.org/project/xmptools/)
[![license](https://img.shields.io/pypi/l/xmptools)](https://gitlab.com/somanyaircraft/xmptools/-/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/xmptools/badge/?version=latest)](https://xmptools.readthedocs.io/en/latest/?badge=latest)

This package provides basic XMP support for [RDFLib](https://github.com/RDFLib/rdflib),
including parsing, modification, and serialization. XMP is Adobe's metadata format, based on
RDF. Trivially, XMP metadata is RDF serialized as
[RDF/XML](https://www.w3.org/TR/rdf-syntax-grammar/),
"wrapped" within a special XML element.

Adobe's XMP documentation
[can be found here](https://developer.adobe.com/xmp/docs/) and [here](https://github.com/adobe/XMP-Toolkit-SDK/tree/main/docs).

Unit tests with incomplete coverage are provided, as well as some [documentation](https://xmptools.readthedocs.io/en/latest/) and examples.

The parser and the serializer are implemented as RDFLib plugins. Because of limited
extensibility of RDFLib, we have copied some methods from RDFLib and modified them. The plugins
register themselves as `format="xmp"`. Normally, you do not have to know this, as we provide
convenience functionality for reading and writing XMP (see below).

## Future plans

Make the embedded metadata support more "robust". Writing of embedded metadata is not in the
plans, at least for now.

## Contact

Author: Ora Lassila <ora@somanyaircraft.com>

Copyright (c) 2021-2022 Ora Lassila and [So Many Aircraft](https://www.somanyaircraft.com/)
