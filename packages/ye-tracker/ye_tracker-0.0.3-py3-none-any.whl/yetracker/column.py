from abc import ABC, abstractmethod
from typing import TypedDict, override, Self, overload, Protocol, Literal
import pprint
import datetime
from dataclasses import dataclass
import re
from enum import Enum, StrEnum

from yetracker.common import *

class Column(ABC):
    def __init__(self, row: Row, column_num: int):
        try:
            self.base_str = row[column_num]
        except:
            self.base_str = ""
    
    @abstractmethod
    def __call__(self) -> object:
        pass

class SimpleColumn(Column):
    def __call__(self) -> str:
        return self.base_str

class TrackLength(Column):
    def __call__(self):
        regex_match = re.search(r'(\d{1,2}):(\d{2})', self.base_str)

        if regex_match is None:
            return None

        minutes = int(regex_match.group(1))
        seconds = int(regex_match.group(2))
        duration = minutes * 60 + seconds
        
        return datetime.timedelta(seconds=duration)
    
class Date(Column):
    def parse_date_str(self, date_str: str) -> datetime.datetime | str | None:
        months = ['Jan', 'Feb', 'Mar', 'Apr',
                  'May', 'Jun', 'Jul', 'Aug'
                  'Sep', 'Oct', 'Nov', 'Dec']
        
        regex_match = re.search(r'(\w{3}) (\d{2}), (\d{4})', date_str)

        if regex_match is None:
            return None
        
        try:
            month = months.index(regex_match.group(1))
            day = int(regex_match.group(2))
            year = int(regex_match.group(3))

            return datetime.datetime(year=year, month=month, day=day)
        except:
            return date_str
        
    def __call__(self):
        return self.parse_date_str(self.base_str)

class Category[T: Enum](Column, ABC):
    @property
    @abstractmethod
    def category_cls(self) -> type[T]:
        pass

    def __call__(self) -> T | None:
        try:
            return self.category_cls(self.base_str)
        except ValueError:
            return

class AvailableLengthEnum(StrEnum):
    SNIPPET = 'Snippet'
    PARTIAL = 'Partial'
    BEAT_ONLY = 'Beat Only'
    TAGGED = 'Tagged'
    STEM_BOUNCE = 'Stem Bounce'
    FULL = 'Full'
    OG_FILE = 'OG File'
    CONFIRMED = 'Confirmed'
    RUMORED = 'Rumored'
    CONFLICTING_SOURCES = 'Conflicting Sources'

class AvailableLength(Category):
    @property
    def category_cls(self):
        return AvailableLengthEnum

    def __call__(self) -> AvailableLengthEnum | None:
        return super().__call__()

class QualityEnum(StrEnum):
    NOT_AVAILABLE = 'Not Available'
    RECORDING = 'Recording'
    LOW_QUALITY = 'Low Quality'
    HIGH_QUALITY = 'High Quality'
    CD_QUALITY = 'CD Quality'
    LOSSLESS = 'Lossless'

class Quality(Category):
    @property
    def category_cls(self):
        return QualityEnum

    def __call__(self) -> QualityEnum | None:
        return super().__call__()

class Streaming(Column):
    def __call__(self):
        return self.base_str == 'Yes'

class ReleasedTypeEnum(StrEnum):
    ALBUM_TRACK = "Album Track"
    FEATURE = "Feature"
    OTHER = "Other"
    PRODUCTION = "Production"
    SINGLE = "Single"

class ReleasedType(Category):
    @property
    def category_cls(self):
        return ReleasedTypeEnum

    def __call__(self) -> ReleasedTypeEnum | None:
        return super().__call__()

@dataclass
class SampleUsed:
    name: str | None
    artist: str | None = None
    note: str | None = None
    link: str | None = None

