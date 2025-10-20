from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Callable, TextIO

from yetracker.raw_values import *
from yetracker.tab import *

class NotAuthenticatedError(Exception):
    pass

class Tracker(ABC):
    "Base class for a tracker. Inherit to create a specific tracker."

    @overload
    def __init__(self, *, spreadsheet_id: str, api_key: str):
        ...

    @overload
    def __init__(self, *, raw_json: str | TextIO):
        ...

    @overload
    def __init__(self):
        ...

    def __init__(self, *, 
                 spreadsheet_id: str | None = None, 
                 api_key: str | None = None, 
                 raw_json: str | TextIO | None = None
        ):
        
        self.collected_raw_values: list[RawTabDict] = []

        if spreadsheet_id is not None and api_key is not None:
            self.use_api(spreadsheet_id, api_key)
        elif raw_json is not None:
            self.use_json(raw_json)

    def use_json(self, json: str | TextIO):
        self.raw_values_fetcher = RawValuesFromJson(json)
        
    def use_api(self, spreadsheet_id: str, api_key: str):
        self.raw_values_fetcher = RawValuesFromAPI(spreadsheet_id)
        self.raw_values_fetcher.authenticate(api_key)
    
    def save_data_to_file(self, file_name: str):
        with open(file_name, 'w') as f:
            json.dump(self.collected_raw_values, f)
    
    def _get_general[T: Tab](self, sheet_name: str, tab_cls: type[T]) -> T:
        if not self.raw_values_fetcher.authenticated:
            raise NotAuthenticatedError()

        raw_values: Range = self.raw_values_fetcher.get_raw_values(sheet_name)

        raw_tab_dict: RawTabDict = {
            'range': sheet_name,
            'values': raw_values
        }
        self.collected_raw_values.append(raw_tab_dict)

        return tab_cls(raw_values)

class YeTracker(Tracker):
    def get_unreleased(self):
        return self._get_general("Unreleased", UnreleasedTab)
    
    def get_released(self):
        return self._get_general("Released", ReleasedTab)

    def get_stems(self):
        return self._get_general("Stems", StemsTab)
    
    def get_samples(self):
        return self._get_general("Samples", SamplesTab)
