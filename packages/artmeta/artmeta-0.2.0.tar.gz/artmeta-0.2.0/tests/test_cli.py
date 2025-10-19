"""
Tests for the command-line interface
"""

import sys
from io import StringIO
from unittest.mock import patch

from artmeta import cli


def run_cli(*args):
    """Helper to run the CLI with arguments and capture output"""
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = captured_stdout = StringIO()
    sys.stderr = captured_stderr = StringIO()

    original_argv = sys.argv
    sys.argv = ["artmeta", *args]

    try:
        return_code = cli.main()
    except SystemExit as e:
        return_code = e.code

    sys.stdout = original_stdout
    sys.stderr = original_stderr
    sys.argv = original_argv

    return return_code, captured_stdout.getvalue(), captured_stderr.getvalue()


def test_init_command(tmp_path):
    """Test the 'init' command"""
    output_file = tmp_path / "art.yml"

    return_code, stdout, stderr = run_cli("init", "-o", str(output_file))

    assert return_code == 0
    assert "Template créé" in stdout
    assert output_file.exists()


def test_init_command_force(tmp_path):
    """Test the 'init' command with --force"""
    output_file = tmp_path / "art.yml"
    output_file.write_text("existing content")

    return_code, stdout, stderr = run_cli("init", "-o", str(output_file), "--force")

    assert return_code == 0
    assert "Template créé" in stdout
    assert "existing content" not in output_file.read_text()


def test_init_command_already_exists(tmp_path):
    """Test the 'init' command when the file already exists"""
    output_file = tmp_path / "art.yml"
    output_file.write_text("existing content")

    return_code, stdout, stderr = run_cli("init", "-o", str(output_file))

    assert return_code == 1
    assert "existe déjà" in stdout
    assert "existing content" in output_file.read_text()


def test_validate_command_success(valid_metadata_file):
    """Test the 'validate' command with a valid file"""
    return_code, stdout, stderr = run_cli("validate", "-m", str(valid_metadata_file))

    assert return_code == 0
    assert "est valide" in stdout


def test_validate_command_errors(invalid_metadata_file):
    """Test the 'validate' command with an invalid file"""
    return_code, stdout, stderr = run_cli("validate", "-m", str(invalid_metadata_file))

    assert return_code == 1
    assert "ERREURS détectées" in stdout


def test_validate_command_warnings(tmp_path):
    """Test the 'validate' command with warnings"""
    meta_file = tmp_path / "art.yml"
    meta_file.write_text(
        """
        title: \"My Title\"
        abstract: \"My Abstract\"
        authors:
          - firstname: \"John\"
            lastname: \"Doe\"
            email: \"john.doe@example.com\"
        affiliations:
          - id: 1
            name: \"Test Lab\"
        """
    )

    return_code, stdout, stderr = run_cli("validate", "-m", str(meta_file))

    assert return_code == 0
    assert "AVERTISSEMENTS" in stdout


def test_validate_command_file_not_found():
    """Test the 'validate' command with a nonexistent file"""
    return_code, stdout, stderr = run_cli("validate", "-m", "nonexistent.yml")

    assert return_code == 1
    assert "introuvable" in stdout


def test_validate_command_yaml_error(invalid_yaml_file):
    """Test the 'validate' command with invalid YAML"""
    return_code, stdout, stderr = run_cli("validate", "-m", str(invalid_yaml_file))

    assert return_code == 1
    assert "Erreur YAML" in stdout


@patch("artmeta.cli.ArtMeta.validate", side_effect=Exception("Unexpected error"))
def test_validate_command_unexpected_error(mock_validate, invalid_metadata_file):
    """Test the 'validate' command with an unexpected error"""
    return_code, stdout, stderr = run_cli("validate", "-m", str(invalid_metadata_file))

    assert return_code == 1
    assert "Une erreur inattendue est survenue" in stdout


def test_generate_command(valid_metadata_file):
    """Test the 'generate' command"""
    return_code, stdout, stderr = run_cli("generate", "article", "-m", str(valid_metadata_file))

    assert return_code == 0
    assert "\\title{My Title}" in stdout


def test_generate_command_output_file(valid_metadata_file, tmp_path):
    """Test the 'generate' command with an output file"""
    output_file = tmp_path / "output.tex"

    return_code, stdout, stderr = run_cli(
        "generate", "article", "-m", str(valid_metadata_file), "-o", str(output_file)
    )

    assert return_code == 0
    assert "Code LaTeX écrit" in stdout
    assert output_file.exists()
    assert "\\title{My Title}" in output_file.read_text()


