"""Public-source collection pipeline for Zambia Digital Lending Ops Radar."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sqlite3
import ssl
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCAL_PYDEPS = ROOT / ".scraping-pydeps"
if LOCAL_PYDEPS.exists():
    sys.path.append(str(LOCAL_PYDEPS))

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_SOURCES = ROOT / "lending_ops_radar" / "sources.json"
DEFAULT_DB = ROOT / "data" / "lending_ops_radar.sqlite3"

from lending_ops_radar.intelligence import (
    assessment_table_rows,
    build_assessments,
    coverage_gaps,
    domain_counts,
    top_interpretive_findings,
)
from lending_ops_radar.competitor_watch import lens_counts, triage_rows

CLASSIFICATION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "complaint": ("complaint", "complaints", "report incident", "support issue", "service issue"),
    "fees": ("fee", "fees", "charges", "pricing", "cost", "interest", "terms"),
    "disbursement": ("disbursement", "payout", "paid out", "cash out", "mobile money", "wallet"),
    "repayment": ("repayment", "repay", "payment", "incomplete transaction", "transaction", "deduction"),
    "collections": ("collection", "collections", "overdue", "arrears", "late payment", "recovery"),
    "privacy": ("privacy", "personal data", "data protection", "data subject", "consent", "controller", "processor"),
    "fraud": ("fraud", "scam", "stolen", "lost", "unsolicited", "phishing", "impersonation"),
    "regulatory": (
        "regulation",
        "regulatory",
        "licensing",
        "licence",
        "license",
        "directive",
        "circular",
        "rules",
        "consumer protection",
        "consumer rights",
        "fair competition",
    ),
    "competitor_change": ("faq", "terms", "eligibility", "offer", "loan amount", "application", "approval"),
    "news_signal": ("press", "news", "public notice", "statement", "market", "report"),
}

RISK_KEYWORDS: dict[str, tuple[str, ...]] = {
    "high": ("fraud", "scam", "privacy", "harassment", "misleading", "illegal", "stolen", "regulatory"),
    "medium": ("complaint", "fee", "incomplete transaction", "delay", "unsolicited", "support"),
}

BOILERPLATE_PATTERNS = (
    "all rights reserved",
    "copyright ©",
    "copyright (c)",
    "terms and conditions",
    "privacy policy",
    "cookie policy",
    "powered by",
)


@dataclass(frozen=True)
class SourceConfig:
    source_id: str
    name: str
    source_type: str
    url: str
    fetcher: str
    frequency: str
    category: str
    keywords: tuple[str, ...]
    exclude_keywords: tuple[str, ...]
    exclude_exact_titles: tuple[str, ...]
    verify_ssl: bool
    compliance_notes: str
    list_selector: str = "a"
    url_include: tuple[str, ...] = ()
    title_min_length: int = 12
    max_pdf_pages: int = 30
    max_json_pages: int = 10
    min_year: int | None = None
    enabled: bool = True


@dataclass
class SimpleElement:
    tag: str
    text: str
    attrib: dict[str, str]


@dataclass
class SimpleResponse:
    url: str
    text: str
    status: int | None
    content_type: str = "html"


class PublicPageParser(HTMLParser):
    def __init__(self, wanted_tags: set[str]) -> None:
        super().__init__()
        self.wanted_tags = wanted_tags
        self.items: list[SimpleElement] = []
        self._stack: list[dict[str, Any]] = []
        self._all_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.wanted_tags:
            self._stack.append({"tag": tag, "attrs": {k: v or "" for k, v in attrs}, "text": []})

    def handle_data(self, data: str) -> None:
        text = html.unescape(data)
        self._all_text.append(text)
        for item in self._stack:
            item["text"].append(text)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._stack) - 1, -1, -1):
            item = self._stack[index]
            if item["tag"] != tag:
                continue
            text = normalize_text(" ".join(item["text"]))
            if text:
                self.items.append(SimpleElement(tag=tag, text=text, attrib=item["attrs"]))
            del self._stack[index]
            break

    @property
    def full_text(self) -> str:
        return normalize_text(" ".join(self._all_text))


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_sources(path: Path = DEFAULT_SOURCES) -> list[SourceConfig]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    sources: list[SourceConfig] = []
    for item in payload:
        sources.append(
            SourceConfig(
                source_id=item["source_id"],
                name=item["name"],
                source_type=item["source_type"],
                url=item["url"],
                fetcher=item.get("fetcher", "http"),
                frequency=item.get("frequency", "weekly"),
                category=item.get("category", "news_signal"),
                keywords=tuple(k.lower() for k in item.get("keywords", [])),
                exclude_keywords=tuple(k.lower() for k in item.get("exclude_keywords", [])),
                exclude_exact_titles=tuple(normalize_text(k).lower() for k in item.get("exclude_exact_titles", [])),
                verify_ssl=bool(item.get("verify_ssl", True)),
                compliance_notes=item.get("compliance_notes", ""),
                list_selector=item.get("list_selector", "a"),
                url_include=tuple(item.get("url_include", [])),
                title_min_length=int(item.get("title_min_length", 12)),
                max_pdf_pages=int(item.get("max_pdf_pages", 30)),
                max_json_pages=int(item.get("max_json_pages", 10)),
                min_year=int(item["min_year"]) if item.get("min_year") is not None else None,
                enabled=bool(item.get("enabled", True)),
            )
        )
    return sources


def connect(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sources (
            source_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            url TEXT NOT NULL,
            fetcher TEXT NOT NULL,
            frequency TEXT NOT NULL,
            category TEXT NOT NULL,
            keywords_json TEXT NOT NULL,
            exclude_keywords_json TEXT NOT NULL DEFAULT '[]',
            compliance_notes TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL UNIQUE,
            source_id TEXT NOT NULL,
            source_name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_url TEXT NOT NULL,
            item_title TEXT NOT NULL,
            item_url TEXT,
            category TEXT NOT NULL,
            classification TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            matched_keywords_json TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            status_code INTEGER,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            UNIQUE(source_id, item_url, item_title)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            signal_id INTEGER PRIMARY KEY,
            review_status TEXT NOT NULL DEFAULT 'new',
            priority INTEGER NOT NULL DEFAULT 2,
            reviewer_notes TEXT NOT NULL DEFAULT '',
            recommended_action TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            FOREIGN KEY(signal_id) REFERENCES signals(id)
        );

        CREATE TABLE IF NOT EXISTS page_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            snapshot_hash TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS brief_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id INTEGER NOT NULL,
            week_label TEXT NOT NULL,
            section TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE(signal_id, week_label),
            FOREIGN KEY(signal_id) REFERENCES signals(id)
        );

        CREATE TABLE IF NOT EXISTS source_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            source_url TEXT NOT NULL,
            run_status TEXT NOT NULL,
            signal_count INTEGER NOT NULL DEFAULT 0,
            error_message TEXT NOT NULL DEFAULT '',
            started_at TEXT NOT NULL,
            finished_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS research_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id INTEGER,
            note_type TEXT NOT NULL,
            title TEXT NOT NULL,
            note TEXT NOT NULL,
            market_question TEXT NOT NULL DEFAULT '',
            confidence TEXT NOT NULL DEFAULT 'medium',
            created_at TEXT NOT NULL,
            FOREIGN KEY(signal_id) REFERENCES signals(id)
        );

        CREATE TABLE IF NOT EXISTS learning_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_key TEXT NOT NULL UNIQUE,
            capability_area TEXT NOT NULL,
            goal TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            evidence TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS source_quality (
            source_id TEXT PRIMARY KEY,
            run_count INTEGER NOT NULL DEFAULT 0,
            success_count INTEGER NOT NULL DEFAULT 0,
            fail_count INTEGER NOT NULL DEFAULT 0,
            last_status TEXT NOT NULL DEFAULT '',
            last_error TEXT NOT NULL DEFAULT '',
            last_signal_count INTEGER NOT NULL DEFAULT 0,
            total_signal_count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS market_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_key TEXT NOT NULL UNIQUE,
            area TEXT NOT NULL,
            question TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            current_hypothesis TEXT NOT NULL DEFAULT '',
            evidence TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL
        );
        """
    )
    ensure_column(conn, "sources", "exclude_keywords_json", "TEXT NOT NULL DEFAULT '[]'")
    ensure_column(conn, "sources", "enabled", "INTEGER NOT NULL DEFAULT 1")
    conn.commit()


def ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
    if column_name not in columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def upsert_sources(conn: sqlite3.Connection, sources: list[SourceConfig]) -> None:
    for source in sources:
        conn.execute(
            """
            INSERT INTO sources (
                source_id, name, source_type, url, fetcher, frequency, category,
                keywords_json, exclude_keywords_json, compliance_notes, enabled, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_id) DO UPDATE SET
                name=excluded.name,
                source_type=excluded.source_type,
                url=excluded.url,
                fetcher=excluded.fetcher,
                frequency=excluded.frequency,
                category=excluded.category,
                keywords_json=excluded.keywords_json,
                exclude_keywords_json=excluded.exclude_keywords_json,
                compliance_notes=excluded.compliance_notes,
                enabled=excluded.enabled,
                updated_at=excluded.updated_at
            """,
            (
                source.source_id,
                source.name,
                source.source_type,
                source.url,
                source.fetcher,
                source.frequency,
                source.category,
                json.dumps(source.keywords, ensure_ascii=False),
                json.dumps(source.exclude_keywords, ensure_ascii=False),
                source.compliance_notes,
                1 if source.enabled else 0,
                now_iso(),
            ),
        )
    conn.commit()


def import_scrapling_fetchers() -> tuple[Any, Any, Any] | None:
    try:
        from scrapling.fetchers import DynamicFetcher, Fetcher, StealthyFetcher
    except ModuleNotFoundError as exc:
        print(f"  Scrapling fetchers unavailable, using HTTP fallback where possible: {exc}")
        return None
    return Fetcher, DynamicFetcher, StealthyFetcher


def import_pdf_reader() -> Any:
    try:
        from pypdf import PdfReader
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "PDF sources need pypdf. Install/update dependencies with: "
            "python -m pip install -r requirements-lending-radar.txt"
        ) from exc
    return PdfReader


def fetch_source(source: SourceConfig, timeout_ms: int) -> Any:
    if source.fetcher == "pdf" or source.url.lower().split("?", 1)[0].endswith(".pdf"):
        return fetch_pdf_source(source, timeout_ms)
    if source.fetcher == "jsonapi":
        return fetch_jsonapi_source(source, timeout_ms)

    fetchers = import_scrapling_fetchers()
    if fetchers is None:
        if source.fetcher == "http":
            return fetch_source_with_urllib(source, timeout_ms)
        raise SystemExit(
            "Dynamic fetching needs scrapling[fetchers]. Install dependencies with: "
            "python -m pip install --target .lending-pydeps -r requirements-lending-radar.txt"
        )

    Fetcher, DynamicFetcher, StealthyFetcher = fetchers
    if source.fetcher == "http":
        try:
            return Fetcher.get(
                source.url,
                stealthy_headers=True,
                timeout=timeout_ms,
                follow_redirects="safe",
            )
        except Exception as exc:
            if source.verify_ssl:
                raise
            print(f"  Scrapling HTTP fetch failed, using configured public-source SSL fallback: {exc}")
            return fetch_source_with_urllib(source, timeout_ms)
    if source.fetcher == "dynamic":
        return DynamicFetcher.fetch(
            source.url,
            headless=True,
            network_idle=True,
            disable_resources=True,
            timeout=timeout_ms,
            follow_redirects="safe",
        )
    if source.fetcher == "stealthy":
        return StealthyFetcher.fetch(
            source.url,
            headless=True,
            network_idle=True,
            disable_resources=True,
            timeout=timeout_ms,
            follow_redirects="safe",
        )
    raise ValueError(f"Unknown fetcher type: {source.fetcher}")


