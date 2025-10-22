sphinx_gemini_builder
#####################

Build `Gemini <https://gemini.circumlunar.space/>`_ blog from
`Sphinx <https://www.sphinx-doc.org>`_ with
`ABlog <https://ablog.readthedocs.io/>`_ compatibility.


Gemini is a simple protocol between gopher and web. Sphinx is
a documentation tool. This project builds Gemini capsule from
Sphinx documentation. It supports ABlog extensions and manage
Atom feeds.

Installation and use
--------------------

Install with `python setup.py install` and do `make gemini` in
your project.


You can add a `gemini_footer` in config, formatted under the
Gemini specification. You need to set `gemini_baseurl` for
good url in Atom feeds.


This project contains some parts of code from Sphinx and from
ABlog.
