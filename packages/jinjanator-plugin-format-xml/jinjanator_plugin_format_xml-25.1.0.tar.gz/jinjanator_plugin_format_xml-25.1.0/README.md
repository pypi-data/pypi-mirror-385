# jinjanator-plugin-format-xml

<a href="https://opensource.org"><img height="150" align="left" src="https://opensource.org/files/OSIApprovedCropped.png" alt="Open Source Initiative Approved License logo"></a>
[![CI](https://github.com/kpfleming/jinjanator-plugin-format-xml/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kpfleming/jinjanator-plugin-format-xml/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-31019/)
[![License - Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-9400d3.svg)](https://spdx.org/licenses/Apache-2.0.html)
[![Code Style - Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)
[![Types - Mypy](https://img.shields.io/badge/Types-Mypy-blue.svg)](https://github.com/python/mypy)
[![Code Quality - Ruff](https://img.shields.io/badge/Code%20Quality-Ruff-red.svg)](https://github.com/astral-sh/ruff)
[![Project Management - Hatch](https://img.shields.io/badge/Project%20Management-Hatch-purple.svg)](https://github.com/pypa/hatch)
[![Testing - Pytest](https://img.shields.io/badge/Testing-Pytest-orange.svg)](https://github.com/pytest-dev/pytest)

This repo contains `jinjanator-plugin-format-xml`, a plugin which
provides an XML parser for the [jinjanator](https://github.com/kpfleming/jinjanator) tool.

Open Source software: [Apache License 2.0](https://spdx.org/licenses/Apache-2.0.html)

## &nbsp;
<!-- fancy-readme start -->

This plugin allows jinjanator to parse XML data for processing in
templates. The format can be selected using `--format xml` or
autoselected by using a data file with a name ending with `.xml`.

## Installation

```
pip install jinjanator-plugin-format-xml
```

## Usage

Suppose you have an NGINX configuration file template, `nginx.j2`:

```jinja2
server {
  listen 80;
  server_name {{ nginx.hostname }};

  root {{ nginx.webroot }};
  index index.htm;
}
```

And you have an XML file with the data, `nginx.xml`:

```xml
<nginx>
  <hostname>
    localhost
  </hostname>
  <webroot>
    /var/www/project
  </webroot>
</nginx>
```

This is how you render it into a working configuration file:

```bash
$ jinjanate nginx.j2 nginx.xml > nginx.conf
```

## Options

* `process-namespaces`: configures the XML parser to replace namespace
  references in element names with the corresponding namespaces from
  `xmlns` attributes in the top-level element in the document.
<!-- fancy-readme end -->

## Chat

If you'd like to chat with the jinjanator community, join us on
[Matrix](https://matrix.to/#/#jinjanator:km6g.us)!

## Credits

["Standing on the shoulders of
giants"](https://en.wikipedia.org/wiki/Standing_on_the_shoulders_of_giants)
could not be more true than it is in the Python community; this
project relies on many wonderful tools and libraries produced by the
global open source software community, in addition to Python
itself. I've listed many of them below, but if I've overlooked any
please do not be offended :-)

* [Black](https://github.com/psf/black)
* [Hatch-Fancy-PyPI-Readme](https://github.com/hynek/hatch-fancy-pypi-readme)
* [Hatch](https://github.com/pypa/hatch)
* [Mypy](https://github.com/python/mypy)
* [Pytest](https://github.com/pytest-dev/pytest)
* [Ruff](https://github.com/astral-sh/ruff)
* [Towncrier](https://github.com/twisted/towncrier)
