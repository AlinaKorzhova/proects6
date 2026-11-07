# main.py
"""Консольное приложение: запрос самолётов, топ по высоте, фильтр по стране."""
from api_class import NominatimAPI, OpenSkyAPI
from plane import Plane
from storagane import JSONStorage


def fetch_planes(country: str) -> list[Plane]:
    """Получает самолёты в воздушном пространстве страны."""
    nom = NominatimAPI()
    bbox = nom.get_data(country)
    sky = OpenSkyAPI()
    raw = sky.get_data(bbox)
    planes = []
    for item in raw:
        try:
            planes.append(Plane(
                icao24=item["icao24"],
                callsign=item["callsign"] or item["icao24"],
                country=item["country"] or "Unknown",
                velocity=item["velocity"],
                altitude=item["altitude"],
                heading=item["heading"],
                vertical_rate=item["vertical_rate"],
                on_ground=item["on_ground"],
            ))
        except (ValueError, TypeError):
            continue  # битые записи API пропускаем
    return planes


def top_by_altitude(planes: list[Plane], n: int) -> list[Plane]:
    """Топ N самолётов по высоте."""
    return sorted(planes, reverse=True)[:n]


def filter_by_country(planes: list[Plane], country: str) -> list[Plane]:
    """Самолёты по стране регистрации (без учёта регистра)."""
    return [p for p in planes if p.country.lower() == country.strip().lower()]


def show(planes: list[Plane]) -> None:
    if not planes:
        print("Самолёты не найдены.")
        return
    for p in planes:
        print(f"{p.icao24:<7} {p.callsign:<10} {p.country:<20} "
              f"скорость: {p.velocity} м/с   высота: {p.altitude} м")


def user_interaction() -> None:
    storage = JSONStorage("planes.json")
    cached: list[Plane] = storage.get_all()   # работаем с уже сохранёнными данными
    print("Текущих самолётов в базе:", len(cached))

    while True:
        print("\n1 — запросить самолёты по стране")
        print("2 — топ N по высоте")
        print("3 — самолёты по стране регистрации")
        print("0 — выход")
        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            break

        if choice == "1":
            country = input("Название страны: ").strip()
            try:
                cached = fetch_planes(country)
            except ValueError as e:
                print(f"Ошибка: {e}")
                continue
            for p in cached:
                storage.add(p)
            print(f"Найдено самолётов: {len(cached)} (сохранено в planes.json)")

        elif choice == "2":
            if not cached:
                print("Сначала запросите самолёты (пункт 1).")
                continue
            try:
                n = int(input("Сколько показать (N): "))
            except ValueError:
                print("N должно быть целым числом.")
                continue
            show(top_by_altitude(cached, max(n, 0)))

        elif choice == "3":
            if not cached:
                print("Сначала запросите самолёты (пункт 1).")
                continue
            country = input("Страна регистрации: ").strip()
            show(filter_by_country(cached, country))

        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    user_interaction()