class SampleColumn(Column):
    def __call__(self) -> list[SampleUsed]:
        samples_used: list[SampleUsed] = []
        lines = self.base_str.splitlines()
        
        pattern = r'(.+) - (.+)'
        for line in lines:
            sample: SampleUsed

            regex_match = re.search(pattern, line)

            if regex_match is None:                
                sample = SampleUsed(line)
            else:
                artist = regex_match.group(1)
                name = regex_match.group(2)
                sample = SampleUsed(name, artist)

            samples_used.append(sample)
        
        return samples_used

    @staticmethod
    def modify_samples_used(samples_used: list[SampleUsed],
                            notes: str,
                            links: str):
        notes_lines = notes.splitlines()
        
        if len(notes_lines) == len(samples_used):
            for i, note in enumerate(notes_lines):
                samples_used[i].note = note
        elif notes != "":
            for sample in (samples_used):
                sample.note = notes

        links_lines = links.splitlines()

        if len(links_lines) == len(samples_used):
            for i, link in enumerate(links_lines):
                samples_used[i].link = link
        elif links != "":
            for sample in (samples_used):
                sample.link = links
        
        return samples_used


class Emoji(Enum):
    BEST_OF = "⭐"
    SPECIAL = "✨"
    GRAIL = "🏆"
    WANTED = "🥇"
    WORST_OF = "🗑️"
    AI = "🤖"
    LOST = "⁉️"

@add_repr
class Version:
    def __init__(self, version_start: int, version_end: int | Literal['?'] | None = None):
        self.version_start = version_start
        self.version_end = version_end

        self.multiple_versions = version_end != None

        self.version: tuple[int, int | Literal['?']] | int
        if version_end is not None:
            self.version = version_start, version_end
        else:
            self.version = version_start

        self.version_count_unknown = version_end == '?'

    @classmethod
    def extract_version(cls, name_str: str) -> tuple[Self | None, str]:
        pattern = r'\[V(\d+)(-V(\d+|\?))*\]'

        regex_match = re.search(pattern, name_str)
        if regex_match is None:
            return None, name_str

        version_start = int(regex_match.group(1))
        version_end = str(regex_match.group(3))

        if version_end == '?':
            pass
        elif version_end == '' or version_end == 'None':
            version_end = None
        else:
            version_end = int(version_end)
        
        name_str = re.sub(pattern, '', name_str)

        return cls(version_start, version_end), name_str

class ContribTag(Enum):
    FEAT = "feat."
    REF  = "ref."
    WITH = "with"
    PROD = "prod."
    QUES = "???."

@add_repr
class Contributors:
    def __init__(self, name_str: str):
        self.feat: str | None = None
        self.ref: str | None = None
        self.with_: str | None = None
        self.prod: str | None = None
        self.ques: str | None = None

        line, name_str = self._get_contrib_line(name_str)
        self._after_parsing = name_str
        if line is None:
            return
        
        self._parse_contrib(line)

    def __call__(self):
        return self._after_parsing

    def _parse_contrib(self, line: str):
        words = line.split()

        contrib_word_dict: dict[ContribTag, list[str]] = {
            tag: [] for tag in ContribTag
        }

        mode: ContribTag | None = None

        def add_to_dict(word: str):
            if mode is None:
                return

            contrib_word_dict[mode].append(word)
        
        for word in words:
            if word[0] == '(':
                try:
                    mode = ContribTag(word[1:])
                except:
                    mode = None
            elif word[-1] == ')':
                add_to_dict(word[:-1])
                mode = None
            else:
                add_to_dict(word)
        
        self.feat = ' '.join(contrib_word_dict[ContribTag.FEAT])
        self.ref = ' '.join(contrib_word_dict[ContribTag.REF])
        self.with_ = ' '.join(contrib_word_dict[ContribTag.WITH])
        self.prod = ' '.join(contrib_word_dict[ContribTag.PROD])
        self.ques = ' '.join(contrib_word_dict[ContribTag.QUES])
    
    def _get_contrib_line(self, name_str: str) -> tuple[str | None, str]:

        split_by_line = name_str.splitlines()

        if len(split_by_line) == 3:
            name_str = f'{split_by_line[0]}\n{split_by_line[2]}'
            return split_by_line[1], name_str
        elif len(split_by_line) == 2:
            first_word = split_by_line[1].split()[0]
            for tag in ContribTag:
                if first_word == f'({tag.value}':
                    name_str = split_by_line[0]
                    return split_by_line[1], name_str
        
        return None, name_str

