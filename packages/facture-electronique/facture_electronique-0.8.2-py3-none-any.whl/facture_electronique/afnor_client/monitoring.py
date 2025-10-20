"""
Utilitaires de monitoring, logging et reporting
pour les clients AFNOR XP Z12-013

Fonctionnalités:
- Logging structuré des appels API
- Métriques de performance
- Génération de rapports
- Surveillance de la santé des services
"""

import logging
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import csv

from facture_electronique.afnor_client.client import DirectoryServiceClient, FlowServiceClient

# ============================================================================
# CONFIGURATION DU LOGGING
# ============================================================================


class AFNORLogger:
    """Logger personnalisé pour les API AFNOR"""

    def __init__(self, name: str = "afnor_client", log_dir: str = "logs"):
        """
        Initialise le logger

        Args:
            name: Nom du logger
            log_dir: Répertoire des logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Configuration du logger principal
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Handler pour fichier JSON structuré
        json_handler = logging.FileHandler(
            self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JSONFormatter())

        # Handler pour fichier texte lisible
        text_handler = logging.FileHandler(
            self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        text_handler.setLevel(logging.DEBUG)
        text_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

        self.logger.addHandler(json_handler)
        self.logger.addHandler(text_handler)
        self.logger.addHandler(console_handler)

    def log_api_call(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_data: Optional[Dict] = None,
        response_data: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        """Log un appel API avec tous les détails"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "success": 200 <= status_code < 300,
        }

        if request_data:
            log_data["request"] = request_data
        if response_data:
            log_data["response"] = response_data
        if error:
            log_data["error"] = error

        level = logging.INFO if log_data["success"] else logging.ERROR
        self.logger.log(level, json.dumps(log_data))

    def log_flow_submission(self, flow_id: str, tracking_id: str, syntax: str):
        """Log la soumission d'un flux"""
        self.logger.info(f"Flow submitted: {flow_id} (tracking: {tracking_id}, syntax: {syntax})")

    def log_search(self, criteria: Dict, results_count: int):
        """Log une recherche"""
        self.logger.info(f"Search executed: {json.dumps(criteria)} - {results_count} results")

    def log_error(self, error_code: str, message: str, context: Dict = None):
        """Log une erreur"""
        error_data = {
            "error_code": error_code,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        if context:
            error_data["context"] = context
        self.logger.error(json.dumps(error_data))


class JSONFormatter(logging.Formatter):
    """Formatter pour logs JSON structurés"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


# ============================================================================
# MÉTRIQUES ET STATISTIQUES
# ============================================================================


@dataclass
class APIMetrics:
    """Métriques d'utilisation des API"""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration: float = 0.0

    # Compteurs par endpoint
    calls_by_endpoint: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Compteurs par code HTTP
    calls_by_status: Dict[int, int] = field(default_factory=lambda: defaultdict(int))

    # Temps de réponse
    response_times: List[float] = field(default_factory=list)

    # Erreurs
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def record_call(
        self, endpoint: str, status_code: int, duration: float, error: Optional[str] = None
    ):
        """Enregistre un appel API"""
        self.total_calls += 1
        self.total_duration += duration
        self.calls_by_endpoint[endpoint] += 1
        self.calls_by_status[status_code] += 1
        self.response_times.append(duration)

        if 200 <= status_code < 300:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
            if error:
                self.errors.append(
                    {
                        "endpoint": endpoint,
                        "status_code": status_code,
                        "error": error,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    def get_average_response_time(self) -> float:
        """Calcule le temps de réponse moyen"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    def get_success_rate(self) -> float:
        """Calcule le taux de succès"""
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100

    def get_percentile(self, percentile: int) -> float:
        """Calcule un percentile des temps de réponse"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": f"{self.get_success_rate():.2f}%",
            "total_duration": f"{self.total_duration:.2f}s",
            "average_response_time": f"{self.get_average_response_time() * 1000:.2f}ms",
            "median_response_time": f"{self.get_percentile(50) * 1000:.2f}ms",
            "p95_response_time": f"{self.get_percentile(95) * 1000:.2f}ms",
            "p99_response_time": f"{self.get_percentile(99) * 1000:.2f}ms",
            "calls_by_endpoint": dict(self.calls_by_endpoint),
            "calls_by_status": {str(k): v for k, v in self.calls_by_status.items()},
            "recent_errors": self.errors[-10:],  # 10 dernières erreurs
        }


# ============================================================================
# MONITORING DES SERVICES
# ============================================================================


class ServiceMonitor:
    """Moniteur de santé des services"""

    def __init__(self, check_interval: int = 60):
        """
        Initialise le moniteur

        Args:
            check_interval: Intervalle de vérification en secondes
        """
        self.check_interval = check_interval
        self.health_history: List[Dict[str, Any]] = []

    def check_service_health(self, service_name: str, healthcheck_func) -> Dict[str, Any]:
        """
        Vérifie la santé d'un service

        Args:
            service_name: Nom du service
            healthcheck_func: Fonction de healthcheck

        Returns:
            Résultat du healthcheck
        """
        start_time = time.time()

        try:
            is_healthy = healthcheck_func()
            duration = time.time() - start_time

            result = {
                "service": service_name,
                "status": "healthy" if is_healthy else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "response_time": f"{duration * 1000:.2f}ms",
            }
        except Exception as e:
            duration = time.time() - start_time
            result = {
                "service": service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "response_time": f"{duration * 1000:.2f}ms",
            }

        self.health_history.append(result)
        return result

    def get_uptime(self, service_name: str, period_hours: int = 24) -> float:
        """
        Calcule l'uptime d'un service sur une période

        Args:
            service_name: Nom du service
            period_hours: Période en heures

        Returns:
            Pourcentage d'uptime
        """
        cutoff = datetime.now() - timedelta(hours=period_hours)

        relevant_checks = [
            h
            for h in self.health_history
            if h["service"] == service_name and datetime.fromisoformat(h["timestamp"]) > cutoff
        ]

        if not relevant_checks:
            return 0.0

        healthy_checks = sum(1 for h in relevant_checks if h["status"] == "healthy")
        return (healthy_checks / len(relevant_checks)) * 100


# ============================================================================
# GÉNÉRATEUR DE RAPPORTS
# ============================================================================


class ReportGenerator:
    """Générateur de rapports d'utilisation"""

    def __init__(self, output_dir: str = "reports"):
        """
        Initialise le générateur

        Args:
            output_dir: Répertoire de sortie des rapports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_metrics_report(self, metrics: APIMetrics, service_name: str = "AFNOR API") -> Path:
        """
        Génère un rapport de métriques en JSON

        Args:
            metrics: Métriques à inclure
            service_name: Nom du service

        Returns:
            Chemin du fichier généré
        """
        report_data = {
            "service": service_name,
            "report_date": datetime.now().isoformat(),
            "metrics": metrics.to_dict(),
        }

        filename = f"metrics_{service_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=2)

        return filepath

    def generate_html_report(self, metrics: APIMetrics, service_name: str = "AFNOR API") -> Path:
        """
        Génère un rapport HTML interactif

        Args:
            metrics: Métriques à inclure
            service_name: Nom du service

        Returns:
            Chemin du fichier généré
        """
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport {service_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            margin-bottom: 10px;
        }}
        .status-ok {{ color: #10b981; }}
        .status-error {{ color: #ef4444; }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background: #f9fafb;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{service_name} - Rapport d'utilisation</h1>
        <p>Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</p>
    </div>
    
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Appels totaux</div>
            <div class="metric-value">{metrics.total_calls}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Taux de succès</div>
            <div class="metric-value status-ok">{metrics.get_success_rate():.1f}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Temps moyen</div>
            <div class="metric-value">{metrics.get_average_response_time() * 1000:.0f}ms</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Erreurs</div>
            <div class="metric-value status-error">{metrics.failed_calls}</div>
        </div>
    </div>
    
    <div class="metric-card">
        <h2>Appels par endpoint</h2>
        <table>
            <thead>
                <tr>
                    <th>Endpoint</th>
                    <th>Nombre d'appels</th>
                </tr>
            </thead>
            <tbody>
                {"".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in sorted(metrics.calls_by_endpoint.items(), key=lambda x: -x[1]))}
            </tbody>
        </table>
    </div>
    
    <div class="metric-card">
        <h2>Codes de statut HTTP</h2>
        <table>
            <thead>
                <tr>
                    <th>Code</th>
                    <th>Nombre</th>
                </tr>
            </thead>
            <tbody>
                {"".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in sorted(metrics.calls_by_status.items()))}
            </tbody>
        </table>
    </div>
    
    <div class="metric-card">
        <h2>Temps de réponse (percentiles)</h2>
        <table>
            <thead>
                <tr>
                    <th>Percentile</th>
                    <th>Temps (ms)</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>P50 (médiane)</td><td>{metrics.get_percentile(50) * 1000:.2f}</td></tr>
                <tr><td>P95</td><td>{metrics.get_percentile(95) * 1000:.2f}</td></tr>
                <tr><td>P99</td><td>{metrics.get_percentile(99) * 1000:.2f}</td></tr>
            </tbody>
        </table>
    </div>
    
    {self._generate_errors_section(metrics)}
</body>
</html>
"""

        filename = f"report_{service_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return filepath

    def _generate_errors_section(self, metrics: APIMetrics) -> str:
        """Génère la section des erreurs pour le rapport HTML"""
        if not metrics.errors:
            return ""

        error_rows = ""
        for error in metrics.errors[-20:]:  # 20 dernières erreurs
            error_rows += f"""
                <tr>
                    <td>{error["timestamp"]}</td>
                    <td>{error["endpoint"]}</td>
                    <td class="status-error">{error["status_code"]}</td>
                    <td>{error["error"]}</td>
                </tr>
            """

        return f"""
    <div class="metric-card">
        <h2>Erreurs récentes</h2>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Endpoint</th>
                    <th>Code</th>
                    <th>Erreur</th>
                </tr>
            </thead>
            <tbody>
                {error_rows}
            </tbody>
        </table>
    </div>
        """

    def generate_csv_export(self, metrics: APIMetrics, service_name: str = "AFNOR API") -> Path:
        """
        Génère un export CSV des métriques

        Args:
            metrics: Métriques à exporter
            service_name: Nom du service

        Returns:
            Chemin du fichier généré
        """
        filename = f"export_{service_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self.output_dir / filename

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # En-têtes généraux
            writer.writerow(["Métrique", "Valeur"])
            writer.writerow(["Service", service_name])
            writer.writerow(["Date génération", datetime.now().isoformat()])
            writer.writerow(["Appels totaux", metrics.total_calls])
            writer.writerow(["Appels réussis", metrics.successful_calls])
            writer.writerow(["Appels échoués", metrics.failed_calls])
            writer.writerow(["Taux de succès", f"{metrics.get_success_rate():.2f}%"])
            writer.writerow(
                ["Temps moyen (ms)", f"{metrics.get_average_response_time() * 1000:.2f}"]
            )
            writer.writerow([])

            # Appels par endpoint
            writer.writerow(["Endpoint", "Nombre appels"])
            for endpoint, count in sorted(metrics.calls_by_endpoint.items(), key=lambda x: -x[1]):
                writer.writerow([endpoint, count])
            writer.writerow([])

            # Codes de statut
            writer.writerow(["Code HTTP", "Nombre"])
            for code, count in sorted(metrics.calls_by_status.items()):
                writer.writerow([code, count])

        return filepath


# ============================================================================
# CLIENT AVEC MONITORING INTÉGRÉ
# ============================================================================


class MonitoredFlowServiceClient:
    """Client Flow Service avec monitoring intégré"""

    def __init__(self, base_url: str, token_url: str, client_id: str, client_secret: str):
        """Initialise le client avec monitoring"""

        self.client = FlowServiceClient(base_url, token_url, client_id, client_secret)
        self.logger = AFNORLogger("flow_service")
        self.metrics = APIMetrics()

    def _wrap_call(self, method_name: str, *args, **kwargs):
        """Wrapper pour monitorer les appels"""
        start_time = time.time()
        endpoint = kwargs.get("endpoint", method_name)

        try:
            method = getattr(self.client, method_name)
            result = method(*args, **kwargs)
            duration = time.time() - start_time

            # Log et métriques
            self.logger.log_api_call(
                method="POST" if "submit" in method_name or "search" in method_name else "GET",
                endpoint=endpoint,
                status_code=200,
                duration=duration,
            )
            self.metrics.record_call(endpoint, 200, duration)

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            status_code = getattr(e, "status_code", 500)

            # Log et métriques
            self.logger.log_api_call(
                method="POST" if "submit" in method_name or "search" in method_name else "GET",
                endpoint=endpoint,
                status_code=status_code,
                duration=duration,
                error=error_msg,
            )
            self.metrics.record_call(endpoint, status_code, duration, error_msg)

            raise

    def submit_flow(self, **kwargs):
        """Soumet un flux avec monitoring"""
        return self._wrap_call("submit_flow", endpoint="/v1/flows", **kwargs)

    def search_flows(self, **kwargs):
        """Recherche des flux avec monitoring"""
        return self._wrap_call("search_flows", endpoint="/v1/flows/search", **kwargs)

    def download_flow(self, flow_id: str, **kwargs):
        """Télécharge un flux avec monitoring"""
        return self._wrap_call(
            "download_flow", endpoint=f"/v1/flows/{flow_id}", flow_id=flow_id, **kwargs
        )

    def healthcheck(self):
        """Vérifie la santé du service avec monitoring"""
        return self._wrap_call("healthcheck", endpoint="/v1/healthcheck")

    def get_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques collectées"""
        return self.metrics.to_dict()

    def generate_report(self, output_dir: str = "reports") -> Path:
        """Génère un rapport des métriques"""
        generator = ReportGenerator(output_dir)
        return generator.generate_html_report(self.metrics, "Flow Service")


class MonitoredDirectoryServiceClient:
    """Client Directory Service avec monitoring intégré"""

    def __init__(self, base_url: str, token_url: str, client_id: str, client_secret: str):
        """Initialise le client avec monitoring"""

        self.client = DirectoryServiceClient(base_url, token_url, client_id, client_secret)
        self.logger = AFNORLogger("directory_service")
        self.metrics = APIMetrics()

    def _wrap_call(self, method_name: str, *args, **kwargs):
        """Wrapper pour monitorer les appels"""
        start_time = time.time()
        endpoint = kwargs.pop("endpoint", method_name)

        try:
            method = getattr(self.client, method_name)
            result = method(*args, **kwargs)
            duration = time.time() - start_time

            http_method = "GET" if method_name.startswith("get_") else "POST"
            if method_name.startswith("create_"):
                http_method = "POST"
            elif method_name.startswith("delete_"):
                http_method = "DELETE"

            self.logger.log_api_call(
                method=http_method, endpoint=endpoint, status_code=200, duration=duration
            )
            self.metrics.record_call(endpoint, 200, duration)

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            status_code = getattr(e, "status_code", 500)

            http_method = "GET" if method_name.startswith("get_") else "POST"

            self.logger.log_api_call(
                method=http_method,
                endpoint=endpoint,
                status_code=status_code,
                duration=duration,
                error=error_msg,
            )
            self.metrics.record_call(endpoint, status_code, duration, error_msg)

            raise

    def get_siren(self, siren: str, **kwargs):
        """Récupère un SIREN avec monitoring"""
        return self._wrap_call("get_siren", siren, endpoint=f"/siren/code-insee:{siren}", **kwargs)

    def search_siren(self, **kwargs):
        """Recherche des SIREN avec monitoring"""
        return self._wrap_call("search_siren", endpoint="/siren/search", **kwargs)

    def get_siret(self, siret: str, **kwargs):
        """Récupère un SIRET avec monitoring"""
        return self._wrap_call("get_siret", siret, endpoint=f"/siret/code-insee:{siret}", **kwargs)

    def search_siret(self, **kwargs):
        """Recherche des SIRET avec monitoring"""
        return self._wrap_call("search_siret", endpoint="/siret/search", **kwargs)

    def get_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques collectées"""
        return self.metrics.to_dict()

    def generate_report(self, output_dir: str = "reports") -> Path:
        """Génère un rapport des métriques"""
        generator = ReportGenerator(output_dir)
        return generator.generate_html_report(self.metrics, "Directory Service")


# ============================================================================
# DASHBOARD EN TEMPS RÉEL
# ============================================================================


class RealTimeDashboard:
    """Dashboard de monitoring en temps réel"""

    def __init__(
        self,
        flow_client: MonitoredFlowServiceClient,
        directory_client: MonitoredDirectoryServiceClient,
    ):
        """
        Initialise le dashboard

        Args:
            flow_client: Client Flow Service monitoré
            directory_client: Client Directory Service monitoré
        """
        self.flow_client = flow_client
        self.directory_client = directory_client
        self.monitor = ServiceMonitor()

    def display_status(self):
        """Affiche le statut en temps réel"""
        import os

        # Clear screen
        os.system("cls" if os.name == "nt" else "clear")

        print("=" * 80)
        print("DASHBOARD AFNOR XP Z12-013 - Monitoring en temps réel")
        print("=" * 80)
        print()

        # État des services
        print("📡 ÉTAT DES SERVICES")
        print("-" * 80)
        flow_health = self.monitor.check_service_health(
            "Flow Service", self.flow_client.healthcheck
        )
        directory_health = self.monitor.check_service_health(
            "Directory Service", self.directory_client.healthcheck
        )

        self._print_health_status(flow_health)
        self._print_health_status(directory_health)
        print()

        # Métriques Flow Service
        print("📊 MÉTRIQUES FLOW SERVICE")
        print("-" * 80)
        flow_metrics = self.flow_client.get_metrics()
        self._print_metrics_summary(flow_metrics)
        print()

        # Métriques Directory Service
        print("📊 MÉTRIQUES DIRECTORY SERVICE")
        print("-" * 80)
        directory_metrics = self.directory_client.get_metrics()
        self._print_metrics_summary(directory_metrics)
        print()

        print("Dernière mise à jour:", datetime.now().strftime("%H:%M:%S"))

    def _print_health_status(self, health: Dict[str, Any]):
        """Affiche le statut de santé d'un service"""
        status_icon = "✅" if health["status"] == "healthy" else "❌"
        print(f"{status_icon} {health['service']}: {health['status'].upper()}")
        print(f"   Temps de réponse: {health['response_time']}")
        if "error" in health:
            print(f"   Erreur: {health['error']}")

    def _print_metrics_summary(self, metrics: Dict[str, Any]):
        """Affiche un résumé des métriques"""
        print(f"  Total appels: {metrics['total_calls']}")
        print(f"  Taux de succès: {metrics['success_rate']}")
        print(f"  Temps moyen: {metrics['average_response_time']}")
        print(f"  P95: {metrics['p95_response_time']}")

        if metrics["total_calls"] > 0:
            print("\n  Top 3 endpoints:")
            endpoints = sorted(metrics["calls_by_endpoint"].items(), key=lambda x: -x[1])[:3]
            for endpoint, count in endpoints:
                print(f"    • {endpoint}: {count} appels")

    def run_continuous(self, interval: int = 5):
        """
        Exécute le dashboard en continu

        Args:
            interval: Intervalle de rafraîchissement en secondes
        """
        print("Dashboard démarré. Appuyez sur Ctrl+C pour arrêter.")

        try:
            while True:
                self.display_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n✅ Dashboard arrêté.")


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    """
    Exemple d'utilisation du monitoring
    """

    # Configuration
    config = {
        "flow_base_url": "https://api.pdp.com/flow-service",
        "directory_base_url": "https://api.pdp.com/directory-service",
        "token_url": "https://auth.pdp.com/oauth/token",
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
    }

    print("🔧 Initialisation des clients avec monitoring...")

    # Créer les clients monitorés
    flow_client = MonitoredFlowServiceClient(
        base_url=config["flow_base_url"],
        token_url=config["token_url"],
        client_id=config["client_id"],
        client_secret=config["client_secret"],
    )

    directory_client = MonitoredDirectoryServiceClient(
        base_url=config["directory_base_url"],
        token_url=config["token_url"],
        client_id=config["client_id"],
        client_secret=config["client_secret"],
    )

    print("✅ Clients initialisés\n")

    # Exemple 1: Utilisation normale avec logging automatique
    print("📤 Exemple 1: Soumission de flux avec monitoring...")
    try:
        # Les appels sont automatiquement loggés et métriqués
        result = flow_client.submit_flow(
            file_path="test_invoice.xml", flow_name="Test Invoice", flow_syntax="CII"
        )
        print(f"✅ Flux soumis: {result.get('flowId')}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

    print()

    # Exemple 2: Affichage des métriques
    print("📊 Exemple 2: Consultation des métriques...")
    metrics = flow_client.get_metrics()
    print(f"Total appels: {metrics['total_calls']}")
    print(f"Taux de succès: {metrics['success_rate']}")
    print(f"Temps moyen: {metrics['average_response_time']}")
    print()

    # Exemple 3: Génération de rapport
    print("📄 Exemple 3: Génération de rapport HTML...")
    report_path = flow_client.generate_report()
    print(f"✅ Rapport généré: {report_path}")
    print()

    # Exemple 4: Dashboard en temps réel (optionnel)
    print("📺 Exemple 4: Dashboard temps réel disponible")
    print("   Pour lancer: dashboard = RealTimeDashboard(flow_client, directory_client)")
    print("                dashboard.run_continuous()")
    print()

    print("✅ Exemples terminés!")
    print("\n💡 Consultez les logs dans le répertoire 'logs/'")
    print("💡 Consultez les rapports dans le répertoire 'reports/'")


"""
═══════════════════════════════════════════════════════════════════════════
📚 DOCUMENTATION DU MODULE DE MONITORING
═══════════════════════════════════════════════════════════════════════════

FONCTIONNALITÉS:
    ✅ Logging structuré (JSON + texte)
    ✅ Métriques de performance
    ✅ Monitoring de santé des services
    ✅ Génération de rapports (HTML, JSON, CSV)
    ✅ Dashboard temps réel
    ✅ Historique des erreurs

UTILISATION:

1. Clients monitorés:
    from monitoring import MonitoredFlowServiceClient
    
    client = MonitoredFlowServiceClient(base_url, token_url, id, secret)
    client.submit_flow(...)  # Automatiquement loggé et métriqué
    
2. Métriques:
    metrics = client.get_metrics()
    print(metrics['success_rate'])
    
3. Rapports:
    client.generate_report()  # Génère un rapport HTML
    
4. Dashboard:
    dashboard = RealTimeDashboard(flow_client, directory_client)
    dashboard.run_continuous()

FICHIERS GÉNÉRÉS:
    logs/
        ├── afnor_client_20251018.jsonl   # Logs JSON structurés
        └── afnor_client_20251018.log     # Logs texte lisibles
    
    reports/
        ├── metrics_flow_service_20251018_143022.json
        ├── report_flow_service_20251018_143022.html
        └── export_flow_service_20251018_143022.csv

═══════════════════════════════════════════════════════════════════════════
"""
