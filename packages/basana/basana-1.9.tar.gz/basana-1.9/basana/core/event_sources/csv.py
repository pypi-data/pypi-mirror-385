# Basana
#
# Copyright 2022 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional, Sequence
import abc
import codecs
import contextlib
import csv

from basana.core import event

# This module is not using async io. Why ?
# asyncio does not support asynchronous operations on the filesystem.
# Check https://github.com/python/asyncio/wiki/ThirdParty#filesystem.
# aiofiles could be used, but given that:
# * aiofiles delegates operations to a separate thread pool
# * this module will be used mostly for backtesting where there is no other IO taking place
# I decided not to support async io initially.


@contextlib.contextmanager
def open_file_with_detected_encoding(filename, default_encoding='utf-8'):
    with open(filename, 'rb') as file:
        raw = file.read(4)  # Read enough bytes to detect BOMs

    boms = [
        (codecs.BOM_UTF32_LE, 'utf-32-le'),
        (codecs.BOM_UTF32_BE, 'utf-32-be'),
        (codecs.BOM_UTF16_LE, "utf-16-le"),
        (codecs.BOM_UTF16_BE, "utf-16-be"),
        (codecs.BOM_UTF8, "utf-8-sig"),
    ]
    encoding = default_encoding
    offset = 0
    for bom, enc in boms:
        if raw.startswith(bom):
            encoding = enc
            offset = len(bom)
            break

    # Re-open the file with the detected encoding and skip the bom.
    f = open(filename, 'r', encoding=encoding)
    if offset:
        f.seek(offset)
    yield f


class RowParser(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse_row(self, row_dict: dict) -> Sequence[event.Event]:
        raise NotImplementedError()


def load_sort_and_yield(csv_path: str, row_parser: RowParser, dict_reader_kwargs: dict = {}):
    events = []

    # Load events.
    with open_file_with_detected_encoding(csv_path) as f:
        dict_reader = csv.DictReader(f, **dict_reader_kwargs)
        for row in dict_reader:
            for ev in row_parser.parse_row(row):
                events.append(ev)

    # Sort them for proper delivery.
    events = sorted(events, key=lambda ev: ev.when)

    for ev in events:
        yield ev


def load_and_yield(csv_path: str, row_parser: RowParser, dict_reader_kwargs: dict = {}):

    # Load events.
    with open_file_with_detected_encoding(csv_path) as f:
        dict_reader = csv.DictReader(f, **dict_reader_kwargs)
        for row in dict_reader:
            for ev in row_parser.parse_row(row):
                yield ev


class EventSource(event.EventSource, event.Producer):
    def __init__(self, csv_path: str, row_parser: RowParser, sort: bool = True, dict_reader_kwargs: dict = {}):
        super().__init__(producer=self)
        self._csv_path = csv_path
        self._row_parser = row_parser
        self._sort = sort
        self._dict_reader_kwargs = dict_reader_kwargs
        self._row_it = None

    async def initialize(self):
        if self._sort:
            self._row_it = load_sort_and_yield(self._csv_path, self._row_parser, self._dict_reader_kwargs)
        else:
            self._row_it = load_and_yield(self._csv_path, self._row_parser, self._dict_reader_kwargs)

    async def finalize(self):
        self._row_it = None

    def pop(self) -> Optional[event.Event]:
        ret = None
        try:
            if self._row_it:
                ret = next(self._row_it)
        except StopIteration:
            self._row_it = None
        return ret
