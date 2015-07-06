import unittest
from collections import OrderedDict, Mapping, MutableMapping

class RelationError(Exception):
    """
    Simply a marker to indicate source of exception
    """
    pass

class Relation(MutableMapping):
    """
    Relation() implements a discrete mathematical relation.  A relation a simply a pairing of elements of one set,
    the domain, with another, the range.  Rephrasing more formally, a relation is a collection of tuples (x,y) where
    x is in the domain and y is in the range.   A relation, implemented as code, can perform a variety of common tasks:

    - Inversion: quickly find the values(range) associated with a key(domain)
    - Partitioning: group values into unique buckets
    - Aliasing: maintain a unique pairing between keys and values
    - Tagging: associate two sets in an arbitrary manner

    These roughly correspond to the four cardinalities of a relation:

    - Many-to-one (M:1): a function, each range value having possibly multiple values in the domain
    - One-to-many (1:M): a categorization, where each element in the domain is associated with a unique group of values in the range
    - One-to-one (1:1): an isomorphism, where each element in the domain is uniquely identified with a single range value
    - Many-to-many (M:N): an unrestricted pairing of domain and range
    """

    CARDINALITIES = '1:1','1:M','M:1','M:N'

    # map the four cardinalities to their inverted cardinality
    INVERTED_CARDINALITY = {'1:1':'1:1','1:M':'M:1','M:1':'1:M','M:N':'M:N'}

    def __init__(self, init=None, cardinality='M:N', ordered=False):
        if not ordered:
            self.forward = {}
            self.inverse = {}
        else:
            self.forward = OrderedDict()
            self.inverse = OrderedDict()

        if cardinality not in Relation.CARDINALITIES:
            raise RelationError('Invalid cardinality:' + str(cardinality))
        else:
            self.cardinality=cardinality

        if init is not None:
            self.update(init)

    def isordered(self):
        return isinstance(self.forward,OrderedDict)

    def __invert__(self):
        """
        Create a shallow copy of a relation.
        Changes to inversion will affect original and vice-versa
        """
        new = Relation(cardinality=Relation.INVERTED_CARDINALITY[self.cardinality])
        new.inverse = self.forward
        new.forward = self.inverse
        return new

    @staticmethod
    def _remove(mapping, reference):
        empty=[]
        for key,values in mapping.items():
            if reference in values:
                mapping[key].remove(reference)
            if len(mapping[key]) == 0:
                empty.append(key) # mark for removal
        for e in empty:
            del mapping[e]

    def _remove_domain(self, key):
        del self.forward[key]
        Relation._remove(self.inverse,key)
    __delitem__ = _remove_domain

    def _remove_range(self, key):
        del self.inverse[key]
        Relation._remove(self.forward,key)

    def __setitem__(self, domain, target):
        """
        Set range for a domain value. Behavior dependent on cardinality:
        - M:1: assign/overwrite range to for domain, similar to dictionary behavior
        - 1:1: assign one domain uniquely to one range; remove pairing from other domains
        - M:N: append range to domain values, append domain to range values
        - 1:M: append range to domain values.  Remove range from other domains.
       """
        if not isinstance(domain,set):
            domain = [domain]
        if not isinstance(target,set):
            target = [target]

        for d in domain:
            for t in target:
                if self.cardinality in ['1:1','M:1']:
                    if d in self.forward:
                        self._remove_domain(d)
                if self.cardinality in ['1:1','1:M']:
                    if t in self.inverse:
                        self._remove_range(t)

                self.forward.setdefault(d,set()).add(t)
                self.inverse.setdefault(t,set()).add(d)

    def __getitem__(self, domain):
        """
        Get range for a domain value. Behavior dependent on cardinality
        - M:1: single value
        - 1:1: single value
        - M:N: set of values
        - 1:M: set of values
       """
        if self.cardinality in ['1:1','M:1']:
            for target in self.forward[domain]:
                return target
        else:
            return self.forward[domain]

    def copy(self):
        """
        Create one-level copy of a Relation
        """
        r = Relation(cardinality=self.cardinality, ordered=self.isordered())
        r.forward.update(self.forward)
        r.inverse.update(self.inverse)
        return r

    def extend(self, mapping):
        if not isinstance(mapping, Mapping):
            raise RelationError('Cannot extend using ' + str(mapping))
        else:
            for data in mapping:
                self[data] = mapping[data]
            return self

    def __str__ (self):

        def setstr(x):
            return '{' + ','.join(x) + '}'

        s = []
        s.append(self.cardinality)
        s.append('->')
        for d in self.forward:
            s.append(str(d)+':'+setstr(self.forward[d]))
        s.append('<-')
        for t in self.inverse:
            s.append(str(t)+':'+setstr(self.inverse[t]))
        return '\n'.join(s)

    def clear(self):
        self.__init__(cardinality=self.cardinality, ordered=self.isordered())

    def __len__(self):
        return len(self.forward)

    def values(self):
        """ All values in range """
        return self.inverse.keys()

    def keys(self):
        """ All values in domain """
        return self.forward.keys()

    def __iter__(self):
        return self.forward.__iter__()

