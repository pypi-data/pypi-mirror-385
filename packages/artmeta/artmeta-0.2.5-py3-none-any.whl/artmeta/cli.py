"""
Interface en ligne de commande pour artmeta
"""

import argparse
from pathlib import Path

import yaml

from .core import ArtMeta
from .generators import HALGenerator, get_generator
from .utils import detect_class_from_tex, generate_yaml_template, get_stats, insert_in_tex

__version__ = "0.1.0"


def cmd_init(args):
    """Génère un template art.yml"""
    output = Path(args.output)

    if output.exists() and not args.force:
        print(f"✗ Le fichier {output} existe déjà. Utilisez --force pour écraser.")
        return 1

    template = generate_yaml_template()
    output.write_text(template, encoding="utf-8")

    print(f"✓ Template créé : {output}")
    print(f"\nÉditez {output} puis utilisez :")
    print("  artmeta validate        # Valider la structure")
    print("  artmeta generate -j amsart --insert main.tex")
    return 0


def cmd_validate(args):
    """Valide le fichier de métadonnées"""
    try:
        artmeta = ArtMeta(args.metadata)
        errors, warnings = artmeta.validate()

        if errors:
            print("✗ ERREURS détectées :")
            for error in errors:
                print(f"  • {error}")

        if warnings:
            print("\n⚠ AVERTISSEMENTS :")
            for warning in warnings:
                print(f"  • {warning}")

        if not errors and not warnings:
            print(f"✓ {args.metadata} est valide !")
            return 0
        elif errors:
            print(f"\n✗ Validation échouée avec {len(errors)} erreur(s)")
            return 1
        else:
            print(f"\n⚠ Validation OK avec {len(warnings)} avertissement(s)")
            return 0

    except FileNotFoundError:
        print(f"✗ Erreur : Le fichier de métadonnées '{args.metadata}' est introuvable.")
        print("  Astuce : Vous pouvez en créer un avec la commande 'artmeta init'.")
        return 1

    except yaml.YAMLError as e:
        print(f"✗ Erreur YAML dans '{args.metadata}': format invalide.")
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            print(f"  Le problème se trouve à la ligne {mark.line + 1}, colonne {mark.column + 1}.")
        return 1

    except Exception as e:
        print(f"✗ Une erreur inattendue est survenue : {e}")
        return 1


def cmd_generate(args):
    """Génère le code LaTeX"""
    try:
        artmeta = ArtMeta(args.metadata)

        # Validation rapide
        errors, _ = artmeta.validate()
        if errors:
            print("✗ Métadonnées invalides. Lancez 'artmeta validate' pour plus de détails.")
            return 1

        journal_class = args.journal
        if args.autodetect_from:
            try:
                detected_class = detect_class_from_tex(args.autodetect_from)
                if not detected_class:
                    print(f"✗ Impossible de détecter la classe dans '{args.autodetect_from}'.")
                    return 1

                # Check if detected class is supported
                supported_classes = ["amsart", "elsarticle", "svjour3", "siamart", "article"]
                if detected_class not in supported_classes:
                    print(f"✗ Classe '{detected_class}' détectée mais non supportée.")
                    print(f"  Classes supportées : {', '.join(supported_classes)}")
                    return 1

                journal_class = detected_class
                print(f"✓ Classe '{journal_class}' détectée depuis '{args.autodetect_from}'.")
            except FileNotFoundError:
                print(f"✗ Erreur : Le fichier TeX '{args.autodetect_from}' est introuvable.")
                return 1

        generator = get_generator(journal_class, artmeta.meta)
        latex_code = generator.generate()

        if args.insert:
            insert_in_tex(args.insert, latex_code, journal_class)
        elif args.output:
            Path(args.output).write_text(latex_code, encoding="utf-8")
            print(f"✓ Code LaTeX écrit dans {args.output}")
        else:
            print(latex_code)

        return 0

    except FileNotFoundError:
        print(f"✗ Erreur : Le fichier de métadonnées '{args.metadata}' est introuvable.")
        print("  Astuce : Vous pouvez en créer un avec la commande 'artmeta init'.")
        return 1

    except yaml.YAMLError as e:
        print(f"✗ Erreur YAML dans '{args.metadata}': format invalide.")
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            print(f"  Le problème se trouve à la ligne {mark.line + 1}, colonne {mark.column + 1}.")
        return 1

    except ValueError as e:
        # Erreur venant de get_generator si la classe de journal est invalide
        print(f"✗ Erreur de génération : {e}")
        return 1

    except (OSError, PermissionError) as e:
        output_file = args.output or args.insert
        print(f"✗ Erreur d'écriture : Impossible d'écrire dans le fichier '{output_file}'.")
        print(f"  Détail : {e}")
        return 1

    except Exception as e:
        print(f"✗ Une erreur inattendue est survenue : {e}")
        return 1


