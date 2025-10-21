from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import pytest
import tenacity
from ops.testing import Container, Exec


@pytest.fixture(autouse=True)
def patch_all(tmp_path: Path):
    with ExitStack() as stack:
        # so we don't have to wait for minutes:
        stack.enter_context(
            patch(
                "coordinated_workers.worker.Worker.SERVICE_START_RETRY_WAIT",
                new=tenacity.wait_none(),
            )
        )
        stack.enter_context(
            patch(
                "coordinated_workers.worker.Worker.SERVICE_START_RETRY_STOP",
                new=tenacity.stop_after_delay(1),
            )
        )
        stack.enter_context(
            patch(
                "coordinated_workers.worker.Worker.SERVICE_STATUS_UP_RETRY_WAIT",
                new=tenacity.wait_none(),
            )
        )
        stack.enter_context(
            patch(
                "coordinated_workers.worker.Worker.SERVICE_STATUS_UP_RETRY_STOP",
                new=tenacity.stop_after_delay(1),
            )
        )

        # Prevent the worker's _update_tls_certificates method to try and write our local filesystem
        stack.enter_context(
            patch("coordinated_workers.worker.ROOT_CA_CERT", new=tmp_path / "rootcacert")
        )
        stack.enter_context(
            patch(
                "coordinated_workers.worker.ROOT_CA_CERT_PATH",
                new=Path(tmp_path / "rootcacert"),
            )
        )

        stack.enter_context(
            patch(
                "coordinated_workers.coordinator.CONSOLIDATED_METRICS_ALERT_RULES_PATH",
                new=tmp_path / "consolidated_metrics_rules",
            )
        )

        stack.enter_context(
            patch(
                "coordinated_workers.coordinator.CONSOLIDATED_LOGS_ALERT_RULES_PATH",
                new=tmp_path / "consolidated_logs_rules",
            )
        )

        yield


@pytest.fixture(autouse=True)
def mock_worker_lightkube_client(request):
    """Global mock for the Worker's lightkube client to avoid lightkube calls."""
    # Skip this fixture if the test has explicitly disabled it.
    # To use this feature in a test, mark it with @pytest.mark.disable_worker_lightkube_client_autouse
    if "disable_worker_lightkube_client_autouse" in request.keywords:
        yield
    else:
        with patch("coordinated_workers.worker.Client") as mocked:
            yield mocked


@pytest.fixture(autouse=True)
def mock_worker_reconcile_charm_labels(request):
    """Global mock for the Worker's reconcile_charm_labels to avoid lightkube calls."""
    # Skip this fixture if the test has explicitly disabled it.
    # To use this feature in a test, mark it with @pytest.mark.disable_worker_reconcile_charm_labels_autouse
    if "disable_worker_reconcile_charm_labels_autouse" in request.keywords:
        yield
    else:
        with patch("coordinated_workers.worker.reconcile_charm_labels") as mocked:
            yield mocked


@pytest.fixture(autouse=True)
def mock_coordinator_lightkube_client(request):
    """Global mock for the Coordinator's lightkube client to avoid lightkube calls."""
    # Skip this fixture if the test has explicitly disabled it.
    # To use this feature in a test, mark it with @pytest.mark.disable_coordinator_lightkube_client_autouse
    if "disable_coordinator_lightkube_client_autouse" in request.keywords:
        yield
    else:
        with patch("coordinated_workers.coordinator.Client") as mocked:
            yield mocked


@pytest.fixture(autouse=True)
def mock_coordinator_reconcile_charm_labels(request):
    """Global mock for the Coordinator's reconcile_charm_labels to avoid lightkube calls."""
    # Skip this fixture if the test has explicitly disabled it.
    # To use this feature in a test, mark it with @pytest.mark.disable_coordinator_reconcile_charm_labels_autouse
    if "disable_coordinator_reconcile_charm_labels_autouse" in request.keywords:
        yield
    else:
        with patch("coordinated_workers.coordinator.reconcile_charm_labels") as mocked:
            yield mocked


@pytest.fixture
def nginx_container():
    return Container(
        "nginx",
        can_connect=True,
        execs={Exec(["update-ca-certificates", "--fresh"], return_code=0)},
    )


@pytest.fixture
def nginx_prometheus_exporter_container():
    return Container(
        "nginx-prometheus-exporter",
        can_connect=True,
    )