# Naming shortcuts

class Isomorphism(Relation):
    def __init__(self, init=None, ordered=False):
        Relation.__init__(self, init, cardinality='1:1', ordered=ordered)

class Function(Relation):
    def __init__(self, init=None, ordered=False):
        Relation.__init__(self, init, cardinality='M:1', ordered=ordered)

class Partition(Relation):
    def __init__(self, init=None, ordered=False):
        Relation.__init__(self, init, cardinality='1:M', ordered=ordered)

# Unit Tests

class Relation_Tests(unittest.TestCase):

    def test_basic(self):
        fruit = Relation(ordered=True)
        fruit['apple']='red'
        fruit['apple']='shiny'
        fruit['apple']='round'
        fruit['melon']='round'
        fruit['melon']='green'
        fruit['watermelon']='red'
        fruit['watermelon']='green'
        fruit['watermelon']='ovoid'
        fruit['pear']='yellow'
        fruit['kiwi']='green'
        fruit['kiwi']='seedy'
        assert 'seedy' in ~fruit
        assert fruit.pop('kiwi') == set(['green','seedy'])
        assert 'seedy' not in fruit.values()
        for f in fruit:
            assert isinstance(f, str)
        assert list(fruit.keys()) == ['apple','melon','watermelon','pear']
        assert len(fruit) == 4
        assert len(~fruit) == 6
        assert len(fruit['apple']) == 3
        assert len(fruit['watermelon']) == 3
        assert 'pear' in (~fruit)['yellow']
        assert 'yellow' in fruit['pear']
        assert fruit['pear'] == set(['yellow'])
        del fruit['pear']
        assert len(fruit) == 3
        assert len(~fruit) == 5
        del fruit['apple']
        assert len(fruit) == 2
        assert len(~fruit) == 4
        foo = fruit.copy()
        assert len(~foo) == len(~fruit)
        assert len(foo) == len(fruit)
        assert len(fruit.keys()) == len(fruit)
        assert len(fruit.values()) == len(~fruit)
        assert len(fruit.items()) == len(fruit)
        assert fruit.get('armadillo') is None
        fruit.clear()
        assert len(fruit) == 0
        assert fruit.get('melon') is None

    def test_creation(self):
        m=Isomorphism({'a':1,'b':2,'c':11})
        mp = ~m
        assert mp[2] == 'b'
        m=Function({'a':1,'b':1,'c':11})
        mp = ~m
        assert mp[1] == {'b','a'}
        m=Partition({'a':1,'b':2,'c':11})
        m['a'] = 3
        mp = ~m
        assert mp[1] == 'a'
        assert mp[2] != 'a'
        assert mp[3] == 'a'

    def test_composite(self):
        fruits = {'apple':'red','cherry':'red','strawberry':'red','banana':'yellow'}
        fruit = Relation(fruits)
        assert len(fruit) == len(fruits)
        more = {'yellow':'pear','pomegranate':'red','watermelon':'seedy'}
        fruit.extend(more)
        assert len(fruit) == len(more) + len(fruits)
        even_more = Isomorphism({'papya':'starchy','grape':'tangy'})
        fruit.extend(even_more)
        assert len(fruit) == len(even_more) + len(more) + len(fruits)

    def test_CARDINALITIES(self):
        fruit = Relation(cardinality='1:1')
        fruit['apple']='red'
        fruit['pear']='yellow'
        fruit['apple']='green'
        assert 'apple' in fruit
        fruit['watermelon']='green'
        assert 'apple' not in fruit
        fruit['papya']='green'
        assert 'watermelon' not in fruit

        fruit = Relation(fruit, cardinality='M:1')
        fruit['papya']='green'
        fruit['rasberry']='blue'
        fruit['rasberry']='red'
        assert fruit['rasberry'] == 'red'
        fruit['cranberry']='red'
        assert 'rasberry' in fruit
        assert fruit['rasberry'] == 'red'

        fruit = Relation(fruit, cardinality='1:M')
        fruit['cranberry'] = 'round'
        fruit['lemon'] = 'sour'
        fruit['cranberry'] = 'sour'
        assert 'lemon' not in fruit
        assert len(fruit['cranberry']) > 1
        fruit['pear']='sweet'
        assert (~fruit)['sweet'] == 'pear'

        fruit = Relation(fruit, cardinality='M:N')
        fruit['apple'] = 'sweet'
        assert len((~fruit)['sweet']) == 2
        fruit['apple'] = 'fruit'
        assert len(fruit['apple']) == 2

if __name__ == '__main__':
     unittest.main()
