"""Main Reactions package code. A reaction is the data behind the reaction.
This will include the list of known reactions.

"""
from typing import Sequence, Dict, Generator, Tuple, Protocol, Hashable, \
    Iterable
from isotopes import ZAID
from .spectrum import Spectrum
from .reaction_category import *

__all__ = ['ReactionType', 'ConcreteReaction', 'Reaction', 'ProtoReaction',
           'ProductionReaction']

eV = float


# noinspection PyMissingOrEmptyDocstring
class ReactionType(Hashable, Protocol):
    """A Protocol that reaction-like types must follow so they can be used under
    a common API.

    """

    @property
    def parent(self) -> ZAID: raise NotImplementedError

    @property
    def typus(self) -> str: raise NotImplementedError

    @property
    def nu(self) -> float: raise NotImplementedError

    @property
    def energy(self) -> eV: raise NotImplementedError

    @property
    def energy_err(self) -> eV: raise NotImplementedError

    @property
    def branching(self) -> Dict[ZAID, float]: raise NotImplementedError

    def branches(self) -> Iterable[Tuple["ConcreteReaction", float]]:
        """A function that returns all Reaction branches from this reaction.

        """
        raise NotImplementedError

    def __str__(self) -> str: return self.typus


# noinspection PyMissingOrEmptyDocstring
class ConcreteReaction(ReactionType, Protocol):
    """A ReactionType that has one specific target nuclide.

    """

    @property
    def target(self) -> ZAID: raise NotImplementedError


# noinspection PyMissingOrEmptyDocstring
class ProtoReaction:
    """An induced reaction that can be non-target-specific due to fission

    """

    _members_ = {}

    def __new__(cls, parent: ZAID, typus: str = '', *,
                energy: eV = 0., energy_err: eV = 0.,
                nu: float = 0.,
                branching: Dict[ZAID, float] = None,
                spectra: Sequence[Spectrum] = ()) -> "ProtoReaction":
        """Create a new proto-reaction object. This is used to implement the
        Singleton pattern, since a reaction can be used tens of thousands of
        times and we can't afford to have copies.

        Parameters
        ----------
        parent - Parent isotope.
        typus - Type of this reaction. For example: (n, fission)
        energy - Energy release in this reaction, in EV.
        energy_err - Uncertainty in energy value.
        nu - Number of released free neutrons in the reaction on average.
        branching - A dictionary of branching ratios for different targets.
        spectra - The resulting spectra from this reaction. Currently unused
                  and placed as a placeholder for when spectral analysis is
                  implemented in other packages.
        """
        frozendict = frozenset(branching.items() if branching else ())
        try:
            return cls._members_[(parent, typus, energy, energy_err, nu, frozendict, spectra)]
        except KeyError:
            obj = super().__new__(cls)
            cls._members_[(parent, typus, energy, energy_err, nu, frozendict, spectra)] = obj
            return obj

    def __getnewargs_ex__(self):
        return (self._parent, self._typus), dict(energy=self._energy, energy_err=self._energy_err, nu=self._nu,
                                                 branching=self._branching, spectra=self.spectra)

    def __init__(self, parent: ZAID, typus: str = '', *,
                 branching: Dict[ZAID, float],
                 energy: eV = 0., energy_err: eV = 0.,
                 nu: float = 0.,
                 spectra: Sequence[Spectrum] = ()):
        self._parent = parent
        self._typus = typus
        self._energy = energy
        self._energy_err = energy_err
        self.spectra = spectra
        self._branching = branching
        self._nu = nu

    @classmethod
    def from_reaction(cls, parent: ZAID, reaction: "ReactionCategory", *,
                      branching: Dict[ZAID, float] = None,
                      spectra: Sequence[Spectrum] = (),
                      nu: float = 0.,
                      energy: eV = 0., energy_err: eV = 0.) -> "ProtoReaction":
        """Make a proto-reaction from a reaction category.

        Parameters
        ----------
        parent - Parent isotope
        reaction - Reaction Category to use
        branching - Different ways this reaction can go and their fractions.
        spectra - Spectrum of this specific reaction
        nu - Mean number of neutrons emitted in a single event.
        energy - Energy release of this specific reaction
        energy_err - Error in energy release of this specific reaction

        """
        return cls(parent=parent, typus=str(reaction),
                   branching=branching or {}, nu=nu, energy=energy,
                   energy_err=energy_err, spectra=spectra)

    @property
    def parent(self) -> ZAID:
        return self._parent

    @property
    def typus(self) -> str:
        return self._typus

    @property
    def energy(self) -> eV:
        return self._energy

    @property
    def energy_err(self) -> eV:
        return self._energy_err

    @property
    def branching(self) -> Dict[ZAID, float]:
        return self._branching

    @property
    def nu(self) -> float:
        return self._nu

    def branches(self) -> Generator[Tuple["Reaction", float], None, None]:
        """Generator for the different branches this reaction has.
        """
        for target, branching in self.branching.items():
            yield Reaction(self, target), branching

    def __hash__(self):
        return hash((
            self._parent, self._typus, self._energy, self._energy_err, self._nu,
            frozenset(self._branching.items()), self.spectra))

    def __str__(self) -> str:
        return f'{self.parent}{self.typus}'

    def __repr__(self) -> str:
        return (f'{str(self)}: {self._energy=}, {self._energy_err=}, {self._nu=},'
                f'{set(self._branching.items())}, {self.spectra=}')

    def __eq__(self, other: "ProtoReaction"):
        return (self.__getnewargs_ex__() == other.__getnewargs_ex__()
                if isinstance(other, ProtoReaction)
                else NotImplemented)


