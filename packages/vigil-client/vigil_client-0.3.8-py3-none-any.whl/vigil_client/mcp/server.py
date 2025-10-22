"""MCP server exposing scientific workflow verbs to external assistants."""

from __future__ import annotations

import asyncio
import json
import shlex
import subprocess
import time
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import polars as pl
import yaml
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

if TYPE_CHECKING:
    from collections.abc import Callable

# Load toolspec from package directory
SPEC_PATH = Path(__file__).parent / "toolspec.yaml"
PREVIEW_RATE_LIMIT = 3
PREVIEW_RATE_WINDOW_SECONDS = 60.0
PREVIEW_MAX_ROWS = 200
WORKSPACE_ROOT = Path.cwd().resolve()


@dataclass(slots=True)
class _RateLimiter:
    """Simple sliding-window rate limiter for preview_data requests."""

    max_calls: int
    window_seconds: float
    timestamps: deque[float]

    @classmethod
    def create(cls, max_calls: int, window_seconds: float) -> _RateLimiter:
        return cls(max_calls=max_calls, window_seconds=window_seconds, timestamps=deque())

    def _prune(self, now: float) -> None:
        while self.timestamps and now - self.timestamps[0] >= self.window_seconds:
            self.timestamps.popleft()

    def allow(self) -> tuple[bool, float]:
        now = time.monotonic()
        self._prune(now)
        if len(self.timestamps) >= self.max_calls:
            retry_after = self.window_seconds - (now - self.timestamps[0])
            return False, max(0.0, retry_after)
        self.timestamps.append(now)
        return True, 0.0


_preview_rate_limiter = _RateLimiter.create(
    max_calls=PREVIEW_RATE_LIMIT,
    window_seconds=PREVIEW_RATE_WINDOW_SECONDS,
)


def _load_toolspec() -> dict[str, Any]:
    try:
        return yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        raise RuntimeError(f"toolspec not found at {SPEC_PATH}") from None


SPEC_DATA = _load_toolspec()
VERB_ENTRIES: list[dict[str, Any]] = [v for v in SPEC_DATA.get("verbs", []) if isinstance(v, dict)]
ALLOWED_VERBS = {entry["name"] for entry in VERB_ENTRIES if "name" in entry}


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _sanitize_workspace_relative(raw: str, *, suffix: str | None = None) -> tuple[str | None, str | None]:
    text = str(raw).strip()
    if not text:
        return None, "value must not be empty"
    if any(ch in text for ch in {"\n", "\r"}):
        return None, "value must not contain newlines"

    candidate = Path(text)
    if candidate.is_absolute():
        return None, "absolute paths are not allowed"
    if any(part == ".." for part in candidate.parts):
        return None, "path traversal using '..' is not allowed"

    resolved = (WORKSPACE_ROOT / candidate).resolve()
    if not _is_relative_to(resolved, WORKSPACE_ROOT):
        return None, "path escapes the workspace root"

    normalized = candidate.as_posix()
    if suffix and not normalized.endswith(suffix):
        return None, f"path must end with {suffix}"
    return normalized, None


def _sanitize_targets(targets: Iterable[str]) -> tuple[list[str] | None, str | None]:
    sanitized: list[str] = []
    for raw in targets:
        text = str(raw).strip()
        if not text:
            continue
        if text.startswith("/"):
            return None, f"target '{text}' must be relative"
        if any(part == ".." for part in Path(text).parts):
            return None, f"target '{text}' may not contain '..'"
        if any(ch in text for ch in {"\n", "\r"}):
            return None, f"target '{text}' contains newline characters"
        sanitized.append(text)

    return (sanitized or ["all"]), None


def _sanitize_profile(profile: str | None) -> tuple[str | None, str | None]:
    if profile is None:
        return None, None
    normalized, error = _sanitize_workspace_relative(str(profile))
    if error:
        return None, f"profile value is unsafe: {error}"
    return normalized, None


def _sanitize_handle_path(handle_path: str) -> tuple[str | None, str | None]:
    return _sanitize_workspace_relative(handle_path, suffix=".dhandle.json")


def _sanitize_directory(path_value: str, *, description: str) -> tuple[str | None, str | None]:
    normalized, error = _sanitize_workspace_relative(path_value)
    if error:
        return None, f"{description} is unsafe: {error}"
    return normalized, None


