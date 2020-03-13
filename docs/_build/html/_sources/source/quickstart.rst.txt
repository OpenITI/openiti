Quick start
===========

Installation
------------

Use pip to install the openiti library: with Python and pip installed, write in a command line window: 

``pip install openiti``

Examples
--------

Remove diacritics from text::

    >>> from openiti.helper.ara import deNoise
    >>> s = 'بِسْمِ الْلّه الْرَحْمنِ الْرَحٍيْمِ'
    >>> deNoise(s)
    'بسم الله الرحمن الرحيم'



