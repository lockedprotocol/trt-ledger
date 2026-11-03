"""Repair a broken price rule with Claude when a clinic redesigns its pricing page.

The weekly checker reads each price with a regex. When a page changes and the regex
stops matching, this asks Claude to find the same price on the new page and write a
replacement regex. Nothing Claude says is trusted on its own:
  - the quote it cites must appear word for word in the page text,
  - the price must appear in that quote, and
  - the new regex, run on the page, must return exactly that price.
Only then is the rule replaced. The usual safety rules in check_prices.py still apply
to the value (big jumps are held for a human).

Needs ANTHROPIC_API_KEY (or another credential the Anthropic SDK can find). Without it,
or without the `anthropic` package, repair is skipped and the failure is reported as before.
"""
import json
import re

MODEL = "claude-opus-5-5"
SCHEMA = {
    "type": "object",
    "properties": {
        "found": {"type": "boolean", "description": "false if the page no longer shows this price"},
        "value": {"type": "number", "description": "the price in US dollars, e.g. 129 or 29.95"},
        "quote": {"type": "string", "description": "the shortest exact span of the page text (copied verbatim, 20-200 characters) that states the price"},
        "pattern": {"type": "string", "description": "a Python regular expression with exactly one capture group that matches the quote in the page text and captures only the number, e.g. 'Plan \\\\$(\\\\d+)/mo'"},
    },
    "required": ["found", "value", "quote", "pattern"],
    "additionalProperties": False,
}


def _client():
    try:
        import anthropic
    except ImportError:
        return None, "anthropic package not installed"
    try:
        return anthropic.Anthropic(), None
    except Exception as e:  # no credentials configured
        return None, f"no Anthropic credentials ({e.__class__.__name__})"


def ask_claude(client, page_text, clinic, field_label, old_value):
    prompt = (
        f"This is the visible text of {clinic}'s pricing page. We track their {field_label}, "
        f"which was ${old_value} last time we checked. Find the current {field_label} on this page.\n\n"
        "Rules:\n"
        "- Only report a price that is on this page. If it's gone or ambiguous, set found to false.\n"
        "- The quote must be copied exactly from the page text, character for character.\n"
        "- The pattern runs with Python re.findall on the same page text; the first match's group must be the number.\n\n"
        f"<page>\n{page_text}\n</page>"
    )
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=4000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        return None
    text = next((b.text for b in response.content if b.type == "text"), None)
    return json.loads(text) if text else None


def validate(answer, page_text, read_value):
    """Return (value, pattern) if every check passes, else (None, reason)."""
    if not answer or not answer.get("found"):
        return None, "Claude didn't find the price on the page"
    value, quote, pattern = answer["value"], answer["quote"].strip(), answer["pattern"]
    if len(quote) < 8 or quote not in page_text:
        return None, "the quoted text isn't on the page"
    if not any(abs(float(n.replace(",", "")) - value) < 0.005 for n in re.findall(r"\d[\d,]*(?:\.\d+)?", quote)):
        return None, "the price isn't in the quoted text"
    try:
        if re.compile(pattern).groups != 1:
            return None, "the new rule needs exactly one capture group"
    except re.error:
        return None, "the new rule isn't a valid regex"
    got = read_value({"pattern": pattern}, page_text)
    if got is None or abs(got - value) >= 0.005:
        return None, f"the new rule reads {got}, not {value}"
    return value, pattern


def heal(page_text, clinic, field_label, old_value, rule, read_value, client=None):
    """Propose a repair for `rule`. Returns (new_value, new_pattern, note); the first two are
    None when there's no trustworthy repair. The rule itself is not changed here: the checker
    saves the new pattern only if it accepts the value."""
    if client is None:
        client, why = _client()
        if client is None:
            return None, None, f"repair skipped: {why}"
    mult = rule.get("multiply", 1)
    per_unit = round(old_value / mult, 2)
    if mult != 1:   # e.g. Defy shows a monthly average and we store it x12 as a yearly figure
        field_label = f"{field_label}, which the page shows as a per-month figure (we multiply it by {mult})"
    try:
        answer = ask_claude(client, page_text, clinic, field_label, per_unit)
        value, result = validate(answer, page_text, read_value)
    except Exception as e:   # API or validation errors never break the weekly run
        return None, None, f"repair failed: {e.__class__.__name__}: {e}"
    if value is None:
        return None, None, f"repair rejected: {result}"
    return round(value * mult, 2), result, f"rule repaired by Claude (quote checked on the page): {answer['quote']!r}"
