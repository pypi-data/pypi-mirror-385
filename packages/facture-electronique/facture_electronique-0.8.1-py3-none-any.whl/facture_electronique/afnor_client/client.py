"""
Client HTTP Python pour les API AFNOR XP Z12-013
- Flow Service API (gestion des flux de facturation)
- Directory Service API (gestion de l'annuaire)

Conforme aux spécifications AFNOR XP Z12-013 (Mai 2025)
"""

from urllib.error import HTTPError

import requests
import hashlib
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path
import json


class AFNORAuthError(Exception):
    """Erreur d'authentification"""

    pass


class AFNORAPIError(Exception):
    """Erreur API générique"""

    def __init__(self, status_code: int, error_code: str, error_message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(f"[{status_code}] {error_code}: {error_message}")


class AFNORBaseClient:
    """Client de base avec authentification OAuth2"""

    def __init__(self, base_url: str, token_url: str, client_id: str, client_secret: str):
        """
        Initialise le client de base

        Args:
                base_url: URL de base de l'API (ex: https://api.company.com)
                token_url: URL pour obtenir le token OAuth2
                client_id: Identifiant client OAuth2
                client_secret: Secret client OAuth2
        """
        self.base_url = base_url.rstrip("/")
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    def _get_access_token(self) -> str:
        """Récupère un token d'accès via OAuth2"""
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token

        response = requests.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )

        if response.status_code != 200:
            raise AFNORAuthError(f"Échec d'authentification: {response.status_code}")

        token_data = response.json()
        self._access_token = token_data["access_token"]

        # Calcul de l'expiration (par défaut 1h si non spécifié)
        expires_in = token_data.get("expires_in", 3600)
        self._token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)

        return self._access_token

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Construit les headers avec le token Bearer"""
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Gère la réponse et les erreurs"""
        if response.status_code in [200, 201, 202, 204, 206]:
            if response.status_code == 204:
                return None
            return response.json() if response.content else None

        # Gestion des erreurs
        try:
            error_data = response.json()
            error_code = error_data.get("errorCode", "UNKNOWN")
            error_message = error_data.get("errorMessage", "Erreur inconnue")
        except HTTPError:
            error_code = "HTTP_ERROR"
            error_message = response.text or f"Erreur HTTP {response.status_code}"

        raise AFNORAPIError(response.status_code, error_code, error_message)


