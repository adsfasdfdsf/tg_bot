from aenum import Enum


class State(Enum):
    ADD_SHARE = 0
    ADD_BOND = 1
    DELETE = 2
    ANY = 3
    CHOICE = 4
    SECRITY_CHOICE = 5