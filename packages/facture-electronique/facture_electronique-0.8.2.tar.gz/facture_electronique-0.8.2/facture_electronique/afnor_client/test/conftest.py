# -*- coding: utf-8 -*-
from pathlib import Path
import json
import pytest
import threading
import time
from wsgiref.simple_server import make_server
import socket

from facture_electronique.afnor_client.serveur_mock import creer_application_mock


def _flow_swagger_path():
    """Chemin vers le Swagger Flow Service"""
    return (
        Path(__file__).parent.parent
        / "swagger"
        / "ANNEXE B - PR XP Z12-013 - AFNOR-Flow_Service-1.0.2-swagger.json"
    )


@pytest.fixture(scope="module")
def flow_swagger_path():
    return _flow_swagger_path()


@pytest.fixture(scope="module")
def spec_flow(flow_swagger_path):
    """
    Charge le contenu du Swagger Flow Service en utilisant le chemin fourni
    par la fixture `flow_swagger_path`.
    """
    with open(flow_swagger_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _directory_swagger_path():
    """Chemin vers le Swagger Directory Service"""
    return (
        Path(__file__).parent.parent
        / "swagger"
        / "ANNEXE A - PR XP Z12-013 - AFNOR-Directory_Service-1.0.0-swagger.json"
    )


@pytest.fixture(scope="module")
def directory_swagger_path():
    return _directory_swagger_path()


@pytest.fixture(scope="module")
def spec_directory(flow_swagger_path):
    """
    Charge le contenu du Swagger Flow Service en utilisant le chemin fourni
    par la fixture `flow_swagger_path`.
    """
    with open(directory_swagger_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def serveur_mock_demarre(request):
    """
    Démarre le serveur de mock Connexion dans un thread séparé.
    Cette fixture a une portée "session", elle ne démarre le serveur qu'une
    seule fois pour tous les tests, ce qui est très performant.
    """
    # Trouve un port TCP libre pour éviter les conflits
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]

    host = "127.0.0.1"
    url_base = f"http://{host}:{port}"

    application_connexion = creer_application_mock()

    # Crée une instance de serveur WSGI
    serveur = make_server(host, port, application_connexion)

    # Lance le serveur dans un thread pour ne pas bloquer les tests
    serveur_thread = threading.Thread(target=serveur.serve_forever)
    serveur_thread.daemon = True
    serveur_thread.start()

    # Attend un court instant pour s'assurer que le serveur est prêt
    time.sleep(0.1)

    # Le `yield` passe la main aux tests, leur fournissant l'URL du serveur
    yield url_base

    # Cette partie est exécutée APRÈS la fin de tous les tests de la session
    serveur.shutdown()
    serveur_thread.join()