class FlowServiceClient(AFNORBaseClient):
    """Client pour l'API Flow Service (gestion des flux de facturation)"""

    def __init__(self, base_url: str, token_url: str, client_id: str, client_secret: str):
        """
        Initialise le client Flow Service

        Args:
                base_url: URL de base (ex: https://api.flow.company.com/flow-service)
                token_url: URL du service de tokens OAuth2
                client_id: Identifiant client
                client_secret: Secret client
        """
        super().__init__(base_url, token_url, client_id, client_secret)

    def healthcheck(self) -> bool:
        """Vérifie si le service API est opérationnel"""
        try:
            response = requests.get(f"{self.base_url}/v1/healthcheck", headers=self._get_headers())
            return response.status_code == 200
        except HTTPError:
            return False

    def submit_flow(
        self,
        file_path: str,
        flow_name: str,
        flow_syntax: str,
        flow_profile: Optional[str] = None,
        tracking_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Soumet un nouveau flux (facture, cycle de vie, e-reporting)

        Args:
                file_path: Chemin vers le fichier à envoyer
                flow_name: Nom du flux
                flow_syntax: Syntaxe du flux (CII, UBL, Factur-X, CDAR, FRR)
                flow_profile: Profil du flux (Basic, CIUS, Extended-CTC-FR)
                tracking_id: Identifiant de suivi externe (optionnel)
                request_id: Identifiant de requête pour corrélation (optionnel)

        Returns:
                Dictionnaire avec flowId, trackingId, name, flowSyntax, flowProfile, sha256
        """
        # Calcul du SHA256
        with open(file_path, "rb") as f:
            file_content = f.read()
            sha256 = hashlib.sha256(file_content).hexdigest()

        # Construction du flowInfo
        flow_info = {"name": flow_name, "flowSyntax": flow_syntax, "sha256": sha256}

        if flow_profile:
            flow_info["flowProfile"] = flow_profile
        if tracking_id:
            flow_info["trackingId"] = tracking_id

        # Headers
        headers = {"Authorization": f"Bearer {self._get_access_token()}"}
        if request_id:
            headers["Request-Id"] = request_id

        # Envoi multipart
        files = {
            "file": (Path(file_path).name, open(file_path, "rb"), "application/octet-stream"),
            "flowInfo": (None, json.dumps(flow_info), "application/json"),
        }

        response = requests.post(f"{self.base_url}/v1/flows", headers=headers, files=files)

        return self._handle_response(response)

    def search_flows(
        self,
        updated_after: Optional[datetime] = None,
        updated_before: Optional[datetime] = None,
        flow_type: Optional[List[str]] = None,
        flow_direction: Optional[List[str]] = None,
        tracking_id: Optional[str] = None,
        flow_id: Optional[str] = None,
        ack_status: Optional[str] = None,
        offset: int = 0,
        limit: int = 25,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Recherche des flux selon des critères

        Args:
                updated_after: Date de mise à jour minimale
                updated_before: Date de mise à jour maximale
                flow_type: Types de flux (CustomerInvoice, SupplierInvoice, CustomerInvoiceLC, etc.)
                flow_direction: Direction des flux (In, Out)
                tracking_id: Identifiant de suivi
                flow_id: Identifiant de flux spécifique
                ack_status: Statut d'acquittement (Pending, Ok, Error)
                offset: Décalage pour la pagination
                limit: Nombre maximum de résultats (max 100)
                request_id: Identifiant de requête

        Returns:
                Dictionnaire avec total, offset, limit, filter et results
        """
        where = {}

        if flow_id:
            where["flowId"] = flow_id
        else:
            if updated_after:
                where["updatedAfter"] = updated_after.isoformat()
            if updated_before:
                where["updatedBefore"] = updated_before.isoformat()
            if flow_type:
                where["flowType"] = flow_type
            if flow_direction:
                where["flowDirection"] = flow_direction
            if tracking_id:
                where["trackingId"] = tracking_id
            if ack_status:
                where["ackStatus"] = ack_status

        body = {"offset": offset, "limit": min(limit, 100), "where": where}

        headers = self._get_headers()
        if request_id:
            headers["Request-Id"] = request_id

        response = requests.post(f"{self.base_url}/v1/flows/search", headers=headers, json=body)

        return self._handle_response(response)

    def download_flow(
        self,
        flow_id: str,
        doc_type: str = "Original",
        doc_index: int = 1,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Télécharge un flux

        Args:
                flow_id: Identifiant du flux
                doc_type: Type de document (Original, Converted, ReadableView, Attachment)
                doc_index: Index du document si plusieurs attachements
                output_path: Chemin de sauvegarde optionnel

        Returns:
                Contenu binaire du fichier
        """
        params = {"docType": doc_type, "docIndex": doc_index}

        response = requests.get(
            f"{self.base_url}/v1/flows/{flow_id}", headers=self._get_headers(), params=params
        )

        if response.status_code != 200:
            self._handle_response(response)

        content = response.content

        if output_path:
            with open(output_path, "wb") as f:
                f.write(content)

        return content


class DirectoryServiceClient(AFNORBaseClient):
    """Client pour l'API Directory Service (gestion de l'annuaire)"""

    def __init__(self, base_url: str, token_url: str, client_id: str, client_secret: str):
        """
        Initialise le client Directory Service

        Args:
                base_url: URL de base (ex: https://api.directory.company.com/directory-service)
                token_url: URL du service de tokens OAuth2
                client_id: Identifiant client
                client_secret: Secret client
        """
        super().__init__(base_url, token_url, client_id, client_secret)

    def healthcheck(self) -> bool:
        """Vérifie si le service API est opérationnel"""
        try:
            response = requests.get(f"{self.base_url}/healthcheck", headers=self._get_headers())
            return response.status_code == 200
        except HTTPError:
            return False

    # === SIREN ===

    def search_siren(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, str]]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 50,
        ignore: int = 0,
    ) -> Dict[str, Any]:
        """Recherche multicritère d'entreprises (unités légales)"""
        body = {"limit": limit, "ignore": ignore}
        if filters:
            body["filters"] = filters
        if sorting:
            body["sorting"] = sorting
        if fields:
            body["fields"] = fields

        response = requests.post(
            f"{self.base_url}/siren/search", headers=self._get_headers(), json=body
        )
        return self._handle_response(response)

    def get_siren(
        self, siren: str, observation_date: Optional[str] = None, fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Consulte une entreprise par son numéro SIREN"""
        params = {}
        if observation_date:
            params["observationDate"] = observation_date
        if fields:
            params["champs"] = ",".join(fields)

        response = requests.get(
            f"{self.base_url}/siren/code-insee:{siren}", headers=self._get_headers(), params=params
        )
        return self._handle_response(response)

    def get_siren_by_instance(
        self, id_instance: int, fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Consulte une entreprise par son id-instance"""
        params = {}
        if fields:
            params["champs"] = ",".join(fields)

        response = requests.get(
            f"{self.base_url}/siren/id-instance:{id_instance}",
            headers=self._get_headers(),
            params=params,
        )
        return self._handle_response(response)

    # === SIRET ===

    def search_siret(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, str]]] = None,
        fields: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
        limit: int = 50,
        ignore: int = 0,
    ) -> Dict[str, Any]:
        """Recherche multicritère d'établissements"""
        body = {"limit": limit, "ignore": ignore}
        if filters:
            body["filters"] = filters
        if sorting:
            body["sorting"] = sorting
        if fields:
            body["champs"] = fields
        if include:
            body["inclure"] = include

        response = requests.post(
            f"{self.base_url}/siret/search", headers=self._get_headers(), json=body
        )
        return self._handle_response(response)

    def get_siret(
        self,
        siret: str,
        observation_date: Optional[str] = None,
        fields: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Consulte un établissement par son numéro SIRET"""
        params = {}
        if observation_date:
            params["observationDate"] = observation_date
        if fields:
            params["fields"] = ",".join(fields)
        if include:
            params["include"] = ",".join(include)

        response = requests.get(
            f"{self.base_url}/siret/code-insee:{siret}", headers=self._get_headers(), params=params
        )
        return self._handle_response(response)

    # === CODE ROUTAGE ===

    def search_routing_code(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, str]]] = None,
        fields: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
        limit: int = 50,
        ignore: int = 0,
    ) -> Dict[str, Any]:
        """Recherche de codes routage"""
        body = {"limit": limit, "ignore": ignore}
        if filters:
            body["filters"] = filters
        if sorting:
            body["sorting"] = sorting
        if fields:
            body["champs"] = fields
        if include:
            body["inclure"] = include

        response = requests.post(
            f"{self.base_url}/routing-code/search", headers=self._get_headers(), json=body
        )
        return self._handle_response(response)

    def create_routing_code(
        self,
        siret: str,
        routing_identifier: str,
        routing_code_name: str,
        facility_nature: str,
        administrative_status: str,
        routing_identifier_type: Optional[str] = None,
        manages_legal_commitment: Optional[bool] = None,
        address: Optional[Dict[str, str]] = None,
        ppf_affiliations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Crée un code routage"""
        body = {
            "siret": siret,
            "routingIdentifier": routing_identifier,
            "routingCodeName": routing_code_name,
            "facilityNature": facility_nature,
            "administrativeStatus": administrative_status,
        }

        if routing_identifier_type:
            body["routingIdentifierType"] = routing_identifier_type
        if manages_legal_commitment is not None:
            body["managesLegalCommitmentCode"] = manages_legal_commitment
        if address:
            body["address"] = address

        headers = self._get_headers()
        if ppf_affiliations:
            headers["PPF-affiliations"] = ", ".join(ppf_affiliations)

        response = requests.post(f"{self.base_url}/routing-code", headers=headers, json=body)
        return self._handle_response(response)

    # === LIGNE D'ANNUAIRE ===

    def search_directory_line(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, str]]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 50,
        ignore: int = 0,
    ) -> Dict[str, Any]:
        """Recherche de lignes d'annuaire"""
        body = {"limit": limit, "ignore": ignore}
        if filters:
            body["filters"] = filters
        if sorting:
            body["sorting"] = sorting
        if fields:
            body["fields"] = fields

        response = requests.post(
            f"{self.base_url}/directory-line/search", headers=self._get_headers(), json=body
        )
        return self._handle_response(response)

    def get_directory_line(
        self,
        addressing_identifier: str,
        observation_date: Optional[str] = None,
        fields: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Consulte une ligne d'annuaire par son identifiant d'adressage"""
        params = {}
        if observation_date:
            params["observationDate"] = observation_date
        if fields:
            params["champs"] = ",".join(fields)
        if include:
            params["include"] = ",".join(include)

        response = requests.get(
            f"{self.base_url}/directory-line/code:{addressing_identifier}",
            headers=self._get_headers(),
            params=params,
        )
        return self._handle_response(response)

    def create_directory_line(
        self,
        siren: str,
        platform_registration_number: str,
        date_from: str,
        siret: Optional[str] = None,
        routing_identifier: Optional[str] = None,
        addressing_suffix: Optional[str] = None,
        date_to: Optional[str] = None,
        ppf_affiliations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Crée une ligne d'annuaire"""
        body = {
            "period": {"dateFrom": date_from},
            "addressingInformation": {
                "siren": siren,
                "platformRegistrationNumber": platform_registration_number,
            },
        }

        if date_to:
            body["period"]["dateTo"] = date_to
        if siret:
            body["addressingInformation"]["siret"] = siret
        if routing_identifier:
            body["addressingInformation"]["routingIdentifier"] = routing_identifier
        if addressing_suffix:
            body["addressingInformation"]["addressingSuffix"] = addressing_suffix

        headers = self._get_headers()
        if ppf_affiliations:
            headers["PPF-affiliations"] = ", ".join(ppf_affiliations)

        response = requests.post(f"{self.base_url}/directory-line", headers=headers, json=body)
        return self._handle_response(response)

    def delete_directory_line(
        self, id_instance: int, ppf_affiliations: Optional[List[str]] = None
    ) -> None:
        """Supprime une ligne d'annuaire"""
        headers = self._get_headers()
        if ppf_affiliations:
            headers["PPF-affiliations"] = ", ".join(ppf_affiliations)

        response = requests.delete(
            f"{self.base_url}/directory-line/id-instance:{id_instance}", headers=headers
        )
        return self._handle_response(response)


# === EXEMPLE D'UTILISATION ===

if __name__ == "__main__":
    # Configuration
    FLOW_BASE_URL = "https://api.flow.company.com/flow-service"
    DIRECTORY_BASE_URL = "https://api.directory.company.com/directory-service"
    TOKEN_URL = "https://auth.company.com/oauth/token"
    CLIENT_ID = "votre_client_id"
    CLIENT_SECRET = "votre_client_secret"

    # Exemple Flow Service
    print("=== Flow Service ===")
    flow_client = FlowServiceClient(FLOW_BASE_URL, TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

    # Vérification du service
    if flow_client.healthcheck():
        print("✓ Flow Service opérationnel")

    # Soumission d'une facture
    try:
        result = flow_client.submit_flow(
            file_path="facture.xml",
            flow_name="Facture 2025-001",
            flow_syntax="CII",
            flow_profile="CIUS",
            tracking_id="TRACK-12345",
        )
        print(f"✓ Flux soumis: {result['flowId']}")
        flow_id = result["flowId"]
    except AFNORAPIError as e:
        print(f"✗ Erreur: {e}")

    # Recherche de flux
    try:
        results = flow_client.search_flows(
            flow_type=["SupplierInvoice"], flow_direction=["Out"], ack_status="Ok", limit=10
        )
        print(f"✓ {results['total']} flux trouvés")
    except AFNORAPIError as e:
        print(f"✗ Erreur: {e}")

    # Exemple Directory Service
    print("\n=== Directory Service ===")
    directory_client = DirectoryServiceClient(
        DIRECTORY_BASE_URL, TOKEN_URL, CLIENT_ID, CLIENT_SECRET
    )

    # Vérification du service
    if directory_client.healthcheck():
        print("✓ Directory Service opérationnel")

    # Recherche d'un SIREN
    try:
        result = directory_client.get_siren("702042755")
        print(f"✓ Entreprise trouvée: {result.get('businessName')}")
    except AFNORAPIError as e:
        print(f"✗ Erreur: {e}")

    # Recherche de lignes d'annuaire
    try:
        results = directory_client.search_directory_line(
            filters={"siren": {"op": "contains", "value": "702042"}}, limit=10
        )
        print(f"✓ {results['total_number_results']} lignes d'annuaire trouvées")
    except AFNORAPIError as e:
        print(f"✗ Erreur: {e}")