def test_generate_command_invalid_metadata(invalid_metadata_file):
    """Test the 'generate' command with invalid metadata"""
    return_code, stdout, stderr = run_cli("generate", "article", "-m", str(invalid_metadata_file))

    assert return_code == 1
    assert "Métadonnées invalides" in stdout


def test_generate_command_file_not_found():
    """Test the 'generate' command with a nonexistent file"""
    return_code, stdout, stderr = run_cli("generate", "article", "-m", "nonexistent.yml")

    assert return_code == 1
    assert "introuvable" in stdout


def test_generate_command_yaml_error(invalid_yaml_file):
    """Test the 'generate' command with invalid YAML"""
    return_code, stdout, stderr = run_cli("generate", "article", "-m", str(invalid_yaml_file))

    assert return_code == 1
    assert "Erreur YAML" in stdout


def test_generate_command_invalid_journal(valid_metadata_file):
    """Test the 'generate' command with an invalid journal"""
    return_code, stdout, stderr = run_cli(
        "generate", "invalid-journal", "-m", str(valid_metadata_file)
    )

    assert return_code == 2
    assert "invalid choice" in stderr


def test_generate_command_os_error(valid_metadata_file, tmp_path):
    """Test the 'generate' command with an OSError"""
    output_file = tmp_path / "output.tex"

    with patch("pathlib.Path.write_text", side_effect=OSError("Permission denied")):
        return_code, stdout, stderr = run_cli(
            "generate", "article", "-m", str(valid_metadata_file), "-o", str(output_file)
        )

    assert return_code == 1
    assert "Erreur d'écriture" in stdout


@patch("artmeta.cli.get_generator", side_effect=Exception("Unexpected error"))
def test_generate_command_unexpected_error(mock_get_generator, valid_metadata_file):
    """Test the 'generate' command with an unexpected error"""
    return_code, stdout, stderr = run_cli("generate", "article", "-m", str(valid_metadata_file))

    assert return_code == 1
    assert "Une erreur inattendue est survenue" in stdout


def test_info_command(valid_metadata_file):
    """Test the 'info' command"""
    return_code, stdout, stderr = run_cli("info", "-m", str(valid_metadata_file))

    assert return_code == 0
    assert "MÉTADONNÉES" in stdout
    assert "My Title" in stdout
    assert "John Doe" in stdout


def test_hal_xml_command(valid_metadata_file, tmp_path):
    """Test the 'hal-xml' command"""
    output_file = tmp_path / "hal.xml"

    return_code, stdout, stderr = run_cli(
        "hal-xml", "-m", str(valid_metadata_file), "-o", str(output_file)
    )

    assert return_code == 0
    assert "HAL-XML généré" in stdout
    assert output_file.exists()
    xml_content = output_file.read_text()
    assert '<title xml:lang="en">My Title</title>' in xml_content


def test_switch_command(valid_metadata_file, sample_tex_file):
    """Test the 'switch' command"""
    return_code, stdout, stderr = run_cli(
        "switch", "amsart", str(sample_tex_file), "-m", str(valid_metadata_file)
    )

    assert return_code == 0
    assert "Classe changée" in stdout
    assert "\\documentclass{amsart}" in sample_tex_file.read_text()


def test_stats_command(valid_metadata_file):
    """Test the 'stats' command"""
    return_code, stdout, stderr = run_cli("stats", "-m", str(valid_metadata_file))

    assert return_code == 0
    assert "STATISTIQUES" in stdout
    assert "Auteurs : 1" in stdout


def test_main_no_command():
    """Test running main with no command"""
    return_code, stdout, stderr = run_cli()
    assert return_code == 1
    assert "usage: artmeta" in stdout


def test_info_command_complete_metadata(complete_metadata_file):
    """Test the 'info' command with complete metadata (affiliations, keywords, msc, funding)"""
    return_code, stdout, stderr = run_cli("info", "-m", str(complete_metadata_file))

    assert return_code == 0
    assert "MÉTADONNÉES" in stdout
    assert "My Complete Article" in stdout
    assert "John Doe" in stdout
    assert "[✉ correspondant]" in stdout
    assert "Jane Smith" in stdout
    assert "AFFILIATIONS" in stdout
    assert "Research Lab" in stdout
    assert "AI Lab" in stdout
    assert "MOTS-CLÉS" in stdout
    assert "Machine Learning" in stdout
    assert "CODES MSC" in stdout
    assert "68T05" in stdout
    assert "FINANCEMENT" in stdout
    assert "NSF grant" in stdout