def cmd_info(args):
    """Affiche un résumé des métadonnées"""
    try:
        artmeta = ArtMeta(args.metadata)

        if artmeta.meta is None:
            if not Path(args.metadata).exists():
                print(f"✗ Erreur : Le fichier de métadonnées '{args.metadata}' est introuvable.")
                print("  Astuce : Vous pouvez en créer un avec la commande 'artmeta init'.")
            else:
                print(f"✗ Erreur : Le fichier de métadonnées '{args.metadata}' est vide.")
            return 1

        meta = artmeta.meta

        print("=" * 70)
        print(f"MÉTADONNÉES : {args.metadata}")
        print("=" * 70)

        print("\n📄 TITRE")
        print(f"  {meta.get('title', 'Non défini')}")

        if "authors" in meta:
            print(f"\n👥 AUTEURS ({len(meta['authors'])})")
            for i, author in enumerate(meta["authors"], 1):
                name = f"{author.get('firstname', '?')} {author.get('lastname', '?')}"
                email = author.get("email", "pas d'email")
                orcid = author.get("orcid", "pas d'ORCID")
                corr = " [✉ correspondant]" if author.get("corresponding") else ""
                print(f"  {i}. {name}{corr}")
                print(f"     {email} | ORCID: {orcid}")

        if "affiliations" in meta:
            print(f"\n🏛 AFFILIATIONS ({len(meta['affiliations'])})")
            for affil in meta["affiliations"]:
                print(f"  [{affil['id']}] {affil.get('name', '?')}")
                print(f"      {affil.get('institution', '?')}, {affil.get('country', '?')}")

        if "abstract" in meta:
            abstract = meta["abstract"][:150].replace("\n", " ")
            print("\n📝 RÉSUMÉ")
            print(f"  {abstract}...")

        if "keywords" in meta:
            print(f"\n🏷 MOTS-CLÉS ({len(meta['keywords'])})")
            print(f"  {', '.join(meta['keywords'])}")

        if "msc_codes" in meta:
            print("\n🔢 CODES MSC")
            print(f"  {', '.join(meta['msc_codes'])}")

        if "funding" in meta:
            print("\n💰 FINANCEMENT")
            print(f"  {meta['funding']}")

        print("\n" + "=" * 70)

        return 0

    except yaml.YAMLError as e:
        print(f"✗ Erreur YAML dans '{args.metadata}': format invalide.")
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            print(f"  Le problème se trouve à la ligne {mark.line + 1}, colonne {mark.column + 1}.")
        return 1

    except Exception as e:
        print(f"✗ Une erreur inattendue est survenue : {e}")
        return 1


