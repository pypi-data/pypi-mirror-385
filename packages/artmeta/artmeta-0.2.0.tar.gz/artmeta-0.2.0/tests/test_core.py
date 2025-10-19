"""
Tests pour le module core (classe ArtMeta)
"""

from pathlib import Path

import pytest
import yaml

from artmeta.core import ArtMeta


def get_sample_metadata_dict():
    """Retourne un dictionnaire de métadonnées de test"""
    return {
        "title": "Test Article Title",
        "title_short": "Test Title",
        "abstract": "This is a comprehensive test abstract for our article.",
        "authors": [
            {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john.doe@example.com",
                "orcid": "0000-0002-1825-0097",
                "affiliations": [1],
                "corresponding": True,
            },
            {
                "firstname": "Jane",
                "lastname": "Smith",
                "email": "jane.smith@university.fr",
                "affiliations": [1, 2],
            },
        ],
        "affiliations": [
            {
                "id": 1,
                "name": "Test Laboratory",
                "institution": "University of Testing",
                "city": "Testville",
                "country": "France",
            },
            {
                "id": 2,
                "name": "Another Lab",
                "institution": "Another University",
                "city": "Another City",
                "country": "Germany",
            },
        ],
        "keywords": ["testing", "validation"],
        "msc_codes": ["35K15"],
    }


def test_artmeta_init_with_existing_file(tmp_path):
    """Test l'initialisation avec un fichier existant"""
    # Créer un fichier de métadonnées temporaire
    meta_file = tmp_path / "art.yml"
    meta_data = get_sample_metadata_dict()
    meta_file.write_text(yaml.dump(meta_data), encoding="utf-8")

    # Initialiser ArtMeta
    artmeta = ArtMeta(str(meta_file))

    assert artmeta.metadata_file == meta_file
    assert artmeta.meta is not None
    assert artmeta.meta["title"] == "Test Article Title"


def test_artmeta_init_with_nonexistent_file():
    """Test l'initialisation avec un fichier inexistant"""
    artmeta = ArtMeta("nonexistent.yml")

    assert artmeta.metadata_file == Path("nonexistent.yml")
    assert artmeta.meta is None


def test_get_authors_count(tmp_path):
    """Test du comptage des auteurs"""
    meta_file = tmp_path / "art.yml"
    meta_data = get_sample_metadata_dict()
    meta_file.write_text(yaml.dump(meta_data), encoding="utf-8")

    artmeta = ArtMeta(str(meta_file))
    assert artmeta.get_authors_count() == 2

    # Test avec aucun auteur
    artmeta.meta = {}
    assert artmeta.get_authors_count() == 0

    # Test avec meta None
    artmeta.meta = None
    assert artmeta.get_authors_count() == 0


def test_get_corresponding_author(tmp_path):
    """Test de la récupération de l'auteur correspondant"""
    meta_file = tmp_path / "art.yml"
    meta_data = get_sample_metadata_dict()
    meta_file.write_text(yaml.dump(meta_data), encoding="utf-8")

    artmeta = ArtMeta(str(meta_file))
    corr_author = artmeta.get_corresponding_author()

    assert corr_author is not None
    assert corr_author["firstname"] == "John"
    assert corr_author["lastname"] == "Doe"
    assert corr_author["corresponding"] is True

    # Test avec meta None
    artmeta.meta = None
    assert artmeta.get_corresponding_author() is None


def test_get_corresponding_author_none(tmp_path):
    """Test get_corresponding_author when no author is corresponding"""
    meta_file = tmp_path / "art.yml"
    meta_data = get_sample_metadata_dict()
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


def test_get_affiliations_map(tmp_path):
    """Test de la création du mapping des affiliations"""
    meta_file = tmp_path / "art.yml"
    meta_data = get_sample_metadata_dict()
    meta_file.write_text(yaml.dump(meta_data), encoding="utf-8")

    artmeta = ArtMeta(str(meta_file))
    affil_map = artmeta.get_affiliations_map()

    assert len(affil_map) == 2
    assert 1 in affil_map
    assert 2 in affil_map
    assert affil_map[1]["name"] == "Test Laboratory"
    assert affil_map[2]["name"] == "Another Lab"

    # Test sans affiliations
    artmeta.meta = {}
    assert artmeta.get_affiliations_map() == {}

    # Test avec meta None
    artmeta.meta = None
    assert artmeta.get_affiliations_map() == {}


def test_get_title(tmp_path):
    """Test de la récupération du titre"""
    meta_file = tmp_path / "art.yml"
    meta_data = get_sample_metadata_dict()
    meta_file.write_text(yaml.dump(meta_data), encoding="utf-8")

    artmeta = ArtMeta(str(meta_file))

    # Test titre normal
    assert artmeta.get_title() == "Test Article Title"

    # Test titre court
    assert artmeta.get_title(short=True) == "Test Title"

    # Test titre court quand il n'existe pas
    del artmeta.meta["title_short"]
    assert artmeta.get_title(short=True) == "Test Article Title"

    # Test titre court vide
    artmeta.meta["title_short"] = ""
    assert artmeta.get_title(short=True) == "Test Article Title"

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
