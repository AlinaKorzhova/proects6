"""Клиенты для nominatim.openstreetmap.org и opensky-network.org."""
from abc import ABC, abstractmethod

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPENSKY_URL = "https://opensky-network.org/api/states/all"


class API(ABC):
    """Абстрактный класс для работы с любым API.

    SOLID: единственная ответственность — организовать HTTP-обмен.
    Потомки реализуют только логику конкретного сервиса.
    """

    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session = requests.Session()

    @abstractmethod
    def connect(self) -> bool:
        """Проверяет доступность сервиса."""

    @abstractmethod
    def get_data(self, *args, **kwargs):
        """Получает данные от сервиса."""


class NominatimAPI(API):
    """Получение географических координат (границ) страны."""

    def __init__(self):
        super().__init__(NOMINATIM_URL)
        self._session.headers["User-Agent"] = "planes-coursework/1.0"

    def connect(self) -> bool:
        response = self._session.get(self._base_url, params={"q": "test", "format": "json"})
        return response.status_code == 200

    def get_data(self, country: str) -> dict:
        """Возвращает bounding box страны: {'south', 'north', 'west', 'east'}."""
        response = self._session.get(
            self._base_url,
            params={"q": country, "format": "json", "limit": 1},
            timeout=15,
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            raise ValueError(f"Страна «{country}» не найдена в Nominatim")
        # boundingbox: [юг, север, запад, восток]
        south, north, west, east = map(float, results[0]["boundingbox"])
        return {"south": south, "north": north, "west": west, "east": east}


class OpenSkyAPI(API):
    """Получение информации о самолётах в воздушном пространстве области."""

    def connect(self) -> bool:
        response = self._session.get(OPENSKY_URL, params={"lamin": 0, "lomin": 0, "lamax": 1, "lomax": 1}, timeout=15)
        return response.status_code == 200

    def get_data(self, bbox: dict) -> list[dict]:
        """Принимает bounding box и возвращает список словарей с самолётами."""
        params = {
            "lamin": bbox["south"],
            "lamax": bbox["north"],
            "lomin": bbox["west"],
            "lomax": bbox["east"],
        }
        response = self._session.get(OPENSKY_URL, params=params, timeout=30)
        response.raise_for_status()
        states = response.json().get("states") or []
        planes = []
        for s in states:
            # Индексы по документации OpenSky REST
            planes.append({
                "icao24": s[0],
                "callsign": (s[1] or "").strip(),
                "country": s[2],            # страна регистрации
                "velocity": s[9],           # скорость, м/с
                "altitude": s[13],          # барометрическая высота, м
                "heading": s[10],           # курс, градусы
                "vertical_rate": s[11],     # вертикальная скорость, м/с
                "on_ground": s[8],
            })
        return planes
