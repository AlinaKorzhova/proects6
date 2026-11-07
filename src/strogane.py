"""Хранилище информации о самолётах."""
from abc import ABC, abstractmethod
import json
from pathlib import Path

from plane import Plane


class StorageInterface(ABC):
    """Абстрактное хранилище самолётов.

    SOLID: открыт для расширения — вместо JSONStorage можно подставить
    коннектор к БД или удалённому хранилищу без изменения остального кода.
    """

    @abstractmethod
    def add(self, plane: Plane) -> None:
        """Добавляет информацию о самолёте."""

    @abstractmethod
    def get_all(self) -> list[Plane]:
        """Возвращает все самолёты."""

    @abstractmethod
    def get_by(self, country: str = None, min_altitude: float = None) -> list[Plane]:
        """Возвращает самолёты по критериям."""

    @abstractmethod
    def remove(self, icao24: str) -> bool:
        """Удаляет самолёт по icao24. True — если удалён."""


class JSONStorage(StorageInterface):
    """Хранение в JSON-файле."""

    def __init__(self, path: str = "planes.json"):
        self._path = Path(path)
        if not self._path.exists():
            self._write([])

    def _read(self) -> list[dict]:
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _write(self, data: list[dict]) -> None:
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, plane: Plane) -> None:
        data = self._read()
        # Заменяем запись, если такой борт уже есть (защита от дублей)
        data = [d for d in data if d.get("icao24") != plane.icao24]
        data.append(plane.to_dict())
        self._write(data)

    def get_all(self) -> list[Plane]:
        return [Plane.from_dict(d) for d in self._read()]

    def get_by(self, country: str = None, min_altitude: float = None) -> list[Plane]:
        planes = self.get_all()
        if country is not None:
            planes = [p for p in planes if p.country == country]
        if min_altitude is not None:
            planes = [p for p in planes if (p.altitude or 0) >= min_altitude]
        return planes

    def remove(self, icao24: str) -> bool:
        data = self._read()
        before = len(data)
        data = [d for d in data if d.get("icao24") != icao24]
        self._write(data)
        return len(data) < before


class DBStorage(StorageInterface):
    """Заглушка под коннектор к БД (пригодится для интеграции в будущем)."""

    def __init__(self, connection_params: dict):
        self._params = connection_params
        raise NotImplementedError("Коннектор к БД будет реализован позже")

    def add(self, plane): ...
    def get_all(self): ...
    def get_by(self, country=None, min_altitude=None): ...
    def remove(self, icao24): ...
