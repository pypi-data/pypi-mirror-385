"""Unit tests for control_plane_client.py."""

import unittest
from unittest import mock
from google_cloud_mldiagnostics.src.google_cloud_mldiagnostics.clients import control_plane_client
import requests

GCP_FQN = "google_cloud_mldiagnostics.src.google_cloud_mldiagnostics.clients.control_plane_client.google.auth.default"
POST_REQUESTS_FQN = "google_cloud_mldiagnostics.src.google_cloud_mldiagnostics.clients.control_plane_client.requests.post"
PATCH_REQUESTS_FQN = "google_cloud_mldiagnostics.src.google_cloud_mldiagnostics.clients.control_plane_client.requests.patch"
GET_REQUESTS_FQN = "google_cloud_mldiagnostics.src.google_cloud_mldiagnostics.clients.control_plane_client.requests.get"


class TestControlPlaneClient(unittest.TestCase):
  """Test cases for ControlPlaneClient."""

  def setUp(self):
    """Set up test resources."""
    super().setUp()
    self.mock_credentials = mock.Mock()
    self.mock_credentials.valid = True
    self.mock_credentials.token = "mock-access-token"
    self.mock_credentials.refresh = mock.Mock()

    self.mock_response = mock.Mock()
    self.mock_response.status_code = 200
    self.mock_response.json.return_value = {
        "name": (
            "projects/test-project/locations/us-west1/machineLearningRuns/test-run"
        ),
        "displayName": "test-run",
        "runPhase": "ACTIVE",
        "createTime": "2025-08-13T10:00:00Z",
    }
    with mock.patch(GCP_FQN, return_value=(self.mock_credentials, None)):
      self.client = control_plane_client.ControlPlaneClient(
          project_id="test-project", location="us-west1"
      )

  def tearDown(self):
    """Clean up mocks after each test method."""
    super().tearDown()
    mock.patch.stopall()

  @mock.patch(GCP_FQN)
  def test_init_default_parameters(self, mock_auth_default):
    """Test client initialization with default parameters."""
    mock_auth_default.return_value = (self.mock_credentials, None)
    client = control_plane_client.ControlPlaneClient()

    assert client.project_id == "supercomputer-testing"
    assert client.location == "us-central1"
    assert (
        client.base_url
        == "https://autopush-hypercomputecluster.sandbox.googleapis.com/v1alpha"
    )
    assert "supercomputer-testing" in client.ml_runs_path
    assert "us-central1" in client.ml_runs_path

  @mock.patch(GCP_FQN)
  def test_init_custom_parameters(self, mock_auth_default):
    """Test client initialization with custom parameters."""
    mock_auth_default.return_value = (self.mock_credentials, None)
    client = control_plane_client.ControlPlaneClient(
        project_id="custom-project",
        location="europe-west1",
        base_url="https://custom-api.example.com/v1",
    )

    assert client.project_id == "custom-project"
    assert client.location == "europe-west1"
    assert client.base_url == "https://custom-api.example.com/v1"

  def test_get_access_token_valid_credentials(self):
    """Test getting access token when credentials are valid."""
    token = self.client._get_access_token()  # pylint: disable=protected-access
    assert token == "mock-access-token"

  def test_get_access_token_refresh_needed(self):
    """Test getting access token when credentials need refresh."""
    self.client.credentials.valid = False

    token = self.client._get_access_token()  # pylint: disable=protected-access

    self.client.credentials.refresh.assert_called_once()
    assert token == "mock-access-token"

  def test_get_headers(self):
    """Test HTTP headers generation."""
    headers = self.client._get_headers()  # pylint: disable=protected-access

    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer mock-access-token",
    }
    assert headers == expected_headers

  @mock.patch(POST_REQUESTS_FQN)
  def test_create_ml_run_minimal_parameters(self, mock_post):
    """Test create_ml_run with minimal required parameters."""
    mock_post.return_value = self.mock_response

    result = self.client.create_ml_run(
        name="test-run", display_name="Test Run", run_phase="ACTIVE"
    )

    # Verify the request was made correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args

    # Check URL
    assert call_args[0][0] == self.client.ml_runs_path

    # Check headers
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer mock-access-token",
    }
    assert call_args[1]["headers"] == expected_headers

    # Check params
    assert call_args[1]["params"] == {"machine_learning_run_id": "test-run"}

    # Check payload
    payload = call_args[1]["json"]
    expected_payload = {
        "displayName": "Test Run",
        "name": "test-run",
        "runPhase": "ACTIVE",
    }
    assert payload == expected_payload

    # Check return value
    assert result == self.mock_response.json.return_value

  @mock.patch(POST_REQUESTS_FQN)
  def test_create_ml_run_all_parameters(self, mock_post):
    """Test create_ml_run with all parameters."""
    mock_post.return_value = self.mock_response

    configs = {
        "userConfigs": {"batch_size": "32"},
        "softwareConfigs": {"jax_version": "0.4.1"},
        "hardwareConfigs": {"tpu_type": "v4-8"},
    }
    metrics = {"test_metric1": "5", "test_metric2": "20"}
    artifacts = {"gcsPath": "gs://test-bucket/artifacts"}
    labels = {"experiment": "test", "owner": "user1"}
    tools = [{"nsys": {}}]
    workload_details = {
        "id": "test-id",
        "kind": "test-kind",
        "cluster": "test-cluster",
        "namespace": "test-namespace",
        "parent_workload": "test-parent-workload",
        "labels": {"key": "value"},
    }

    self.client.create_ml_run(
        name="projects-my-project-locations-us-central1-runs-full-test-run-1",
        display_name="Full Test Run",
        run_phase="ACTIVE",
        configs=configs,
        tools=tools,
        metrics=metrics,
        artifacts=artifacts,
        run_group="test-group",
        labels=labels,
        orchestrator="GKE",
        workload_details=workload_details,
    )

    # Check params
    assert mock_post.call_args[1]["params"] == {
        "machine_learning_run_id": (
            "projects-my-project-locations-us-central1-runs-full-test-run-1"
        )
    }

    # Check payload contains all parameters
    payload = mock_post.call_args[1]["json"]

    assert payload["displayName"] == "Full Test Run"
    assert (
        payload["name"]
        == "projects-my-project-locations-us-central1-runs-full-test-run-1"
    )
    assert payload["configs"] == configs
    assert payload["metrics"] == metrics
    assert payload["artifacts"] == artifacts
    assert payload["runSet"] == "test-group"
    assert payload["labels"] == labels
    assert payload["runPhase"] == "ACTIVE"
    assert payload["tools"] == tools
    assert payload["orchestrator"] == "GKE"
    assert payload["workloadDetails"] == {
        "gke": {
            "id": "test-id",
            "kind": "test-kind",
            "cluster": "test-cluster",
            "namespace": "test-namespace",
            "parentWorkload": "test-parent-workload",
            "labels": {"key": "value"},
        }
    }

  @mock.patch(POST_REQUESTS_FQN)
  def test_create_ml_run_orchestrator_not_gke(self, mock_post):
    """Test create_ml_run with orchestrator other than GKE."""
    mock_post.return_value = self.mock_response

    workload_details = {
        "id": "test-id",
        "kind": "test-kind",
        "cluster": "test-cluster",
        "namespace": "test-namespace",
        "parent_workload": "test-parent-workload",
        "labels": {"key": "value"},
    }

    self.client.create_ml_run(
        name="test-run-gce",
        display_name="Test Run GCE",
        run_phase="ACTIVE",
        orchestrator="GCE",
        workload_details=workload_details,
    )

    # Check payload does not contain workloadDetails
    payload = mock_post.call_args[1]["json"]

    self.assertEqual(payload["displayName"], "Test Run GCE")
    self.assertEqual(payload["name"], "test-run-gce")
    self.assertEqual(payload["orchestrator"], "GCE")
    self.assertNotIn("workloadDetails", payload)

  @mock.patch(POST_REQUESTS_FQN)
  def test_create_ml_run_gke_workload_details_none_values(self, mock_post):
    """Test create_ml_run with GKE workload details containing None values."""
    mock_post.return_value = self.mock_response

    workload_details = {
        "id": "test-id",
        "kind": "test-kind",
        "cluster": "test-cluster",
        "namespace": "test-namespace",
        "parent_workload": None,
        "labels": None,
    }

    self.client.create_ml_run(
        name="test-run-gke-none",
        display_name="Test Run GKE None",
        run_phase="ACTIVE",
        orchestrator="GKE",
        workload_details=workload_details,
    )

    # Check payload does not contain parentWorkload or labels
    payload = mock_post.call_args[1]["json"]
    gke_details = payload["workloadDetails"]["gke"]
    self.assertNotIn("parentWorkload", gke_details)
    self.assertNotIn("labels", gke_details)
    self.assertEqual(gke_details["id"], "test-id")

  @mock.patch(POST_REQUESTS_FQN)
  def test_create_ml_run_http_error(self, mock_post):
    """Test handling of HTTP errors."""
    # mock.Mock HTTP error response
    mock_response = mock.Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Not Found"
    )
    mock_post.return_value = mock_response

    with self.assertRaises(requests.exceptions.HTTPError):
      self.client.create_ml_run(
          name="test-run", display_name="Test Run", run_phase="ACTIVE"
      )

  @mock.patch(POST_REQUESTS_FQN)
  def test_create_ml_run_request_exception(self, mock_post):
    """Test handling of request exceptions."""
    mock_post.side_effect = requests.exceptions.RequestException(
        "Network error"
    )

    with self.assertRaises(requests.exceptions.RequestException):
      self.client.create_ml_run(
          name="test-run", display_name="Test Run", run_phase="ACTIVE"
      )

  def test_create_ml_run_url_construction(self):
    """Test that the ML runs URL is constructed correctly."""
    expected_url = (
        "https://autopush-hypercomputecluster.sandbox.googleapis.com/v1alpha/"
        "projects/test-project/locations/us-west1/machineLearningRuns"
    )
    assert self.client.ml_runs_path == expected_url

  @mock.patch(POST_REQUESTS_FQN)
  def test_create_ml_run_optional_parameters_none(self, mock_post):
    """Test that None values for optional parameters are not included in payload."""
    mock_post.return_value = self.mock_response

    self.client.create_ml_run(
        name="test-run",
        display_name="Test Run",
        run_phase="ACTIVE",
        configs=None,
        metrics=None,
        artifacts=None,
        run_group=None,
        labels=None,
    )

    assert mock_post.call_args[1]["params"] == {
        "machine_learning_run_id": "test-run"
    }
    payload = mock_post.call_args[1]["json"]

    # These fields should not be present when None
    assert "configs" not in payload
    assert "metrics" not in payload
    assert "artifacts" not in payload
    assert "runSet" not in payload
    assert "labels" not in payload

    # These should always be present
    assert "displayName" in payload
    assert "name" in payload
    assert "runPhase" in payload
    assert "createTime" not in payload

  @mock.patch(GET_REQUESTS_FQN)
  def test_get_ml_run_success(self, mock_get):
    """Test get_ml_run success."""
    mock_get.return_value = self.mock_response
    result = self.client.get_ml_run(name="test-run")
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args[0][0] == f"{self.client.ml_runs_path}/test-run"
    assert result == self.mock_response.json.return_value

  @mock.patch(GET_REQUESTS_FQN)
  def test_get_ml_run_http_error(self, mock_get):
    """Test get_ml_run handling of HTTP errors."""
    mock_response = mock.Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Not Found"
    )
    mock_get.return_value = mock_response
    with self.assertRaises(requests.exceptions.HTTPError):
      self.client.get_ml_run(name="test-run")

  @mock.patch(PATCH_REQUESTS_FQN)
  @mock.patch(GET_REQUESTS_FQN)
  def test_update_ml_run_all_parameters(self, mock_get, mock_patch):
    """Test update_ml_run with all parameters."""
    mock_get.return_value = self.mock_response
    mock_patch.return_value = self.mock_response
    metrics = {"avgMfu": "100.0"}

    get_response_dict = self.mock_response.json.return_value.copy()

    result = self.client.update_ml_run(
        name="test-run", run_phase="COMPLETED", metrics=metrics
    )

    mock_get.assert_called_once()
    mock_patch.assert_called_once()

    expected_payload = get_response_dict
    expected_payload["metrics"] = metrics
    expected_payload["runPhase"] = "COMPLETED"
    expected_payload.pop("createTime", None)

    call_args = mock_patch.call_args
    assert call_args[0][0] == f"{self.client.ml_runs_path}/test-run"
    assert call_args[1]["params"] == {"update_mask": "*"}
    assert call_args[1]["json"] == expected_payload
    assert result == self.mock_response.json.return_value

  @mock.patch(PATCH_REQUESTS_FQN)
  @mock.patch(GET_REQUESTS_FQN)
  def test_update_ml_run_only_metrics(self, mock_get, mock_patch):
    """Test update_ml_run with only metrics."""
    mock_get.return_value = self.mock_response
    mock_patch.return_value = self.mock_response
    metrics = {"avgMfu": "100.0"}

    get_response_dict = self.mock_response.json.return_value.copy()

    result = self.client.update_ml_run(name="test-run", metrics=metrics)

    mock_get.assert_called_once()
    mock_patch.assert_called_once()

    expected_payload = get_response_dict
    expected_payload["metrics"] = metrics
    expected_payload.pop("createTime", None)

    call_args = mock_patch.call_args
    assert call_args[0][0] == f"{self.client.ml_runs_path}/test-run"
    assert call_args[1]["params"] == {"update_mask": "*"}
    assert call_args[1]["json"] == expected_payload
    assert result == self.mock_response.json.return_value

  @mock.patch(PATCH_REQUESTS_FQN)
  @mock.patch(GET_REQUESTS_FQN)
  def test_update_ml_run_only_run_phase(self, mock_get, mock_patch):
    """Test update_ml_run with only run_phase."""
    mock_get.return_value = self.mock_response
    mock_patch.return_value = self.mock_response

    get_response_dict = self.mock_response.json.return_value.copy()

    result = self.client.update_ml_run(name="test-run", run_phase="COMPLETED")

    mock_get.assert_called_once()
    mock_patch.assert_called_once()

    expected_payload = get_response_dict
    expected_payload["runPhase"] = "COMPLETED"
    expected_payload.pop("createTime", None)

    call_args = mock_patch.call_args
    assert call_args[0][0] == f"{self.client.ml_runs_path}/test-run"
    assert call_args[1]["params"] == {"update_mask": "*"}
    assert call_args[1]["json"] == expected_payload
    assert result == self.mock_response.json.return_value

  @mock.patch(PATCH_REQUESTS_FQN)
  @mock.patch(GET_REQUESTS_FQN)
  def test_update_ml_run_no_updates(self, mock_get, mock_patch):
    """Test update_ml_run with no update parameters."""
    mock_get.return_value = self.mock_response
    result = self.client.update_ml_run(name="test-run")
    mock_get.assert_called_once()
    assert result == self.mock_response.json.return_value
    mock_patch.assert_not_called()

  @mock.patch(PATCH_REQUESTS_FQN)
  @mock.patch(GET_REQUESTS_FQN)
  def test_update_ml_run_http_error(self, mock_get, mock_patch):
    """Test update_ml_run handling of HTTP errors."""
    mock_get.return_value = self.mock_response
    mock_response = mock.Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "500 Server Error"
    )
    mock_patch.return_value = mock_response

    with self.assertRaises(requests.exceptions.HTTPError):
      self.client.update_ml_run(name="test-run", run_phase="FAILED")

    mock_get.assert_called_once()
    mock_patch.assert_called_once()


if __name__ == "__main__":
  unittest.main()
