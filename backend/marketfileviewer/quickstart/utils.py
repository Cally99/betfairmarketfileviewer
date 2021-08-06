import gzip
import bz2
import csv
import json
import pathlib
import betfairlightweight
from betfairlightweight.resources.baseresource import BaseResource
from django.http import HttpResponse

from .listener import CustomListener

CONFLATION = [0, 0.5, 1, 10, 60, 600]
MARKET_COLUMNS = [
    "marketId",
    "publishTime",
    "betDelay",
    "bspReconciled",
    "complete",
    "crossMatching",
    "status",
    "inplay",
    "version",
    "totalMatched",
]
SELECTION_COLUMNS = [
    "selectionId",
    "status",
    "handicap",
    "adjustmentFactor",
    "lastPriceTraded",
    "totalMatched",
    "removalDate",
]


def get_file_extension(file_path: str) -> str:
    # todo dodgy double suffix
    return pathlib.Path(file_path).suffix


def get_md_bz2(file_path: str) -> dict:
    mds = {}
    with bz2.BZ2File(file_path) as zipfile:
        for line in zipfile.readlines():
            update = json.loads(line)
            for market_update in update["mc"]:
                if "marketDefinition" in market_update:
                    mds[market_update["id"]] = _process_definition(
                        market_update["id"], market_update["marketDefinition"]
                    )
    return mds


def get_md_gz(file_path: str) -> dict:
    mds = {}
    with gzip.GzipFile(fileobj=file_path) as zipfile:
        for line in zipfile.readlines():
            update = json.loads(line)
            for market_update in update["mc"]:
                if "marketDefinition" in market_update:
                    mds[market_update["id"]] = _process_definition(
                        market_update["id"], market_update["marketDefinition"]
                    )
    return mds


def _process_definition(market_id: str, market_definition: dict) -> dict:
    market_definition["marketId"] = market_id
    market_definition["marketDate"] = BaseResource.strip_datetime(
        market_definition["marketTime"]
    ).date()
    for selection in market_definition["runners"]:
        selection["enable"] = True
    return market_definition


def get_updates_bz2(
    file_path: str,
    update_count: int,
    market_id: str,
    conflation: float,
    pre_play: bool,
    in_play: bool,
    seconds_to_start: int,
    operation: str = "marketSubscription",
) -> list:
    # create bflw listener
    listener = _create_listener(
        operation, conflation, pre_play, in_play, seconds_to_start
    )
    # process file
    updates = []
    with bz2.BZ2File(file_path) as zipfile:
        for _ in range(0, update_count):
            update = zipfile.readline()
            if update:
                _process_update(listener, update, updates, market_id)
            else:
                break
    return updates


def get_updates_gz(
    file_path: str,
    update_count: int,
    market_id: str,
    conflation: float,
    pre_play: bool,
    in_play: bool,
    seconds_to_start: int = None,
    operation: str = "marketSubscription",
) -> list:
    # create bflw listener
    listener = _create_listener(
        operation, conflation, pre_play, in_play, seconds_to_start
    )
    # process file
    updates = []
    with gzip.GzipFile(fileobj=file_path) as zipfile:
        for _ in range(0, update_count):
            update = zipfile.readline()
            if update:
                _process_update(listener, update, updates, market_id)
            else:
                break
    return updates


def create_csv(
    lines: list, market_columns: list, selection_columns: list
) -> HttpResponse:
    all_columns = market_columns + [
        "selection_{0}".format(i) for i in selection_columns
    ]
    # response
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="market-export.csv"'
    # writer
    writer = csv.DictWriter(response, fieldnames=all_columns)
    writer.writeheader()
    # process
    for market_book in lines:
        for selection in market_book["runners"]:
            x = {}
            # market
            for column in market_columns:
                value = market_book[column]
                if column == "publishTime":
                    value = BaseResource.strip_datetime(value)
                x[column] = value
            # selection
            for column in selection_columns:
                value = selection[column]
                if column == "lastPriceTraded":
                    value = value or None
                x["selection_{0}".format(column)] = value
            writer.writerow(x)
    return response


def _process_update(listener, update, updates: list, market_id: str) -> None:
    if listener.on_data(update) is False:
        raise ValueError("Processing error")  # todo
    data = listener.snap(market_ids=[market_id])
    if data:
        for market_book in data:
            del market_book["streaming_update"]
            del market_book["streaming_unique_id"]
            del market_book["streaming_snap"]
        updates += data


def _create_listener(
    operation: str,
    conflation: float,
    pre_play: bool,
    in_play: bool,
    seconds_to_start: int,
) -> betfairlightweight.StreamListener:
    listener = CustomListener(
        conflation=conflation,
        pre_play=pre_play,
        in_play=in_play,
        seconds_to_start=seconds_to_start,
    )
    listener.register_stream(0, operation)
    return listener
