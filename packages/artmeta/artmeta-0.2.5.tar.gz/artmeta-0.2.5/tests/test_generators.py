"""
Tests pour les générateurs LaTeX
"""

import pytest

from artmeta.generators import AMSGenerator, get_generator
from artmeta.generators.base import BaseGenerator


def test_get_generator_amsart(complete_metadata_dict):
    """Test de récupération du générateur AMS"""
    generator = get_generator("amsart", complete_metadata_dict)

    assert isinstance(generator, AMSGenerator)
    assert generator.DOCUMENT_CLASS == "amsart"


def test_get_generator_invalid(complete_metadata_dict):
    """Test avec une classe invalide"""
    with pytest.raises(ValueError) as exc_info:
        get_generator("invalid_class", complete_metadata_dict)

    assert "inconnue" in str(exc_info.value).lower()


def test_ams_generator_basic(complete_metadata_dict):
    """Test du générateur AMS basique"""
    generator = AMSGenerator(complete_metadata_dict)
    latex = generator.generate()

    # Vérifications basiques
    assert "\\title{My Complete Article}" in latex  # Updated title
    assert "\\author{John Doe}" in latex
    assert "\\author{Jane Smith}" in latex
    assert "\\email{john.doe@example.com}" in latex
    assert "\\begin{abstract}" in latex
    assert "\\keywords{Machine Learning, AI, Deep Learning}" in latex  # Updated keywords
    assert "\\subjclass[2020]{68T05, 68T07}" in latex  # Updated msc_codes
    assert "\\maketitle" in latex


def test_ams_generator_affiliations(complete_metadata_dict):
    """Test des affiliations dans le générateur AMS"""
    generator = AMSGenerator(complete_metadata_dict)
    latex = generator.generate()

    # Vérifier que les affiliations sont présentes
    assert "MIT" in latex  # Updated institution
    assert "USA" in latex  # Updated country
    assert "Research Lab" in latex  # Updated name


def test_all_generators_work(complete_metadata_dict):
    """Test que tous les générateurs peuvent être instanciés"""
    classes = ["amsart", "elsarticle", "svjour3", "siamart", "article"]

    for journal_class in classes:
        generator = get_generator(journal_class, complete_metadata_dict)
        latex = generator.generate()

        # Vérifications minimales
        assert isinstance(latex, str)
        assert len(latex) > 0
        # Le titre devrait apparaître d'une manière ou d'une autre
        assert "My Complete Article" in latex or "title" in latex.lower()  # Updated title


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


def test_format_author_name(complete_metadata_dict):
    """Test du formatage des noms d'auteurs"""
    generator = BaseGenerator(complete_metadata_dict)  # Pass metadata to BaseGenerator

    # Test avec prénom et nom
    author = {"firstname": "John", "lastname": "Doe"}
    assert generator._format_author_name(author) == "John Doe"

    # Test avec champs manquants
    author_no_first = {"lastname": "Smith"}
    assert generator._format_author_name(author_no_first) == " Smith"

    author_no_last = {"firstname": "Jane"}
    assert generator._format_author_name(author_no_last) == "Jane "


def test_get_affiliations_map_empty(complete_metadata_dict):
    """Test du mapping des affiliations avec métadonnées vides"""
    # Test avec métadonnées sans affiliations
    meta_no_affil = {"title": "Test", "authors": []}
    generator = BaseGenerator(meta_no_affil)

    affil_map = generator.get_affiliations_map()
    assert affil_map == {}

    # Test avec métadonnées complètes (using the fixture now)
    generator = BaseGenerator(complete_metadata_dict)

    affil_map = generator.get_affiliations_map()
    assert len(affil_map) == 2
    assert 1 in affil_map
    assert 2 in affil_map
    assert affil_map[1]["name"] == "Research Lab"  # Updated name


def test_hal_generator(complete_metadata_dict):
    """Test the HAL XML generator"""
    generator = get_generator("hal", complete_metadata_dict)
    xml_output = generator.generate_xml()

    assert isinstance(xml_output, str)
    assert '<title xml:lang="en">My Complete Article</title>' in xml_output  # Updated title
    assert "<author>" in xml_output
    assert '<forename type="first">John</forename>' in xml_output
    assert "<surname>Doe</surname>" in xml_output
    assert "jane.smith@example.com" in xml_output  # Updated email
    assert "Research Lab" in xml_output  # Updated affiliation


def test_jinja_autoescape_function(complete_metadata_dict):
    """Test the autoescape function in Jinja2 environment setup"""
    generator = BaseGenerator(complete_metadata_dict)  # Pass metadata to BaseGenerator

    # Access the autoescape function from the Jinja2 environment
    # The autoescape function should return False for None
    autoescape_func = generator.jinja_env.autoescape

    # Test with None (should return False)
    assert autoescape_func(None) is False

    # Test with .xml.j2 template (should return True)
    assert autoescape_func("template.xml.j2") is True

    # Test with non-XML template (should return False)
    assert autoescape_func("template.tex.j2") is False