def fetch_jsonapi_source(source: SourceConfig, timeout_ms: int) -> SimpleResponse:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ZambiaDigitalLendingOpsRadar/0.1; public-source-monitor)",
        "Accept": "application/vnd.api+json,application/json,*/*",
    }
    context = None if source.verify_ssl else ssl._create_unverified_context()
    next_url: str | None = source.url
    status: int | None = None
    page_count = 0
    seen_urls: set[str] = set()
    combined: dict[str, Any] = {"data": [], "included": []}
    seen_data: set[str] = set()
    seen_included: set[str] = set()

    while next_url and page_count < source.max_json_pages and next_url not in seen_urls:
        seen_urls.add(next_url)
        request = Request(next_url, headers=headers)
        with urlopen(request, timeout=max(1, timeout_ms / 1000), context=context) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            body = response.read().decode(charset, errors="replace")
            status = getattr(response, "status", None)
        payload = json.loads(body)

        data = payload.get("data", [])
        records = [data] if isinstance(data, dict) else data if isinstance(data, list) else []
        for record in records:
            record_key = f"{record.get('type')}:{record.get('id')}"
            if record_key not in seen_data:
                combined["data"].append(record)
                seen_data.add(record_key)

        included = payload.get("included", [])
        if isinstance(included, list):
            for item in included:
                item_key = f"{item.get('type')}:{item.get('id')}"
                if item_key not in seen_included:
                    combined["included"].append(item)
                    seen_included.add(item_key)

        next_href = payload.get("links", {}).get("next", {}).get("href")
        next_url = urljoin(next_url, next_href) if next_href else None
        page_count += 1

    return SimpleResponse(
        url=source.url,
        text=json.dumps(combined, ensure_ascii=False),
        status=status,
        content_type="jsonapi",
    )


def fetch_pdf_source(source: SourceConfig, timeout_ms: int) -> SimpleResponse:
    PdfReader = import_pdf_reader()
    request = Request(
        source.url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ZambiaDigitalLendingOpsRadar/0.1; public-source-monitor)",
            "Accept": "application/pdf,*/*",
        },
    )
    context = None if source.verify_ssl else ssl._create_unverified_context()
    with urlopen(request, timeout=max(1, timeout_ms / 1000), context=context) as response:
        data = response.read()
        status = getattr(response, "status", None)

    reader = PdfReader(BytesIO(data), strict=False)
    pages: list[str] = []
    for page_index, page in enumerate(reader.pages[: source.max_pdf_pages]):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        text = text.strip()
        if text:
            pages.append(f"[[page:{page_index + 1}]]\n{text}")

    body = "\n\n".join(pages)
    if not body:
        body = f"[[page:1]]\n{source.name} PDF fetched, but no extractable text was found."
    return SimpleResponse(url=source.url, text=body, status=status, content_type="pdf")


def fetch_source_with_urllib(source: SourceConfig, timeout_ms: int) -> SimpleResponse:
    request = Request(
        source.url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; ZambiaDigitalLendingOpsRadar/0.1; public-source-monitor)"
        },
    )
    context = None if source.verify_ssl else ssl._create_unverified_context()
    with urlopen(request, timeout=max(1, timeout_ms / 1000), context=context) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read().decode(charset, errors="replace")
        return SimpleResponse(url=source.url, text=body, status=getattr(response, "status", None))


