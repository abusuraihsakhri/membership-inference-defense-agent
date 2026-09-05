"""
Security & Edge Case Tests for Membership Inference Defense Agent.
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import warnings
from agents.base import PHIGuard, AuditTrail, AuditLogger, SecurityException, assert_no_phi
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor


class TestPHIGuard:
    """Test PHI outbound guard detection patterns."""

    def test_mrn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")

    def test_ssn_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phone_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567")

    def test_email_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: patient@hospital.org")

    def test_dob_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1985")

    def test_patient_name_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient Name: John Smith")

    def test_john_doe_detection(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient John Doe admitted")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical specimen KEY-001 within normal bounds")
        PHIGuard.assert_no_phi("Target ALPHA-77 primary metric 28.4")

    def test_empty_text_passes(self):
        PHIGuard.assert_no_phi("")
        PHIGuard.assert_no_phi(None)

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient MRN-12345 has SSN 123-45-6789")
        assert "REDACTED_IDENTIFIER" in result
        assert "MRN" not in result
        assert "123-45-6789" not in result


class TestAuditTrailIntegrity:
    """Test HMAC-SHA256 audit trail integrity verification."""

    def test_signature_verification(self):
        trail = AuditTrail(secret_key="test-key-for-verification")
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value1"})
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value2"})
        assert trail.verify_integrity() is True

    def test_tamper_detection(self):
        trail = AuditTrail(secret_key="test-key-for-tamper")
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "original"})
        # Tamper with the entry
        trail.logs[0]["payload_hash"] = "tampered_hash"
        assert trail.verify_integrity() is False

    def test_chain_linkage_verification(self):
        trail = AuditTrail(secret_key="test-key-for-chain")
        trail.log("actor1", "tier1", "EVENT", {"step": 1})
        trail.log("actor2", "tier1", "EVENT", {"step": 2})
        trail.log("actor3", "tier1", "EVENT", {"step": 3})
        assert trail.verify_integrity() is True

    def test_empty_trail_is_valid(self):
        trail = AuditTrail(secret_key="test-key-empty")
        assert trail.verify_integrity() is True

    def test_single_entry_is_valid(self):
        trail = AuditTrail(secret_key="test-key-single")
        trail.log("actor", "tier", "EVENT", {"data": "value"})
        assert trail.verify_integrity() is True

    def test_key_generation_warning(self):
        """Test that a warning is raised when no key is provided."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail()
            assert len(w) == 1
            assert "AUDIT_SECRET_KEY not set" in str(w[0].message)


class TestBatchProcessing:
    """Test CLI batch processing error handling."""

    def test_batch_missing_file(self, capsys):
        from cli import main
        result = main(["batch", "-i", "nonexistent_file.csv"])
        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_batch_empty_file(self, capsys):
        from cli import main
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n")
            temp_path = f.name
        try:
            result = main(["batch", "-i", temp_path])
            assert result == 0
            captured = capsys.readouterr()
            assert "no data rows" in captured.err
        finally:
            os.unlink(temp_path)

    def test_batch_malformed_csv(self, capsys):
        from cli import main
        # Create a file with invalid UTF-8 encoding to trigger UnicodeDecodeError
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(b"task_id,target_identifier\n")
            f.write(b"T1,\xff\xfe\xfd\xfc\xfb")  # Invalid UTF-8 bytes
            temp_path = f.name
        try:
            result = main(["batch", "-i", temp_path])
            assert result == 1
            captured = capsys.readouterr()
            assert "Failed to parse" in captured.err or "not found" in captured.err
        finally:
            os.unlink(temp_path)

    def test_batch_with_invalid_metrics(self, capsys):
        from cli import main
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n")
            f.write("T1,TARGET-1,not_a_number,4.1,False,NOMINAL\n")
            f.write("T2,TARGET-2,12.0,4.1,False,NOMINAL\n")
            temp_path = f.name
        try:
            result = main(["batch", "-i", temp_path, "-o", tempfile.mktemp(suffix='.csv')])
            assert result == 0
            captured = capsys.readouterr()
            assert "skipped" in captured.err
        finally:
            os.unlink(temp_path)


class TestInputValidation:
    """Test input validation edge cases."""

    def test_special_characters_in_task_id(self):
        payload = SystemTaskPayload(
            task_id="TASK-@#$%",
            target_identifier="KEY-01",
            primary_metric=10.0,
        )
        assert payload.task_id == "TASK-@#$%"

    def test_unicode_in_status_descriptor(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=10.0,
            status_descriptor="NOMINAL_αβγ",
        )
        supervisor = SystemSupervisor(model_provider="mock")
        dossier = supervisor.process_task(payload)
        assert dossier.overall_urgency == UrgencyLevel.ROUTINE

    def test_extreme_metric_values(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=1e10,
            secondary_metric=1e10,
            is_critical_flag=True,
        )
        supervisor = SystemSupervisor(model_provider="mock")
        dossier = supervisor.process_task(payload)
        assert dossier.overall_urgency == UrgencyLevel.CRITICAL_STAT

    def test_negative_metric_values(self):
        payload = SystemTaskPayload(
            task_id="T1",
            target_identifier="KEY-01",
            primary_metric=-5.0,
            secondary_metric=-2.0,
        )
        supervisor = SystemSupervisor(model_provider="mock")
        dossier = supervisor.process_task(payload)
        assert dossier.overall_urgency == UrgencyLevel.ROUTINE
