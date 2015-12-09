from __future__ import absolute_import

from collections import OrderedDict


class LastUpdatedOrderedDict(OrderedDict):

    '''
    Store items in the order the keys were last added
    Extracted from the OrderedDict receipes:

        https://docs.python.org/2/library/collections.html#ordereddict-examples-and-recipes

    > This ordered dictionary variant remembers the order the keys were last inserted. If a new
    > entry overwrites an existing entry, the original insertion position is changed and moved to
    > the end.
    '''

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value)

    def __repr__(self):
        return dict(self).__repr__()
