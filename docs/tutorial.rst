Tutorial
========

Create a schema
---------------

Let's start by creating a fairly simple schema. Our running example will be an API for a simple account management system.

    >>> from scheme import *
    >>> account = Structure({
            'name': Text(description='the name for the account', nonempty=True),
            'email': Email(),
            'gender': Enumeration('male female'),

            'active': Boolean(default=True),
            'interests': Sequence(Text(nonempty=True), unique=True),
            'logins': Integer(minimum=0, default=0),
        }, name='account')


