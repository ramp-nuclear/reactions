"""Module for defining common ways to report reaction rates.

"""
from typing import Generator, Type, Any, TypeVar
try:
    from typing import Self
except ImportError:
    Self = TypeVar("Self")

import numpy as np
from isotopes import ZAID
from ramp_core.serializable import Serializable, deserialize_default

from reactions.reaction import ReactionType

PerSecondCm3 = float
eV = float

__all__ = ['ReactionRate']


class ReactionRate:
    """This object holds the common way to report reaction rate data.

    """

    ser_identifier = "ReactionRate"

    def __init__(self, component: str, reaction: ReactionType,
                 mean: PerSecondCm3, std: PerSecondCm3):
        r"""Object initialization

        Parameters
        ----------
        component - Structural name for the Component this reaction happens in.
        reaction - Reaction measured
        mean - Average reaction mean in the component, in 1/(s*cm^3)
        std - Absolute error in the reaction mean average reported.
                     For now it is best to assume this represents a 1-\sigma
                     standard deviation in a normally distributed result.
        """

        self.component = component
        self.reaction = reaction
        self.mean = mean
        self.std = std

    @classmethod
    def from_other(cls, other: "ReactionRate",
                   mean: PerSecondCm3, std: PerSecondCm3) -> "ReactionRate":
        """Use one reaction rate to make another different one

        Parameters
        ----------
        other - Template reaction rate to use
        mean - Reaction rate mean value for the new ReactionRate
        std - Reaction rate std value for the new ReactionRate

        """
        return cls(other.component, other.reaction, mean, std)

    def __eq__(self, other: "ReactionRate"):
        if not isinstance(other, ReactionRate):
            return NotImplemented
        return all((self.component == other.component,
                    self.reaction == other.reaction,
                    np.isclose(self.mean, other.mean, rtol=1e-10, atol=1e-14),
                    np.isclose(self.std, other.std, rtol=1e-10, atol=1e-14),
                    ))

    @property
    def parent(self) -> ZAID:
        """Return the parent isotope for the reaction here

        """

        return self.reaction.parent

    @property
    def target(self) -> ZAID:
        """Returns the target if available.

        Raises
        ------
        AttributeError if not available.

        """
        return self.reaction.target

    @property
    def branching(self) -> dict[ZAID, float]:
        return self.reaction.branching

    def expand(self) -> Generator["ReactionRate", None, None]:
        """Return the target isotope for this reaction, if possible.

        Raises
        ------
        AttributeError if reaction has no target

        """

        for reaction, branching in self.reaction.branches():
            yield ReactionRate(self.component, reaction,
                               self.mean * branching,
                               self.std * branching)

    # noinspection PyMissingOrEmptyDocstring
    @property
    def rate(self) -> PerSecondCm3: 
        return self.mean

    @property
    def typus(self) -> str:
        """Return a string representation of the type of this reaction

        """
        return self.reaction.typus

    @property
    def nu(self) -> float:
        """Return the mean number of emitted neutrons per event

        """
        return self.reaction.nu

    @property
    def energy(self) -> eV:
        """Returns the usable energy of a single reaction of this type, in eV.
        Defaults to 0. if the reaction doesn't have a listed energy.

        Returns
        -------

        """
        try:
            return self.reaction.energy
        except AttributeError:
            return 0.

    def __mul__(self, other: float):
        if not isinstance(other, float):
            return NotImplemented
        return type(self).from_other(self, 
                                     mean=self.rate * other, 
                                     std=self.std * other)

    def serialize(self) -> tuple[str, dict[str, Any]]:
        return self.ser_identifier, {"component": self.component,
                                     "reaction": self.reaction.serialize(),
                                     "mean": self.mean,
                                     "std": self.std}

    @classmethod
    def deserialize(cls: Type[Self], d: dict[str, Any], *, 
                    supported: dict[str, Type[Serializable]]) -> Self:
        reaction = deserialize_default(d["reaction"], supported=supported)
        del d["reaction"]
        return cls(reaction=reaction, **d)