@dataclass(slots=True)
class CommandResult:
    ok: bool
    stdout: str
    stderr: str

    def merged_output(self) -> str:
        text = "\n".join(part for part in (self.stdout.strip(), self.stderr.strip()) if part)
        return text.strip() or "(no output)"


def run_command(cmd: Sequence[str]) -> CommandResult:
    """Run a command without raising, returning stdout/stderr."""

    proc = subprocess.run(list(cmd), capture_output=True, text=True, check=False)
    return CommandResult(proc.returncode == 0, proc.stdout, proc.stderr)


def _render_targets(arguments: dict[str, Any]) -> list[str]:
    if "targets" in arguments and arguments["targets"] is not None:
        raw = arguments["targets"]
        if isinstance(raw, str):
            return shlex.split(raw)
        if isinstance(raw, Iterable):
            return [str(item) for item in raw]

    single = arguments.get("target", "all")
    if isinstance(single, str):
        return shlex.split(single)
    return ["all"]


def _snakemake_base(targets: list[str], profile: str | None) -> list[str]:
    base = ["uv", "run", "snakemake", "-s", "app/code/pipelines/Snakefile"]
    base.extend(targets)
    if profile:
        base.extend(["--profile", profile])
    return base


def _build_run_target_tool() -> Tool:
    return Tool(
        name="run_target",
        description="Dry-run, execute, and optionally promote a Snakemake target",
        inputSchema={
            "type": "object",
            "properties": {
                "targets": {
                    "type": ["array", "string"],
                    "items": {"type": "string"},
                    "description": "Explicit targets to operate on (defaults to 'all')",
                },
                "target": {
                    "type": "string",
                    "description": "Pipeline target to run (e.g., 'all', 'processed.parquet')",
                },
                "profile": {
                    "type": "string",
                    "description": "Optional Snakemake profile to use",
                },
                "cores": {
                    "type": "integer",
                    "description": "Number of cores for execution phase",
                    "default": 4,
                    "minimum": 1,
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Set true to execute after dry-run",
                    "default": False,
                },
                "promote": {
                    "type": "boolean",
                    "description": "Set true to trigger promote.py after execution succeeds",
                    "default": False,
                },
                "promote_confirm": {
                    "type": "boolean",
                    "description": "Second confirmation required when promote=true",
                    "default": False,
                },
                "promotion_output_dir": {
                    "type": "string",
                    "description": "Receipt output directory for promotion step",
                    "default": "app/code/receipts",
                },
                "promotion_input_dir": {
                    "type": "string",
                    "description": "Artifact directory provided to promote.py",
                    "default": "app/code/artifacts",
                },
                "promotion_vigil_url": {
                    "type": "string",
                    "description": "Vigil URL recorded in generated receipts",
                    "default": "vigil://labs.example/your-org/your-project@refs/heads/main",
                },
            },
            "required": [],
        },
    )


def _build_promote_tool() -> Tool:
    return Tool(
        name="promote",
        description="Generate receipts for completed runs",
        inputSchema={
            "type": "object",
            "properties": {
                "confirm": {
                    "type": "boolean",
                    "description": "Set true to actually generate receipts",
                    "default": False,
                },
                "input_dir": {
                    "type": "string",
                    "description": "Input directory containing artifacts",
                    "default": "app/code/artifacts",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory for receipts",
                    "default": "app/code/receipts",
                },
                "vigil_url": {
                    "type": "string",
                    "description": "Vigil URL to record in the receipt",
                    "default": "vigil://labs.example/your-org/your-project@refs/heads/main",
                },
            },
        },
    )


def _build_preview_tool() -> Tool:
    return Tool(
        name="preview_data",
        description="Inspect a data handle and return a row sample",
        inputSchema={
            "type": "object",
            "properties": {
                "handle_path": {
                    "type": "string",
                    "description": "Path to data handle JSON file",
                    "default": "app/data/handles/data.parquet.dhandle.json",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of rows to preview",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 500,
                },
            },
        },
    )


