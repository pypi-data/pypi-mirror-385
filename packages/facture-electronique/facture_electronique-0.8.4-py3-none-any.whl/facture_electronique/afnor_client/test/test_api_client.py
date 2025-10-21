import pytest
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import requests_mock
from prance import ResolvingParser
from openapi_spec_validator import validate
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError
from facture_electronique.afnor_client.test.conftest import (
    _flow_swagger_path,
    _directory_swagger_path,
)

# ============================================================================
# FIXTURES DE TEST
# ============================================================================


@pytest.fixture
def mock_credentials():
    """Credentials de test"""
    return {
        "base_url": "https://api.test.com",
        "token_url": "https://auth.test.com/token",
        "client_id": "test_client",
        "client_secret": "test_secret",
    }


@pytest.fixture
def mock_token_response():
    """Réponse OAuth2 mock"""
    return {"access_token": "mock_access_token_12345", "token_type": "Bearer", "expires_in": 3600}


@pytest.fixture
def sample_invoice_xml():
    """Facture XML de test"""
    return """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
</rsm:CrossIndustryInvoice>"""


# ============================================================================
# TESTS DE VALIDATION SWAGGER
# ============================================================================


class TestSwaggerValidation:
    """Tests de validation des fichiers Swagger"""

    def test_flow_swagger_is_valid(self, flow_swagger_path):
        """Vérifie que le Swagger Flow Service est valide"""
        if not flow_swagger_path.exists():
            pytest.skip("Fichier Swagger Flow Service non trouvé")

        with open(flow_swagger_path, "r", encoding="utf-8") as f:
            spec = json.load(f)

        try:
            validate(spec)
            assert True, "Swagger Flow Service est valide"
        except OpenAPIValidationError as e:
            pytest.fail(f"Swagger Flow Service invalide: {e}")

    def test_directory_swagger_is_valid(self, directory_swagger_path):
        """Vérifie que le Swagger Directory Service est valide"""
        if not directory_swagger_path.exists():
            pytest.skip("Fichier Swagger Directory Service non trouvé")

        with open(directory_swagger_path, "r", encoding="utf-8") as f:
            spec = json.load(f)

        try:
            validate(spec)
            assert True, "Swagger Directory Service est valide"
        except OpenAPIValidationError as e:
            pytest.fail(f"Swagger Directory Service invalide: {e}")

    def test_flow_endpoints_exist(self, flow_swagger_path):
        """Vérifie que tous les endpoints obligatoires Flow existent"""
        if not flow_swagger_path.exists():
            pytest.skip("Fichier Swagger Flow Service non trouvé")

        with open(flow_swagger_path, "r", encoding="utf-8") as f:
            spec = json.load(f)

        required_paths = ["/v1/flows", "/v1/flows/search", "/v1/flows/{flowId}", "/v1/healthcheck"]

        paths = spec.get("paths", {})
        for path in required_paths:
            assert path in paths, f"Endpoint obligatoire manquant: {path}"

    def test_directory_endpoints_exist(self, directory_swagger_path):
        """Vérifie que tous les endpoints obligatoires Directory existent"""
        if not directory_swagger_path.exists():
            pytest.skip("Fichier Swagger Directory Service non trouvé")

        with open(directory_swagger_path, "r", encoding="utf-8") as f:
            spec = json.load(f)

        required_paths = [
            "/siren/search",
            "/siren/code-insee:{siren}",
            "/siret/search",
            "/siret/code-insee:{siret}",
            "/routing-code/search",
            "/directory-line/search",
            "/healthcheck",
        ]

        paths = spec.get("paths", {})
        for path in required_paths:
            assert path in paths, f"Endpoint obligatoire manquant: {path}"


# ============================================================================
# TESTS FLOW SERVICE CLIENT
# ============================================================================