def pdf_page_blocks(text: str) -> list[tuple[int, str]]:
    matches = list(re.finditer(r"\[\[page:(\d+)\]\]\s*", text))
    if not matches:
        return [(1, text)]

    blocks: list[tuple[int, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        page_text = text[start:end].strip()
        if page_text:
            blocks.append((int(match.group(1)), page_text))
    return blocks


def chunk_pdf_text(text: str, max_chars: int = 900) -> list[str]:
    parts = [normalize_text(part) for part in re.split(r"\n\s*\n+", text) if normalize_text(part)]
    if len(parts) <= 1:
        parts = [normalize_text(line) for line in text.splitlines() if normalize_text(line)]

    chunks: list[str] = []
    current: list[str] = []
    for part in parts:
        candidate = " ".join(current + [part])
        if len(candidate) > max_chars and current:
            chunks.append(" ".join(current))
            current = [part]
        else:
            current.append(part)
    if current:
        chunks.append(" ".join(current))
    return chunks


def pdf_response_items(response: SimpleResponse) -> list[SimpleElement]:
    items: list[SimpleElement] = []
    for page_number, page_body in pdf_page_blocks(response.text):
        for chunk_index, chunk in enumerate(chunk_pdf_text(page_body)):
            if len(chunk) < 40:
                continue
            items.append(
                SimpleElement(
                    tag="pdf",
                    text=f"Page {page_number}: {chunk}",
                    attrib={"href": f"{response.url}#page={page_number}-item-{chunk_index + 1}"},
                )
            )
    return items


def clean_markup(value: Any) -> str:
    text = html.unescape("" if value is None else str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    return normalize_text(text)


def jsonapi_response_items(response: SimpleResponse) -> list[SimpleElement]:
    try:
        payload = json.loads(response.text)
    except json.JSONDecodeError:
        return []

    data = payload.get("data")
    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        records = []

    included_items = payload.get("included", [])
    if not isinstance(included_items, list):
        included_items = []

    included: dict[str, dict[str, Any]] = {}
    for item in included_items:
        item_type = item.get("type")
        item_id = item.get("id")
        if item_type and item_id:
            included[f"{item_type}:{item_id}"] = item

    items: list[SimpleElement] = []
    for index, record in enumerate(records):
        attrs = record.get("attributes", {}) if isinstance(record, dict) else {}
        relationships = record.get("relationships", {}) if isinstance(record, dict) else {}
        title = clean_markup(attrs.get("title"))
        if not title:
            continue
        date = clean_markup(attrs.get("field_regulatory_date") or attrs.get("created"))

        category = ""
        category_ref = relationships.get("field_regulatory_framework_categ", {}).get("data")
        if isinstance(category_ref, dict):
            category_node = included.get(f"{category_ref.get('type')}:{category_ref.get('id')}", {})
            category = clean_markup(category_node.get("attributes", {}).get("name"))

        file_url = ""
        file_ref = relationships.get("field_regulatory_file", {}).get("data")
        if isinstance(file_ref, dict):
            file_node = included.get(f"{file_ref.get('type')}:{file_ref.get('id')}", {})
            file_url = clean_markup(file_node.get("attributes", {}).get("uri", {}).get("url"))
            file_url = urljoin(response.url, file_url) if file_url else ""

        tag_names: list[str] = []
        tag_refs = relationships.get("field_regulatory_tags", {}).get("data") or []
        if isinstance(tag_refs, list):
            for tag_ref in tag_refs:
                if not isinstance(tag_ref, dict):
                    continue
                tag_node = included.get(f"{tag_ref.get('type')}:{tag_ref.get('id')}", {})
                tag_name = clean_markup(tag_node.get("attributes", {}).get("name"))
                if tag_name:
                    tag_names.append(tag_name)

        parts = [part for part in [date, category, title] if part]
        if tag_names:
            parts.append("Tags: " + ", ".join(tag_names))
        if file_url:
            parts.append("File: " + file_url)
        items.append(
            SimpleElement(
                tag="jsonapi",
                text=" | ".join(parts),
                attrib={"href": file_url or f"{response.url}#item-{index}"},
            )
        )
    return items


def select_items(response: Any, selector: str) -> list[Any]:
    if isinstance(response, SimpleResponse):
        if response.content_type == "pdf":
            return pdf_response_items(response)
        if response.content_type == "jsonapi":
            return jsonapi_response_items(response)
        tags = {part.strip().split()[0] for part in selector.split(",") if part.strip()}
        tags = {tag for tag in tags if re.match(r"^[a-zA-Z0-9]+$", tag)}
        parser = PublicPageParser(tags or {"a", "h1", "h2", "h3", "p", "li"})
        parser.feed(response.text)
        return parser.items

    items: list[Any] = []
    for part in [s.strip() for s in selector.split(",") if s.strip()]:
        try:
            items.extend(list(response.css(part)))
        except Exception:
            continue
    return items


def item_text(item: Any) -> str:
    if isinstance(item, SimpleElement):
        return normalize_text(item.text)

    parts: list[str] = []
    for selector in ("::text", "span::text", "td::text", "div::text", "li::text"):
        try:
            parts.extend(normalize_text(x) for x in item.css(selector).getall())
        except Exception:
            continue
    text = " ".join(part for part in parts if part)
    if not text:
        text = normalize_text(getattr(item, "text", ""))
    return normalize_text(text)


def item_href(item: Any, base_url: str, index: int) -> str:
    href = None
    try:
        href = item.attrib.get("href")
    except Exception:
        href = None
    if not href:
        try:
            href = item.css("::attr(href)").get()
        except Exception:
            href = None
    if href:
        return urljoin(base_url, str(href))
    return f"{base_url}#item-{index}"


def keyword_hits(text: str, keywords: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in keywords if keyword in lowered]


def has_excluded_keyword(text: str, exclude_keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in exclude_keywords)


def has_excluded_exact_title(text: str, exclude_exact_titles: tuple[str, ...]) -> bool:
    normalized = normalize_text(text).lower()
    return normalized in exclude_exact_titles


def is_before_min_year(text: str, min_year: int | None) -> bool:
    if min_year is None:
        return False
    match = re.search(r"\b(19\d{2}|20\d{2})-\d{2}-\d{2}\b", text)
    if not match:
        return False
    return int(match.group(1)) < min_year


def classify_signal(text: str, default_category: str) -> str:
    lowered = text.lower()
    for label, keywords in CLASSIFICATION_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return label
    return default_category or "news_signal"


def risk_level(text: str) -> str:
    lowered = text.lower()
    if any(keyword in lowered for keyword in RISK_KEYWORDS["high"]):
        return "high"
    if any(keyword in lowered for keyword in RISK_KEYWORDS["medium"]):
        return "medium"
    return "low"


def is_boilerplate_signal(text: str) -> bool:
    lowered = normalize_text(text).lower()
    if not lowered:
        return True
    return any(pattern in lowered for pattern in BOILERPLATE_PATTERNS)


def signal_uid(source_id: str, item_url: str, title: str) -> str:
    payload = f"{source_id}|{item_url}|{normalize_text(title).lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def page_text(response: Any) -> str:
    if isinstance(response, SimpleResponse):
        if response.content_type == "pdf":
            return normalize_text(response.text)
        if response.content_type == "jsonapi":
            return normalize_text(" ".join(item.text for item in jsonapi_response_items(response)))
        parser = PublicPageParser({"title", "h1", "h2", "h3", "p", "li", "a", "option"})
        parser.feed(response.text)
        return parser.full_text

    try:
        return normalize_text(" ".join(str(x) for x in response.css("body ::text").getall()))
    except Exception:
        return normalize_text(getattr(response, "text", ""))


def record_snapshot(conn: sqlite3.Connection, source: SourceConfig, raw_text: str) -> None:
    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    conn.execute(
        """
        INSERT INTO page_snapshots (source_id, source_url, snapshot_hash, raw_text, fetched_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (source.source_id, source.url, digest, raw_text[:20000], now_iso()),
    )


def record_source_run(
    conn: sqlite3.Connection,
    source: SourceConfig,
    run_status: str,
    signal_count: int,
    error_message: str,
    started_at: str,
) -> None:
    conn.execute(
        """
        INSERT INTO source_runs (
            source_id, source_url, run_status, signal_count, error_message,
            started_at, finished_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source.source_id,
            source.url,
            run_status,
            signal_count,
            error_message[:1000],
            started_at,
            now_iso(),
        ),
    )
    success_inc = 1 if run_status == "success" else 0
    fail_inc = 1 if run_status != "success" else 0
    conn.execute(
        """
        INSERT INTO source_quality (
            source_id, run_count, success_count, fail_count, last_status,
            last_error, last_signal_count, total_signal_count, updated_at
        )
        VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_id) DO UPDATE SET
            run_count=source_quality.run_count + 1,
            success_count=source_quality.success_count + excluded.success_count,
            fail_count=source_quality.fail_count + excluded.fail_count,
            last_status=excluded.last_status,
            last_error=excluded.last_error,
            last_signal_count=excluded.last_signal_count,
            total_signal_count=source_quality.total_signal_count + excluded.total_signal_count,
            updated_at=excluded.updated_at
        """,
        (
            source.source_id,
            success_inc,
            fail_inc,
            run_status,
            error_message[:1000],
            signal_count,
            signal_count,
            now_iso(),
        ),
    )


def extract_candidates(source: SourceConfig, response: Any) -> list[dict[str, Any]]:
    raw_page_text = page_text(response)
    candidates: list[dict[str, Any]] = []
    for index, item in enumerate(select_items(response, source.list_selector)):
        text = item_text(item)
        if len(text) < source.title_min_length:
            continue
        if is_boilerplate_signal(text):
            continue
        if has_excluded_exact_title(text, source.exclude_exact_titles):
            continue
        if is_before_min_year(text, source.min_year):
            continue
        href = item_href(item, source.url, index)
        if source.url_include and not any(pattern.lower() in href.lower() for pattern in source.url_include):
            continue
        if has_excluded_keyword(text, source.exclude_keywords):
            continue
        hits = keyword_hits(text, source.keywords)
        if source.keywords and not hits:
            continue
        candidates.append(build_candidate(source, text, href, hits, getattr(response, "status", None)))

    if not candidates and raw_page_text:
        hits = keyword_hits(raw_page_text, source.keywords)
        if (
            (hits or not source.keywords)
            and not is_boilerplate_signal(raw_page_text)
            and not has_excluded_keyword(raw_page_text, source.exclude_keywords)
        ):
            candidates.append(
                build_candidate(
                    source,
                    f"{source.name} page snapshot",
                    source.url,
                    hits,
                    getattr(response, "status", None),
                    raw_text=raw_page_text[:1200],
                )
            )

    return candidates


def build_candidate(
    source: SourceConfig,
    title: str,
    item_url: str,
    hits: list[str],
    status_code: int | None,
    raw_text: str | None = None,
) -> dict[str, Any]:
    text = raw_text or title
    classification = classify_signal(text, source.category)
    return {
        "uid": signal_uid(source.source_id, item_url, title),
        "source_id": source.source_id,
        "source_name": source.name,
        "source_type": source.source_type,
        "source_url": source.url,
        "item_title": normalize_text(title)[:300],
        "item_url": item_url,
        "category": source.category,
        "classification": classification,
        "risk_level": risk_level(text),
        "matched_keywords": hits,
        "raw_text": normalize_text(text)[:2000],
        "status_code": status_code,
    }


def insert_signal(conn: sqlite3.Connection, candidate: dict[str, Any], review_status: str = "new") -> int:
    timestamp = now_iso()
    conn.execute(
        """
        INSERT INTO signals (
            uid, source_id, source_name, source_type, source_url, item_title, item_url,
            category, classification, risk_level, matched_keywords_json, raw_text,
            status_code, first_seen_at, last_seen_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(uid) DO UPDATE SET
            last_seen_at=excluded.last_seen_at,
            risk_level=excluded.risk_level,
            matched_keywords_json=excluded.matched_keywords_json,
            raw_text=excluded.raw_text,
            status_code=excluded.status_code
        """,
        (
            candidate["uid"],
            candidate["source_id"],
            candidate["source_name"],
            candidate["source_type"],
            candidate["source_url"],
            candidate["item_title"],
            candidate["item_url"],
            candidate["category"],
            candidate["classification"],
            candidate["risk_level"],
            json.dumps(candidate["matched_keywords"], ensure_ascii=False),
            candidate["raw_text"],
            candidate["status_code"],
            timestamp,
            timestamp,
        ),
    )
    signal_id = int(conn.execute("SELECT id FROM signals WHERE uid = ?", (candidate["uid"],)).fetchone()["id"])
    conn.execute(
        """
        INSERT INTO reviews (signal_id, review_status, priority, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(signal_id) DO NOTHING
        """,
        (signal_id, review_status, priority_for(candidate["risk_level"]), timestamp),
    )
    return signal_id


def priority_for(risk: str) -> int:
    if risk == "high":
        return 1
    if risk == "medium":
        return 2
    return 3


def run_sources(args: argparse.Namespace) -> int:
    sources = [source for source in load_sources(args.sources) if source.enabled]
    if args.source != "all":
        sources = [source for source in sources if source.source_id == args.source]
    if not sources:
        raise SystemExit(f"No enabled source matched: {args.source}")

    conn = connect(args.db)
    init_db(conn)
    upsert_sources(conn, sources)

    total = 0
    for source in sources:
        print(f"Fetching {source.source_id}: {source.url}")
        started_at = now_iso()
        try:
            response = fetch_source(source, args.timeout)
            raw_text = page_text(response)
            record_snapshot(conn, source, raw_text)
            candidates = extract_candidates(source, response)
        except Exception as exc:
            print(f"  failed: {exc}")
            record_source_run(conn, source, "failed", 0, str(exc), started_at)
            conn.commit()
            continue
        for candidate in candidates:
            insert_signal(conn, candidate)
        record_source_run(conn, source, "success", len(candidates), "", started_at)
        conn.commit()
        total += len(candidates)
        print(f"  signals: {len(candidates)}")
    print(f"Stored {total} signal(s) in {args.db}")
    return 0


def seed_sample(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    sources = load_sources(args.sources)
    upsert_sources(conn, sources)
    samples = [
        build_candidate(
            sources_by_id(sources)["zicta_dfs_incident_home"],
            "DFS Incident Reporting System lists mobile payment fraud and incomplete transaction as reportable public categories",
            "https://dfscomplaints.zicta.zm/",
            ["incident", "mobile payment fraud", "incomplete transaction"],
            200,
            "Public DFS incident page references report incident, track incident, mobile payment fraud, and incomplete transaction categories.",
        ),
        build_candidate(
            sources_by_id(sources)["data_protection_commission_home"],
            "Data Protection Commission public page highlights data-subject rights and responsible personal-data handling",
            "https://www.dataprotection.gov.zm/",
            ["data protection", "personal data", "privacy", "rights"],
            200,
            "Public data protection source mentions personal data, rights, controllers, processors, and privacy responsibilities.",
        ),
        build_candidate(
            sources_by_id(sources)["ccpc_public_notices"],
            "CCPC public notice language reinforces clear, truthful, and sufficient consumer information",
            "https://www.ccpc.org.zm/",
            ["consumer", "rights", "misleading", "public notice"],
            200,
            "Public consumer-protection source reinforces truthful, clear, and sufficient information for consumers.",
        ),
    ]
    for sample in samples:
        signal_id = insert_signal(conn, sample, review_status="reviewed")
        conn.execute(
            """
            UPDATE reviews
            SET reviewer_notes = ?, recommended_action = ?, updated_at = ?
            WHERE signal_id = ?
            """,
            (
                "Sample reviewed item for personal research workflow testing.",
                recommended_action_for(sample["classification"]),
                now_iso(),
                signal_id,
            ),
        )
    conn.commit()
    print(f"Seeded {len(samples)} reviewed sample signal(s) in {args.db}")
    return 0


def seed_learning(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    goals = [
        (
            "scrapling_public_sources",
            "Scrapling collection",
            "Run at least three public-source fetches and understand which source types are stable for HTTP fetching.",
        ),
        (
            "lending_taxonomy",
            "Market taxonomy",
            "Build a useful taxonomy for complaint, fraud, privacy, fees, repayment, disbursement, and regulatory signals.",
        ),
        (
            "review_discipline",
            "Human review workflow",
            "Review signals weekly and write notes that separate source facts from personal interpretation.",
        ),
        (
            "weekly_personal_brief",
            "Research synthesis",
            "Generate one weekly personal market note with sources, open questions, and next learning actions.",
        ),
        (
            "payment_rails_lens",
            "Payment rails lens",
            "Track how public BoZ payment-system rules and payment-rail changes may affect lending disbursement, repayment, failed transactions, complaints, fees, and partner risk.",
        ),
    ]
    for goal_key, area, goal in goals:
        conn.execute(
            """
            INSERT INTO learning_goals (goal_key, capability_area, goal, status, updated_at)
            VALUES (?, ?, ?, 'active', ?)
            ON CONFLICT(goal_key) DO UPDATE SET
                capability_area=excluded.capability_area,
                goal=excluded.goal,
                updated_at=excluded.updated_at
            """,
            (goal_key, area, goal, now_iso()),
        )
    conn.commit()
    print(f"Seeded {len(goals)} learning goal(s) in {args.db}")
    return 0


def seed_questions(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    questions = [
        (
            "complaint_themes",
            "Complaints",
            "Which public complaint themes appear most often around digital financial services and lending-adjacent journeys?",
        ),
        (
            "regulatory_surface",
            "Regulatory watch",
            "Which public regulator pages are most useful for tracking lending, payments, consumer protection, and data protection risk?",
        ),
        (
            "fraud_payment_overlap",
            "Fraud and payments",
            "Where do mobile-money fraud, incomplete transaction, and customer-support issues overlap with lending operations?",
        ),
        (
            "privacy_lending_apps",
            "Privacy",
            "What privacy and data-subject rights themes should a lending app operator understand from public sources?",
        ),
        (
            "source_reliability",
            "Research process",
            "Which public sources are stable enough for recurring Scrapling collection, and which should remain manual review sources?",
        ),
        (
            "payment_rails_lending_ops",
            "Payment rails",
            "How do BoZ payment-system rules, payment-rail changes, and mobile-money/payment-service directives affect digital lending disbursement, repayment, failed transactions, complaints, fees, and partner risk?",
        ),
    ]
    for key, area, question in questions:
        conn.execute(
            """
            INSERT INTO market_questions (question_key, area, question, status, updated_at)
            VALUES (?, ?, ?, 'open', ?)
            ON CONFLICT(question_key) DO UPDATE SET
                area=excluded.area,
                question=excluded.question,
                updated_at=excluded.updated_at
            """,
            (key, area, question, now_iso()),
        )
    conn.commit()
    print(f"Seeded {len(questions)} market question(s) in {args.db}")
    return 0


def add_note(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    conn.execute(
        """
        INSERT INTO research_notes (
            signal_id, note_type, title, note, market_question, confidence, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            args.signal_id,
            args.note_type,
            args.title,
            args.note,
            args.question or "",
            args.confidence,
            now_iso(),
        ),
    )
    conn.commit()
    print("Added research note")
    return 0


def list_signals(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    rows = conn.execute(
        """
        SELECT
            s.id,
            s.source_name,
            s.item_title,
            s.classification,
            s.risk_level,
            s.item_url,
            r.review_status
        FROM signals s
        JOIN reviews r ON r.signal_id = s.id
        WHERE (? = 'all' OR r.review_status = ?)
        ORDER BY s.last_seen_at DESC, s.id DESC
        LIMIT ?
        """,
        (args.status, args.status, args.limit),
    ).fetchall()
    if not rows:
        print("No signals matched.")
        return 0
    for row in rows:
        print(f"[{row['id']}] {row['review_status']} | {row['classification']} / {row['risk_level']}")
        print(f"  {row['item_title']}")
        print(f"  {row['source_name']} | {row['item_url']}")
    return 0


def review_signal(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    signal = conn.execute("SELECT id FROM signals WHERE id = ?", (args.signal_id,)).fetchone()
    if signal is None:
        raise SystemExit(f"Unknown signal id: {args.signal_id}")
    conn.execute(
        """
        UPDATE reviews
        SET review_status = ?, priority = ?, reviewer_notes = ?, recommended_action = ?, updated_at = ?
        WHERE signal_id = ?
        """,
        (
            args.status,
            args.priority,
            args.notes or "",
            args.action or "",
            now_iso(),
            args.signal_id,
        ),
    )
    conn.commit()
    print(f"Updated signal {args.signal_id} review status to {args.status}")
    return 0


def answer_question(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    conn.execute(
        """
        UPDATE market_questions
        SET status = ?, current_hypothesis = ?, evidence = ?, updated_at = ?
        WHERE question_key = ?
        """,
        (args.status, args.hypothesis, args.evidence, now_iso(), args.question_key),
    )
    if conn.total_changes == 0:
        raise SystemExit(f"Unknown question_key: {args.question_key}. Run seed-questions first.")
    conn.commit()
    print(f"Updated market question: {args.question_key}")
    return 0


def stats_command(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    rows = conn.execute(
        """
        SELECT classification, risk_level, COUNT(*) AS count
        FROM signals
        GROUP BY classification, risk_level
        ORDER BY count DESC, classification
        """
    ).fetchall()
    print("Signal counts by classification/risk:")
    for row in rows:
        print(f"- {row['classification']} / {row['risk_level']}: {row['count']}")

    review_rows = conn.execute(
        """
        SELECT review_status, COUNT(*) AS count
        FROM reviews
        GROUP BY review_status
        ORDER BY count DESC
        """
    ).fetchall()
    print("Review queue:")
    for row in review_rows:
        print(f"- {row['review_status']}: {row['count']}")

    note_count = conn.execute("SELECT COUNT(*) AS count FROM research_notes").fetchone()["count"]
    source_run_count = conn.execute("SELECT COUNT(*) AS count FROM source_runs").fetchone()["count"]
    question_count = conn.execute("SELECT COUNT(*) AS count FROM market_questions").fetchone()["count"]
    print(f"Research notes: {note_count}")
    print(f"Source runs: {source_run_count}")
    print(f"Market questions: {question_count}")
    return 0


def intelligence_command(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    rows = conn.execute(
        """
        SELECT
            s.id,
            s.source_id,
            s.source_name,
            s.source_url,
            s.item_title,
            s.item_url,
            s.classification,
            s.risk_level,
            s.raw_text,
            r.priority,
            r.reviewer_notes,
            r.recommended_action,
            r.review_status
        FROM signals s
        JOIN reviews r ON r.signal_id = s.id
        WHERE r.review_status IN ('reviewed', 'briefed')
        ORDER BY r.priority ASC, s.risk_level DESC, s.last_seen_at DESC
        """
    ).fetchall()
    assessments = build_assessments(rows)
    if not assessments:
        print("No reviewed signals available for business interpretation.")
        return 0

    counts = domain_counts(assessments)
    print("Business impact interpretation | 业务影响解读")
    print(f"Reviewed signals interpreted: {len(assessments)}")
    print("Impact domains | 影响域:")
    for domain_key, count in counts.most_common():
        print(f"- {domain_key}: {count}")

    print("Key findings | 关键判断:")
    for item in top_interpretive_findings(assessments):
        print(f"- {item['finding_cn']}")
        print(f"  {item['why_cn']}")

    print("Top impact items | 重点业务影响条目:")
    for item in assessment_table_rows(assessments, limit=args.limit):
        print(f"[{item['signal_id']}] {item['impact_level']} | {item['domain_cn']}")
        print(f"  信号: {item['signal']}")
        print(f"  影响: {item['lending_impact_cn']}")
        print(f"  动作: {item['recommended_actions_cn']}")
        print(f"  问题: {item['follow_up_questions_cn']}")
        print(f"  来源: {item['source_link']}")

    if args.show_gaps:
        print("Coverage gaps | 情报覆盖缺口:")
        for row in coverage_gaps(assessments):
            print(f"- {row['area_cn']} ({row['coverage_cn']}): {row['gap_cn']}")
            print(f"  下一步: {row['next_source_cn']}")
    return 0


def competitor_triage_command(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    rows = conn.execute(
        """
        SELECT
            s.id,
            s.source_id,
            s.source_name,
            s.source_type,
            s.source_url,
            s.item_title,
            s.item_url,
            s.classification,
            s.risk_level,
            s.raw_text,
            r.review_status,
            r.priority,
            r.reviewer_notes,
            r.recommended_action
        FROM signals s
        JOIN reviews r ON r.signal_id = s.id
        WHERE s.source_id LIKE 'competitor_%'
          AND (? = 'all' OR r.review_status = ?)
        ORDER BY s.last_seen_at DESC, s.id DESC
        """,
        (args.status, args.status),
    ).fetchall()
    triaged = triage_rows(rows)
    if not triaged:
        print("No competitor signals matched.")
        return 0

    print("Competitor signal triage | 竞品信号预分诊")
    print(f"Signals: {len(triaged)}")
    print("Lens counts | 阅读角度:")
    for lens_key, count in lens_counts(triaged).most_common():
        print(f"- {lens_key}: {count}")

    if args.apply:
        updated = 0
        for item in triaged:
            action = f"竞品预分诊：{item['lens_cn']}。{item['action_cn']}"
            result = conn.execute(
                """
                UPDATE reviews
                SET
                    priority = ?,
                    recommended_action = CASE
                        WHEN ? = 1 OR recommended_action = '' THEN ?
                        ELSE recommended_action
                    END,
                    updated_at = ?
                WHERE signal_id = ?
                  AND review_status = 'new'
                """,
                (
                    int(item["priority"]),
                    1 if args.overwrite else 0,
                    action,
                    now_iso(),
                    int(item["signal_id"]),
                ),
            )
            updated += result.rowcount
        conn.commit()
        print(f"Applied triage priority/action to {updated} new competitor signal(s).")

    print("Top items | 优先阅读:")
    for item in triaged[: args.limit]:
        print(f"[{item['signal_id']}] P{item['priority']} | {item['lens_cn']} | {item['classification']} / {item['risk_level']}")
        print(f"  信号: {item['signal']}")
        print(f"  为什么看: {item['why_cn']}")
        print(f"  建议动作: {item['action_cn']}")
        print(f"  来源: {item['source_link']}")
    return 0


def source_health(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    rows = conn.execute(
        """
        SELECT
            q.source_id,
            s.name,
            s.enabled,
            q.run_count,
            q.success_count,
            q.fail_count,
            q.last_status,
            q.last_signal_count,
            q.total_signal_count,
            q.last_error,
            q.updated_at
        FROM source_quality q
        LEFT JOIN sources s ON s.source_id = q.source_id
        ORDER BY q.updated_at DESC
        """
    ).fetchall()
    if not rows:
        print("No source quality records yet. Run a source first.")
        return 0
    print("Source health:")
    for row in rows:
        success_rate = row["success_count"] / row["run_count"] if row["run_count"] else 0
        enabled_label = "enabled" if row["enabled"] in (None, 1) else "disabled"
        print(
            f"- {row['source_id']} ({row['last_status']}, {enabled_label}): "
            f"{row['success_count']}/{row['run_count']} success "
            f"({success_rate:.0%}), last signals={row['last_signal_count']}"
        )
        if row["last_error"]:
            print(f"  last_error: {row['last_error'][:180]}")
    return 0


def export_csv(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = conn.execute(
        """
        SELECT
            s.id,
            s.source_name,
            s.item_title,
            s.item_url,
            s.classification,
            s.risk_level,
            s.last_seen_at,
            r.review_status,
            r.priority,
            r.reviewer_notes,
            r.recommended_action
        FROM signals s
        JOIN reviews r ON r.signal_id = s.id
        ORDER BY s.last_seen_at DESC
        """
    ).fetchall()
    import csv

    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(rows[0].keys() if rows else ["id", "source_name", "item_title"])
        for row in rows:
            writer.writerow([row[key] for key in row.keys()])
    print(f"Exported {len(rows)} signal(s) to {args.output}")
    return 0


def reclassify_signals(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    rows = conn.execute(
        """
        SELECT id, category, classification, raw_text, risk_level
        FROM signals
        """
    ).fetchall()
    changed = 0
    for row in rows:
        new_classification = classify_signal(row["raw_text"], row["category"])
        new_risk = risk_level(row["raw_text"])
        conn.execute(
            """
            UPDATE signals
            SET classification = ?, risk_level = ?
            WHERE id = ?
            """,
            (new_classification, new_risk, row["id"]),
        )
        if new_classification != row["classification"] or new_risk != row["risk_level"]:
            changed += 1
    conn.commit()
    print(f"Reclassified {len(rows)} signal(s); updated classification/risk calculations for {changed} row(s)")
    return 0


def sources_by_id(sources: list[SourceConfig]) -> dict[str, SourceConfig]:
    return {source.source_id: source for source in sources}


def recommended_action_for(classification: str) -> str:
    actions = {
        "fraud": "Publish and review official payment-channel and anti-scam guidance.",
        "privacy": "Review consent, data-permission, and privacy wording in customer-facing journeys.",
        "regulatory": "Add this source to weekly management watch and verify any affected disclosure language.",
        "complaint": "Review support macros and escalation rules for repeated complaint themes.",
    }
    return actions.get(classification, "Review source and decide whether it belongs in the weekly brief.")


def init_command(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    init_db(conn)
    sources = load_sources(args.sources)
    upsert_sources(conn, sources)
    print(f"Initialized {args.db} with {len(sources)} configured source(s)")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Zambia Digital Lending Ops Radar pipeline")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize SQLite schema and sources")
    init_parser.set_defaults(func=init_command)

    run_parser = subparsers.add_parser("run", help="Fetch configured public sources")
    run_parser.add_argument("--source", default="all", help="Source ID to run, or 'all'")
    run_parser.add_argument("--timeout", type=int, default=30_000, help="Fetch timeout in milliseconds")
    run_parser.set_defaults(func=run_sources)

    sample_parser = subparsers.add_parser("seed-sample", help="Seed reviewed sample signals for offline testing")
    sample_parser.set_defaults(func=seed_sample)

    learning_parser = subparsers.add_parser("seed-learning", help="Seed capability-building learning goals")
    learning_parser.set_defaults(func=seed_learning)

    questions_parser = subparsers.add_parser("seed-questions", help="Seed personal market research questions")
    questions_parser.set_defaults(func=seed_questions)

    note_parser = subparsers.add_parser("add-note", help="Add a personal research note")
    note_parser.add_argument("--signal-id", type=int, default=None)
    note_parser.add_argument("--note-type", default="market_observation")
    note_parser.add_argument("--title", required=True)
    note_parser.add_argument("--note", required=True)
    note_parser.add_argument("--question", default="")
    note_parser.add_argument("--confidence", choices=["low", "medium", "high"], default="medium")
    note_parser.set_defaults(func=add_note)

    list_parser = subparsers.add_parser("list-signals", help="List signals for CLI review")
    list_parser.add_argument("--status", default="new", choices=["all", "new", "reviewed", "briefed", "rejected"])
    list_parser.add_argument("--limit", type=int, default=10)
    list_parser.set_defaults(func=list_signals)

    review_parser = subparsers.add_parser("review-signal", help="Update one signal review from the CLI")
    review_parser.add_argument("--signal-id", type=int, required=True)
    review_parser.add_argument("--status", choices=["new", "reviewed", "briefed", "rejected"], default="reviewed")
    review_parser.add_argument("--priority", type=int, choices=[1, 2, 3], default=2)
    review_parser.add_argument("--notes", default="")
    review_parser.add_argument("--action", default="")
    review_parser.set_defaults(func=review_signal)

    answer_parser = subparsers.add_parser("answer-question", help="Update a market question hypothesis and evidence")
    answer_parser.add_argument("--question-key", required=True)
    answer_parser.add_argument("--status", choices=["open", "investigating", "answered", "parked"], default="investigating")
    answer_parser.add_argument("--hypothesis", required=True)
    answer_parser.add_argument("--evidence", required=True)
    answer_parser.set_defaults(func=answer_question)

    stats_parser = subparsers.add_parser("stats", help="Show personal research platform stats")
    stats_parser.set_defaults(func=stats_command)

    intelligence_parser = subparsers.add_parser("intelligence", help="Show reviewed signals as business impact interpretation")
    intelligence_parser.add_argument("--limit", type=int, default=10)
    intelligence_parser.add_argument("--show-gaps", action="store_true")
    intelligence_parser.set_defaults(func=intelligence_command)

    competitor_triage_parser = subparsers.add_parser("competitor-triage", help="Pre-triage public competitor signals without marking them reviewed")
    competitor_triage_parser.add_argument("--status", default="new", choices=["all", "new", "reviewed", "briefed", "rejected"])
    competitor_triage_parser.add_argument("--limit", type=int, default=20)
    competitor_triage_parser.add_argument("--apply", action="store_true", help="Write suggested priority/action to new competitor reviews")
    competitor_triage_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing recommended_action when applying")
    competitor_triage_parser.set_defaults(func=competitor_triage_command)

    health_parser = subparsers.add_parser("source-health", help="Show Scrapling source run health")
    health_parser.set_defaults(func=source_health)

    export_parser = subparsers.add_parser("export-csv", help="Export signal review table to CSV")
    export_parser.add_argument("--output", type=Path, default=ROOT / "data" / "lending_ops_signals_export.csv")
    export_parser.set_defaults(func=export_csv)

    reclassify_parser = subparsers.add_parser("reclassify", help="Recalculate signal classification and risk after taxonomy changes")
    reclassify_parser.set_defaults(func=reclassify_signals)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
