"""General pre-structures for making reactions.

These define ideas like "Fission" or "Helium production".

"""
import re
from collections import Counter
from dataclasses import dataclass

from isotopes import Isotope, ZAID


__all__ = [
    "ProductionReactionCategory",
    "ReactionCategory",
    "NInelastic",
    "NAnything",
    "N2ND",
    "N2N",
    "N3N",
    "Fission",
    "NNAlpha",
    "NN3Alpha",
    "N2NAlpha",
    "N3NAlpha",
    "NNP",
    "NN2Alpha",
    "N2N2Alpha",
    "NND",
    "NNT",
    "NNHe3",
    "NND2Alpha",
    "NNT2Alpha",
    "N4N",
    "N2NP",
    "N3NP",
    "NN2P",
    "NNPAlpha",
    "NGamma",
    "NP",
    "ND",
    "NT",
    "NHe3",
    "NAlpha",
    "N2Alpha",
    "N3Alpha",
    "N2P",
    "NPAlpha",
    "NT2Alpha",
    "ND2Alpha",
    "NPD",
    "NPT",
    "NDAlpha",
    "N5N",
    "N6N",
    "N2NT",
    "N4NP",
    "N3ND",
    "NNDAlpha",
    "N2NPAlpha",
    "N7N",
    "N8N",
    "N5NP",
    "N6NP",
    "N7NP",
    "N4NAlpha",
    "N5NAlpha",
    "N6NAlpha",
    "N7NAlpha",
    "N4ND",
    "N5ND",
    "N6ND",
    "N3NT",
    "N4NT",
    "N5NT",
    "N6NT",
    "N2NHe3",
    "N3NHe3",
    "N4NHe3",
    "N3N2P",
    "N3N2Alpha",
    "N3NPAlpha",
    "NDT",
    "NNPD",
    "NNPT",
    "NNDT",
    "NNPHe3",
    "NNDHe3",
    "NNTHe3",
    "NNTAlpha",
    "N2N2P",
    "NPHe3",
    "NDHe3",
    "NHe3Alpha",
    "N4N2P",
    "N4N2Alpha",
    "N4NPAlpha",
    "N3P",
    "NN3P",
    "N3N2PAlpha",
    "N5N2P",
    "NPtot",
    "NDtot",
    "NTtot",
    "NHe3tot",
    "NHeating",
]

from .particle import Alpha, Deutron, He3, Neutron, Particle, Photon, Proton, Triton
from .typus import ProdTypus, Typus


class FissionTargetError(ValueError):
    """An error that is raised when trying to figure out what the resulting
    nuclide is for a fission event.

    """
    pass


@dataclass(init=True, frozen=True)
class ProductionReactionCategory:
    """An abstract black box view of all reactions that produce a specific
    product.

    """
    produces: ZAID
    typus: str

    def __repr__(self):
        return self.typus

    __str__ = __repr__


class ReactionCategory:
    """An abstract nuclear reaction, that isn't specific to one parent isotope.

    Usually reactions happen between a nucleus and an inducing particle, but
    often we like work with a non-specific category of induced reactions

    Parameters
    ----------
    typus - The way to mark this reaction. For example, (n, fission)
    releases - Released particles. Proton for (n,p) for example.
    target_state - The resulting nuclear energy state of the daughter nuclide.
                   Sometimes reactions cause the daughters to come out excited.

    """

    def __init__(self, typus: str, releases, target_state: int = 0):
        self.typus = typus
        self.releases = releases
        self.target_state = target_state

    def __eq__(self, other: "ReactionCategory"):
        return (self.typus == other.typus
                and self.target_state == other.target_state)

    def __hash__(self):
        return hash((self.typus, self.target_state))

    def calc_target(self, parent: ZAID) -> ZAID:
        """Return the ZAID of what will happen if this reaction applies to a
        specific parent

        Parameters
        ----------
        parent - Parent isotope that conceptually undergoes this reaction

        Returns
        -------
        ZAID for the target of this reaction in this case

        Raises
        ------
        FissionTargetError if this is a fission reaction category,
        since fission can't determine a unique outcome.

        """

        if self.typus == Typus.NFission:
            raise FissionTargetError("Fission has no specific target")
        z = parent.Z + self.induced_by.Z - sum(n * particle.Z for
                                               particle, n in
                                               self.releases.items())
        a = parent.A + self.induced_by.A - sum(n * particle.A for
                                               particle, n in
                                               self.releases.items())
        
        zaid_isotope = ZAID(z, a, self.target_state)
        return Isotope.from_zaid_with_fallback(zaid_isotope)

    _induce_pattern = re.compile(r'\(([\\\w]+),.*\)')
    _induce_dict = {'n': Neutron,
                    'p': Proton,
                    r'\gamma': Photon}

    @property
    def induced_by(self) -> Particle:
        """Figure out what the inducing particle in this reaction is

        """
        particle_str = re.match(self._induce_pattern, self.typus).groups()[0]
        try:
            return self._induce_dict[particle_str]
        except KeyError as e:
            raise NotImplementedError("Unsupported induced_by for "
                                      "Reaction Category type: "
                                      f"{self.typus}"
                                      f"{particle_str}") from e

    def __repr__(self):
        return self.typus

    __str__ = __repr__


