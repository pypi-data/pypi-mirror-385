"""Utility functions for identifying orchestrator."""

import os
import requests


def detect_orchestrator():
  """Detects the orchestrator the workload is running on."""
  orchestrator = None

  # Check for GCE Metadata Server to determine if running on GCP
  on_gcp = False
  try:
    headers = {'Metadata-Flavor': 'Google'}
    # Use a more specific endpoint to be sure
    response = requests.get(
        'http://metadata.google.internal/computeMetadata/v1/instance/id',
        headers=headers,
        timeout=0.1,
    )
    if (
        response.status_code == 200
        and response.headers.get('Metadata-Flavor') == 'Google'
    ):
      on_gcp = True
  except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
    pass

  if on_gcp:
    # Running on GCP, check if it's GKE or standard GCE
    if os.getenv('KUBERNETES_SERVICE_HOST') or os.path.exists(
        '/var/run/secrets/kubernetes.io/serviceaccount/token'
    ):
      orchestrator = 'GKE'
    else:
      orchestrator = 'GCE'

  return orchestrator
