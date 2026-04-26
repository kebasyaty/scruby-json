```py title="main.py" linenums="1"
import anyio
from typing import Any
from pydantic import Field
from scruby import Scruby, ScrubyModel, ScrubySettings
from scruby_json import ReturnJson

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


async def main() -> None:
    """Example."""
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

    # Find one car
    car_json: str | None = await car_coll.plugins.returnJson.find_one(c
        filter_fn=lambda doc: doc.brand == "Mazda" and doc.model == "EZ-6 9",
    )
    if car_json is not None:
      print(car_json)
    else:
      print("Not Found")

    # Fand many cars
    car_json_list: list[str] | None = await car_coll.plugins.returnJson.find_many(
        filter_fn=lambda doc: doc.brand == "Mazda",
    )
    if car_json_list is not None:
      print(car_list)
    else:
      print("Not Found")

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```
