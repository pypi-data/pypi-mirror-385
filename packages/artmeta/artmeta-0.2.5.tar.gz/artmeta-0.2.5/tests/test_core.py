"""
Tests pour le module core (classe ArtMeta)
"""

from pathlib import Path

import pytest
import yaml  # Keep yaml import for tests that modify metadata and dump to file

from artmeta.core import ArtMeta


def test_artmeta_init_with_existing_file(complete_metadata_file):
    """Test l'initialisation avec un fichier existant"""
    # Initialiser ArtMeta
    artmeta = ArtMeta(str(complete_metadata_file))

    assert artmeta.metadata_file == complete_metadata_file
    assert artmeta.meta is not None
    assert artmeta.meta["title"] == "My Complete Article"  # Updated title


def test_artmeta_init_with_nonexistent_file():
    """Test l'initialisation avec un fichier inexistant"""
    artmeta = ArtMeta("nonexistent.yml")

    assert artmeta.metadata_file == Path("nonexistent.yml")
    assert artmeta.meta is None


def test_get_authors_count(complete_metadata_file):  # Changed fixture
    """Test du comptage des auteurs"""
    artmeta = ArtMeta(str(complete_metadata_file))  # Used fixture

    assert artmeta.get_authors_count() == 2

    # Test avec aucun auteur
    artmeta.meta = {}
    assert artmeta.get_authors_count() == 0

    # Test avec meta None
    artmeta.meta = None
    assert artmeta.get_authors_count() == 0


def test_get_corresponding_author(complete_metadata_file):  # Changed fixture
    """Test de la récupération de l'auteur correspondant"""
    artmeta = ArtMeta(str(complete_metadata_file))  # Used fixture
    corr_author = artmeta.get_corresponding_author()

    assert corr_author is not None
    assert corr_author["firstname"] == "John"
    assert corr_author["lastname"] == "Doe"
    assert corr_author["corresponding"] is True

    # Test avec meta None
    artmeta.meta = None
    assert artmeta.get_corresponding_author() is None


def test_get_corresponding_author_none(tmp_path, complete_metadata_dict):  # Changed fixtures
    """Test get_corresponding_author when no author is corresponding"""
    meta_file = tmp_path / "art.yml"
    meta_data = complete_metadata_dict.copy()  # Use copy to avoid modifying the fixture
    meta_data["authors"][0]["corresponding"] = False
    meta_file.write_text(yaml.dump(meta_data), encoding="utf-8")
    artmeta = ArtMeta(str(meta_file))
    assert artmeta.get_corresponding_author() is None


def test_get_corresponding_author_no_authors_key(tmp_path):
    """Test get_corresponding_author when 'authors' key is missing"""
    meta_file = tmp_path / "art.yml"
    meta_data = {"title": "Title"}
    meta_file.write_text(yaml.dump(meta_data), encoding="utf-8")
    artmeta = ArtMeta(str(meta_file))
    assert artmeta.get_corresponding_author() is None


def test_get_corresponding_author_empty_authors(tmp_path):
    """Test get_corresponding_author when 'authors' is an empty list"""
    meta_file = tmp_path / "art.yml"
    meta_data = {"title": "Title", "authors": []}
    meta_file.write_text(yaml.dump(meta_data), encoding="utf-8")
    artmeta = ArtMeta(str(meta_file))
    assert artmeta.get_corresponding_author() is None


def test_get_affiliations_map(complete_metadata_file):  # Changed fixture
    """Test de la création du mapping des affiliations"""
    artmeta = ArtMeta(str(complete_metadata_file))  # Used fixture
    affil_map = artmeta.get_affiliations_map()

    assert len(affil_map) == 2
    assert 1 in affil_map
    assert 2 in affil_map
    assert affil_map[1]["name"] == "Research Lab"  # Updated name
    assert affil_map[2]["name"] == "AI Lab"  # Updated name

    # Test sans affiliations
    artmeta.meta = {}
    assert artmeta.get_affiliations_map() == {}

    # Test avec meta None
    artmeta.meta = None
    assert artmeta.get_affiliations_map() == {}


def test_get_title(tmp_path, complete_metadata_dict):  # Changed fixtures
    """Test de la récupération du titre"""
    meta_file = tmp_path / "art.yml"
    meta_data = complete_metadata_dict.copy()  # Use copy to avoid modifying the fixture
    # Add a short title for this specific test, as complete_metadata.yml doesn't have one
    meta_data["title_short"] = "My Short Title"
    meta_file.write_text(yaml.dump(meta_data), encoding="utf-8")

    artmeta = ArtMeta(str(meta_file))

    # Test titre normal
    assert artmeta.get_title() == "My Complete Article"  # Updated title

    # Test titre court
    assert artmeta.get_title(short=True) == "My Short Title"  # Updated title

    # Test titre court quand il n'existe pas (after deletion)
    del artmeta.meta["title_short"]
    assert artmeta.get_title(short=True) == "My Complete Article"  # Updated title

    # Test titre court vide
    artmeta.meta["title_short"] = ""
    assert artmeta.get_title(short=True) == "My Complete Article"  # Updated title

    # Test avec meta None
    artmeta.meta = None
    assert artmeta.get_title() == ""


def test_validate_file_not_found():
    """Test de validation avec fichier inexistant"""
    artmeta = ArtMeta("nonexistent.yml")

    with pytest.raises(FileNotFoundError) as exc_info:
        artmeta.validate()

    assert "nonexistent.yml" in str(exc_info.value)


def test_validate_meta_none(tmp_path):
    """Test de validation avec métadonnées None"""
    # Créer un fichier vide
    meta_file = tmp_path / "empty.yml"
    meta_file.write_text("", encoding="utf-8")

    artmeta = ArtMeta(str(meta_file))

    with pytest.raises(ValueError) as exc_info:
        artmeta.validate()

    assert "non chargées" in str(exc_info.value)
