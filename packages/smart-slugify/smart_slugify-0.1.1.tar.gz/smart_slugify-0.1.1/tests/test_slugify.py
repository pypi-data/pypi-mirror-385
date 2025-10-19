# tests/test_slugify.py

import pytest
from smart_slugify import slugify

def test_basic_ascii():
    assert slugify("Hello World!") == "hello-world"
    assert slugify("Hello   World!!") == "hello-world"

def test_accents_unicode():
    assert slugify("C'est déjà l'été!") == "c-est-deja-l-ete"
    assert slugify("São Paulo") == "sao-paulo"

def test_truncation():
    assert slugify("hello world example", max_length=10) == "hello-worl"
    # Also check that trailing sep is stripped
    assert slugify("hello-world-test", max_length=12) == "hello-world"

def test_custom_separator():
    assert slugify("Hello World!", separator="_") == "hello_world"
    assert slugify("Café au lait", separator="_") == "cafe_au_lait"

def test_empty_and_none():
    assert slugify("", max_length=5) == ""
    assert slugify(None) == ""