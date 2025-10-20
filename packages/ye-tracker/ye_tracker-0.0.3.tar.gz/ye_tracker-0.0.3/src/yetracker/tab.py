from abc import ABC, abstractmethod
from typing import Any, TypeGuard
import json
import pprint

from yetracker.era import *
from yetracker.entry import *

class EraManager:
    def __init__(self, 
                 era_cls: type[Era] = BasicEra, 
                 subera_cls: type[SubEra] = BasicSubEra,
                 no_eras: bool = False):
        self.no_eras = no_eras

        self._era_cls = era_cls
        self._subera_cls = subera_cls

        self.eras: list[Era] = []
        self.suberas: list[SubEra] = []

        self._current_era: Era | None = None
        self._current_subera: SubEra | None = None

    def manage_era(self, row: Row) -> bool:
        if self.no_eras:
            return False

        if self._era_cls.is_era(row):
            era = self._era_cls(row)
            self._current_era = era
            self._current_subera = None
            self.eras.append(era)
        elif self._subera_cls.is_subera(row):
            subera = self._subera_cls(row)
            self._current_subera = subera
            self.suberas.append(subera)
        else:
            return False

        return True

    def set_era_and_subera(self, entry: WithEras):
        if self._current_era is not None:
            entry.set_era(self._current_era)

        if self._current_subera is not None:
            entry.set_subera(self._current_subera)
        
class Tab[T: Entry](list[T], ABC):
    "Base class for a tab/sheet within a tracker."

    @property
    @abstractmethod
    def entry_cls(self) -> type[T]:
        pass

    @abstractmethod
    def get_era_manager(self) -> EraManager:
        pass

    def ignore_row(self, row_idx: int, row: Row) -> bool:
        return row_idx == 0 or len(row) == 1 or row[0] == ''
    
    def is_end(self, row: Row) -> bool:
        return False

    def __init__(self, raw_values: Range):
        """
        Args:
            values: The two-dimensional array representing 
                a range of cells, or its JSON.
        """

        super().__init__()
        
        era_manager = self.get_era_manager()

        for i, row in enumerate(raw_values):
            if self.ignore_row(i, row):
                continue

            if era_manager.manage_era(row):
                continue
            
            if self.is_end(row):
                break
            
            entry = self.entry_cls(row)

            if isinstance(entry, WithEras):
                era_manager.set_era_and_subera(entry)

            self.append(entry)

        self.eras = era_manager.eras

class UnreleasedTab(Tab[Unreleased]):
    @property
    def entry_cls(self):
        return Unreleased

    def is_end(self, row: Row):
        for i, x in enumerate(['Links', '', 'Quality']):
            if x != row[i]:
                return False
        
        return True

    def get_era_manager(self) -> EraManager:
        return EraManager()

    def get_emoji_subtab(self, *match_emojis: Emoji) -> 'UnreleasedTab':
        new_tab = UnreleasedTab([])
        new_tab.eras = self.eras

        for entry in self:
            if any(match_emoji in entry.emojis 
                   for match_emoji in match_emojis):
                new_tab.append(entry)
            
        return new_tab

    def get_best_of(self):
        return self.get_emoji_subtab(Emoji.BEST_OF)
    
    def get_worst_of(self):
        return self.get_emoji_subtab(Emoji.WORST_OF)
    
    def get_ai(self):
        return self.get_emoji_subtab(Emoji.AI)
    
    def get_special(self):
        return self.get_emoji_subtab(Emoji.SPECIAL)
    
    def get_grails_or_wanted(self):
        return self.get_emoji_subtab(Emoji.GRAIL, Emoji.WANTED)

class ReleasedTab(Tab[Released]):
    @property
    def entry_cls(self):
        return Released

    def get_era_manager(self) -> EraManager:
        return EraManager()

class StemsTab(Tab[Stem]):
    @property
    def entry_cls(self):
        return Stem

    def get_era_manager(self) -> EraManager:
        return EraManager(subera_cls=StemSubEra)

class SamplesTab(Tab[Sample]):
    @property
    def entry_cls(self):
        return Sample

    def get_era_manager(self) -> EraManager:
        return EraManager(no_eras=True)