def test_info_command_empty_file(empty_metadata_file):
    """Test the 'info' command with an empty file"""
    return_code, stdout, stderr = run_cli("info", "-m", str(empty_metadata_file))

    assert return_code == 1
    assert "est vide" in stdout


def test_info_command_file_not_found():
    """Test the 'info' command with a nonexistent file"""
    return_code, stdout, stderr = run_cli("info", "-m", "nonexistent.yml")

    assert return_code == 1
    assert "introuvable" in stdout


def test_info_command_yaml_error(invalid_yaml_file):
    """Test the 'info' command with invalid YAML"""
    return_code, stdout, stderr = run_cli("info", "-m", str(invalid_yaml_file))

    assert return_code == 1
    assert "Erreur YAML" in stdout


@patch("artmeta.cli.ArtMeta", side_effect=Exception("Unexpected error"))
def test_info_command_unexpected_error(mock_artmeta, invalid_metadata_file):
    """Test the 'info' command with an unexpected error"""
    return_code, stdout, stderr = run_cli("info", "-m", str(invalid_metadata_file))

    assert return_code == 1
    assert "Une erreur inattendue est survenue" in stdout


def test_hal_xml_command_validation_errors(invalid_metadata_file, tmp_path):
    """Test the 'hal-xml' command with validation errors"""
    output_file = tmp_path / "hal.xml"

    return_code, stdout, stderr = run_cli(
        "hal-xml", "-m", str(invalid_metadata_file), "-o", str(output_file)
    )

    assert return_code == 1
    assert "Métadonnées invalides" in stdout


def test_hal_xml_command_file_not_found():
    """Test the 'hal-xml' command with a nonexistent file"""
    return_code, stdout, stderr = run_cli("hal-xml", "-m", "nonexistent.yml")

    assert return_code == 1
    assert "introuvable" in stdout


def test_hal_xml_command_yaml_error(invalid_yaml_file):
    """Test the 'hal-xml' command with invalid YAML"""
    return_code, stdout, stderr = run_cli("hal-xml", "-m", str(invalid_yaml_file))

    assert return_code == 1
    assert "Erreur YAML" in stdout


def test_hal_xml_command_os_error(valid_metadata_file, tmp_path):
    """Test the 'hal-xml' command with an OSError"""
    output_file = tmp_path / "hal.xml"

    with patch("pathlib.Path.write_text", side_effect=OSError("Permission denied")):
        return_code, stdout, stderr = run_cli(
            "hal-xml", "-m", str(valid_metadata_file), "-o", str(output_file)
        )

    assert return_code == 1
    assert "Erreur d'écriture" in stdout


@patch("artmeta.cli.HALGenerator", side_effect=Exception("Unexpected error"))
def test_hal_xml_command_unexpected_error(mock_hal_generator, valid_metadata_file, tmp_path):
    """Test the 'hal-xml' command with an unexpected error"""
    output_file = tmp_path / "hal.xml"

    return_code, stdout, stderr = run_cli(
        "hal-xml", "-m", str(valid_metadata_file), "-o", str(output_file)
    )

    assert return_code == 1
    assert "Une erreur inattendue est survenue" in stdout


def test_switch_command_empty_file(empty_metadata_file, sample_tex_file):
    """Test the 'switch' command with an empty metadata file"""
    return_code, stdout, stderr = run_cli(
        "switch", "amsart", str(sample_tex_file), "-m", str(empty_metadata_file)
    )

    assert return_code == 1
    assert "est vide" in stdout


def test_switch_command_file_not_found():
    """Test the 'switch' command with a nonexistent metadata file"""
    return_code, stdout, stderr = run_cli("switch", "amsart", "main.tex", "-m", "nonexistent.yml")

    assert return_code == 1
    assert "introuvable" in stdout


def test_switch_command_tex_file_not_found(valid_metadata_file):
    """Test the 'switch' command with a nonexistent tex file"""
    return_code, stdout, stderr = run_cli(
        "switch", "amsart", "nonexistent.tex", "-m", str(valid_metadata_file)
    )

    assert return_code == 1
    assert "introuvable" in stdout


