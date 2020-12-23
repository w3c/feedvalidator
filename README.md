[![Build Status](https://travis-ci.com/w3c/feedvalidator.svg)](https://travis-ci.com/w3c/feedvalidator)

Some tests, and some functionality, will not be enabled unless a full set
of 32-bit character encodings are available through Python.

The feedvalidator relies on html5lib for parsing HTML.

The package 'iconvcodec' provides the necessary codecs, if your underlying
operating system supports them. Its web page is at
<http://cjkpython.i18n.org/#iconvcodec>, and a range of packages are
provided.

Python 2.3.x is required, for its Unicode support.

To run with Docker:
```bash
docker build -t feedvalidator .
docker run -p 8080:80 feedvalidator
```
