from dataclasses import dataclass, astuple, MISSING
from enum import Enum, unique, StrEnum
from functools import cached_property, reduce
from typing import Any, Optional, TypedDict, Literal, Callable, TypeVar, NamedTuple, Self, ClassVar
import re
import json

from yetracker.legacy.entries import Song

from .entries import *
from googleapiclient.discovery import build

def get_el[T](l: list[T], i: int) -> Optional[T]:
    return l[i] if i < len(l) else None

class FetchedValues(TypedDict):
    spreadsheetId: str
    valueRanges: list

class Tracker:
    def __init__(self, api_key: Optional[str] = None, values_json: Optional[str] = None):
        self.spreadsheet_id = '1vW-nFbnR02F9BEnNPe5NBejHRGPt0QEGOYXLSePsC1k'

        self.using_json_data = values_json is not None
        
        self.using_api_key = api_key is not None

        self.just_fetched_values: FetchedValues = {
            "spreadsheetId": self.spreadsheet_id,
            'valueRanges': []
        }

        if self.using_api_key:
            self.service = build('sheets', 'v4', developerKey=api_key)
            self.spreadsheets = self.service.spreadsheets()
            self.values = self.spreadsheets.values()
        
        if self.using_json_data:
            self.just_fetched_values = json.loads(values_json)
        
        self.all_fetched_values = self.just_fetched_values
    
    def add_to_all_fetched_values(self):
        current_value_ranges: list = self.just_fetched_values['valueRanges']
        temp_all_fetched_values = current_value_ranges + self.all_fetched_values['valueRanges']

        sheet_pattern = re.compile(r'.+(?=\!)')
        def reduce_to_unique(cum: list, n: Any):
            n_sheet = sheet_pattern.match(n['range']).group()
            cum_sheets = [sheet_pattern.match(x['range']).group() for x in cum]
            if n_sheet in cum_sheets:
                return cum
            else:
                return cum + [n]

        self.all_fetched_values['valueRanges'] = reduce(reduce_to_unique, temp_all_fetched_values, [])
        
    def merge_tracker(self, other_tracker: 'Tracker'):
        self.just_fetched_values = other_tracker.all_fetched_values
        self.add_to_all_fetched_values()
    
    def save_to_file(self, file_name: str):
        self.add_to_all_fetched_values()
        with open(file_name, 'w') as file:
            json.dump(self.all_fetched_values, file)
    
    def get_album_cover(self):
        g = self.spreadsheets.get(spreadsheetId=self.spreadsheet_id, ranges=['Art!F:F'], includeGridData=True).execute()
        return g

    def get_general[P: Common](self, using_api_key: bool, sheet_class: type[P], sheet_name: str):
        if using_api_key:
            if not self.using_api_key:
                raise ValueError()
            
            self.just_fetched_values = self.values\
                .batchGet(spreadsheetId=self.spreadsheet_id, ranges=[sheet_name]).execute()
        elif not self.using_json_data:
            raise ValueError()

        self.add_to_all_fetched_values()
        data = [x['values'] for x in self.all_fetched_values['valueRanges']
                            if sheet_name in x['range']][0]
        
        return sheet_class(data)
        
    def get_unreleased_local(self):
        return self.get_general(False, Unreleased, 'Unreleased')
    
    def get_unreleased_fetch(self):
        return self.get_general(True, Unreleased, 'Unreleased')
    
    def get_released_local(self):
        return self.get_general(False, Released, 'Released')
    
    def get_released_fetch(self):
        return self.get_general(True, Released, 'Released')
    
    def get_stems_local(self):
        return self.get_general(False, Stems, 'Stems')
    
    def get_stems_fetch(self):
        return self.get_general(True, Stems, 'Stems')
    
    def get_samples_local(self):
        return self.get_general(False, Samples, 'Samples')
    
    def get_samples_fetch(self):
        return self.get_general(True, Samples, 'Samples')
    
    def get_groupbuys_local(self):
        return self.get_general(False, Groupbuys, 'Groupbuys')
    
    def get_groupbuys_fetch(self):
        return self.get_general(True, Groupbuys, 'Groupbuys')
    
    def get_album_copies_local(self):
        return self.get_general(False, AlbumCopies, 'Album Copies')
    
    def get_album_copies_fetch(self):
        return self.get_general(True, AlbumCopies, 'Album Copies')
    
    def get_fakes_local(self):
        return self.get_general(False, Fakes, 'Fakes')

    def get_fakes_fetch(self):
        return self.get_general(True, Fakes, 'Fakes')

