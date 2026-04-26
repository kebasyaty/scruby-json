<div align="center">
  <p align="center">
    <a href="https://github.com/kebasyaty/scruby-json">
      <img
        height="80"
        alt="Logo"
        src="https://raw.githubusercontent.com/kebasyaty/scruby-json/main/assets/logo.svg">
    </a>
  </p>
  <p>
    <h1>scruby-json</h1>
    <h3>Plugin for Scruby - In search methods, returns result as json strings.</h3>
    <p align="center">
      <a href="https://github.com/kebasyaty/scruby-json/actions/workflows/test.yml" alt="Build Status"><img src="https://github.com/kebasyaty/scruby-json/actions/workflows/test.yml/badge.svg" alt="Build Status"></a>
      <a href="https://kebasyaty.github.io/scruby-json/" alt="Docs"><img src="https://img.shields.io/badge/docs-available-brightgreen.svg" alt="Docs"></a>
      <a href="https://pypi.python.org/pypi/scruby-json/" alt="PyPI pyversions"><img src="https://img.shields.io/pypi/pyversions/scruby-json.svg" alt="PyPI pyversions"></a>
      <a href="https://pypi.python.org/pypi/scruby-json/" alt="PyPI status"><img src="https://img.shields.io/pypi/status/scruby-json.svg" alt="PyPI status"></a>
      <a href="https://pypi.python.org/pypi/scruby-json/" alt="PyPI version fury.io"><img src="https://badge.fury.io/py/scruby-json.svg" alt="PyPI version fury.io"></a>
      <br>
      <a href="https://pyrefly.org/" alt="Types: Pyrefly"><img src="https://img.shields.io/badge/types-Pyrefly-FFB74D.svg" alt="Types: Pyrefly"></a>
      <a href="https://docs.astral.sh/ruff/" alt="Code style: Ruff"><img src="https://img.shields.io/badge/code%20style-Ruff-FDD835.svg" alt="Code style: Ruff"></a>
      <a href="https://pypi.org/project/scruby-json"><img src="https://img.shields.io/pypi/format/scruby-json" alt="Format"></a>
      <a href="https://pepy.tech/projects/scruby-json"><img src="https://static.pepy.tech/badge/scruby-json" alt="PyPI Downloads"></a>
      <a href="https://github.com/kebasyaty/scruby-json/blob/main/LICENSE" alt="GitHub license"><img src="https://img.shields.io/github/license/kebasyaty/scruby-json" alt="GitHub license"></a>
    </p>
    <p align="center">
      scruby-json is a plugin for the <a href="https://pypi.org/project/scruby/" alt="Scruby">Scruby</a> project.
    </p>
  </p>
</div>

##

<br>

[![Documentation](https://raw.githubusercontent.com/kebasyaty/scruby-json/v0/assets/links/documentation.svg "Documentation")](https://kebasyaty.github.io/scruby-json/ "Documentation")

[![Requirements](https://raw.githubusercontent.com/kebasyaty/scruby-json/v0/assets/links/requirements.svg "Requirements")](https://github.com/kebasyaty/scruby-json/blob/v0/REQUIREMENTS.md "Requirements")

## Installation

```shell
uv add scruby-json
```

## Usage

[![Examples](https://raw.githubusercontent.com/kebasyaty/scruby-json/v0/assets/links/examples.svg "Examples")](https://kebasyaty.github.io/scruby-json/latest/pages/usage/ "Examples")

```python
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
      print(car_json_list)
    else:
      print("Not Found")

    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()


if __name__ == "__main__":
    anyio.run(main)
```

<br>

[![Changelog](https://raw.githubusercontent.com/kebasyaty/scruby-json/v0/assets/links/changelog.svg "Changelog")](https://github.com/kebasyaty/scruby-json/blob/v0/CHANGELOG.md "Changelog")

[![GPL-3.0](https://raw.githubusercontent.com/kebasyaty/scruby-json/v0/assets/links/mit.svg "MIT")](https://github.com/kebasyaty/scruby-json/blob/main/LICENSE "MIT")
