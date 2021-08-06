import json
from django.contrib.auth.models import User
from rest_framework import viewsets, parsers
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from . import serializers, utils


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = serializers.UserSerializer


@api_view(["GET"])
def navigation(request):
    navigation_data = {
        "settings": {
            "conflation": utils.CONFLATION,
            "columns": {
                "market": utils.MARKET_COLUMNS,
                "selection": utils.SELECTION_COLUMNS,
            },
        }
    }
    return Response(navigation_data)


class FileProcessViewSet(viewsets.ViewSet):
    """
    POST /api/file-process/
        Return list of raw marketBook objects
    POST /api/file-process/csv
        Return csv
        todo runner/market level? time/time_to_start/marketType/selectionId filter?
        todo zip outfile?
    """

    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializers.FileProcessSerializer

    def list(self, request):
        serializer = serializers.FileProcessSerializer(instance=[], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="market-definition")
    def market_definition(self, request):
        up_file = request.FILES["file"]
        # get all marketDefinitions
        mds = self._get_mds(up_file)
        return Response(mds)

    @action(detail=False, methods=["post"], url_path="market-book")
    def market_book(self, request):
        """
        Read / uncompress file
        Process file through bflw
        Return list of raw marketBooks
        # todo cache?
        # todo paginate
        # todo virus scanning
        """
        up_file = request.FILES["file"]
        update_count = request.POST.get("update_count") or 1
        # get lines
        lines = self._get_lines(up_file, int(update_count))
        # serializer = serializers.FileProcessSerializer(instance=lines, many=True)
        return Response(lines)

    @action(detail=False, methods=["post"], url_name="csv")
    def csv(self, request):
        """
        Read / uncompress file
        Process file through bflw
        Return csv based on columns
        # todo cache?
        # todo paginate
        # todo virus scanning
        """
        up_file = request.FILES["file"]
        market_id = request.POST.get("marketId")
        pre_play = json.loads(request.POST["preplay"])
        in_play = json.loads(request.POST["inplay"])
        conflation = float(request.POST["conflation"])
        market_columns = request.POST["marketColumns"]
        selection_columns = request.POST["selectionColumns"]
        seconds_to_start = request.POST.get("secondsToStart", None)
        if market_columns:
            market_columns = market_columns.split(",")
        else:
            market_columns = []
        if selection_columns:
            selection_columns = selection_columns.split(",")
        else:
            selection_columns = []
        # get lines
        lines = self._get_lines(
            up_file,
            int(1e6),
            market_id,
            conflation,
            pre_play,
            in_play,
            seconds_to_start,
        )
        # create csv
        return utils.create_csv(lines, market_columns, selection_columns)

    @staticmethod
    def _get_mds(up_file) -> dict:
        # get file extension
        file_extension = utils.get_file_extension(up_file.name)
        # process
        if file_extension == ".bz2":
            return utils.get_md_bz2(up_file)
        elif file_extension == ".gz":
            return utils.get_md_gz(up_file)
        else:
            raise ValueError("Unknown filetype")  # todo handle zip/raw file

    @staticmethod
    def _get_lines(
        up_file,
        update_count: int,
        market_id: str,
        conflation: float,
        pre_play: bool,
        in_play: bool,
        seconds_to_start: int,
    ) -> list:
        # get file extension
        file_extension = utils.get_file_extension(up_file.name)
        # process
        if file_extension == ".bz2":
            return utils.get_updates_bz2(
                up_file,
                update_count,
                market_id,
                conflation,
                pre_play,
                in_play,
                seconds_to_start,
            )
        elif file_extension == ".gz":
            return utils.get_updates_gz(
                up_file, update_count, market_id, conflation, pre_play, in_play
            )
        else:
            raise ValueError("Unknown filetype")  # todo handle zip/raw file