class Common:
    def __init__(self, data: Any):
        self.data = data
    
    def _process_songs[T](self, raw_songs: list[list[str]], 
                                extra_process_func: Callable[[Song, list[str]], T]):
        songs: list[T] = []

        version_pattern = re.compile(r'\[(.+)\]')

        feat_pattern = re.compile(r'\(feat\. ([^(]+)\)')
        ref_pattern = re.compile(r'\(ref\. ([^(]+)\)')
        with_pattern = re.compile(r'\(with ([^(]+)\)')
        prod_pattern = re.compile(r'\(prod\. ([^(]+)\)')
        unknown_pattern = re.compile(r'\(\?\?\?. ([^(]+)\)')

        for song_raw in raw_songs:
            era = song_raw[0]

            song_name_info = song_raw[1]
            name_info_split = song_name_info.splitlines()

            name_line = name_info_split[0]

            version: Optional[str] = None
            version_match = version_pattern.search(name_line)
            if version_match != None:
                name_line = name_line.replace(version_match.group(), '')
                version = version_match.group(1)
            
            artist = None
            name_with_artist_split = name_line.split(' - ', 1)
            if len(name_with_artist_split) == 1:
                name = name_with_artist_split[0]
            else:
                artist, name = name_with_artist_split
                artist = artist.strip()

            name = name.strip()
            
            aliases_line: Optional[str] = None
            contribs = SongContribs()
            if len(name_info_split) >= 2:
                second_line = name_info_split[1]
                
                prod_match = prod_pattern.search(second_line)
                feat_match = feat_pattern.search(second_line)
                with_match = with_pattern.search(second_line)
                ref_match = ref_pattern.search(second_line)
                unknown_match = unknown_pattern.search(second_line)

                contribs.feat = feat_match.group(1) if feat_match != None else None
                contribs.ref = ref_match.group(1) if ref_match != None else None
                contribs.prod = prod_match.group(1) if prod_match != None else None
                contribs.with_ = with_match.group(1) if with_match != None else None
                contribs.unknown = unknown_match.group(1) if unknown_match != None else None

                if not any((feat_match, ref_match, prod_match, with_match, unknown_match)):
                    aliases_line = second_line
                elif len(name_info_split) >= 3:
                    aliases_line = name_info_split[2]
            
            aliases: list[str] = []
            if aliases_line is not None:
                aliases_line = aliases_line[1:-1]
                aliases = aliases_line.split(', ')
            
            notes = song_raw[2]

            links = []
            if len(song_raw) >= 9:
                links_str = song_raw[8] 
                links = links_str.split('\n')

            song = Song(era, artist, name, version, contribs, 
                        aliases, notes, links)
        
            song = extra_process_func(song, song_raw)
            songs.append(song)
        
        return songs

    def _process_eras(self, raw_eras: list[list[str]], stat_word_to_key: Optional[dict[str, str]] = None):
        eras: list[Era] = []

        collab_pattern = re.compile(r'(\n\(Collaboration with (.+)\))')
        alias_pattern = re.compile(r'\n\(.+\)')

        event_pattern = re.compile(r'\((.+)\) \((.+)\)')
        
        for era_raw in raw_eras:
            notes = era_raw[-1]
            name = era_raw[1]

            collab_matches: list[tuple[str, str]] = collab_pattern.findall(name)
            collab_name: str | None = None
            if len(collab_matches) > 0:
                collab = collab_matches[0]
                collab_name = collab[1]
                name = name.replace(collab[0], '')
            
            alias_matches: list = alias_pattern.findall(name)
            aliases: list[str] = []
            if len(alias_matches) > 0:
                alias_str: str = alias_matches[0] 
                aliases = alias_str[2:-1].split(', ') # Last index range is to remove brackets
                name = name.replace(alias_str, '')

            stats: Optional[dict[str, int]]
            if stat_word_to_key is None:
                stats = None
            else:
                stats_str = era_raw[0]
                stats = self.__process_era_stats(stats_str, stat_word_to_key)

            ongoing = False
            event_str = era_raw[2]
            event_split = event_str.split('\n')
            event_matches = [event_pattern.match(x) for x in event_split]
            
            events: dict[str, str] = dict()
            for i, x in enumerate(event_matches):
                if x is not None:
                    timestamp = x.group(1)
                    event = x.group(2)
                    events[timestamp] = event
                elif event_split[i] == '(Ongoing)':
                    ongoing = True

            era = Era(stats, name, collab_name, aliases, events, ongoing, notes)
            eras.append(era)
        
        return eras
        
    def __process_era_stats(self, stats_str: str, stat_word_to_key: dict[str, str]):
        stats_pattern = re.compile(r'(\d+) (.+)')
        stats_list = stats_str.split('\n')
        stats_matches = [stats_pattern.match(x) for x in stats_list]

        stats: dict[str, int] = dict()
        for stat_match in stats_matches:
            number = stat_match.group(1)
            stat_key = stat_word_to_key[(stat_match.group(2))]
            stats[stat_key] = int(number)
        
        return stats
    
