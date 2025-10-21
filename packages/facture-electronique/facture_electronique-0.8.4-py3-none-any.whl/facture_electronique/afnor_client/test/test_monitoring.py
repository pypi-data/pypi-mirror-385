import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from facture_electronique.afnor_client.monitoring import (
    APIMetrics,
    ReportGenerator,
    MonitoredFlowServiceClient,
    ServiceMonitor,
)
from facture_electronique.afnor_client.client import AFNORAPIError

# ============================================================================
# FIXTURES
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


# ============================================================================
# TESTS POUR APIMetrics
# ============================================================================


class TestAPIMetrics:
    def test_record_call(self):
        metrics = APIMetrics()
        metrics.record_call("/test", 200, 0.1)
        metrics.record_call("/test", 500, 0.2, "Server Error")

        assert metrics.total_calls == 2
        assert metrics.successful_calls == 1
        assert metrics.failed_calls == 1
        assert metrics.total_duration == pytest.approx(0.3)
        assert metrics.calls_by_endpoint["/test"] == 2
        assert metrics.calls_by_status[200] == 1
        assert metrics.calls_by_status[500] == 1
        assert len(metrics.errors) == 1
        assert metrics.errors[0]["error"] == "Server Error"

    def test_calculations(self):
        metrics = APIMetrics()
        metrics.record_call("/test", 200, 0.1)
        metrics.record_call("/test", 200, 0.2)
        metrics.record_call("/test", 200, 0.3)
        metrics.record_call("/test", 500, 0.4)

        assert metrics.get_success_rate() == 75.0
        assert metrics.get_average_response_time() == pytest.approx(0.25)
        # The current implementation of percentile is a simple index access.
        # For a list of 4 elements, the 50th percentile (index 2) is the 3rd element.
        assert metrics.get_percentile(50) == 0.3
        assert metrics.get_percentile(95) == 0.4

    def test_empty_metrics(self):
        metrics = APIMetrics()
        assert metrics.get_success_rate() == 0.0
        assert metrics.get_average_response_time() == 0.0
        assert metrics.get_percentile(50) == 0.0


# ============================================================================
# TESTS POUR ReportGenerator
# ============================================================================


class TestReportGenerator:
    @pytest.fixture
    def metrics(self):
        m = APIMetrics()
        m.record_call("/flows", 202, 0.15)
        m.record_call("/flows/search", 200, 0.25)
        m.record_call("/flows/search", 500, 0.35, "Internal Error")
        return m

    def test_generate_html_report(self, metrics, tmp_path):
        generator = ReportGenerator(output_dir=str(tmp_path))
        report_path = generator.generate_html_report(metrics, "Test Service")

        assert report_path.exists()
        assert report_path.name.startswith("report_test_service")
        assert report_path.name.endswith(".html")

        content = report_path.read_text()
        assert "<h1>Test Service - Rapport d'utilisation</h1>" in content
        assert "<td>/flows/search</td><td>2</td>" in content
        assert '<div class="metric-value status-error">1</div>' in content

    def test_generate_csv_report(self, metrics, tmp_path):
        generator = ReportGenerator(output_dir=str(tmp_path))
        report_path = generator.generate_csv_export(metrics, "Test Service")

        assert report_path.exists()
        content = report_path.read_text()
        assert "Test Service" in content
        assert "/flows/search,2" in content
        assert "500,1" in content


# ============================================================================
# TESTS POUR Monitored Clients
# ============================================================================


@patch("facture_electronique.afnor_client.monitoring.AFNORLogger")
@patch("facture_electronique.afnor_client.monitoring.APIMetrics")
def test_monitored_flow_client_success(MockMetrics, MockLogger, mock_credentials):
    # Mock des dépendances
    mock_metrics_instance = MockMetrics.return_value
    mock_logger_instance = MockLogger.return_value

    # Mock du client interne
    mock_internal_client = MagicMock()
    mock_internal_client.submit_flow.return_value = {"flowId": "123"}

    with patch(
        "facture_electronique.afnor_client.monitoring.FlowServiceClient",
        return_value=mock_internal_client,
    ):
        client = MonitoredFlowServiceClient(**mock_credentials)

        # Appel de la méthode
        client.submit_flow(file_path="dummy.xml")

        # Assertions
        mock_internal_client.submit_flow.assert_called_once()
        mock_logger_instance.log_api_call.assert_called_once()
        mock_metrics_instance.record_call.assert_called_once()

        # Vérifier que l'appel a été enregistré comme un succès
        call_args, call_kwargs = mock_metrics_instance.record_call.call_args
        assert call_args[1] == 200


@patch("facture_electronique.afnor_client.monitoring.AFNORLogger")
@patch("facture_electronique.afnor_client.monitoring.APIMetrics")
def test_monitored_flow_client_failure(MockMetrics, MockLogger, mock_credentials):
    # Mock des dépendances
    mock_metrics_instance = MockMetrics.return_value
    mock_logger_instance = MockLogger.return_value

    # Mock du client interne qui lève une exception
    mock_internal_client = MagicMock()
    mock_internal_client.submit_flow.side_effect = AFNORAPIError(
        400, "VALIDATION_ERROR", "Bad request"
    )

    with patch(
        "facture_electronique.afnor_client.monitoring.FlowServiceClient",
        return_value=mock_internal_client,
    ):
        client = MonitoredFlowServiceClient(**mock_credentials)

        with pytest.raises(AFNORAPIError):
            client.submit_flow(file_path="dummy.xml")

        # Assertions
        mock_internal_client.submit_flow.assert_called_once()
        mock_logger_instance.log_api_call.assert_called_once()
        mock_metrics_instance.record_call.assert_called_once()

        # Vérifier que l'appel a été enregistré comme un échec
        call_args, call_kwargs = mock_metrics_instance.record_call.call_args
        assert call_args[1] == 400
        assert call_args[3] is not None


# ============================================================================
# TESTS POUR ServiceMonitor
# ============================================================================


class TestServiceMonitor:
    def test_check_service_health_healthy(self):
        monitor = ServiceMonitor()
        healthcheck_func = MagicMock(return_value=True)

        result = monitor.check_service_health("TestService", healthcheck_func)

        assert result["service"] == "TestService"
        assert result["status"] == "healthy"
        healthcheck_func.assert_called_once()

    def test_check_service_health_unhealthy(self):
        monitor = ServiceMonitor()
        healthcheck_func = MagicMock(return_value=False)

        result = monitor.check_service_health("TestService", healthcheck_func)

        assert result["status"] == "unhealthy"

    def test_check_service_health_error(self):
        monitor = ServiceMonitor()
        healthcheck_func = MagicMock(side_effect=Exception("Connection failed"))

        result = monitor.check_service_health("TestService", healthcheck_func)

        assert result["status"] == "error"
        assert result["error"] == "Connection failed"

    def test_get_uptime(self):
        monitor = ServiceMonitor()
        monitor.health_history = [
            {
                "service": "TestService",
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "service": "TestService",
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "service": "TestService",
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "service": "OtherService",
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
            },
        ]

        uptime = monitor.get_uptime("TestService")
        assert uptime == pytest.approx(66.66, 0.1)
