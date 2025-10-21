import pytest
import requests
import threading
import time

from facture_electronique.afnor_client.serveur_mock import creer_application_mock


@pytest.fixture(scope="module")
def mock_server():
    """Fixture qui lance le serveur mock dans un thread en arrière-plan."""
    port = 8088
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    app = creer_application_mock()

    server_thread = threading.Thread(target=app.run, kwargs={"port": port, "host": host})
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)  # Donner le temps au serveur de démarrer

    try:
        requests.get(f"{url}/flow/v1/healthcheck", timeout=1)
    except requests.ConnectionError:
        pytest.fail("Le serveur de mock n'a pas pu démarrer.")

    yield url


def test_mock_server_flow_healthcheck(mock_server):
    """Teste le endpoint de healthcheck du Flow Service."""
    response = requests.get(f"{mock_server}/flow/v1/healthcheck")
    assert response.status_code == 200


def test_mock_server_directory_healthcheck(mock_server):
    """Teste le endpoint de healthcheck du Directory Service."""
    response = requests.get(f"{mock_server}/directory/v1/healthcheck")
    assert response.status_code == 200


def test_mock_server_swagger_ui_is_available(mock_server):
    """Vérifie que les interfaces Swagger UI sont accessibles."""
    # Le base_path du Flow service est /flow, l'UI est à la racine de ce path.
    response_flow = requests.get(f"{mock_server}/flow/ui/")
    assert response_flow.status_code == 200
    assert "Swagger UI" in response_flow.text

    # Le base_path du Directory service est /directory/v1
    response_dir = requests.get(f"{mock_server}/directory/v1/ui/")
    assert response_dir.status_code == 200
    assert "Swagger UI" in response_dir.text


def test_mock_server_returns_mocked_data(mock_server):
    """Vérifie qu'un endpoint mocké retourne des données conformes au schéma."""
    # On utilise un payload simple et valide (recherche par flowId)
    search_payload = {"where": {"flowId": "flow-id-12345"}}
    response = requests.post(f"{mock_server}/flow/v1/flows/search", json=search_payload)

    assert response.status_code == 200

    data = response.json()
    assert "total" in data
    assert "results" in data
    assert isinstance(data["results"], list)
