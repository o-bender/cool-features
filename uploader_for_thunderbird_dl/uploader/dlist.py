class dlistNode(object):
    next  = None
    prev  = None
    value = None

    def __init__(self, value, next=None, prev=None):
        super(dlistNode, self).__init__()
        self.value = value
        if (next is None) and (prev is None):
            self.next = self
            self.prev = self
        elif next is None:
            self.prev = prev
            self.next = prev
        elif prev is None:
            self.next = next #if type(next) if dlistNode else dlistNode(next, None, self)
            self.prev = next
        else:
            self.next = next
            self.prev = prev

    def __str__(self):
        return str( self.value )


class dlist(object):
    first = None
    last  = None
    current = None

    def __init__(self, lst):
        super(dlist, self).__init__()
        for item in lst:
            self.append(item)

    def append(self, item):
        if self.last:
           self.last.next = dlistNode( item, self.first, self.last )
           self.last = self.last.next
           self.first.prev = self.last
        else:
           self.last = dlistNode( item )
           self.first = self.last

    def prepend(self, item):
        if self.first:
           self.first.prev = dlistNode( item, self.first, self.last )
           self.first = self.first.prev
        else:
           self.first = dlistNode( item )
           self.last = self.first

    def insert(self, item, pos):
        for i,iter in enumerate(self):
            if i == pos:
                iter.value = item
            if iter == self.last: break

    def __iter__(self):
        self.current = self.first
        return self

    # For python 2.*
    def next(self):
        fib = self.current
        self.current = self.current.next
        return fib

    # For python 3.*
    def __next__(self):
        return self.next()

    def __getitem__(self, item):
        for iter in self:
            if iter.value == item:
                return iter
            if self.last == iter:
                return None

    def __len__(self):
        count = 0
        for iter in self:
            if self.last == iter:
                return count
            count += 1

if __name__ == '__main__':
    a = dlist([1,2,3,4,5])
    a.append(10)
    a.append(11)
    a.append(12)
    a.append(13)
    a.append(14)
    a.append(15)

    a.prepend(100)
    a.prepend(101)
    a.prepend(102)
    a.prepend(103)

    a.insert(0, 2)
    a.insert(333, 0)
    a.insert(999, 5)

    for i in a:
        if a.last == i: break
