class Handle:
    """Stable reference to an inserted key, valid until that key is removed."""
    __slots__ = ("node",)

    @property
    def key(self):
        return self.node.key


class Node:
    __slots__ = ("key", "handle", "degree", "parent", "child", "sibling")

    def __init__(self, key):
        self.key = key
        self.handle = Handle()
        self.handle.node = self
        self.degree = 0
        self.parent = None
        self.child = None    # leftmost child
        self.sibling = None  # next root / next sibling


class BinomialHeap:
    """Min-heap. insert returns a Handle usable in decrease_key / delete."""

    def __init__(self):
        self.head = None
        self.n = 0

    @classmethod
    def build(cls, keys):
        h = cls()
        for k in keys:
            h.insert(k)
        return h

    def __len__(self):
        return self.n

    # ---------- helpers ----------
    @staticmethod
    def _swap(a, b):
        a.key, b.key = b.key, a.key
        a.handle, b.handle = b.handle, a.handle
        a.handle.node, b.handle.node = a, b

    @staticmethod
    def _link(y, z):
        """Make root y a child of root z (same degree)."""
        y.parent = z
        y.sibling = z.child
        z.child = y
        z.degree += 1

    @staticmethod
    def _merge_lists(a, b):
        """Merge two root lists into one sorted by degree."""
        dummy = Node(None)
        t = dummy
        while a and b:
            if a.degree <= b.degree:
                t.sibling, a = a, a.sibling
            else:
                t.sibling, b = b, b.sibling
            t = t.sibling
        t.sibling = a or b
        return dummy.sibling

    def _union_with(self, other_head):
        head = self._merge_lists(self.head, other_head)
        if head is None:
            self.head = None
            return
        prev, x, nxt = None, head, head.sibling
        while nxt:
            if x.degree != nxt.degree or (nxt.sibling and nxt.sibling.degree == x.degree):
                prev, x = x, nxt
            elif x.key <= nxt.key:
                x.sibling = nxt.sibling
                self._link(nxt, x)
            else:
                if prev is None:
                    head = nxt
                else:
                    prev.sibling = nxt
                self._link(x, nxt)
                x = nxt
            nxt = x.sibling
        self.head = head

    def _remove_root(self, root):
        """Detach root from the root list and merge its children back in."""
        prev, cur = None, self.head
        while cur is not root:
            prev, cur = cur, cur.sibling
        if prev is None:
            self.head = root.sibling
        else:
            prev.sibling = root.sibling
        # children are in decreasing degree order; reverse them
        rev, c = None, root.child
        while c:
            nxt = c.sibling
            c.sibling = rev
            c.parent = None
            rev, c = c, nxt
        self._union_with(rev)
        self.n -= 1

    # ---------- operations ----------
    def insert(self, key):
        node = Node(key)
        self._union_with(node)
        self.n += 1
        return node.handle

    def find_min(self):
        if self.head is None:
            raise IndexError("empty heap")
        best, r = self.head, self.head.sibling
        while r:
            if r.key < best.key:
                best = r
            r = r.sibling
        return best.key

    def extract_min(self):
        if self.head is None:
            raise IndexError("empty heap")
        best, r = self.head, self.head.sibling
        while r:
            if r.key < best.key:
                best = r
            r = r.sibling
        key = best.key
        self._remove_root(best)
        return key

    def union(self, other):
        """Merge other into self; other becomes empty."""
        self._union_with(other.head)
        self.n += other.n
        other.head, other.n = None, 0

    def decrease_key(self, handle, new_key):
        y = handle.node
        if new_key > y.key:
            raise ValueError("new key is larger than current key")
        y.key = new_key
        z = y.parent
        while z and y.key < z.key:
            self._swap(y, z)
            y, z = z, z.parent

    def delete(self, handle):
        # float the entry to its tree's root, then remove that root
        y = handle.node
        while y.parent:
            self._swap(y, y.parent)
            y = y.parent
        self._remove_root(y)

    # ---------- debugging ----------
    def __iter__(self):
        """Yield all keys (unordered)."""
        stack = []
        r = self.head
        while r:
            stack.append(r)
            r = r.sibling
        while stack:
            u = stack.pop()
            yield u.key
            c = u.child
            while c:
                stack.append(c)
                c = c.sibling

    def check(self):
        """Verify heap order, binomial tree shapes, and root degree order."""
        count, last_deg, r = 0, -1, self.head
        while r:
            assert r.degree > last_deg and r.parent is None
            last_deg = r.degree
            count += self._check_tree(r)
            r = r.sibling
        assert count == self.n


    def _check_tree(self, u):
        size, deg, c = 1, u.degree, u.child
        for d in range(deg - 1, -1, -1):
            assert c is not None and c.degree == d and c.parent is u
            assert c.key >= u.key
            size += self._check_tree(c)
            c = c.sibling
        assert c is None
        assert size == 2 ** deg
        return size


if __name__ == "__main__":
    import random

    for _ in range(500):
        h, ref = BinomialHeap(), []
        for _ in range(random.randint(0, 80)):
            if random.random() < 0.6 or not ref:
                k = random.randint(0, 50)
                h.insert(k)
                ref.append(k)
            else:
                m = min(ref)
                assert h.extract_min() == m
                ref.remove(m)
            h.check()
            assert sorted(h) == sorted(ref)

        # delete via handles (a handle tracks a node, whose key may move)
        nodes = [h.insert(random.randint(0, 100)) for _ in range(30)]
        random.shuffle(nodes)
        for nd in nodes[:15]:
            ref = sorted(h)
            ref.remove(nd.key)
            h.delete(nd)
            h.check()
            assert sorted(h) == ref

        # decrease_key
        nd = h.insert(1000)
        h.decrease_key(nd, -5)
        assert h.find_min() == -5
        h.check()

        # union
        before = sorted(h)
        g = BinomialHeap.build(range(10, 30))
        h.union(g)
        h.check()
        assert len(g) == 0 and sorted(h) == sorted(before + list(range(10, 30)))
    print("all tests passed")