N2ND = ReactionCategory(Typus.N2ND, Counter([Neutron, Neutron, Deutron]))
N2N = ReactionCategory(Typus.N2N, Counter([Neutron, Neutron]))
N3N = ReactionCategory(Typus.N3N, Counter([Neutron, Neutron, Neutron]))
Fission = ReactionCategory(Typus.NFission, Counter([Neutron, Photon]))
NNAlpha = ReactionCategory(Typus.NNAlpha, Counter([Neutron, Alpha]))
NN3Alpha = ReactionCategory(Typus.NN3Alpha, Counter([Neutron, Alpha, Alpha, Alpha]))
N2NAlpha = ReactionCategory(Typus.N2NAlpha, Counter([Neutron, Neutron, Alpha]))
N3NAlpha = ReactionCategory(Typus.N3NAlpha, Counter([Neutron, Neutron, Neutron, Alpha]))
NNP = ReactionCategory(Typus.NNP, Counter([Neutron, Proton]))
NN2Alpha = ReactionCategory(Typus.NN2Alpha, Counter([Neutron, Alpha, Alpha]))
N2N2Alpha = ReactionCategory(Typus.N2N2Alpha, Counter([Neutron, Neutron, Alpha, Alpha]))
NND = ReactionCategory(Typus.NND, Counter([Neutron, Deutron]))
NNT = ReactionCategory(Typus.NNT, Counter([Neutron, Triton]))
NNHe3 = ReactionCategory(Typus.NNHe3, Counter([Neutron, He3]))
NND2Alpha = ReactionCategory(Typus.NND2Alpha, Counter([Neutron, Deutron, Alpha, Alpha]))
NNT2Alpha = ReactionCategory(Typus.NNT2Alpha, Counter([Neutron, Triton, Alpha, Alpha]))
N4N = ReactionCategory(Typus.N4N, Counter([Neutron, Neutron, Neutron, Neutron]))
N2NP = ReactionCategory(Typus.N2NP, Counter([Neutron, Neutron, Proton]))
N3NP = ReactionCategory(Typus.N3NP, Counter([Neutron, Neutron, Neutron, Proton]))
NN2P = ReactionCategory(Typus.NN2P, Counter([Neutron, Proton, Proton]))
NNPAlpha = ReactionCategory(Typus.NNPAlpha, Counter([Neutron, Proton, Alpha]))
NGamma = ReactionCategory(Typus.NGamma, Counter([Photon]))
NP = ReactionCategory(Typus.NP, Counter([Proton]))
ND = ReactionCategory(Typus.ND, Counter([Deutron]))
NT = ReactionCategory(Typus.NT, Counter([Triton]))
NHe3 = ReactionCategory(Typus.NHe3, Counter([He3]))
NAlpha = ReactionCategory(Typus.NAlpha, Counter([Alpha]))
N2Alpha = ReactionCategory(Typus.N2Alpha, Counter([Alpha, Alpha]))
N3Alpha = ReactionCategory(Typus.N3Alpha, Counter([Alpha, Alpha, Alpha]))
N2P = ReactionCategory(Typus.N2P, Counter([Proton, Proton]))
NPAlpha = ReactionCategory(Typus.NPAlpha, Counter([Proton, Alpha]))
NT2Alpha = ReactionCategory(Typus.NT2Alpha, Counter([Triton, Alpha, Alpha]))
ND2Alpha = ReactionCategory(Typus.ND2Alpha, Counter([Deutron, Alpha, Alpha]))
NPD = ReactionCategory(Typus.NPD, Counter([Proton, Deutron]))
NPT = ReactionCategory(Typus.NPT, Counter([Proton, Triton]))
NDAlpha = ReactionCategory(Typus.NDAlpha, Counter([Deutron, Alpha]))
N5N = ReactionCategory(Typus.N5N, Counter([Neutron, Neutron, Neutron, Neutron, Neutron]))
N6N = ReactionCategory(Typus.N6N, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Neutron]))
N2NT = ReactionCategory(Typus.N2NT, Counter([Neutron, Neutron, Triton]))
N4NP = ReactionCategory(Typus.N4NP, Counter([Neutron, Neutron, Neutron, Neutron, Proton]))
N3ND = ReactionCategory(Typus.N3ND, Counter([Neutron, Neutron, Neutron, Deutron]))
NNDAlpha = ReactionCategory(Typus.NNDAlpha, Counter([Neutron, Deutron, Alpha]))
N2NPAlpha = ReactionCategory(Typus.N2NPAlpha, Counter([Neutron, Neutron, Proton, Alpha]))
N7N = ReactionCategory(Typus.N7N, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Neutron]))
N8N = ReactionCategory(Typus.N8N, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Neutron]))
N5NP = ReactionCategory(Typus.N5NP, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Proton]))
N6NP = ReactionCategory(Typus.N6NP, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Proton]))
N7NP = ReactionCategory(Typus.N7NP, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Proton]))
N4NAlpha = ReactionCategory(Typus.N4NAlpha, Counter([Neutron, Neutron, Neutron, Neutron, Alpha]))
N5NAlpha = ReactionCategory(Typus.N5NAlpha, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Alpha]))
N6NAlpha = ReactionCategory(Typus.N6NAlpha, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Alpha]))
N7NAlpha = ReactionCategory(Typus.N7NAlpha, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Alpha]))
N4ND = ReactionCategory(Typus.N4ND, Counter([Neutron, Neutron, Neutron, Neutron, Deutron]))
N5ND = ReactionCategory(Typus.N5ND, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Deutron]))
N6ND = ReactionCategory(Typus.N6ND, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Deutron]))
N3NT = ReactionCategory(Typus.N3NT, Counter([Neutron, Neutron, Neutron, Triton]))
N4NT = ReactionCategory(Typus.N4NT, Counter([Neutron, Neutron, Neutron, Neutron, Triton]))
N5NT = ReactionCategory(Typus.N5NT, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Triton]))
N6NT = ReactionCategory(Typus.N6NT, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Neutron, Triton]))
N2NHe3 = ReactionCategory(Typus.N2NHe3, Counter([Neutron, Neutron, He3]))
N3NHe3 = ReactionCategory(Typus.N3NHe3, Counter([Neutron, Neutron, Neutron, He3]))
N4NHe3 = ReactionCategory(Typus.N4NHe3, Counter([Neutron, Neutron, Neutron, Neutron, He3]))
N3N2P = ReactionCategory(Typus.N3N2P, Counter([Neutron, Neutron, Neutron, Proton, Proton]))
N3N2Alpha = ReactionCategory(Typus.N3N2Alpha, Counter([Neutron, Neutron, Neutron, Alpha, Alpha]))
N3NPAlpha = ReactionCategory(Typus.N3NPAlpha, Counter([Neutron, Neutron, Neutron, Proton, Alpha]))
NDT = ReactionCategory(Typus.NDT, Counter([Deutron, Triton]))
NNPD = ReactionCategory(Typus.NNPD, Counter([Neutron, Proton, Deutron]))
NNPT = ReactionCategory(Typus.NNPT, Counter([Neutron, Proton, Triton]))
NNDT = ReactionCategory(Typus.NNDT, Counter([Neutron, Deutron, Triton]))
NNPHe3 = ReactionCategory(Typus.NNPHe3, Counter([Neutron, Proton, He3]))
NNDHe3 = ReactionCategory(Typus.NNDHe3, Counter([Neutron, Deutron, He3]))
NNTHe3 = ReactionCategory(Typus.NNTHe3, Counter([Neutron, Triton, He3]))
NNTAlpha = ReactionCategory(Typus.NNTAlpha, Counter([Neutron, Triton, Alpha]))
N2N2P = ReactionCategory(Typus.N2N2P, Counter([Neutron, Neutron, Proton, Proton]))
NPHe3 = ReactionCategory(Typus.NPHe3, Counter([Proton, He3]))
NDHe3 = ReactionCategory(Typus.NDHe3, Counter([Deutron, He3]))
NHe3Alpha = ReactionCategory(Typus.NHe3Alpha, Counter([He3, Alpha]))
N4N2P = ReactionCategory(Typus.N4N2P, Counter([Neutron, Neutron, Neutron, Neutron, Proton, Proton]))
N4N2Alpha = ReactionCategory(Typus.N4N2Alpha, Counter([Neutron, Neutron, Neutron, Neutron, Alpha, Alpha]))
N4NPAlpha = ReactionCategory(Typus.N4NPAlpha, Counter([Neutron, Neutron, Neutron, Neutron, Proton, Alpha]))
N3P = ReactionCategory(Typus.N3P, Counter([Proton, Proton, Proton]))
NN3P = ReactionCategory(Typus.NN3P, Counter([Neutron, Proton, Proton, Proton]))
N3N2PAlpha = ReactionCategory(Typus.N3N2PAlpha, Counter([Neutron, Neutron, Neutron, Proton, Proton, Alpha]))
N5N2P = ReactionCategory(Typus.N5N2P, Counter([Neutron, Neutron, Neutron, Neutron, Neutron, Proton, Proton]))

NNTot = ProductionReactionCategory(ZAID(0, 1, 0), ProdTypus.NNTot)
NPtot = ProductionReactionCategory(ZAID(1, 1, 0), ProdTypus.NPtot)
NDtot = ProductionReactionCategory(ZAID(1, 2, 0), ProdTypus.NDtot)
NTtot = ProductionReactionCategory(ZAID(1, 3, 0), ProdTypus.NTtot)
NHe3tot = ProductionReactionCategory(ZAID(2, 3, 0), ProdTypus.NHe3tot)

NAnything = ReactionCategory(Typus.NAnything, Counter([Neutron]))
NInelastic = ReactionCategory(Typus.NInelastic, Counter([Neutron, Photon]))
NHeating = ReactionCategory(Typus.NHeating, Counter([Neutron]))
