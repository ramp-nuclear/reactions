from isotopes import ZAID
from reactions import Reaction, NGamma

sink = ZAID(0, 0, 0)

def test_reaction_sink_is_target_when_set_for_one_example():
    reac = Reaction.from_reaction(ZAID(1, 1, 0), NGamma, target=sink)
    assert reac.target is sink


def test_reaction_no_sink_is_computed_for_one_example():
    reac = Reaction.from_reaction(ZAID(1, 1, 0), NGamma)
    assert reac.target == ZAID(1, 2, 0)
    
