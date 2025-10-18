"""Utility functions for host- related checks."""

import datetime
import json
import logging
import os
import re
from typing import Any

import jax


logger = logging.getLogger(__name__)


# jax related functions
def _get_jax_process_index() -> int:
  """Returns the process index."""
  return jax.process_index()


# GKE related functions
def _get_gke_diagon_identifier() -> dict[str, Any] | None:
  """Returns GKE Diagon identifier as a dictionary if set, otherwise None."""
  diagon_identifier_str = os.environ.get("GKE_DIAGON_IDENTIFIER")
  if not diagon_identifier_str:
    logger.info("GKE_DIAGON_IDENTIFIER environment variable not set.")
    return None

  try:
    diagon_identifier = json.loads(diagon_identifier_str)
    return diagon_identifier
  except json.JSONDecodeError:
    logger.error(
        "Failed to parse GKE_DIAGON_IDENTIFIER: %s", diagon_identifier_str
    )
    return None


def _get_gke_diagon_metadata() -> dict[str, Any] | None:
  """Returns GKE Diagon metadata as a dictionary if set, otherwise None."""
  diagon_metadata_str = os.environ.get("GKE_DIAGON_METADATA")
  if not diagon_metadata_str:
    logger.info("GKE_DIAGON_METADATA environment variable not set.")
    return None

  try:
    diagon_metadata = json.loads(diagon_metadata_str)
    return diagon_metadata
  except json.JSONDecodeError:
    logger.error(
        "Failed to parse GKE_DIAGON_METADATA: %s", diagon_metadata_str
    )
    return None


def _get_gke_workload_details() -> dict[str, Any] | None:
  """Returns workload details if available, otherwise None."""
  identifier = _get_gke_diagon_identifier() or {}
  metadata = _get_gke_diagon_metadata() or {}

  details = {
      "id": identifier.get("metadata.name", ""),
      "kind": identifier.get("metadata.kind", ""),
      "cluster": identifier.get("clustername", ""),
      "namespace": identifier.get("namespace", ""),
      "parent_workload": metadata.get("parent-workload", None),
      "timestamp": metadata.get("timestamp", ""),
  }
  # Parse labels from metadata.
  labels_str = metadata.get("associated-labels", None)
  if labels_str:
    gke_labels = {}
    for pair in labels_str.split(","):
      if "=" in pair:
        key, value = pair.split("=", 1)
        gke_labels[key.strip()] = value.strip()
    details["labels"] = gke_labels
  else:
    details["labels"] = None

  if all(not v for v in details.values()):
    return None

  return details


def _gke_run_identifier(workload_details: dict[str, Any]) -> str:
  """Returns the unique identifier for the gke workload.

  Args:
    workload_details: A dictionary containing workload details.

  Example output:
  cluster-test_namespace-test_kind-test_workloadid-test_20240520-110840
  """

  if not workload_details:
    raise ValueError(
        "Could not generate GKE workload identifier due to missing workload"
        " details. This might be because environment variables"
        " 'GKE_DIAGON_IDENTIFIER' or 'GKE_DIAGON_METADATA' are not set or are"
        " incomplete. Please ensure you are running SDK in a GKE environment"
        " with the GKE diagon operator webhook enabled."
    )

  identifier_keys = ["namespace", "cluster", "kind", "id"]
  metadata_keys = ["timestamp"]
  missed_identifier_keys = []
  missed_metadata_keys = []
  for key in identifier_keys:
    if not workload_details.get(key):
      missed_identifier_keys.append(key)
  for key in metadata_keys:
    if not workload_details.get(key):
      missed_metadata_keys.append(key)

  if missed_identifier_keys or missed_metadata_keys:
    missing_keys_str = ", ".join(missed_identifier_keys + missed_metadata_keys)
    error_message = (
        "Could not generate GKE workload identifier due to missing"
        f" properties: {missing_keys_str}."
    )
    if missed_identifier_keys:
      error_message += (
          " Please check if 'GKE_DIAGON_IDENTIFIER' environment variable is"
          " set correctly."
      )
    if missed_metadata_keys:
      error_message += (
          " Please check if 'GKE_DIAGON_METADATA' environment variable is set"
          " correctly."
      )
    error_message += (
        " Ensure you are running SDK in a GKE environment with the GKE diagon"
        " operator webhook enabled."
    )
    raise ValueError(error_message)

  # Preprocess cluster name and timestamp.
  cluster = workload_details["cluster"].split("/")[-1]
  transformed_timestamp = workload_details["timestamp"]
  transformed_timestamp = transformed_timestamp[:-1] + "+00:00"
  transformed_timestamp = (
      datetime.datetime.fromisoformat(transformed_timestamp)
      .astimezone(datetime.timezone.utc)
      .strftime("%Y%m%d-%H%M%S")
  )

  identifier = (
      f"{cluster}"
      f"-{workload_details['namespace']}"
      f"-{workload_details['kind']}-{workload_details['id']}"
      f"-{transformed_timestamp}"
  )
  return identifier.replace("_", "-").lower()


# Public functions
def get_host_index() -> int:
  """Returns host index."""
  # TODO: b/445435361 - Add support for non-jax workloads.
  return _get_jax_process_index()


def is_master_host() -> bool:
  """Checks if the current host is the master host."""
  return get_host_index() == 0


def get_workload_details() -> dict[str, Any] | None:
  """Returns workload details if available, otherwise None."""
  # TODO: b/444305756 - Add support for non-GKE workloads.
  return _get_gke_workload_details()


def get_identifier(workload_details: dict[str, Any]) -> str:
  """Returns the GCS path for the workload."""
  # TODO: b/444305756 - Add support for non-GKE workloads.

  return _gke_run_identifier(workload_details)


def sanitize_identifier(identifier: str) -> str:
  """Sanitize the identifier for the MLRun."""
  sanitized_id = re.sub(r"[^a-z0-9]+", "-", identifier.lower())
  # Remove leading/trailing hyphens
  sanitized_id = sanitized_id.strip("-")
  return sanitized_id
