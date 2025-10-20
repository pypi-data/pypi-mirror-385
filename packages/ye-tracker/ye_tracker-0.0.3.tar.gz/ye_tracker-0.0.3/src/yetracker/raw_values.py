from abc import ABC, abstractmethod
from googleapiclient.discovery import build
from typing import Any, TextIO, TypedDict
import json

type Row = list[str]
type Range = list[Row]

class RawValuesFetcher(ABC):
    def __init__(self):
        self.authenticated = False

    @abstractmethod
    def get_raw_values(self, tab_name: str) -> Range:
        pass

    @abstractmethod
    def authenticate(self, *args) -> Any:
        pass

class RawTabDict(TypedDict):
    values: Range
    range: str

type ProvidedJson = list[RawTabDict] | dict[str, list[RawTabDict]]

class RawValuesFromJson(RawValuesFetcher):
    def __init__(self, json_arg: str | TextIO):
        self.authenticated = True
        self._parse_json_data(json_arg)
    
    def _parse_json_data(self, json_arg: str | TextIO):
        if isinstance(json_arg, str):
            provided_json: ProvidedJson = json.loads(json_arg)
        else:
            provided_json: ProvidedJson = json.load(json_arg)
        
        if isinstance(provided_json, list):
            self.json_data = provided_json
        else:
            inner = provided_json.get('valueRanges')
            if isinstance(inner, list):
                self.json_data = inner
        
    
    def get_raw_values(self, tab_name: str) -> Range:
        for tab in self.json_data:
            if tab_name in tab['range']:
                return tab['values']
        
        raise KeyError()

    def authenticate(self, *args) -> Any:
        pass

class AuthenticationError(Exception):
    pass

class RawValuesFromAPI(RawValuesFetcher):
    def __init__(self, spreadsheet_id: str):
        super().__init__()
        self.spreadsheet_id = spreadsheet_id
    
    def authenticate(self, api_key: str | None = None, *args):
        if api_key is None:
            raise AuthenticationError()
        
        self._use_api_key(api_key)
        self.authenticated = True

    def _use_api_key(self, api_key: str):
        service = build('sheets', 'v4', developerKey=api_key)
        self.spreadsheets = service.spreadsheets()
        self.values = self.spreadsheets.values()
    
    def get_raw_values(self, tab_name: str) -> Range:
        response = self.values.get(
            spreadsheetId=self.spreadsheet_id,
            range=tab_name
        ).execute()

        return response['values']