# noinspection PyMissingOrEmptyDocstring
class Reaction:
    """An induced reaction to turn one thing into another.

    """

    _members_ = {}

    def __new__(cls, proto: ProtoReaction, target: ZAID) -> "Reaction":
        try:
            return cls._members_[(proto, target)]
        except KeyError:
            obj = super().__new__(cls)
            cls._members_[(proto, target)] = obj
            return obj

    def __getnewargs__(self):
        return self._proto, self._target

    def __init__(self, proto: ProtoReaction, target: ZAID):
        self._proto = proto
        self._target = target

    @property
    def parent(self) -> ZAID:
        return self._proto.parent

    @property
    def target(self) -> ZAID:
        return self._target

    @property
    def typus(self) -> str:
        return self._proto.typus

    @property
    def energy(self) -> eV:
        return self._proto.energy

    @property
    def energy_err(self) -> eV:
        return self._proto.energy_err

    @property
    def nu(self) -> float:
        return self._proto.nu

    @property
    def spectra(self) -> Sequence[Spectrum]:
        return self._proto.spectra

    def __str__(self):
        return f'{self._proto}{self._target}'

    def __eq__(self, other: "Reaction"):
        return ((self._proto, self._target) == (other._proto, other._target)
                if isinstance(other, Reaction)
                else NotImplemented)

    def __hash__(self):
        return hash((self._proto, self._target))

    @property
    def branching(self):
        return self._proto.branching

    @classmethod
    def from_reaction(cls, parent: ZAID, reaction: "ReactionCategory",
                      target: ZAID = None, *,
                      spectra: Sequence[Spectrum] = (),
                      branching: Dict[ZAID, float] = None,
                      nu: float = 0.,
                      energy: eV = 0., energy_err: eV = 0.) -> "Reaction":
        """Make a reaction from a reaction category.

        Parameters
        ----------
        parent - Parent isotope
        reaction - Reaction Category to use
        target - Ignored. Used so one can make a protoreaction or a reaction
                 with the same code
        spectra - Spectrum of this specific reaction
        branching - How this reaction branches out. If None, assumes it just
        doesn't.
        nu - Mean number of emitted neutrons per event.
        energy - Energy release of this specific reaction
        energy_err - Error in energy release of this specific reaction

        """
        proto = ProtoReaction.from_reaction(parent, reaction,
                                            spectra=spectra,
                                            energy=energy,
                                            nu=nu,
                                            branching=branching or {},
                                            energy_err=energy_err)
        target = target or reaction.calc_target(parent)
        return cls(proto, target)

    def branches(self) -> Generator[Tuple["Reaction", float], None, None]:
        yield self, 1.

    def __repr__(self):
        return str(self)


# noinspection PyMissingOrEmptyDocstring
class ProductionReaction:
    """Specific production of some nuclide from a parent isotope


    """

    _members_ = {}

    def __new__(cls, parent: ZAID, target: ZAID, typus: str):
        try:
            return cls._members_[(parent, target, typus)]
        except KeyError:
            obj = super().__new__(cls)
            cls._members_[(parent, target, typus)] = obj
            return obj

    def __getnewargs__(self):
        return self._parent, self._target, self._typus

    def __init__(self, parent: ZAID, target: ZAID, typus: str):
        self._parent = parent
        self._target = target
        self._typus = typus

    @classmethod
    def from_reaction(cls, parent: ZAID,
                      reaction: ProductionReactionCategory) \
            -> "ProductionReaction":
        """Creates a ProductionReaction from a category for a specific parent.

        Parameters
        ----------
        parent - Parent isotope that generates the target
        reaction - ProductionReactionCategory, such as (n,xp) for H1.

        """
        return cls(parent, reaction.produces, reaction.typus)

    @property
    def parent(self) -> ZAID:
        return self._parent

    @property
    def target(self) -> ZAID:
        return self._target

    @property
    def typus(self) -> str:
        return self._typus

    @property
    def nu(self) -> float:
        """Return mean number of neutrons emitted in this reaction.

        For production reactions this is just 0.

        """
        return 0.

    @property
    def energy(self) -> eV:
        """Returns the produced energy by this reaction.

        For production reactions this is always 0.
        """
        return 0.

    @property
    def energy_err(self) -> eV:
        return 0.

    @property
    def branching(self) -> Dict[ZAID, float]:
        return {}

    def __hash__(self):
        return hash((self._parent, self._target, self._typus))

    def branches(self) -> Generator[Tuple["ProductionReaction", float],
    None, None]:
        yield self, 1.

    def __str__(self):
        return self.typus

    def __eq__(self, other: "ProductionReaction") -> bool:
        return ((self.parent == other.parent
                 and self.target == other.target
                 and self.typus == other.typus)
                if isinstance(other, type(self))
                else NotImplemented
                )
