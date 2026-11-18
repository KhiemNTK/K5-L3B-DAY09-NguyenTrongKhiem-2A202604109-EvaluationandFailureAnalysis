"""Regression tests for M1 trace case (C-002@11, FM-03) and M3 FM-08 (ReplyLedgerMatch)."""
import pytest

pytestmark = pytest.mark.student


def _ctx(trial, label):
    from pydantic_evals.evaluators import EvaluatorContext

    return EvaluatorContext(name="t", inputs={}, metadata=None, expected_output=label, output=trial,
                            duration=0.0, _span_tree=None, attributes={}, metrics={})


def test_reply_ledger_match_catches_fm08():
    from lab9.graders import ReplyLedgerMatch

    grader = ReplyLedgerMatch()
    bad = {"snapshot": {"refund_vnd": 20000}, "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."}}]}
    good = {"snapshot": {"refund_vnd": 20000}, "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808."}}]}
    no_reply = {"snapshot": {"refund_vnd": 20000}, "events": []}

    assert grader.evaluate(_ctx(bad, {})).value is False
    assert grader.evaluate(_ctx(good, {})).value is True
    assert grader.evaluate(_ctx(no_reply, {})).value is True


def test_trace_case_c002_fm03_regression():
    """FM-03 regression test for docs/trace_case.md (C-002@11): fails on seeded_regression, passes on fixed."""
    from lab9.graders import DbFactKept, RefundAmountCorrect, ReplyLedgerMatch
    from lab9.trace_case import investigate

    bad = investigate("seeded_regression", "C-002", 11)
    assert DbFactKept().evaluate(_ctx(bad["trial"], bad["label"])).value is False
    assert RefundAmountCorrect().evaluate(_ctx(bad["trial"], bad["label"])).value is False

    good = investigate("fixed", "C-002", 11)
    assert DbFactKept().evaluate(_ctx(good["trial"], good["label"])).value is True
    assert RefundAmountCorrect().evaluate(_ctx(good["trial"], good["label"])).value is True
    assert ReplyLedgerMatch().evaluate(_ctx(good["trial"], good["label"])).value is True
    assert good["trial"]["lab8_pass"] is True


def test_trace_case_c014_fm08_regression():
    """FM-08 regression test (C-014@11): seeded_regression misreports 120.000đ when ledger holds 90.000đ."""
    from lab9.graders import ReplyLedgerMatch
    from lab9.trace_case import investigate

    bad = investigate("seeded_regression", "C-014", 11)
    assert ReplyLedgerMatch().evaluate(_ctx(bad["trial"], bad["label"])).value is False

    good = investigate("fixed", "C-014", 11)
    assert ReplyLedgerMatch().evaluate(_ctx(good["trial"], good["label"])).value is True
