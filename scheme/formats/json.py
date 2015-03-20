from __future__ import absolute_import

import json

from scheme.format import Format

__all__ = ('Json',)

class Json(Format):
    extensions = ['.json']
    mimetype = 'application/json'
    name = 'json'

    @classmethod
    def serialize(cls, value):
        return json.dumps(value)

    @classmethod
    def unserialize(cls, value):
        return json.loads(value)