class Ssc(Common):
    def __init__(self, data: Any):
        super().__init__(data)
        self._process_data()

    def _process_data(self):
        rows = self.data[1:]

        raw_eras = []

class Unreleased(Common):
    def __init__(self, data: Any):
        super().__init__(data)
        self._process_data()

    def _process_data(self):
        rows = self.data[1:]

        raw_eras = [row for row in rows if len(row) == 6]
        self.eras = self._process_eras(raw_eras)

        raw_songs = [row for row in rows if len(row) >= 8]
        self.songs = self._process_songs(raw_songs)
        
        # The second row in the tuple is the song that contains the super era
        raw_sub_eras = [(row, rows[i+1]) for i, row in enumerate(rows) if len(row) == 3]
        self.sub_eras = self._process_sub_eras(raw_sub_eras)
    
    def _process_sub_eras(self, raw_sub_eras: list[tuple[list[str], list[str]]]):
        sub_eras: list[SubEra] = []

        event_pattern = re.compile(r'\((.+)\) \((.+)\)')
        for sub_era_raw, song_from_sub_era in raw_sub_eras:
            super_era = song_from_sub_era[0]
            if super_era not in [x.name for x in self.eras]:
                break

            name = sub_era_raw[1]
                
            event_str = sub_era_raw[2]
            event_split = event_str.split('\n')
            event_matches = [event_pattern.search(x) for x in event_split]
            
            events: dict[str, str] = dict()
            for x in event_matches:
                if x is not None:
                    timestamp = x.group(1)
                    event = x.group(2)
                    events[timestamp] = event
            
            sub_era = SubEra(name, events, super_era)
            sub_eras.append(sub_era)
        
        return sub_eras
    
    def get_era_from_name(self, name: str) -> Era:
        for era in self.eras:
            if era.name == name:
                return era

    def _process_songs(self, raw_songs: list[list[str]]):
        emoji_pattern = re.compile(r'⭐|✨|🏆|🗑️')
        og_filename_pattern = re.compile(r'OG Filename: (.+)\n')

        def extra_unreleased_process(base_song: Song, song_raw: list[str]) -> UnreleasedSong:
            name = base_song.name
            artist = base_song.artist

            emoji = None
            if artist is not None:
                emoji_match = emoji_pattern.search(artist)

                if emoji_match is not None:
                    base_song.artist = artist.replace(emoji_match.group(), '').strip()
                    emoji = emoji_match.group(0)
            else:
                emoji_match = emoji_pattern.search(name)

                if emoji_match is not None:
                    base_song.name = name.replace(emoji_match.group(), '').strip()
                    emoji = emoji_match.group(0)
            
            version = base_song.version
            unknown_collabs: Optional[str] = None
            if version is not None and ('Collaborations' in version 
                                    or 'Reference Track' in version):
                unknown_collabs = version
                base_song.version = None
            
            notes = base_song.notes
            og_filename: Optional[str] = None
            og_filename_match = og_filename_pattern.match(notes)
            if og_filename_match is not None:
                og_filename = og_filename_match.group(1)
                base_song.notes = notes.replace(og_filename_match.group(0), '')

            track_length = song_raw[3] if song_raw[3] != '' else None
            file_date = song_raw[4] if song_raw[4] != '' else None
            leak_date = song_raw[5] if song_raw[5] != '' else None

            available_length = AvaliableLength(song_raw[6])
            quality = Quality(song_raw[7])

            return UnreleasedSong(*astuple(base_song), emoji, unknown_collabs, og_filename,
                            track_length, file_date, leak_date,
                            available_length, quality)

        songs = super()._process_songs(raw_songs, extra_unreleased_process)

        return songs

    def _process_eras(self, raw_eras: list[list[str]]) -> list[UnreleasedEra]:
        stat_word_to_key:dict[str, UnreleasedEraStatKeys] = {
            'OG File(s)': 'og_file',
            'Full': 'full',
            'Tagged': 'tagged',
            'Partial': 'partial',
            'Unavailable': 'unavailable',
            'Snippet(s)': 'snippet'
        }

        return super()._process_eras(raw_eras, stat_word_to_key)