def cmd_hal_xml(args):
    """Génère le fichier HAL-XML"""
    try:
        artmeta = ArtMeta(args.metadata)

        # Validation
        errors, _ = artmeta.validate()
        if errors:
            print("✗ Métadonnées invalides. Lancez 'artmeta validate' pour corriger.")
            return 1

        generator = HALGenerator(artmeta.meta)
        xml_content = generator.generate_xml()

        output = Path(args.output)
        output.write_text(xml_content, encoding="utf-8")

        print(f"✓ HAL-XML généré : {output}")
        return 0

    except FileNotFoundError:
        print(f"✗ Erreur : Le fichier de métadonnées '{args.metadata}' est introuvable.")
        print("  Astuce : Vous pouvez en créer un avec la commande 'artmeta init'.")
        return 1

    except yaml.YAMLError as e:
        print(f"✗ Erreur YAML dans '{args.metadata}': format invalide.")
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            print(f"  Le problème se trouve à la ligne {mark.line + 1}, colonne {mark.column + 1}.")
        return 1

    except (OSError, PermissionError) as e:
        print(f"✗ Erreur d'écriture : Impossible d'écrire dans le fichier '{args.output}'.")
        print(f"  Détail : {e}")
        return 1

    except Exception as e:
        print(f"✗ Une erreur inattendue est survenue : {e}")
        return 1


def cmd_switch(args):
    """Change de classe de revue dans un fichier .tex"""
    try:
        artmeta = ArtMeta(args.metadata)

        if artmeta.meta is None:
            if not Path(args.metadata).exists():
                print(f"✗ Erreur : Le fichier de métadonnées '{args.metadata}' est introuvable.")
                print("  Astuce : Vous pouvez en créer un avec la commande 'artmeta init'.")
            else:
                print(f"✗ Erreur : Le fichier de métadonnées '{args.metadata}' est vide.")
            return 1

        tex_file = Path(args.texfile)
        if not tex_file.exists():
            print(f"✗ Erreur : Le fichier TeX '{tex_file}' est introuvable.")
            return 1

        generator = get_generator(args.journal, artmeta.meta)
        latex_code = generator.generate()

        insert_in_tex(str(tex_file), latex_code, args.journal)

        print(f"✓ Classe changée pour {args.journal} dans {tex_file}")
        return 0

    except yaml.YAMLError as e:
        print(f"✗ Erreur YAML dans '{args.metadata}': format invalide.")
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            print(f"  Le problème se trouve à la ligne {mark.line + 1}, colonne {mark.column + 1}.")
        return 1

    except ValueError as e:
        # Erreur venant de get_generator ou insert_in_tex
        print(f"✗ Erreur de changement : {e}")
        return 1

    except (OSError, PermissionError) as e:
        print(f"✗ Erreur d'écriture : Impossible de modifier le fichier '{args.texfile}'.")
        print(f"  Détail : {e}")
        return 1

    except Exception as e:
        print(f"✗ Une erreur inattendue est survenue : {e}")
        return 1


def cmd_stats(args):
    """Affiche des statistiques sur l'article"""
    try:
        artmeta = ArtMeta(args.metadata)

        if artmeta.meta is None:
            if not Path(args.metadata).exists():
                print(f"✗ Erreur : Le fichier de métadonnées '{args.metadata}' est introuvable.")
                print("  Astuce : Vous pouvez en créer un avec la commande 'artmeta init'.")
            else:
                print(f"✗ Erreur : Le fichier de métadonnées '{args.metadata}' est vide.")
            return 1

        stats = get_stats(artmeta.meta)

        print("📊 STATISTIQUES\n")

        if "abstract_words" in stats:
            print(f"Résumé : {stats['abstract_words']} mots, {stats['abstract_chars']} caractères")

        if "authors_count" in stats:
            authors_count = stats["authors_count"]
            orcid_count = stats.get("authors_with_orcid", 0)
            print(f"Auteurs : {authors_count} ({orcid_count} avec ORCID)")

        if "affiliations_count" in stats:
            print(f"Affiliations : {stats['affiliations_count']}")

        if "countries" in stats:
            print(f"Pays : {', '.join(stats['countries'])}")

        if "keywords_count" in stats:
            print(f"Mots-clés : {stats['keywords_count']}")

        if "msc_codes_count" in stats:
            print(f"Codes MSC : {stats['msc_codes_count']}")

        return 0

    except yaml.YAMLError as e:
        print(f"✗ Erreur YAML dans '{args.metadata}': format invalide.")

        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            print(f"  Le problème se trouve à la ligne {mark.line + 1}, colonne {mark.column + 1}.")
        return 1

    except Exception as e:
        print(f"✗ Une erreur inattendue est survenue : {e}")
        return 1