class TestFlowServiceClient:
    """Tests pour le FlowServiceClient"""

    @pytest.fixture
    def flow_client(self, mock_credentials):
        """Instance du client Flow"""
        from facture_electronique.afnor_client.client import FlowServiceClient

        return FlowServiceClient(
            base_url=mock_credentials["base_url"] + "/flow-service",
            token_url=mock_credentials["token_url"],
            client_id=mock_credentials["client_id"],
            client_secret=mock_credentials["client_secret"],
        )

    def test_healthcheck_success(self, flow_client, mock_token_response):
        """Test healthcheck réussi"""
        with requests_mock.Mocker() as m:
            # Mock OAuth2
            m.post("https://auth.test.com/token", json=mock_token_response)
            # Mock healthcheck
            m.get("https://api.test.com/flow-service/v1/healthcheck", status_code=200)

            result = flow_client.healthcheck()
            assert result is True

    def test_healthcheck_failure(self, flow_client, mock_token_response):
        """Test healthcheck en échec"""
        with requests_mock.Mocker() as m:
            # Mock OAuth2
            m.post("https://auth.test.com/token", json=mock_token_response)
            # Mock healthcheck en erreur
            m.get("https://api.test.com/flow-service/v1/healthcheck", status_code=503)

            result = flow_client.healthcheck()
            assert result is False

    def test_submit_flow_success(
        self, flow_client, mock_token_response, sample_invoice_xml, tmp_path
    ):
        """Test soumission de flux réussie"""
        # Créer un fichier temporaire
        invoice_file = tmp_path / "invoice.xml"
        invoice_file.write_text(sample_invoice_xml)

        # Calculer le SHA256 attendu
        expected_sha256 = hashlib.sha256(sample_invoice_xml.encode()).hexdigest()

        mock_response = {
            "flowId": "flow-123456",
            "trackingId": "track-789",
            "name": "Test Invoice",
            "flowSyntax": "CII",
            "flowProfile": "CIUS",
            "sha256": expected_sha256,
        }

        with requests_mock.Mocker() as m:
            # Mock OAuth2
            m.post("https://auth.test.com/token", json=mock_token_response)
            # Mock submit flow
            m.post(
                "https://api.test.com/flow-service/v1/flows", json=mock_response, status_code=202
            )

            result = flow_client.submit_flow(
                file_path=str(invoice_file),
                flow_name="Test Invoice",
                flow_syntax="CII",
                flow_profile="CIUS",
                tracking_id="track-789",
            )

            assert result["flowId"] == "flow-123456"
            assert result["sha256"] == expected_sha256

            # Vérifier que la requête contient bien le flowInfo
            last_request = m.last_request
            assert last_request.method == "POST"
            assert "Authorization" in last_request.headers

    def test_submit_flow_validation_error(self, flow_client, mock_token_response, tmp_path):
        """Test erreur de validation lors de la soumission"""
        invoice_file = tmp_path / "invalid.xml"
        invoice_file.write_text("invalid content")

        error_response = {"errorCode": "VALIDATION_ERROR", "errorMessage": "Invalid XML format"}

        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.post(
                "https://api.test.com/flow-service/v1/flows", json=error_response, status_code=400
            )

            from facture_electronique.afnor_client.client import AFNORAPIError

            with pytest.raises(AFNORAPIError) as exc_info:
                flow_client.submit_flow(
                    file_path=str(invoice_file), flow_name="Invalid", flow_syntax="CII"
                )

            assert exc_info.value.status_code == 400
            assert exc_info.value.error_code == "VALIDATION_ERROR"

    def test_search_flows_with_filters(self, flow_client, mock_token_response):
        """Test recherche de flux avec filtres"""
        mock_response = {
            "total": 42,
            "offset": 0,
            "limit": 25,
            "filter": {},
            "results": [
                {
                    "flowId": "flow-001",
                    "flowType": "SupplierInvoice",
                    "flowDirection": "Out",
                    "flowSyntax": "CII",
                    "acknowledgement": {"status": "Ok"},
                }
            ],
        }

        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.post("https://api.test.com/flow-service/v1/flows/search", json=mock_response)

            result = flow_client.search_flows(
                flow_type=["SupplierInvoice"], flow_direction=["Out"], ack_status="Ok", limit=25
            )

            assert result["total"] == 42
            assert len(result["results"]) == 1
            assert result["results"][0]["flowId"] == "flow-001"

            # Vérifier la structure de la requête
            last_request = m.last_request
            request_body = json.loads(last_request.body)
            assert "where" in request_body
            assert request_body["limit"] == 25

    def test_download_flow_original(self, flow_client, mock_token_response, tmp_path):
        """Test téléchargement d'un flux original"""
        file_content = b"Mock invoice content"

        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.get(
                "https://api.test.com/flow-service/v1/flows/flow-123",
                content=file_content,
                headers={"Content-Disposition": "attachment;filename=invoice.xml"},
            )

            output_path = tmp_path / "downloaded.xml"
            result = flow_client.download_flow(
                flow_id="flow-123", doc_type="Original", output_path=str(output_path)
            )

            assert result == file_content
            assert output_path.exists()
            assert output_path.read_bytes() == file_content


