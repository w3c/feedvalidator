![Build Status](https://github.com/w3c/feedvalidator/actions/workflows/test.yml/badge.svg)

Some tests, and some functionality, will not be enabled unless a full set
of 32-bit character encodings are available through Python.

The feedvalidator relies on html5lib for parsing HTML and rdflib for parsing RDF.

Python 3 is required.

To run with Docker:
```bash
docker build -t feedvalidator .
docker run -p 8080:80 feedvalidator
```