def create_parser():
    """Crée et configure le parser d'arguments"""
    parser = argparse.ArgumentParser(
        prog="artmeta",
        description="Gestionnaire de métadonnées pour articles académiques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  artmeta init                                    # Créer un template art.yml
  artmeta validate                                # Valider art.yml
  artmeta info                                    # Afficher un résumé
  artmeta generate -j amsart --insert main.tex    # Générer et insérer
  artmeta generate --autodetect-from main.tex     # Autodétection
  artmeta switch -j elsarticle main.tex           # Changer de revue
  artmeta hal-xml -o metadata.xml                 # Générer HAL-XML
  artmeta stats                                   # Statistiques

Documentation : https://artmeta.readthedocs.io
        """,
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")

    # init
    parser_init = subparsers.add_parser("init", help="Créer un template art.yml")
    parser_init.add_argument("-o", "--output", default="art.yml", help="Fichier de sortie")
    parser_init.add_argument("-f", "--force", action="store_true", help="Écraser si existe")

    # validate
    parser_validate = subparsers.add_parser("validate", help="Valider art.yml")
    parser_validate.add_argument("-m", "--metadata", default="art.yml", help="Fichier à valider")

    # generate
    parser_generate = subparsers.add_parser("generate", help="Générer le code LaTeX")
    group = parser_generate.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-j",
        "--journal",
        choices=["amsart", "elsarticle", "svjour3", "siamart", "article"],
        help="Classe de document (ex: amsart)",
    )
    group.add_argument(
        "--autodetect-from",
        metavar="FILE.tex",
        help="Détecter la classe depuis un fichier .tex",
    )
    parser_generate.add_argument("-m", "--metadata", default="art.yml")
    parser_generate.add_argument("-i", "--insert", metavar="FILE.tex", help="Insérer dans FILE.tex")
    parser_generate.add_argument("-o", "--output", help="Fichier de sortie")

    # info
    parser_info = subparsers.add_parser("info", help="Afficher un résumé")
    parser_info.add_argument("-m", "--metadata", default="art.yml")

    # hal-xml
    parser_hal = subparsers.add_parser("hal-xml", help="Générer HAL-XML")
    parser_hal.add_argument("-m", "--metadata", default="art.yml")
    parser_hal.add_argument("-o", "--output", default="hal_metadata.xml")

    # switch
    parser_switch = subparsers.add_parser("switch", help="Changer de classe de revue")
    parser_switch.add_argument(
        "-j",
        "--journal",
        choices=["amsart", "elsarticle", "svjour3", "siamart", "article"],
        required=True,
        help="Nouvelle classe de document",
    )
    parser_switch.add_argument("texfile", help="Fichier .tex à modifier")
    parser_switch.add_argument("-m", "--metadata", default="art.yml")

    # stats
    parser_stats = subparsers.add_parser("stats", help="Afficher des statistiques")
    parser_stats.add_argument("-m", "--metadata", default="art.yml")

    return parser


def main():
    """Point d'entrée principal de l'application CLI"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Dispatcher
    commands = {
        "init": cmd_init,
        "validate": cmd_validate,
        "generate": cmd_generate,
        "info": cmd_info,
        "hal-xml": cmd_hal_xml,
        "switch": cmd_switch,
        "stats": cmd_stats,
    }

    return commands[args.command](args)
