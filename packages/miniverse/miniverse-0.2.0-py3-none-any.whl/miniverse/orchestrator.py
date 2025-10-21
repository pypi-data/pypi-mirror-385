"""
Main simulation orchestrator.

Fully decoupled from file I/O, database, and config.
All dependencies are injected by the user.

Coordinates the simulation loop:
1. Apply deterministic physics (if simulation_rules provided)
2. Build agent perceptions (partial observability)
3. Gather agent actions in parallel (LLM calls)
4. Process world update (World Engine LLM call)
5. Persist via injected strategy
6. Update agent memories via injected strategy
"""

import asyncio
import os
from typing import Any, Callable, List, Dict, Optional
from uuid import UUID, uuid4

from .perception import build_agent_perception
from .llm_calls import process_world_update
from .schemas import AgentProfile, WorldState, AgentAction, AgentMemory
from .simulation_rules import SimulationRules, format_resources_generic
from .persistence import PersistenceStrategy, InMemoryPersistence
from .memory import MemoryStrategy, SimpleMemoryStream
from .logging_utils import (
    colored,
    Color,
    LOG_TAG_DETERMINISTIC,
    LOG_TAG_LLM,
    LOG_TAG_SUCCESS,
)
from .cognition import (
    AgentCognition,
    AgentCognitionMap,
    PromptContext,
    build_default_cognition,
    build_prompt_context,
    DEFAULT_PROMPTS,
    LLMPlanner,
    LLMExecutor,
    LLMReflectionEngine,
)
from .cognition.cadence import PLANNER_LAST_TICK_KEY, REFLECTION_LAST_TICK_KEY
from .cognition.planner import Plan, PlanStep


# =============================
# Module-level Exceptions
# =============================

class AgentActionsFailedError(Exception):
    """Raised when one or more agent actions fail during a tick.

    Contains a mapping of agent_id to the underlying exception for better
    diagnostics, along with guidance on common remediation steps.
    """

    def __init__(self, *, tick: int, errors: Dict[str, Exception]) -> None:
        self.tick = tick
        self.errors = errors
        message_lines = [
            f"One or more agent actions failed at tick {tick}.",
            "Agents that failed:",
        ]
        for agent_id, exc in errors.items():
            message_lines.append(f"  - {agent_id}: {exc}")
        message_lines.extend(
            [
                "\nRemediation tips:",
                "  - Verify LLM configuration (LLM_PROVIDER, LLM_MODEL, API key)",
                "  - Enable DEBUG_LLM=true to inspect prompts/responses",
                "  - Enable DEBUG_PERCEPTION=true to inspect agent inputs",
                "  - Enable MINIVERSE_VERBOSE=true to see reasoning",
            ]
        )
        super().__init__("\n".join(message_lines))


class WorldEngineUnavailableError(Exception):
    """Raised when World Engine LLM is not configured but required."""

    def __init__(self, *, tick: int, reason: str) -> None:
        self.tick = tick
        self.reason = reason
        message = (
            f"World Engine unavailable at tick {tick}: {reason}\n\n"
            "Remediation tips:\n"
            "  - Set LLM_PROVIDER and LLM_MODEL environment variables\n"
            "  - Ensure API key env var is set for your provider\n"
            "  - DEBUG_LLM=true to inspect prompts/responses if still failing"
        )
        super().__init__(message)


class WorldEngineValidationError(Exception):
    """Raised when World Engine LLM response fails validation after retries."""

    def __init__(self, *, tick: int, underlying: Exception) -> None:
        self.tick = tick
        self.underlying = underlying
        message = (
            f"World Engine validation failed at tick {tick}: {underlying}\n\n"
            "The LLM response remained invalid after retries.\n"
            "Remediation tips:\n"
            "  - DEBUG_LLM=true to inspect prompts and validation feedback\n"
            "  - Review world prompt and response schema\n"
            "  - Consider simplifying the request or adjusting constraints"
        )
        super().__init__(message)