class Fakes(Common):
    def __init__(self, data: Any):
        super().__init__(data)
        self._process_data()

    def _process_data(self):
        rows = self.data[1:]
        raw_fakes = [row + ['', row[6]] for row in rows if len(row) >= 6]

        self.fakes = self._process_fakes(raw_fakes)

    def _process_fakes(self, raw_fakes: list[list[str]]):
        def extra_fake_process(base_song: Song, song_raw: list[str]):

            version = base_song.version
            unknown_collabs: Optional[str] = None
            if version is not None and ('Collaborations' in version 
                                    or 'Reference Track' in version):
                unknown_collabs = version
                base_song.version = None

            made_by = song_raw[3]
            fake_type = FakeType(song_raw[4])
            available_length = AvaliableLength(song_raw[5])

            
            return Fake(*astuple(base_song), unknown_collabs, made_by, fake_type, available_length)

        return self._process_songs(raw_fakes, extra_fake_process)

class Stems(Common):
    def __init__(self, data: Any):
        super().__init__(data)
        self._process_data()

    def _process_data(self):
        rows = self.data[1:]

        raw_eras = [row
                    for row in rows if len(row) == 7 
                    ]
        self.eras = self._process_eras(raw_eras)

        raw_stems = [row 
                    if len(row) != 2 else row + ['a' for _ in range(7)]
                    for row in rows if len(row) >= 8 
                    or len(row) == 2]

        self.stems = self._process_stems(raw_stems)
    
    def _process_stems(self, raw_stems: list[list[str]]):
        og_filename_pattern = re.compile(r'OG Filenames?: ((.+ & *\n)*.+)\n')

        stem_type = None
        def extra_stem_process(base_song: Song, song_raw: list[str]):
            if song_raw[0] == '':
                nonlocal stem_type 
                stem_type = StemType(song_raw[1])
                return None

            notes = base_song.notes
            og_filename: Optional[str] = None

            og_filename_match = og_filename_pattern.match(notes)
            if og_filename_match is not None:
                og_filename = og_filename_match.group(1)
                base_song.notes = notes.replace(og_filename_match.group(0), '')

            file_date = song_raw[3] if song_raw[3] != '' else None
            full_length = song_raw[4] if song_raw[4] != '' else None
            bpm = song_raw[5]

            available_length = AvaliableLength(song_raw[6])
            quality = Quality(song_raw[7])

            return Stem(*astuple(base_song), stem_type,
                        og_filename, file_date, full_length,
                        bpm, available_length, quality)

        return  [x for x in super()._process_songs(raw_stems, extra_stem_process) if x is not None]

    def _process_eras(self, raw_eras: list[list[str]]) -> list[GenericEra]:
        return super()._process_eras(raw_eras)

class Samples(Common):
    def __init__(self, data: Any):
        super().__init__(data)
        self._process_data()

    def _process_data(self):
        rows = self.data[1:]
        raw_samples = [row for row in rows if len(row) >= 4]

        self.samples = self._process_samples(raw_samples)
    
    def _process_samples(self, raw_samples: list[list[str]]):
        def extra_sample_process(base_song: Song, raw_sample: list[str]):
            samples_str = base_song.notes

            base_song.notes = raw_sample[3]

            samples: list[SampleTuple] = []
            samples_split = samples_str.splitlines()
            for sample_line in samples_split:

                sample_line_split = sample_line.split(' - ')
                if len(sample_line_split) >= 2: 
                    artist, *name_list = sample_line_split
                    name =  ' - '.join(name_list)
                else:
                    artist = None
                    name = sample_line

                sample_tuple = SampleTuple(artist, name)
                samples.append(sample_tuple)
            
            if len(raw_sample) == 5:
                link_str = raw_sample[4]
                base_song.links = link_str.split('\n')

            return Sample(*astuple(base_song), samples)

        return super()._process_songs(raw_samples, extra_sample_process)

