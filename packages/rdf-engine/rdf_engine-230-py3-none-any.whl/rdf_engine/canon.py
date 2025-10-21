"""
canonicalization
"""


class _quads:
    from pyoxigraph import Quad, Triple, NamedNode
    from typing import Iterable


    def __call__(self, quads: Iterable[Quad]) -> Iterable[Quad]:
        """
        canonicalization of sets of quads
        """
        # the set of quads have to be broken into sets of triples
        # after canonicalization,
        # each set of triples has to be reassembled as quads
        from collections import defaultdict
        g2t = defaultdict(set)
        for q in quads: g2t[q.graph_name].add(q.triple)
        from .data import reification
        for g,ts in g2t.items():
            _ = ts
            _ = reification.standard(_)
            _ = triples(_)
            _ = reification.star(_)
            _ = map(lambda t: Quad(*t, graph_name=g), _)
            yield from _

    class _deanon:
        from pyoxigraph import Triple
        from typing import Iterable
        from pyoxigraph import Quad
        class defaults:
            uri = "urn:anon:hash:"
        def __call__(slf,
                quads: Iterable[Quad], *,
                uri = defaults.uri) -> Iterable[Quad]:
            """takes blank node value as an identifier for a uri"""
            _ = map(lambda q: slf.quad(q, uri), quads)
            return _
        @classmethod
        def quad(cls, q: Quad, uri):
            if isinstance(q.object, cls.Triple):
                _ = cls.Triple(*(cls.f(n, uri) for n in q.object))
                q = cls.Quad(q.subject, q.predicate, _, q.graph_name)
            return cls.Quad(*(cls.f(n, uri) for n in q))
        
        from pyoxigraph import BlankNode, NamedNode
        @classmethod
        def f(cls, n, uri: str):
            if isinstance(n, cls.BlankNode):
                return cls.NamedNode(uri+n.value)
            else:
                return n
    deanon = _deanon()
quads = _quads()


from pyoxigraph import BlankNode, Quad, Triple
from typing import Iterable
def hasanon(d: Iterable[Quad| Triple]):
    for q in d:
        if isinstance(q.subject, BlankNode):
            return True
        if isinstance(q.object, BlankNode):
            return True
    return False


def triples(ts):
    if not isinstance(ts, frozenset):
        ts = frozenset(ts)
    assert(isinstance(ts, frozenset))
    from pyoxigraph import Triple
    for t in ts:
        assert(not isinstance(t.object,     Triple))
    # optimization
    if not hasanon(ts):
        return ts
    
    from . import conversions as c
    ts = c.oxigraph.rdflib(ts)
    from rdflib import Graph
    _ = Graph()
    for t in ts: ts = _.add(t)
    from rdflib.compare import to_canonical_graph
    ts = _; del _
    ts = to_canonical_graph(ts)
    ts = c.rdflib.oxigraph(ts)
    ts = frozenset(ts)
    return ts
def _ogtriples(triples):
    # algo seems to gets stuck (slow?)
    # wait for update TODO
    from pyoxigraph import Dataset, CanonicalizationAlgorithm, Quad
    def _(triples):
        d = Dataset(Quad(*t) for t in triples)
        d.canonicalize(CanonicalizationAlgorithm.UNSTABLE) # ?? unstable??
        for q in d: yield q.triple
    yield from _(triples)
