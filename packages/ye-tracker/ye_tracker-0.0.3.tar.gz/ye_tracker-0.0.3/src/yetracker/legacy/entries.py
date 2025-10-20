from dataclasses import dataclass
from enum import unique, StrEnum
from functools import cached_property
from typing import Optional, Literal, NamedTuple

@unique
class Quality(StrEnum):
    NOT_AVAILABLE = 'Not Available'
    RECORDING = 'Recording'
    LOW_QUALITY = 'Low Quality'
    HIGH_QUALITY = 'High Quality'
    CD_QUALITY = 'CD Quality'
    LOSSLESS = 'Lossless'

@unique
class AvaliableLength(StrEnum):
    SNIPPET = 'Snippet'
    PARTIAL = 'Partial'
    BEAT_ONLY = 'Beat Only'
    TAGGED = 'Tagged'
    FULL = 'Full'
    OG_FILE = 'OG File'
    CONFIRMED = 'Confirmed'
    RUMORED = 'Rumored'
    CONFLICTING_SOURCES = 'Conflicting Sources'

type SongEmoji = Literal['⭐', '✨', '🏆', '🗑️']
type SongEmojiName = Literal['Best Of', 'Special', 'Grail', 'Worst Of']

@dataclass
class SongContribs:
    ref: Optional[str] = None
    prod: Optional[str] = None
    feat: Optional[str] = None
    with_: Optional[str] = None
    unknown: Optional[str] = None

@dataclass
class Song:
    era: str
    artist: Optional[str]
    name: str
    version: Optional[str]
    contribs: SongContribs
    aliases: list[str]
    notes: str
    links: list[str]

class StemType(StrEnum):
    STEM_PLAYER_STEMS = 'Stem Player Stems'
    SESSIONS = 'Sessions'
    STUDIO_STEMS = 'Studio Stems'
    ACAPELLAS = 'Acapellas'
    LIVE_ACAPELLAS = 'Live Acapellas'
    INSTRUMENTALS = 'Instrumentals'
    TV_TRACKS = 'TV Tracks'
    LIVE_STEMS = 'Live Stems'
    
@dataclass
class Stem(Song):
    stem_type: StemType
    og_filename: Optional[str]
    file_date: Optional[str]
    full_length: Optional[str]
    bpm: str    
    available_length: AvaliableLength
    quality: Quality

class SampleTuple(NamedTuple):
    artist: str
    name: str

@dataclass
class Sample(Song):
    samples: list[SampleTuple]

class GroupbuyType(StrEnum):
    CHARITY = 'Charity'
    NORMAL = 'Normal'
    FLASH = 'Flash'
    BLIND = 'Blind'
    SCAMMED = 'No (Funds Transferred)'

class GroupbuyStatus(StrEnum):
    YES = 'Yes'
    REWORKED = 'Reworked'
    FORCELEAKED = 'Forceleaked'
    NO = 'No'

@dataclass
class GroupbuyContent:
    content: str
    tags: list[str]
    stems: bool

@dataclass
class Groupbuy:
    era: str
    main_content: str
    main_aliases: list[str]
    all_content: list[GroupbuyContent]
    price: int
    start_and_end_date: tuple[str, str]
    type: GroupbuyType
    status: GroupbuyStatus
    snippets: list[str]

@dataclass
class AlbumCopy(Song):
    copy_length: Optional[str]
    og_filename: str
    file_date: str
    available_length: AvaliableLength
    quality: Quality
    aliases: Literal[None]
    artist: Literal[None]

class ReleaseType(StrEnum):
    FEATURE = 'Feature'
    PRODUCTION = 'Production'
    SINGLE = 'Single'
    ALBUM_TRACK = 'Album Track'
    OTHER = 'Other'

class FakeType(StrEnum):
    FAKE_RUMOR = 'Fake Rumor'
    FAKE_LEAK = 'Fake Leak'
    STEM_EDIT = 'Stem Edit'
    COMP = 'Comp'
    IMPRESSION = 'Impression'
    AI = 'AI'

class SscType(StrEnum):
    FEATURE = 'Feature'
    OG = 'OG'
    OTHER = 'OTHER'
    PERFORMANCE = 'Performance'
    REF_TRACK = 'Ref Track'
    REHEARSAL = 'Rehearsal'
    STUDIO_RECORDING = 'Studio Recording'
    UNKNOWN = 'Unknown'

@dataclass
class SscSong(Song):
    og_filename: Optional[str]
    track_length: Optional[str]
    file_date: Optional[str]
    leak_date: Optional[str]
    type: SscType
    available_length: AvaliableLength
    quality: Quality

@dataclass
class Fake(Song):
    unknown_collabs: Optional[str]
    made_by: str
    fake_type: FakeType
    available_length: str

@dataclass
class ReleasedSong(Song):
    length: str
    release_date: str
    release_type: ReleaseType
    streaming: bool

@dataclass
class UnreleasedSong(Song):
    emoji: Optional[SongEmoji]
    unknown_collabs: Optional[str]
    og_filename: Optional[str]
    track_length: Optional[str]
    file_date: Optional[str]
    leak_date: Optional[str]
    available_length: AvaliableLength
    quality: Quality
    
    @cached_property
    def all_names(self):
        return [self.name, *self.aliases]
    
    @cached_property
    def emoji_name(self) -> SongEmojiName:
        emoji_to_name: dict[SongEmoji, SongEmojiName] = {
            '⭐': 'Best Of', 
            '✨': 'Special', 
            '🏆': 'Grail', 
            '🗑️': 'Worst Of' 
        }
        if self.emoji is None:
            return None
        else:
            return emoji_to_name[self.emoji]

type UnreleasedEraStatKeys = Literal['og_file', 'full', 'tagged', 'partial', 'snippet', 'unavailable']
type UnreleasedEraStats = dict[UnreleasedEraStatKeys, int]
type ReleasedEraStatKeys = Literal['album_track', 'single', 'feature', 'production', 'other']
type ReleasedEraStats = dict[ReleasedEraStatKeys, int]

@dataclass
class SubEra:
    name: str
    events: dict[str, str]
    super_era: str

@dataclass
class Era[T: (UnreleasedEraStats, ReleasedEraStats, None)]:
    stats: T
    name: str
    collabs: Optional[str]
    aliases: list[str]
    events: dict[str, str]
    ongoing: bool
    notes: str

    @property
    def all_names(self):
        return [self.name, *self.aliases]

type UnreleasedEra = Era[UnreleasedEraStats]
type ReleasedEra = Era[ReleasedEraStats]
type GenericEra = Era[None]
