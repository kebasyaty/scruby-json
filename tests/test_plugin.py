"""Test Plugin."""

from __future__ import annotations

import pytest
from pydantic import Field
from scruby import Scruby, ScrubyModel, ScrubySettings
from scruby_json import ReturnJson

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Plugins connection.
ScrubySettings.plugins = [
    ReturnJson,
]


class Car(ScrubyModel):
    """Car model."""

    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    year: int = Field(strict=True, frozen=True)
    power_reserve: int = Field(strict=True, frozen=True)
    description: str = Field(strict=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


class TestPositive:
    """Positive tests."""

    async def test_find_one(self) -> None:
        """Test a `find_one` method."""
        # Delete DB.
        Scruby.napalm()
        #
        # Get collection `Car`
        car_coll = await Scruby.collection(Car)
        # Create cars.
        for num in range(1, 10):
            car = Car(
                brand="Mazda",
                model=f"EZ-6 {num}",
                year=2025,
                power_reserve=600,
                description="Electric cars are the future of the global automotive industry.",
            )
            await car_coll.add_doc(car)
        # Find a car
        car_json: str | None = await car_coll.plugins.returnJson.find_one(
            filter_fn=lambda doc: doc.brand == "Mazda",
        )

        assert car_json is not None
        assert isinstance(car_json, str)
        assert Car.model_validate_json(car_json).brand == "Mazda"

        car_2_json: str | None = await car_coll.plugins.returnJson.find_one(
            filter_fn=lambda doc: doc.brand == "Mazda" and doc.model == "EZ-6 9",
        )

        assert car_2_json is not None
        assert isinstance(car_2_json, str)
        assert Car.model_validate_json(car_2_json).model == "EZ-6 9"
        #
        # Delete DB.
        Scruby.napalm()

    async def test_find_many(self) -> None:
        """Test a `find_many` method."""
        # Delete DB.
        Scruby.napalm()
        #
        # Get collection `Car`
        car_coll = await Scruby.collection(Car)
        # Create cars.
        for num in range(1, 10):
            car = Car(
                brand="Mazda",
                model=f"EZ-6 {num}",
                year=2025,
                power_reserve=600,
                description="Electric cars are the future of the global automotive industry.",
            )
            await car_coll.add_doc(car)
        # Find a car
        car_list: list[str] | None = await car_coll.plugins.returnJson.find_many()

        assert car_list is not None
        assert isinstance(car_list, list)
        assert len(car_list) == 9
        assert Car.model_validate_json(car_list[0]).brand == "Mazda"

        car_2_list: list[str] | None = await car_coll.plugins.returnJson.find_many(
            filter_fn=lambda doc: doc.brand == "Mazda",
        )

        assert car_2_list is not None
        assert isinstance(car_2_list, list)
        assert len(car_2_list) == 9
        assert Car.model_validate_json(car_2_list[0]).brand == "Mazda"

        car_3_list: list[str] | None = await car_coll.plugins.returnJson.find_many(
            filter_fn=lambda doc: doc.brand == "Mazda" and doc.model == "EZ-6 9",
        )

        assert car_3_list is not None
        assert isinstance(car_3_list, list)
        assert Car.model_validate_json(car_3_list[0]).model == "EZ-6 9"
        #
        # Delete DB.
        Scruby.napalm()
