"""Package for particles that can induce reactions.

"""
from enum import Enum


__all__ = ['Particle', 'Photon', 'Proton', 'Neutron', 'Deutron', 'Triton',
           'He3', 'Alpha', 'Electron', 'Positron']

from typing import Any, Type, TypeVar
try:
    from typing import Self
except ImportError:
    Self = TypeVar("Self")


class Particle:
    """Nuclear particle concept.

    Parameters
    ----------
    charge - The charge of the particle, in elementary charges (i.e, -1 for an electron)
    mass - Mass of the particle. Used as its A-number.
    name - Name to call the particle by.
    sign - Way to represent it in strings, if different from name.

    """

    ser_identifier = "Particle"

    def __init__(self, charge: int, mass: int, name: str, sign: str | None = None):
        self.Z = charge
        self.A = mass
        self._name = name
        self._representation = sign

    def __repr__(self) -> str:
        return self._representation if self._representation else self._name

    __str__ = __repr__

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, Particle):
            return NotImplemented
        return (self.Z == other.Z
                and self.A == other.A
                and self._name == other._name
                and self._representation == other._representation
                )

    def __hash__(self):
        return hash((self.Z, self.A, self._name, self._representation))

    def serialize(self) -> tuple[str, dict]:
        return self.ser_identifier, dict(charge=self.Z, 
                                         mass=self.A, 
                                         name=self._name, 
                                         sign=self._representation)

    @classmethod
    def deserialize(cls: Type[Self], d: dict[str, Any], **_) -> Self:
        return cls(**d)


class NamedParticle(Particle, Enum):
    """Named enum for different reaction inducing particles.

    """

    def serialize(self) -> tuple[str, dict]:
        return Particle(*self.value).serialize()

    Photon = (0, 0, 'photon', r'$\gamma$')
    Neutron = (0, 1, 'neutron', 'n')
    Proton = (1, 1, 'proton', 'p')
    Deutron = (1, 2, 'Deutron', 'd')
    Triton = (1, 3, 'triton', 't')
    Electron = (-1, 0, 'electron', r'$e^-$')
    Positron = (1, 0, 'positron', r'$e^+$')
    He3 = (2, 3, 'helium-3', r'$^{3}He$')
    Alpha = (2, 4, 'alpha', r'$\alpha$')


Photon = NamedParticle.Photon
Neutron = NamedParticle.Neutron
Proton = NamedParticle.Proton
Deutron = NamedParticle.Deutron
Triton = NamedParticle.Triton
Electron = NamedParticle.Electron
Positron = NamedParticle.Positron
He3 = NamedParticle.He3
Alpha = NamedParticle.Alpha
