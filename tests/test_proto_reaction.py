import hypothesis.strategies as st
from hypothesis import given, settings, HealthCheck
from isotopes import Isotope

from reactions import ProtoReaction
from reactions.reaction_category import *


def gen_iso(z, a, m) -> Isotope | None:
    try:
        return Isotope(z, a, m)
    except ValueError:
        return None


isos = st.builds(gen_iso, st.integers(1, 92), st.integers(1, 238), st.integers(0, 2)).filter(lambda x: x is not None)
categories = [
    NInelastic,
    NAnything,
    N2ND,
    N2N,
    N3N,
    Fission,
    NNAlpha,
    NN3Alpha,
    N2NAlpha,
    N3NAlpha,
    NNP,
    NN2Alpha,
    N2N2Alpha,
    NND,
    NNT,
    NNHe3,
    NND2Alpha,
    NNT2Alpha,
    N4N,
    N2NP,
    N3NP,
    NN2P,
    NNPAlpha,
    NGamma,
    NP,
    ND,
    NT,
    NHe3,
    NAlpha,
    N2Alpha,
    N3Alpha,
    N2P,
    NPAlpha,
    NT2Alpha,
    ND2Alpha,
    NPD,
    NPT,
    NDAlpha,
    N5N,
    N6N,
    N2NT,
    N4NP,
    N3ND,
    NNDAlpha,
    N2NPAlpha,
    N7N,
    N8N,
    N5NP,
    N6NP,
    N7NP,
    N4NAlpha,
    N5NAlpha,
    N6NAlpha,
    N7NAlpha,
    N4ND,
    N5ND,
    N6ND,
    N3NT,
    N4NT,
    N5NT,
    N6NT,
    N2NHe3,
    N3NHe3,
    N4NHe3,
    N3N2P,
    N3N2Alpha,
    N3NPAlpha,
    NDT,
    NNPD,
    NNPT,
    NNDT,
    NNPHe3,
    NNDHe3,
    NNTHe3,
    NNTAlpha,
    N2N2P,
    NPHe3,
    NDHe3,
    NHe3Alpha,
    N4N2P,
    N4N2Alpha,
    N4NPAlpha,
    N3P,
    NN3P,
    N3N2PAlpha,
    N5N2P,
    NPtot,
    NDtot,
    NTtot,
    NHe3tot,
    NHeating,
]
categories_st = st.sampled_from(categories)
proto_reactions = st.builds(ProtoReaction.from_reaction,
                            isos,
                            categories_st,
                            branching=st.dictionaries(isos, st.floats(1e-6, 1 - 1e-6)),
                            spectra=st.just(tuple()),
                            nu=st.floats(0, 4),
                            energy=st.floats(1, 10),
                            energy_err=st.floats(1, 10)
                            )


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(proto_reactions, proto_reactions)
def test_different_reaction_are_not_equal(reac1: ProtoReaction, reac2: ProtoReaction):
    assert (reac1 is reac2) or reac1 != reac2


@settings(suppress_health_check=[HealthCheck.filter_too_much])
@given(proto_reactions, categories_st)
def test_equal_reactions_are_the_same_object(reac: ProtoReaction, reac_category: ReactionCategory):
    react1 = ProtoReaction.from_reaction(reac._parent, reac_category, branching=reac._branching,
                                         spectra=reac.spectra, nu=reac.nu,
                                         energy=reac.energy, energy_err=reac.energy_err)
    react2 = ProtoReaction.from_reaction(reac._parent, reac_category, branching=reac._branching,
                                         spectra=reac.spectra, nu=reac.nu,
                                         energy=reac.energy, energy_err=reac.energy_err)
    assert (react1 is react2) and react1 == react2
