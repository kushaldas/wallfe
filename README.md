wallfe
======

A personal feed reader.


Hacking on wallfe
-----------------

Prerequisites
~~~~~~~~~~~~~
    * virtualenvwrapper

Install virtualenvwrapper::

   $ sudo yum install python-virtualenvwrapper

Setting up the stack
~~~~~~~~~~~~~~~~~~~~

Use a virtualenv::

    $ mkvirtualenv wallfe
    $ workon wallfe

Install dependencies::

    $ pip install -r requirements.txt

Starting the development server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $ python runserver.py
