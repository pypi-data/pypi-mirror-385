"""
Tests pour le module utils (fonctions utilitaires)
"""

import pytest

from artmeta.utils import (
    detect_class_from_tex,
    generate_yaml_template,
    get_stats,
    insert_in_tex,
)


def test_insert_in_tex_new_block(tmp_path):
    """Test d'insertion d'un nouveau bloc dans un fichier .tex"""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        "\\documentclass{article}\n\\begin{document}\nContent here\n\\end{document}",
        encoding="utf-8",
    )

    latex_code = "\\title{Test}\n\\author{John Doe}"
    insert_in_tex(str(tex_file), latex_code, "amsart")

    content = tex_file.read_text(encoding="utf-8")

    # Vérifier que les balises ont été insérées
    assert "% BEGIN AUTO-GENERATED [amsart]" in content
    assert "% END AUTO-GENERATED [amsart]" in content
    assert "\\title{Test}" in content
    assert "\\author{John Doe}" in content


def test_insert_in_tex_update_existing_block(tmp_path):
    """Test de mise à jour d'un bloc existant"""
    tex_file = tmp_path / "test.tex"
    initial_content = """\\documentclass{article}
\\begin{document}

% BEGIN AUTO-GENERATED [amsart]
\\title{Old Title}
% END AUTO-GENERATED [amsart]

Content here
\\end{document}"""
    tex_file.write_text(initial_content, encoding="utf-8")

    new_latex_code = "\\title{New Title}\n\\author{Jane Smith}"
    insert_in_tex(str(tex_file), new_latex_code, "amsart")

    content = tex_file.read_text(encoding="utf-8")

    # Vérifier que le bloc a été mis à jour
    assert "New Title" in content
    assert "Old Title" not in content
    assert "Jane Smith" in content
    # Vérifier qu'il n'y a qu'un seul bloc
    assert content.count("% BEGIN AUTO-GENERATED [amsart]") == 1


def test_insert_in_tex_without_begin_document(tmp_path):
    """Test d'insertion dans un fichier sans \\begin{document}"""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("\\documentclass{article}\n% Preamble only", encoding="utf-8")

    latex_code = "\\title{Test Title}"
    insert_in_tex(str(tex_file), latex_code, "elsarticle")

    content = tex_file.read_text(encoding="utf-8")

    # Le bloc devrait être inséré au début
    assert content.startswith("% BEGIN AUTO-GENERATED [elsarticle]")
    assert "\\title{Test Title}" in content


def test_insert_in_tex_file_not_found():
    """Test avec un fichier inexistant"""
    with pytest.raises(FileNotFoundError) as exc_info:
        insert_in_tex("nonexistent.tex", "\\title{Test}", "amsart")

    assert "nonexistent.tex" in str(exc_info.value)


def test_insert_in_tex_different_classes(tmp_path):
    """Test d'insertion de blocs pour différentes classes"""
    tex_file = tmp_path / "multi.tex"
    tex_file.write_text(
        "\\documentclass{article}\n\\begin{document}\n\\end{document}", encoding="utf-8"
    )

    # Insérer pour amsart
    insert_in_tex(str(tex_file), "\\title{AMS Title}", "amsart")
    # Insérer pour elsarticle
    insert_in_tex(str(tex_file), "\\title{Elsevier Title}", "elsarticle")

    content = tex_file.read_text(encoding="utf-8")

    # Les deux blocs doivent coexister
    assert "% BEGIN AUTO-GENERATED [amsart]" in content
    assert "% BEGIN AUTO-GENERATED [elsarticle]" in content
    assert "AMS Title" in content
    assert "Elsevier Title" in content


def test_generate_yaml_template():
    """Test de génération du template YAML"""
    template = generate_yaml_template()

    # Vérifier la présence des sections principales
    assert "title:" in template
    assert "authors:" in template
    assert "affiliations:" in template
    assert "abstract:" in template
    assert "keywords:" in template
    assert "msc_codes:" in template
    assert "funding:" in template
    assert "hal:" in template

    # Vérifier la présence d'exemples
    assert "Prénom" in template
    assert "Nom" in template
    assert "0000-0000-0000-0000" in template
    assert "prenom.nom@institution.fr" in template

    # Vérifier que la date est présente
    assert "Généré le" in template


def test_get_stats_complete_metadata(stats_metadata_dict):
    """Test des statistiques avec métadonnées complètes"""
    stats = get_stats(stats_metadata_dict)

    assert stats["abstract_words"] == 11
    assert stats["abstract_chars"] == 64
    assert stats["authors_count"] == 2
    assert stats["authors_with_orcid"] == 1
    assert stats["affiliations_count"] == 2
    assert stats["countries"] == ["France", "USA"]
    assert stats["keywords_count"] == 2
    assert stats["msc_codes_count"] == 2


def test_get_stats_minimal_metadata():
    """Test des statistiques avec métadonnées minimales"""
    meta = {
        "title": "Test",
        "abstract": "Short abstract.",
    }

    stats = get_stats(meta)

    assert stats["abstract_words"] == 2
    assert stats["abstract_chars"] == 15
    assert "authors_count" not in stats
    assert "affiliations_count" not in stats


def test_get_stats_empty_metadata():
    """Test des statistiques avec métadonnées vides"""
    meta = {}
    stats = get_stats(meta)

    assert stats == {}


def test_get_stats_countries_deduplication():
    """Test que les pays sont dédupliqués et triés"""
    meta = {
        "affiliations": [
            {"id": 1, "country": "France"},
            {"id": 2, "country": "USA"},
            {"id": 3, "country": "France"},
            {"id": 4, "country": "Germany"},
        ]
    }

    stats = get_stats(meta)

    assert stats["countries"] == ["France", "Germany", "USA"]
    assert len(stats["countries"]) == 3


def test_detect_class_from_tex(
    amsart_tex_file,
    elsarticle_tex_file,
    no_class_tex_file,
    commented_class_tex_file,
):
    """Tests the detect_class_from_tex function."""
    # Test with a standard class
    assert detect_class_from_tex(amsart_tex_file) == "amsart"

    # Test with a class with options
    assert detect_class_from_tex(elsarticle_tex_file) == "elsarticle"

    # Test with no documentclass
    assert detect_class_from_tex(no_class_tex_file) is None

    # Test with commented documentclass
    assert detect_class_from_tex(commented_class_tex_file) is None

    # Test with a non-existent file
    with pytest.raises(FileNotFoundError):
        detect_class_from_tex("non_existent_file.tex")


def test_insert_in_tex_no_documentclass(tmp_path):
    """Test insert_in_tex with a .tex file without documentclass"""
    tex_file = tmp_path / "no_class.tex"
    tex_file.write_text(
        "\\begin{document}\nSome content\n\\end{document}",
        encoding="utf-8",
    )

    # Should work even without documentclass (just inserts the block)
    latex_code = "\\title{Test}"
    insert_in_tex(str(tex_file), latex_code, "article")

    content = tex_file.read_text(encoding="utf-8")
    assert "% BEGIN AUTO-GENERATED [article]" in content
    assert "\\title{Test}" in content
