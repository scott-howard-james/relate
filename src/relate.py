import unittest
from collections import OrderedDict, Mapping, MutableMapping

class RelationError(Exception):
    pass

class Relation(MutableMapping):

    RESTRICTIONS = '1:1','1:M','M:1','M:M'
    INVERTED = {'1:1':'1:1','1:M':'M:1','M:1':'1:M','M:M':'M:M'}

    def __init__(self, init=None, restriction='M:M', ordered=False):
        if not ordered:
            self.forward = {}
            self.inverse = {}
        else:
            self.forward = OrderedDict()
            self.inverse = OrderedDict()

        if restriction not in Relation.RESTRICTIONS:
            raise RelationError('Invalid restriction:' + str(restriction))
        else:
            self.restriction=restriction

        if init is not None:
            self.update(init)

    def isordered(self):
        return isinstance(self.forward,OrderedDict)

    def __invert__(self):
        # NOTE: uses references .. not copies
        new = Relation(restriction=Relation.INVERTED[self.restriction])
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
        # NOTE: unconventional usage: ADD  instead of OVERWRITE

        if self.restriction in ['1:1','M:1']:
            if domain in self.forward:
                self._remove_domain(domain)
        if self.restriction in ['1:1','1:M']:
            if target in self.inverse:
                self._remove_range(target)

        self.forward.setdefault(domain,set()).add(target)
        self.inverse.setdefault(target,set()).add(domain)

    def __getitem__(self, domain):
        if self.restriction in ['1:1','M:1']:
            for target in self.forward[domain]:
                return target
        else:
            return self.forward[domain]

    def copy(self):
        r = Relation(restriction=self.restriction, ordered=self.isordered())
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
        s = []
        s.append('->')
        for d in self.forward:
            s.append(' '.join([str(d),'<',str(self.forward[d])]))
        s.append('<-')
        for t in self.inverse:
            s.append(' '.join([str(t),'<',str(self.inverse[t])]))
        return '\n'.join(s)

    def clear(self):
        self.__init__(restriction=self.restriction, ordered=self.isordered())

    def __len__(self):
        return len(self.forward)

    def values(self):
        return self.inverse.keys()

    def keys(self):
        return self.forward.keys()

    def __iter__(self):
        return self.forward.__iter__()

# Naming shortcuts

class Isomorphism(Relation):
    def __init__(self, init=None, ordered=False):
        Relation.__init__(self, init, restriction='1:1', ordered=ordered)

class Function(Relation):
    def __init__(self, init=None, ordered=False):
        Relation.__init__(self, init, restriction='M:1', ordered=ordered)

class Partition(Relation):
    def __init__(self, init=None, ordered=False):
        Relation.__init__(self, init, restriction='1:M', ordered=ordered)

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

    def test_restrictions(self):
        fruit = Relation(restriction='1:1')
        fruit['apple']='red'
        fruit['pear']='yellow'
        fruit['apple']='green'
        assert 'apple' in fruit
        fruit['watermelon']='green'
        assert 'apple' not in fruit
        fruit['papya']='green'
        assert 'watermelon' not in fruit

        # NOTE: setting restriction directly; not suggested usage as this can make objects inconsistent.

        fruit.restriction = 'M:1'
        fruit['papya']='green'
        fruit['rasberry']='blue'
        fruit['rasberry']='red'
        assert fruit['rasberry'] == 'red'
        fruit['cranberry']='red'
        assert 'rasberry' in fruit
        assert fruit['rasberry'] == 'red'

        fruit.restriction = '1:M'
        fruit['cranberry'] = 'round'
        fruit['lemon'] = 'sour'
        fruit['cranberry'] = 'sour'
        assert 'lemon' not in fruit
        assert len(fruit['cranberry']) > 1
        fruit['pear']='sweet'

        fruit.restriction = 'M:M'
        fruit['apple'] = 'sweet'
        assert len(fruit['apple']) == 1
        fruit['apple'] = 'fruit'
        assert len(fruit['apple']) == 2

if __name__ == '__main__':
     unittest.main()
