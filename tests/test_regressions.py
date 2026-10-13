"""Regression coverage for finite metrics, PHI rejection, and browser/API safety."""

import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from agents.api import app
from agents.base import AuditTrail, SecurityException
from agents.llm_factory import LLMFactory
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from mia_defense.models import FrontierPayload


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_non_finite_metrics_rejected(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="KEY", primary_metric=value)
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="KEY", primary_metric=1.0, secondary_metric=value)
    with pytest.raises(ValueError):
        FrontierPayload("T", "KEY", value, 1.0, "NOMINAL")


def test_supervisor_rejects_metadata_identifiers():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="T", target_identifier="KEY", primary_metric=1.0,
        attributes={"nested": {"contact": "person@hospital.example"}}
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


def test_audit_readers_cannot_mutate_live_chain():
    trail = AuditTrail(secret_key="regression-test-key")
    trail.log("test", "worker", "EVENT", {"data": "ok"})
    snapshot = trail.get_trail()
    snapshot[0]["current_hash"] = "tampered"
    assert trail.verify_integrity()
    del trail.logs[0]["timestamp"]
    assert not trail.verify_integrity()


def test_mock_provider_makes_no_unsupported_model_claims():
    result = LLMFactory.create("mock").invoke("What is the status?")
    assert "No language-model inference" in result
    with pytest.raises(ValueError, match="not implemented"):
        LLMFactory.create("openai")


def test_api_rejects_phi_with_422():
    client = TestClient(app)
    res = client.post("/api/audit", json={
        "task_id": "T", "target_identifier": "KEY",
        "primary_metric": 1.0,
        "attributes": {"contact": "person@hospital.example"},
    })
    assert res.status_code == 422
    assert "person@hospital.example" not in res.text


def test_web_home_uses_local_preview_without_fabricated_audits():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert 'value="local"' in response.text
    assert "LOCAL_PREVIEW" in response.text
    assert "Math.random" not in response.text
    assert "HMAC_SHA256_e83" not in response.text


def test_api_nominal_and_schema():
    response = TestClient(app).post("/api/audit", json={
        "task_id": "REGRESSION-OK", "target_identifier": "KEY",
        "primary_metric": 1.0, "secondary_metric": 1.0,
        "status_descriptor": "NOMINAL"
    })
    assert response.status_code == 200
    assert response.json()["overall_urgency"] == "ROUTINE"
    assert len(response.json()["audit_hash"]) == 64
