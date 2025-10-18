# Copyright 2025 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for orchestrator_utils."""

import unittest
from unittest import mock

from google_cloud_mldiagnostics.utils import orchestrator_utils
import requests


class OrchestratorUtilsTest(unittest.TestCase):
  """Tests for orchestrator_utils."""

  @mock.patch("requests.get", side_effect=requests.exceptions.ConnectionError)
  def test_detect_orchestrator_not_on_gcp_connection_error(self, mock_get):
    """Tests that None is returned if connection to metadata server fails."""
    self.assertIsNone(orchestrator_utils.detect_orchestrator())
    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/id",
        headers={"Metadata-Flavor": "Google"},
        timeout=0.1,
    )

  @mock.patch("requests.get", side_effect=requests.exceptions.Timeout)
  def test_detect_orchestrator_not_on_gcp_timeout(self, mock_get):
    """Tests that None is returned if connection to metadata server times out."""
    self.assertIsNone(orchestrator_utils.detect_orchestrator())
    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/id",
        headers={"Metadata-Flavor": "Google"},
        timeout=0.1,
    )

  @mock.patch("requests.get")
  def test_detect_orchestrator_not_on_gcp_wrong_header(self, mock_get):
    """Tests that None is returned if metadata server returns wrong header."""
    response = mock.Mock()
    response.status_code = 200
    response.headers = {"Metadata-Flavor": "NotGoogle"}
    mock_get.return_value = response
    self.assertIsNone(orchestrator_utils.detect_orchestrator())
    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/id",
        headers={"Metadata-Flavor": "Google"},
        timeout=0.1,
    )

  @mock.patch("requests.get")
  def test_detect_orchestrator_not_on_gcp_wrong_status(self, mock_get):
    """Tests that None is returned if metadata server returns non-200 status."""
    response = mock.Mock()
    response.status_code = 404
    response.headers = {"Metadata-Flavor": "Google"}
    mock_get.return_value = response
    self.assertIsNone(orchestrator_utils.detect_orchestrator())
    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/id",
        headers={"Metadata-Flavor": "Google"},
        timeout=0.1,
    )

  @mock.patch("os.path.exists", return_value=False)
  @mock.patch("os.getenv", return_value=None)
  @mock.patch("requests.get")
  def test_detect_orchestrator_on_gce(self, mock_get, mock_getenv, mock_exists):
    """Tests that GCE is detected if metadata server is present but k8s is not."""
    response = mock.Mock()
    response.status_code = 200
    response.headers = {"Metadata-Flavor": "Google"}
    mock_get.return_value = response
    self.assertEqual(orchestrator_utils.detect_orchestrator(), "GCE")
    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/id",
        headers={"Metadata-Flavor": "Google"},
        timeout=0.1,
    )
    mock_getenv.assert_called_once_with("KUBERNETES_SERVICE_HOST")
    mock_exists.assert_called_once_with(
        "/var/run/secrets/kubernetes.io/serviceaccount/token"
    )

  @mock.patch("os.path.exists", return_value=False)
  @mock.patch("os.getenv", return_value="kubernetes-host")
  @mock.patch("requests.get")
  def test_detect_orchestrator_on_gke_by_env_var(
      self, mock_get, mock_getenv, mock_exists
  ):
    """Tests that GKE is detected if k8s env var is present."""
    response = mock.Mock()
    response.status_code = 200
    response.headers = {"Metadata-Flavor": "Google"}
    mock_get.return_value = response
    self.assertEqual(orchestrator_utils.detect_orchestrator(), "GKE")
    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/id",
        headers={"Metadata-Flavor": "Google"},
        timeout=0.1,
    )
    mock_getenv.assert_called_once_with("KUBERNETES_SERVICE_HOST")
    mock_exists.assert_not_called()

  @mock.patch("os.path.exists", return_value=True)
  @mock.patch("os.getenv", return_value=None)
  @mock.patch("requests.get")
  def test_detect_orchestrator_on_gke_by_token(
      self, mock_get, mock_getenv, mock_exists
  ):
    """Tests that GKE is detected if k8s token file is present."""
    response = mock.Mock()
    response.status_code = 200
    response.headers = {"Metadata-Flavor": "Google"}
    mock_get.return_value = response
    self.assertEqual(orchestrator_utils.detect_orchestrator(), "GKE")
    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/id",
        headers={"Metadata-Flavor": "Google"},
        timeout=0.1,
    )
    mock_getenv.assert_called_once_with("KUBERNETES_SERVICE_HOST")
    mock_exists.assert_called_once_with(
        "/var/run/secrets/kubernetes.io/serviceaccount/token"
    )
