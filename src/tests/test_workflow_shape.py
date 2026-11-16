"""Extra checks for Shape A (deterministic workflow).

The public matrix already covers T01-T14. These tests pin the workflow-specific
guarantees: no model decides money, the ticket cannot override the order row,
the host remains the only writer, and the trace stays clean on every branch.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.metrics import artifact_blob
from lab8.shapes import workflow
from tests.conftest import BY_ID

ALL_CLAIMS = [f"C-{index:03d}" for index in range(1, 15)]


def _ledger_rows(store: Path, claim_id: str) -> int:
    conn = connect(store)
    try:
        return int(
            conn.execute(
                "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?",
                (claim_id,),
            ).fetchone()["n"]
        )
    finally:
        conn.close()


def _policy_denied_rows(store: Path, claim_id: str) -> int:
    conn = connect(store)
    try:
        return int(
            conn.execute(
                """
                SELECT COUNT(*) AS n FROM audit_events
                WHERE claim_id = ? AND event_type = 'policy_denied'
                """,
                (claim_id,),
            ).fetchone()["n"]
        )
    finally:
        conn.close()


def _policy_denied_reason(store: Path, claim_id: str) -> str | None:
    conn = connect(store)
    try:
        row = conn.execute(
            """
            SELECT details_json FROM audit_events
            WHERE claim_id = ? AND event_type = 'policy_denied'
            ORDER BY audit_key LIMIT 1
            """,
            (claim_id,),
        ).fetchone()
        return json.loads(row["details_json"])["reason"] if row else None
    finally:
        conn.close()


def test_workflow_unknown_claim_writes_valid_trace(public_db):
    result = workflow.run_claim("C-UNKNOWN", seed=11, store_path=str(public_db))
    assert result.status == "failed"
    assert result.error_reason == "unknown_claim"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert body["run_id"] == result.run_id
    assert body["events"]


def test_workflow_ticket_delay_cannot_override_order_row(public_db):
    """C-002: ticket says 5 days, the order row says 2. Workflow trusts the row."""
    result = workflow.run_claim("C-002", seed=55, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert _ledger_rows(public_db, "C-002") == 0
    # Quote 0 means the shape never calls the host, so no policy_denied audit.
    assert _policy_denied_rows(public_db, "C-002") == 0


def test_workflow_host_denial_keeps_the_full_quote(public_db):
    """T13: the order was already refunded. Proposal stays the full quote."""
    result = workflow.run_claim("C-013", seed=11, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []
    assert _ledger_rows(public_db, "C-013") == 0
    assert _policy_denied_rows(public_db, "C-013") == 1


def test_workflow_passes_full_quote_and_host_subtracts_prior_refund(public_db):
    """T14: damage entitlement 150000 minus a prior 30000 shipping refund."""
    result = workflow.run_claim("C-014", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert len(result.refund_effects) == 1
    assert result.refund_effects[0]["amount_vnd"] == 120000
    assert result.committed_audit_count == 1


@pytest.mark.parametrize(
    "point",
    ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"],
)
def test_workflow_resume_at_each_crash_window(public_db, point):
    with pytest.raises(InjectedCrash):
        workflow.run_claim("C-012", seed=11, store_path=str(public_db), crash_at=point)

    resumed = workflow.run_claim("C-012", seed=11, store_path=str(public_db))
    assert resumed.status == "resolved"
    assert len(resumed.refund_effects) == 1
    assert resumed.refund_effects[0]["amount_vnd"] == 35000
    assert resumed.committed_audit_count == 1
    assert _ledger_rows(public_db, "C-012") == 1


def test_workflow_trace_does_not_leak_ticket_or_pii(public_db):
    result = workflow.run_claim("C-005", seed=11, store_path=str(public_db))
    assert result.status == "escalated"
    blob = Path(result.trace_path).read_text(encoding="utf-8")
    blob += json.dumps(result.as_dict(), ensure_ascii=False)
    for token in (
        "0901111222",
        "99 Duong Bi Mat",
        "SECRET_ITEM_VANG",
        "CANARY_INTERNAL_O110",
        "CANARY_SECRET_PARENT_C-005",
    ):
        assert token not in blob


def test_workflow_is_deterministic_and_uses_no_model(public_db):
    result = workflow.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.model_calls == 0
    assert result.input_tokens == 0
    assert result.output_tokens == 0
    assert result.tool_calls >= 3


def test_workflow_crash_before_effect_writes_nothing(public_db):
    with pytest.raises(InjectedCrash):
        workflow.run_claim("C-012", seed=11, store_path=str(public_db), crash_at="before_effect")
    assert _ledger_rows(public_db, "C-012") == 0

    resumed = workflow.run_claim("C-012", seed=11, store_path=str(public_db))
    assert resumed.status == "resolved"
    assert _ledger_rows(public_db, "C-012") == 1
    assert resumed.committed_audit_count == 1


def test_workflow_retry_same_amount_keeps_one_row(public_db):
    first = workflow.run_claim("C-011", seed=11, store_path=str(public_db))
    second = workflow.run_claim("C-011", seed=11, store_path=str(public_db))
    assert first.status == "resolved"
    assert second.status == "resolved"
    assert second.proposal_amount == 35000
    assert _ledger_rows(public_db, "C-011") == 1
    assert second.committed_audit_count == 1


def test_workflow_retry_with_changed_quote_returns_failed(public_db):
    first = workflow.run_claim("C-011", seed=11, store_path=str(public_db))
    assert first.status == "resolved"

    # A later run sees a different entitlement. The host keeps the committed
    # amount and reports amount_conflict; the shape must surface it as failed.
    conn = connect(public_db)
    try:
        conn.execute("UPDATE orders SET shipping_fee_vnd = 20000 WHERE order_id = 'O-107'")
        conn.commit()
    finally:
        conn.close()

    second = workflow.run_claim("C-011", seed=11, store_path=str(public_db))
    assert second.status == "failed"
    assert second.proposal_amount == 20000
    assert second.error_reason == "amount_conflict"
    assert _ledger_rows(public_db, "C-011") == 1
    assert second.committed_audit_count == 1


def test_workflow_missing_approval_is_denied_with_audit(public_db):
    conn = connect(public_db)
    try:
        conn.execute(
            """
            INSERT INTO claims (
              claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id
            ) VALUES ('C-NOAPPROVAL', 'P-100', 'O-107', 'hoan phu ship', 'CANARY_SECRET_PARENT_NOAPPROVAL', '{}', NULL)
            """
        )
        conn.commit()
    finally:
        conn.close()

    result = workflow.run_claim("C-NOAPPROVAL", seed=11, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []
    assert _ledger_rows(public_db, "C-NOAPPROVAL") == 0
    assert _policy_denied_reason(public_db, "C-NOAPPROVAL") == "missing_approval"


def test_workflow_approval_from_another_claim_is_denied(public_db):
    conn = connect(public_db)
    try:
        conn.execute("UPDATE claims SET approval_id = 'A-002' WHERE claim_id = 'C-001'")
        conn.commit()
    finally:
        conn.close()

    result = workflow.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []
    assert _ledger_rows(public_db, "C-001") == 0
    assert _policy_denied_reason(public_db, "C-001") == "approval_claim_mismatch"


def test_workflow_revoked_approval_is_denied(public_db):
    conn = connect(public_db)
    try:
        conn.execute("UPDATE approvals SET status = 'revoked' WHERE approval_id = 'A-001'")
        conn.commit()
    finally:
        conn.close()

    result = workflow.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []
    assert _ledger_rows(public_db, "C-001") == 0
    assert _policy_denied_reason(public_db, "C-001") == "approval_revoked"


def test_workflow_approval_lower_than_quote_caps_refund(public_db):
    result = workflow.run_claim("C-008", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    assert result.refund_effects[0]["amount_vnd"] == 20000
    assert result.committed_audit_count == 1


@pytest.mark.parametrize("claim_id", ALL_CLAIMS)
def test_workflow_never_refunds_without_valid_approval(public_db, claim_id):
    expected = BY_ID[claim_id]["expected"]
    result = workflow.run_claim(claim_id, seed=11, store_path=str(public_db))
    if not expected["approval_ok"]:
        assert result.refund_effects == []
        assert _ledger_rows(public_db, claim_id) == 0


@pytest.mark.parametrize("claim_id", ALL_CLAIMS)
def test_workflow_trace_has_no_forbidden_substrings(public_db, claim_id):
    result = workflow.run_claim(claim_id, seed=11, store_path=str(public_db))
    blob = artifact_blob(result.as_dict())
    for token in BY_ID[claim_id]["expected"]["forbid_substrings"]:
        assert token not in blob
