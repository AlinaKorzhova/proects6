import json
import pytest

from plane import Plane
from storogane import JSONStorage
from main import fetch_planes, top_by_altitude, filter_by_country


def make_plane(icao24="abc123", callsign="TEST1", country="Germany",
               velocity=200.0, altitude=10000.0):
    return Plane(icao24, callsign, country, velocity, altitude)


# --- Plane ---
def test_plane_valid():
    p = make_plane()
    assert p.icao24 == "abc123"
    assert p.country == "Germany"

def test_plane_empty_callsign_raises():
    with pytest.raises(ValueError):
        make_plane(callsign="  ")

def test_plane_negative_velocity_raises():
    with pytest.raises(ValueError):
        make_plane(velocity=-5)

def test_plane_bad_heading_raises():
    with pytest.raises(ValueError):
        make_plane(velocity=100) and Plane("x", "x", "x", 100, 1000, heading=450)

def test_plane_non_numeric_velocity_raises():
    with pytest.raises(ValueError):
        make_plane(velocity="fast")

def test_comparison():
    fast = make_plane(velocity=300, altitude=5000)
    slow = make_plane(velocity=100, altitude=9000)
    assert fast.faster_than(slow)
    assert slow.higher_than(fast)
    assert sorted([fast, slow])[0] == fast  # по высоте выше slow → fast последний

# --- Storage ---
def test_json_storage_roundtrip(tmp_path):
    store = JSONStorage(str(tmp_path / "planes.json"))
    p = make_plane()
    store.add(p)
    loaded = store.get_all()
    assert loaded == [p]

def test_json_storage_get_by_country(tmp_path):
    store = JSONStorage(str(tmp_path / "planes.json"))
    store.add(make_plane(country="Germany"))
    store.add(make_plane(icao24="xyz", country="France"))
    assert len(store.get_by(country="Germany")) == 1

def test_json_storage_remove(tmp_path):
    store = JSONStorage(str(tmp_path / "planes.json"))
    store.add(make_plane())
    assert store.remove("abc123") is True
    assert store.remove("abc123") is False
    assert store.get_all() == []

def test_json_storage_no_duplicates(tmp_path):
    store = JSONStorage(str(tmp_path / "planes.json"))
    store.add(make_plane())
    store.add(make_plane())
    assert len(store.get_all()) == 1

# --- Фильтрация и сортировка ---
def test_top_by_altitude():
    planes = [make_plane(icao24=f"i{i}", altitude=i * 1000) for i in range(10)]
    top = top_by_altitude(planes, 3)
    assert [p.altitude for p in top] == [9000, 8000, 7000]

def test_filter_by_country_case_insensitive():
    planes = [make_plane(country="Germany"), make_plane(icao24="z", country="france")]
    assert len(filter_by_country(planes, "FRANCE")) == 1

def test_fetch_planes_mocked(monkeypatch):
    class FakeNominatim:
        def get_data(self, country):
            return {"south": 1, "north": 2, "west": 3, "east": 4}

    class FakeOpenSky:
        def get_data(self, bbox):
            return [{
                "icao24": "abc", "callsign": "CS1", "country": "Germany",
                "velocity": 250.0, "altitude": 11000.0, "heading": 90.0,
                "vertical_rate": 0.0, "on_ground": False,
            }]

    monkeypatch.setattr("main.NominatimAPI", lambda: FakeNominatim())
    monkeypatch.setattr("main.OpenSkyAPI", lambda: FakeOpenSky())
    planes = fetch_planes("Germany")
    assert len(planes) == 1
    assert planes[0].country == "Germany"
