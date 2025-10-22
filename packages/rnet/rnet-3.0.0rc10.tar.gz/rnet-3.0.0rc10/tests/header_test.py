import pytest
from rnet.header import OrigHeaderMap, HeaderMap


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_construction_and_is_empty():
    h = HeaderMap()
    assert h.is_empty()
    assert len(h) == 0
    assert h.keys_len() == 0


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_insert_and_get():
    h = HeaderMap()
    h.insert("Content-Type", "application/json")
    assert h.get("Content-Type") == b"application/json"
    assert h["Content-Type"] == b"application/json"
    assert h.contains_key("Content-Type")
    assert "Content-Type" in h
    assert not h.is_empty()
    assert len(h) == 1
    assert h.keys_len() == 1


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_append_and_get_all():
    h = HeaderMap()
    h.insert("Accept", "application/json")
    h.append("Accept", "text/html")
    all_vals = list(h.get_all("Accept"))
    assert all_vals == [b"application/json", b"text/html"]
    assert len(h) == 2
    assert h.keys_len() == 1


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_remove_and_delitem():
    h = HeaderMap()
    h.insert("X-Test", "foo")
    h.remove("X-Test")
    assert not h.contains_key("X-Test")
    h.insert("X-Test", "bar")
    del h["X-Test"]
    assert "X-Test" not in h


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_setitem_and_getitem():
    h = HeaderMap()
    h["A"] = "B"
    assert h["A"] == b"B"
    h["A"] = "C"
    assert h["A"] == b"C"
    assert list(h.get_all("A")) == [b"C"]


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_len_and_keys_len():
    h = HeaderMap()
    h.insert("A", "1")
    h.append("A", "2")
    h.insert("B", "3")
    assert len(h) == 3
    assert h.keys_len() == 2


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_clear():
    h = HeaderMap()
    h.insert("A", "1")
    h.insert("B", "2")
    h.clear()
    assert h.is_empty()
    assert len(h) == 0
    assert h.keys_len() == 0


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_iter():
    h = HeaderMap()
    h.insert("A", "1")
    h.append("A", "2")
    h.insert("B", "3")

    values = list(h.values())
    assert len(values) == 3
    assert b"1" in values
    assert b"2" in values
    assert b"3" in values

    keys = list(h.keys())
    assert len(keys) == 2
    assert b"a" in keys
    assert b"b" in keys

    items = list(iter(h))
    assert len(items) == 3
    assert (b"a", b"1") in items
    assert (b"a", b"2") in items
    assert (b"b", b"3") in items

    orig_h = OrigHeaderMap()
    orig_h.insert("A")
    orig_h.insert("B")
    orig_h.insert("C")
    orig_h.insert("d")

    items_orig = list(iter(orig_h))
    assert len(items_orig) == 4
    assert (b"a", b"A") in items_orig
    assert (b"b", b"B") in items_orig
    assert (b"c", b"C") in items_orig
    assert (b"d", b"d") in items_orig
    assert items_orig == [
        (b"a", b"A"),
        (b"b", b"B"),
        (b"c", b"C"),
        (b"d", b"d"),
    ]


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_edge_cases():
    h = HeaderMap()
    h.remove("nope")
    assert h.get("nope") is None
    assert list(h.get_all("nope")) == []
    try:
        del h["nope"]
    except KeyError:
        pass
    h.append("X", "1")
    assert h["X"] == b"1"
    h.append("X", "2")
    # hash is randomized, so we check both possible orders
    assert len(h) == 2
    assert (list(h.get_all("X")) == [b"1", b"2"]) or (
        list(h.get_all("X")) == [b"2", b"1"]
    )


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_get_with_default():
    h = HeaderMap()
    h.insert("A", "1")
    assert h.get("A") == b"1"
    assert h.get("B", b"default") == b"default"
    assert h.get("C") is None
    assert h.get("C", b"default") == b"default"
    assert h.get("A", b"default") == b"1"


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_init_with_dict():
    h = HeaderMap({"A": "1", "B": "2"})
    assert h["A"] == b"1"
    assert h["B"] == b"2"
    assert len(h) == 2
    assert h.keys_len() == 2
    assert not h.is_empty()
    assert h.contains_key("A")
    assert h.contains_key("B")
