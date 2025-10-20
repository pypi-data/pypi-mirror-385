"""
Tests pour le module de validation
"""

from artmeta.validators import validate_email, validate_metadata, validate_orcid


def test_validate_email():
    """Test de validation des emails"""
    # Emails valides
    assert validate_email("user@example.com") is True
    assert validate_email("first.last@university.fr") is True
    assert validate_email("user+tag@domain.co.uk") is True

    # Emails invalides
    assert validate_email("invalid") is False
    assert validate_email("@example.com") is False
    assert validate_email("user@") is False
    assert validate_email("") is False


def test_validate_orcid():
    """Test de validation des ORCID"""
    # ORCID valides
    assert validate_orcid("0000-0002-1825-0097") is True
    assert validate_orcid("0000-0001-5000-0007") is True
    assert validate_orcid("0000-0002-1694-233X") is True

    # ORCID invalides
    assert validate_orcid("0000-0002-1825-009") is False  # Trop court
    assert validate_orcid("0000-0002-1825-00971") is False  # Trop long
    assert validate_orcid("1234-5678-9012-ABCD") is False  # Format incorrect
    assert validate_orcid("") is False


def test_validate_metadata_missing_required():
    """Test avec des champs obligatoires manquants"""
    meta = {}
    errors, warnings = validate_metadata(meta)

    assert len(errors) == 3  # title, authors, abstract manquants
    assert any("title" in err.lower() for err in errors)
    assert any("authors" in err.lower() for err in errors)
    assert any("abstract" in err.lower() for err in errors)


def test_validate_metadata_valid():
    """Test avec des métadonnées valides"""
    meta = {
        "title": "Test Article",
        "abstract": "This is a test abstract.",
        "authors": [
            {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john.doe@example.com",
                "orcid": "0000-0002-1825-0097",
                "affiliations": [1],
            }
        ],
        "affiliations": [
            {"id": 1, "name": "Test Lab", "institution": "Test University", "country": "France"}
        ],
    }

    errors, warnings = validate_metadata(meta)

    assert len(errors) == 0
    assert len(warnings) == 0


def test_validate_metadata_invalid_orcid():
    """Test avec un ORCID invalide"""
    meta = {
        "title": "Test Article",
        "abstract": "This is a test abstract.",
        "authors": [
            {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john.doe@example.com",
                "orcid": "1234-5678",  # ORCID invalide
            }
        ],
    }

    errors, warnings = validate_metadata(meta)

    assert len(errors) >= 1
    assert any("ORCID" in err for err in errors)


def test_validate_metadata_msc_codes():
    """Test de validation des codes MSC"""
    # Codes MSC valides
    meta = {
        "title": "Test",
        "abstract": "Test",
        "authors": [{"firstname": "A", "lastname": "B", "email": "a.b@test.com"}],
        "msc_codes": ["35K15", "65M12"],
    }

    errors, warnings = validate_metadata(meta)
    assert len(warnings) == 0

    # Codes MSC invalides
    meta["msc_codes"] = ["35K1", "invalid"]
    errors, warnings = validate_metadata(meta)
    assert len(warnings) >= 2


def test_validate_author_missing_fields():
    """Test avec un champ manquant pour un auteur"""
    meta = {
        "title": "Test",
        "abstract": "Test",
        "authors": [{"lastname": "Doe", "email": "j.d@test.com"}],
    }
    errors, _ = validate_metadata(meta)
    assert any("firstname' manquant" in err for err in errors)


def test_validate_author_invalid_email_warning():
    """Test d'un avertissement pour un email d'auteur invalide"""
    meta = {
        "title": "Test",
        "abstract": "Test",
        "authors": [{"firstname": "John", "lastname": "Doe", "email": "invalid-email"}],
    }
    _, warnings = validate_metadata(meta)
    assert any("format email suspect" in warn for warn in warnings)


def test_validate_author_missing_meta_affiliations():
    """Test une erreur quand un auteur a des affiliations mais pas la clé affiliations"""
    meta = {
        "title": "Test",
        "abstract": "Test",
        "authors": [
            {"firstname": "John", "lastname": "Doe", "email": "j.d@test.com", "affiliations": [1]}
        ],
    }
    errors, _ = validate_metadata(meta)
    assert any("référence des affiliations mais aucune n'est définie" in err for err in errors)


def test_validate_author_invalid_affiliation_id():
    """Test une erreur quand l'ID d'affiliation d'un auteur n'existe pas"""
    meta = {
        "title": "Test",
        "abstract": "Test",
        "authors": [
            {"firstname": "John", "lastname": "Doe", "email": "j.d@test.com", "affiliations": [2]}
        ],
        "affiliations": [{"id": 1, "name": "Lab"}],
    }
    errors, _ = validate_metadata(meta)
    assert any("affiliation 2 introuvable" in err for err in errors)


def test_validate_affiliation_missing_id():
    """Test une erreur quand une affiliation n'a pas d'ID"""
    meta = {"title": "Test", "abstract": "Test", "authors": [], "affiliations": [{"name": "Lab"}]}
    errors, _ = validate_metadata(meta)
    assert any("champ 'id' manquant" in err for err in errors)


def test_validate_affiliation_duplicate_id():
    """Test une erreur quand deux affiliations ont le même ID"""
    meta = {
        "title": "Test",
        "abstract": "Test",
        "authors": [],
        "affiliations": [{"id": 1, "name": "Lab1"}, {"id": 1, "name": "Lab2"}],
    }
    errors, _ = validate_metadata(meta)
    assert any("ID 1 dupliqué" in err for err in errors)


def test_validate_affiliation_missing_recommended_fields():
    """Test un avertissement quand il manque des champs recommandés à une affiliation"""
    meta = {
        "title": "Test",
        "abstract": "Test",
        "authors": [],
        "affiliations": [{"id": 1, "name": "Lab"}],
    }
    _, warnings = validate_metadata(meta)
    assert len(warnings) > 0
    assert any("champ 'institution' recommandé" in warn for warn in warnings)


def test_validate_author_no_email_with_orcid():
    """Test validation of author without email but with ORCID (covers branch 65->70)"""
    meta = {
        "title": "Test",
        "abstract": "Test",
        "authors": [
            {
                "firstname": "John",
                "lastname": "Doe",
                "orcid": "0000-0002-1825-0097",
                "affiliations": [1],
            }
        ],
        "affiliations": [{"id": 1, "name": "Lab"}],
    }
    errors, _ = validate_metadata(meta)
    # Should have error for missing email (required field)
    # But ORCID validation should still run and pass (this tests branch 65->70)
    assert any("email" in err for err in errors)
    # Should not have ORCID error since it's valid
    assert not any("ORCID" in err for err in errors)


def test_validate_author_no_email_with_invalid_orcid():
    """Test validation of author without email but with invalid ORCID"""
    meta = {
        "title": "Test",
        "abstract": "Test",
        "authors": [
            {
                "firstname": "John",
                "lastname": "Doe",
                "orcid": "invalid-orcid",
                "affiliations": [1],
            }
        ],
        "affiliations": [{"id": 1, "name": "Lab"}],
    }
    errors, _ = validate_metadata(meta)
    # Should have errors for both missing email and invalid ORCID
    assert any("email" in err for err in errors)
    assert any("ORCID invalide" in err for err in errors)
