#!/usr/bin/env python3
"""
Enhanced Nocturnal AI Agent - Production-Ready Research Assistant
Integrates with Archive API and FinSight API for comprehensive research capabilities
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import shlex
import subprocess
import time
from importlib import resources

import aiohttp
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass, field
from pathlib import Path

from .telemetry import TelemetryManager
from .setup_config import DEFAULT_QUERY_LIMIT

# Suppress noise
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Removed: No direct Groq import in production
# All LLM calls go through backend API for monetization
# Backend has the API keys, not the client

@dataclass
class ChatRequest:
    question: str
    user_id: str = "default"
    conversation_id: str = "default"
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatResponse:
    response: str
    tools_used: List[str] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)
    model: str = "enhanced-nocturnal-agent"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tokens_used: int = 0
    confidence_score: float = 0.0
    execution_results: Dict[str, Any] = field(default_factory=dict)
    api_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

class EnhancedNocturnalAgent:
    """
    Enhanced AI Agent with full API integration:
    - Archive API for academic research
    - FinSight API for financial data
    - Shell access for system operations
    - Memory system for context retention
    """
    
    def __init__(self):
        self.client = None
        self.conversation_history = []
        self.shell_session = None
        self.memory = {}
        self.daily_token_usage = 0
        self.daily_limit = 100000
        self.daily_query_limit = self._resolve_daily_query_limit()
        self.per_user_query_limit = self.daily_query_limit
        
        # Initialize web search for fallback
        self.web_search = None
        try:
            from .web_search import WebSearchIntegration
            self.web_search = WebSearchIntegration()
        except Exception:
            pass  # Web search optional
        self.daily_query_count = 0
        self.total_cost = 0.0
        self.cost_per_1k_tokens = 0.0001  # Groq pricing estimate
        self._auto_update_enabled = True
        
        # Workflow integration
        from .workflow import WorkflowManager
        self.workflow = WorkflowManager()
        self.last_paper_result = None  # Track last paper mentioned for "save that"
        
        # File context tracking (for pronoun resolution and multi-turn)
        self.file_context = {
            'last_file': None,           # Last file mentioned/read
            'last_directory': None,      # Last directory mentioned/navigated
            'recent_files': [],          # Last 5 files (for "those files")
            'recent_dirs': [],           # Last 5 directories
            'current_cwd': None,         # Track shell's current directory
        }
        try:
            self.per_user_token_limit = int(os.getenv("GROQ_PER_USER_TOKENS", 50000))
        except (TypeError, ValueError):
            self.per_user_token_limit = 50000  # 50 queries at ~1000 tokens each
        self.user_token_usage: Dict[str, int] = {}
        self.user_query_counts: Dict[str, int] = {}
        self._usage_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self._initialized = False
        self._env_loaded = False
        self._init_lock: Optional[asyncio.Lock] = None
        self._default_headers: Dict[str, str] = {}

        # API clients
        self.archive_client = None
        self.finsight_client = None
        self.session = None
        self.company_name_to_ticker = {}

        # Groq key rotation state
        self.api_keys: List[str] = []
        self.current_key_index: int = 0
        self.current_api_key: Optional[str] = None
        self.exhausted_keys: Dict[str, float] = {}
        try:
            self.key_recheck_seconds = float(
                os.getenv("GROQ_KEY_RECHECK_SECONDS", 3600)
            )
        except Exception:
            self.key_recheck_seconds = 3600.0
        
        self._service_roots: List[str] = []
        self._backend_health_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize authentication
        self.auth_token = None
        self.user_id = None
        self._load_authentication()
        try:
            self._health_ttl = float(os.getenv("NOCTURNAL_HEALTH_TTL", 30))
        except Exception:
            self._health_ttl = 30.0
        self._recent_sources: List[Dict[str, Any]] = []

    def _load_authentication(self):
        """Load authentication from session file"""
        use_local_keys = os.getenv("USE_LOCAL_KEYS", "false").lower() == "true"
        
        debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
        if debug_mode:
            print(f"🔍 _load_authentication: USE_LOCAL_KEYS={os.getenv('USE_LOCAL_KEYS')}, use_local_keys={use_local_keys}")
        
        if not use_local_keys:
            # Backend mode - load auth token from session
            from pathlib import Path
            session_file = Path.home() / ".nocturnal_archive" / "session.json"
            if debug_mode:
                print(f"🔍 _load_authentication: session_file exists={session_file.exists()}")
            if session_file.exists():
                try:
                    import json
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                        self.auth_token = session_data.get('auth_token')
                        self.user_id = session_data.get('account_id')
                        if debug_mode:
                            print(f"🔍 _load_authentication: loaded auth_token={self.auth_token}, user_id={self.user_id}")
                except Exception as e:
                    if debug_mode:
                        print(f"🔍 _load_authentication: ERROR loading session: {e}")
                    self.auth_token = None
                    self.user_id = None
            else:
                # FALLBACK: Check if config.env has credentials but session.json is missing
                # This handles cases where old setup didn't create session.json
                import json
                email = os.getenv("NOCTURNAL_ACCOUNT_EMAIL")
                account_id = os.getenv("NOCTURNAL_ACCOUNT_ID")
                auth_token = os.getenv("NOCTURNAL_AUTH_TOKEN")
                
                if email and account_id and auth_token:
                    # Auto-create session.json from config.env
                    try:
                        session_data = {
                            "email": email,
                            "account_id": account_id,
                            "auth_token": auth_token,
                            "refresh_token": "auto_generated",
                            "issued_at": datetime.now(timezone.utc).isoformat()
                        }
                        session_file.parent.mkdir(parents=True, exist_ok=True)
                        session_file.write_text(json.dumps(session_data, indent=2))
                        
                        self.auth_token = auth_token
                        self.user_id = account_id
                        
                        if debug_mode:
                            print(f"🔍 _load_authentication: Auto-created session.json from config.env")
                    except Exception as e:
                        if debug_mode:
                            print(f"🔍 _load_authentication: Failed to auto-create session: {e}")
                        self.auth_token = None
                        self.user_id = None
                else:
                    self.auth_token = None
                    self.user_id = None
        else:
            # Local keys mode
            if debug_mode:
                print(f"🔍 _load_authentication: Local keys mode, not loading session")
            self.auth_token = None
            self.user_id = None
        self._session_topics: Dict[str, Dict[str, Any]] = {}

        # Initialize API clients
        self._init_api_clients()
        self._load_ticker_map()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics and cost information"""
        limit = self.daily_limit if self.daily_limit > 0 else 1
        remaining = max(self.daily_limit - self.daily_token_usage, 0)
        usage_percentage = (self.daily_token_usage / limit) * 100 if limit else 0.0
        return {
            "daily_tokens_used": self.daily_token_usage,
            "daily_token_limit": self.daily_limit,
            "remaining_tokens": remaining,
            "usage_percentage": usage_percentage,
            "total_cost": self.total_cost,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "estimated_monthly_cost": self.total_cost * 30,  # Rough estimate
            "per_user_token_limit": self.per_user_token_limit,
            "daily_queries_used": self.daily_query_count,
            "daily_query_limit": self.daily_query_limit,
            "per_user_query_limit": self.per_user_query_limit,
        }
    
    async def close(self):
        """Cleanly close resources (HTTP session and shell)."""
        lock = self._get_init_lock()
        async with lock:
            await self._close_resources()

    async def _close_resources(self):
        try:
            if self.session and not self.session.closed:
                await self.session.close()
        except Exception:
            pass
        finally:
            self.session = None

        try:
            if self.shell_session:
                self.shell_session.terminate()
        except Exception:
            pass
        finally:
            self.shell_session = None

        self.client = None
        self.current_api_key = None
        self.current_key_index = 0
        self._initialized = False
        self.exhausted_keys.clear()
        
    def _init_api_clients(self):
        """Initialize API clients for Archive and FinSight"""
        try:
            def _normalize_base(value: Optional[str], fallback: str) -> str:
                candidate = (value or fallback).strip()
                return candidate[:-1] if candidate.endswith('/') else candidate

            archive_env = (
                os.getenv("ARCHIVE_API_URL")
                or os.getenv("NOCTURNAL_ARCHIVE_API_URL")
            )
            finsight_env = (
                os.getenv("FINSIGHT_API_URL")
                or os.getenv("NOCTURNAL_FINSIGHT_API_URL")
            )

            # Archive API client
            self.archive_base_url = _normalize_base(archive_env, "https://cite-agent-api-720dfadd602c.herokuapp.com/api")

            # FinSight API client
            self.finsight_base_url = _normalize_base(finsight_env, "https://cite-agent-api-720dfadd602c.herokuapp.com/v1/finance")

            # Workspace Files API client
            files_env = os.getenv("FILES_API_URL")
            self.files_base_url = _normalize_base(files_env, "http://127.0.0.1:8000/v1/files")

            # Shared API key handling for protected routes
            self.api_key = (
                os.getenv("NOCTURNAL_KEY")
                or os.getenv("NOCTURNAL_API_KEY")
                or os.getenv("X_API_KEY")
                or "demo-key-123"
            )
            self._default_headers.clear()
            if self.api_key:
                self._default_headers["X-API-Key"] = self.api_key
            
            self._update_service_roots()
            
            # Only show init messages in debug mode
            debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
            if debug_mode:
                if self.api_key == "demo-key-123":
                    print("⚠️ Using demo API key")
                print(f"✅ API clients initialized (Archive={self.archive_base_url}, FinSight={self.finsight_base_url})")
            
        except Exception as e:
            print(f"⚠️ API client initialization warning: {e}")

    def _update_service_roots(self) -> None:
        roots = set()
        for base in (getattr(self, "archive_base_url", None), getattr(self, "finsight_base_url", None), getattr(self, "files_base_url", None)):
            if not base:
                continue
            parsed = urlparse(base)
            if parsed.scheme and parsed.netloc:
                roots.add(f"{parsed.scheme}://{parsed.netloc}")

        if not roots:
            roots.add("http://127.0.0.1:8000")

        self._service_roots = sorted(roots)
        # Drop caches for roots that no longer exist
        for cached in list(self._backend_health_cache.keys()):
            if cached not in self._service_roots:
                self._backend_health_cache.pop(cached, None)

    async def _probe_health_endpoint(self, root: str) -> Tuple[bool, str]:
        if not self.session:
            return False, "HTTP session not initialized"

        if not hasattr(self.session, "get"):
            # Assume healthy when using lightweight mocks that lack GET semantics
            return True, ""

        candidates = ["/readyz", "/health", "/api/health", "/livez"]
        last_detail = ""

        for endpoint in candidates:
            try:
                async with self.session.get(f"{root}{endpoint}", timeout=5) as response:
                    if response.status == 200:
                        return True, ""
                    body = await response.text()
                    if response.status == 404:
                        # Endpoint absent—record detail but keep probing
                        last_detail = (
                            f"{endpoint} missing (404)."
                            if not body else f"{endpoint} missing (404): {body.strip()}"
                        )
                        continue
                    last_detail = (
                        f"{endpoint} returned {response.status}"
                        if not body else f"{endpoint} returned {response.status}: {body.strip()}"
                    )
            except Exception as exc:
                last_detail = f"{endpoint} failed: {exc}"

        # Fall back to a lightweight root probe so services without explicit
        # health endpoints don't register as offline.
        try:
            async with self.session.get(root, timeout=5) as response:
                if response.status < 500:
                    fallback_detail = f"fallback probe returned {response.status}"
                    if response.status == 200:
                        detail = (f"{last_detail}; {fallback_detail}" if last_detail else "")
                    else:
                        detail = (
                            f"{last_detail}; {fallback_detail}"
                            if last_detail else f"Health endpoint unavailable; {fallback_detail}"
                        )
                    return True, detail
        except Exception as exc:  # pragma: no cover - network failure already captured above
            last_detail = last_detail or f"Fallback probe failed: {exc}"

        return False, last_detail or f"Health check failed for {root}"

    async def _check_backend_health(self, force: bool = False) -> Dict[str, Any]:
        now = time.monotonic()
        overall_ok = True
        details: List[str] = []

        if not self._service_roots:
            self._update_service_roots()

        for root in self._service_roots:
            cache = self._backend_health_cache.get(root)
            if cache and not force and now - cache.get("timestamp", 0.0) < self._health_ttl:
                if not cache.get("ok", False) and cache.get("detail"):
                    details.append(cache["detail"])
                    overall_ok = False
                overall_ok = overall_ok and cache.get("ok", False)
                continue

            ok, detail = await self._probe_health_endpoint(root)
            self._backend_health_cache[root] = {"ok": ok, "detail": detail, "timestamp": now}
            if not ok and detail:
                details.append(detail)
            overall_ok = overall_ok and ok

        return {"ok": overall_ok, "detail": "; ".join(details) if details else ""}

    async def _ensure_backend_ready(self) -> Tuple[bool, str]:
        status = await self._check_backend_health()
        return status["ok"], status.get("detail", "")

    def _record_data_source(self, service: str, endpoint: str, success: bool, detail: str = "") -> None:
        entry = {
            "service": service,
            "endpoint": endpoint,
            "success": success,
            "detail": detail,
        }
        self._recent_sources.append(entry)
        if len(self._recent_sources) > 10:
            self._recent_sources = self._recent_sources[-10:]

    def _format_data_sources_footer(self) -> str:
        if not self._recent_sources:
            return ""

        snippets: List[str] = []
        for item in self._recent_sources[:4]:
            status = "ok" if item.get("success") else f"error ({item.get('detail')})" if item.get("detail") else "error"
            snippets.append(f"{item.get('service')} {item.get('endpoint')} – {status}")
        if len(self._recent_sources) > 4:
            snippets.append("…")
        return "Data sources: " + "; ".join(snippets)

    def _reset_data_sources(self) -> None:
        self._recent_sources = []

    def _load_ticker_map(self):
        """Load a simple company name -> ticker map for FinSight lookups."""
        # Start with common aliases
        mapping = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "alphabet": "GOOGL",
            "google": "GOOGL",
            "amazon": "AMZN",
            "nvidia": "NVDA",
            "palantir": "PLTR",
            "shopify": "SHOP",
            "target": "TGT",
            "amd": "AMD",
            "tesla": "TSLA",
            "meta": "META",
            "netflix": "NFLX",
            "goldman sachs": "GS",
            "goldman": "GS",
            "exxonmobil": "XOM",
            "exxon": "XOM",
            "jpmorgan": "JPM",
            "square": "SQ"
        }

        def _augment_from_records(records: List[Dict[str, Any]]) -> None:
            for item in records:
                name = str(item.get("name", "")).lower()
                symbol = item.get("symbol")
                if name and symbol:
                    mapping.setdefault(name, symbol)
                    short = (
                        name.replace("inc.", "")
                        .replace("inc", "")
                        .replace("corporation", "")
                        .replace("corp.", "")
                        .strip()
                    )
                    if short and short != name:
                        mapping.setdefault(short, symbol)

        try:
            supplemental: List[Dict[str, Any]] = []

            try:
                package_resource = resources.files("nocturnal_archive.data").joinpath("company_tickers.json")
                if package_resource.is_file():
                    supplemental = json.loads(package_resource.read_text(encoding="utf-8"))
            except (FileNotFoundError, ModuleNotFoundError, AttributeError):
                supplemental = []

            if not supplemental:
                candidate_paths = [
                    Path(__file__).resolve().parent / "data" / "company_tickers.json",
                    Path("./data/company_tickers.json"),
                ]
                for data_path in candidate_paths:
                    if data_path.exists():
                        supplemental = json.loads(data_path.read_text(encoding="utf-8"))
                        break

            if supplemental:
                _augment_from_records(supplemental)

            override_candidates: List[Path] = []
            override_env = os.getenv("NOCTURNAL_TICKER_MAP")
            if override_env:
                override_candidates.append(Path(override_env).expanduser())

            default_override = Path.home() / ".nocturnal_archive" / "tickers.json"
            override_candidates.append(default_override)

            for override_path in override_candidates:
                if not override_path or not override_path.exists():
                    continue
                try:
                    override_records = json.loads(override_path.read_text(encoding="utf-8"))
                    if isinstance(override_records, list):
                        _augment_from_records(override_records)
                except Exception as override_exc:
                    logger.warning(f"Failed to load ticker override from {override_path}: {override_exc}")
        except Exception:
            pass

        self.company_name_to_ticker = mapping

    def _ensure_environment_loaded(self):
        if self._env_loaded:
            return

        try:
            from .setup_config import NocturnalConfig

            config = NocturnalConfig()
            config.setup_environment()
        except ImportError:
            pass
        except Exception as exc:
            print(f"⚠️ Environment setup warning: {exc}")

        try:
            from dotenv import load_dotenv
            from pathlib import Path
            
            # ONLY load from user's config directory (never from cwd/project root)
            # Project .env.local is for developers, not end users
            env_local = Path.home() / ".nocturnal_archive" / ".env.local"
            if env_local.exists():
                load_dotenv(env_local, override=False)  # Don't override existing env vars
        except ImportError:
            pass  # python-dotenv not installed
        except Exception as exc:
            pass  # Silently fail - not critical
        finally:
            self._env_loaded = True

    def _get_init_lock(self) -> asyncio.Lock:
        if self._init_lock is None:
            self._init_lock = asyncio.Lock()
        return self._init_lock

    async def _get_workspace_listing(self, limit: int = 20) -> Dict[str, Any]:
        params = {"path": ".", "limit": limit, "include_hidden": "false"}
        result = await self._call_files_api("GET", "/", params=params)
        if "error" not in result:
            return result

        fallback = self._fallback_workspace_listing(limit)
        fallback["error"] = result["error"]
        return fallback

    def _fallback_workspace_listing(self, limit: int = 20) -> Dict[str, Any]:
        base = Path.cwd().resolve()
        items: List[Dict[str, str]] = []
        try:
            for entry in sorted(base.iterdir(), key=lambda e: e.name.lower()):
                if entry.name.startswith('.'):
                    continue
                item = {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file"
                }
                items.append(item)
                if len(items) >= limit:
                    break
        except Exception as exc:
            return {
                "base": str(base),
                "items": [],
                "error": f"Unable to list workspace: {exc}"
            }

        return {
            "base": str(base),
            "items": items,
            "note": "Showing up to first {limit} non-hidden entries.".format(limit=limit)
        }

    def _format_workspace_listing_response(self, listing: Dict[str, Any]) -> str:
        base = listing.get("base", Path.cwd().resolve())
        items = listing.get("items")
        if not items:
            items = listing.get("entries", []) or []
        note = listing.get("note")
        error = listing.get("error")
        truncated_flag = listing.get("truncated")

        if not items:
            summary_lines = ["(no visible files in the current directory)"]
        else:
            max_entries = min(len(items), 12)
            summary_lines = [
                f"- {item.get('name')} ({item.get('type', 'unknown')})"
                for item in items[:max_entries]
            ]
            if len(items) > max_entries:
                remaining = len(items) - max_entries
                summary_lines.append(f"… and {remaining} more")

        message_parts = [
            f"Workspace root: {base}",
            "Here are the first entries I can see:",
            "\n".join(summary_lines)
        ]

        if note:
            message_parts.append(note)
        if error:
            message_parts.append(f"Workspace API warning: {error}")
        if truncated_flag:
            message_parts.append("(Listing truncated by workspace service)")

        footer = self._format_data_sources_footer()
        if footer:
            message_parts.append(f"_{footer}_")

        return "\n\n".join(part for part in message_parts if part)

    def _respond_with_workspace_listing(self, request: ChatRequest, listing: Dict[str, Any]) -> ChatResponse:
        message = self._format_workspace_listing_response(listing)

        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(request.user_id, request.conversation_id, f"Q: {request.question[:100]}... A: {message[:100]}...")

        items = listing.get("items") or listing.get("entries") or []
        success = "error" not in listing
        self._emit_telemetry(
            "workspace_listing",
            request,
            success=success,
            extra={
                "item_count": len(items),
                "truncated": bool(listing.get("truncated")),
            },
        )

        return ChatResponse(
            response=message,
            tools_used=["files_listing"],
            reasoning_steps=["Direct workspace listing response"],
            tokens_used=0,
            confidence_score=0.7,
            api_results={"workspace_listing": listing}
        )

    def _respond_with_shell_command(self, request: ChatRequest, command: str) -> ChatResponse:
        command_stub = command.split()[0] if command else ""
        if not self._is_safe_shell_command(command):
            message = (
                "I couldn't run that command because it violates the safety policy. "
                "Please try a simpler shell command (no pipes, redirection, or file writes)."
            )
            tools = ["shell_blocked"]
            execution_results = {"command": command, "output": "Command blocked by safety policy", "success": False}
            telemetry_event = "shell_blocked"
            success = False
            output_len = 0
        else:
            output = self.execute_command(command)
            truncated_output = output if len(output) <= 2000 else output[:2000] + "\n… (truncated)"
            message = (
                f"Running the command: `{command}`\n\n"
                "Output:\n```\n"
                f"{truncated_output}\n"
                "```"
            )
            tools = ["shell_execution"]
            success = not output.startswith("ERROR:")
            execution_results = {"command": command, "output": truncated_output, "success": success}
            telemetry_event = "shell_execution"
            output_len = len(truncated_output)

        footer = self._format_data_sources_footer()
        if footer:
            message = f"{message}\n\n_{footer}_"

        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(
            request.user_id,
            request.conversation_id,
            f"Q: {request.question[:100]}... A: {message[:100]}..."
        )

        self._emit_telemetry(
            telemetry_event,
            request,
            success=success,
            extra={
                "command": command_stub,
                "output_len": output_len,
            },
        )

        return ChatResponse(
            response=message,
            tools_used=tools,
            reasoning_steps=["Direct shell execution"],
            tokens_used=0,
            confidence_score=0.75 if tools == ["shell_execution"] else 0.4,
            execution_results=execution_results
        )
    def _format_currency_value(self, value: float) -> str:
        try:
            abs_val = abs(value)
            if abs_val >= 1e12:
                return f"${value / 1e12:.2f} trillion"
            if abs_val >= 1e9:
                return f"${value / 1e9:.2f} billion"
            if abs_val >= 1e6:
                return f"${value / 1e6:.2f} million"
            return f"${value:,.2f}"
        except Exception:
            return str(value)

    def _respond_with_financial_metrics(self, request: ChatRequest, payload: Dict[str, Any]) -> ChatResponse:
        ticker, metrics = next(iter(payload.items()))
        headline = [f"{ticker} key metrics:"]
        citations: List[str] = []

        for metric_name, metric_data in metrics.items():
            if not isinstance(metric_data, dict):
                continue
            value = metric_data.get("value")
            if value is None:
                inner_inputs = metric_data.get("inputs", {})
                entry = inner_inputs.get(metric_name) or next(iter(inner_inputs.values()), {})
                value = entry.get("value")
            formatted_value = self._format_currency_value(value) if value is not None else "(value unavailable)"
            period = metric_data.get("period")
            if not period or (isinstance(period, str) and period.lower().startswith("latest")):
                inner_inputs = metric_data.get("inputs", {})
                entry = inner_inputs.get(metric_name) or next(iter(inner_inputs.values()), {})
                period = entry.get("period")
            sources = metric_data.get("citations") or []
            if sources:
                source_url = sources[0].get("source_url")
                if source_url:
                    citations.append(source_url)
            label = metric_name.replace("Gross", "Gross ").replace("Income", " Income").replace("Net", "Net ")
            label = label.replace("operating", "operating ").replace("Ratio", " Ratio").title()
            if period:
                headline.append(f"• {label}: {formatted_value} (as of {period})")
            else:
                headline.append(f"• {label}: {formatted_value}")

        unique_citations = []
        for c in citations:
            if c not in unique_citations:
                unique_citations.append(c)

        message_parts = ["\n".join(headline)]
        if unique_citations:
            message_parts.append("Sources:\n" + "\n".join(unique_citations))

        footer = self._format_data_sources_footer()
        if footer:
            message_parts.append(f"_{footer}_")

        message = "\n\n".join(message_parts)

        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(
            request.user_id,
            request.conversation_id,
            f"Q: {request.question[:100]}... A: {message[:100]}..."
        )

        self._emit_telemetry(
            "financial_metrics",
            request,
            success=True,
            extra={
                "ticker": ticker,
                "metric_count": len(metrics),
            },
        )

        return ChatResponse(
            response=message,
            tools_used=["finsight_api"],
            reasoning_steps=["Direct financial metrics response"],
            tokens_used=0,
            confidence_score=0.8,
            api_results={"financial": payload}
        )

    def _local_file_preview(self, path_str: str) -> Optional[Dict[str, Any]]:
        try:
            p = Path(path_str)
            if not p.exists():
                return None
            if p.is_dir():
                entries = sorted([e.name for e in p.iterdir()][:10])
                return {
                    "path": str(p),
                    "type": "directory",
                    "preview": "\n".join(entries),
                    "encoding": "utf-8",
                    "truncated": False,
                    "size": None,
                }

            stat_result = p.stat()
            if p.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg", ".parquet", ".zip", ".gif"}:
                return {
                    "path": str(p),
                    "type": "binary",
                    "preview": "(binary file preview skipped)",
                    "encoding": "binary",
                    "truncated": False,
                    "size": stat_result.st_size,
                }

            content = p.read_text(errors="ignore")
            truncated = len(content) > 65536
            snippet = content[:65536]
            preview = "\n".join(snippet.splitlines()[:60])
            return {
                "path": str(p),
                "type": "text",
                "preview": preview,
                "encoding": "utf-8",
                "truncated": truncated,
                "size": stat_result.st_size,
            }
        except Exception as exc:
            return {
                "path": path_str,
                "type": "error",
                "preview": f"error: {exc}",
                "encoding": "utf-8",
                "truncated": False,
                "size": None,
            }

    async def _preview_file(self, path_str: str) -> Optional[Dict[str, Any]]:
        params = {"path": path_str}
        result = await self._call_files_api("GET", "/preview", params=params)
        if "error" not in result:
            encoding = result.get("encoding", "utf-8")
            return {
                "path": result.get("path", path_str),
                "type": "text" if encoding == "utf-8" else "binary",
                "preview": result.get("content", ""),
                "encoding": encoding,
                "truncated": bool(result.get("truncated", False)),
                "size": result.get("size"),
            }

        message = result.get("error", "")
        if message and "does not exist" in message.lower():
            return None

        fallback = self._local_file_preview(path_str)
        if fallback:
            fallback.setdefault("error", message)
            return fallback
        return {
            "path": path_str,
            "type": "error",
            "preview": "",
            "encoding": "utf-8",
            "truncated": False,
            "size": None,
            "error": message,
        }

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
        return False

    def _is_simple_greeting(self, text: str) -> bool:
        greetings = {"hi", "hello", "hey", "hola", "howdy", "greetings"}
        normalized = text.lower().strip()
        return any(normalized.startswith(greet) for greet in greetings)

    def _is_casual_acknowledgment(self, text: str) -> bool:
        acknowledgments = {
            "thanks",
            "thank you",
            "thx",
            "ty",
            "appreciate it",
            "got it",
            "cool",
            "great",
            "awesome"
        }
        normalized = text.lower().strip()
        return any(normalized.startswith(ack) for ack in acknowledgments)

    def _format_api_results_for_prompt(self, api_results: Dict[str, Any]) -> str:
        if not api_results:
            logger.info("🔍 DEBUG: _format_api_results_for_prompt called with EMPTY api_results")
            return "No API results yet."
        try:
            serialized = json.dumps(api_results, indent=2)
        except Exception:
            serialized = str(api_results)
        max_len = 3000  # Aggressive limit to prevent token explosion
        if len(serialized) > max_len:
            serialized = serialized[:max_len] + "\n... (truncated for length)"

        # DEBUG: Log formatted results length and preview
        logger.info(f"🔍 DEBUG: _format_api_results_for_prompt returning {len(serialized)} chars")
        if "research" in api_results:
            papers_count = len(api_results.get("research", {}).get("results", []))
            logger.info(f"🔍 DEBUG: api_results contains 'research' with {papers_count} papers")

        return serialized

    def _build_system_prompt(
        self,
        request_analysis: Dict[str, Any],
        memory_context: str,
        api_results: Dict[str, Any]
    ) -> str:
        sections: List[str] = []
        
        # TRUTH-SEEKING CORE IDENTITY
        # Adapt intro based on analysis mode
        analysis_mode = request_analysis.get("analysis_mode", "quantitative")
        
        if analysis_mode == "qualitative":
            intro = (
                "You are Nocturnal, a truth-seeking research AI specialized in QUALITATIVE ANALYSIS. "
                "PRIMARY DIRECTIVE: Accuracy > Agreeableness. Quote verbatim, never paraphrase. "
                "You analyze text, identify themes, extract quotes with context, and synthesize patterns. "
                "You have direct access to academic sources and can perform thematic coding."
            )
        elif analysis_mode == "mixed":
            intro = (
                "You are Nocturnal, a truth-seeking research AI handling MIXED METHODS analysis. "
                "PRIMARY DIRECTIVE: Accuracy > Agreeableness. "
                "You work with both quantitative data (numbers, stats) and qualitative data (themes, quotes). "
                "For numbers: calculate and cite. For text: quote verbatim and identify patterns. "
                "You have access to production data sources and can write/execute code (Python, R, SQL)."
            )
        else:  # quantitative
            # Check if we're in dev mode (has local LLM client)
            dev_mode = self.client is not None
            
            if dev_mode:
                intro = (
                    "You are Cite Agent, a data analysis and research assistant with CODE EXECUTION. "
                    "PRIMARY DIRECTIVE: Execute code when needed. You have a persistent shell session. "
                    "When user asks for data analysis, calculations, or file operations: WRITE and EXECUTE the code. "
                    "Languages available: Python, R, SQL, Bash. "
                    "You can read files, run scripts, perform calculations, and show results."
                )
            else:
                intro = (
                    "You are Cite Agent, a truth-seeking research and finance AI with CODE EXECUTION. "
                    "PRIMARY DIRECTIVE: Accuracy > Agreeableness. Execute code for analysis, calculations, and file operations. "
                    "You are a fact-checker and analyst with a persistent shell session. "
                    "You have access to research (Archive), financial data (FinSight SEC filings), and can run Python/R/SQL/Bash. "
                    "When user asks about files, directories, or data: EXECUTE commands to find answers."
                )
        
        sections.append(intro)

        apis = request_analysis.get("apis", [])
        capability_lines: List[str] = []
        if "archive" in apis:
            capability_lines.append("• Archive Research API for academic search and synthesis")
        if "finsight" in apis:
            capability_lines.append("• FinSight Finance API for SEC-quality metrics and citations")
        if "shell" in apis:
            capability_lines.append("• Persistent shell session for system inspection and code execution")
        if not capability_lines:
            capability_lines.append("• Core reasoning, code generation (Python/R/SQL), memory recall")
        
        # Add workflow capabilities
        capability_lines.append("")
        capability_lines.append("📚 WORKFLOW INTEGRATION (Always available):")
        capability_lines.append("• You can SAVE papers to user's local library")
        capability_lines.append("• You can LIST papers from library")
        capability_lines.append("• You can EXPORT citations to BibTeX or APA")
        capability_lines.append("• You can SEARCH user's paper collection")
        capability_lines.append("• You can COPY text to user's clipboard")
        capability_lines.append("• User's query history is automatically tracked")

        # Add file operation capabilities (Claude Code / Cursor parity)
        capability_lines.append("")
        capability_lines.append("📁 DIRECT FILE OPERATIONS (Always available):")
        capability_lines.append("• read_file(path) - Read files with line numbers (like cat but better)")
        capability_lines.append("• write_file(path, content) - Create/overwrite files directly")
        capability_lines.append("• edit_file(path, old, new) - Surgical find/replace edits")
        capability_lines.append("• glob_search(pattern) - Fast file search (e.g., '**/*.py')")
        capability_lines.append("• grep_search(pattern) - Fast content search in files")
        capability_lines.append("• batch_edit_files(edits) - Multi-file refactoring")

        sections.append("Capabilities in play:\n" + "\n".join(capability_lines))

        # ENHANCED TRUTH-SEEKING RULES (adapt based on mode)
        base_rules = [
            "🚨 BE RESOURCEFUL: You have Archive, FinSight (SEC+Yahoo), and Web Search. USE them to find answers.",
            "🚨 TRY TOOLS FIRST: Before asking user for clarification, try your tools to find the answer.",
            "🚨 WEB SEARCH IS YOUR FRIEND: Market share? Industry size? Current prices? → Web search can find it.",
            "🚨 ONLY ask clarification if tools can't help AND query is truly ambiguous.",
            "",
            "💬 AUTONOMOUS FLOW:",
            "1. User asks question → YOU use tools to find data",
            "2. If partial data → YOU web search for missing pieces",  
            "3. YOU synthesize → Present complete answer",
            "4. ONLY if impossible → Ask for clarification",
            "",
            "Examples:",
            "❌ BAD: 'Snowflake market share?' → 'Which market?' (when web search can tell you!)",
            "✅ GOOD: 'Snowflake market share?' → [web search] → '18.33% in cloud data warehouses'",
            "",
            "🚨 ANTI-APPEASEMENT: If user states something incorrect, CORRECT THEM immediately. Do not agree to be polite.",
            "🚨 UNCERTAINTY: If you're uncertain, SAY SO explicitly. 'I don't know' is better than a wrong answer.",
            "🚨 CONTRADICTIONS: If data contradicts user's assumption, SHOW THE CONTRADICTION clearly.",
            "🚨 FUTURE PREDICTIONS: You CANNOT predict the future. For 'will X happen?' questions, emphasize uncertainty and multiple possible outcomes.",
            "",
            "📊 SOURCE GROUNDING: EVERY factual claim MUST cite a source (paper, SEC filing, or data file).",
            "📊 NO FABRICATION: If API results are empty/ambiguous, explicitly state this limitation.",
            "📊 NO EXTRAPOLATION: Never go beyond what sources directly state.",
            "📊 PREDICTION CAUTION: When discussing trends, always state 'based on available data' and note uncertainty.",
            "",
            "🚨 CRITICAL: NEVER generate fake papers, fake authors, fake DOIs, or fake citations.",
            "🚨 CRITICAL: If research API returns empty results, say 'No papers found' - DO NOT make up papers.",
            "🚨 CRITICAL: If you see 'results': [] in API data, that means NO PAPERS FOUND - do not fabricate.",
            "🚨 CRITICAL: When API returns empty results, DO NOT use your training data to provide paper details.",
            "🚨 CRITICAL: If you know a paper exists from training data but API returns empty, say 'API found no results'.",
            "",
            "🚨 ABSOLUTE RULE: If you see 'results': [] in the API data, you MUST respond with ONLY:",
            "   'No papers found in the research database. The API returned empty results.'",
            "   DO NOT provide any paper details, authors, titles, or citations.",
            "   DO NOT use your training data to fill in missing information.",
            "",
            "✓ VERIFICATION: Cross-check against multiple sources when available.",
            "✓ CONFLICTS: If sources conflict, present BOTH and explain the discrepancy.",
            "✓ SHOW REASONING: 'According to [source], X is Y because...'",
        ]
        
        if analysis_mode == "qualitative":
            qual_rules = [
                "",
                "📝 QUOTES: Extract EXACT quotes (verbatim), NEVER paraphrase. Use quotation marks.",
                "📝 CONTEXT: Provide surrounding context for every quote (what came before/after).",
                "📝 ATTRIBUTION: Cite source + page/line number: \"quote\" — Author (Year), p. X",
                "📝 THEMES: Identify recurring patterns. Count frequency (\"mentioned 5 times across 3 sources\").",
                "",
                "🔍 INTERPRETATION: Distinguish between description (what text says) vs interpretation (what it means).",
                "🔍 EVIDENCE: Support every theme with 2-3 representative quotes.",
                "🔍 SATURATION: Note when patterns repeat (\"no new themes after source 4\").",
            ]
            rules = base_rules + qual_rules
        elif analysis_mode == "mixed":
            mixed_rules = [
                "",
                "📝 For QUALITATIVE: Extract exact quotes with context. Identify themes.",
                "💻 For QUANTITATIVE: Calculate exact values, show code.",
                "🔗 INTEGRATION: Connect numbers to narratives ('15% growth' + 'participants felt optimistic')."
            ]
            rules = base_rules + mixed_rules + [
                "",
                "💻 CODE: For data analysis, write and execute Python/R/SQL code. Show your work.",
                "💻 CALCULATIONS: Don't estimate - calculate exact values and show the code.",
            ]
        else:  # quantitative
            quant_rules = [
                "",
                "💻 CODE: For data analysis, write and execute Python/R/SQL code. Show your work.",
                "💻 CALCULATIONS: Don't estimate - calculate exact values and show the code.",
            ]
            rules = base_rules + quant_rules
        
        rules.append("")
        rules.append("Keep responses concise but complete. Quote exact text from sources when possible.")
        
        # Add workflow behavior rules
        workflow_rules = [
            "",
            "📚 WORKFLOW BEHAVIOR:",
            "• After finding papers, OFFER to save them: 'Would you like me to save this to your library?'",
            "• After showing a citation, ASK: 'Want me to copy that to your clipboard?'",
            "• If user says 'save that' or 'add to library', ACKNOWLEDGE and confirm the save",
            "• If user mentions 'my library', LIST their saved papers",
            "• If user asks for 'bibtex' or 'apa', PROVIDE the formatted citation",
            "• Be PROACTIVE: suggest exports, show library stats, offer clipboard copies",
            "• Example: 'I found 3 papers. I can save them to your library or export to BibTeX if you'd like.'",
        ]
        rules.extend(workflow_rules)

        # Add file operation tool usage rules (CRITICAL for Claude Code parity)
        file_ops_rules = [
            "",
            "📁 FILE OPERATION TOOL USAGE (Use these INSTEAD of shell commands):",
            "",
            "🔴 ALWAYS PREFER (in order):",
            "1. read_file(path) → INSTEAD OF: cat, head, tail",
            "2. write_file(path, content) → INSTEAD OF: echo >, cat << EOF, printf >",
            "3. edit_file(path, old, new) → INSTEAD OF: sed, awk",
            "4. glob_search(pattern, path) → INSTEAD OF: find, ls",
            "5. grep_search(pattern, path, file_pattern) → INSTEAD OF: grep -r",
            "",
            "✅ CORRECT USAGE:",
            "• Reading code: result = read_file('app.py')",
            "• Creating file: write_file('config.json', '{...}')",
            "• Editing code: edit_file('main.py', 'old_var', 'new_var', replace_all=True)",
            "• Finding files: glob_search('**/*.py', '/home/user/project')",
            "• Searching code: grep_search('class.*Agent', '.', '*.py', output_mode='content')",
            "• Multi-file refactor: batch_edit_files([{file: 'a.py', old: '...', new: '...'}, ...])",
            "",
            "❌ ANTI-PATTERNS (Don't do these):",
            "• DON'T use cat when read_file exists",
            "• DON'T use echo > when write_file exists",
            "• DON'T use sed when edit_file exists",
            "• DON'T use find when glob_search exists",
            "• DON'T use grep -r when grep_search exists",
            "",
            "🎯 WHY USE THESE TOOLS:",
            "• read_file() shows line numbers (critical for code analysis)",
            "• write_file() handles escaping/quoting automatically (no heredoc hell)",
            "• edit_file() validates changes before applying (safer than sed)",
            "• glob_search() is faster and cleaner than find",
            "• grep_search() returns structured data (easier to parse)",
            "",
            "⚠️ SHELL COMMANDS ONLY FOR:",
            "• System operations (ps, df, du, uptime)",
            "• Git commands (git status, git diff, git log)",
            "• Package installs (pip install, Rscript -e \"install.packages(...)\")",
            "• Running Python/R scripts (python script.py, Rscript analysis.R)",
        ]
        rules.extend(file_ops_rules)
        
        sections.append("CRITICAL RULES:\n" + "\n".join(rules))
        
        # CORRECTION EXAMPLES (adapt based on mode)
        if analysis_mode == "qualitative":
            examples = (
                "EXAMPLE RESPONSES:\n"
                "User: 'So participants felt happy about the change?'\n"
                "You: '⚠️ Mixed. 3 participants expressed satisfaction: \"I welcomed the new policy\" (P2, line 45), "
                "but 2 expressed concern: \"It felt rushed\" (P4, line 67). Theme: Ambivalence about pace.'\n\n"
                "User: 'What's the main theme?'\n"
                "You: 'THEME 1: Trust in leadership (8 mentions across 4 interviews)\n"
                "\"I trust my manager to make the right call\" — Interview 2, Line 34\n"
                "\"Leadership has been transparent\" — Interview 5, Line 89\n"
                "[Context: Both quotes from questions about organizational changes]'"
            )
        else:
            examples = (
                "EXAMPLE 1: Be Patient, Don't Rush\n"
                "User: 'Find papers on 2008, 2015, 2019'\n"
                "❌ BAD: [Searches for year:2008 immediately] 'Found 50 papers from 2008...'\n"
                "✅ GOOD: 'Are you looking for papers ABOUT events in those years (financial crises, policy changes), "
                "or papers PUBLISHED in those years? Also, what topic? (Economics? Healthcare? Climate?)'\n\n"
                
                "EXAMPLE 2: Know Your Tools' Limits\n"
                "User: 'What's Palantir's market share?'\n"
                "❌ BAD: 'Palantir's latest revenue is $1B...' (Revenue ≠ Market Share! SEC doesn't have market share!)\n"
                "✅ GOOD: 'Market share requires: (1) Palantir's revenue, (2) total market size. SEC has #1, not #2. "
                "Which market? (Data analytics = ~$50B, Gov contracts = ~$200B). I can web search for total market size if you specify.'\n\n"
                
                "EXAMPLE 3: Conversational Flow\n"
                "User: 'Compare Tesla and Ford'\n"
                "❌ BAD: [Immediately fetches both revenues] 'Tesla: $81B, Ford: $158B'\n"
                "✅ GOOD: 'Compare on what dimension? Revenue? (Ford larger). Market cap? (Tesla larger). EV sales? (Tesla dominates). "
                "Production volume? (Ford higher). Each tells a different story. Which matters to you?'\n\n"
                
                "EXAMPLE CORRECTIONS:\n"
                "User: 'So revenue went up 50%?'\n"
                "You: '❌ No. According to 10-K page 23, revenue increased 15%, not 50%. "
                "You may be thinking of gross margin (30%→45%, a 15pp increase).'\n\n"
                "User: 'What will the stock price be?'\n"
                "You: '⚠️ Cannot predict future prices. I can show: historical trends, current fundamentals, analyst data (if in filings).'"
            )
        
        sections.append(examples)

        if memory_context:
            sections.append("CONTEXT:\n" + memory_context.strip())

        sections.append(
            "REQUEST ANALYSIS: "
            f"type={request_analysis.get('type')}, "
            f"apis={apis}, "
            f"confidence={request_analysis.get('confidence')}"
        )

        # Add explicit instruction before API results
        api_instructions = (
            "🚨 CRITICAL: The following API RESULTS are REAL DATA from production APIs.\n"
            "🚨 These are NOT examples or templates - they are ACTUAL results to use in your response.\n"
            "🚨 DO NOT generate new/fake data - USE EXACTLY what is shown below.\n"
            "🚨 If you see paper titles, authors, DOIs below - these are REAL papers you MUST cite.\n"
            "🚨 If API results show empty/no papers, say 'No papers found' - DO NOT make up papers.\n"
        )

        sections.append(api_instructions + "\nAPI RESULTS:\n" + self._format_api_results_for_prompt(api_results))

        return "\n\n".join(sections)

    def _quick_reply(
        self,
        request: ChatRequest,
        message: str,
        tools_used: Optional[List[str]] = None,
        confidence: float = 0.6
    ) -> ChatResponse:
        tools = tools_used or []
        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(
            request.user_id,
            request.conversation_id,
            f"Q: {request.question[:100]}... A: {message[:100]}..."
        )
        self._emit_telemetry(
            "quick_reply",
            request,
            success=True,
            extra={
                "tools_used": tools,
            },
        )
        return ChatResponse(
            response=message,
            tools_used=tools,
            reasoning_steps=["Quick reply without LLM"],
            timestamp=datetime.now().isoformat(),
            tokens_used=0,
            confidence_score=confidence,
            execution_results={},
            api_results={}
        )

    def _select_model(
        self,
        request: ChatRequest,
        request_analysis: Dict[str, Any],
        api_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        question = request.question.strip()
        apis = request_analysis.get("apis", [])
        use_light_model = False

        if len(question) <= 180 and not api_results and not apis:
            use_light_model = True
        elif len(question) <= 220 and set(apis).issubset({"shell"}):
            use_light_model = True
        elif len(question.split()) <= 40 and request_analysis.get("type") in {"general", "system"} and not api_results:
            use_light_model = True

        # Select model based on LLM provider
        if getattr(self, 'llm_provider', 'groq') == 'cerebras':
            if use_light_model:
                return {
                    "model": "llama3.1-8b",  # Cerebras 8B model
                    "max_tokens": 520,
                    "temperature": 0.2
                }
            return {
                "model": "llama-3.3-70b",  # Cerebras 70B model
                "max_tokens": 900,
                "temperature": 0.3
            }
        else:
            # Groq models
            if use_light_model:
                return {
                    "model": "llama-3.1-8b-instant",
                    "max_tokens": 520,
                    "temperature": 0.2
                }
            return {
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 900,
                "temperature": 0.3
            }

    def _mark_current_key_exhausted(self, reason: str = "rate_limit"):
        if not self.api_keys:
            return
        key = self.api_keys[self.current_key_index]
        self.exhausted_keys[key] = time.time()
        logger.warning(f"Groq key index {self.current_key_index} marked exhausted ({reason})")

    def _rotate_to_next_available_key(self) -> bool:
        if not self.api_keys:
            return False

        attempts = 0
        total = len(self.api_keys)
        now = time.time()

        while attempts < total:
            self.current_key_index = (self.current_key_index + 1) % total
            key = self.api_keys[self.current_key_index]
            exhausted_at = self.exhausted_keys.get(key)
            if exhausted_at:
                if now - exhausted_at >= self.key_recheck_seconds:
                    del self.exhausted_keys[key]
                else:
                    attempts += 1
                    continue
            try:
                if self.llm_provider == "cerebras":
                    from openai import OpenAI
                    self.client = OpenAI(
                        api_key=key,
                        base_url="https://api.cerebras.ai/v1"
                    )
                else:
                    self.client = Groq(api_key=key)
                self.current_api_key = key
                return True
            except Exception as e:
                logger.error(f"Failed to initialize {self.llm_provider.upper()} client for rotated key: {e}")
                self.exhausted_keys[key] = now
                attempts += 1
        return False

    def _ensure_client_ready(self) -> bool:
        if self.client and self.current_api_key:
            return True

        if not self.api_keys:
            return False

        total = len(self.api_keys)
        attempts = 0
        now = time.time()

        while attempts < total:
            key = self.api_keys[self.current_key_index]
            exhausted_at = self.exhausted_keys.get(key)
            if exhausted_at and (now - exhausted_at) < self.key_recheck_seconds:
                attempts += 1
                self.current_key_index = (self.current_key_index + 1) % total
                continue

            if exhausted_at and (now - exhausted_at) >= self.key_recheck_seconds:
                del self.exhausted_keys[key]

            try:
                if self.llm_provider == "cerebras":
                    from openai import OpenAI
                    self.client = OpenAI(
                        api_key=key,
                        base_url="https://api.cerebras.ai/v1"
                    )
                else:
                    self.client = Groq(api_key=key)
                self.current_api_key = key
                return True
            except Exception as e:
                logger.error(f"Failed to initialize {self.llm_provider.upper()} client for key index {self.current_key_index}: {e}")
                self.exhausted_keys[key] = now
                attempts += 1
                self.current_key_index = (self.current_key_index + 1) % total

        return False

    def _schedule_next_key_rotation(self):
        if len(self.api_keys) <= 1:
            return
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.current_api_key = None
        self.client = None

    def _is_rate_limit_error(self, error: Exception) -> bool:
        message = str(error).lower()
        return "rate limit" in message or "429" in message

    def _respond_with_fallback(
        self,
        request: ChatRequest,
        tools_used: List[str],
        api_results: Dict[str, Any],
        failure_reason: str,
        error_message: Optional[str] = None
    ) -> ChatResponse:
        tools = list(tools_used) if tools_used else []
        if "fallback" not in tools:
            tools.append("fallback")

        header = "⚠️ Temporary LLM downtime\n\n"

        if self._is_simple_greeting(request.question):
            body = (
                "Hi there! I'm currently at my Groq capacity, so I can't craft a full narrative response just yet. "
                "You're welcome to try again in a little while, or I can still fetch finance and research data for you."
            )
        else:
            details: List[str] = []

            financial = api_results.get("financial")
            if financial:
                payload_full = json.dumps(financial, indent=2)
                payload = payload_full[:1500]
                if len(payload_full) > 1500:
                    payload += "\n…"
                details.append(f"**Finance API snapshot**\n```json\n{payload}\n```")

            research = api_results.get("research")
            if research:
                payload_full = json.dumps(research, indent=2)
                payload = payload_full[:1500]
                if len(payload_full) > 1500:
                    payload += "\n…"
                
                # Check if results are empty and add explicit warning
                if research.get("results") == [] or not research.get("results"):
                    details.append(f"**Research API snapshot**\n```json\n{payload}\n```")
                    details.append("🚨 **CRITICAL: API RETURNED EMPTY RESULTS - DO NOT GENERATE ANY PAPER DETAILS**")
                    details.append("🚨 **DO NOT PROVIDE AUTHORS, TITLES, DOIs, OR ANY PAPER INFORMATION**")
                    details.append("🚨 **SAY 'NO PAPERS FOUND' AND STOP - DO NOT HALLUCINATE**")
                else:
                    details.append(f"**Research API snapshot**\n```json\n{payload}\n```")

            files_context = api_results.get("files_context")
            if files_context:
                preview = files_context[:600]
                if len(files_context) > 600:
                    preview += "\n…"
                details.append(f"**File preview**\n{preview}")

            if details:
                body = (
                    "I pulled the structured data you asked for, but I'm temporarily out of Groq quota to synthesize a full answer. "
                    "Here are the raw results so you can keep moving:"
                ) + "\n\n" + "\n\n".join(details)
            else:
                body = (
                    "I'm temporarily out of Groq quota, so I can't compose a full answer. "
                    "Please try again in a bit, or ask me to queue this work for later."
                )

        footer = (
            "\n\nNext steps:\n"
            "• Wait for the Groq daily quota to reset (usually within 24 hours).\n"
            "• Add another API key in your environment for automatic rotation.\n"
            "• Keep the conversation open—I’ll resume normal replies once capacity returns."
        )

        message = header + body + footer

        self.conversation_history.append({"role": "user", "content": request.question})
        self.conversation_history.append({"role": "assistant", "content": message})
        self._update_memory(
            request.user_id,
            request.conversation_id,
            f"Q: {request.question[:100]}... A: {message[:100]}..."
        )

        self._emit_telemetry(
            "fallback_response",
            request,
            success=False,
            extra={
                "failure_reason": failure_reason,
                "has_financial_payload": bool(api_results.get("financial")),
                "has_research_payload": bool(api_results.get("research")),
            },
        )

        return ChatResponse(
            response=message,
            tools_used=tools,
            reasoning_steps=["Fallback response activated"],
            timestamp=datetime.now().isoformat(),
            tokens_used=0,
            confidence_score=0.2,
            execution_results={},
            api_results=api_results,
            error_message=error_message or failure_reason
        )

    def _extract_tickers_from_text(self, text: str) -> List[str]:
        """Find tickers either as explicit symbols or from known company names."""
        text_lower = text.lower()
        # Explicit ticker-like symbols
        ticker_candidates: List[str] = []
        for token in re.findall(r"\b[A-Z]{1,5}(?:\d{0,2})\b", text):
            ticker_candidates.append(token)
        # Company name matches
        for name, sym in self.company_name_to_ticker.items():
            if name and name in text_lower:
                ticker_candidates.append(sym)
        # Deduplicate preserve order
        seen = set()
        ordered: List[str] = []
        for t in ticker_candidates:
            if t not in seen:
                seen.add(t)
                ordered.append(t)
        return ordered[:4]
    
    async def initialize(self, force_reload: bool = False):
        """Initialize the agent with API keys and shell session."""
        lock = self._get_init_lock()
        async with lock:
            if self._initialized and not force_reload:
                return True

            if self._initialized and force_reload:
                await self._close_resources()

            # Check for updates automatically (silent background check)
            self._check_updates_background()
            self._ensure_environment_loaded()
            self._init_api_clients()
            
            # Suppress verbose initialization messages in production
            import logging
            logging.getLogger("aiohttp").setLevel(logging.ERROR)
            logging.getLogger("asyncio").setLevel(logging.ERROR)

            # SECURITY FIX: No API keys on client!
            # All API calls go through our secure backend
            # This prevents key extraction and piracy
            # DISABLED for beta testing - set USE_LOCAL_KEYS=false to enable backend-only mode

            # SECURITY: Production users MUST use backend for monetization
            # Priority: 1) Session exists → backend, 2) USE_LOCAL_KEYS → dev mode
            from pathlib import Path
            session_file = Path.home() / ".nocturnal_archive" / "session.json"
            has_session = session_file.exists()
            use_local_keys_env = os.getenv("USE_LOCAL_KEYS", "").lower()

            if has_session:
                # Session exists → ALWAYS use backend mode (ignore USE_LOCAL_KEYS)
                use_local_keys = False
            elif use_local_keys_env == "true":
                # No session but dev mode requested → use local keys
                use_local_keys = True
            elif use_local_keys_env == "false":
                # Explicit backend mode
                use_local_keys = False
            else:
                # Default: Always use backend (for monetization)
                use_local_keys = False

            if not use_local_keys:
                self.api_keys = []  # Empty - keys stay on server
                self.current_key_index = 0
                self.current_api_key = None
                self.client = None  # Will use HTTP client instead

                # Get backend API URL from config
                self.backend_api_url = os.getenv(
                    "NOCTURNAL_API_URL",
                    "https://cite-agent-api-720dfadd602c.herokuapp.com/api"  # Production Heroku backend
                )

                # Get auth token from session (set by auth.py after login)
                from pathlib import Path
                session_file = Path.home() / ".nocturnal_archive" / "session.json"
                if session_file.exists():
                    try:
                        import json
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)
                            self.auth_token = session_data.get('auth_token')
                            self.user_id = session_data.get('account_id')
                    except Exception:
                        self.auth_token = None
                        self.user_id = None
                else:
                    self.auth_token = None
                    self.user_id = None

                # Suppress messages in production (only show in debug mode)
                debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
                if debug_mode:
                    if self.auth_token:
                        print(f"✅ Enhanced Nocturnal Agent Ready! (Authenticated)")
                    else:
                        print("⚠️ Not authenticated. Please log in to use the agent.")
            else:
                # Local keys mode - load Cerebras API keys (primary) with Groq fallback
                self.auth_token = None
                self.user_id = None

                # Load Cerebras keys from environment (PRIMARY)
                self.api_keys = []
                for i in range(1, 10):  # Check CEREBRAS_API_KEY_1 through CEREBRAS_API_KEY_9
                    key = os.getenv(f"CEREBRAS_API_KEY_{i}") or os.getenv(f"CEREBRAS_API_KEY")
                    if key and key not in self.api_keys:
                        self.api_keys.append(key)

                # Fallback to Groq keys if no Cerebras keys found
                if not self.api_keys:
                    for i in range(1, 10):
                        key = os.getenv(f"GROQ_API_KEY_{i}") or os.getenv(f"GROQ_API_KEY")
                        if key and key not in self.api_keys:
                            self.api_keys.append(key)
                    self.llm_provider = "groq"
                else:
                    self.llm_provider = "cerebras"

                debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
                if not self.api_keys:
                    if debug_mode:
                        print("⚠️ No LLM API keys found. Set CEREBRAS_API_KEY or GROQ_API_KEY")
                else:
                    if debug_mode:
                        print(f"✅ Loaded {len(self.api_keys)} {self.llm_provider.upper()} API key(s)")
                    # Initialize first client - Cerebras uses OpenAI-compatible API
                    try:
                        if self.llm_provider == "cerebras":
                            # Cerebras uses OpenAI client with custom base URL
                            from openai import OpenAI
                            self.client = OpenAI(
                                api_key=self.api_keys[0],
                                base_url="https://api.cerebras.ai/v1"
                            )
                        else:
                            # Groq fallback
                            from groq import Groq
                            self.client = Groq(api_key=self.api_keys[0])
                        self.current_api_key = self.api_keys[0]
                        self.current_key_index = 0
                    except Exception as e:
                        print(f"⚠️ Failed to initialize {self.llm_provider.upper()} client: {e}")

            # Initialize shell session for BOTH production and dev mode
            # Production users need code execution too (like Cursor/Aider)
            if self.shell_session and self.shell_session.poll() is not None:
                self.shell_session = None

            if self.shell_session is None:
                try:
                    self.shell_session = subprocess.Popen(
                        ['bash'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=os.getcwd()
                    )
                except Exception as exc:
                    print(f"⚠️ Unable to launch persistent shell session: {exc}")
                    self.shell_session = None

            if self.session is None or getattr(self.session, "closed", False):
                if self.session and not self.session.closed:
                    await self.session.close()
                default_headers = dict(getattr(self, "_default_headers", {}))
                self.session = aiohttp.ClientSession(headers=default_headers)

            self._initialized = True
            return True
    
    def _check_updates_background(self):
        """Check for updates and auto-install if available"""
        if not self._auto_update_enabled:
            return
        
        # Check for updates (synchronous, fast)
        try:
            from .updater import NocturnalUpdater
            updater = NocturnalUpdater()
            update_info = updater.check_for_updates()
            
            if update_info and update_info["available"]:
                # Auto-update silently in background
                import threading
                def do_update():
                    try:
                        updater.update_package(silent=True)
                    except:
                        pass
                threading.Thread(target=do_update, daemon=True).start()
                
        except Exception:
            # Silently ignore update check failures
            pass
    
    async def call_backend_query(self, query: str, conversation_history: Optional[List[Dict]] = None, 
                                 api_results: Optional[Dict[str, Any]] = None, tools_used: Optional[List[str]] = None) -> ChatResponse:
        """
        Call backend /query endpoint instead of Groq directly
        This is the SECURE method - all API keys stay on server
        Includes API results (Archive, FinSight) in context for better responses
        """
        # DEBUG: Print auth status
        debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
        if debug_mode:
            print(f"🔍 call_backend_query: auth_token={self.auth_token}, user_id={self.user_id}")
        
        if not self.auth_token:
            return ChatResponse(
                response="❌ Not authenticated. Please log in first.",
                error_message="Authentication required"
            )
        
        if not self.session:
            return ChatResponse(
                response="❌ HTTP session not initialized",
                error_message="Session not initialized"
            )
        
        try:
            # Build request with API context as separate field
            payload = {
                "query": query,  # Keep query clean
                "conversation_history": conversation_history or [],
                "api_context": api_results,  # Send API results separately
                "model": "llama-3.3-70b",  # Compatible with Cerebras (priority) and Groq
                "temperature": 0.2,  # Low temp for accuracy
                "max_tokens": 4000
            }
            
            # Call backend
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.backend_api_url}/query/"
            
            async with self.session.post(url, json=payload, headers=headers, timeout=60) as response:
                if response.status == 401:
                    return ChatResponse(
                        response="❌ Authentication expired. Please log in again.",
                        error_message="Authentication expired"
                    )
                
                elif response.status == 429:
                    # Rate limit exceeded
                    data = await response.json()
                    detail = data.get('detail', {})
                    tokens_remaining = detail.get('tokens_remaining', 0)
                    return ChatResponse(
                        response=f"❌ Daily token limit reached. You have {tokens_remaining} tokens remaining today. The limit resets tomorrow.",
                        error_message="Rate limit exceeded",
                        tokens_used=detail.get('tokens_used_today', 0)
                    )
                
                elif response.status == 503:
                    # Backend AI service temporarily unavailable (Cerebras/Groq rate limited)
                    # Auto-retry silently with exponential backoff
                    
                    print("\n💭 Thinking... (backend is busy, retrying automatically)")
                    
                    import asyncio
                    retry_delays = [5, 15, 30]  # Exponential backoff
                    
                    for retry_num, delay in enumerate(retry_delays):
                        await asyncio.sleep(delay)
                        
                        # Retry the request
                        async with self.session.post(url, json=payload, headers=headers, timeout=60) as retry_response:
                            if retry_response.status == 200:
                                # Success!
                                data = await retry_response.json()
                                response_text = data.get('response', '')
                                tokens = data.get('tokens_used', 0)
                                
                                all_tools = tools_used or []
                                all_tools.append("backend_llm")
                                
                                self.workflow.save_query_result(
                                    query=query,
                                    response=response_text,
                                    metadata={
                                        "tools_used": all_tools,
                                        "tokens_used": tokens,
                                        "model": data.get('model'),
                                        "provider": data.get('provider'),
                                        "retries": retry_num + 1
                                    }
                                )
                                
                                return ChatResponse(
                                    response=response_text,
                                    tokens_used=tokens,
                                    tools_used=all_tools,
                                    model=data.get('model', 'llama-3.3-70b'),
                                    timestamp=data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                                    api_results=api_results
                                )
                            elif retry_response.status != 503:
                                # Different error, stop retrying
                                break
                    
                    # All retries exhausted
                    return ChatResponse(
                        response="❌ Service unavailable. Please try again in a few minutes.",
                        error_message="Service unavailable after retries"
                    )
                
                elif response.status == 200:
                    data = await response.json()
                    response_text = data.get('response', '')
                    tokens = data.get('tokens_used', 0)
                    
                    # Combine tools used
                    all_tools = tools_used or []
                    all_tools.append("backend_llm")
                    
                    # Save to workflow history
                    self.workflow.save_query_result(
                        query=query,
                        response=response_text,
                        metadata={
                            "tools_used": all_tools,
                            "tokens_used": tokens,
                            "model": data.get('model'),
                            "provider": data.get('provider')
                        }
                    )
                    
                    return ChatResponse(
                        response=response_text,
                        tokens_used=tokens,
                        tools_used=all_tools,
                        model=data.get('model', 'llama-3.3-70b-versatile'),
                        timestamp=data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                        api_results=api_results
                    )
                
                else:
                    error_text = await response.text()
                    return ChatResponse(
                        response=f"❌ Backend error (HTTP {response.status}): {error_text}",
                        error_message=f"HTTP {response.status}"
                    )
        
        except asyncio.TimeoutError:
            return ChatResponse(
                response="❌ Request timeout. Please try again.",
                error_message="Timeout"
            )
        except Exception as e:
            return ChatResponse(
                response=f"❌ Error calling backend: {str(e)}",
                error_message=str(e)
            )
    
    async def _call_files_api(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        data: Any = None,
    ) -> Dict[str, Any]:
        if not self.session:
            return {"error": "HTTP session not initialized"}

        ok, detail = await self._ensure_backend_ready()
        if not ok:
            self._record_data_source("Files", f"{method.upper()} {endpoint}", False, detail)
            return {"error": f"Workspace API unavailable: {detail or 'backend offline'}"}

        url = f"{self.files_base_url}{endpoint}"
        request_method = getattr(self.session, method.lower(), None)
        if not request_method:
            return {"error": f"Unsupported HTTP method: {method}"}

        try:
            async with request_method(url, params=params, json=json_body, data=data, timeout=20) as response:
                payload: Any
                if response.content_type and "json" in response.content_type:
                    payload = await response.json()
                else:
                    payload = {"raw": await response.text()}

                success = response.status == 200
                self._record_data_source(
                    "Files",
                    f"{method.upper()} {endpoint}",
                    success,
                    "" if success else f"HTTP {response.status}"
                )

                if success:
                    return payload if isinstance(payload, dict) else {"data": payload}

                detail_msg = payload.get("detail") if isinstance(payload, dict) else None
                return {"error": detail_msg or f"Files API error: {response.status}"}
        except Exception as exc:
            self._record_data_source("Files", f"{method.upper()} {endpoint}", False, str(exc))
            return {"error": f"Files API call failed: {exc}"}

    async def _call_archive_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Archive API endpoint with retry mechanism"""
        max_retries = 3
        retry_delay = 1
        
        ok, detail = await self._ensure_backend_ready()
        if not ok:
            self._record_data_source("Archive", f"POST {endpoint}", False, detail)
            return {"error": f"Archive backend unavailable: {detail or 'backend offline'}"}

        for attempt in range(max_retries):
            try:
                if not self.session:
                    return {"error": "HTTP session not initialized"}
                
                url = f"{self.archive_base_url}/{endpoint}"
                # Start fresh with headers
                headers = {}
                
                # Always use demo key for Archive (public research data)
                headers["X-API-Key"] = "demo-key-123"
                headers["Content-Type"] = "application/json"
                
                # Also add JWT if we have it
                if self.auth_token:
                    headers["Authorization"] = f"Bearer {self.auth_token}"
                
                debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
                if debug_mode:
                    print(f"🔍 Archive headers: {list(headers.keys())}, X-API-Key={headers.get('X-API-Key')}")
                    print(f"🔍 Archive URL: {url}")
                    print(f"🔍 Archive data: {data}")
                
                async with self.session.post(url, json=data, headers=headers, timeout=30) as response:
                    if debug_mode:
                        print(f"🔍 Archive response status: {response.status}")
                    
                    if response.status == 200:
                        payload = await response.json()
                        self._record_data_source("Archive", f"POST {endpoint}", True)
                        return payload
                    elif response.status == 422:  # Validation error
                        try:
                            error_detail = await response.json()
                            logger.error(f"Archive API validation error (HTTP 422): {error_detail}")
                        except Exception:
                            error_detail = await response.text()
                            logger.error(f"Archive API validation error (HTTP 422): {error_detail}")

                        if attempt < max_retries - 1:
                            # Retry with simplified request
                            if "sources" in data and len(data["sources"]) > 1:
                                data["sources"] = [data["sources"][0]]  # Try single source
                                logger.info(f"Retrying with single source: {data['sources']}")
                            await asyncio.sleep(retry_delay)
                            continue
                        self._record_data_source("Archive", f"POST {endpoint}", False, "422 validation error")
                        return {"error": f"Archive API validation error: {error_detail}"}
                    elif response.status == 429:  # Rate limited
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            continue
                        self._record_data_source("Archive", f"POST {endpoint}", False, "rate limited")
                        return {"error": "Archive API rate limited. Please try again later."}
                    elif response.status == 401:
                        self._record_data_source("Archive", f"POST {endpoint}", False, "401 unauthorized")
                        return {"error": "Archive API authentication failed. Please check API key."}
                    else:
                        error_text = await response.text()
                        logger.error(f"Archive API error (HTTP {response.status}): {error_text}")
                        self._record_data_source("Archive", f"POST {endpoint}", False, f"HTTP {response.status}")
                        return {"error": f"Archive API error: {response.status}"}
                        
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                self._record_data_source("Archive", f"POST {endpoint}", False, "timeout")
                return {"error": "Archive API timeout. Please try again later."}
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                self._record_data_source("Archive", f"POST {endpoint}", False, str(e))
                return {"error": f"Archive API call failed: {e}"}
        
        return {"error": "Archive API call failed after all retries"}
    
    async def _call_finsight_api(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call FinSight API endpoint with retry mechanism"""
        max_retries = 3
        retry_delay = 1
        
        ok, detail = await self._ensure_backend_ready()
        if not ok:
            self._record_data_source("FinSight", f"GET {endpoint}", False, detail)
            return {"error": f"FinSight backend unavailable: {detail or 'backend offline'}"}

        for attempt in range(max_retries):
            try:
                if not self.session:
                    return {"error": "HTTP session not initialized"}
                
                url = f"{self.finsight_base_url}/{endpoint}"
                # Start fresh with headers - don't use _default_headers which might be wrong
                headers = {}

                # Always use demo key for FinSight (SEC data is public)
                headers["X-API-Key"] = "demo-key-123"

                # Mark request as agent-mediated for product separation
                headers["X-Request-Source"] = "agent"

                # Also add JWT if we have it
                if self.auth_token:
                    headers["Authorization"] = f"Bearer {self.auth_token}"

                debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
                if debug_mode:
                    print(f"🔍 FinSight headers: {list(headers.keys())}, X-API-Key={headers.get('X-API-Key')}")
                    print(f"🔍 FinSight URL: {url}")
                
                async with self.session.get(url, params=params, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        payload = await response.json()
                        self._record_data_source("FinSight", f"GET {endpoint}", True)
                        return payload
                    elif response.status == 429:  # Rate limited
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                            continue
                        self._record_data_source("FinSight", f"GET {endpoint}", False, "rate limited")
                        return {"error": "FinSight API rate limited. Please try again later."}
                    elif response.status == 401:
                        self._record_data_source("FinSight", f"GET {endpoint}", False, "401 unauthorized")
                        return {"error": "FinSight API authentication failed. Please check API key."}
                    else:
                        self._record_data_source("FinSight", f"GET {endpoint}", False, f"HTTP {response.status}")
                        return {"error": f"FinSight API error: {response.status}"}
                        
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                self._record_data_source("FinSight", f"GET {endpoint}", False, "timeout")
                return {"error": "FinSight API timeout. Please try again later."}
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                self._record_data_source("FinSight", f"GET {endpoint}", False, str(e))
                return {"error": f"FinSight API call failed: {e}"}
        
        return {"error": "FinSight API call failed after all retries"}
    
    async def _call_finsight_api_post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call FinSight API endpoint with POST request"""
        ok, detail = await self._ensure_backend_ready()
        if not ok:
            self._record_data_source("FinSight", f"POST {endpoint}", False, detail)
            return {"error": f"FinSight backend unavailable: {detail or 'backend offline'}"}

        try:
            if not self.session:
                return {"error": "HTTP session not initialized"}
            
            url = f"{self.finsight_base_url}/{endpoint}"
            headers = getattr(self, "_default_headers", None)
            if headers:
                headers = dict(headers)
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    payload = await response.json()
                    self._record_data_source("FinSight", f"POST {endpoint}", True)
                    return payload
                self._record_data_source("FinSight", f"POST {endpoint}", False, f"HTTP {response.status}")
                return {"error": f"FinSight API error: {response.status}"}
                    
        except Exception as e:
            self._record_data_source("FinSight", f"POST {endpoint}", False, str(e))
            return {"error": f"FinSight API call failed: {e}"}
    
    async def search_academic_papers(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search academic papers using Archive API with resilient fallbacks."""
        source_sets: List[List[str]] = [
            ["semantic_scholar", "openalex"],
            ["semantic_scholar"],
            ["openalex"],
            ["pubmed"],
            ["offline"],
        ]

        tried: List[List[str]] = []
        provider_errors: List[Dict[str, Any]] = []
        aggregated_payload: Dict[str, Any] = {"results": []}

        for sources in source_sets:
            data = {"query": query, "limit": limit, "sources": sources}
            tried.append(list(sources))
            result = await self._call_archive_api("search", data)

            if "error" in result:
                provider_errors.append({"sources": sources, "error": result["error"]})
                continue

            results = result.get("results") or result.get("papers") or []
            # Validate papers have minimal required fields
            validated_results = []
            for paper in results:
                if isinstance(paper, dict) and paper.get("title") and paper.get("year"):
                    validated_results.append(paper)
                else:
                    logger.warning(f"Skipping invalid paper: {paper}")

            if validated_results:
                aggregated_payload = dict(result)
                aggregated_payload["results"] = validated_results
                aggregated_payload["validation_note"] = f"Validated {len(validated_results)} out of {len(results)} papers"
                break

        aggregated_payload.setdefault("results", [])
        aggregated_payload["sources_tried"] = [",".join(s) for s in tried]

        if provider_errors:
            aggregated_payload["provider_errors"] = provider_errors

        # CRITICAL: Add explicit marker for empty results to prevent hallucination
        if not aggregated_payload["results"]:
            aggregated_payload["notes"] = (
                "No papers were returned by the research providers. This often occurs during "
                "temporary rate limits; please retry in a minute or adjust the query scope."
            )
            aggregated_payload["EMPTY_RESULTS"] = True
            aggregated_payload["warning"] = "DO NOT GENERATE FAKE PAPERS - API returned zero results"

        return aggregated_payload
    
    async def synthesize_research(self, paper_ids: List[str], max_words: int = 500) -> Dict[str, Any]:
        """Synthesize research papers using Archive API"""
        data = {
            "paper_ids": paper_ids,
            "max_words": max_words,
            "focus": "key_findings",
            "style": "academic"
        }
        return await self._call_archive_api("synthesize", data)
    
    async def get_financial_data(self, ticker: str, metric: str, limit: int = 12) -> Dict[str, Any]:
        """Get financial data using FinSight API"""
        params = {
            "freq": "Q",
            "limit": limit
        }
        return await self._call_finsight_api(f"kpis/{ticker}/{metric}", params)
    
    async def get_financial_metrics(self, ticker: str, metrics: List[str] = None) -> Dict[str, Any]:
        """Get financial metrics using FinSight KPI endpoints (with schema drift fixes)"""
        if metrics is None:
            metrics = ["revenue", "grossProfit", "operatingIncome", "netIncome"]

        if not metrics:
            return {}

        async def _fetch_metric(metric_name: str) -> Dict[str, Any]:
            params = {"period": "latest", "freq": "Q"}
            try:
                result = await self._call_finsight_api(f"calc/{ticker}/{metric_name}", params)
            except Exception as exc:
                return {metric_name: {"error": str(exc)}}

            if "error" in result:
                return {metric_name: {"error": result["error"]}}
            return {metric_name: result}

        tasks = [asyncio.create_task(_fetch_metric(metric)) for metric in metrics]
        results: Dict[str, Any] = {}

        for payload in await asyncio.gather(*tasks):
            results.update(payload)

        return results
    
    def execute_command(self, command: str) -> str:
        """Execute command and return output - improved with echo markers"""
        try:
            if self.shell_session is None:
                return "ERROR: Shell session not initialized"
            
            # Clean command - remove natural language prefixes
            command = command.strip()
            prefixes_to_remove = [
                'run this bash:', 'execute this:', 'run command:', 'execute:', 
                'run this:', 'run:', 'bash:', 'command:', 'this bash:', 'this:',
                'r code to', 'R code to', 'python code to', 'in r:', 'in R:',
                'in python:', 'in bash:', 'with r:', 'with bash:'
            ]
            for prefix in prefixes_to_remove:
                if command.lower().startswith(prefix.lower()):
                    command = command[len(prefix):].strip()
                    # Try again in case of nested prefixes
                    for prefix2 in prefixes_to_remove:
                        if command.lower().startswith(prefix2.lower()):
                            command = command[len(prefix2):].strip()
                            break
                    break
            
            # Use echo markers to detect when command is done
            import uuid
            marker = f"CMD_DONE_{uuid.uuid4().hex[:8]}"
            
            # Send command with marker
            full_command = f"{command}; echo '{marker}'\n"
            self.shell_session.stdin.write(full_command)
            self.shell_session.stdin.flush()
            
            # Read until we see the marker
            output_lines = []
            start_time = time.time()
            timeout = 30  # Increased for R scripts
            
            while time.time() - start_time < timeout:
                try:
                    line = self.shell_session.stdout.readline()
                    if not line:
                        break
                    
                    line = line.rstrip()
                    
                    # Check if we hit the marker
                    if marker in line:
                        break
                    
                    output_lines.append(line)
                except Exception:
                    break
            
            output = '\n'.join(output_lines).strip()
            return output if output else "Command executed (no output)"

        except Exception as e:
            return f"ERROR: {e}"

    # ========================================================================
    # DIRECT FILE OPERATIONS (Claude Code / Cursor Parity)
    # ========================================================================

    def read_file(self, file_path: str, offset: int = 0, limit: int = 2000) -> str:
        """
        Read file with line numbers (like Claude Code's Read tool)

        Args:
            file_path: Path to file
            offset: Starting line number (0-indexed)
            limit: Maximum number of lines to read

        Returns:
            File contents with line numbers in format: "  123→content"
        """
        try:
            # Expand ~ to home directory
            file_path = os.path.expanduser(file_path)

            # Make absolute if relative
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            # Apply offset and limit
            if offset or limit:
                lines = lines[offset:offset+limit if limit else None]

            # Format with line numbers (1-indexed, like vim/editors)
            numbered_lines = [
                f"{offset+i+1:6d}→{line.rstrip()}\n"
                for i, line in enumerate(lines)
            ]

            result = ''.join(numbered_lines)

            # Update file context
            self.file_context['last_file'] = file_path
            if file_path not in self.file_context['recent_files']:
                self.file_context['recent_files'].append(file_path)
                self.file_context['recent_files'] = self.file_context['recent_files'][-5:]

            return result if result else "(empty file)"

        except FileNotFoundError:
            return f"ERROR: File not found: {file_path}"
        except PermissionError:
            return f"ERROR: Permission denied: {file_path}"
        except IsADirectoryError:
            return f"ERROR: {file_path} is a directory, not a file"
        except Exception as e:
            return f"ERROR: {type(e).__name__}: {e}"

    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write file directly (like Claude Code's Write tool)
        Creates new file or overwrites existing one.

        Args:
            file_path: Path to file
            content: Full file content

        Returns:
            {"success": bool, "message": str, "bytes_written": int}
        """
        try:
            # Expand ~ to home directory
            file_path = os.path.expanduser(file_path)

            # Make absolute if relative
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            # Create parent directories if needed
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                bytes_written = f.write(content)

            # Update file context
            self.file_context['last_file'] = file_path
            if file_path not in self.file_context['recent_files']:
                self.file_context['recent_files'].append(file_path)
                self.file_context['recent_files'] = self.file_context['recent_files'][-5:]

            return {
                "success": True,
                "message": f"Wrote {bytes_written} bytes to {file_path}",
                "bytes_written": bytes_written
            }

        except PermissionError:
            return {
                "success": False,
                "message": f"ERROR: Permission denied: {file_path}",
                "bytes_written": 0
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"ERROR: {type(e).__name__}: {e}",
                "bytes_written": 0
            }

    def edit_file(self, file_path: str, old_string: str, new_string: str,
                  replace_all: bool = False) -> Dict[str, Any]:
        """
        Surgical file edit (like Claude Code's Edit tool)

        Args:
            file_path: Path to file
            old_string: Exact string to replace (must be unique unless replace_all=True)
            new_string: Replacement string
            replace_all: If True, replace all occurrences. If False, old_string must be unique.

        Returns:
            {"success": bool, "message": str, "replacements": int}
        """
        try:
            # Expand ~ to home directory
            file_path = os.path.expanduser(file_path)

            # Make absolute if relative
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)

            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Check if old_string exists
            if old_string not in content:
                return {
                    "success": False,
                    "message": f"ERROR: old_string not found in {file_path}",
                    "replacements": 0
                }

            # Check uniqueness if not replace_all
            occurrences = content.count(old_string)
            if not replace_all and occurrences > 1:
                return {
                    "success": False,
                    "message": f"ERROR: old_string appears {occurrences} times in {file_path}. Use replace_all=True or provide more context to make it unique.",
                    "replacements": 0
                }

            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
            else:
                new_content = content.replace(old_string, new_string, 1)

            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Update file context
            self.file_context['last_file'] = file_path

            return {
                "success": True,
                "message": f"Replaced {occurrences if replace_all else 1} occurrence(s) in {file_path}",
                "replacements": occurrences if replace_all else 1
            }

        except FileNotFoundError:
            return {
                "success": False,
                "message": f"ERROR: File not found: {file_path}",
                "replacements": 0
            }
        except PermissionError:
            return {
                "success": False,
                "message": f"ERROR: Permission denied: {file_path}",
                "replacements": 0
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"ERROR: {type(e).__name__}: {e}",
                "replacements": 0
            }

    def glob_search(self, pattern: str, path: str = ".") -> Dict[str, Any]:
        """
        Fast file pattern matching (like Claude Code's Glob tool)

        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.md", "src/**/*.ts")
            path: Starting directory (default: current directory)

        Returns:
            {"files": List[str], "count": int, "pattern": str}
        """
        try:
            import glob as glob_module

            # Expand ~ to home directory
            path = os.path.expanduser(path)

            # Make absolute if relative
            if not os.path.isabs(path):
                path = os.path.abspath(path)

            # Combine path and pattern
            full_pattern = os.path.join(path, pattern)

            # Find matches (recursive if ** in pattern)
            matches = glob_module.glob(full_pattern, recursive=True)

            # Filter to files only (not directories)
            files = [f for f in matches if os.path.isfile(f)]

            # Sort by modification time (newest first)
            files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

            return {
                "files": files,
                "count": len(files),
                "pattern": full_pattern
            }

        except Exception as e:
            return {
                "files": [],
                "count": 0,
                "pattern": pattern,
                "error": f"{type(e).__name__}: {e}"
            }

    def grep_search(self, pattern: str, path: str = ".",
                    file_pattern: str = "*",
                    output_mode: str = "files_with_matches",
                    context_lines: int = 0,
                    ignore_case: bool = False,
                    max_results: int = 100) -> Dict[str, Any]:
        """
        Fast content search (like Claude Code's Grep tool / ripgrep)

        Args:
            pattern: Regex pattern to search for
            path: Directory to search in
            file_pattern: Glob pattern for files to search (e.g., "*.py")
            output_mode: "files_with_matches", "content", or "count"
            context_lines: Lines of context around matches
            ignore_case: Case-insensitive search
            max_results: Maximum number of results to return

        Returns:
            Depends on output_mode:
            - files_with_matches: {"files": List[str], "count": int}
            - content: {"matches": {file: [(line_num, line_content), ...]}}
            - count: {"counts": {file: match_count}}
        """
        try:
            import re

            # Expand ~ to home directory
            path = os.path.expanduser(path)

            # Make absolute if relative
            if not os.path.isabs(path):
                path = os.path.abspath(path)

            # Compile regex
            flags = re.IGNORECASE if ignore_case else 0
            regex = re.compile(pattern, flags)

            # Find files to search
            glob_result = self.glob_search(file_pattern, path)
            files_to_search = glob_result["files"]

            # Search each file
            if output_mode == "files_with_matches":
                matching_files = []
                for file_path in files_to_search[:max_results]:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                        if regex.search(content):
                            matching_files.append(file_path)
                    except:
                        continue

                return {
                    "files": matching_files,
                    "count": len(matching_files),
                    "pattern": pattern
                }

            elif output_mode == "content":
                matches = {}
                for file_path in files_to_search:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            lines = f.readlines()

                        file_matches = []
                        for line_num, line in enumerate(lines, 1):
                            if regex.search(line):
                                file_matches.append((line_num, line.rstrip()))

                                if len(file_matches) >= max_results:
                                    break

                        if file_matches:
                            matches[file_path] = file_matches
                    except:
                        continue

                return {
                    "matches": matches,
                    "file_count": len(matches),
                    "pattern": pattern
                }

            elif output_mode == "count":
                counts = {}
                for file_path in files_to_search:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()

                        match_count = len(regex.findall(content))
                        if match_count > 0:
                            counts[file_path] = match_count
                    except:
                        continue

                return {
                    "counts": counts,
                    "total_matches": sum(counts.values()),
                    "pattern": pattern
                }

            else:
                return {
                    "error": f"Invalid output_mode: {output_mode}. Use 'files_with_matches', 'content', or 'count'."
                }

        except re.error as e:
            return {
                "error": f"Invalid regex pattern: {e}"
            }
        except Exception as e:
            return {
                "error": f"{type(e).__name__}: {e}"
            }

    async def batch_edit_files(self, edits: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Apply multiple file edits atomically (all-or-nothing)

        Args:
            edits: List of edit operations:
                [
                    {"file": "path.py", "old": "...", "new": "..."},
                    {"file": "other.py", "old": "...", "new": "...", "replace_all": True},
                    ...
                ]

        Returns:
            {
                "success": bool,
                "results": {file: {"success": bool, "message": str, "replacements": int}},
                "total_edits": int,
                "failed_edits": int
            }
        """
        try:
            results = {}

            # Phase 1: Validate all edits
            for edit in edits:
                file_path = edit["file"]
                old_string = edit["old"]
                replace_all = edit.get("replace_all", False)

                # Expand path
                file_path = os.path.expanduser(file_path)
                if not os.path.isabs(file_path):
                    file_path = os.path.abspath(file_path)

                # Check file exists
                if not os.path.exists(file_path):
                    return {
                        "success": False,
                        "results": {},
                        "total_edits": 0,
                        "failed_edits": len(edits),
                        "error": f"Validation failed: {file_path} not found. No edits applied."
                    }

                # Check old_string exists
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()

                    if old_string not in content:
                        return {
                            "success": False,
                            "results": {},
                            "total_edits": 0,
                            "failed_edits": len(edits),
                            "error": f"Validation failed: Pattern not found in {file_path}. No edits applied."
                        }

                    # Check uniqueness if not replace_all
                    if not replace_all and content.count(old_string) > 1:
                        return {
                            "success": False,
                            "results": {},
                            "total_edits": 0,
                            "failed_edits": len(edits),
                            "error": f"Validation failed: Pattern appears {content.count(old_string)} times in {file_path}. Use replace_all or provide more context. No edits applied."
                        }
                except Exception as e:
                    return {
                        "success": False,
                        "results": {},
                        "total_edits": 0,
                        "failed_edits": len(edits),
                        "error": f"Validation failed reading {file_path}: {e}. No edits applied."
                    }

            # Phase 2: Apply all edits (validation passed)
            for edit in edits:
                file_path = edit["file"]
                old_string = edit["old"]
                new_string = edit["new"]
                replace_all = edit.get("replace_all", False)

                result = self.edit_file(file_path, old_string, new_string, replace_all)
                results[file_path] = result

            # Count successes/failures
            successful_edits = sum(1 for r in results.values() if r["success"])
            failed_edits = len(edits) - successful_edits

            return {
                "success": failed_edits == 0,
                "results": results,
                "total_edits": len(edits),
                "successful_edits": successful_edits,
                "failed_edits": failed_edits
            }

        except Exception as e:
            return {
                "success": False,
                "results": {},
                "total_edits": 0,
                "failed_edits": len(edits),
                "error": f"Batch edit failed: {type(e).__name__}: {e}"
            }

    # ========================================================================
    # END DIRECT FILE OPERATIONS
    # ========================================================================

    def _classify_command_safety(self, cmd: str) -> str:
        """
        Classify command by safety level for smart execution.
        Returns: 'SAFE', 'WRITE', 'DANGEROUS', or 'BLOCKED'
        """
        cmd = cmd.strip()
        if not cmd:
            return 'BLOCKED'
        
        cmd_lower = cmd.lower()
        cmd_parts = cmd.split()
        cmd_base = cmd_parts[0] if cmd_parts else ''
        cmd_with_sub = ' '.join(cmd_parts[:2]) if len(cmd_parts) >= 2 else ''
        
        # BLOCKED: Catastrophic commands
        nuclear_patterns = [
            'rm -rf /',
            'rm -rf ~',
            'rm -rf /*',
            'dd if=/dev/zero',
            'mkfs',
            'fdisk',
            ':(){ :|:& };:',  # Fork bomb
            'chmod -r 777 /',
            '> /dev/sda',
        ]
        for pattern in nuclear_patterns:
            if pattern in cmd_lower:
                return 'BLOCKED'
        
        # SAFE: Read-only commands
        safe_commands = {
            'pwd', 'ls', 'cd', 'cat', 'head', 'tail', 'grep', 'find', 'which', 'type',
            'wc', 'diff', 'echo', 'ps', 'top', 'df', 'du', 'file', 'stat', 'tree',
            'whoami', 'hostname', 'date', 'cal', 'uptime', 'printenv', 'env',
        }
        safe_git = {'git status', 'git log', 'git diff', 'git branch', 'git show', 'git remote'}
        
        if cmd_base in safe_commands or cmd_with_sub in safe_git:
            return 'SAFE'
        
        # WRITE: File creation/modification (allowed but tracked)
        write_commands = {'mkdir', 'touch', 'cp', 'mv', 'tee'}
        if cmd_base in write_commands:
            return 'WRITE'
        
        # WRITE: Redirection operations (echo > file, cat > file)
        if '>' in cmd or '>>' in cmd:
            # Allow redirection to regular files, block to devices
            if '/dev/' not in cmd_lower:
                return 'WRITE'
            else:
                return 'BLOCKED'
        
        # DANGEROUS: Deletion and permission changes
        dangerous_commands = {'rm', 'rmdir', 'chmod', 'chown', 'chgrp'}
        if cmd_base in dangerous_commands:
            return 'DANGEROUS'
        
        # WRITE: Git write operations
        write_git = {'git add', 'git commit', 'git push', 'git pull', 'git checkout', 'git merge'}
        if cmd_with_sub in write_git:
            return 'WRITE'
        
        # Default: Treat unknown commands as requiring user awareness
        return 'WRITE'
    
    def _is_safe_shell_command(self, cmd: str) -> bool:
        """
        Compatibility wrapper for old safety check.
        Now uses tiered classification system.
        """
        classification = self._classify_command_safety(cmd)
        return classification in ['SAFE', 'WRITE']  # Allow SAFE and WRITE, block DANGEROUS and BLOCKED
    
    def _check_token_budget(self, estimated_tokens: int) -> bool:
        """Check if we have enough token budget"""
        self._ensure_usage_day()
        return (self.daily_token_usage + estimated_tokens) < self.daily_limit

    def _check_user_token_budget(self, user_id: str, estimated_tokens: int) -> bool:
        self._ensure_usage_day()
        current = self.user_token_usage.get(user_id, 0)
        return (current + estimated_tokens) < self.per_user_token_limit

    def _resolve_daily_query_limit(self) -> int:
        limit_env = os.getenv("NOCTURNAL_QUERY_LIMIT")
        if limit_env and limit_env != str(DEFAULT_QUERY_LIMIT):
            logger.warning("Ignoring attempted query-limit override (%s); enforcing default %s", limit_env, DEFAULT_QUERY_LIMIT)
        os.environ["NOCTURNAL_QUERY_LIMIT"] = str(DEFAULT_QUERY_LIMIT)
        os.environ.pop("NOCTURNAL_QUERY_LIMIT_SIG", None)
        return DEFAULT_QUERY_LIMIT

    def _check_query_budget(self, user_id: Optional[str]) -> bool:
        self._ensure_usage_day()
        if self.daily_query_limit > 0 and self.daily_query_count >= self.daily_query_limit:
            return False

        effective_limit = self.per_user_query_limit if self.per_user_query_limit > 0 else self.daily_query_limit
        if user_id and effective_limit > 0 and self.user_query_counts.get(user_id, 0) >= effective_limit:
            return False

        return True

    def _record_query_usage(self, user_id: Optional[str]):
        self._ensure_usage_day()
        self.daily_query_count += 1
        if user_id:
            self.user_query_counts[user_id] = self.user_query_counts.get(user_id, 0) + 1

    def _ensure_usage_day(self):
        current_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if current_day != self._usage_day:
            self._usage_day = current_day
            self.daily_token_usage = 0
            self.user_token_usage = {}
            self.daily_query_count = 0
            self.user_query_counts = {}

    def _charge_tokens(self, user_id: Optional[str], tokens: int):
        """Charge tokens to daily and per-user usage"""
        self._ensure_usage_day()
        self.daily_token_usage += tokens
        if user_id:
            self.user_token_usage[user_id] = self.user_token_usage.get(user_id, 0) + tokens
    
    def _get_memory_context(self, user_id: str, conversation_id: str) -> str:
        """Get relevant memory context for the conversation"""
        if user_id not in self.memory:
            self.memory[user_id] = {}
        
        if conversation_id not in self.memory[user_id]:
            self.memory[user_id][conversation_id] = []
        
        # Get last 3 interactions for context
        recent_memory = self.memory[user_id][conversation_id][-3:]
        if not recent_memory:
            return ""
        
        context = "Recent conversation context:\n"
        for mem in recent_memory:
            context += f"- {mem}\n"
        return context
    
    def _update_memory(self, user_id: str, conversation_id: str, interaction: str):
        """Update memory with new interaction"""
        if user_id not in self.memory:
            self.memory[user_id] = {}
        
        if conversation_id not in self.memory[user_id]:
            self.memory[user_id][conversation_id] = []
        
        self.memory[user_id][conversation_id].append(interaction)
        
        # Keep only last 10 interactions
        if len(self.memory[user_id][conversation_id]) > 10:
            self.memory[user_id][conversation_id] = self.memory[user_id][conversation_id][-10:]

    @staticmethod
    def _hash_identifier(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return digest[:16]

    def _emit_telemetry(
        self,
        event: str,
        request: Optional[ChatRequest] = None,
        *,
        success: Optional[bool] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        manager = TelemetryManager.get()
        if not manager:
            return

        payload: Dict[str, Any] = {}
        if request:
            payload["user"] = self._hash_identifier(request.user_id)
            payload["conversation"] = self._hash_identifier(request.conversation_id)
        if success is not None:
            payload["success"] = bool(success)
        if extra:
            for key, value in extra.items():
                if value is None:
                    continue
                payload[key] = value

        manager.record(event, payload)

    @staticmethod
    def _format_model_error(details: str) -> str:
        headline = "⚠️ I couldn't finish the reasoning step because the language model call failed."
        advice = "Please retry shortly or verify your Groq API keys and network connectivity."
        if details:
            return f"{headline}\n\nDetails: {details}\n\n{advice}"
        return f"{headline}\n\n{advice}"

    def _summarize_command_output(
        self,
        request: ChatRequest,
        command: str,
        truncated_output: str,
        base_response: str
    ) -> Tuple[str, int]:
        """Attach a deterministic shell output block to the agent response."""

        rendered_output = truncated_output.rstrip()
        if not rendered_output:
            rendered_output = "(no output)"

        formatted = (
            f"{base_response.strip()}\n\n"
            "```shell\n"
            f"$ {command}\n"
            f"{rendered_output}\n"
            "```"
        )

        return formatted, 0
    
    async def _handle_workflow_commands(self, request: ChatRequest) -> Optional[ChatResponse]:
        """Handle natural language workflow commands directly"""
        question_lower = request.question.lower()
        
        # Show library
        if any(phrase in question_lower for phrase in ["show my library", "list my papers", "what's in my library", "my saved papers"]):
            papers = self.workflow.list_papers()
            if not papers:
                message = "Your library is empty. As you find papers, I can save them for you."
            else:
                paper_list = []
                for i, paper in enumerate(papers[:10], 1):
                    authors_str = paper.authors[0] if paper.authors else "Unknown"
                    if len(paper.authors) > 1:
                        authors_str += " et al."
                    paper_list.append(f"{i}. {paper.title} ({authors_str}, {paper.year})")
                
                message = f"You have {len(papers)} paper(s) in your library:\n\n" + "\n".join(paper_list)
                if len(papers) > 10:
                    message += f"\n\n...and {len(papers) - 10} more."
            
            return self._quick_reply(request, message, tools_used=["workflow_library"], confidence=1.0)
        
        # Export to BibTeX
        if any(phrase in question_lower for phrase in ["export to bibtex", "export bibtex", "generate bibtex", "bibtex export"]):
            success = self.workflow.export_to_bibtex()
            if success:
                message = f"✅ Exported {len(self.workflow.list_papers())} papers to BibTeX.\n\nFile: {self.workflow.bibtex_file}\n\nYou can import this into Zotero, Mendeley, or use it in your LaTeX project."
            else:
                message = "❌ Failed to export BibTeX. Make sure you have papers in your library first."
            
            return self._quick_reply(request, message, tools_used=["workflow_export"], confidence=1.0)
        
        # Export to Markdown
        if any(phrase in question_lower for phrase in ["export to markdown", "export markdown", "markdown export"]):
            success = self.workflow.export_to_markdown()
            if success:
                message = f"✅ Exported to Markdown. Check {self.workflow.exports_dir} for the file.\n\nYou can open it in Obsidian, Notion, or any markdown editor."
            else:
                message = "❌ Failed to export Markdown."
            
            return self._quick_reply(request, message, tools_used=["workflow_export"], confidence=1.0)
        
        # Show history
        if any(phrase in question_lower for phrase in ["show history", "my history", "recent queries", "what did i search"]):
            history = self.workflow.get_history()[:10]
            if not history:
                message = "No query history yet."
            else:
                history_list = []
                for i, entry in enumerate(history, 1):
                    timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%m/%d %H:%M")
                    query = entry['query'][:60] + "..." if len(entry['query']) > 60 else entry['query']
                    history_list.append(f"{i}. [{timestamp}] {query}")
                
                message = "Recent queries:\n\n" + "\n".join(history_list)
            
            return self._quick_reply(request, message, tools_used=["workflow_history"], confidence=1.0)
        
        # Search library
        search_match = re.match(r".*(?:search|find).*(?:in|my).*library.*[\"'](.+?)[\"']", question_lower)
        if not search_match:
            search_match = re.match(r".*search library (?:for )?(.+)", question_lower)
        
        if search_match:
            query_term = search_match.group(1).strip()
            results = self.workflow.search_library(query_term)
            if not results:
                message = f"No papers found matching '{query_term}' in your library."
            else:
                result_list = []
                for i, paper in enumerate(results[:5], 1):
                    authors_str = paper.authors[0] if paper.authors else "Unknown"
                    if len(paper.authors) > 1:
                        authors_str += " et al."
                    result_list.append(f"{i}. {paper.title} ({authors_str}, {paper.year})")
                
                message = f"Found {len(results)} paper(s) matching '{query_term}':\n\n" + "\n".join(result_list)
                if len(results) > 5:
                    message += f"\n\n...and {len(results) - 5} more."
            
            return self._quick_reply(request, message, tools_used=["workflow_search"], confidence=1.0)
        
        # No workflow command detected
        return None

    async def _analyze_request_type(self, question: str) -> Dict[str, Any]:
        """Analyze what type of request this is and what APIs to use"""
        
        # Financial indicators - COMPREHENSIVE list to ensure FinSight is used
        financial_keywords = [
            # Core metrics
            'financial', 'revenue', 'sales', 'income', 'profit', 'earnings', 'loss',
            'net income', 'operating income', 'gross profit', 'ebitda', 'ebit',
            
            # Margins & Ratios
            'margin', 'gross margin', 'profit margin', 'operating margin', 'net margin', 'ebitda margin',
            'ratio', 'current ratio', 'quick ratio', 'debt ratio', 'pe ratio', 'p/e',
            'roe', 'roa', 'roic', 'roce', 'eps',
            
            # Balance Sheet
            'assets', 'liabilities', 'equity', 'debt', 'cash', 'capital',
            'balance sheet', 'total assets', 'current assets', 'fixed assets',
            'shareholders equity', 'stockholders equity', 'retained earnings',
            
            # Cash Flow
            'cash flow', 'fcf', 'free cash flow', 'operating cash flow',
            'cfo', 'cfi', 'cff', 'capex', 'capital expenditure',
            
            # Market Metrics
            'stock', 'market cap', 'market capitalization', 'enterprise value',
            'valuation', 'price', 'share price', 'stock price', 'quote',
            'volume', 'trading volume', 'shares outstanding',
            
            # Financial Statements
            'income statement', '10-k', '10-q', '8-k', 'filing', 'sec filing',
            'quarterly', 'annual report', 'earnings report', 'financial statement',
            
            # Company Info
            'ticker', 'company', 'corporation', 'ceo', 'earnings call',
            'dividend', 'dividend yield', 'payout ratio',
            
            # Growth & Performance
            'growth', 'yoy', 'year over year', 'qoq', 'quarter over quarter',
            'cagr', 'trend', 'performance', 'returns'
        ]
        
        # Research indicators (quantitative)
        research_keywords = [
            'research', 'paper', 'study', 'academic', 'literature', 'journal',
            'synthesis', 'findings', 'methodology', 'abstract', 'citation',
            'author', 'publication', 'peer review', 'scientific'
        ]
        
        # Qualitative indicators (NEW)
        qualitative_keywords = [
            'theme', 'themes', 'thematic', 'code', 'coding', 'qualitative',
            'interview', 'interviews', 'transcript', 'case study', 'narrative',
            'discourse', 'content analysis', 'quote', 'quotes', 'excerpt',
            'participant', 'respondent', 'informant', 'ethnography',
            'grounded theory', 'phenomenology', 'what do people say',
            'how do participants', 'sentiment', 'perception', 'experience',
            'lived experience', 'meaning', 'interpret', 'understand',
            'focus group', 'observation', 'field notes', 'memoir', 'diary'
        ]
        
        # Quantitative indicators (explicit stats/math)
        quantitative_keywords = [
            'calculate', 'average', 'mean', 'median', 'percentage', 'correlation',
            'regression', 'statistical', 'significance', 'p-value', 'variance',
            'standard deviation', 'trend', 'forecast', 'model', 'predict',
            'rate of', 'ratio', 'growth rate', 'change in', 'compared to'
        ]
        
        # System/technical indicators
        system_keywords = [
            'file', 'directory', 'command', 'run', 'execute', 'install',
            'python', 'code', 'script', 'program', 'system', 'terminal'
        ]
        
        question_lower = question.lower()
        
        matched_types: List[str] = []
        apis_to_use: List[str] = []
        analysis_mode = "quantitative"  # default
        
        # Context-aware keyword detection
        # Strong quant contexts that override everything
        strong_quant_contexts = [
            'algorithm', 'park', 'system', 'database',
            'calculate', 'predict', 'forecast', 'ratio', 'percentage'
        ]
        
        # Measurement words (can indicate mixed when combined with qual words)
        measurement_words = ['score', 'metric', 'rating', 'measure', 'index']
        
        has_strong_quant_context = any(ctx in question_lower for ctx in strong_quant_contexts)
        has_measurement = any(mw in question_lower for mw in measurement_words)
        
        # Special cases: Certain qual words + measurement = mixed (subjective + quantified)
        # BUT: Only if NOT in a strong quant context (algorithm overrides)
        mixed_indicators = [
            'experience',  # user experience
            'sentiment',   # sentiment analysis
            'perception',  # perception
        ]
        
        is_mixed_method = False
        if not has_strong_quant_context and has_measurement:
            if any(indicator in question_lower for indicator in mixed_indicators):
                is_mixed_method = True
        
        # Check for qualitative vs quantitative keywords
        qual_score = sum(1 for kw in qualitative_keywords if kw in question_lower)
        quant_score = sum(1 for kw in quantitative_keywords if kw in question_lower)
        
        # Financial queries are quantitative by nature (unless explicitly qualitative like "interview")
        has_financial = any(kw in question_lower for kw in financial_keywords)
        if has_financial and qual_score == 1:
            # Single qual keyword + financial = probably mixed
            # e.g., "Interview CEO about earnings" = interview (qual) + earnings/CEO (financial)
            quant_score += 1
        
        # Adjust for context
        if has_strong_quant_context:
            # Reduce qualitative score if in strong quantitative context
            # e.g., "theme park" or "sentiment analysis algorithm"
            qual_score = max(0, qual_score - 1)
        
        # Improved mixed detection: use ratio instead of simple comparison
        if is_mixed_method:
            # Special case: qual word + measurement = always mixed
            analysis_mode = "mixed"
        elif qual_score >= 2 and quant_score >= 1:
            # Clear mixed: multiple qual + some quant
            analysis_mode = "mixed"
        elif qual_score > quant_score and qual_score > 0:
            # Predominantly qualitative
            analysis_mode = "qualitative"
        elif qual_score > 0 and quant_score > 0:
            # Some of both - default to mixed
            analysis_mode = "mixed"

        if any(keyword in question_lower for keyword in financial_keywords):
            matched_types.append("financial")
            apis_to_use.append("finsight")

        if any(keyword in question_lower for keyword in research_keywords):
            matched_types.append("research")
            apis_to_use.append("archive")
        
        # Qualitative queries often involve research
        if analysis_mode in ("qualitative", "mixed") and "research" not in matched_types:
            matched_types.append("research")
            if "archive" not in apis_to_use:
                apis_to_use.append("archive")

        if any(keyword in question_lower for keyword in system_keywords):
            matched_types.append("system")
            apis_to_use.append("shell")

        # Deduplicate while preserving order
        apis_to_use = list(dict.fromkeys(apis_to_use))
        unique_types = list(dict.fromkeys(matched_types))

        if not unique_types:
            request_type = "general"
        elif len(unique_types) == 1:
            request_type = unique_types[0]
        elif {"financial", "research"}.issubset(set(unique_types)):
            request_type = "comprehensive"
            if "system" in unique_types:
                request_type += "+system"
        else:
            request_type = "+".join(unique_types)

        confidence = 0.8 if apis_to_use else 0.5
        if len(unique_types) > 1:
            confidence = 0.85

        return {
            "type": request_type,
            "apis": apis_to_use,
            "confidence": confidence,
            "analysis_mode": analysis_mode  # NEW: qualitative, quantitative, or mixed
        }
    
    def _is_query_too_vague_for_apis(self, question: str) -> bool:
        """
        Detect if query is too vague to warrant API calls
        Returns True if we should skip APIs and just ask clarifying questions
        """
        question_lower = question.lower()
        
        # Pattern 1: Multiple years without SPECIFIC topic (e.g., "2008, 2015, 2019")
        import re
        years_pattern = r'\b(19\d{2}|20\d{2})\b'
        years = re.findall(years_pattern, question)
        if len(years) >= 2:
            # Multiple years - check if there's a SPECIFIC topic beyond just "papers on"
            # Generic terms that don't add specificity
            generic_terms = ['papers', 'about', 'on', 'regarding', 'concerning', 'related to']
            # Remove generic terms and check what's left
            words = question_lower.split()
            content_words = [w for w in words if w not in generic_terms and not re.match(r'\d{4}', w)]
            # If fewer than 2 meaningful content words, it's too vague
            if len(content_words) < 2:
                return True  # Too vague: "papers on 2008, 2015, 2019" needs topic
        
        # Pattern 2: Market share without market specified
        if 'market share' in question_lower:
            market_indicators = ['analytics', 'software', 'government', 'data', 'cloud', 'sector', 'industry']
            if not any(indicator in question_lower for indicator in market_indicators):
                return True  # Too vague: needs market specification
        
        # Pattern 3: Comparison without metric (compare X and Y)
        if any(word in question_lower for word in ['compare', 'versus', 'vs', 'vs.']):
            metric_indicators = ['revenue', 'market cap', 'sales', 'growth', 'profit', 'valuation']
            if not any(indicator in question_lower for indicator in metric_indicators):
                return True  # Too vague: needs metric specification
        
        # Pattern 4: Ultra-short queries without specifics (< 4 words)
        word_count = len(question.split())
        if word_count <= 3 and '?' in question:
            return True  # Too short and questioning - likely needs clarification
        
        return False  # Query seems specific enough for API calls
    
    async def process_request(self, request: ChatRequest) -> ChatResponse:
        """Process request with full AI capabilities and API integration"""
        try:
            # Check workflow commands first (both modes)
            workflow_response = await self._handle_workflow_commands(request)
            if workflow_response:
                return workflow_response
            
            # Initialize
            api_results = {}
            tools_used = []
            debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"
            
            # ========================================================================
            # PRIORITY 1: SHELL PLANNING (Reasoning Layer - Runs FIRST for ALL modes)
            # ========================================================================
            # This determines USER INTENT before fetching any data
            # Prevents waste: "find cm522" won't trigger Archive API, "look into it" won't web search
            # Works in BOTH production and dev modes
            
            shell_action = "none"  # Will be: pwd|ls|find|none
            
            # Quick check if query might need shell
            question_lower = request.question.lower()
            might_need_shell = any(word in question_lower for word in [
                'directory', 'folder', 'where', 'find', 'list', 'files', 'file', 'look', 'search', 'check', 'into',
                'show', 'open', 'read', 'display', 'cat', 'view', 'contents', '.r', '.py', '.csv', '.ipynb',
                'create', 'make', 'mkdir', 'touch', 'new', 'write', 'copy', 'move', 'delete', 'remove',
                'git', 'grep', 'navigate', 'go to', 'change to'
            ])
            
            if might_need_shell and self.shell_session:
                # Get current directory and context for intelligent planning
                try:
                    current_dir = self.execute_command("pwd").strip()
                    self.file_context['current_cwd'] = current_dir
                except:
                    current_dir = "~"
                
                last_file = self.file_context.get('last_file') or 'None'
                last_dir = self.file_context.get('last_directory') or 'None'
                
                # Ask LLM planner: What shell command should we run?
                planner_prompt = f"""You are a shell command planner. Determine what shell command to run, if any.

User query: "{request.question}"
Previous conversation: {json.dumps(self.conversation_history[-2:]) if self.conversation_history else "None"}
Current directory: {current_dir}
Last file mentioned: {last_file}
Last directory mentioned: {last_dir}

Respond ONLY with JSON:
{{
  "action": "execute|none",
  "command": "pwd" (the actual shell command to run, if action=execute),
  "reason": "Show current directory" (why this command is needed),
  "updates_context": true (set to true if command changes files/directories)
}}

IMPORTANT RULES:
1. Return "none" for conversational queries ("hello", "test", "thanks", "how are you")
2. Return "none" when query is ambiguous without more context
3. Return "none" for questions about data that don't need shell (e.g., "Tesla revenue", "Apple stock price")
4. Use ACTUAL shell commands (pwd, ls, cd, mkdir, cat, grep, find, touch, etc.)
5. Resolve pronouns using context: "it"={last_file}, "there"/{last_dir}
6. For reading files, prefer: head -100 filename (shows first 100 lines)
7. For finding things, use: find ~ -maxdepth 4 -name '*pattern*' 2>/dev/null
8. For creating files: touch filename OR echo "content" > filename
9. For creating directories: mkdir dirname
10. ALWAYS include 2>/dev/null to suppress errors from find
11. 🚨 MULTI-STEP QUERIES: For queries like "read X and do Y", ONLY generate the FIRST step (reading X). The LLM will handle subsequent steps after seeing the file contents.
12. 🚨 NEVER use python -m py_compile or other code execution for finding bugs - just read the file with cat/head

Examples:
"where am i?" → {{"action": "execute", "command": "pwd", "reason": "Show current directory", "updates_context": false}}
"list files" → {{"action": "execute", "command": "ls -lah", "reason": "List all files with details", "updates_context": false}}
"find cm522" → {{"action": "execute", "command": "find ~ -maxdepth 4 -name '*cm522*' -type d 2>/dev/null | head -20", "reason": "Search for cm522 directory", "updates_context": false}}
"go to Downloads" → {{"action": "execute", "command": "cd ~/Downloads && pwd", "reason": "Navigate to Downloads directory", "updates_context": true}}
"show me calc.R" → {{"action": "execute", "command": "head -100 calc.R", "reason": "Display file contents", "updates_context": true}}
"create test directory" → {{"action": "execute", "command": "mkdir test && echo 'Created test/'", "reason": "Create new directory", "updates_context": true}}
"create empty config.json" → {{"action": "execute", "command": "touch config.json && echo 'Created config.json'", "reason": "Create empty file", "updates_context": true}}
"write hello.txt with content Hello World" → {{"action": "execute", "command": "echo 'Hello World' > hello.txt", "reason": "Create file with content", "updates_context": true}}
"create results.txt with line 1 and line 2" → {{"action": "execute", "command": "echo 'line 1' > results.txt && echo 'line 2' >> results.txt", "reason": "Create file with multiple lines", "updates_context": true}}
"fix bug in script.py change OLD to NEW" → {{"action": "execute", "command": "sed -i 's/OLD/NEW/g' script.py && echo 'Fixed script.py'", "reason": "Edit file to fix bug", "updates_context": true}}
"search for TODO in py files" → {{"action": "execute", "command": "grep -n 'TODO' *.py 2>/dev/null", "reason": "Find TODO comments", "updates_context": false}}
"find all bugs in code" → {{"action": "execute", "command": "grep -rn 'BUG:' . 2>/dev/null", "reason": "Search for bug markers in code", "updates_context": false}}
"read analyze.py and find bugs" → {{"action": "execute", "command": "head -200 analyze.py", "reason": "Read file to analyze bugs", "updates_context": false}}
"show me calc.py completely" → {{"action": "execute", "command": "cat calc.py", "reason": "Display entire file", "updates_context": false}}
"git status" → {{"action": "execute", "command": "git status", "reason": "Check repository status", "updates_context": false}}
"what's in that file?" + last_file=data.csv → {{"action": "execute", "command": "head -100 data.csv", "reason": "Show file contents", "updates_context": false}}
"hello" → {{"action": "none", "reason": "Conversational greeting, no command needed"}}
"test" → {{"action": "none", "reason": "Ambiguous query, needs clarification"}}
"thanks" → {{"action": "none", "reason": "Conversational acknowledgment"}}
"Tesla revenue" → {{"action": "none", "reason": "Finance query, will use FinSight API not shell"}}
"what does the error mean?" → {{"action": "none", "reason": "Explanation request, no command needed"}}

JSON:"""

                try:
                    plan_response = await self.call_backend_query(
                        query=planner_prompt,
                        conversation_history=[],
                        api_results={},
                        tools_used=[]
                    )
                    
                    plan_text = plan_response.response.strip()
                    if '```' in plan_text:
                        plan_text = plan_text.split('```')[1].replace('json', '').strip()
                    
                    plan = json.loads(plan_text)
                    shell_action = plan.get("action", "none")
                    command = plan.get("command", "")
                    reason = plan.get("reason", "")
                    updates_context = plan.get("updates_context", False)
                    
                    if debug_mode:
                        print(f"🔍 SHELL PLAN: {plan}")
                    
                    # GENERIC COMMAND EXECUTION - No more hardcoded actions!
                    if shell_action == "execute" and command:
                        # Check command safety
                        safety_level = self._classify_command_safety(command)
                        
                        if debug_mode:
                            print(f"🔍 Command: {command}")
                            print(f"🔍 Safety: {safety_level}")
                        
                        if safety_level == 'BLOCKED':
                            api_results["shell_info"] = {
                                "error": f"Command blocked for safety: {command}",
                                "reason": "This command could cause system damage"
                            }
                        else:
                            # ========================================
                            # COMMAND INTERCEPTOR: Translate shell commands to file operations
                            # (Claude Code / Cursor parity)
                            # ========================================
                            intercepted = False
                            output = ""

                            # Check for file reading commands (cat, head, tail)
                            if command.startswith(('cat ', 'head ', 'tail ')):
                                import shlex
                                try:
                                    parts = shlex.split(command)
                                    cmd = parts[0]

                                    # Extract filename (last non-flag argument)
                                    filename = None
                                    for part in reversed(parts[1:]):
                                        if not part.startswith('-'):
                                            filename = part
                                            break

                                    if filename:
                                        # Use read_file instead of cat/head/tail
                                        if cmd == 'head':
                                            # head -n 100 file OR head file
                                            limit = 100  # default
                                            if '-n' in parts or '-' in parts[0]:
                                                try:
                                                    idx = parts.index('-n') if '-n' in parts else 0
                                                    limit = int(parts[idx + 1])
                                                except:
                                                    pass
                                            output = self.read_file(filename, offset=0, limit=limit)
                                        elif cmd == 'tail':
                                            # For tail, read last N lines (harder, so just read all and show it's tail)
                                            output = self.read_file(filename)
                                            if "ERROR" not in output:
                                                lines = output.split('\n')
                                                output = '\n'.join(lines[-100:])  # last 100 lines
                                        else:  # cat
                                            output = self.read_file(filename)

                                        intercepted = True
                                        tools_used.append("read_file")
                                        if debug_mode:
                                            print(f"🔄 Intercepted: {command} → read_file({filename})")
                                except:
                                    pass  # Fall back to shell execution

                            # Check for file search commands (find)
                            if not intercepted and 'find' in command and '-name' in command:
                                try:
                                    import re
                                    # Extract pattern: find ... -name '*pattern*'
                                    name_match = re.search(r"-name\s+['\"]?\*?([^'\"*\s]+)\*?['\"]?", command)
                                    if name_match:
                                        pattern = f"**/*{name_match.group(1)}*"
                                        path_match = re.search(r"find\s+([^\s]+)", command)
                                        search_path = path_match.group(1) if path_match else "."

                                        result = self.glob_search(pattern, search_path)
                                        output = '\n'.join(result['files'][:20])  # Show first 20 matches
                                        intercepted = True
                                        tools_used.append("glob_search")
                                        if debug_mode:
                                            print(f"🔄 Intercepted: {command} → glob_search({pattern}, {search_path})")
                                except:
                                    pass

                            # Check for file writing commands (echo > file, grep > file, etc.) - CHECK THIS FIRST!
                            # This must come BEFORE the plain grep interceptor
                            if not intercepted and ('>' in command or '>>' in command):
                                try:
                                    import re

                                    # Handle grep ... > file (intercept and execute grep, then write output)
                                    if 'grep' in command and '>' in command:
                                        # Extract: grep -rn 'pattern' path > output.txt
                                        grep_match = re.search(r"grep\s+(.*)>\s*(\S+)", command)
                                        if grep_match:
                                            grep_part = grep_match.group(1).strip()
                                            output_file = grep_match.group(2)

                                            # Extract pattern and options from grep command
                                            pattern_match = re.search(r"['\"]([^'\"]+)['\"]", grep_part)
                                            if pattern_match:
                                                pattern = pattern_match.group(1)
                                                search_path = "."
                                                file_pattern = "*.py" if "*.py" in command else "*"

                                                if debug_mode:
                                                    print(f"🔄 Intercepted: {command} → grep_search('{pattern}', '{search_path}', '{file_pattern}') + write_file({output_file})")

                                                # Execute grep_search
                                                try:
                                                    grep_result = self.grep_search(
                                                        pattern=pattern,
                                                        path=search_path,
                                                        file_pattern=file_pattern,
                                                        output_mode="content"
                                                    )

                                                    # Format matches as text (like grep -rn output)
                                                    output_lines = []
                                                    for file_path, matches in grep_result.get('matches', {}).items():
                                                        for line_num, line_content in matches:
                                                            output_lines.append(f"{file_path}:{line_num}:{line_content}")

                                                    content_to_write = '\n'.join(output_lines) if output_lines else "(no matches found)"

                                                    # Write grep output to file
                                                    write_result = self.write_file(output_file, content_to_write)
                                                    if write_result['success']:
                                                        output = f"Found {len(output_lines)} lines with '{pattern}' → Created {output_file} ({write_result['bytes_written']} bytes)"
                                                        intercepted = True
                                                        tools_used.extend(["grep_search", "write_file"])
                                                except Exception as e:
                                                    if debug_mode:
                                                        print(f"⚠️ Grep > file interception error: {e}")
                                                    # Fall back to normal execution
                                                    pass

                                    # Extract: echo 'content' > filename OR cat << EOF > filename
                                    if not intercepted and 'echo' in command and '>' in command:
                                        # echo 'content' > file OR echo "content" > file
                                        match = re.search(r"echo\s+['\"](.+?)['\"].*?>\s*(\S+)", command)
                                        if match:
                                            content = match.group(1)
                                            filename = match.group(2)
                                            # Unescape common sequences
                                            content = content.replace('\\n', '\n').replace('\\t', '\t')
                                            result = self.write_file(filename, content + '\n')
                                            if result['success']:
                                                output = f"Created {filename} ({result['bytes_written']} bytes)"
                                                intercepted = True
                                                tools_used.append("write_file")
                                                if debug_mode:
                                                    print(f"🔄 Intercepted: {command} → write_file({filename}, ...)")
                                except:
                                    pass

                            # Check for sed editing commands
                            if not intercepted and command.startswith('sed '):
                                try:
                                    import re
                                    # sed 's/old/new/g' file OR sed -i 's/old/new/' file
                                    match = re.search(r"sed.*?['\"]s/([^/]+)/([^/]+)/", command)
                                    if match:
                                        old_text = match.group(1)
                                        new_text = match.group(2)
                                        # Extract filename (last argument)
                                        parts = command.split()
                                        filename = parts[-1]

                                        # Determine if replace_all based on /g flag
                                        replace_all = '/g' in command

                                        result = self.edit_file(filename, old_text, new_text, replace_all=replace_all)
                                        if result['success']:
                                            output = result['message']
                                            intercepted = True
                                            tools_used.append("edit_file")
                                            if debug_mode:
                                                print(f"🔄 Intercepted: {command} → edit_file({filename}, {old_text}, {new_text})")
                                except:
                                    pass

                            # Check for heredoc file creation (cat << EOF > file)
                            if not intercepted and '<<' in command and ('EOF' in command or 'HEREDOC' in command):
                                try:
                                    import re
                                    # Extract: cat << EOF > filename OR cat > filename << EOF
                                    # Note: We can't actually get the heredoc content from a single command line
                                    # This would need to be handled differently (multi-line input)
                                    # For now, just detect and warn
                                    if debug_mode:
                                        print(f"⚠️  Heredoc detected but not intercepted: {command[:80]}")
                                except:
                                    pass

                            # Check for content search commands (grep -r) WITHOUT redirection
                            # This comes AFTER grep > file interceptor to avoid conflicts
                            if not intercepted and command.startswith('grep ') and ('-r' in command or '-R' in command):
                                try:
                                    import re
                                    # Extract pattern: grep -r 'pattern' path
                                    pattern_match = re.search(r"grep.*?['\"]([^'\"]+)['\"]", command)
                                    if pattern_match:
                                        pattern = pattern_match.group(1)
                                        # Extract path (last argument usually)
                                        parts = command.split()
                                        search_path = parts[-1] if len(parts) > 2 else "."

                                        result = self.grep_search(pattern, search_path, "*.py", output_mode="files_with_matches")
                                        output = f"Files matching '{pattern}':\n" + '\n'.join(result['files'][:20])
                                        intercepted = True
                                        tools_used.append("grep_search")
                                        if debug_mode:
                                            print(f"🔄 Intercepted: {command} → grep_search({pattern}, {search_path})")
                                except:
                                    pass

                            # If not intercepted, execute as shell command
                            if not intercepted:
                                output = self.execute_command(command)
                            
                            if not output.startswith("ERROR"):
                                # Success - store results
                                api_results["shell_info"] = {
                                    "command": command,
                                    "output": output,
                                    "reason": reason,
                                    "safety_level": safety_level
                                }
                                tools_used.append("shell_execution")
                                
                                # Update file context if needed
                                if updates_context:
                                    import re
                                    # Extract file paths from command
                                    file_patterns = r'([a-zA-Z0-9_\-./]+\.(py|r|csv|txt|json|md|ipynb|rmd))'
                                    files_mentioned = re.findall(file_patterns, command, re.IGNORECASE)
                                    if files_mentioned:
                                        file_path = files_mentioned[0][0]
                                        self.file_context['last_file'] = file_path
                                        if file_path not in self.file_context['recent_files']:
                                            self.file_context['recent_files'].append(file_path)
                                            self.file_context['recent_files'] = self.file_context['recent_files'][-5:]  # Keep last 5
                                    
                                    # Extract directory paths
                                    dir_patterns = r'cd\s+([^\s&|;]+)|mkdir\s+([^\s&|;]+)'
                                    dirs_mentioned = re.findall(dir_patterns, command)
                                    if dirs_mentioned:
                                        for dir_tuple in dirs_mentioned:
                                            dir_path = dir_tuple[0] or dir_tuple[1]
                                            if dir_path:
                                                self.file_context['last_directory'] = dir_path
                                                if dir_path not in self.file_context['recent_dirs']:
                                                    self.file_context['recent_dirs'].append(dir_path)
                                                    self.file_context['recent_dirs'] = self.file_context['recent_dirs'][-5:]  # Keep last 5
                                    
                                    # If cd command, update current_cwd
                                    if command.startswith('cd '):
                                        try:
                                            new_cwd = self.execute_command("pwd").strip()
                                            self.file_context['current_cwd'] = new_cwd
                                        except:
                                            pass
                            else:
                                # Command failed
                                api_results["shell_info"] = {
                                    "error": output,
                                    "command": command
                                }
                    
                    # Backwards compatibility: support old hardcoded actions if LLM still returns them
                    elif shell_action == "pwd":
                        target = plan.get("target_path")
                        if target:
                            ls_output = self.execute_command(f"ls -lah {target}")
                            api_results["shell_info"] = {
                                "directory_contents": ls_output,
                                "target_path": target
                            }
                        else:
                            ls_output = self.execute_command("ls -lah")
                            api_results["shell_info"] = {"directory_contents": ls_output}
                        tools_used.append("shell_execution")
                    
                    elif shell_action == "find":
                        search_target = plan.get("search_target", "")
                        search_path = plan.get("search_path", "~")
                        if search_target:
                            find_cmd = f"find {search_path} -maxdepth 4 -type d -iname '*{search_target}*' 2>/dev/null | head -20"
                            find_output = self.execute_command(find_cmd)
                            if debug_mode:
                                print(f"🔍 FIND: {find_cmd}")
                                print(f"🔍 OUTPUT: {repr(find_output)}")
                            if find_output.strip():
                                api_results["shell_info"] = {
                                    "search_results": f"Searched for '*{search_target}*' in {search_path}:\n{find_output}"
                                }
                            else:
                                api_results["shell_info"] = {
                                    "search_results": f"No directories matching '{search_target}' found in {search_path}"
                                }
                            tools_used.append("shell_execution")
                    
                    elif shell_action == "cd":
                        # NEW: Change directory
                        target = plan.get("target_path")
                        if target:
                            # Expand ~ to home directory
                            if target.startswith("~"):
                                home = os.path.expanduser("~")
                                target = target.replace("~", home, 1)
                            
                            # Execute cd command
                            cd_cmd = f"cd {target} && pwd"
                            cd_output = self.execute_command(cd_cmd)
                            
                            if not cd_output.startswith("ERROR"):
                                api_results["shell_info"] = {
                                    "directory_changed": True,
                                    "new_directory": cd_output.strip(),
                                    "target_path": target
                                }
                                tools_used.append("shell_execution")
                            else:
                                api_results["shell_info"] = {
                                    "directory_changed": False,
                                    "error": f"Failed to change to {target}: {cd_output}"
                                }
                    
                    elif shell_action == "read_file":
                        # NEW: Read and inspect file (R, Python, CSV, etc.)
                        import re  # Import at function level
                        
                        file_path = plan.get("file_path", "")
                        if not file_path and might_need_shell:
                            # Try to infer from query (e.g., "show me calculate_betas.R")
                            filenames = re.findall(r'([a-zA-Z0-9_-]+\.[a-zA-Z]{1,4})', request.question)
                            if filenames:
                                # Check if file exists in current directory
                                pwd = self.execute_command("pwd").strip()
                                file_path = f"{pwd}/{filenames[0]}"
                        
                        if file_path:
                            if debug_mode:
                                print(f"🔍 READING FILE: {file_path}")
                            
                            # Read file content (first 100 lines to detect structure)
                            cat_output = self.execute_command(f"head -100 {file_path}")
                            
                            if not cat_output.startswith("ERROR"):
                                # Detect file type and extract structure
                                file_ext = file_path.split('.')[-1].lower()
                                
                                # Extract column/variable info based on file type
                                columns_info = ""
                                if file_ext in ['csv', 'tsv']:
                                    # CSV: first line is usually headers
                                    first_line = cat_output.split('\n')[0] if cat_output else ""
                                    columns_info = f"CSV columns: {first_line}"
                                elif file_ext in ['r', 'rmd']:
                                    # R script: look for dataframe column references (df$columnname)
                                    column_refs = re.findall(r'\$(\w+)', cat_output)
                                    unique_cols = list(dict.fromkeys(column_refs))[:10]
                                    if unique_cols:
                                        columns_info = f"Detected columns/variables: {', '.join(unique_cols)}"
                                elif file_ext == 'py':
                                    # Python: look for DataFrame['column'] or df.column
                                    column_refs = re.findall(r'\[[\'""](\w+)[\'"]\]|\.(\w+)', cat_output)
                                    unique_cols = list(dict.fromkeys([c[0] or c[1] for c in column_refs if c[0] or c[1]]))[:10]
                                    if unique_cols:
                                        columns_info = f"Detected columns/attributes: {', '.join(unique_cols)}"
                                
                                api_results["file_context"] = {
                                    "file_path": file_path,
                                    "file_type": file_ext,
                                    "content_preview": cat_output[:2000],  # First 2000 chars
                                    "structure": columns_info,
                                    "full_content": cat_output  # Full content for analysis
                                }
                                tools_used.append("file_read")
                                
                                if debug_mode:
                                    print(f"🔍 FILE STRUCTURE: {columns_info}")
                            else:
                                api_results["file_context"] = {
                                    "error": f"Could not read file: {file_path}"
                                }
                
                except Exception as e:
                    if debug_mode:
                        print(f"🔍 Shell planner failed: {e}, continuing without shell")
                    shell_action = "none"
            
            # ========================================================================
            # PRIORITY 2: DATA APIs (Only if shell didn't fully handle the query)
            # ========================================================================
            # If shell_action = pwd/ls/find, we might still want data APIs
            # But we skip vague queries to save tokens
            
            # Analyze what data APIs are needed (only if not pure shell command)
            request_analysis = await self._analyze_request_type(request.question)
            if debug_mode:
                print(f"🔍 Request analysis: {request_analysis}")
            
            is_vague = self._is_query_too_vague_for_apis(request.question)
            if debug_mode and is_vague:
                print(f"🔍 Query is VAGUE - skipping expensive APIs")
            
            # If query is vague, hint to backend LLM to ask clarifying questions
            if is_vague:
                api_results["query_analysis"] = {
                    "is_vague": True,
                    "suggestion": "Ask clarifying questions instead of guessing",
                    "reason": "Query needs more specificity to provide accurate answer"
                }
            
            # Skip Archive/FinSight if query is too vague, but still allow web search later
            if not is_vague:
                # Archive API for research
                if "archive" in request_analysis.get("apis", []):
                    result = await self.search_academic_papers(request.question, 3)  # Reduced from 5 to save tokens
                    if "error" not in result:
                        # Strip abstracts to save tokens - only keep essential fields
                        if "results" in result:
                            for paper in result["results"]:
                                # Remove heavy fields
                                paper.pop("abstract", None)
                                paper.pop("tldr", None)
                                paper.pop("full_text", None)
                                # Keep only: title, authors, year, doi, url
                        api_results["research"] = result
                        tools_used.append("archive_api")
                
                # FinSight API for financial data - Use LLM for ticker/metric extraction
                if "finsight" in request_analysis.get("apis", []):
                    # LLM extracts ticker + metric (more accurate than regex)
                    finance_prompt = f"""Extract financial query details from user's question.

User query: "{request.question}"

Respond with JSON:
{{
  "tickers": ["AAPL", "TSLA"] (stock symbols - infer from company names if needed),
  "metric": "revenue|marketCap|price|netIncome|eps|freeCashFlow|grossProfit"
}}

Examples:
- "Tesla revenue" → {{"tickers": ["TSLA"], "metric": "revenue"}}
- "What's Apple worth?" → {{"tickers": ["AAPL"], "metric": "marketCap"}}
- "tsla stock price" → {{"tickers": ["TSLA"], "metric": "price"}}
- "Microsoft profit" → {{"tickers": ["MSFT"], "metric": "netIncome"}}

JSON:"""

                    try:
                        finance_response = await self.call_backend_query(
                            query=finance_prompt,
                            conversation_history=[],
                            api_results={},
                            tools_used=[]
                        )
                        
                        import json as json_module
                        finance_text = finance_response.response.strip()
                        if '```' in finance_text:
                            finance_text = finance_text.split('```')[1].replace('json', '').strip()
                        
                        finance_plan = json_module.loads(finance_text)
                        tickers = finance_plan.get("tickers", [])
                        metric = finance_plan.get("metric", "revenue")
                        
                        if debug_mode:
                            print(f"🔍 LLM FINANCE PLAN: tickers={tickers}, metric={metric}")
                        
                        if tickers:
                            # Call FinSight with extracted ticker + metric
                            financial_data = await self._call_finsight_api(f"calc/{tickers[0]}/{metric}")
                            if debug_mode:
                                print(f"🔍 FinSight returned: {list(financial_data.keys()) if financial_data else None}")
                            if financial_data and "error" not in financial_data:
                                api_results["financial"] = financial_data
                                tools_used.append("finsight_api")
                    
                    except Exception as e:
                        if debug_mode:
                            print(f"🔍 Finance LLM extraction failed: {e}")
            
            # ========================================================================
            # PRIORITY 3: WEB SEARCH (Fallback - only if shell didn't handle AND no data yet)
            # ========================================================================
            # Only web search if:
            # - Shell said "none" (not a directory/file operation)
            # - We don't have enough data from Archive/FinSight
            
            # First check: Is this a conversational query that doesn't need web search?
            def is_conversational_query(query: str) -> bool:
                """Detect if query is conversational (greeting, thanks, testing, etc.)"""
                query_lower = query.lower().strip()
                
                # Single word queries that are conversational
                conversational_words = {
                    'hello', 'hi', 'hey', 'thanks', 'thank', 'ok', 'okay', 'yes', 'no',
                    'test', 'testing', 'cool', 'nice', 'great', 'awesome', 'perfect',
                    'bye', 'goodbye', 'quit', 'exit', 'help'
                }
                
                # Short conversational phrases
                conversational_phrases = [
                    'how are you', 'thank you', 'thanks!', 'ok', 'got it', 'i see',
                    'makes sense', 'sounds good', 'that works', 'no problem'
                ]
                
                words = query_lower.split()
                
                # Single word check
                if len(words) == 1 and words[0] in conversational_words:
                    return True
                
                # Short phrase check
                if len(words) <= 3 and any(phrase in query_lower for phrase in conversational_phrases):
                    return True
                
                # Question marks with no content words (just pronouns)
                if '?' in query_lower and len(words) <= 2:
                    return True
                
                return False
            
            skip_web_search = is_conversational_query(request.question)
            
            if self.web_search and shell_action == "none" and not skip_web_search:
                # Ask LLM: Should we web search for this?
                web_decision_prompt = f"""You are a tool selection expert. Decide if web search is needed.

User query: "{request.question}"
Data already available: {list(api_results.keys())}
Tools already used: {tools_used}

AVAILABLE TOOLS YOU SHOULD KNOW:
1. FinSight API: Company financial data (revenue, income, margins, ratios, cash flow, balance sheet, SEC filings)
   - Covers: All US public companies (~8,000)
   - Data: SEC EDGAR + Yahoo Finance
   - Metrics: 50+ financial KPIs
   
2. Archive API: Academic research papers
   - Covers: Semantic Scholar, OpenAlex, PubMed
   - Data: Papers, citations, abstracts
   
3. Web Search: General information, current events
   - Covers: Anything on the internet
   - Use for: Market share, industry news, non-financial company info

DECISION RULES:
- If query is about company financials (revenue, profit, margins, etc.) → Check if FinSight already provided data
- If FinSight has data in api_results → Web search is NOT needed
- If FinSight was called but no data → Web search as fallback is OK
- If query is about market share, industry size, trends → Web search (FinSight doesn't have this)
- If query is about research papers → Archive handles it, not web
- If query is conversational → Already filtered, you won't see these

Respond with JSON:
{{
  "use_web_search": true/false,
  "reason": "explain why based on tools available and data already fetched"
}}

JSON:"""

                try:
                    web_decision_response = await self.call_backend_query(
                        query=web_decision_prompt,
                        conversation_history=[],
                        api_results={},
                        tools_used=[]
                    )
                    
                    import json as json_module
                    decision_text = web_decision_response.response.strip()
                    if '```' in decision_text:
                        decision_text = decision_text.split('```')[1].replace('json', '').strip()
                    
                    decision = json_module.loads(decision_text)
                    needs_web_search = decision.get("use_web_search", False)
                    
                    if debug_mode:
                        print(f"🔍 WEB SEARCH DECISION: {needs_web_search}, reason: {decision.get('reason')}")
                    
                    if needs_web_search:
                        web_results = await self.web_search.search_web(request.question, num_results=3)
                        if web_results and "results" in web_results:
                            api_results["web_search"] = web_results
                            tools_used.append("web_search")
                            if debug_mode:
                                print(f"🔍 Web search returned: {len(web_results.get('results', []))} results")
                
                except Exception as e:
                    if debug_mode:
                        print(f"🔍 Web search decision failed: {e}")
            
            # PRODUCTION MODE: Call backend LLM with all gathered data
            if self.client is None:
                # DEBUG: Log what we're sending
                if debug_mode and api_results.get("shell_info"):
                    print(f"🔍 SENDING TO BACKEND: shell_info keys = {list(api_results.get('shell_info', {}).keys())}")
                
                # Call backend and UPDATE CONVERSATION HISTORY
                response = await self.call_backend_query(
                    query=request.question,
                    conversation_history=self.conversation_history[-10:],
                    api_results=api_results,
                    tools_used=tools_used
                )

                # POST-PROCESSING: Auto-extract code blocks and write files if user requested file creation
                # This fixes the issue where LLM shows corrected code but doesn't create the file
                if any(keyword in request.question.lower() for keyword in ['create', 'write', 'save', 'generate', 'fixed', 'corrected']):
                    # Extract filename from query (e.g., "write to foo.py", "create bar_fixed.py")
                    import re
                    filename_match = re.search(r'(?:to|create|write|save|generate)\s+(\w+[._-]\w+\.[\w]+)', request.question, re.IGNORECASE)
                    if not filename_match:
                        # Try pattern: "foo_fixed.py" or "bar.py"
                        filename_match = re.search(r'(\w+_fixed\.[\w]+|\w+\.[\w]+)', request.question)

                    if filename_match:
                        target_filename = filename_match.group(1)

                        # Extract code block from response (```python ... ``` or ``` ... ```)
                        code_block_pattern = r'```(?:python|bash|sh|r|sql)?\n(.*?)```'
                        code_blocks = re.findall(code_block_pattern, response.response, re.DOTALL)

                        if code_blocks:
                            # Use the LARGEST code block (likely the complete file)
                            largest_block = max(code_blocks, key=len)

                            # Write to file
                            try:
                                write_result = self.write_file(target_filename, largest_block)
                                if write_result['success']:
                                    # Append confirmation to response
                                    response.response += f"\n\n✅ File created: {target_filename} ({write_result['bytes_written']} bytes)"
                                    if debug_mode:
                                        print(f"🔄 Auto-extracted code block → write_file({target_filename})")
                            except Exception as e:
                                if debug_mode:
                                    print(f"⚠️ Auto-write failed: {e}")

                # CRITICAL: Save to conversation history
                self.conversation_history.append({"role": "user", "content": request.question})
                self.conversation_history.append({"role": "assistant", "content": response.response})

                return response

            # DEV MODE ONLY: Direct Groq calls (only works with local API keys)
            # This code path won't execute in production since self.client = None

            if not self._check_query_budget(request.user_id):
                effective_limit = self.daily_query_limit if self.daily_query_limit > 0 else self.per_user_query_limit
                if effective_limit <= 0:
                    effective_limit = 25
                message = (
                    "Daily query limit reached. You've hit the "
                    f"{effective_limit} request cap for today. "
                    "Try again tomorrow or reach out if you need the limit raised."
                )
                return self._quick_reply(
                    request,
                    message,
                    tools_used=["rate_limit"],
                    confidence=0.35,
                )

            self._record_query_usage(request.user_id)

            # Analyze request type
            request_analysis = await self._analyze_request_type(request.question)
            question_lower = request.question.lower()
            
            self._reset_data_sources()

            direct_shell = re.match(r"^(?:run|execute)\s*:?\s*(.+)$", request.question.strip(), re.IGNORECASE)
            if direct_shell:
                return self._respond_with_shell_command(request, direct_shell.group(1).strip())

            # Get memory context
            memory_context = self._get_memory_context(request.user_id, request.conversation_id)

            # Ultra-light handling for small talk to save tokens entirely
            if self._is_simple_greeting(request.question):
                return self._quick_reply(
                    request,
                    "Hi there! I'm up and ready whenever you want to dig into finance or research.",
                    tools_used=["quick_reply"],
                    confidence=0.5
                )

            if self._is_casual_acknowledgment(request.question):
                return self._quick_reply(
                    request,
                    "Happy to help! Feel free to fire off another question whenever you're ready.",
                    tools_used=["quick_reply"],
                    confidence=0.55
                )
            
            # Check for workflow commands (natural language)
            workflow_response = await self._handle_workflow_commands(request)
            if workflow_response:
                return workflow_response
            
            # Call appropriate APIs based on request type
            api_results = {}
            tools_used = []

            # Auto file-reading: detect filenames in the prompt and attach previews
            def _extract_filenames(text: str) -> List[str]:
                # Match common file patterns (no spaces) and simple quoted paths
                patterns = [
                    r"[\w\-./]+\.(?:py|md|txt|json|csv|yml|yaml|toml|ini|ts|tsx|js|ipynb)",
                    r"(?:\./|/)?[\w\-./]+/"  # directories
                ]
                matches: List[str] = []
                for pat in patterns:
                    matches.extend(re.findall(pat, text))
                # Deduplicate and keep reasonable length
                uniq = []
                for m in matches:
                    if len(m) <= 256 and m not in uniq:
                        uniq.append(m)
                return uniq[:5]

            mentioned = _extract_filenames(request.question)
            file_previews: List[Dict[str, Any]] = []
            files_forbidden: List[str] = []
            base_dir = Path.cwd().resolve()
            sensitive_roots = {Path('/etc'), Path('/proc'), Path('/sys'), Path('/dev'), Path('/root'), Path('/usr'), Path('/bin'), Path('/sbin'), Path('/var')}
            def _is_safe_path(path_str: str) -> bool:
                try:
                    rp = Path(path_str).resolve()
                    if any(str(rp).startswith(str(sr)) for sr in sensitive_roots):
                        return False
                    return str(rp).startswith(str(base_dir))
                except Exception:
                    return False
            for m in mentioned:
                if not _is_safe_path(m):
                    files_forbidden.append(m)
                    continue
                pr = await self._preview_file(m)
                if pr:
                    file_previews.append(pr)
            if file_previews:
                api_results["files"] = file_previews
                # Build grounded context from first text preview
                text_previews = [fp for fp in file_previews if fp.get("type") == "text" and fp.get("preview")]
                files_context = ""
                if text_previews:
                    fp = text_previews[0]
                    quoted = "\n".join(fp["preview"].splitlines()[:20])
                    files_context = f"File: {fp['path']} (first lines)\n" + quoted
                api_results["files_context"] = files_context
            elif mentioned:
                # Mentioned files but none found
                api_results["files_missing"] = mentioned
            if files_forbidden:
                api_results["files_forbidden"] = files_forbidden

            workspace_listing: Optional[Dict[str, Any]] = None
            if not file_previews:
                file_browse_keywords = (
                    "list files",
                    "show files",
                    "show me files",
                    "file browser",
                    "file upload",
                    "upload file",
                    "files?",
                    "browse files",
                    "what files",
                    "available files"
                )
                describe_files = (
                    "file" in question_lower or "directory" in question_lower
                ) and any(verb in question_lower for verb in ("show", "list", "what", "which", "display"))
                if any(keyword in question_lower for keyword in file_browse_keywords) or describe_files:
                    workspace_listing = await self._get_workspace_listing()
                    api_results["workspace_listing"] = workspace_listing

            if workspace_listing and set(request_analysis.get("apis", [])) <= {"shell"}:
                return self._respond_with_workspace_listing(request, workspace_listing)
            
            if "finsight" in request_analysis["apis"]:
                # Extract tickers from symbols or company names
                tickers = self._extract_tickers_from_text(request.question)
                financial_payload = {}
                session_key = f"{request.user_id}:{request.conversation_id}"
                last_topic = self._session_topics.get(session_key)
                if not tickers:
                    # Heuristic defaults for common requests
                    if "apple" in request.question.lower():
                        tickers = ["AAPL"]
                    if "microsoft" in request.question.lower():
                        tickers = tickers + ["MSFT"] if "AAPL" in tickers else ["MSFT"]

                # Determine which metrics to fetch based on query keywords
                metrics_to_fetch = []
                if any(kw in question_lower for kw in ["revenue", "sales", "top line"]):
                    metrics_to_fetch.append("revenue")
                if any(kw in question_lower for kw in ["gross profit", "gross margin", "margin"]):
                    metrics_to_fetch.append("grossProfit")
                if any(kw in question_lower for kw in ["operating income", "operating profit", "ebit"]):
                    metrics_to_fetch.append("operatingIncome")
                if any(kw in question_lower for kw in ["net income", "profit", "earnings", "bottom line"]):
                    metrics_to_fetch.append("netIncome")

                # Default to key metrics if no specific request
                if not metrics_to_fetch and last_topic and last_topic.get("metrics"):
                    metrics_to_fetch = list(last_topic["metrics"])

                if not metrics_to_fetch:
                    metrics_to_fetch = ["revenue", "grossProfit"]

                # Fetch metrics for each ticker (cap 2 tickers)
                for t in tickers[:2]:
                    result = await self.get_financial_metrics(t, metrics_to_fetch)
                    financial_payload[t] = result

                if financial_payload:
                    self._session_topics[session_key] = {
                        "tickers": tickers[:2],
                        "metrics": metrics_to_fetch,
                    }
                    direct_finance = (
                        len(financial_payload) == 1
                        and set(request_analysis.get("apis", [])) == {"finsight"}
                        and not api_results.get("research")
                        and not file_previews
                        and not workspace_listing
                    )
                    if direct_finance:
                        return self._respond_with_financial_metrics(request, financial_payload)
                    api_results["financial"] = financial_payload
                    tools_used.append("finsight_api")
            
            if "archive" in request_analysis["apis"]:
                # Extract research query
                result = await self.search_academic_papers(request.question, 5)
                if "error" not in result:
                    api_results["research"] = result
                    # DEBUG: Log what we got from the API
                    papers_count = len(result.get("results", []))
                    logger.info(f"🔍 DEBUG: Got {papers_count} papers from Archive API")
                    if papers_count > 0:
                        logger.info(f"🔍 DEBUG: First paper: {result['results'][0].get('title', 'NO TITLE')[:80]}")
                else:
                    api_results["research"] = {"error": result["error"]}
                    logger.warning(f"🔍 DEBUG: Archive API returned error: {result['error']}")
                tools_used.append("archive_api")
            
            # Build enhanced system prompt with trimmed sections based on detected needs
            system_prompt = self._build_system_prompt(request_analysis, memory_context, api_results)
            
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            # If we have file context, inject it as an additional grounding message
            fc = api_results.get("files_context")
            if fc:
                messages.append({"role": "system", "content": f"Grounding from mentioned file(s):\n{fc}\n\nAnswer based strictly on this content when relevant. Do not run shell commands."})
            missing = api_results.get("files_missing")
            if missing:
                messages.append({"role": "system", "content": f"User mentioned file(s) not found: {missing}. Respond explicitly that the file was not found and avoid speculation."})
            forbidden = api_results.get("files_forbidden")
            if forbidden:
                messages.append({"role": "system", "content": f"User mentioned file(s) outside the allowed workspace or sensitive paths: {forbidden}. Refuse to access and explain the restriction succinctly."})
            
            # Add conversation history with smart context management
            if len(self.conversation_history) > 12:
                # For long conversations, summarize early context and keep recent history
                early_history = self.conversation_history[:-6]
                recent_history = self.conversation_history[-6:]
                
                # Create a summary of early conversation
                summary_prompt = "Summarize the key points from this conversation history in 2-3 sentences:"
                summary_messages = [
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": str(early_history)}
                ]
                
                try:
                    if self._ensure_client_ready():
                        summary_response = self.client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=summary_messages,
                            max_tokens=160,
                            temperature=0.2
                        )
                        conversation_summary = summary_response.choices[0].message.content
                        if summary_response.usage and summary_response.usage.total_tokens:
                            summary_tokens = summary_response.usage.total_tokens
                            self._charge_tokens(request.user_id, summary_tokens)
                            self.total_cost += (summary_tokens / 1000) * self.cost_per_1k_tokens
                        messages.append({"role": "system", "content": f"Previous conversation summary: {conversation_summary}"})
                except:
                    # If summary fails, just use recent history
                    pass
                
                messages.extend(recent_history)
            else:
                # For shorter conversations, use full history
                messages.extend(self.conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": request.question})

            model_config = self._select_model(request, request_analysis, api_results)
            target_model = model_config["model"]
            max_completion_tokens = model_config["max_tokens"]
            temperature = model_config["temperature"]
            
            # Check token budget
            estimated_tokens = (len(str(messages)) // 4) + max_completion_tokens  # Rough estimate incl. completion budget
            if not self._check_token_budget(estimated_tokens):
                return self._respond_with_fallback(
                    request,
                    tools_used,
                    api_results,
                    failure_reason="Daily Groq token budget exhausted",
                    error_message="Daily token limit reached"
                )

            if not self._check_user_token_budget(request.user_id, estimated_tokens):
                return self._respond_with_fallback(
                    request,
                    tools_used,
                    api_results,
                    failure_reason="Per-user Groq token budget exhausted",
                    error_message="Per-user token limit reached"
                )

            if not self._ensure_client_ready():
                return self._respond_with_fallback(
                    request,
                    tools_used,
                    api_results,
                    failure_reason="No available Groq API key"
                )

            response_text: Optional[str] = None
            tokens_used = 0
            attempts_remaining = len(self.api_keys) if self.api_keys else (1 if self.client else 0)
            last_error: Optional[Exception] = None

            while attempts_remaining > 0:
                attempts_remaining -= 1
                try:
                    response = self.client.chat.completions.create(
                        model=target_model,
                        messages=messages,
                        max_tokens=max_completion_tokens,
                        temperature=temperature
                    )

                    response_text = response.choices[0].message.content
                    tokens_used = response.usage.total_tokens if response.usage else estimated_tokens
                    self._charge_tokens(request.user_id, tokens_used)
                    cost = (tokens_used / 1000) * self.cost_per_1k_tokens
                    self.total_cost += cost
                    break
                except Exception as e:
                    last_error = e
                    if self._is_rate_limit_error(e):
                        self._mark_current_key_exhausted(str(e))
                        if not self._rotate_to_next_available_key():
                            break
                        continue
                    else:
                        error_str = str(e)
                        friendly = self._format_model_error(error_str)
                        return ChatResponse(
                            response=friendly,
                            timestamp=datetime.now().isoformat(),
                            tools_used=tools_used,
                            api_results=api_results,
                            error_message=error_str
                        )

            if response_text is None:
                rate_limit_error = last_error if last_error and self._is_rate_limit_error(last_error) else None
                if rate_limit_error:
                    return self._respond_with_fallback(
                        request,
                        tools_used,
                        api_results,
                        failure_reason="All Groq API keys exhausted",
                        error_message=str(rate_limit_error)
                    )
                error_str = str(last_error) if last_error else "Unknown error"
                friendly = self._format_model_error(error_str)
                return ChatResponse(
                    response=friendly,
                    timestamp=datetime.now().isoformat(),
                    tools_used=tools_used,
                    api_results=api_results,
                    error_message=error_str
                )

            self._schedule_next_key_rotation()
            
            allow_shell_commands = "shell" in request_analysis.get("apis", []) or request_analysis.get("type") in {"system", "comprehensive+system"}
            if api_results.get("files_context") or api_results.get("files_missing") or api_results.get("files_forbidden"):
                allow_shell_commands = False

            commands = re.findall(r'`([^`]+)`', response_text) if allow_shell_commands else []
            execution_results = {}
            final_response = response_text

            if commands:
                command = commands[0].strip()
                if self._is_safe_shell_command(command):
                    print(f"\n🔧 Executing: {command}")
                    output = self.execute_command(command)
                    print(f"✅ Command completed")
                    execution_results = {
                        "command": command,
                        "output": output,
                        "success": not output.startswith("ERROR:")
                    }
                    tools_used.append("shell_execution")
                else:
                    execution_results = {
                        "command": command,
                        "output": "Command blocked by safety policy",
                        "success": False
                    }
                    if "⚠️ Shell command skipped for safety." not in final_response:
                        final_response = f"{final_response.strip()}\n\n⚠️ Shell command skipped for safety."
                
                # Create analysis prompt only if we actually executed and have output
                if execution_results.get("success") and isinstance(execution_results.get("output"), str):
                    truncated_output = execution_results["output"]
                    truncated_flag = False
                    if len(truncated_output) > 1000:
                        truncated_output = truncated_output[:1000]
                        truncated_flag = True

                    summarised_text, summary_tokens = self._summarize_command_output(
                        request,
                        command,
                        truncated_output,
                        response_text
                    )

                    final_response = summarised_text
                    if truncated_flag:
                        final_response += "\n\n(Output truncated to first 1000 characters.)"
                    if summary_tokens:
                        self._charge_tokens(request.user_id, summary_tokens)
                        tokens_used += summary_tokens
            else:
                final_response = response_text
            
            footer = self._format_data_sources_footer()
            if footer:
                final_response = f"{final_response}\n\n_{footer}_"

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": request.question})
            self.conversation_history.append({"role": "assistant", "content": final_response})
            
            # Update memory
            self._update_memory(
                request.user_id, 
                request.conversation_id, 
                f"Q: {request.question[:100]}... A: {final_response[:100]}..."
            )
            
            # Save to workflow history automatically
            self.workflow.save_query_result(
                query=request.question,
                response=final_response,
                metadata={
                    "tools_used": tools_used,
                    "tokens_used": tokens_used,
                    "confidence_score": request_analysis['confidence']
                }
            )
            
            return ChatResponse(
                response=final_response,
                tools_used=tools_used,
                reasoning_steps=[f"Request type: {request_analysis['type']}", f"APIs used: {request_analysis['apis']}"],
                timestamp=datetime.now().isoformat(),
                tokens_used=tokens_used,
                confidence_score=request_analysis['confidence'],
                execution_results=execution_results,
                api_results=api_results
            )
            
        except Exception as e:
            details = str(e)
            message = (
                "⚠️ Something went wrong while orchestrating your request, but no actions were performed. "
                "Please retry, and if the issue persists share this detail with the team: {details}."
            ).format(details=details)
            return ChatResponse(
                response=message,
                timestamp=datetime.now().isoformat(),
                confidence_score=0.0,
                error_message=details
            )
    
    async def process_request_streaming(self, request: ChatRequest):
        """
        Process request with streaming response from Groq API
        Returns a Groq stream object that yields chunks as they arrive

        This enables real-time character-by-character streaming in the UI
        """
        # PRODUCTION MODE: Backend doesn't support streaming yet, use regular response
        if self.client is None:
            response = await self.call_backend_query(request.question, self.conversation_history[-10:])
            async def single_yield():
                yield response.response
            return single_yield()

        # DEV MODE ONLY
        try:
            # Quick budget checks
            if not self._check_query_budget(request.user_id):
                effective_limit = self.daily_query_limit if self.daily_query_limit > 0 else self.per_user_query_limit
                if effective_limit <= 0:
                    effective_limit = 25
                error_msg = (
                    f"Daily query limit reached. You've hit the {effective_limit} request cap for today. "
                    "Try again tomorrow or reach out if you need the limit raised."
                )
                async def error_gen():
                    yield error_msg
                return error_gen()

            self._record_query_usage(request.user_id)
            
            # Analyze request
            request_analysis = await self._analyze_request_type(request.question)
            question_lower = request.question.lower()
            self._reset_data_sources()

            # Direct shell commands (non-streaming fallback)
            direct_shell = re.match(r"^(?:run|execute)\s*:?\s*(.+)$", request.question.strip(), re.IGNORECASE)
            if direct_shell:
                result = self._respond_with_shell_command(request, direct_shell.group(1).strip())
                async def shell_gen():
                    yield result.response
                return shell_gen()

            # Memory context
            memory_context = self._get_memory_context(request.user_id, request.conversation_id)

            # Quick greetings (non-streaming)
            if self._is_simple_greeting(request.question):
                async def greeting_gen():
                    yield "Hi there! I'm up and ready whenever you want to dig into finance or research."
                return greeting_gen()

            if self._is_casual_acknowledgment(request.question):
                async def ack_gen():
                    yield "Happy to help! Feel free to fire off another question whenever you're ready."
                return ack_gen()
            
            # Gather API results (same logic as process_request but abbreviated)
            api_results = {}
            tools_used = []

            # File preview
            def _extract_filenames(text: str) -> List[str]:
                patterns = [
                    r"[\w\-./]+\.(?:py|md|txt|json|csv|yml|yaml|toml|ini|ts|tsx|js|ipynb)",
                    r"(?:\./|/)?[\w\-./]+/"
                ]
                matches: List[str] = []
                for pat in patterns:
                    matches.extend(re.findall(pat, text))
                uniq = []
                for m in matches:
                    if len(m) <= 256 and m not in uniq:
                        uniq.append(m)
                return uniq[:5]

            mentioned = _extract_filenames(request.question)
            file_previews: List[Dict[str, Any]] = []
            files_forbidden: List[str] = []
            base_dir = Path.cwd().resolve()
            sensitive_roots = {Path('/etc'), Path('/proc'), Path('/sys'), Path('/dev'), Path('/root'), Path('/usr'), Path('/bin'), Path('/sbin'), Path('/var')}
            
            def _is_safe_path(path_str: str) -> bool:
                try:
                    rp = Path(path_str).resolve()
                    if any(str(rp).startswith(str(sr)) for sr in sensitive_roots):
                        return False
                    return str(rp).startswith(str(base_dir))
                except Exception:
                    return False
                    
            for m in mentioned:
                if not _is_safe_path(m):
                    files_forbidden.append(m)
                    continue
                pr = await self._preview_file(m)
                if pr:
                    file_previews.append(pr)
                    
            if file_previews:
                api_results["files"] = file_previews
                text_previews = [fp for fp in file_previews if fp.get("type") == "text" and fp.get("preview")]
                files_context = ""
                if text_previews:
                    fp = text_previews[0]
                    quoted = "\n".join(fp["preview"].splitlines()[:20])
                    files_context = f"File: {fp['path']} (first lines)\n" + quoted
                api_results["files_context"] = files_context
            elif mentioned:
                api_results["files_missing"] = mentioned
            if files_forbidden:
                api_results["files_forbidden"] = files_forbidden

            # Workspace listing
            workspace_listing: Optional[Dict[str, Any]] = None
            if not file_previews:
                file_browse_keywords = ("list files", "show files", "what files")
                describe_files = ("file" in question_lower or "directory" in question_lower)
                if any(keyword in question_lower for keyword in file_browse_keywords) or describe_files:
                    workspace_listing = await self._get_workspace_listing()
                    api_results["workspace_listing"] = workspace_listing

            if workspace_listing and set(request_analysis.get("apis", [])) <= {"shell"}:
                result = self._respond_with_workspace_listing(request, workspace_listing)
                async def workspace_gen():
                    yield result.response
                return workspace_gen()
            
            # FinSight API (abbreviated)
            if "finsight" in request_analysis["apis"]:
                tickers = self._extract_tickers_from_text(request.question)
                financial_payload = {}
                
                if not tickers:
                    if "apple" in question_lower:
                        tickers = ["AAPL"]
                    if "microsoft" in question_lower:
                        tickers = ["MSFT"] if not tickers else tickers + ["MSFT"]

                metrics_to_fetch = ["revenue", "grossProfit"]
                if any(kw in question_lower for kw in ["revenue", "sales"]):
                    metrics_to_fetch = ["revenue"]
                if any(kw in question_lower for kw in ["profit", "margin"]):
                    metrics_to_fetch.append("grossProfit")

                for t in tickers[:2]:
                    result = await self.get_financial_metrics(t, metrics_to_fetch)
                    financial_payload[t] = result

                if financial_payload:
                    api_results["financial"] = financial_payload
                    tools_used.append("finsight_api")
            
            # Archive API (abbreviated)
            if "archive" in request_analysis["apis"]:
                result = await self.search_academic_papers(request.question, 5)
                if "error" not in result:
                    api_results["research"] = result
                else:
                    api_results["research"] = {"error": result["error"]}
                tools_used.append("archive_api")
            
            # Build messages
            system_prompt = self._build_system_prompt(request_analysis, memory_context, api_results)
            messages = [{"role": "system", "content": system_prompt}]
            
            fc = api_results.get("files_context")
            if fc:
                messages.append({"role": "system", "content": f"Grounding from mentioned file(s):\n{fc}"})
            
            # Add conversation history (abbreviated - just recent)
            if len(self.conversation_history) > 6:
                messages.extend(self.conversation_history[-6:])
            else:
                messages.extend(self.conversation_history)
            
            messages.append({"role": "user", "content": request.question})

            # Model selection
            model_config = self._select_model(request, request_analysis, api_results)
            target_model = model_config["model"]
            max_completion_tokens = model_config["max_tokens"]
            temperature = model_config["temperature"]
            
            # Token budget check
            estimated_tokens = (len(str(messages)) // 4) + max_completion_tokens
            if not self._check_token_budget(estimated_tokens):
                async def budget_gen():
                    yield "⚠️ Daily Groq token budget exhausted. Please try again tomorrow."
                return budget_gen()

            if not self._ensure_client_ready():
                async def no_key_gen():
                    yield "⚠️ No available Groq API key."
                return no_key_gen()

            # **STREAMING: Call Groq with stream=True**
            try:
                stream = self.client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    max_tokens=max_completion_tokens,
                    temperature=temperature,
                    stream=True  # Enable streaming!
                )
                
                # Update conversation history (add user message now, assistant message will be added after streaming completes)
                self.conversation_history.append({"role": "user", "content": request.question})
                
                # Return the stream directly - groq_stream_to_generator() in streaming_ui.py will handle it
                return stream
                
            except Exception as e:
                if self._is_rate_limit_error(e):
                    self._mark_current_key_exhausted(str(e))
                    if self._rotate_to_next_available_key():
                        try:
                            stream = self.client.chat.completions.create(
                                model=target_model,
                                messages=messages,
                                max_tokens=max_completion_tokens,
                                temperature=temperature,
                                stream=True
                            )
                            self.conversation_history.append({"role": "user", "content": request.question})
                            return stream
                        except:
                            pass
                async def error_gen():
                    yield f"⚠️ Groq API error: {str(e)}"
                return error_gen()
                        
        except Exception as e:
            async def exception_gen():
                yield f"⚠️ Request failed: {str(e)}"
            return exception_gen()
    
    async def run_interactive(self):
        """Run interactive chat session"""
        if not await self.initialize():
            return
            
        print("\n" + "="*70)
        print("🤖 ENHANCED NOCTURNAL AI AGENT")
        print("="*70)
        print("Research Assistant with Archive API + FinSight API Integration")
        print("Type 'quit' to exit")
        print("="*70)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    await self.close()
                    break
                
                # Process request
                request = ChatRequest(question=user_input)
                response = await self.process_request(request)
                
                print(f"\n🤖 Agent: {response.response}")
                
                if response.api_results:
                    print(f"📊 API Results: {len(response.api_results)} sources used")
                
                if response.execution_results:
                    print(f"🔧 Command: {response.execution_results['command']}")
                    print(f"📊 Success: {response.execution_results['success']}")
                
                print(f"📈 Tokens used: {response.tokens_used}")
                print(f"🎯 Confidence: {response.confidence_score:.2f}")
                print(f"🛠️ Tools used: {', '.join(response.tools_used) if response.tools_used else 'None'}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                await self.close()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

async def main():
    """Main entry point"""
    agent = EnhancedNocturnalAgent()
    await agent.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())
