from __future__ import annotations
import os
import asyncio
import inspect
import json
import re
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Type, Union
from pydantic import BaseModel, TypeAdapter

# silence noisy libs
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GRPC_SUPPRESS_LOGS"] = "1"
os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from .memory import Memory
from .tools import Tool, ToolCall, function_tool

# optional handoffs import
try:
    from .handoffs import Handoff, handoff as handoff_factory, RunContextWrapper
except Exception:
    class RunContextWrapper:
        def __init__(self, current_agent=None, target_agent=None, memory=None, steps=None, context=None):
            self.current_agent = current_agent
            self.target_agent = target_agent
            self.memory = memory
            self.steps = steps or []
            self.context = context

    Handoff = None
    def handoff_factory(agent):
        raise RuntimeError("Handoffs are not available; module not found.")

# optional guardrails
try:
    from .guardrails import run_input_guardrails, run_output_guardrails
except Exception:
    def run_input_guardrails(*args, **kwargs): return None
    def run_output_guardrails(*args, **kwargs): return None

from ..config import SDKConfig
from ..providers.gemini import GeminiProvider


BASE_SYSTEM_PROMPT = (
    "You are the ABZ Agent SDK runtime.\n"
    "When you need a TOOL, output ONLY a single JSON object on ONE line, with NO markdown/backticks/extra text:\n"
    '{"tool":"<name>","args":{...}}\n'
    "When replying to the user, DO NOT include any tool JSON—reply only with the final answer text.\n"
    "Use ONLY tool names exactly as given in the tools manifest."
)

InstructionsFn = Callable[[RunContextWrapper, "Agent"], Union[str, Awaitable[str]]]


class AgentResult:
    def __init__(self, content: str, steps: List[str], parsed: Any = None):
        self.content = content
        self.steps = steps
        self.parsed = parsed


