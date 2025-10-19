"""
Tests pour les générateurs LaTeX
"""

import pytest

from artmeta.generators import AMSGenerator, get_generator


def get_sample_metadata():
    """Métadonnées de test"""
    return {
        "title": "A Novel Method for Testing",
        "abstract": "This is a test abstract with multiple lines.\n\nSecond paragraph.",
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
        "keywords": ["testing", "validation", "LaTeX"],
        "msc_codes": ["35K15", "65M12"],
    }


def test_get_generator_amsart():
    """Test de récupération du générateur AMS"""
    meta = get_sample_metadata()
    generator = get_generator("amsart", meta)

    assert isinstance(generator, AMSGenerator)
    assert generator.DOCUMENT_CLASS == "amsart"


def test_get_generator_invalid():
    """Test avec une classe invalide"""
    meta = get_sample_metadata()

    with pytest.raises(ValueError) as exc_info:
        get_generator("invalid_class", meta)

    assert "inconnue" in str(exc_info.value).lower()


def test_ams_generator_basic():
    """Test du générateur AMS basique"""
    meta = get_sample_metadata()
    generator = AMSGenerator(meta)
    latex = generator.generate()

    # Vérifications basiques
    assert "\\title{A Novel Method for Testing}" in latex
    assert "\\author{John Doe}" in latex
    assert "\\author{Jane Smith}" in latex
    assert "\\email{john.doe@example.com}" in latex
    assert "\\begin{abstract}" in latex
    assert "\\keywords{testing, validation, LaTeX}" in latex
    assert "\\subjclass[2020]{35K15, 65M12}" in latex
    assert "\\maketitle" in latex


def test_ams_generator_affiliations():
    """Test des affiliations dans le générateur AMS"""
    meta = get_sample_metadata()
    generator = AMSGenerator(meta)
    latex = generator.generate()

    # Vérifier que les affiliations sont présentes
    assert "University of Testing" in latex
    assert "Testville" in latex
    assert "France" in latex


def test_all_generators_work():
    """Test que tous les générateurs peuvent être instanciés"""
    meta = get_sample_metadata()
    classes = ["amsart", "elsarticle", "svjour3", "siamart", "article"]

    for journal_class in classes:
        generator = get_generator(journal_class, meta)
        latex = generator.generate()

        # Vérifications minimales
        assert isinstance(latex, str)
        assert len(latex) > 0
        # Le titre devrait apparaître d'une manière ou d'une autre
        assert "Novel Method" in latex or "title" in latex.lower()


def test_latex_escape_special_chars():
    """Test de l'échappement des caractères spéciaux LaTeX"""
    from artmeta.generators.base import BaseGenerator

    # Tester les caractères spéciaux
    assert BaseGenerator._latex_escape("&") == r"\&"
    assert BaseGenerator._latex_escape("%") == r"\%"
    assert BaseGenerator._latex_escape("$") == r"\$"
    assert BaseGenerator._latex_escape("#") == r"\#"
    assert BaseGenerator._latex_escape("_") == r"\_"
    assert BaseGenerator._latex_escape("{") == r"\{"
    assert BaseGenerator._latex_escape("}") == r"\}"
    assert BaseGenerator._latex_escape("~") == r"\textasciitilde{}"
    assert BaseGenerator._latex_escape("^") == r"\textasciicircum{}"
    assert BaseGenerator._latex_escape("\\") == r"\textbackslash{}"

    # Tester une chaîne avec plusieurs caractères spéciaux
    text = "Income: $50 & up, 10% off #discount"
    escaped = BaseGenerator._latex_escape(text)
    assert escaped == r"Income: \$50 \& up, 10\% off \#discount"


def test_latex_escape_non_string():
    """Test de l'échappement avec des types non-string"""
    from artmeta.generators.base import BaseGenerator

    # Les types non-string doivent être retournés tels quels
    assert BaseGenerator._latex_escape(123) == 123
    assert BaseGenerator._latex_escape(None) is None
    assert BaseGenerator._latex_escape([1, 2, 3]) == [1, 2, 3]


def test_format_author_name():
    """Test du formatage des noms d'auteurs"""
    from artmeta.generators.base import BaseGenerator

    meta = get_sample_metadata()
    generator = BaseGenerator(meta)

    # Test avec prénom et nom
    author = {"firstname": "John", "lastname": "Doe"}
    assert generator._format_author_name(author) == "John Doe"

    # Test avec champs manquants
    author_no_first = {"lastname": "Smith"}
    assert generator._format_author_name(author_no_first) == " Smith"

    author_no_last = {"firstname": "Jane"}
    assert generator._format_author_name(author_no_last) == "Jane "


def test_get_affiliations_map_empty():
    """Test du mapping des affiliations avec métadonnées vides"""
    from artmeta.generators.base import BaseGenerator

    # Test avec métadonnées sans affiliations
    meta_no_affil = {"title": "Test", "authors": []}
    generator = BaseGenerator(meta_no_affil)

    affil_map = generator.get_affiliations_map()
    assert affil_map == {}

    # Test avec métadonnées complètes
    meta = get_sample_metadata()
    generator = BaseGenerator(meta)

    affil_map = generator.get_affiliations_map()
    assert len(affil_map) == 2
    assert 1 in affil_map
    assert 2 in affil_map
    assert affil_map[1]["name"] == "Test Laboratory"


def test_hal_generator():
    """Test the HAL XML generator"""
    meta = get_sample_metadata()
    generator = get_generator("hal", meta)
    xml_output = generator.generate_xml()

    assert isinstance(xml_output, str)
    assert '<title xml:lang="en">A Novel Method for Testing</title>' in xml_output
    assert "<author>" in xml_output
    assert '<forename type="first">John</forename>' in xml_output
    assert "<surname>Doe</surname>" in xml_output
    assert "jane.smith@university.fr" in xml_output
    assert "Test Laboratory" in xml_output


def test_jinja_autoescape_function():
    """Test the autoescape function in Jinja2 environment setup"""
    from artmeta.generators.base import BaseGenerator

    meta = get_sample_metadata()
    generator = BaseGenerator(meta)

    # Access the autoescape function from the Jinja2 environment
    # The autoescape function should return False for None
    autoescape_func = generator.jinja_env.autoescape

    # Test with None (should return False)
    assert autoescape_func(None) is False

    # Test with .xml.j2 template (should return True)
    assert autoescape_func("template.xml.j2") is True

    # Test with non-XML template (should return False)
    assert autoescape_func("template.tex.j2") is False