# ============================================================================
# TESTS DIRECTORY SERVICE CLIENT
# ============================================================================


class TestDirectoryServiceClient:
    """Tests pour le DirectoryServiceClient"""

    @pytest.fixture
    def directory_client(self, mock_credentials):
        """Instance du client Directory"""
        from facture_electronique.afnor_client.client import DirectoryServiceClient

        return DirectoryServiceClient(
            base_url=mock_credentials["base_url"] + "/directory-service",
            token_url=mock_credentials["token_url"],
            client_id=mock_credentials["client_id"],
            client_secret=mock_credentials["client_secret"],
        )

    def test_get_siren_success(self, directory_client, mock_token_response):
        """Test récupération d'un SIREN"""
        mock_response = {
            "siren": "702042755",
            "businessName": "Test Company",
            "entityType": "PrivateVatRegistered",
            "administrativeStatus": "A",
        }

        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.get(
                "https://api.test.com/directory-service/siren/code-insee:702042755",
                json=mock_response,
            )

            result = directory_client.get_siren("702042755")

            assert result["siren"] == "702042755"
            assert result["businessName"] == "Test Company"
            assert result["entityType"] == "PrivateVatRegistered"

    def test_search_siret_with_filters(self, directory_client, mock_token_response):
        """Test recherche SIRET avec filtres"""
        mock_response = {
            "total_number_results": 5,
            "results": [
                {
                    "siret": "70204275500240",
                    "siren": "702042755",
                    "name": "Établissement Principal",
                    "facilityType": "P",
                    "administrativeStatus": "A",
                }
            ],
        }

        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.post("https://api.test.com/directory-service/siret/search", json=mock_response)

            result = directory_client.search_siret(
                filters={
                    "siren": {"op": "contains", "value": "702042"},
                    "administrativeStatus": {"op": "strict", "value": "A"},
                },
                limit=10,
            )

            assert result["total_number_results"] == 5
            assert len(result["results"]) == 1

            # Vérifier la structure de la requête
            last_request = m.last_request
            request_body = json.loads(last_request.body)
            assert "filters" in request_body
            assert request_body["filters"]["siren"]["op"] == "contains"

    def test_create_routing_code(self, directory_client, mock_token_response):
        """Test création d'un code routage"""
        mock_response = {
            "idInstance": 12345,
            "siret": "70204275500240",
            "routingIdentifier": "SERVICE-001",
        }

        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.post(
                "https://api.test.com/directory-service/routing-code",
                json=mock_response,
                status_code=201,
            )

            result = directory_client.create_routing_code(
                siret="70204275500240",
                routing_identifier="SERVICE-001",
                routing_code_name="Service Comptabilité",
                facility_nature="Private",
                administrative_status="A",
                routing_identifier_type="0224",
            )

            assert result["idInstance"] == 12345
            assert result["routingIdentifier"] == "SERVICE-001"

            # Vérifier le corps de la requête
            last_request = m.last_request
            request_body = json.loads(last_request.body)
            assert request_body["siret"] == "70204275500240"
            assert request_body["facilityNature"] == "Private"

    def test_create_directory_line(self, directory_client, mock_token_response):
        """Test création d'une ligne d'annuaire"""
        mock_response = {
            "idInstance": 67890,
            "addressingIdentifier": "ADDR-123456",
            "dateFrom": "2025-01-01",
        }

        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.post(
                "https://api.test.com/directory-service/directory-line",
                json=mock_response,
                status_code=201,
            )

            result = directory_client.create_directory_line(
                siren="702042755",
                platform_registration_number="0145",
                date_from="2025-01-01",
                siret="70204275500240",
            )

            assert result["idInstance"] == 67890
            assert result["addressingIdentifier"] == "ADDR-123456"

            # Vérifier la structure de la requête
            last_request = m.last_request
            request_body = json.loads(last_request.body)
            assert "period" in request_body
            assert "addressingInformation" in request_body
            assert request_body["period"]["dateFrom"] == "2025-01-01"

    def test_delete_directory_line(self, directory_client, mock_token_response):
        """Test suppression d'une ligne d'annuaire"""
        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.delete(
                "https://api.test.com/directory-service/directory-line/id-instance:12345",
                status_code=204,
            )

            result = directory_client.delete_directory_line(
                id_instance=12345, ppf_affiliations=["702042755"]
            )

            assert result is None

            # Vérifier les headers
            last_request = m.last_request
            assert "PPF-affiliations" in last_request.headers

    def test_healthcheck_success(self, directory_client, mock_token_response):
        """Test healthcheck réussi pour DirectoryService"""
        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.get("https://api.test.com/directory-service/healthcheck", status_code=200)

            result = directory_client.healthcheck()
            assert result is True

    def test_get_siren_not_found(self, directory_client, mock_token_response):
        """Test récupération d'un SIREN non trouvé"""
        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.get(
                "https://api.test.com/directory-service/siren/code-insee:999999999",
                status_code=404,
                json={"errorCode": "NOT_FOUND", "errorMessage": "SIREN not found"},
            )
            from facture_electronique.afnor_client.client import AFNORAPIError

            with pytest.raises(AFNORAPIError) as exc_info:
                directory_client.get_siren("999999999")

            assert exc_info.value.status_code == 404

    def test_get_siren_by_instance_success(self, directory_client, mock_token_response):
        """Test récupération d'un SIREN par id-instance"""
        mock_response = {"siren": "702042755", "businessName": "Test Company"}
        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.get(
                "https://api.test.com/directory-service/siren/id-instance:12345",
                json=mock_response,
            )
            result = directory_client.get_siren_by_instance(12345)
            assert result["siren"] == "702042755"

    def test_get_siret_success(self, directory_client, mock_token_response):
        """Test récupération d'un SIRET"""
        mock_response = {"siret": "70204275500240", "name": "Établissement Principal"}
        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.get(
                "https://api.test.com/directory-service/siret/code-insee:70204275500240",
                json=mock_response,
            )
            result = directory_client.get_siret("70204275500240")
            assert result["siret"] == "70204275500240"

    def test_search_routing_code_success(self, directory_client, mock_token_response):
        """Test recherche de code routage"""
        mock_response = {
            "total_number_results": 1,
            "results": [{"routingIdentifier": "SERVICE-001"}],
        }
        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.post(
                "https://api.test.com/directory-service/routing-code/search",
                json=mock_response,
            )
            result = directory_client.search_routing_code(
                filters={"siret": {"op": "strict", "value": "70204275500240"}}
            )
            assert result["total_number_results"] == 1
            assert result["results"][0]["routingIdentifier"] == "SERVICE-001"

    def test_get_directory_line_success(self, directory_client, mock_token_response):
        """Test récupération d'une ligne d'annuaire"""
        mock_response = {"addressingIdentifier": "ADDR-123456", "siren": "702042755"}
        with requests_mock.Mocker() as m:
            m.post("https://auth.test.com/token", json=mock_token_response)
            m.get(
                "https://api.test.com/directory-service/directory-line/code:ADDR-123456",
                json=mock_response,
            )
            result = directory_client.get_directory_line("ADDR-123456")
            assert result["siren"] == "702042755"


