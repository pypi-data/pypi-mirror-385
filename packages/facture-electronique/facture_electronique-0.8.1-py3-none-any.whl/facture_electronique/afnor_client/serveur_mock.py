# -*- coding: utf-8 -*-
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any
import connexion
from connexion.mock import MockResolver


def configurer_journalisation():
    """Configure le logger racine pour un affichage unifié."""
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)-8s - %(name)-20s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("connexion").setLevel(logging.INFO)


logger = logging.getLogger(__name__)

# --- Constantes ---
CHEMIN_SPECIFICATIONS = Path(__file__).parent
SPEC_FLOW_SERVICE = "ANNEXE B - PR XP Z12-013 - AFNOR-Flow_Service-1.0.2-swagger.json"
SPEC_DIRECTORY_SERVICE = "ANNEXE A - PR XP Z12-013 - AFNOR-Directory_Service-1.0.0-swagger.json"


def charger_et_patcher_spec(chemin_spec: Path) -> Dict[str, Any]:
    """
    Charge une spec OpenAPI et RETIRE toutes les exigences de sécurité.

    Cela permet au serveur mock de fonctionner sans aucune authentification.

    Args:
            chemin_spec: Chemin vers le fichier JSON de la spec

    Returns:
            Dict contenant la spec modifiée
    """
    logger.info(f"Chargement et patch de la spec: {chemin_spec.name}")

    with open(chemin_spec, "r", encoding="utf-8") as f:
        spec = json.load(f)

    # Retire la sécurité globale (au niveau de l'API)
    if "security" in spec:
        logger.debug("  → Suppression de la sécurité globale")
        del spec["security"]

    # Retire la sécurité de chaque endpoint
    if "paths" in spec:
        for chemin, operations in spec["paths"].items():
            for methode, details in operations.items():
                if isinstance(details, dict) and "security" in details:
                    logger.debug(f"  → Suppression de la sécurité pour {methode.upper()} {chemin}")
                    del details["security"]

    logger.info("  ✓ Spec patchée: toute authentification désactivée")
    return spec


def lister_endpoints_enregistres(application: connexion.AsyncApp):
    """Affiche tous les endpoints enregistrés."""
    logger.info(msg="-" * 70)
    logger.info(msg="Endpoints disponibles sur ce serveur de mock :")
    logger.info(msg="-" * 70)

    apis_chargees = application.middleware.apis if hasattr(application, "middleware") else []

    if not apis_chargees:
        logger.info(msg="Aucune API chargée")
        return

    for api in apis_chargees:
        titre_api = api.specification.get("info", {}).get("title", "API sans titre")
        logger.info(msg=f"\n▶ API : {titre_api} (Base: {api.base_path})")

        chemins = api.specification.get("paths", {})
        if not chemins:
            logger.info(msg="\t(Aucun endpoint défini)")
            continue

        for chemin, details_chemin in chemins.items():
            for methode, details_methode in details_chemin.items():
                if methode.upper() in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                    resume = details_methode.get("summary", "")
                    url_complete = f"{api.base_path}{chemin}"
                    logger.info(msg=f"\t{methode.upper():<7} {url_complete:<60} {resume}")


# --- Configuration de l'application Connexion ---
application_connexion = connexion.AsyncApp(__name__)

# Charge et patche les specs pour retirer l'authentification
spec_flow_patchee = charger_et_patcher_spec(CHEMIN_SPECIFICATIONS / SPEC_FLOW_SERVICE)
spec_directory_patchee = charger_et_patcher_spec(CHEMIN_SPECIFICATIONS / SPEC_DIRECTORY_SERVICE)

# Ajout de l'API Flow Service (SANS authentification)
application_connexion.add_api(
    spec_flow_patchee,  # Utilise la spec modifiée en mémoire
    resolver=MockResolver(mock_all="all"),
    base_path="/flow",
    pythonic_params=True,
    validate_responses=False,
)

# Ajout de l'API Directory Service (SANS authentification)
application_connexion.add_api(
    spec_directory_patchee,  # Utilise la spec modifiée en mémoire
    resolver=MockResolver(mock_all="all"),
    base_path="/directory/v1",
    pythonic_params=True,
    validate_responses=False,
)


def main():
    """Point d'entrée pour le lancement du serveur de mock."""
    configurer_journalisation()

    analyseur = argparse.ArgumentParser(
        description="Serveur de mock pour les API de facturation électronique AFNOR."
    )
    analyseur.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="Le port TCP sur lequel le serveur doit écouter.",
    )
    analyseur.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="L'adresse IP. Utiliser 0.0.0.0 pour le rendre accessible sur le réseau.",
    )
    arguments = analyseur.parse_args()

    port = arguments.port
    host = arguments.host
    url_base = f"http://{host}:{port}"

    logger.info(msg="\n" + "=" * 70)
    logger.info(msg="🚀 SERVEUR MOCK AFNOR - FACTURATION ÉLECTRONIQUE")
    logger.info(msg="=" * 70)

    lister_endpoints_enregistres(application_connexion)

    logger.info(msg="\n" + "-" * 70)
    logger.info(msg="📚 Interfaces Swagger UI :")
    logger.info(msg=f"  • Flow Service:      {url_base}/flow/v1/ui/")
    logger.info(msg=f"  • Directory Service: {url_base}/directory/ui/")
    logger.info(msg="-" * 70)
    logger.info(msg="\n💡 Exemples de commandes curl (SANS authentification) :")
    logger.info(msg=f"  curl {url_base}/flow/v1/healthcheck")
    logger.info(msg=f"  curl {url_base}/directory/healthcheck")
    logger.info(msg="-" * 70)
    logger.info(msg=f"\n✅ Serveur démarré sur {url_base}")
    logger.info(msg="   Appuyez sur Ctrl+C pour arrêter.\n")

    application_connexion.run(port=port, host=host)


if __name__ == "__main__":
    main()
