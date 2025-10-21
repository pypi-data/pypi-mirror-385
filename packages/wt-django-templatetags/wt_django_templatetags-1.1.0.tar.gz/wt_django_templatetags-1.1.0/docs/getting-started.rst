Getting Started
===============

Installation
------------

Install from GitHub (not yet available on PyPI).

To install the unstable development version from GitHub:

.. code-block:: bash

    pip install "wt-django-templatetags @ git+https://github.com/ian-wt/wt-django-templatetags.git"

Once installed, add ``wt_templatetags`` to ``INSTALLED_APPS`` in your settings module.

.. code-block:: python

    INSTALLED_APPS = [
        # other packages
        'wt_templatetags',
    ]

Development Installation
------------------------

To install as a repository so you can use ``git pull`` to retrieve updates:

.. code-block:: bash

    pip install -e git+https://github.com/ian-wt/wt-django-templatetags.git@master#egg=wt-django-templatetags

Then to later pull any changes:

.. code-block:: bash

    git -C $VIRTUAL_ENV/src/wt-django-templatetags pull

Or, cd into the package:

.. code-block:: bash

    cd $VIRTUAL_ENV/src/wt-django-templatetags
    git pull

Where ``$VIRTUAL_ENV`` is the path to your virtual environment directory.
If you're using standard names, this is usually ``venv`` or ``env``.

Alternative Configuration
-------------------------

You could instead register a particular module of templatetags directly in your
``TEMPLATES`` setting.

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    ...
                ],
                'libraries': {
                    'pagination_tags': 'wt_templatetags.templatetags.pagination_tags',
                }
            },
        },
    ]

This is most useful when you're only interested in using a limited set
of modules from the broader project and that's unlikely to change.
For simplicity, I recommend using the ``INSTALLED_APPS`` approach rather
than selectively registering modules.
