"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from requests import ConnectionError, JSONDecodeError, Response
from urllib3.exceptions import NewConnectionError
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.exceptions import ImportParkingSiteException, ImportParkingSpotException, ImportSourceException
from parkapi_sources.models import (
    GeojsonFeatureInput,
    GeojsonFeatureParkingSpotInput,
    GeojsonInput,
    SourceInfo,
    StaticParkingSiteInput,
    StaticParkingSpotInput,
)
from parkapi_sources.util import ConfigHelper


class StaticGeojsonDataMixin(ABC):
    config_helper: ConfigHelper
    source_info: SourceInfo
    apply_static_patches: Callable
    geojson_validator = DataclassValidator(GeojsonInput)
    geojson_feature_parking_sites_validator = DataclassValidator(GeojsonFeatureInput)
    geojson_feature_parking_spots_validator = DataclassValidator(GeojsonFeatureParkingSpotInput)
    _base_url = 'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/main/sources'

    @abstractmethod
    def request_get(self, **kwargs) -> Response: ...

    def _get_static_parking_sites_geojson(self, source_uid: str) -> GeojsonInput:
        base_path: str | None = self.config_helper.get('STATIC_GEOJSON_BASE_PATH')
        if base_path:
            with Path(base_path, f'{source_uid}.geojson').open() as geojson_file:
                return json.loads(geojson_file.read())
        else:
            try:
                response = self.request_get(
                    url=f'{self.config_helper.get("STATIC_GEOJSON_BASE_URL")}/{source_uid}.geojson',
                    timeout=30,
                )
            except (ConnectionError, NewConnectionError) as e:
                raise ImportParkingSiteException(
                    source_uid=self.source_info.uid,
                    message='Connection issue for GeoJSON data',
                ) from e
            try:
                return response.json()
            except JSONDecodeError as e:
                raise ImportParkingSiteException(
                    source_uid=self.source_info.uid,
                    message='Invalid JSON response for GeoJSON data',
                ) from e

    def _get_static_parking_spots_geojson(self, source_uid: str) -> GeojsonInput:
        base_path: str | None = self.config_helper.get('STATIC_GEOJSON_BASE_PATH')
        if base_path:
            with Path(base_path, 'parking-spots', f'{source_uid}.geojson').open() as geojson_file:
                return json.loads(geojson_file.read())
        else:
            try:
                response = self.request_get(
                    url=f'{self.config_helper.get("STATIC_GEOJSON_BASE_URL")}/parking-spots/{source_uid}.geojson',
                    timeout=30,
                )
            except (ConnectionError, NewConnectionError) as e:
                raise ImportParkingSpotException(
                    source_uid=self.source_info.uid,
                    message='Connection issue for GeoJSON data',
                ) from e
            try:
                return response.json()
            except JSONDecodeError as e:
                raise ImportParkingSpotException(
                    source_uid=self.source_info.uid,
                    message='Invalid JSON response for GeoJSON data',
                ) from e

    def _get_static_parking_site_inputs_and_exceptions(
        self,
        source_uid: str,
    ) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        feature_inputs, import_parking_site_exceptions = self._get_geojson_parking_sites_features_and_exceptions(
            source_uid,
        )

        for feature_input in feature_inputs:
            static_parking_site_inputs.append(
                feature_input.to_static_parking_site_input(
                    # TODO: Use the Last-Updated HTTP header instead, but as Github does not set such an header, we
                    #  need to move all GeoJSON data in order to use this.
                    static_data_updated_at=datetime.now(tz=timezone.utc),
                ),
            )

        return self.apply_static_patches(static_parking_site_inputs), import_parking_site_exceptions

    def _get_static_parking_spots_inputs_and_exceptions(
        self,
        source_uid: str,
    ) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[StaticParkingSpotInput] = []

        feature_inputs, import_parking_spot_exceptions = self._get_geojson_parking_spots_features_and_exceptions(
            source_uid
        )

        for feature_input in feature_inputs:
            static_parking_spot_inputs.append(
                feature_input.to_static_parking_spot_input(
                    # TODO: Use the Last-Updated HTTP header instead, but as Github does not set such an header, we
                    #  need to move all GeoJSON data in order to use this.
                    static_data_updated_at=datetime.now(tz=timezone.utc),
                ),
            )

        return self.apply_static_patches(static_parking_spot_inputs), import_parking_spot_exceptions

    def _get_geojson_parking_sites_features_and_exceptions(
        self,
        source_uid: str,
    ) -> tuple[list[GeojsonFeatureInput], list[ImportParkingSiteException]]:
        geojson_dict = self._get_static_parking_sites_geojson(source_uid)
        try:
            geojson_input = self.geojson_validator.validate(geojson_dict)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=source_uid,
                message=f'Invalid GeoJSON for source {source_uid}: {e.to_dict()}. Data: {geojson_dict}',
            ) from e

        feature_inputs: list[GeojsonFeatureInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        for feature_dict in geojson_input.features:
            try:
                feature_inputs.append(self.geojson_feature_parking_sites_validator.validate(feature_dict))
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=feature_dict.get('properties', {}).get('uid'),
                        message=f'Invalid GeoJSON feature for source {source_uid}: {e.to_dict()}',
                    ),
                )

        return feature_inputs, import_parking_site_exceptions

    def _get_geojson_parking_spots_features_and_exceptions(
        self,
        source_uid: str,
    ) -> tuple[list[GeojsonFeatureParkingSpotInput], list[ImportParkingSpotException]]:
        geojson_dict = self._get_static_parking_spots_geojson(source_uid)
        try:
            geojson_input = self.geojson_validator.validate(geojson_dict)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=source_uid,
                message=f'Invalid GeoJSON for source {source_uid}: {e.to_dict()}. Data: {geojson_dict}',
            ) from e

        feature_inputs: list[GeojsonFeatureParkingSpotInput] = []
        import_parking_spot_exceptions: list[ImportParkingSpotException] = []

        for feature_dict in geojson_input.features:
            try:
                feature_inputs.append(self.geojson_feature_parking_spots_validator.validate(feature_dict))
            except ValidationError as e:
                import_parking_spot_exceptions.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=feature_dict.get('properties', {}).get('uid'),
                        message=f'Invalid GeoJSON feature for source {source_uid}: {e.to_dict()}',
                    ),
                )

        return feature_inputs, import_parking_spot_exceptions
