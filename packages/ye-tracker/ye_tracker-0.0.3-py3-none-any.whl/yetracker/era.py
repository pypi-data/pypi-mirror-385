import re
import pprint
from typing import Protocol

from yetracker.column import *

@add_repr
class Era(ABC):
    @abstractmethod
    def __init__(self, row: Row) -> None:
        pass

    @classmethod
    @abstractmethod
    def is_era(cls, row: Row) -> bool:
        pass

class BasicEra(Era):
    def __init__(self, row: Row):
        self.notes = SimpleColumn(row, 5)()

        self.stats = EraStats(row, 0)()
        self.events = EraEvents(row, 2)()

        name = EraName(row, 1)
        self.main_name = name()
        self.alt_names = name.alt_names

    @classmethod
    def is_era(cls, row: Row):
        return len(row) == 6

@add_repr
class SubEra(ABC):
    @abstractmethod
    def __init__(self, row: Row) -> None:
        pass

    @classmethod
    @abstractmethod
    def is_subera(cls, row: Row) -> bool:
        pass

class BasicSubEra(SubEra):
    def __init__(self, row: Row):
        self.name = SimpleColumn(row, 1)()
        self.events = EraEvents(row, 2)()

    @classmethod
    def is_subera(cls, row: Row):
        return len(row) == 3
    
class StemSubEra(SubEra):
    def __init__(self, row):
        self.stem_type = StemType(row, 1)()

    @classmethod
    def is_subera(cls, row: Row):
        return len(row) == 2

class MusicVideosSubEra(SubEra):
    def __init__(self, row: Row):
        self.release_status = MVStatus(row, 1)()

    @classmethod
    def is_subera(cls, row: Row):
        return len(row) == 2
