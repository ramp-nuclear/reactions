import json
from collections import Counter

import hypothesis.strategies as st
from hypothesis import given, settings
from isotopes import ZAID
from ramp_core import RampJSONEncoder, RampJSONDecoder

from reactions import (
        jsonable, ProtoReaction, Reaction, ReactionCategory, Particle, 
        ProductionReaction, ReactionRate,
        )

zaids = st.tuples(st.integers(min_value=0, max_value=100),
                  st.integers(min_value=0, max_value=100),
                  st.integers(min_value=0, max_value=3)
                  ).map(lambda x: ZAID(x[0], x[1], x[2]))
branches = st.dictionaries(zaids, st.floats(min_value=1e-10, max_value=1.)).map(
        lambda d: {k: v / sum(d.values()) for k, v in d.items()})
proto = st.builds(ProtoReaction, zaids, branching=branches | st.none(), 
                  spectra=st.just(tuple()))
reac = st.builds(Reaction, proto, zaids)
preac = st.builds(ProductionReaction, zaids, zaids, st.text())
particles = st.builds(Particle, 
                      st.integers(min_value=0, max_value=4), 
                      st.integers(min_value=0, max_value=4),
                      st.text())
rcategories = st.builds(ReactionCategory, st.text(), 
                        st.dictionaries(particles, st.integers(min_value=1, max_value=3)))
rates = st.builds(ReactionRate, 
                  st.text(), 
                  st.one_of(proto, reac, preac), 
                  st.floats(min_value=0, max_value=100), 
                  st.floats(min_value=0, max_value=1))

strats = {ProtoReaction: proto,
          Reaction: reac,
          ReactionCategory: rcategories,
          ProductionReaction: preac,
          ReactionRate: rates,
          Particle: particles
          }


def test_no_two_identifiers_the_same():
    c = dict(Counter([c.ser_identifier for c in jsonable]))
    assert set(c.values()) == {1}, c


def test_strat_for_all_supported():
    assert set(strats) == set(jsonable)


RampJSONDecoder.supported = {c.ser_identifier: c for c in jsonable}


def _test_ser_deser(x):
    s = json.dumps(x, cls=RampJSONEncoder)
    try:
        v = json.loads(s, cls=RampJSONDecoder)
    except (RuntimeError, TypeError):
        print(s)
        raise
    assert x == v, (x, v, s)


for cls, strat in strats.items():
    globals()[f"test_ser_deser_{cls.__name__}"] = settings(deadline=None)(given(strat)(_test_ser_deser))

