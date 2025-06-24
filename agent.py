import json, time, os
from pathlib import Path
import openai
from openai import RateLimitError
from jsonschema import validate as _validate, ValidationError

schema = json.load(open(os.path.join(os.path.dirname(__file__), "schema.json")))

tool_spec = {
    "type": "function",
    "function": {
        "name": "process_bill_payment",
        "description": schema["description"],
        "parameters": {
            "type": "object",
            "properties": schema["properties"],
            "required": schema["required"],
        },
    },
}

client = openai.OpenAI()


def validate(payload: dict, sch: dict | None = None) -> None:
    """Thin wrapper so pytest can assert ValidationError is raised."""
    _validate(instance=payload, schema=sch or schema)


def run_chat(txt: str):
    backoff = 0
    while True:
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                tools=[tool_spec],
                tool_choice="auto",
                messages=[{"role": "user", "content": txt}],
            )
            break
        except RateLimitError:
            time.sleep(2 ** backoff); backoff += 1

    # ========== NEW robust handling =====================================
    tool_calls = resp.choices[0].message.tool_calls
    if not tool_calls:               # No function call → just return
        return None

    tool_call = tool_calls[0]        # only one tool defined
    raw_args = tool_call.function.arguments
    tool_args = json.loads(raw_args)
    validate(tool_args)              # raises ValidationError if bad
    # ====================================================================

    from .payments import enqueue_payment
    enqueue_payment(tool_args)

    cost = resp.usage.total_tokens * 1e-5
    print(tool_calls, f"cost=${cost:.4f}")

    return tool_calls


if __name__ == "__main__":
    import sys
    run_chat(" ".join(sys.argv[1:]) or "Pay my $45.99 utility bill before Friday")