def _build_ai_generate_pipeline_tool() -> Tool:
    return Tool(
        name="ai_generate_pipeline",
        description="Generate a Snakemake pipeline from natural language description using foundation models",
        inputSchema={
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Natural language description of the analysis pipeline",
                },
                "template": {
                    "type": "string",
                    "description": "Base template (genomics-starter, imaging-starter, etc.)",
                    "default": "genomics-starter",
                },
                "model": {
                    "type": "string",
                    "description": "Specific model to use (e.g., claude-3-5-sonnet, esm-2-650m)",
                },
                "domain": {
                    "type": "string",
                    "description": "Scientific domain for automatic model selection (biology, chemistry, materials, general)",
                },
            },
            "required": ["description"],
        },
    )


def _build_ai_debug_error_tool() -> Tool:
    return Tool(
        name="ai_debug_error",
        description="Get AI-powered debugging suggestions for workflow errors",
        inputSchema={
            "type": "object",
            "properties": {
                "error_message": {
                    "type": "string",
                    "description": "Error message from the failed pipeline",
                },
                "context": {
                    "type": "object",
                    "description": "Additional context (Snakefile, logs, etc.)",
                },
                "model": {
                    "type": "string",
                    "description": "Model to use for debugging",
                },
            },
            "required": ["error_message"],
        },
    )


def _build_ai_optimize_workflow_tool() -> Tool:
    return Tool(
        name="ai_optimize_workflow",
        description="Analyze workflow and get optimization suggestions",
        inputSchema={
            "type": "object",
            "properties": {
                "snakefile": {
                    "type": "string",
                    "description": "Path to Snakefile",
                    "default": "app/code/pipelines/Snakefile",
                },
                "focus": {
                    "type": "string",
                    "description": "Optimization focus (speed, memory, cost, readability)",
                },
            },
            "required": [],
        },
    )


def _build_ai_list_models_tool() -> Tool:
    return Tool(
        name="ai_list_models",
        description="List all available foundation models",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )


def _build_ai_get_model_info_tool() -> Tool:
    return Tool(
        name="ai_get_model_info",
        description="Get detailed information about a specific model",
        inputSchema={
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Model name to get info for",
                },
            },
            "required": ["model"],
        },
    )


def _build_ai_generate_step_tool() -> Tool:
    return Tool(
        name="ai_generate_step",
        description="Generate a Snakemake step script from a natural language description",
        inputSchema={
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Natural language description of the step",
                },
                "rule_name": {
                    "type": "string",
                    "description": "Optional Snakemake rule name",
                },
                "inputs": {
                    "type": ["array", "string"],
                    "description": "Optional inputs for the rule",
                    "items": {"type": "string"},
                },
                "outputs": {
                    "type": ["array", "string"],
                    "description": "Optional outputs for the rule",
                    "items": {"type": "string"},
                },
                "language": {
                    "type": "string",
                    "description": "Script language (python, r, shell)",
                    "default": "python",
                },
                "model": {
                    "type": "string",
                    "description": "Specific foundation model to use",
                },
            },
            "required": ["description"],
        },
    )


_TOOL_BUILDERS: dict[str, Callable[[], Tool]] = {
    # Foundation Layer
    "run_target": _build_run_target_tool,
    "promote": _build_promote_tool,
    "preview_data": _build_preview_tool,
    # Application Layer (AI)
    "ai_generate_pipeline": _build_ai_generate_pipeline_tool,
    "ai_debug_error": _build_ai_debug_error_tool,
    "ai_optimize_workflow": _build_ai_optimize_workflow_tool,
    "ai_generate_step": _build_ai_generate_step_tool,
    "ai_list_models": _build_ai_list_models_tool,
    "ai_get_model_info": _build_ai_get_model_info_tool,
}

unknown_verbs = ALLOWED_VERBS - _TOOL_BUILDERS.keys()
if unknown_verbs:
    raise RuntimeError(f"toolspec declares unsupported verbs: {', '.join(sorted(unknown_verbs))}")


app = Server("scientific-workflow")


def _declared_tools() -> list[Tool]:
    tools: list[Tool] = []
    for entry in VERB_ENTRIES:
        name = entry.get("name")
        if isinstance(name, str):
            builder = _TOOL_BUILDERS.get(name)
            if builder:
                tools.append(builder())
    return tools


