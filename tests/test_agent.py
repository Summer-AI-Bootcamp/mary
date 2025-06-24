import json, pytest
from .. import agent, payments
from jsonschema import ValidationError

# run with pytest -q

GOOD = "Pay the $45.99 utility bill for Denver Water from checking on 2025-07-01."
BAD = "How much do I owe?"


@pytest.mark.parametrize("msg,should_call", [(GOOD, True), (BAD, False)])
def test_intent(monkeypatch, tmp_path, msg, should_call):
    payments.OUTBOX = tmp_path                 # redirect stub outbox

    calls_before = list(tmp_path.iterdir())
    _ = agent.run_chat(msg)                   # uses real OpenAI; OK for smoke

    calls_after = list(tmp_path.iterdir())
    assert (len(calls_after) > len(calls_before)) == should_call


def test_schema_validation_fails(monkeypatch):
    with pytest.raises(ValidationError):
        agent.validate({"amount_due": -5}, agent.schema)