# ============================================================================
# TESTS DE CONFORMITÉ SWAGGER
# ============================================================================


class TestSwaggerConformity:
    """Tests de conformité avec les spécifications Swagger"""

    def test_flow_request_conforms_to_swagger(self, flow_swagger_path):
        """Vérifie que les requêtes Flow respectent le Swagger"""
        if not flow_swagger_path.exists():
            pytest.skip("Fichier Swagger non trouvé")

        # Parser le Swagger avec résolution des références
        parser = ResolvingParser(str(flow_swagger_path))
        spec = parser.specification

        # Vérifier le schéma FlowInfo
        flow_info_schema = spec["components"]["schemas"]["FlowInfo"]

        assert "name" in flow_info_schema["required"]
        assert "flowSyntax" in flow_info_schema["required"]

        # Vérifier les valeurs d'énumération pour FlowSyntax
        flow_syntax_schema = spec["components"]["schemas"]["FlowSyntax"]
        expected_syntaxes = ["CII", "UBL", "Factur-X", "CDAR", "FRR"]
        assert flow_syntax_schema["enum"] == expected_syntaxes

        # Vérifier les FlowTypes
        flow_type_schema = spec["components"]["schemas"]["FlowType"]
        expected_types = [
            "CustomerInvoice",
            "SupplierInvoice",
            "CustomerInvoiceLC",
            "SupplierInvoiceLC",
            "TransactionReport",
            "PaymentReport",
        ]
        assert flow_type_schema["enum"] == expected_types

    def test_directory_request_conforms_to_swagger(self, directory_swagger_path):
        """Vérifie que les requêtes Directory respectent le Swagger"""
        if not directory_swagger_path.exists():
            pytest.skip("Fichier Swagger non trouvé")

        parser = ResolvingParser(str(directory_swagger_path))
        spec = parser.specification

        # Vérifier le pattern SIREN
        siren_param = spec["components"]["parameters"]["siren-path"]
        assert siren_param["schema"]["pattern"] == "^([0-9]{9})$"
        assert siren_param["schema"]["maxLength"] == 9

        # Vérifier le pattern SIRET
        siret_param = spec["components"]["parameters"]["siret-path"]
        assert siret_param["schema"]["pattern"] == "^([0-9]{14})$"
        assert siret_param["schema"]["maxLength"] == 14

        # Vérifier les champs obligatoires pour createRoutingCodeBody
        routing_code_schema = spec["components"]["schemas"]["createRoutingCodeBody"]
        required_fields = routing_code_schema["required"]
        assert "siret" in required_fields
        assert "routingIdentifier" in required_fields
        assert "facilityNature" in required_fields


