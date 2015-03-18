Test header
===========

This is some example text. It contains **bold**, *italic* and ``monospace`` text. We can use everything `reStructedText <http://docutils.sourceforge.net/rst.html>`_ provides, including blocks like:

.. note:: This is an example note.

Example code
------------

This is a subsection, and should render with a smaller font size. In this section, we show some example code:

.. code-block:: c++

	class Foo {
		public:
			int bar () const;
			virtual bool baz () const;
	}

.. code-block:: python

	class LinkFixupVisitor(docutils.nodes.SparseNodeVisitor):
		def visit_reference (self, n):
			if n ['refuri'] [0] == '/':
				n ['refuri'] = '/wiki' + n ['refuri']

Another subsection
------------------

Here is an internal link to the `installation page </installation>`_
