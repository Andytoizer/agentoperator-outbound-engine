"""Gmail client tests — verify HTML auto-generation + MCP arg shape."""
from clients.gmail import DraftSpec, _plain_to_html, create_draft


def test_plain_to_html_wraps_paragraphs():
    body = "Hey-\n\nFirst paragraph.\n\nSecond paragraph.\n\nAndy"
    html = _plain_to_html(body)
    assert html == "<p>Hey-</p><p>First paragraph.</p><p>Second paragraph.</p><p>Andy</p>"


def test_plain_to_html_ignores_empty_trailing():
    body = "Hey-\n\nBody.\n\n\n\n"
    html = _plain_to_html(body)
    assert html == "<p>Hey-</p><p>Body.</p>"


def test_create_draft_auto_generates_html():
    spec = create_draft(
        to="test@example.com",
        subject="hi",
        body="Hey-\n\nBody line.\n\nAndy",
    )
    assert spec.html_body == "<p>Hey-</p><p>Body line.</p><p>Andy</p>"
    args = spec.to_mcp_args()
    assert args["htmlBody"] == spec.html_body
    assert args["body"] == "Hey-\n\nBody line.\n\nAndy"
    assert args["to"] == ["test@example.com"]
    assert args["subject"] == "hi"


def test_create_draft_accepts_explicit_html():
    spec = create_draft(
        to="test@example.com",
        subject="hi",
        body="Hey-\n\nBody.",
        html_body="<div>custom html</div>",
    )
    assert spec.html_body == "<div>custom html</div>"


def test_create_draft_opts_out_of_html():
    spec = create_draft(
        to="test@example.com",
        subject="hi",
        body="Hey-\n\nBody.",
        html_body="",  # explicit opt-out
    )
    assert spec.html_body is None
    assert "htmlBody" not in spec.to_mcp_args()


def test_create_draft_string_or_list_to():
    single = create_draft(to="a@example.com", subject="x", body="y")
    multi = create_draft(to=["a@example.com", "b@example.com"], subject="x", body="y")
    assert single.to == ["a@example.com"]
    assert multi.to == ["a@example.com", "b@example.com"]