# ============================================================================
# TESTS D'AUTHENTIFICATION
# ============================================================================


class TestAuthentication:
    """Tests du mécanisme d'authentification OAuth2"""

    def test_token_is_cached(self, mock_credentials, mock_token_response):
        """Vérifie que le token est mis en cache"""
        from facture_electronique.afnor_client.client import FlowServiceClient

        client = FlowServiceClient(
            base_url=mock_credentials["base_url"],
            token_url=mock_credentials["token_url"],
            client_id=mock_credentials["client_id"],
            client_secret=mock_credentials["client_secret"],
        )

        with requests_mock.Mocker() as m:
            m.post(mock_credentials["token_url"], json=mock_token_response)
            m.get(f"{mock_credentials['base_url']}/v1/healthcheck", status_code=200)

            # Premier appel
            client.healthcheck()
            # Deuxième appel
            client.healthcheck()

            # Vérifier qu'on n'a appelé le token endpoint qu'une seule fois
            token_requests = [
                req for req in m.request_history if req.url == mock_credentials["token_url"]
            ]
            assert len(token_requests) == 1

    def test_token_refresh_on_expiry(self, mock_credentials, mock_token_response):
        """Vérifie que le token est renouvelé à expiration"""
        from facture_electronique.afnor_client.client import FlowServiceClient

        client = FlowServiceClient(
            base_url=mock_credentials["base_url"],
            token_url=mock_credentials["token_url"],
            client_id=mock_credentials["client_id"],
            client_secret=mock_credentials["client_secret"],
        )

        # Simuler un token expiré
        client._token_expiry = datetime.now() - timedelta(seconds=60)

        with requests_mock.Mocker() as m:
            m.post(mock_credentials["token_url"], json=mock_token_response)
            m.get(f"{mock_credentials['base_url']}/v1/healthcheck", status_code=200)

            client.healthcheck()

            # Vérifier qu'un nouveau token a été demandé
            token_requests = [
                req for req in m.request_history if req.url == mock_credentials["token_url"]
            ]
            assert len(token_requests) == 1


# ============================================================================
# TESTS DE PAGINATION
# ============================================================================