class Groupbuys(Common):
    def __init__(self, data: Any):
        super().__init__(data)
        self._process_data()

    def _process_data(self):
        rows = self.data[1:]

        raw_groupbuys = [row for row in rows if len(row) >= 8]
        self.groupbuys = self._process_groupbuys(raw_groupbuys)
    
    def _process_groupbuys(self, raw_songs: list[list[str]]):
        tag_pattern = re.compile(r'\([^\(]+\)')
        has_stems_pattern = re.compile(r'((\+ )|\()?[Ss]tems?\)?')
        price_pattern = re.compile(r'\$((\d|\,)+)')

        def extra_groupbuy_process(base_song: Song, song_raw: list[str]):
            main_era = base_song.era
            main_content = base_song.name
            snippets = base_song.links
            aliases = base_song.aliases

            all_content_str = base_song.notes
            all_content_split = all_content_str.splitlines()
            all_content: list[GroupbuyContent] = []

            for line in all_content_split:
                has_stems_match = has_stems_pattern.search(line)
                stems = has_stems_match is not None
                if stems:
                    line = line.replace(has_stems_match.group(), '')

                tags: list[str] = tag_pattern.findall(line)
                for tag in tags:
                    line = line.replace(tag, '').strip()
                
                content = GroupbuyContent(line, tags, stems)
                all_content.append(content)
            
            price = int(
                price_pattern.search(song_raw[3])\
                    .group(1).replace(',', '')
            )

            start_and_end_date: tuple[str] = song_raw[4], song_raw[5]
            groupbuy_type = GroupbuyType(song_raw[6])
            status = GroupbuyStatus(song_raw[7])

            return Groupbuy(main_era, main_content, aliases, all_content, price, 
                            start_and_end_date, groupbuy_type, status, snippets)

        return super()._process_songs(raw_songs, extra_groupbuy_process)

class AlbumCopies(Common):
    def __init__(self, data: Any):
        super().__init__(data)
        self._process_data()

    def _process_data(self):
        rows = self.data[1:]

        raw_album_copies = [row + [row[7]] for row in rows if len(row) >= 8]
        self.album_copies = self._process_album_copies(raw_album_copies)
    
    def _process_album_copies(self, raw_album_copies: list[list[str]]):
        og_filename_pattern = re.compile(r'OG Filename: (.+)\n')

        def extra_album_copies_process(base_song: Song, copy_raw: list[str]):
            copy_length = copy_raw[3] if copy_raw[3] != '' else None
            file_date = copy_raw[4] if copy_raw[4] != '' else None 
            available_length = AvaliableLength(copy_raw[5])
            quality = Quality(copy_raw[6])

            if base_song.artist is not None:
                base_song.name = base_song.artist + ' - ' + base_song.name
                base_song.artist = None

            notes = base_song.notes
            og_filename: Optional[str] = None

            og_filename_match = og_filename_pattern.match(notes)
            if og_filename_match is not None:
                og_filename = og_filename_match.group(1)
                base_song.notes = notes.replace(og_filename_match.group(0), '')

            return AlbumCopy(*astuple(base_song), copy_length, og_filename, 
                            file_date, available_length, quality)
        
        return super()._process_songs(raw_album_copies, extra_album_copies_process)

class Released(Common):
    def __init__(self, data: Any):
        super().__init__(data)
        self._process_data()

    def _process_data(self):
        rows = self.data[2:]

        raw_eras = [row for row in rows if len(row) == 6]
        self.eras = self._process_eras(raw_eras)

        raw_songs = [row + [row[7]] for row in rows if len(row) >= 8]
        self.songs = self._process_songs(raw_songs)
    
    def _process_songs(self, raw_songs: list[list[str]]):
        def extra_released_process(base_song: Song, song_raw: list[str]):
            length = song_raw[3]
            release_date = song_raw[4]
            release_type = ReleaseType(song_raw[5])
            streaming = song_raw[6] == 'Yes'
            return ReleasedSong(*astuple(base_song), length, release_date, release_type, streaming)

        return super()._process_songs(raw_songs, extra_released_process)

    def _process_eras(self, raw_eras: list[list[str]]) -> list[ReleasedEra]:
        stat_word_to_key:dict[str, ReleasedEraStatKeys] = {
            'Album Track(s)': 'album_track',
            'Feature(s)': 'feature',
            'Other': 'other',
            'Production': 'production',
            'Single(s)': 'single',
        }

        return super()._process_eras(raw_eras, stat_word_to_key)
