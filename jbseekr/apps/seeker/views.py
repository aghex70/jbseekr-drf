import logging

from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from . import tasks, serializers


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger('msd')

    @property
    def logger(self):
        """Return logger"""
        return self._logger

    @logger.setter
    def logger(self, value):
        """Set logger"""
        self._logger = value


class PositionGeneratorViewSet(BaseViewSet):

    """
    Viewset that retrieves job offers for all sources.
    """

    authentication_classes = []
    permission_classes = ()
    serializer_class = serializers.PositionQuerySerializer

    @swagger_auto_schema(request_body=serializer_class, security=[])
    def create(self, request):

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            self.logger.error(f"Validation error: {serializer.errors}")
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        saved_data = serializer.save()
        tasks.generate_offers.apply_async(kwargs=saved_data, countdown=0)
        return Response(status=status.HTTP_201_CREATED)


class PositionViewSet(viewsets.ModelViewSet):
    pass
