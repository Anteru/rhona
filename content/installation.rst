Getting started
===============

Requirements
------------

**Rhona** requires Python 3.4 or later. On the browser-side, a recent browser with support for `flexbox <http://caniuse.com/#feat=flexbox>`_ is needed for the default theme.

Installation
------------

Create a virtual environment and install ``docutils``, ``pygments`` and ``tornado``. Using ``pip``, you can install them in one go using the following command line::

	pip install -r requirements.txt

Now you can run **Rhona** by executing::

	python rhona.py

It will print the current listen port on the command line. Open your web-browser and open  ``localhost`` at the specified port and see the Wiki.

Editing content
---------------

Content is stored in `reStructedText <http://docutils.sourceforge.net/rst.html>`_ in the ``content`` subfolder. Creating a file with the ``.rst`` extension is enough to make it immediately visible to **Rhona**. Some special markup is supported to link between topics and to static files.

Content links
^^^^^^^^^^^^^

Use references with ``/page/name`` to link relative to the ``content`` directory, and ``./page/name`` to link relative to the current file.