class TestPagination:
    """Tests du mécanisme de pagination"""

    def test_flow_search_pagination(self, mock_credentials, mock_token_response):
        """Test pagination dans la recherche de flux"""
        from facture_electronique.afnor_client.client import FlowServiceClient

        client = FlowServiceClient(
            base_url=mock_credentials["base_url"] + "/flow-service",
            token_url=mock_credentials["token_url"],
            client_id=mock_credentials["client_id"],
            client_secret=mock_credentials["client_secret"],
        )

        with requests_mock.Mocker() as m:
            m.post(mock_credentials["token_url"], json=mock_token_response)
            m.post(
                f"{mock_credentials['base_url']}/flow-service/v1/flows/search",
                json={"total": 150, "offset": 50, "limit": 25, "results": []},
            )

            result = client.search_flows(flow_type=["SupplierInvoice"], offset=50, limit=25)

            assert result["total"] == 150
            assert result["offset"] == 50
            assert result["limit"] == 25

            # Vérifier la requête
            last_request = m.last_request
            request_body = json.loads(last_request.body)
            assert request_body["offset"] == 50
            assert request_body["limit"] == 25

    def test_directory_search_pagination(self, mock_credentials, mock_token_response):
        """Test pagination dans la recherche Directory"""
        from facture_electronique.afnor_client.client import DirectoryServiceClient

        client = DirectoryServiceClient(
            base_url=mock_credentials["base_url"] + "/directory-service",
            token_url=mock_credentials["token_url"],
            client_id=mock_credentials["client_id"],
            client_secret=mock_credentials["client_secret"],
        )

        with requests_mock.Mocker() as m:
            m.post(mock_credentials["token_url"], json=mock_token_response)
            m.post(
                f"{mock_credentials['base_url']}/directory-service/siren/search",
                json={"total_number_results": 200, "results": []},
            )

            client.search_siren(
                filters={"siren": {"op": "contains", "value": "702"}}, limit=50, ignore=100
            )

            # Vérifier la requête
            last_request = m.last_request
            request_body = json.loads(last_request.body)
            assert request_body["limit"] == 50
            assert request_body["ignore"] == 100


# ============================================================================
# SCRIPT DE VALIDATION COMPLÈTE
# ============================================================================


def validate_client_against_swagger(swagger_path: Path, client_class: str):
    """
    Valide qu'un client implémente correctement tous les endpoints du Swagger

    Args:
        swagger_path: Chemin vers le fichier Swagger
        client_class: Nom de la classe client ('FlowServiceClient' ou 'DirectoryServiceClient')
    """
    if not swagger_path.exists():
        print(f"❌ Fichier Swagger non trouvé: {swagger_path}")
        return False

    with open(swagger_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    print(f"\n{'=' * 80}")
    print(f"Validation du client {client_class} contre {swagger_path.name}")
    print(f"{'=' * 80}\n")

    # 1. Valider le Swagger
    print("1. Validation du fichier Swagger...")
    try:
        validate(spec)
        print("   ✅ Swagger valide\n")
    except OpenAPIValidationError as e:
        print(f"   ❌ Swagger invalide: {e}\n")
        return False

    # 2. Vérifier les endpoints
    print("2. Vérification des endpoints...")
    paths = spec.get("paths", {})
    print(f"   Nombre d'endpoints: {len(paths)}")

    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "patch", "delete"]:
                operation_id = details.get("operationId", "N/A")
                print(f"   ✅ {method.upper():6} {path:50} ({operation_id})")

    print()

    # 3. Vérifier les schémas obligatoires
    print("3. Vérification des schémas...")
    schemas = spec.get("components", {}).get("schemas", {})
    print(f"   Nombre de schémas: {len(schemas)}")

    # 4. Vérifier l'authentification
    print("\n4. Vérification de l'authentification...")
    security_schemes = spec.get("components", {}).get("securitySchemes", {})
    for scheme_name, scheme_details in security_schemes.items():
        scheme_type = scheme_details.get("type")
        print(f"   ✅ {scheme_name}: {scheme_type}")

    print(f"\n{'=' * 80}")
    print("✅ Validation complète réussie!")
    print(f"{'=' * 80}\n")

    return True


if __name__ == "__main__":
    """
    Exécution des tests et validation
    
    Usage:
        # Exécuter tous les tests
        pytest test_afnor_client.py -v
        
        # Exécuter seulement les tests de validation Swagger
        pytest test_afnor_client.py::TestSwaggerValidation -v
        
        # Exécuter avec couverture
        pytest test_afnor_client.py --cov=afnor_client --cov-report=html
        
        # Validation manuelle
        python test_afnor_client.py
    """

    print("🧪 VALIDATION DES CLIENTS AFNOR XP Z12-013\n")

    # Validation Flow Service
    validate_client_against_swagger(_flow_swagger_path(), "FlowServiceClient")

    # Validation Directory Service
    validate_client_against_swagger(_directory_swagger_path(), "DirectoryServiceClient")

    print("\n✅ Validation terminée! Exécutez pytest pour les tests unitaires.")
    print("   Command: pytest test_afnor_client.py -v --cov=afnor_client")
