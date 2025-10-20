"""
Guide d'intégration complète et tests End-to-End
pour les API AFNOR XP Z12-013

Ce fichier contient:
1. Configuration centralisée
2. Tests d'intégration E2E
3. Exemples de scénarios réels
4. Utilitaires de validation
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv

from facture_electronique.afnor_client.client import FlowServiceClient, DirectoryServiceClient

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================


@dataclass
class AFNORConfig:
    """Configuration centralisée pour les clients AFNOR"""

    # URLs des services
    flow_service_url: str
    directory_service_url: str
    oauth_token_url: str

    # Credentials OAuth2
    client_id: str
    client_secret: str

    # Configuration optionnelle
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1

    @classmethod
    def from_env(cls) -> "AFNORConfig":
        """Charge la configuration depuis les variables d'environnement"""
        return cls(
            flow_service_url=os.getenv(
                "AFNOR_FLOW_SERVICE_URL", "https://api.pdp.com/flow-service"
            ),
            directory_service_url=os.getenv(
                "AFNOR_DIRECTORY_SERVICE_URL", "https://api.pdp.com/directory-service"
            ),
            oauth_token_url=os.getenv("AFNOR_OAUTH_TOKEN_URL", "https://auth.pdp.com/oauth/token"),
            client_id=os.getenv("AFNOR_CLIENT_ID", ""),
            client_secret=os.getenv("AFNOR_CLIENT_SECRET", ""),
            request_timeout=int(os.getenv("AFNOR_TIMEOUT", "30")),
            max_retries=int(os.getenv("AFNOR_MAX_RETRIES", "3")),
        )

    @classmethod
    def from_file(cls, config_path: str) -> "AFNORConfig":
        """Charge la configuration depuis un fichier JSON"""
        with open(config_path, "r") as f:
            config_data = json.load(f)
        return cls(**config_data)

    def save_to_file(self, config_path: str):
        """Sauvegarde la configuration dans un fichier JSON"""
        with open(config_path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def validate(self) -> List[str]:
        """Valide la configuration et retourne les erreurs"""
        errors = []

        if not self.flow_service_url:
            errors.append("flow_service_url est requis")
        if not self.directory_service_url:
            errors.append("directory_service_url est requis")
        if not self.oauth_token_url:
            errors.append("oauth_token_url est requis")
        if not self.client_id:
            errors.append("client_id est requis")
        if not self.client_secret:
            errors.append("client_secret est requis")

        return errors


class FlowSyntax(Enum):
    """Syntaxes de flux supportées"""

    CII = "CII"
    UBL = "UBL"
    FACTUR_X = "Factur-X"
    CDAR = "CDAR"
    FRR = "FRR"


class FlowProfile(Enum):
    """Profils de flux supportés"""

    BASIC = "Basic"
    CIUS = "CIUS"
    EXTENDED_CTC_FR = "Extended-CTC-FR"


class FlowType(Enum):
    """Types de flux"""

    CUSTOMER_INVOICE = "CustomerInvoice"
    SUPPLIER_INVOICE = "SupplierInvoice"
    CUSTOMER_INVOICE_LC = "CustomerInvoiceLC"
    SUPPLIER_INVOICE_LC = "SupplierInvoiceLC"
    TRANSACTION_REPORT = "TransactionReport"
    PAYMENT_REPORT = "PaymentReport"


# ============================================================================
# UTILITAIRES
# ============================================================================


class InvoiceValidator:
    """Validateur de factures selon les formats du socle"""

    @staticmethod
    def validate_xml_structure(xml_content: str) -> Dict[str, Any]:
        """Valide la structure XML basique"""
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(xml_content)
            return {
                "valid": True,
                "root_tag": root.tag,
                "namespaces": list(root.nsmap.values()) if hasattr(root, "nsmap") else [],
            }
        except ET.ParseError as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def detect_syntax(xml_content: str) -> Optional[str]:
        """Détecte automatiquement la syntaxe du flux"""
        if "CrossIndustryInvoice" in xml_content:
            return FlowSyntax.CII.value
        elif "Invoice" in xml_content and "urn:oasis:names" in xml_content:
            return FlowSyntax.UBL.value
        elif "CrossDomainAcknowledgement" in xml_content:
            return FlowSyntax.CDAR.value
        return None

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Calcule le SHA256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class TestDataGenerator:
    """Générateur de données de test"""

    @staticmethod
    def generate_cii_invoice(
        invoice_number: str = "INV-2025-001",
        issue_date: str = None,
        seller_name: str = "Test Seller",
        buyer_name: str = "Test Buyer",
        amount: float = 1000.00,
    ) -> str:
        """Génère une facture CII minimale de test"""
        if not issue_date:
            issue_date = datetime.now().strftime("%Y%m%d")

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
    xmlns:qdt="urn:un:unece:uncefact:data:standard:QualifiedDataType:100"
    xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
    xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:ExchangedDocumentContext>
        <ram:GuidelineSpecifiedDocumentContextParameter>
            <ram:ID>urn:cen.eu:en16931:2017</ram:ID>
        </ram:GuidelineSpecifiedDocumentContextParameter>
    </rsm:ExchangedDocumentContext>
    <rsm:ExchangedDocument>
        <ram:ID>{invoice_number}</ram:ID>
        <ram:TypeCode>380</ram:TypeCode>
        <ram:IssueDateTime>
            <udt:DateTimeString format="102">{issue_date}</udt:DateTimeString>
        </ram:IssueDateTime>
    </rsm:ExchangedDocument>
    <rsm:SupplyChainTradeTransaction>
        <ram:ApplicableHeaderTradeAgreement>
            <ram:SellerTradeParty>
                <ram:Name>{seller_name}</ram:Name>
            </ram:SellerTradeParty>
            <ram:BuyerTradeParty>
                <ram:Name>{buyer_name}</ram:Name>
            </ram:BuyerTradeParty>
        </ram:ApplicableHeaderTradeAgreement>
        <ram:ApplicableHeaderTradeSettlement>
            <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
            <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
                <ram:TaxBasisTotalAmount>{amount:.2f}</ram:TaxBasisTotalAmount>
                <ram:GrandTotalAmount>{amount:.2f}</ram:GrandTotalAmount>
                <ram:DuePayableAmount>{amount:.2f}</ram:DuePayableAmount>
            </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        </ram:ApplicableHeaderTradeSettlement>
    </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>"""

    @staticmethod
    def generate_cdar_lifecycle(
        flow_id: str, status: str = "AP", reason: str = "Invoice accepted"
    ) -> str:
        """Génère un message de cycle de vie CDAR de test"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossDomainAcknowledgement xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossDomainAcknowledgement:1"
    xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
    xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
    <rsm:AcknowledgementDocument>
        <ram:ID>{flow_id}</ram:ID>
        <ram:StatusCode>{status}</ram:StatusCode>
        <ram:Remarks>
            <udt:Content>{reason}</udt:Content>
        </ram:Remarks>
    </rsm:AcknowledgementDocument>
</rsm:CrossDomainAcknowledgement>"""


# ============================================================================
# TESTS D'INTÉGRATION END-TO-END
# ============================================================================


class IntegrationTestSuite:
    """Suite de tests d'intégration complète"""

    def __init__(self, config: AFNORConfig):
        """
        Initialise la suite de tests

        Args:
            config: Configuration AFNOR
        """

        self.config = config
        self.flow_client = FlowServiceClient(
            base_url=config.flow_service_url,
            token_url=config.oauth_token_url,
            client_id=config.client_id,
            client_secret=config.client_secret,
        )
        self.directory_client = DirectoryServiceClient(
            base_url=config.directory_service_url,
            token_url=config.oauth_token_url,
            client_id=config.client_id,
            client_secret=config.client_secret,
        )
        self.test_results = []

    def run_test(self, test_name: str, test_func):
        """Exécute un test et enregistre le résultat"""
        print(f"\n{'=' * 80}")
        print(f"🧪 Test: {test_name}")
        print(f"{'=' * 80}")

        start_time = time.time()
        try:
            test_func()
            duration = time.time() - start_time
            result = {
                "test": test_name,
                "status": "PASSED",
                "duration": f"{duration:.2f}s",
                "timestamp": datetime.now().isoformat(),
            }
            print(f"✅ PASSED ({duration:.2f}s)")
        except Exception as e:
            duration = time.time() - start_time
            result = {
                "test": test_name,
                "status": "FAILED",
                "error": str(e),
                "duration": f"{duration:.2f}s",
                "timestamp": datetime.now().isoformat(),
            }
            print(f"❌ FAILED: {e}")

        self.test_results.append(result)
        return result

    def test_01_healthcheck_services(self):
        """Test 1: Vérification de la disponibilité des services"""
        print("Vérification Flow Service...")
        assert self.flow_client.healthcheck(), "Flow Service non disponible"
        print("✓ Flow Service OK")

        print("Vérification Directory Service...")
        assert self.directory_client.healthcheck(), "Directory Service non disponible"
        print("✓ Directory Service OK")

    def test_02_submit_supplier_invoice(self):
        """Test 2: Soumission d'une facture fournisseur"""
        # Créer une facture de test
        invoice_xml = TestDataGenerator.generate_cii_invoice()

        # Sauvegarder temporairement
        test_file = Path("test_invoice.xml")
        test_file.write_text(invoice_xml)

        try:
            result = self.flow_client.submit_flow(
                file_path=str(test_file),
                flow_name="Test Supplier Invoice",
                flow_syntax=FlowSyntax.CII.value,
                flow_profile=FlowProfile.CIUS.value,
                tracking_id=f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            )

            print("✓ Facture soumise avec succès")
            print(f"  - Flow ID: {result['flowId']}")
            print(f"  - Tracking ID: {result.get('trackingId')}")
            print(f"  - SHA256: {result.get('sha256')[:16]}...")

            # Stocker le flow_id pour les tests suivants
            self.last_flow_id = result["flowId"]

        finally:
            test_file.unlink(missing_ok=True)

    def test_03_search_flows_by_date(self):
        """Test 3: Recherche de flux par date"""
        updated_after = datetime.now() - timedelta(hours=1)

        result = self.flow_client.search_flows(
            updated_after=updated_after, flow_type=[FlowType.SUPPLIER_INVOICE.value], limit=10
        )

        print("✓ Recherche effectuée")
        print(f"  - Total trouvé: {result['total']}")
        print(f"  - Résultats retournés: {len(result['results'])}")

        if result["results"]:
            first = result["results"][0]
            print(f"  - Premier flux: {first.get('flowId')}")
            print(f"    Type: {first.get('flowType')}")
            print(f"    Statut: {first.get('acknowledgement', {}).get('status')}")

    def test_04_download_flow(self):
        """Test 4: Téléchargement d'un flux"""
        if not hasattr(self, "last_flow_id"):
            print("⚠️  Pas de flow_id disponible, test ignoré")
            return

        output_file = Path("downloaded_invoice.xml")

        try:
            content = self.flow_client.download_flow(
                flow_id=self.last_flow_id, doc_type="Original", output_path=str(output_file)
            )

            print("✓ Flux téléchargé")
            print(f"  - Taille: {len(content)} bytes")
            print(f"  - Fichier: {output_file}")

            # Vérifier que le fichier est valide XML
            validation = InvoiceValidator.validate_xml_structure(content.decode("utf-8"))
            assert validation["valid"], "XML invalide"
            print("  - Validation XML: OK")

        finally:
            output_file.unlink(missing_ok=True)

    def test_05_search_company_by_siren(self):
        """Test 5: Recherche d'une entreprise par SIREN"""
        # Utiliser un SIREN de test (ou adapter selon votre environnement)
        test_siren = "702042755"

        try:
            result = self.directory_client.get_siren(test_siren)

            print("✓ Entreprise trouvée")
            print(f"  - SIREN: {result.get('siren')}")
            print(f"  - Raison sociale: {result.get('businessName')}")
            print(f"  - Type: {result.get('entityType')}")
            print(f"  - Statut: {result.get('administrativeStatus')}")

        except Exception as e:
            if "404" in str(e):
                print(f"ℹ️  SIREN {test_siren} non trouvé (normal en test)")
            else:
                raise

    def test_06_search_establishments(self):
        """Test 6: Recherche d'établissements"""
        result = self.directory_client.search_siret(
            filters={"administrativeStatus": {"op": "strict", "value": "A"}}, limit=5
        )

        print("✓ Recherche effectuée")
        print(f"  - Total: {result.get('total_number_results', 0)}")
        print(f"  - Résultats: {len(result.get('results', []))}")

        for establishment in result.get("results", [])[:3]:
            print(f"  - {establishment.get('siret')}: {establishment.get('name')}")

    def test_07_complete_flow_lifecycle(self):
        """Test 7: Cycle complet de facture"""
        print("Étape 1: Soumission de la facture...")
        invoice_xml = TestDataGenerator.generate_cii_invoice(
            invoice_number=f"INV-E2E-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        test_file = Path("test_lifecycle.xml")
        test_file.write_text(invoice_xml)

        try:
            # 1. Soumettre la facture
            submit_result = self.flow_client.submit_flow(
                file_path=str(test_file),
                flow_name="Lifecycle Test Invoice",
                flow_syntax=FlowSyntax.CII.value,
                flow_profile=FlowProfile.CIUS.value,
            )
            flow_id = submit_result["flowId"]
            print(f"  ✓ Facture soumise: {flow_id}")

            # 2. Attendre un peu
            time.sleep(2)

            # 3. Rechercher la facture
            print("Étape 2: Recherche de la facture...")
            search_result = self.flow_client.search_flows(flow_id=flow_id)
            assert search_result["total"] >= 1, "Facture non trouvée"
            print("  ✓ Facture trouvée")

            # 4. Télécharger la facture
            print("Étape 3: Téléchargement...")
            content = self.flow_client.download_flow(flow_id)
            assert len(content) > 0, "Contenu vide"
            print(f"  ✓ Téléchargement OK ({len(content)} bytes)")

            print("✅ Cycle complet réussi!")

        finally:
            test_file.unlink(missing_ok=True)

    def run_all_tests(self):
        """Exécute tous les tests de la suite"""
        print("\n" + "=" * 80)
        print("🚀 SUITE DE TESTS D'INTÉGRATION AFNOR XP Z12-013")
        print("=" * 80)

        tests = [
            ("Healthcheck Services", self.test_01_healthcheck_services),
            ("Submit Supplier Invoice", self.test_02_submit_supplier_invoice),
            ("Search Flows by Date", self.test_03_search_flows_by_date),
            ("Download Flow", self.test_04_download_flow),
            ("Search Company by SIREN", self.test_05_search_company_by_siren),
            ("Search Establishments", self.test_06_search_establishments),
            ("Complete Flow Lifecycle", self.test_07_complete_flow_lifecycle),
        ]

        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        self.print_summary()

    def print_summary(self):
        """Affiche le résumé des tests"""
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 80)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASSED")
        failed = total - passed

        print(f"\nTotal: {total} tests")
        print(f"✅ Réussis: {passed}")
        print(f"❌ Échoués: {failed}")
        print(f"Taux de réussite: {(passed / total * 100):.1f}%")

        if failed > 0:
            print("\n❌ Tests échoués:")
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(f"  - {result['test']}: {result.get('error')}")

        # Sauvegarder les résultats
        results_file = Path(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Résultats sauvegardés dans: {results_file}")


# ============================================================================
# EXEMPLES DE SCÉNARIOS RÉELS
# ============================================================================


class UseCaseExamples:
    """Exemples de cas d'usage réels"""

    def __init__(self, config: AFNORConfig):
        self.flow_client = FlowServiceClient(
            base_url=config.flow_service_url,
            token_url=config.oauth_token_url,
            client_id=config.client_id,
            client_secret=config.client_secret,
        )
        self.directory_client = DirectoryServiceClient(
            base_url=config.directory_service_url,
            token_url=config.oauth_token_url,
            client_id=config.client_id,
            client_secret=config.client_secret,
        )

    def scenario_edi_to_pdp(self, invoice_file: str):
        """
        Scénario 1: OD (solution EDI) envoie une facture à la PDP
        """
        print("\n📋 Scénario: Transmission EDI → PDP")
        print("-" * 60)

        # 1. Valider le fichier
        print("1. Validation du fichier...")
        with open(invoice_file, "r") as f:
            content = f.read()

        validation = InvoiceValidator.validate_xml_structure(content)
        if not validation["valid"]:
            raise ValueError(f"Fichier invalide: {validation['error']}")

        syntax = InvoiceValidator.detect_syntax(content)
        print(f"   ✓ Syntaxe détectée: {syntax}")

        # 2. Soumettre à la PDP
        print("2. Transmission à la PDP...")
        result = self.flow_client.submit_flow(
            file_path=invoice_file,
            flow_name=Path(invoice_file).stem,
            flow_syntax=syntax,
            flow_profile=FlowProfile.CIUS.value,
            tracking_id=f"EDI-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )

        print(f"   ✓ Flow ID: {result['flowId']}")
        print(f"   ✓ Tracking ID: {result['trackingId']}")

        return result

    def scenario_accountant_access(self, company_siren: str):
        """
        Scénario 2: Expert-comptable consulte les factures de ses clients
        """
        print("\n📋 Scénario: Consultation expert-comptable")
        print("-" * 60)

        # 1. Vérifier l'entreprise
        print(f"1. Vérification de l'entreprise {company_siren}...")
        company = self.directory_client.get_siren(company_siren)
        print(f"   ✓ {company.get('businessName')}")

        # 2. Récupérer les factures récentes
        print("2. Récupération des factures...")
        since = datetime.now() - timedelta(days=30)

        # Factures reçues
        received = self.flow_client.search_flows(
            updated_after=since, flow_type=[FlowType.CUSTOMER_INVOICE.value], flow_direction=["In"]
        )
        print(f"   ✓ Factures reçues: {received['total']}")

        # Factures émises
        sent = self.flow_client.search_flows(
            updated_after=since, flow_type=[FlowType.SUPPLIER_INVOICE.value], flow_direction=["Out"]
        )
        print(f"   ✓ Factures émises: {sent['total']}")

        return {"company": company, "invoices_received": received, "invoices_sent": sent}

    def scenario_create_routing_structure(self, siret: str):
        """
        Scénario 3: Création d'une structure d'adressage complète
        """
        print("\n📋 Scénario: Création structure d'adressage")
        print("-" * 60)

        # 1. Créer un code routage
        print("1. Création du code routage...")
        routing_code = self.directory_client.create_routing_code(
            siret=siret,
            routing_identifier="COMPTA-001",
            routing_code_name="Service Comptabilité",
            facility_nature="Private",
            administrative_status="A",
            routing_identifier_type="0224",
        )
        print(f"   ✓ Code routage créé: {routing_code['routingIdentifier']}")

        # 2. Créer une ligne d'annuaire
        print("2. Création de la ligne d'annuaire...")
        directory_line = self.directory_client.create_directory_line(
            siren=siret[:9],
            siret=siret,
            routing_identifier="COMPTA-001",
            platform_registration_number="0145",
            date_from=datetime.now().strftime("%Y-%m-%d"),
        )
        print(f"   ✓ Ligne d'annuaire créée: {directory_line['addressingIdentifier']}")

        return {"routing_code": routing_code, "directory_line": directory_line}


# ============================================================================
# CLI ET EXÉCUTION
# ============================================================================


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Tests d'intégration et validation AFNOR XP Z12-013"
    )
    parser.add_argument("--config", type=str, help="Chemin vers le fichier de configuration JSON")
    parser.add_argument(
        "--env",
        action="store_true",
        help="Charger la configuration depuis les variables d'environnement",
    )
    parser.add_argument(
        "--test",
        choices=["all", "flow", "directory", "e2e"],
        default="all",
        help="Type de tests à exécuter",
    )
    parser.add_argument(
        "--scenario",
        choices=["edi", "accountant", "routing"],
        help="Exécuter un scénario spécifique",
    )
    parser.add_argument(
        "--create-config", type=str, help="Créer un fichier de configuration template"
    )

    args = parser.parse_args()

    # Créer un template de configuration
    if args.create_config:
        template = AFNORConfig(
            flow_service_url="https://api.pdp.com/flow-service",
            directory_service_url="https://api.pdp.com/directory-service",
            oauth_token_url="https://auth.pdp.com/oauth/token",
            client_id="YOUR_CLIENT_ID",
            client_secret="YOUR_CLIENT_SECRET",
        )
        template.save_to_file(args.create_config)
        print(f"✅ Configuration template créée: {args.create_config}")
        print("⚠️  N'oubliez pas de remplacer les valeurs par vos credentials!")
        return

    # Charger la configuration
    if args.config:
        config = AFNORConfig.from_file(args.config)
    elif args.env:
        config = AFNORConfig.from_env()
    else:
        print("❌ Erreur: Spécifiez --config ou --env")
        parser.print_help()
        return

    # Valider la configuration
    errors = config.validate()
    if errors:
        print("❌ Configuration invalide:")
        for error in errors:
            print(f"  - {error}")
        return

    print("✅ Configuration chargée et validée")

    # Exécuter les tests ou scénarios
    if args.scenario:
        examples = UseCaseExamples(config)

        if args.scenario == "edi":
            # Exemple EDI
            print("\n⚠️  Créer un fichier invoice.xml pour tester ce scénario")
            invoice_file = "invoice.xml"
            if Path(invoice_file).exists():
                examples.scenario_edi_to_pdp(invoice_file)
            else:
                # Créer un exemple
                invoice_xml = TestDataGenerator.generate_cii_invoice()
                Path(invoice_file).write_text(invoice_xml)
                print(f"✅ Fichier d'exemple créé: {invoice_file}")
                examples.scenario_edi_to_pdp(invoice_file)

        elif args.scenario == "accountant":
            # Demander le SIREN
            siren = input("Entrez le SIREN de l'entreprise: ")
            examples.scenario_accountant_access(siren)

        elif args.scenario == "routing":
            # Demander le SIRET
            siret = input("Entrez le SIRET: ")
            examples.scenario_create_routing_structure(siret)

    else:
        # Exécuter les tests d'intégration
        suite = IntegrationTestSuite(config)
        suite.run_all_tests()


if __name__ == "__main__":
    main()

"""


10. RÉFÉRENCE SWAGGER
────────────────────────────────────────────────────────────────────────────

Flow Service API v1.0.2:
    Endpoints:
        POST   /v1/flows              - Soumettre un flux
        POST   /v1/flows/search       - Rechercher des flux
        GET    /v1/flows/{flowId}     - Télécharger un flux
        GET    /v1/healthcheck        - Vérifier le service

Directory Service API v1.0.0:
    Endpoints:
        POST   /siren/search          - Rechercher des SIREN
        GET    /siren/code-insee:{siren}
        POST   /siret/search          - Rechercher des SIRET
        GET    /siret/code-insee:{siret}
        POST   /routing-code          - Créer un code routage
        POST   /routing-code/search   - Rechercher codes routage
        POST   /directory-line        - Créer ligne d'annuaire
        POST   /directory-line/search - Rechercher lignes
        DELETE /directory-line/id-instance:{id}
        GET    /healthcheck           - Vérifier le service

11. FORMATS SUPPORTÉS
────────────────────────────────────────────────────────────────────────────

Syntaxes de factures:
    - CII (UN/CEFACT Cross Industry Invoice)
    - UBL (Universal Business Language)
    - Factur-X (PDF/A-3 avec XML embarqué)
    - CDAR (Cycle de vie)
    - FRR (E-reporting)

Profils:
    - Basic
    - CIUS (EN16931 CIUS France)
    - Extended-CTC-FR (Extension France)

"""