class Agent:
    def __init__(
        self,
        *,
        name: str,
        instructions: Union[str, InstructionsFn],
        model: Optional[str] = "auto",
        tools: Optional[List[Union[Tool, Callable[..., Any]]]] = None,
        handoffs: Optional[List[Union["Agent", Handoff]]] = None,
        memory: Optional[Memory] = None,
        verbose: bool = False,
        max_iterations: Optional[int] = None,
        api_key: Optional[str] = None,
        validate_model: bool = False,
        include_experimental: bool = True,
        output_type: Optional[Type[Any]] = None,
        input_guardrails: Optional[Sequence[Any]] = None,
        output_guardrails: Optional[Sequence[Any]] = None,
    ) -> None:
        if not name:
            raise ValueError("Agent 'name' is required.")
        if not instructions or (isinstance(instructions, str) and not instructions.strip()):
            raise ValueError("Agent 'instructions' is required (string or function).")

        self.name = name
        self._instructions_src = instructions
        self.instructions: str = ""
        self.verbose = verbose
        # ✅ single-turn by default
        self.max_iterations = max_iterations if max_iterations is not None else 1
        self.memory = memory or Memory()
        self.output_type = output_type
        self._type_adapter = TypeAdapter(output_type) if output_type else None
        self.input_guardrails = list(input_guardrails or [])
        self.output_guardrails = list(output_guardrails or [])

        self.model = self._resolve_model_param(
            model=model,
            include_experimental=include_experimental,
            validate_model=validate_model,
        )

        # tools
        self.tools = self._normalize_and_index_tools(tools or [])

        # handoffs
        self._handoffs: List[Handoff] = []
        for item in (handoffs or []):
            if Handoff is not None and isinstance(item, Handoff):
                self._handoffs.append(item)
            else:
                self._handoffs.append(handoff_factory(agent=item))
        for h in self._handoffs:
            ht = h.to_tool(self)
            self.tools[ht.name] = ht

        cfg_env = SDKConfig()
        resolved_key = api_key or cfg_env.api_key
        if not resolved_key:
            raise RuntimeError("GEMINI_API_KEY missing — set in env or .env")

        cfg = SDKConfig(
            model=self.model,
            api_key=resolved_key,
            temperature=cfg_env.temperature,
            max_iterations=self.max_iterations,
            verbose=self.verbose,
        )
        self.provider = GeminiProvider(cfg)

    # ---------------- PUBLIC ----------------

    def register_tool(self, tool: Union[Tool, Callable[..., Any]]) -> None:
        t = self._coerce_tool(tool, idx=-1)
        self.tools[t.name] = t

    class _AgentInvokeSchema(BaseModel):
        message: str

    def as_tool(self, *, tool_name: str, tool_description: str) -> Tool:
        outer = self

        class _AgentTool(Tool):
            name = tool_name
            description = tool_description
            schema = Agent._AgentInvokeSchema

            def run(self, **kwargs) -> str:
                msg = kwargs.get("message", "Please take over from here.")
                return outer.run(msg).content

        return _AgentTool()

    # ---------------- UPDATED run() ----------------
    def run(self, user_message: str, *, context: Any = None) -> AgentResult:
        steps: List[str] = []
        ctx_for_run = RunContextWrapper(
            current_agent=self,
            target_agent=self,
            memory=self.memory,
            steps=steps,
            context=context,
        )

        if self.input_guardrails:
            run_input_guardrails(
                guards=self.input_guardrails,
                ctx=ctx_for_run,
                agent=self,
                user_input=user_message,
            )

        self.memory.remember("user", user_message)

        # ✅ Single-turn fast mode
        if self.max_iterations <= 1:
            effective_instructions = self._resolve_instructions(ctx_for_run)
            prompt = self._build_prompt(user_message, effective_instructions=effective_instructions)
            model_out = self.provider.generate(prompt)

            model_out = self._normalize_output(model_out)
            steps.append(model_out)

            tool_call = self._maybe_parse_toolcall(model_out)
            if tool_call:
                obs = self._execute_tool(tool_call)
                self.memory.remember("tool", obs)
                return AgentResult(content=obs, steps=[model_out, obs])

            return AgentResult(content=model_out, steps=steps)

        # 🔁 Iterative mode
        for _i in range(self.max_iterations):
            effective_instructions = self._resolve_instructions(ctx_for_run)
            prompt = self._build_prompt(
                user_message if _i == 0 else "Continue.",
                effective_instructions=effective_instructions,
            )

            raw_out = self.provider.generate(prompt)
            model_out = self._normalize_output(raw_out)
            steps.append(model_out)

            tool_call = self._maybe_parse_toolcall(model_out)
            if tool_call:
                obs = self._execute_tool(tool_call)
                self.memory.remember("tool", obs)
                user_message = f"TOOL RESULT ({tool_call.tool}): {obs}"
                continue

            return AgentResult(content=model_out, steps=steps)

        fallback = "Reached iteration limit without final answer.\n\n" + (steps[-1] if steps else "")
        return AgentResult(content=fallback, steps=steps)

    # ---------------- INTERNAL HELPERS ----------------
    def _normalize_output(self, raw_out):
        if isinstance(raw_out, dict):
            return raw_out.get("content") or raw_out.get("text") or raw_out.get("message") or json.dumps(raw_out)
        elif hasattr(raw_out, "content"):
            return getattr(raw_out, "content")
        else:
            return str(raw_out)

    def _normalize_and_index_tools(self, tools_in: List[Union[Tool, Callable[..., Any]]]) -> Dict[str, Tool]:
        tools_dict: Dict[str, Tool] = {}
        for idx, raw in enumerate(tools_in):
            if isinstance(raw, Tool):
                name = getattr(raw, "name", None) or f"tool_{idx}"
                tools_dict[name] = raw
                continue
            if callable(raw):
                try:
                    wrapped = function_tool()(raw)
                    name = getattr(wrapped, "name", None) or getattr(raw, "__name__", f"tool_{idx}")
                    tools_dict[name] = wrapped
                    continue
                except Exception:
                    fn_name = getattr(raw, "__name__", f"tool_{idx}")

                    class _FallbackTool(Tool):
                        name = fn_name
                        description = f"Auto-wrapped tool for {fn_name}"
                        schema = None
                        def run(self, **kwargs) -> str:
                            try:
                                out = raw(**kwargs)
                                return out if isinstance(out, str) else str(out)
                            except Exception as e:
                                return f"[Tool Error] {e}"

                    tools_dict[_FallbackTool.name] = _FallbackTool()
        return tools_dict

    def _resolve_instructions(self, ctx: RunContextWrapper) -> str:
        src = self._instructions_src
        if isinstance(src, str):
            self.instructions = src
            return src
        fn = src
        if inspect.iscoroutinefunction(fn):
            try:
                return asyncio.run(fn(ctx, self))
            except RuntimeError:
                import nest_asyncio
                nest_asyncio.apply()
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(fn(ctx, self))
        else:
            text = fn(ctx, self)
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Dynamic instructions function must return non-empty string.")
            self.instructions = text
            return text

    def _execute_tool(self, call: ToolCall) -> str:
        tool = self.tools.get(call.tool)
        if not tool:
            return f"[Tool Error] Unknown tool: {call.tool}"
        try:
            kwargs = tool.parse_args(call.args)
            if self.verbose:
                print(f"Executing tool {call.tool} with kwargs={kwargs}")
            return tool.run(**kwargs)
        except Exception as e:
            return f"[Tool Error] {e}"

    def _build_prompt(self, user_message: str, *, effective_instructions: str) -> str:
        system = (
            f"{BASE_SYSTEM_PROMPT}\n\n"
            f"[AGENT NAME]: {self.name}\n"
            f"[INSTRUCTIONS]: {effective_instructions}\n"
            f"[MODEL]: {self.model}\n"
        )
        if self.tools:
            manifest = ["Available TOOLS:"]
            for n, t in self.tools.items():
                desc = (t.description or "").strip().replace("\n", " ")
                manifest.append(f"- {n}: {desc}")
            system += "\n" + "\n".join(manifest)

        history = self.memory.to_prompt()
        return f"[SYSTEM]: {system}\n\n{history}\n\n[USER]: {user_message}"

    def _maybe_parse_toolcall(self, text: str) -> Optional[ToolCall]:
        blob = _extract_json_blob(text.strip())
        if not blob:
            return None
        try:
            data = json.loads(blob)
            if isinstance(data, dict) and "tool" in data:
                args = data.get("args") or {}
                if not isinstance(args, dict):
                    args = {}
                return ToolCall(tool=str(data["tool"]), args=args)
        except Exception:
            return None
        return None

    def _resolve_model_param(self, *, model: Optional[str], include_experimental: bool, validate_model: bool) -> str:
        if not model or str(model).strip().lower() == "auto":
            return "gemini-2.0-flash"
        return str(model)


_JSON_OBJECT_OR_ARRAY = re.compile(r"(\{.*\}|\[.*\])", re.DOTALL)
def _extract_json_blob(text: str) -> Optional[str]:
    m = _JSON_OBJECT_OR_ARRAY.search(text.strip())
    if not m:
        return None
    return m.group(1)
