"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.validators import (
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import (
    ExternalIdentifierInput,
    GeojsonBaseFeatureInput,
    RealtimeParkingSiteInput,
    StaticParkingSiteInput,
)
from parkapi_sources.models.enums import ParkAndRideType, ParkingSiteType, PurposeType


@validataclass
class KienzlerInput:
    id: str = StringValidator(min_length=1)
    name: str = StringValidator()
    lat: Decimal = NumericValidator()
    long: Decimal = NumericValidator()
    bookable: int = IntegerValidator(min_value=0)
    sum_boxes: int = IntegerValidator(min_value=0)
    direct_link: str | None = UrlValidator(), Default(None)

    def to_static_parking_site(self, base_url: str) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=self.id,
            name=self.name,
            purpose=PurposeType.ITEM if 'Schließfächer' in self.name else PurposeType.BIKE,
            lat=self.lat,
            lon=self.long,
            has_realtime_data=True,
            capacity=self.sum_boxes,
            type=ParkingSiteType.LOCKERS,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            public_url=self.direct_link,
            opening_hours='24/7',
            has_fee=True,
        )

    def to_realtime_parking_site(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id,
            realtime_data_updated_at=datetime.now(tz=timezone.utc),
            realtime_capacity=self.sum_boxes,
            realtime_free_capacity=self.bookable,
        )


@validataclass
class KienzlerGeojsonFeaturePropertiesInput(ValidataclassMixin):
    uid: str = StringValidator(min_length=1, max_length=256)
    address: Optional[str] = StringValidator(max_length=512), Default(None)
    type: Optional[ParkingSiteType] = EnumValidator(ParkingSiteType), Default(None)
    max_height: int | None = IntegerValidator(min_value=0), Default(None)
    max_width: int | None = IntegerValidator(min_value=0), Default(None)
    max_depth: int | None = IntegerValidator(min_value=0), Default(None)
    park_and_ride_type: list[ParkAndRideType] = ListValidator(EnumValidator(ParkAndRideType))
    external_identifiers: list[ExternalIdentifierInput] | None = (
        ListValidator(
            DataclassValidator(ExternalIdentifierInput),
        ),
        Default(None),
    )


@validataclass
class KienzlerGeojsonFeatureInput(GeojsonBaseFeatureInput):
    properties: KienzlerGeojsonFeaturePropertiesInput = DataclassValidator(KienzlerGeojsonFeaturePropertiesInput)