def _clamp_preview_limit(limit: int) -> int:
    return max(1, min(limit, PREVIEW_MAX_ROWS))


def _load_handle_rows(handle_path: str | Path, requested_limit: int) -> str:
    try:
        handle = json.loads(Path(handle_path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return f"Handle not found: {handle_path}"
    except json.JSONDecodeError as exc:
        return f"Invalid handle JSON: {exc}"

    clamped_limit = _clamp_preview_limit(requested_limit)
    effective_limit = clamped_limit
    redact_cols = set(handle.get("redact_columns", []))
    offline = handle.get("offline_fallback")
    try:
        if offline:
            frame = pl.read_csv(offline, n_rows=clamped_limit)
        else:
            uri = handle.get("uri")
            guidance = (
                "Handle is missing an 'offline_fallback'. Add a small sample under "
                "app/data/samples/ and set offline_fallback to that path so previews "
                "work without remote storage access."
            )
            if not uri:
                return f"{guidance} The handle also lacks a 'uri' for online preview."
            return (
                f"{guidance} Online preview would require accessing the remote URI: {uri}"
            )
    except FileNotFoundError:
        return "Data source not found for preview"
    except Exception as exc:  # noqa: BLE001 - surface underlying issue
        return f"Error loading data: {exc}"

    if redact_cols:
        frame = frame.drop([col for col in redact_cols if col in frame.columns])

    rows = frame.head(clamped_limit).to_dicts()
    payload = {
        "columns": frame.columns,
        "requested_limit": requested_limit,
        "limit": clamped_limit,
        "max_rows": PREVIEW_MAX_ROWS,
        "effective_limit": effective_limit,
        "returned": len(rows),
        "rows": rows,
    }
    return json.dumps(payload, indent=2)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools defined by the toolspec."""
    return _declared_tools()


async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Execute a tool declared in the toolspec."""
    if name not in ALLOWED_VERBS:
        return CallToolResult(content=[TextContent(type="text", text=f"tool '{name}' not allowed")])

    if name == "run_target":
        targets = _render_targets(arguments)
        sanitized_targets, target_error = _sanitize_targets(targets)
        if target_error:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Invalid targets: {target_error}")]
            )

        profile_value, profile_error = _sanitize_profile(arguments.get("profile"))
        if profile_error:
            return CallToolResult(
                content=[TextContent(type="text", text=profile_error)]
            )

        base_args = _snakemake_base(sanitized_targets, profile_value)

        dry_result = run_command([*base_args, "-n"])
        dry_output = dry_result.merged_output()
        target_label = " ".join(sanitized_targets) or "all"

        if not dry_result.ok:
            message = (
                f"Dry-run for target(s) '{target_label}' failed:\n{dry_output}\n\n"
                "No execution attempted. Resolve the dry-run errors before confirming."
            )
            return CallToolResult(content=[TextContent(type="text", text=message)])

        if not arguments.get("confirm", False):
            message = (
                f"Dry-run for target(s) '{target_label}':\n{dry_output}\n\n"
                "No changes executed. Re-run with confirm=true to apply."
            )
            if arguments.get("promote"):
                message += (
                    "\nPromotion requested but requires confirm=true and promote_confirm=true "
                    "on a follow-up call."
                )
            return CallToolResult(content=[TextContent(type="text", text=message)])

        cores = int(arguments.get("cores", 4) or 4)
        live_args = [*base_args, "--cores", str(max(1, cores))]
        live_result = run_command(live_args)
        live_output = live_result.merged_output()

        if not live_result.ok:
            combined = (
                f"Dry-run output:\n{dry_output}\n\n"
                f"Execution failed:\n{live_output}"
            )
            return CallToolResult(content=[TextContent(type="text", text=combined)])

        sections = [
            f"Dry-run output:\n{dry_output}",
            f"Execution output:\n{live_output}",
        ]

        if arguments.get("promote"):
            if not arguments.get("promote_confirm", False):
                sections.append(
                    "Promotion was requested. Re-run with promote_confirm=true to invoke promote.py "
                    "after a successful execution."
                )
                return CallToolResult(
                    content=[TextContent(type="text", text="\n\n".join(sections))]
                )

            # Use vigil CLI for promotion
            input_dir_raw = arguments.get("promotion_input_dir", "app/code/artifacts")
            output_dir_raw = arguments.get("promotion_output_dir", "app/code/receipts")
            input_dir, input_error = _sanitize_directory(str(input_dir_raw), description="promotion input dir")
            if input_error:
                sections.append(input_error)
                return CallToolResult(content=[TextContent(type="text", text="\n\n".join(sections))])
            output_dir, output_error = _sanitize_directory(str(output_dir_raw), description="promotion output dir")
            if output_error:
                sections.append(output_error)
                return CallToolResult(content=[TextContent(type="text", text="\n\n".join(sections))])

            promote_cmd = [
                "vigil",
                "promote",
                "--in",
                input_dir,
                "--out",
                output_dir,
            ]
            promote_result = run_command(promote_cmd)
            promote_output = promote_result.merged_output()
            if not promote_result.ok:
                sections.append(f"Promotion failed:\n{promote_output}")
            else:
                sections.append(f"Promotion output:\n{promote_output}")

        return CallToolResult(content=[TextContent(type="text", text="\n\n".join(sections))])

    if name == "promote":
        if not arguments.get("confirm", False):
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=(
                            "Promotion requires explicit confirmation. "
                            "Re-run with confirm=true after verifying outputs."
                        ),
                    )
                ]
            )
        input_dir_raw = arguments.get("input_dir", "app/code/artifacts")
        output_dir_raw = arguments.get("output_dir", "app/code/receipts")
        input_dir, input_error = _sanitize_directory(str(input_dir_raw), description="input dir")
        if input_error:
            return CallToolResult(content=[TextContent(type="text", text=input_error)])
        output_dir, output_error = _sanitize_directory(str(output_dir_raw), description="output dir")
        if output_error:
            return CallToolResult(content=[TextContent(type="text", text=output_error)])

        # Use vigil CLI for promotion
        promote_cmd = [
            "vigil",
            "promote",
            "--in",
            input_dir,
            "--out",
            output_dir,
        ]
        result = run_command(promote_cmd)
        message = (
            "Promotion succeeded:\n" + result.merged_output()
            if result.ok
            else "Promotion failed:\n" + result.merged_output()
        )
        return CallToolResult(content=[TextContent(type="text", text=message)])

    if name == "preview_data":
        allowed, retry_after = _preview_rate_limiter.allow()
        if not allowed:
            wait_seconds = int(retry_after) + 1
            message = (
                "preview_data rate limit exceeded. "
                f"Try again in approximately {wait_seconds} second(s)."
            )
            return CallToolResult(content=[TextContent(type="text", text=message)])
        handle_raw = arguments.get("handle_path", "app/data/handles/data.parquet.dhandle.json")
        sanitized_handle, handle_error = _sanitize_handle_path(str(handle_raw))
        if handle_error:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Invalid handle path: {handle_error}")]
            )
        try:
            requested_limit = int(arguments.get("limit", 100))
        except (TypeError, ValueError):
            requested_limit = 100
        preview = _load_handle_rows(sanitized_handle, requested_limit)
        return CallToolResult(content=[TextContent(type="text", text=preview)])

    # ═══════════════════════════════════════════════════════════
    # APPLICATION LAYER - AI-powered operations
    # ═══════════════════════════════════════════════════════════

    if name == "ai_generate_pipeline":
        try:
            from vigil_ai import generate_pipeline
        except ImportError:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="vigil-ai not installed. Install with: pip install vigil-ai",
                    )
                ]
            )

        description = arguments.get("description", "")
        if not description:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: description is required")]
            )

        template = arguments.get("template", "genomics-starter")
        model = arguments.get("model")
        domain = arguments.get("domain")

        try:
            pipeline_content = generate_pipeline(
                description=description,
                template=template,
                model=model,
                domain=domain,
            )

            message = f"Generated Snakemake pipeline:\n\n```snakemake\n{pipeline_content}\n```"
            return CallToolResult(content=[TextContent(type="text", text=message)])

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error generating pipeline: {str(e)}")]
            )

    if name == "ai_debug_error":
        try:
            from vigil_ai import ai_debug
        except ImportError:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="vigil-ai not installed. Install with: pip install vigil-ai",
                    )
                ]
            )

        error_message = arguments.get("error_message", "")
        if not error_message:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: error_message is required")]
            )

        context = arguments.get("context", {})
        model = arguments.get("model")

        try:
            debug_suggestions = ai_debug(
                error_message=error_message,
                context=context,
                model=model,
            )

            message = f"AI Debug Suggestions:\n\n{debug_suggestions}"
            return CallToolResult(content=[TextContent(type="text", text=message)])

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error debugging: {str(e)}")]
            )

    if name == "ai_optimize_workflow":
        try:
            from vigil_ai import ai_optimize
        except ImportError:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="vigil-ai not installed. Install with: pip install vigil-ai",
                    )
                ]
            )

        snakefile_path = Path(arguments.get("snakefile", "app/code/pipelines/Snakefile"))
        focus = arguments.get("focus")

        try:
            result = ai_optimize(snakefile=snakefile_path, focus=focus)
            suggestions = result.get("optimization_suggestions", "No suggestions")

            message = f"Optimization Suggestions:\n\n{suggestions}"
            return CallToolResult(content=[TextContent(type="text", text=message)])

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error optimizing workflow: {str(e)}")]
            )

    if name == "ai_generate_step":
        try:
            from vigil_ai.generator import generate_step_script
        except ImportError:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="vigil-ai not installed. Install with: pip install vigil-ai",
                    )
                ]
            )

        description = arguments.get("description", "")
        if not isinstance(description, str) or not description.strip():
            return CallToolResult(
                content=[TextContent(type="text", text="Error: description is required")]
            )

        rule_name = str(arguments.get("rule_name", "") or "")

        def _normalize_list(value: Any) -> list[str]:
            if isinstance(value, str):
                return [value]
            if isinstance(value, Iterable):  # type: ignore[arg-type]
                return [str(item) for item in value]
            return []

        inputs = _normalize_list(arguments.get("inputs"))
        outputs = _normalize_list(arguments.get("outputs"))
        language = str(arguments.get("language", "python") or "python")
        model = arguments.get("model")

        try:
            script = generate_step_script(
                description=description,
                rule_name=rule_name,
                inputs=inputs,
                outputs=outputs,
                language=language,
                model=str(model) if model else None,
                domain=None,
            )
        except Exception as exc:  # noqa: BLE001 - bubble up model errors
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error generating step: {exc}")]
            )

        header = f"Generated {language} step script"
        if rule_name:
            header += f" for rule '{rule_name}'"
        message = f"{header}:\n\n```{language}\n{script}\n```"
        return CallToolResult(content=[TextContent(type="text", text=message)])

    if name == "ai_list_models":
        try:
            from vigil_ai import list_models
        except ImportError:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="vigil-ai not installed. Install with: pip install vigil-ai",
                    )
                ]
            )

        try:
            models = list_models()
            message = "Available foundation models:\n\n" + "\n".join(f"  - {model}" for model in models)
            return CallToolResult(content=[TextContent(type="text", text=message)])

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listing models: {str(e)}")]
            )

    if name == "ai_get_model_info":
        try:
            from vigil_ai import get_model
        except ImportError:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="vigil-ai not installed. Install with: pip install vigil-ai",
                    )
                ]
            )

        model_name = arguments.get("model")
        if not model_name:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: model name is required")]
            )

        try:
            model = get_model(name=model_name)
            metadata = model.get_metadata()

            info = f"""Model: {metadata.display_name}
Name: {metadata.name}
Domain: {metadata.domain}
Capabilities: {', '.join(str(c) for c in metadata.capabilities)}
Description: {metadata.description}
Parameters: {metadata.parameters if metadata.parameters else 'N/A'}
Requires GPU: {metadata.requires_gpu}
License: {metadata.license or 'N/A'}
"""
            return CallToolResult(content=[TextContent(type="text", text=info)])

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting model info: {str(e)}")]
            )

    # Should not be reachable thanks to ALLOWED_VERBS check
    return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])


@app.call_tool()
async def _call_tool_handler(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Adapter that returns raw content blocks for the MCP transport."""

    result = await call_tool(name, arguments)
    return [content for content in result.content if isinstance(content, TextContent)]


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="scientific-workflow",
                server_version="0.2.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
