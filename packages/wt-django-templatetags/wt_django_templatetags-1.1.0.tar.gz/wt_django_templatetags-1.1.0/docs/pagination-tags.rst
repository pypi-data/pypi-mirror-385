Pagination Tags
===============
To use ``pagination_tags`` in your project, load the module with
`{% load pagination_tags %}`.

relative_url
------------

.. code-block:: html

   {% relative_url page_index [field_name] [urlencode] %}

For detailed parameter information, see :ref:`relative-url-api`.

To use the ``relative_url`` tag, you need to pass a page index. This could be
a number or the string ``'last'`` if the index is in the final position of
the paginated ``QuerySet``. The tag additionally accepts optional arguments
for ``field_name`` and ``urlencode``.

Most often, you'll leave the ``field_name`` parameter alone since the default
value of ``'page'`` is fairly semantic as it is. However, this value can be
overridden in your views so make sure your views and the ``field_name``
are consistent.

Last, the ``urlencode`` parameter is used to preserve existing query strings.
If your view doesn't handle query strings, you can omit this parameter.

Example
~~~~~~~

.. code-block:: html

    <a href="{% relative_url page_obj.next_page_number %}">Next Page</a>

To extend this example further we can supply values to override the defaults:

.. code-block:: html

    <a href="{% relative_url page_obj.next_page_number 'page' request.GET.urlencode %}">Next Page</a>

Common Usage
~~~~~~~~~~~~

In a pagination template:

.. code-block:: html

   {% if page_obj.has_previous %}
       <a href="{% relative_url page_obj.previous_page_number %}">Previous</a>
   {% endif %}

   {% if page_obj.has_next %}
       <a href="{% relative_url page_obj.next_page_number %}">Next</a>
   {% endif %}