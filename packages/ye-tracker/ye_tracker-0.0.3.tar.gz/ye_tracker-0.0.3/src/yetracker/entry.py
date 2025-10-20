from abc import ABC, abstractmethod
import pprint

from yetracker.column import * 
from yetracker.era import *
from yetracker.era import Era

@add_repr
class Entry(ABC):
    @abstractmethod
    def __init__(self, row: Row):
        pass

class WithNames:
    def _set_name_attrs(self, row: Row):
        name_column = Name(row, 1)
        self.full_name = name_column()
        self.main_name = name_column.main_name
        self.emojis = name_column.emojis
        self.version = name_column.version
        self.contribs = name_column.contribs
        self.alt_names = name_column.alt_names
        self.artist = name_column.artist

class WithEras:
    def _set_era_attrs(self, era_name: str):
        self.era: str | Era = era_name
        self.subera: SubEra | None = None

    def set_era(self, era: Era):
        self.era = era

    def set_subera(self, subera: SubEra):
        self.subera = subera

class Song(Entry, WithNames, WithEras):
    def __init__(self, row: Row):
        self.era_name: str = SimpleColumn(row, 0)()

        self.notes = SimpleColumn(row, 2)()
        self.length = TrackLength(row, 3)()
        self.link = SimpleColumn(row, 8)()

        self._set_name_attrs(row)
        self._set_era_attrs(self.era_name)

class Unreleased(Song):
    def __init__(self, row: Row):
        super().__init__(row)

        self.file_date = Date(row, 4)()
        self.leak_date = Date(row, 5)()

        self.available_length = AvailableLength(row, 6)()
        self.quality = Quality(row, 7)()

class Released(Song):
    def __init__(self, row: Row):
        super().__init__(row)

        self.link = SimpleColumn(row, 7)()

        self.release_date = Date(row, 4)()
        self.type = ReleasedType(row, 5)
        self.streaming = Streaming(row, 6)()

class Stem(Song):
    def __init__(self, row: Row):
        super().__init__(row)

        self.link = SimpleColumn(row, 9)()
        self.length = TrackLength(row, 5)()

        self.file_date = Date(row, 3)()
        self.leak_date = Date(row, 4)()
        self.bpm = SimpleColumn(row, 6)
        self.available_length = AvailableLength(row, 7)()
        self.quality = Quality(row, 8)()

class Sample(Entry, WithNames):
    def __init__(self, row: Row):
        super().__init__(row)

        self.era_name: str = SimpleColumn(row, 0)()
        self.notes = SimpleColumn(row, 3)()
        self.links = SimpleColumn(row, 4)()

        self.samples = SampleColumn(row, 2)()
        self.samples = SampleColumn.modify_samples_used(
            self.samples, 
            self.notes,
            self.links
        )

        self._set_name_attrs(row)
