"""Класс самолёта с инкапсуляцией и валидацией атрибутов."""

NUMBER_FIELDS = ("velocity", "altitude", "heading", "vertical_rate")


class Plane:
    """Информация о самолёте в воздушном пространстве.

    Атрибуты (инкапсулированы, доступ через properties):
      icao24        — уникальный бортовой номер
      callsign      — позывной
      country       — страна регистрации
      velocity      — скорость, м/с
      altitude      — высота, м
      heading       — курс, градусы
      vertical_rate — вертикальная скорость, м/с
      on_ground     — на земле (bool)
    """

    def __init__(self, icao24: str, callsign: str, country: str,
                 velocity, altitude, heading=None, vertical_rate=None,
                 on_ground: bool = False):
        self.icao24 = self._validate_text(icao24, "icao24")
        self.callsign = self._validate_text(callsign, "callsign")
        self.country = self._validate_text(country, "country")
        self.velocity = velocity        # валидация в сеттерах
        self.altitude = altitude
        self.heading = heading
        self.vertical_rate = vertical_rate
        self.on_ground = bool(on_ground)

    # --- Валидация ---
    @staticmethod
    def _validate_text(value, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Поле {field} должно быть непустой строкой")
        return value.strip()

    def _validate_number(self, value, field: str):
        if value is not None and not isinstance(value, (int, float)):
            raise ValueError(f"Поле {field} должно быть числом")
        return value

    # --- Инкапсуляция: сеттеры с проверками ---
    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        self._velocity = self._validate_number(value, "velocity")
        if self._velocity is not None and self._velocity < 0:
            raise ValueError("Скорость не может быть отрицательной")

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        self._altitude = self._validate_number(value, "altitude")
        if self._altitude is not None and self._altitude < 0:
            raise ValueError("Высота не может быть отрицательной")

    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        self._heading = self._validate_number(value, "heading")
        if self._heading is not None and not 0 <= self._heading <= 360:
            raise ValueError("Курс должен быть в диапазоне 0–360")

    @property
    def vertical_rate(self):
        return self._vertical_rate

    @vertical_rate.setter
    def vertical_rate(self, value):
        self._vertical_rate = self._validate_number(value, "vertical_rate")

    # --- Сравнение ---
    def faster_than(self, other: "Plane") -> bool:
        """True, если этот самолёт быстрее."""
        return (self.velocity or 0) > (other.velocity or 0)

    def higher_than(self, other: "Plane") -> bool:
        """True, если этот самолёт выше."""
        return (self.altitude or 0) > (other.altitude or 0)

    def __eq__(self, other):
        return isinstance(other, Plane) and self.icao24 == other.icao24

    def __lt__(self, other):
        """Сортировка по высоте (основной критерий), при равенстве — по скорости."""
        if (self.altitude or 0) == (other.altitude or 0):
            return (self.velocity or 0) < (other.velocity or 0)
        return (self.altitude or 0) < (other.altitude or 0)

    def __gt__(self, other):
        return (self.altitude or 0) > (other.altitude or 0) or (
            (self.altitude or 0) == (other.altitude or 0) and (self.velocity or 0) > (other.velocity or 0)
        )

    def __repr__(self):
        return (f"Plane(icao24={self.icao24!r}, callsign={self.callsign!r}, "
                f"country={self.country!r}, velocity={self.velocity}, "
                f"altitude={self.altitude})")

    # --- Сериализация для хранения ---
    def to_dict(self) -> dict:
        return {
            "icao24": self.icao24, "callsign": self.callsign,
            "country": self.country, "velocity": self.velocity,
            "altitude": self.altitude, "heading": self.heading,
            "vertical_rate": self.vertical_rate, "on_ground": self.on_ground,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Plane":
        return cls(**data)