class Name(Column):
    def __call__(self):
        self.emojis, name_str = self.extract_emojis(self.base_str)
        self.version, name_str = self.extract_version(name_str)
        self.contribs, name_str = self.extract_contribs(name_str)
        self.alt_names, name_str = self.extract_alt_names(name_str)
        self.artist, name_str = self.extract_artist(name_str)

        self.main_name = name_str

        return self.base_str
    
    def extract_emojis(self, name_str: str) -> tuple[list[Emoji], str]:
        emojis: list[Emoji] = []

        for emoji in Emoji:
            emoji_match = re.match(emoji.value, name_str)
            if emoji_match is None:
                continue

            emojis.append(emoji)
            name_str = re.sub(emoji.value, "", name_str)
        
        return emojis, name_str
    
    def extract_version(self, name_str: str) -> tuple[Version | None, str]:        
        return Version.extract_version(name_str)
    
    def extract_contribs(self, name_str: str) -> tuple[Contributors, str]:
        contribs = Contributors(name_str)
        return contribs, contribs()

    def extract_alt_names(self, name_str: str) -> tuple[list[str], str]:
        split_by_line = name_str.splitlines()
        if len(split_by_line) == 1:
            return [], name_str
        else:
            line = split_by_line[1]
            line = line.strip('(').strip(')')
            alt_names = line.split(', ')
            return alt_names, split_by_line[0]
 
    def extract_artist(self, name_str: str) -> tuple[str | None, str]:
        if ' - ' in name_str:
            split = name_str.split(' - ')
            return split[0], split[1]
        
        return None, name_str

class EraStats(Column):
    def __call__(self) -> dict[str, int]:
        stats: dict[str, int] = {}

        lines = self.base_str.splitlines()
        for line in lines:
            regex_match = re.match(r'(\d+) (.+)', line)
            if regex_match is None:
                continue
            
            count = int(regex_match.group(1))
            status = str(regex_match.group(2))
            stats[status] = count
        
        return stats

class EraName(Column):
    def __call__(self) -> str:
        lines = self.base_str.splitlines()

        self.alt_names: list[str] | None = None
        if len(lines) >= 2:
            alt_names_line = lines[1]
            alt_names_line = alt_names_line.strip('(').strip(')')
            self.alt_names = alt_names_line.split(', ')

        return lines[0]

class EraEvents(Column):
    def __call__(self) -> dict[str, str]:
        events: dict[str, str] = {}

        event_lines = self.base_str.splitlines()

        for line in event_lines:
            event_pattern = r'\((.+)\) \((.+)\)'
            event_match = re.match(event_pattern, line)

            if event_match is None:
                continue
            
            event_date = str(event_match.group(1))
            event_desc = str(event_match.group(2))

            events[event_date] = event_desc
        
        return events

class StemTypeEnum(Enum):
    ACAPELLAS = "Acapellas"
    INSTRUMENTALS = "Instrumentals"
    LIVE_ACAPELLAS = "Live Acapellas"
    LIVE_STEMS = "Live Stems"
    SESSIONS = "Sessions"
    STEM_PLAYER_STEMS = "Stem Player Stems"
    STUDIO_STEMS = "Studio Stems"
    TV_TRACKS = "TV Tracks"

class StemType(Category):
    @property
    def category_cls(self) -> type[StemTypeEnum]:
        return StemTypeEnum

    def __call__(self) -> StemTypeEnum | None:
        return super().__call__()

class MVStatusEnum(Enum):
    UNRELEASED = "Unreleased"
    RELEASED = "RELEASED"

class MVStatus(Category):
    @property
    def category_cls(self) -> type[MVStatusEnum]:
        return MVStatusEnum

    def __call__(self) -> MVStatusEnum | None:
        return super().__call__()