class Orchestrator:
    """
    Main simulation orchestrator.

    Fully decoupled - accepts all dependencies as parameters.
    No file I/O, no database requirement, no global config.
    """

    def __init__(
        self,
        world_state: WorldState,
        agents: Dict[str, AgentProfile],
        world_prompt: str,
        agent_prompts: Dict[str, str],
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        simulation_rules: Optional[SimulationRules] = None,
        world_update_mode: str = "auto",
        persistence: Optional[PersistenceStrategy] = None,
        memory: Optional[MemoryStrategy] = None,
        agent_cognition: Optional[AgentCognitionMap] = None,
        tick_listeners: Optional[
            List[Callable[[int, WorldState, WorldState, List[AgentAction]], None]]
        ] = None,
    ):
        """Initialize orchestrator with all dependencies injected.

        Args:
            world_state: Initial WorldState
            agents: Dict mapping agent_id to AgentProfile
            world_prompt: System prompt for world engine
            agent_prompts: Dict mapping agent_id to system prompt
            llm_provider: Optional LLM provider name (e.g., "openai", "anthropic")
            llm_model: Optional model identifier (e.g., "gpt-5-nano")
            simulation_rules: Optional SimulationRules for deterministic physics
            persistence: Optional persistence strategy (defaults to InMemory)
            memory: Optional memory strategy (defaults to SimpleMemoryStream)
            agent_cognition: Optional mapping of agent_id to AgentCognition;
                defaults provide empty planner/executor/reflection stacks.
            tick_listeners: Optional callables invoked after each tick for
                additional analysis or logging. Each listener receives
                (tick, previous_state, new_state, actions).
        """
        self.current_state = world_state
        self.agents = agents
        self.world_prompt = world_prompt
        self.agent_prompts = agent_prompts
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.simulation_rules = simulation_rules
        self.world_update_mode = world_update_mode  # 'auto' | 'deterministic' | 'llm'
        self._world_llm_warning_emitted = False

        # Use defaults if strategies not provided. InMemoryPersistence is fastest for
        # prototyping but data is lost after run. SimpleMemoryStream uses the same
        # persistence backend to store and retrieve memories with recency-based filtering.
        self.persistence = persistence or InMemoryPersistence()
        self.memory = memory or SimpleMemoryStream(self.persistence)

        # Prepare cognition modules per agent. Each agent gets a bundle containing
        # planner (generates multi-step plans), executor (chooses tick actions),
        # reflection engine (periodically summarizes experiences), and scratchpad
        # (working memory for plan state). If user doesn't provide custom cognition,
        # build_default_cognition() returns simple deterministic implementations.
        cognition_map: AgentCognitionMap = {}
        for agent_id in agents:
            if agent_cognition and agent_id in agent_cognition:
                # User provided custom cognition for this agent
                cognition_map[agent_id] = agent_cognition[agent_id]
            else:
                # Fall back to default cognition (deterministic, no-op reflection)
                cognition_map[agent_id] = build_default_cognition()
        self.agent_cognition: AgentCognitionMap = cognition_map

        # Tick listeners are optional callbacks invoked after each tick completes.
        # They receive (tick, previous_state, new_state, actions) for analysis/logging.
        self.tick_listeners = tick_listeners or []

        # Give simulation rules a chance to modify initial state (e.g., compute
        # derived metrics, initialize tracking structures). Not all rules need this.
        if self.simulation_rules:
            self.current_state = self.simulation_rules.on_simulation_start(
                self.current_state
            )

        # Generate unique ID for this simulation run. All persistence/memory operations
        # tag data with this ID so multiple runs can coexist in the same backend.
        self.run_id: UUID = uuid4()

        # Preflight cache for one-time warnings per template
        self._prompt_warnings_emitted: Dict[str, bool] = {}

    # (no inner exception classes)

    def _get_scratchpad_state(self, cognition: AgentCognition) -> dict:
        """Safely get scratchpad state dict (returns empty dict if scratchpad is None)."""
        if cognition.scratchpad is None:
            return {}
        return cognition.scratchpad.state

    def _resolve_agent_id(self, name_or_id: str) -> Optional[str]:
        """
        Map agent name or ID to agent_id.

        LLMs naturally use agent names ("Ayesha Khan") in communications,
        but our agent dictionary is keyed by agent_id ("ayesha").
        This helper resolves both formats.

        Args:
            name_or_id: Either agent_id ("ayesha") or display name ("Ayesha Khan")

        Returns:
            Agent ID if found, None otherwise
        """
        # Check if already an agent_id
        if name_or_id in self.agents:
            return name_or_id

        # Search by display name
        for agent_id, profile in self.agents.items():
            if profile.name == name_or_id:
                return agent_id

        return None

    def _preflight_prompt_templates(self) -> None:
        """Warn once per missing template before the tick loop starts.

        Checks planner/executor/reflection template names requested by each agent's
        cognition. If a named template is missing from the configured prompt library,
        logs a one-time warning and indicates which default will be used instead.
        """
        for agent_id, cognition in self.agent_cognition.items():
            library = cognition.prompt_library or DEFAULT_PROMPTS

            # Planner
            if isinstance(cognition.planner, LLMPlanner):
                planner_obj = cognition.planner
                name = getattr(planner_obj, "template_name", None)
                # One-time notice: using default template
                if getattr(planner_obj, "template", None) is None and (name is None or name == "plan") and library is DEFAULT_PROMPTS:
                    key = f"planner_default:{agent_id}"
                    if not self._prompt_warnings_emitted.get(key):
                        print(f"  [Prompts] Agent '{agent_id}' planner using default template 'plan'.")
                        self._prompt_warnings_emitted[key] = True
                # Missing named template warning
                if name and name not in library.templates and not self._prompt_warnings_emitted.get(f"planner_missing:{name}"):
                    print(f"  [Prompts] Agent '{agent_id}' planner template '{name}' not found; using default 'plan'.")
                    self._prompt_warnings_emitted[f"planner_missing:{name}"] = True

            # Executor
            if isinstance(cognition.executor, LLMExecutor):
                exec_obj = cognition.executor
                name = getattr(exec_obj, "template_name", None)
                # One-time notice: using default template
                if getattr(exec_obj, "template", None) is None and (name is None or name in ("default", "execute_tick")) and library is DEFAULT_PROMPTS:
                    key = f"executor_default:{agent_id}"
                    if not self._prompt_warnings_emitted.get(key):
                        print(f"  [Prompts] Agent '{agent_id}' executor using default template '{'default' if name in (None, 'default') else name}'.")
                        self._prompt_warnings_emitted[key] = True
                # Missing named template warning
                if name and name not in library.templates and not self._prompt_warnings_emitted.get(f"executor_missing:{name}"):
                    print(f"  [Prompts] Agent '{agent_id}' executor template '{name}' not found; using default 'default'.")
                    self._prompt_warnings_emitted[f"executor_missing:{name}"] = True

            # Reflection
            if isinstance(cognition.reflection, LLMReflectionEngine):
                refl_obj = cognition.reflection
                name = getattr(refl_obj, "template_name", None)
                # One-time notice: using default template
                if getattr(refl_obj, "template", None) is None and (name is None or name == "reflect_diary") and library is DEFAULT_PROMPTS:
                    key = f"reflection_default:{agent_id}"
                    if not self._prompt_warnings_emitted.get(key):
                        print(f"  [Prompts] Agent '{agent_id}' reflection using default template 'reflect_diary'.")
                        self._prompt_warnings_emitted[key] = True
                # Missing named template warning
                if name and name not in library.templates and not self._prompt_warnings_emitted.get(f"reflection_missing:{name}"):
                    print(f"  [Prompts] Agent '{agent_id}' reflection template '{name}' not found; using default 'reflect_diary'.")
                    self._prompt_warnings_emitted[f"reflection_missing:{name}"] = True

    def _describe_world_update_mode(self) -> str:
        """Return a one-line summary of the selected world update mode and reason."""
        mode = self.world_update_mode
        rules = self.simulation_rules
        if mode == "deterministic":
            if rules and getattr(rules, "process_actions").__func__ is not SimulationRules.process_actions:
                return "[Preflight] World updates: deterministic (rules.process_actions)"
            return "[Preflight] World updates: deterministic (basic)"
        if mode == "llm":
            return "[Preflight] World updates: LLM (fail-fast if misconfigured)"
        # auto mode
        if rules and getattr(rules, "process_actions").__func__ is not SimulationRules.process_actions:
            return "[Preflight] World updates (auto): deterministic via rules.process_actions"
        if self.llm_provider and self.llm_model:
            return "[Preflight] World updates (auto): LLM"
        return "[Preflight] World updates (auto): deterministic (basic)"

    def _set_scratchpad_value(self, cognition: AgentCognition, key: str, value: Any) -> None:
        """Safely set scratchpad value (no-op if scratchpad is None)."""
        if cognition.scratchpad is not None:
            cognition.scratchpad.state[key] = value

    def _get_scratchpad_value(self, cognition: AgentCognition, key: str, default: Any = None) -> Any:
        """Safely get scratchpad value (returns default if scratchpad is None)."""
        if cognition.scratchpad is None:
            return default
        return cognition.scratchpad.state.get(key, default)

    async def run(self, num_ticks: int) -> Dict:
        """Run simulation for N ticks.

        Args:
            num_ticks: Number of ticks to simulate

        Returns:
            Dict with run_id and final_state

        Raises:
            Exception: If simulation fails
        """
        # Initialize persistence and memory backends. Each backend (InMemory, JSON, Postgres)
        # may need setup (e.g., opening DB connections, creating directories). Initialization
        # is idempotent - safe to call multiple times.
        await self.persistence.initialize()
        await self.memory.initialize()

        try:
            # Save initial state at tick 0. This establishes baseline for debugging and allows
            # users to rewind simulations. All persistence operations tag data with run_id so
            # multiple simulation runs can coexist in the same backend.
            await self.persistence.save_state(self.run_id, 0, self.current_state)

            print(f"Starting simulation run {self.run_id}")
            print(f"Agents: {len(self.agents)}, Ticks: {num_ticks}\n")

            # Preflight: warn early if requested prompt templates are missing
            self._preflight_prompt_templates()

            # Preflight: report world update mode
            print(self._describe_world_update_mode())

            # Main simulation loop. Each tick is independent - if one tick fails, we propagate
            # the exception immediately rather than continuing with corrupted state.
            ticks_completed = 0
            stopped_early = False
            for tick in range(1, num_ticks + 1):
                print(f"=== Tick {tick}/{num_ticks} ===")

                try:
                    await self._run_tick(tick)
                except Exception as e:
                    print(f"ERROR at tick {tick}: {e}")
                    raise

                ticks_completed = tick

                if self.simulation_rules and self.simulation_rules.should_stop(
                    self.current_state, tick
                ):
                    stopped_early = True
                    print(
                        f"\nSimulation stopped early at tick {tick} (signaled by simulation rules)."
                    )
                    break

            # Give simulation rules a chance to compute final statistics, aggregate metrics,
            # or clean up tracking structures. Not all rules need this hook.
            if self.simulation_rules:
                self.current_state = self.simulation_rules.on_simulation_end(
                    self.current_state, ticks_completed
                )

            if stopped_early:
                print("\nSimulation finished early (simulation rules signaled stop).")
            else:
                print("\n✅ Simulation complete!")

            return {"run_id": self.run_id, "final_state": self.current_state}

        finally:
            # Always cleanup persistence and memory backends even if simulation fails.
            # Ensures DB connections are closed, file handles released, etc.
            await self.persistence.close()
            await self.memory.close()

    async def _run_tick(self, tick: int) -> None:
        """Execute single tick.

        Args:
            tick: Current tick number
        """
        # Preserve previous state for tick listeners. Listeners compare before/after states
        # to detect emergent patterns, compute metrics, or trigger custom events.
        previous_state = self.current_state

        # 0. Apply deterministic physics FIRST (if simulation_rules provided).
        # Physics runs BEFORE agent actions to ensure agents perceive the consequences of
        # previous tick's physics. Example: resource consumption, environmental decay,
        # scheduled events. Physics is pure Python (fast, testable, deterministic).
        if self.simulation_rules:
            print(colored(f"  {LOG_TAG_DETERMINISTIC} [Physics] Applying deterministic rules for tick {tick}...", Color.BLUE))
            self.current_state = self.simulation_rules.apply_tick(
                self.current_state, tick
            )
            print(colored(f"  {LOG_TAG_SUCCESS} [Physics] Physics applied", Color.GREEN))

        # 1. Gather agent actions in parallel. Each agent gets partial observability based on
        # their location and access rights. Running in parallel minimizes total LLM latency
        # (critical for large agent populations). Each agent's cognition stack independently
        # builds perceptions, retrieves memories, generates/advances plans, and selects actions.
        actions = await self._gather_agent_actions(tick)

        # 2. World engine processes all actions and returns updated state. The world engine
        # uses an LLM to resolve action conflicts, apply narrative consistency, and generate
        # emergent events. If LLM fails validation after retries, we fall back to deterministic
        # physics to prevent simulation crashes.
        new_state = await self._process_world_update(tick, actions)

        # 3. Persist tick data (state, actions, memories) to backend. Persistence happens
        # AFTER the world engine succeeds so we never save partial/corrupt data. Memory
        # creation includes reflection engine invocations for agents that hit their cadence.
        await self._persist_tick(tick, new_state, actions)

        # 4. Print human-readable summary for monitoring. Shows resource levels, agent actions,
        # and recent events. Helps users understand simulation progress without reading logs.
        self._print_tick_summary(tick, actions, new_state)

        # 5. Update current state to serve as baseline for next tick. This happens AFTER
        # persistence to avoid race conditions between tick listeners and the next tick.
        self.current_state = new_state

        # 6. Invoke tick listeners for optional analysis/debugging. Listeners receive
        # (tick, prev_state, new_state, actions) to compute custom metrics, detect anomalies,
        # or trigger external integrations (e.g., logging to analytics platforms).
        # Listener failures are logged but don't crash the simulation.
        if self.tick_listeners:
            for listener in self.tick_listeners:
                try:
                    listener(tick, previous_state, new_state, actions)
                except Exception as exc:  # pragma: no cover - diagnostic hook
                    print(f"  [Analysis] Listener failed: {exc}")

    async def _gather_agent_actions(self, tick: int) -> List[AgentAction]:
        """Get all agent actions in parallel.

        Args:
            tick: Current tick number

        Returns:
            List of agent actions
        """
        # Build perceptions and gather actions in parallel. Each agent's action decision is
        # independent (no coordination) so we run all agents concurrently to minimize total
        # LLM latency. With N agents and ~2s LLM latency, parallel execution takes ~2s total
        # vs ~2N seconds sequential.
        tasks = []
        for agent_id, profile in self.agents.items():
            task = self._get_single_agent_action(agent_id, tick)
            tasks.append((agent_id, task))

        # Execute all agent queries in parallel. return_exceptions=True ensures one agent's
        # failure doesn't crash the entire tick - we handle failures individually below.
        results = await asyncio.gather(
            *[task for _, task in tasks], return_exceptions=True
        )

        # Fail-fast: if any agent action failed, raise an informative error with all failures.
        valid_actions: List[AgentAction] = []
        failures: Dict[str, Exception] = {}
        for i, result in enumerate(results):
            agent_id = tasks[i][0]
            if isinstance(result, Exception):
                failures[agent_id] = result
            else:
                valid_actions.append(result)

        if failures:
            raise AgentActionsFailedError(tick=tick, errors=failures)

        return valid_actions

    async def _get_single_agent_action(
        self, agent_id: str, tick: int
    ) -> AgentAction:
        """Get single agent's action decision.

        Args:
            agent_id: ID of agent
            tick: Current tick number

        Returns:
            AgentAction from LLM

        Raises:
            Exception: If LLM call fails
        """
        agent_name = self.agents[agent_id].name
        cognition = self.agent_cognition[agent_id]
        print(colored(f"  {LOG_TAG_DETERMINISTIC} [{agent_name}] Building perception...", Color.BLUE))

        # A2: Do not read messages from actions. Messages are sourced from memories.

        # Retrieve structured memory objects (AgentMemory instances) once.
        # We'll use these for both perception (as strings) and prompt context (as objects).
        # This eliminates the dual-fetch pattern that was confusing and inefficient.
        recent_agent_memories = await self.persistence.get_recent_memories(
            self.run_id, agent_id, limit=10
        )

        # Convert memories to strings for perception's recent_observations field.
        # Perception displays these in human-readable format for agent decision-making.
        recent_memory_strings = [m.content for m in recent_agent_memories]

        # Get debug flag once at top of function
        debug_memory = os.getenv("DEBUG_MEMORY")

        # DEBUG_MEMORY: Show what memories agent retrieved
        if debug_memory:
            print(colored(f"\n  [DEBUG_MEMORY] {agent_name} - Retrieved {len(recent_agent_memories)} memories:", Color.CYAN))
            for i, mem in enumerate(recent_agent_memories[:5], 1):  # Show first 5
                mem_preview = mem.content[:80] + "..." if len(mem.content) > 80 else mem.content
                print(colored(f"    {i}. [Tick {mem.tick}, Imp: {mem.importance}] {mem_preview}", Color.CYAN))
            if len(recent_agent_memories) > 5:
                print(colored(f"    ... and {len(recent_agent_memories) - 5} more", Color.CYAN))

        # Build direct messages for this agent from recent memories (recipient entries only)
        recent_messages: List[Dict[str, str]] = []
        for mem in recent_agent_memories:
            if mem.memory_type != "communication":
                continue
            role = (mem.metadata or {}).get("role")
            if role != "recipient":
                continue
            sender = (mem.metadata or {}).get("sender") or (mem.metadata or {}).get("sender_name") or "unknown"
            message_text = (mem.metadata or {}).get("message") or mem.content
            recent_messages.append({"from": sender, "message": message_text})

        # Build partial observability view (Stanford Generative Agents pattern).
        # Perception includes: agent's own status, messages to them, and memory context.
        perception = build_agent_perception(
            agent_id,
            self.current_state,
            recent_messages,
            recent_memory_strings,
        )

        if self.simulation_rules:
            try:
                perception = self.simulation_rules.customize_perception(
                    agent_id, perception, self.current_state
                )
            except Exception as exc:  # pragma: no cover - defensive
                raise RuntimeError(
                    f"SimulationRules.customize_perception raised an error for agent {agent_id}"
                ) from exc

        # DEBUG_PERCEPTION: Log what agent perceives (parallel to DEBUG_LLM)
        if os.getenv("DEBUG_PERCEPTION"):
            print(f"\n[DEBUG_PERCEPTION] {agent_name} (tick {tick})")
            print(f"  Recent memories ({len(recent_memory_strings)}):")
            for i, mem in enumerate(recent_memory_strings[:5], 1):  # Show first 5
                preview = mem[:80] + "..." if len(mem) > 80 else mem
                print(f"    {i}. {preview}")
            if len(recent_memory_strings) > 5:
                print(f"    ... and {len(recent_memory_strings) - 5} more")
            print(f"  Messages ({len(perception.messages)}):")
            for msg in perception.messages:
                preview = msg["message"][:60] + "..." if len(msg["message"]) > 60 else msg["message"]
                print(f"    - From {msg['from']}: {preview}")
            if not perception.messages:
                print(f"    (none)")
            print(f"  System alerts: {len(perception.system_alerts)}")
            print()

        # Use custom prompt library if agent's cognition provides one, otherwise fall back
        # to system defaults. Prompt library contains templates for planning, execution,
        # and reflection - allowing per-agent customization of reasoning styles.
        prompt_library = cognition.prompt_library or DEFAULT_PROMPTS

        # Assemble common metadata for all prompt contexts (planning, execution, reflection).
        # This avoids repeating the same data across multiple context builds.
        extra_common = {
            # First-turn only initial state prompt; otherwise empty
            "initial_state_agent_prompt": self.agent_prompts.get(agent_id, "") if tick == 1 else "",
            # Optional simulation instructions (system-level contract). If empty, template default applies
            "simulation_instructions": self.world_prompt or "",
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "prompt_library": prompt_library,
        }

        # Extract existing plan from scratchpad. Plan may be None (agent hasn't planned yet)
        # or Plan object (agent has active multi-step plan). We normalize to Plan() for
        # consistency - empty plans are valid (agent will rest or use heuristics).
        existing_plan = self._get_scratchpad_value(cognition, "plan")
        existing_plan_index = self._get_scratchpad_value(cognition, "plan_index", 0)
        if isinstance(existing_plan, Plan):
            initial_plan = existing_plan
        else:
            # No plan exists - use empty plan as placeholder
            initial_plan = Plan()
            existing_plan_index = 0

        # Summarize current plan state for planning context. Planner needs to see existing
        # plan to decide whether to refresh, extend, or keep current plan.
        planning_plan_state = self._plan_state_summary(initial_plan, existing_plan_index)

        # Build prompt context for planning. Planner receives full world state, perception,
        # memories, and current plan to generate/refresh multi-step plans. Context is
        # JSON-serializable for template rendering.
        planning_context = await build_prompt_context(
            agent_profile=self.agents[agent_id],
            perception=perception,
            world_state=self.current_state,
            scratchpad_state=self._get_scratchpad_state(cognition),
            plan_state=planning_plan_state,
            memories=recent_agent_memories,
            extra=extra_common,
        )

        # Ensure agent has valid plan. Planner cadence determines whether to generate fresh
        # plan or reuse existing. Returns (plan, current_step, step_index) tuple. Plan may
        # be empty if planner is deterministic or LLM unavailable.
        plan, plan_step, plan_index = await self._ensure_plan(
            agent_id, cognition, planning_context, tick
        )

        # Summarize updated plan state for execution context. Executor needs to see full
        # plan to coordinate actions with long-term goals.
        plan_state = self._plan_state_summary(plan, plan_index)

        # Build prompt context for execution. Executor receives same data as planner but
        # with updated plan state (in case planner just refreshed the plan).
        context = await build_prompt_context(
            agent_profile=self.agents[agent_id],
            perception=perception,
            world_state=self.current_state,
            scratchpad_state=self._get_scratchpad_state(cognition),
            plan_state=plan_state,
            memories=recent_agent_memories,
            extra=extra_common,
        )

        # Delegate action selection to executor. Executor considers current plan step,
        # perception, memories, and world state to choose concrete action (move, interact,
        # communicate, rest). Executor may deviate from plan if circumstances changed.
        # Choose appropriate tag based on executor capability
        executor_obj = cognition.executor
        uses_llm = False
        if hasattr(executor_obj, "uses_llm"):
            try:
                uses_llm = bool(executor_obj.uses_llm())  # type: ignore[attr-defined]
            except Exception:
                uses_llm = False
        else:
            # Fallback: detect known LLM executor type
            try:
                from .cognition.llm import LLMExecutor as _LLMExec
                uses_llm = isinstance(executor_obj, _LLMExec)
            except Exception:
                uses_llm = False

        exec_tag = LOG_TAG_LLM if uses_llm else LOG_TAG_DETERMINISTIC
        print(colored(f"  {exec_tag} [{agent_name}] Choosing action via executor...", Color.YELLOW))
        action = await cognition.executor.choose_action(
            agent_id,
            perception,
            cognition.scratchpad,  # Pass scratchpad directly (can be None)
            plan=plan,
            plan_step=plan_step,
            context=context,
        )

        # Show action details if verbose mode enabled
        if os.getenv("MINIVERSE_VERBOSE"):
            msg_preview = ""
            if action.communication and action.communication.get("message"):
                msg = action.communication["message"][:60]
                msg_preview = f'\n    Message: "{msg}..."' if len(action.communication["message"]) > 60 else f'\n    Message: "{msg}"'
            print(colored(f"    Reasoning: {action.reasoning[:80]}...", Color.CYAN))
            if msg_preview:
                print(colored(msg_preview, Color.CYAN))

        print(colored(f"  {LOG_TAG_SUCCESS} [{agent_name}] Got action: {action.action_type}", Color.GREEN))

        # Ensure agent_id matches the requesting agent. LLM may hallucinate wrong agent_id
        # or executor may use templates that don't populate it correctly. Overwriting here
        # prevents actions from being misattributed.
        action.agent_id = agent_id

        # Advance to next plan step after action executes. If plan is exhausted, wrap around
        # to step 0 (plans loop until planner refreshes). This keeps agents active rather
        # than blocking when plan completes.
        self._advance_plan(agent_id, cognition, plan)

        return action

    async def _process_world_update(
        self, tick: int, actions: List[AgentAction]
    ) -> WorldState:
        """World engine processes actions and returns new state.

        Args:
            tick: Current tick number
            actions: List of all agent actions this tick

        Returns:
            Updated WorldState from World Engine LLM

        Raises:
            Exception: If LLM call fails
        """
        # Tag world engine step based on mode/branch
        # Compute branch to tag the world update step
        has_rules_processor = bool(
            self.simulation_rules and getattr(self.simulation_rules, "process_actions").__func__ is not SimulationRules.process_actions
        )
        will_use_llm = (
            self.world_update_mode == "llm"
            or (
                self.world_update_mode == "auto"
                and not has_rules_processor
                and self.llm_provider
                and self.llm_model
            )
        )
        print(f"  [{'LLM' if will_use_llm else '•'}] [World Engine] Processing {len(actions)} actions...")
        mode = self.world_update_mode
        rules = self.simulation_rules

        # Helper to detect overridden process_actions
        has_rules_processor = bool(
            rules and getattr(rules, "process_actions").__func__ is not SimulationRules.process_actions
        )

        # Mode selection
        if mode == "deterministic":
            if has_rules_processor:
                return rules.process_actions(self.current_state, actions, tick)  # type: ignore[arg-type]
            return self._apply_deterministic_world_update(tick, actions)

        if mode == "llm":
            # Require LLM and call
            physics_applied = rules is not None
            if not self.llm_provider or not self.llm_model:
                raise WorldEngineUnavailableError(
                    tick=tick,
                    reason=(
                        "World Engine LLM is not configured (missing LLM_PROVIDER and/or LLM_MODEL). "
                        "Set provider/model and API key, or disable world engine usage."
                    ),
                )
            try:
                new_state = await process_world_update(
                    self.current_state,
                    actions,
                    tick,
                    self.world_prompt,
                    self.llm_provider,
                    self.llm_model,
                    physics_applied=physics_applied,
                )
            except Exception as exc:
                raise WorldEngineValidationError(tick=tick, underlying=exc)
            print(f"  [World Engine] ✓ World state updated")
            return new_state

        # auto mode
        if has_rules_processor:
            return rules.process_actions(self.current_state, actions, tick)  # type: ignore[arg-type]
        if self.llm_provider and self.llm_model:
            physics_applied = rules is not None
            try:
                new_state = await process_world_update(
                    self.current_state,
                    actions,
                    tick,
                    self.world_prompt,
                    self.llm_provider,
                    self.llm_model,
                    physics_applied=physics_applied,
                )
            except Exception as exc:
                raise WorldEngineValidationError(tick=tick, underlying=exc)
            print(f"  [World Engine] ✓ World state updated")
            return new_state
        # No LLM configured and no rules processor: basic deterministic
        return self._apply_deterministic_world_update(tick, actions)

    async def _persist_tick(
        self, tick: int, state: WorldState, actions: List[AgentAction]
    ) -> None:
        """Save tick data via persistence strategy.

        Args:
            tick: Current tick number
            state: New world state
            actions: Agent actions this tick
        """
        print(f"  [Persistence] Persisting tick {tick}...")
        await self.persistence.save_state(self.run_id, tick, state)

        # A4: Actions should not persist full communication content. Keep only minimal reference.
        sanitized_actions: List[AgentAction] = []
        for action in actions:
            comm = action.communication
            if comm:
                # Preserve only the recipient reference; drop message body from action history
                recipient = comm.get("to") if isinstance(comm, dict) else None
                if recipient is None:
                    recipient = "unknown"
                action = action.model_copy(update={"communication": {"to": recipient}})
            sanitized_actions.append(action)

        await self.persistence.save_actions(self.run_id, tick, sanitized_actions)
        await self._update_memories(tick, actions, state)
        print(f"  [Persistence] ✓ Tick {tick} persisted")

    async def _update_memories(
        self, tick: int, actions: List[AgentAction], state: WorldState
    ) -> None:
        """Create memory records for actions, communications, and events.

        Args:
            tick: Current tick number
            actions: Agent actions this tick
            state: New world state
        """
        import os
        debug_memory = os.getenv("DEBUG_MEMORY")

        if debug_memory:
            print(colored(f"\n  [DEBUG_MEMORY] Tick {tick} - Creating memories...", Color.CYAN))

        new_memories: Dict[str, List[AgentMemory]] = {}

        # Store actions as memories
        for action in actions:
            # Capture the action itself so downstream retrieval engines can filter by type/target.
            memory = await self.memory.add_memory(
                run_id=self.run_id,
                agent_id=action.agent_id,
                tick=tick,
                memory_type="action",
                content=f"I {action.action_type}: {action.reasoning}",
                importance=5,
                tags=[f"action:{action.action_type}"],
                metadata={
                    "target": action.target,
                    "parameters": action.parameters or {},
                    "reasoning": action.reasoning,
                },
            )
            new_memories.setdefault(action.agent_id, []).append(memory)

            # Store communications as memories FOR BOTH SENDER AND RECIPIENT
            if action.communication:
                recipient = action.communication.get("to", "unknown")
                message = action.communication.get("message") or action.communication.get("content", "")

                # Sender memory: "I told X: message"
                sender_memory = await self.memory.add_memory(
                    run_id=self.run_id,
                    agent_id=action.agent_id,
                    tick=tick,
                    memory_type="communication",
                    content=f"I told {recipient}: {message}",
                    importance=6,
                    tags=["communication", f"to:{recipient}"],
                    metadata={
                        "message": message,
                        "recipient": recipient,
                        "action_type": action.action_type,
                        "role": "sender",
                    },
                )
                new_memories.setdefault(action.agent_id, []).append(sender_memory)

                if debug_memory:
                    sender_name = self.agents[action.agent_id].name
                    msg_preview = message[:60] + "..." if len(message) > 60 else message
                    print(colored(f"    💬 {sender_name} → {recipient}: \"{msg_preview}\"", Color.CYAN))
                    print(colored(f"       Sender memory stored: \"I told {recipient}: ...\"", Color.CYAN))

                # RECIPIENT memory: "X told me: message"
                # This is the CRITICAL fix for information diffusion!
                # Recipients need to remember messages they received.

                # Map recipient name to agent_id (LLMs use names like "Ayesha Khan",
                # but our agent dict has keys like "ayesha")
                recipient_id = self._resolve_agent_id(recipient)

                if recipient_id and recipient_id != "unknown":
                    sender_name = self.agents[action.agent_id].name
                    recipient_memory = await self.memory.add_memory(
                        run_id=self.run_id,
                        agent_id=recipient_id,  # Use resolved agent_id, not raw name
                        tick=tick,
                        memory_type="communication",
                        content=f"{sender_name} told me: {message}",
                        importance=7,  # Slightly higher - receiving information is important
                        tags=["communication", f"from:{action.agent_id}"],
                        metadata={
                            "message": message,
                            "sender": action.agent_id,
                            "sender_name": sender_name,
                            "action_type": action.action_type,
                            "role": "recipient",
                        },
                    )
                    new_memories.setdefault(recipient_id, []).append(recipient_memory)

                    if debug_memory:
                        recipient_name = self.agents[recipient_id].name
                        print(colored(f"       Recipient memory stored: \"{recipient_name} received: ...\"", Color.CYAN))

        # Store events as observations for affected agents
        for event in state.recent_events:
            if event.tick == tick:  # Only new events
                for agent_id in event.affected_agents:
                    # Events may not have severity; default to 5 (medium importance)
                    importance = event.severity if event.severity is not None else 5

                    memory = await self.memory.add_memory(
                        run_id=self.run_id,
                        agent_id=agent_id,
                        tick=tick,
                        memory_type="observation",
                        content=event.description,
                        importance=importance,
                        tags=[
                            "event",
                            f"severity:{event.severity}" if event.severity is not None else "severity:unknown",
                            event.category,
                        ],
                        metadata={
                            "event_id": event.event_id,
                            "category": event.category,
                        },
                    )
                    new_memories.setdefault(agent_id, []).append(memory)

        await self._run_reflections(tick, new_memories)

    def _default_action(self, agent_id: str, tick: int) -> AgentAction:
        """Fallback action when agent fails.

        Args:
            agent_id: ID of agent
            tick: Current tick number

        Returns:
            Default rest action
        """
        return AgentAction(
            agent_id=agent_id,
            tick=tick,
            action_type="rest",
            target=None,
            parameters={},
            reasoning="System default: agent failed to respond",
            communication=None,
        )

    async def _ensure_plan(
        self,
        agent_id: str,
        cognition: AgentCognition,
        planning_context: PromptContext,
        tick: int,
    ) -> tuple[Plan, PlanStep | None, int]:
        """Ensure the agent has an active plan and return the current step.

        If planner is None (agent doesn't use planning), returns empty plan with no steps.
        Otherwise implements the planner cadence pattern - plans are refreshed periodically
        (e.g., once per day) rather than every tick, reducing LLM calls while maintaining
        long-term coherence. Cadence is configurable per agent via AgentCognition.
        """

        # If agent doesn't use planner, return empty plan (agent is purely reactive)
        if cognition.planner is None:
            return Plan(), None, 0

        # Extract existing plan from scratchpad. Plan may be None if agent never planned,
        # or Plan object if agent has active plan. We need to check type because scratchpad
        # stores arbitrary key-value pairs.
        plan_state = self._get_scratchpad_value(cognition, "plan")
        if isinstance(plan_state, Plan):
            plan = plan_state
        else:
            plan = None

        # Check cadence to determine if plan needs refresh. Cadence considers:
        # 1. Time elapsed since last plan (e.g., 24 ticks = 1 simulated day)
        # 2. Whether current plan is empty/expired
        # 3. Custom trigger conditions (scenario-specific)
        cadence = cognition.cadence.planner
        last_plan_tick = self._get_scratchpad_value(cognition, PLANNER_LAST_TICK_KEY)

        should_refresh = cadence.should_generate(
            tick=tick,
            last_run_tick=last_plan_tick,
            current_plan=plan,
        )

        if should_refresh:
            # Generate fresh plan via LLM or deterministic planner. Planner considers
            # agent's personality, current world state, recent memories, and existing plan
            # to produce coherent multi-step agenda. New plan replaces old plan entirely
            # (no merging) and resets plan_index to 0.
            plan = await cognition.planner.generate_plan(
                agent_id,
                cognition.scratchpad,  # Pass scratchpad directly (can be None)
                world_context=self.current_state,
                context=planning_context,
            )
            # Normalize non-Plan return values (shouldn't happen but defensive)
            if not isinstance(plan, Plan):
                plan = Plan()
            # Store new plan and reset index. Recording tick enables cadence tracking.
            self._set_scratchpad_value(cognition, "plan", plan)
            self._set_scratchpad_value(cognition, "plan_index", 0)
            self._set_scratchpad_value(cognition, PLANNER_LAST_TICK_KEY, tick)
        else:
            # Reuse existing plan. If plan somehow missing (shouldn't happen due to cadence
            # logic), create empty plan as safety net.
            if plan is None:  # safety net; shouldn't happen due to cadence
                plan = Plan()
                self._set_scratchpad_value(cognition, "plan", plan)
            # Ensure plan_index exists (default to 0 if missing)
            if self._get_scratchpad_value(cognition, "plan_index") is None:
                self._set_scratchpad_value(cognition, "plan_index", 0)

        # Extract current step from plan. If plan_index exceeds plan length (can happen if
        # plan was shortened), wrap to 0 to keep agent active. Empty plans return None step,
        # signaling executor to use fallback behavior (rest, wander, reactive actions).
        plan_index = self._get_scratchpad_value(cognition, "plan_index", 0)
        if plan.steps:
            if plan_index >= len(plan.steps):
                # Plan exhausted - wrap around to beginning to keep agent active
                plan_index = 0
                self._set_scratchpad_value(cognition, "plan_index", plan_index)
            plan_step = plan.steps[plan_index]
        else:
            # Empty plan - executor will use fallback logic
            plan_step = None

        return plan, plan_step, plan_index

    def _advance_plan(
        self, agent_id: str, cognition: AgentCognition, plan: Plan
    ) -> None:
        """Advance the plan index after an action executes.

        This implements sequential plan execution - agent moves to next step after each tick.
        When plan exhausts, wraps to step 0 to keep agent active. Alternative strategies
        (conditional branching, parallel steps) could be implemented by subclassing.
        """

        # No planning or empty plan - nothing to advance
        if cognition.planner is None or not plan.steps:
            return

        # Move to next step, or wrap to beginning if plan exhausted. Wrap-around prevents
        # agents from blocking when plan completes - they loop through plan until planner
        # refreshes with new agenda. This is appropriate for daily routines (wake -> eat ->
        # work -> sleep -> repeat) but not for project plans (may want to stop at end).
        plan_index = self._get_scratchpad_value(cognition, "plan_index", 0)
        if plan_index < len(plan.steps) - 1:
            # More steps remaining - advance to next step
            self._set_scratchpad_value(cognition, "plan_index", plan_index + 1)
        else:
            # Plan exhausted - wrap to beginning to maintain activity
            self._set_scratchpad_value(cognition, "plan_index", 0)

    @staticmethod
    def _plan_state_summary(plan: Plan, plan_index: int) -> Dict[str, Any]:
        return {
            "current_index": plan_index,
            "steps": [
                {"description": step.description, "metadata": step.metadata}
                for step in plan.steps
            ],
        }

    async def _run_reflections(
        self, tick: int, new_memories: Dict[str, List[AgentMemory]]
    ) -> None:
        """Invoke reflection engines for each agent.

        Stanford Generative Agents pattern: Periodically synthesize recent experiences into
        higher-level insights (e.g., "I'm running low on resources" from multiple actions).
        Reflections are stored as memories with elevated importance, making them more likely
        to influence future decisions.
        """

        for agent_id, cognition in self.agent_cognition.items():
            # Skip agents that don't use reflection
            if cognition.reflection is None:
                continue

            # Count new memories created this tick. Reflection cadence may trigger based on
            # memory accumulation (e.g., reflect after every 5 new experiences) rather than
            # fixed time intervals.
            new_memory_count = len(new_memories.get(agent_id, []))
            cadence = cognition.cadence.reflection
            last_reflection_tick = self._get_scratchpad_value(cognition, REFLECTION_LAST_TICK_KEY)

            # Check if reflection should trigger. Cadence considers both time elapsed and
            # memory count to balance insight generation with LLM cost. Skip if not ready.
            if not cadence.should_reflect(
                tick=tick,
                last_run_tick=last_reflection_tick,
                new_memories=new_memory_count,
            ):
                continue

            # Retrieve larger memory window (20 vs 10) for reflection. Reflections synthesize
            # longer-term patterns, so need broader historical context than tick actions.
            recent_memories = await self.persistence.get_recent_memories(
                self.run_id, agent_id, limit=20
            )

            prompt_library = cognition.prompt_library or DEFAULT_PROMPTS

            # Convert first 10 memories to strings for perception's recent_observations.
            # Reflection uses broader window (20) for context but perception shows recent subset.
            recent_memory_strings = [m.content for m in recent_memories[:10]]

            # Build minimal perception for reflection. Reflections focus on internal state
            # (memories, plans, goals) rather than environment, so pass empty actions list.
            perception = build_agent_perception(
                agent_id,
                self.current_state,
                [],  # No direct messages needed for reflection context
                recent_memory_strings,
            )

            # Extract current plan for reflection context. Reflections may comment on plan
            # progress or suggest adjustments based on accumulated experiences.
            plan_obj = self._get_scratchpad_value(cognition, "plan")
            plan_index = self._get_scratchpad_value(cognition, "plan_index", 0)
            if not isinstance(plan_obj, Plan):
                plan_obj = Plan()
                plan_index = 0
            plan_state = self._plan_state_summary(plan_obj, plan_index)

            # Build prompt context for reflection. Reflection engine receives full memories,
            # current plan, and world state to generate synthesized insights.
            reflection_context = await build_prompt_context(
                agent_profile=self.agents[agent_id],
                perception=perception,
                world_state=self.current_state,
                scratchpad_state=self._get_scratchpad_state(cognition),
                plan_state=plan_state,
                memories=recent_memories,
                extra={
                    "llm_provider": self.llm_provider,
                    "llm_model": self.llm_model,
                    "prompt_library": prompt_library,
                },
            )

            # Invoke reflection engine. May return empty list if no interesting patterns
            # detected. Reflections are free-form text with importance scores (typically
            # higher than raw observations to influence future retrieval).
            reflections = await cognition.reflection.maybe_reflect(
                agent_id,
                cognition.scratchpad,  # Pass scratchpad directly (can be None)
                recent_memories,
                trigger_context={
                    "tick": tick,
                    "new_memories": new_memory_count,
                },
                context=reflection_context,
            )

            # Record reflection tick to prevent double-reflection same tick
            self._set_scratchpad_value(cognition, REFLECTION_LAST_TICK_KEY, tick)

            # Store reflections as memories. Reflections get memory_type="reflection" for
            # retrieval filtering and typically have elevated importance (6-10) vs actions (5).
            # High importance ensures reflections surface in future memory retrieval.
            for reflection in reflections:
                await self.memory.add_memory(
                    run_id=self.run_id,
                    agent_id=agent_id,
                    tick=tick,
                    memory_type="reflection",
                    content=reflection.content,
                    importance=reflection.importance,
                    metadata=reflection.metadata,
                )

    def _apply_deterministic_world_update(
        self, tick: int, actions: List[AgentAction]
    ) -> WorldState:
        """Clone the current state and apply basic deterministic updates.

        This is the fallback world update when LLM world engine fails validation or is
        unavailable. Applies minimal physics: update agent activities, process move actions,
        update occupancy tracking. Does NOT generate events, resolve conflicts, or apply
        narrative consistency - purely mechanical state updates.
        """

        # Deep copy current state to avoid mutating baseline. Pydantic model_copy ensures
        # nested objects (agents, locations, resources) are fully cloned.
        new_state = self.current_state.model_copy(deep=True)
        new_state.tick = tick
        # Clear recent_events since we're not generating new events in deterministic mode
        new_state.recent_events = []

        # Extract occupancy tracker from simulation rules if present. Occupancy prevents
        # multiple agents from occupying same location and enforces capacity limits.
        occupancy = getattr(self.simulation_rules, "occupancy", None)

        for action in actions:
            # Find agent's status object in world state. Status tracks location, activity,
            # resources, and other dynamic properties. Skip if agent not found (shouldn't happen).
            status = next((agent for agent in new_state.agents if agent.agent_id == action.agent_id), None)
            if status is None:
                continue

            # Record previous location before move for occupancy tracking
            previous_location = status.location
            # Update activity regardless of action type (move, interact, rest, etc.)
            status.activity = action.action_type

            # Process move actions: update location and occupancy. Other action types
            # (interact, rest, communicate) don't affect location.
            if action.action_type == "move" and action.target:
                target = action.target
                # No-op moves: if target equals current location, skip occupancy ops entirely
                if target == previous_location:
                    continue
                entered = True
                if occupancy is not None:
                    # Attempt to enter new location respecting capacity; if refused, keep agent in place
                    try:
                        entered = bool(occupancy.enter(target, action.agent_id))
                    except Exception:
                        entered = False
                    if entered and previous_location:
                        try:
                            occupancy.leave(previous_location, action.agent_id)
                        except Exception:
                            pass
                if entered:
                    status.location = target

        return new_state

    def _print_tick_summary(
        self, tick: int, actions: List[AgentAction], state: WorldState
    ) -> None:
        """Print human-readable tick summary.

        Args:
            tick: Current tick number
            actions: Agent actions this tick
            state: New world state
        """
        # Print resource levels
        resource_summary = (
            self.simulation_rules.format_resource_summary(state)
            if self.simulation_rules
            else format_resources_generic(state)
        )
        if resource_summary:
            print(f"  Resources: {resource_summary}")

        # Print agent actions (full details)
        for action in actions:
            agent = self.agents[action.agent_id]
            reasoning_text = action.reasoning if action.reasoning is not None else ""
            target_str = f" target={action.target}" if action.target is not None else ""
            params_str = f" params={action.parameters}" if action.parameters else ""
            comm_to = None
            if action.communication and isinstance(action.communication, dict):
                comm_to = action.communication.get("to")
            comm_str = f" comm.to={comm_to}" if comm_to else ""
            print(
                f"  {agent.name}: {action.action_type}{target_str}{params_str}{comm_str} - {reasoning_text}"
            )

        # Print events
        for event in state.recent_events:
            if event.tick == tick:
                print(f"  EVENT (severity {event.severity}): {event.description}")

        print()  # Blank line for readability