def test_switch_command_yaml_error(invalid_yaml_file):
    """Test the 'switch' command with invalid YAML"""
    return_code, stdout, stderr = run_cli(
        "switch", "amsart", "main.tex", "-m", str(invalid_yaml_file)
    )

    assert return_code == 1
    assert "Erreur YAML" in stdout


def test_switch_command_value_error(valid_metadata_file, sample_tex_file):
    """Test the 'switch' command with an error from get_generator"""
    with patch("artmeta.cli.get_generator", side_effect=ValueError("Invalid generator")):
        return_code, stdout, stderr = run_cli(
            "switch", "amsart", str(sample_tex_file), "-m", str(valid_metadata_file)
        )

    assert return_code == 1
    assert "Erreur de changement" in stdout


def test_switch_command_os_error(valid_metadata_file, sample_tex_file):
    """Test the 'switch' command with an OSError"""
    with patch("artmeta.cli.insert_in_tex", side_effect=OSError("Permission denied")):
        return_code, stdout, stderr = run_cli(
            "switch", "amsart", str(sample_tex_file), "-m", str(valid_metadata_file)
        )

    assert return_code == 1
    assert "Erreur d'écriture" in stdout


@patch("artmeta.cli.get_generator", side_effect=Exception("Unexpected error"))
def test_switch_command_unexpected_error(mock_get_generator, valid_metadata_file, sample_tex_file):
    """Test the 'switch' command with an unexpected error"""
    return_code, stdout, stderr = run_cli(
        "switch", "amsart", str(sample_tex_file), "-m", str(valid_metadata_file)
    )

    assert return_code == 1
    assert "Une erreur inattendue est survenue" in stdout


def test_stats_command_complete_metadata(stats_metadata_file):
    """Test the 'stats' command with complete metadata"""
    return_code, stdout, stderr = run_cli("stats", "-m", str(stats_metadata_file))

    assert return_code == 0
    assert "STATISTIQUES" in stdout
    assert "Résumé" in stdout
    assert "mots" in stdout
    assert "Auteurs : 2" in stdout
    assert "1 avec ORCID" in stdout
    assert "Affiliations : 2" in stdout
    assert "Pays : " in stdout
    assert "Mots-clés : 2" in stdout
    assert "Codes MSC : 2" in stdout


def test_stats_command_empty_file(empty_metadata_file):
    """Test the 'stats' command with an empty file"""
    return_code, stdout, stderr = run_cli("stats", "-m", str(empty_metadata_file))

    assert return_code == 1
    assert "est vide" in stdout


def test_stats_command_file_not_found():
    """Test the 'stats' command with a nonexistent file"""
    return_code, stdout, stderr = run_cli("stats", "-m", "nonexistent.yml")

    assert return_code == 1
    assert "introuvable" in stdout


def test_stats_command_yaml_error(invalid_yaml_file):
    """Test the 'stats' command with invalid YAML"""
    return_code, stdout, stderr = run_cli("stats", "-m", str(invalid_yaml_file))

    assert return_code == 1
    assert "Erreur YAML" in stdout


@patch("artmeta.cli.get_stats", side_effect=Exception("Unexpected error"))
def test_stats_command_unexpected_error(mock_get_stats, invalid_metadata_file):
    """Test the 'stats' command with an unexpected error"""
    return_code, stdout, stderr = run_cli("stats", "-m", str(invalid_metadata_file))

    assert return_code == 1
    assert "Une erreur inattendue est survenue" in stdout


def test_generate_command_with_insert(valid_metadata_file, sample_tex_file):
    """Test the 'generate' command with --insert flag"""
    return_code, stdout, stderr = run_cli(
        "generate", "article", "-m", str(valid_metadata_file), "--insert", str(sample_tex_file)
    )

    assert return_code == 0
    content = sample_tex_file.read_text()
    assert "\\title{My Title}" in content


def test_generate_command_value_error(valid_metadata_file):
    """Test the 'generate' command with ValueError from get_generator"""
    with patch("artmeta.cli.get_generator", side_effect=ValueError("Invalid journal class")):
        return_code, stdout, stderr = run_cli("generate", "article", "-m", str(valid_metadata_file))

    assert return_code == 1
    assert "Erreur de génération" in stdout
