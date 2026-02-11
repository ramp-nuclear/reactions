"""Package for particles that can induce reactions.

"""
from enum import Enum


__all__ = ['Particle', 'Photon', 'Proton', 'Neutron', 'Deutron', 'Triton',
           'He3', 'Alpha', 'Electron', 'Positron']

from typing import Optional


class Particle:
    """Nuclear particle concept.

    Parameters
    ----------
    charge - The charge of the particle, in elementary charges (i.e, -1 for Beta)
    mass - Mass of the particle. Usually just the number of nucleons...
    name - Name to call the particle by.
    sign - Way to represent it in strings, if different from name.

    """

    def __init__(self, charge: int, mass, name: str, sign: Optional[str]=None):
        self.Z = charge
        self.A = mass
        self._name = name
        self._representation = sign

    def __repr__(self):
        return self._representation if self._representation else self._name

    __str__ = __repr__


class NamedParticle(Particle, Enum):
    """Named enum for different reaction inducing particles.

    """

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
