"""Package designed to fascilitate the basic concepts behind nuclear reactions.
This should be a fairly lightweight package, I think.

"""

from .particle import *
from .reaction import *
from .reaction_category import *
from .spectrum import *
from .typus import Typus
from .reaction_rate import ReactionRate

jsonable = [ReactionCategory, Reaction, ProtoReaction, ProductionReaction, 
            ReactionRate, Particle]

__ver__ = 0.1
