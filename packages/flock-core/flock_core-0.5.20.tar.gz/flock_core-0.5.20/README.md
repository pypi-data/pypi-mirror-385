<p align="center">
  <img alt="Flock Banner" src="docs/assets/images/flock.png" width="800">
</p>
<p align="center">
  <a href="https://whiteducksoftware.github.io/flock/" target="_blank"><img alt="Documentation" src="https://img.shields.io/badge/docs-online-blue?style=for-the-badge&logo=readthedocs"></a>
  <a href="https://pypi.org/project/flock-core/" target="_blank"><img alt="PyPI Version" src="https://img.shields.io/pypi/v/flock-core?style=for-the-badge&logo=pypi&label=pip%20version"></a>
  <img alt="Python Version" src="https://img.shields.io/badge/python-3.12%2B-blue?style=for-the-badge&logo=python">
  <a href="LICENSE" target="_blank"><img alt="License" src="https://img.shields.io/github/license/whiteducksoftware/flock?style=for-the-badge"></a>
  <a href="https://whiteduck.de" target="_blank"><img alt="Built by white duck" src="https://img.shields.io/badge/Built%20by-white%20duck%20GmbH-white?style=for-the-badge&labelColor=black"></a>
  <a href="https://codecov.io/gh/whiteducksoftware/flock" target="_blank"><img alt="Test Coverage" src="https://codecov.io/gh/whiteducksoftware/flock/branch/main/graph/badge.svg?token=YOUR_TOKEN_HERE&style=for-the-badge"></a>
  <img alt="Tests" src="https://img.shields.io/badge/tests-1300+-brightgreen?style=for-the-badge">
</p>

---

# Flock 0.5: Declarative Blackboard Multi-Agent Orchestration

> **Stop engineering prompts. Start declaring contracts.**

Flock is a production-focused framework for orchestrating AI agents through **declarative type contracts** and **blackboard architecture**—proven patterns from distributed systems, decades of experience with microservice architectures, and classical AI—now applied to modern LLMs.

**📖 [Read the full documentation →](https://whiteducksoftware.github.io/flock)**

**Quick links:**
- **[Getting Started](https://whiteducksoftware.github.io/flock/getting-started/installation/)** - Installation and first steps
- **[Tutorials](https://whiteducksoftware.github.io/flock/tutorials/)** - Step-by-step learning path
  - [Custom Engines: Emoji Vibes & Batch Brews](https://whiteducksoftware.github.io/flock/tutorials/custom-engines/)
  - [Custom Agent Components: Foreshadow & Hype](https://whiteducksoftware.github.io/flock/tutorials/custom-agent-components/)
- **[User Guides](https://whiteducksoftware.github.io/flock/guides/)** - In-depth feature documentation
- **[API Reference](https://whiteducksoftware.github.io/flock/reference/api/)** - Complete API documentation
- **[Roadmap](https://whiteducksoftware.github.io/flock/about/roadmap/)** - What's coming in v1.0
- **Architecture & Patterns:**
  - [Architecture Overview](docs/architecture.md) - System design and module organization
  - [Error Handling Patterns](docs/patterns/error_handling.md) - Production error handling guide
  - [Async Patterns](docs/patterns/async_patterns.md) - Async/await best practices

---

## The Problem With Current Approaches

Building production multi-agent systems today means dealing with:

**🔥 Prompt Engineering Hell**
```python

prompt = """You are an expert code reviewer. When you receive code, you should...
[498 more lines of instructions that the LLM ignores half the time]"""

# 500-line prompt that breaks when models update

# How do I know that there isn't an even better prompt? (you don't)
# -> proving 'best possible performance' is impossible
```

**🧪 Testing Nightmares**
```python
# How do you unit test this?
result = llm.invoke(prompt)  # Hope for valid JSON
data = json.loads(result.content)  # Crashes in production
```

**📐 Rigid topology and tight coupling**
```python
# Want to add a new agent? Rewrite the entire graph.
workflow.add_edge("agent_a", "agent_b")
workflow.add_edge("agent_b", "agent_c")
# Add agent_d? Start rewiring...
```

**💀 Single point of failure: Orchestrator dies? Everything dies.**
```python
# Orchestrator dies? Everything dies.
```

**🧠 God object anti-pattern:**
```python
# One orchestrator needs domain knowledge of 20+ agents to route correctly
# Orchestrator 'guesses' next agent based on a natural language description.
# Not suitable for critical systems.
```

These aren't framework limitations, they're **architectural choices** that don't scale.

These challenges are solvable—decades of experience with microservices have taught us hard lessons about decoupling, orchestration, and reliability. Let's apply those lessons!

---

## The Flock Approach

Flock takes a different path, combining two proven patterns:

### 1. Declarative Type Contracts (Not Prompts)

**Traditional approach:**
```python
prompt = """You are an expert software engineer and bug analyst. Your task is to analyze bug reports and provide structured diagnostic information.

INSTRUCTIONS:
1. Read the bug report carefully
2. Determine the severity level (must be exactly one of: Critical, High, Medium, Low)
3. Classify the bug category (e.g., "performance", "security", "UI", "data corruption")
4. Formulate a root cause hypothesis (minimum 50 characters)
5. Assign a confidence score between 0.0 and 1.0

OUTPUT FORMAT:
You MUST return valid JSON with this exact structure:
{
  "severity": "string (Critical|High|Medium|Low)",
  "category": "string",
  "root_cause_hypothesis": "string (minimum 50 characters)",
  "confidence_score": "number (0.0 to 1.0)"
}

VALIDATION RULES:
- severity: Must be exactly one of: Critical, High, Medium, Low (case-sensitive)
- category: Must be a single word or short phrase describing the bug type
- root_cause_hypothesis: Must be at least 50 characters long and explain the likely cause
- confidence_score: Must be a decimal number between 0.0 and 1.0 inclusive

EXAMPLES:
Input: "App crashes when user clicks submit button"
Output: {"severity": "Critical", "category": "crash", "root_cause_hypothesis": "Null pointer exception in form validation logic when required fields are empty", "confidence_score": 0.85}

Input: "Login button has wrong color"
Output: {"severity": "Low", "category": "UI", "root_cause_hypothesis": "CSS class override not applied correctly in the theme configuration", "confidence_score": 0.9}

IMPORTANT:
- Do NOT include any explanatory text before or after the JSON
- Do NOT use markdown code blocks (no ```json```)
- Do NOT add comments in the JSON
- Ensure the JSON is valid and parseable
- If you cannot determine something, use your best judgment
- Never return null values

Now analyze this bug report:
{bug_report_text}"""

result = llm.invoke(prompt)  # 500-line prompt that breaks when models update
# Then parse and hope it's valid JSON
data = json.loads(result.content)  # Crashes in production 🔥
```

**The Flock way:**
```python
@flock_type
class BugDiagnosis(BaseModel):
    severity: str = Field(pattern="^(Critical|High|Medium|Low)$")
    category: str = Field(description="Bug category")
    root_cause_hypothesis: str = Field(min_length=50)
    confidence_score: float = Field(ge=0.0, le=1.0)

# The schema IS the instruction. No 500-line prompt needed.
agent.consumes(BugReport).publishes(BugDiagnosis)
```

<p align="center">
  <img alt="Flock Banner" src="docs/assets/images/bug_diagnosis.png" width="1000">
</p>

**Why this matters:**
- ✅ **Survives model upgrades** - GPT-6 will still understand Pydantic schemas
- ✅ **Runtime validation** - Errors caught at parse time, not in production
- ✅ **Testable** - Mock inputs/outputs with concrete types
- ✅ **Self-documenting** - The code tells you what agents do

### 2. Blackboard Architecture (Not Directed Graphs)

**Graph-based approach:**
```python
# Explicit workflow with hardcoded edges
workflow.add_edge("radiologist", "diagnostician")
workflow.add_edge("lab_tech", "diagnostician")
# Add performance_analyzer? Rewrite the graph.
```

**The Flock way (blackboard):**
```python
# Agents subscribe to types, workflows emerge
radiologist = flock.agent("radiologist").consumes(Scan).publishes(XRayAnalysis)
lab_tech = flock.agent("lab_tech").consumes(Scan).publishes(LabResults)
diagnostician = flock.agent("diagnostician").consumes(XRayAnalysis, LabResults).publishes(Diagnosis)

# Add performance_analyzer? Just subscribe it:
performance = flock.agent("perf").consumes(Scan).publishes(PerfAnalysis)
# Done. No graph rewiring. Diagnostician can optionally consume it.
```

**What just happened:**
- ✅ **Parallel execution** - Radiologist and lab_tech run concurrently (automatic)
- ✅ **Dependency resolution** - Diagnostician waits for both inputs (automatic)
- ✅ **Loose coupling** - Agents don't know about each other, just data types
- ✅ **Scalable** - O(n) complexity, not O(n²) edges

**This is not a new idea.** Blackboard architecture has powered groundbreaking AI systems since the 1970s (Hearsay-II, HASP/SIAP, BB1). We're applying proven patterns to modern LLMs.

---

## Quick Start (60 Seconds)

```bash
pip install flock-core
export OPENAI_API_KEY="sk-..."
# Optional: export DEFAULT_MODEL (falls back to hard-coded default if unset)
export DEFAULT_MODEL="openai/gpt-4.1"
```

```python
import os
import asyncio
from pydantic import BaseModel, Field
from flock import Flock, flock_type

# 1. Define typed artifacts
@flock_type
class CodeSubmission(BaseModel):
    code: str
    language: str

@flock_type
class BugAnalysis(BaseModel):
    bugs_found: list[str]
    severity: str = Field(pattern="^(Critical|High|Medium|Low|None)$")
    confidence: float = Field(ge=0.0, le=1.0)

@flock_type
class SecurityAnalysis(BaseModel):
    vulnerabilities: list[str]
    risk_level: str = Field(pattern="^(Critical|High|Medium|Low|None)$")

@flock_type
class FinalReview(BaseModel):
    overall_assessment: str = Field(pattern="^(Approve|Approve with Changes|Reject)$")
    action_items: list[str]

# 2. Create the blackboard
flock = Flock(os.getenv("DEFAULT_MODEL", "openai/gpt-4.1"))

# 3. Agents subscribe to types (NO graph wiring!)
bug_detector = flock.agent("bug_detector").consumes(CodeSubmission).publishes(BugAnalysis)
security_auditor = flock.agent("security_auditor").consumes(CodeSubmission).publishes(SecurityAnalysis)

# AND gate: This agent AUTOMATICALLY waits for BOTH analyses before triggering
final_reviewer = flock.agent("final_reviewer").consumes(BugAnalysis, SecurityAnalysis).publishes(FinalReview)

# 4. Run with real-time dashboard
async def main():
    await flock.serve(dashboard=True)

asyncio.run(main())
```

**What happened:**
- Bug detector and security auditor ran **in parallel** (both consume CodeSubmission)
- Final reviewer **automatically waited** for both
- **Zero prompts written** - types defined the behavior
- **Zero graph edges** - subscriptions created the workflow
- **Full type safety** - Pydantic validates all outputs

---

## Core Concepts

### Typed Artifacts (The Vocabulary)

Every piece of data on the blackboard is a validated Pydantic model:

```python
@flock_type
class PatientDiagnosis(BaseModel):
    condition: str = Field(min_length=10)
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_treatment: list[str] = Field(min_length=1)
    follow_up_required: bool
```

**Benefits:**
- Runtime validation ensures quality
- Field constraints prevent bad outputs
- Self-documenting data structures
- Version-safe (types survive model updates)

### Agent Subscriptions (The Rules)

Agents declare what they consume and produce:

```python
analyzer = (
    flock.agent("analyzer")
    .description("Analyzes patient scans")  # Optional: improves multi-agent coordination
    .consumes(PatientScan)                   # What triggers this agent
    .publishes(PatientDiagnosis)             # What it produces
)
```

**Logic Operations (AND/OR Gates):**

Flock provides intuitive syntax for coordinating multiple input types:

```python
# AND gate: Wait for BOTH types before triggering
diagnostician = flock.agent("diagnostician").consumes(XRayAnalysis, LabResults).publishes(Diagnosis)
# Agent triggers only when both XRayAnalysis AND LabResults are available

# OR gate: Trigger on EITHER type (via chaining)
alert_handler = flock.agent("alerts").consumes(SystemAlert).consumes(UserAlert).publishes(Response)
# Agent triggers when SystemAlert OR UserAlert is published

# Count-based AND gate: Wait for MULTIPLE instances of the same type
aggregator = flock.agent("aggregator").consumes(Order, Order, Order).publishes(BatchSummary)
# Agent triggers when THREE Order artifacts are available

# Mixed counts: Different requirements per type
validator = flock.agent("validator").consumes(Image, Image, Metadata).publishes(ValidationResult)
# Agent triggers when TWO Images AND ONE Metadata are available
```

**What just happened:**
- ✅ **Natural syntax** - Code clearly expresses intent ("wait for 3 orders")
- ✅ **Order-independent** - Artifacts can arrive in any sequence
- ✅ **Latest wins** - If 4 As arrive but need 3, uses the 3 most recent
- ✅ **Zero configuration** - No manual coordination logic needed

**Advanced subscriptions unlock crazy powerful patterns:**

<p align="center">
  <img alt="Event Join" src="docs/assets/images/join.png" width="800">
</p>

```python
# 🎯 Predicates - Smart filtering (only process critical cases)
urgent_care = flock.agent("urgent").consumes(
    Diagnosis,
    where=lambda d: d.severity in ["Critical", "High"]  # Conditional routing!
)

# 📦 BatchSpec - Cost optimization (process 10 at once = 90% cheaper API calls)
payment_processor = flock.agent("payments").consumes(
    Transaction,
    batch=BatchSpec(size=25, timeout=timedelta(seconds=30))  # $5 saved per batch!
)

# 🔗 JoinSpec - Data correlation (match orders + shipments by ID)
customer_service = flock.agent("notifications").consumes(
    Order,
    Shipment,
    join=JoinSpec(by=lambda x: x.order_id, within=timedelta(hours=24))  # Correlated!
)

# 🏭 Combined Features - Correlate sensors, THEN batch for analysis
quality_control = flock.agent("qc").consumes(
    TemperatureSensor,
    PressureSensor,
    join=JoinSpec(by=lambda x: x.device_id, within=timedelta(seconds=30)),
    batch=BatchSpec(size=5, timeout=timedelta(seconds=45))  # IoT at scale!
)
```

**What just happened:**
- ✅ **Predicates** route work by business rules ("only critical severity")
- ✅ **BatchSpec** optimizes costs (25 transactions = 1 API call instead of 25)
- ✅ **JoinSpec** correlates related data (orders ↔ shipments, sensors ↔ readings)
- ✅ **Combined** delivers production-grade multi-stage pipelines

**Real-world impact:**
- 💰 E-commerce: Save $5 per batch on payment processing fees
- 🏥 Healthcare: Correlate patient scans + lab results for diagnosis
- 🏭 Manufacturing: Monitor 1000+ IoT sensors with efficient batching
- 📊 Finance: Match trades + confirmations within 5-minute windows

<p align="center">
  <img alt="Event Batch" src="docs/assets/images/batch.png" width="800">
</p>

### 🌟 Fan-Out Publishing (New in 0.5)

**Produce multiple outputs from a single agent execution:**

```python
# Generate 10 diverse product ideas from one brief
idea_generator = (
    flock.agent("generator")
    .consumes(ProductBrief)
    .publishes(ProductIdea, fan_out=10)  # Produces 10 ideas per brief!
)

# With WHERE filtering - only publish high-quality ideas
idea_generator = (
    flock.agent("generator")
    .consumes(ProductBrief)
    .publishes(
        ProductIdea,
        fan_out=20,  # Generate 20 candidates
        where=lambda idea: idea.score >= 8.0  # Only publish score >= 8
    )
)

# With VALIDATE - enforce quality standards
code_reviewer = (
    flock.agent("reviewer")
    .consumes(CodeSubmission)
    .publishes(
        BugReport,
        fan_out=5,
        validate=lambda bug: bug.severity in ["Critical", "High", "Medium", "Low"]
    )
)

# With Dynamic Visibility - control access per artifact
notification_agent = (
    flock.agent("notifier")
    .consumes(Alert)
    .publishes(
        Notification,
        fan_out=3,
        visibility=lambda n: PrivateVisibility(agents=[n.recipient])  # Dynamic!
    )
)
```

**What just happened:**
- ✅ **fan_out=N** - Agent produces N artifacts per execution (not just 1!)
- ✅ **where** - Filter outputs before publishing (reduce noise, save costs)
- ✅ **validate** - Enforce quality standards (fail-fast on bad outputs)
- ✅ **Dynamic visibility** - Control access per artifact based on content

**Real-world impact:**
- 🎯 **Content Generation** - Generate 10 blog post ideas, filter to top 3 by score
- 🐛 **Code Review** - Produce 5 potential bugs, validate severity levels
- 📧 **Notifications** - Create 3 notification variants, target specific agents
- 🧪 **A/B Testing** - Generate N variations, filter by quality metrics

**🤯 Multi-Output Fan-Out (New in 0.5)**

**The truly mind-blowing part:** Fan-out works across **multiple output types**:

```python
# Generate 3 of EACH type = 9 total artifacts in ONE LLM call!
multi_master = (
    flock.agent("multi_master")
    .consumes(Idea)
    .publishes(Movie, MovieScript, MovieCampaign, fan_out=3)
)

# Single execution produces:
# - 3 complete Movie artifacts (with title, genre, cast, plot)
# - 3 complete MovieScript artifacts (with characters, scenes, pages)
# - 3 complete MovieCampaign artifacts (with taglines, poster descriptions)
# = 9 complex artifacts, ~100+ fields total, full Pydantic validation, ONE LLM call!

await flock.publish(Idea(story_idea="An action thriller set in space"))
await flock.run_until_idle()

# Result: 9 artifacts on the blackboard, all validated, all ready
movies = await flock.store.get_by_type(Movie)  # 3 movies
scripts = await flock.store.get_by_type(MovieScript)  # 3 scripts
campaigns = await flock.store.get_by_type(MovieCampaign)  # 3 campaigns
```

**Why this is revolutionary:**
- ⚡ **Massive efficiency** - 1 LLM call generates 9 production-ready artifacts
- ✅ **Full validation** - All 100+ fields validated with Pydantic constraints
- 🎯 **Coherent generation** - Movie/Script/Campaign are thematically aligned (same LLM context)
- 💰 **Cost optimized** - 9 artifacts for the price of 1 API call

**Can any other agent framework do this?** We haven't found one. 🚀

**📖 [Full Fan-Out Guide →](https://whiteducksoftware.github.io/flock/guides/fan-out/)**

### Visibility Controls (The Security)

**Unlike other frameworks, Flock has zero-trust security built-in:**

```python
# Multi-tenancy (SaaS isolation)
agent.publishes(CustomerData, visibility=TenantVisibility(tenant_id="customer_123"))

# Explicit allowlist (HIPAA compliance)
agent.publishes(MedicalRecord, visibility=PrivateVisibility(agents={"physician", "nurse"}))

# Role-based access control
agent.identity(AgentIdentity(name="analyst", labels={"clearance:secret"}))
agent.publishes(IntelReport, visibility=LabelledVisibility(required_labels={"clearance:secret"}))

# Time-delayed release (embargo periods)
artifact.visibility = AfterVisibility(ttl=timedelta(hours=24), then=PublicVisibility())

# Public (default)
agent.publishes(PublicReport, visibility=PublicVisibility())
```

**Visibility has a dual purpose:** It controls both which agents can be **triggered** by an artifact AND which artifacts agents can **see** in their context. This ensures consistent security across agent execution and data access—agents cannot bypass visibility controls through subscription filters or context providers.

**Why this matters:** Financial services, healthcare, defense, SaaS platforms all need this for compliance. Other frameworks make you build it yourself.

---

### 🔒 Architecturally Impossible to Bypass Security

**Here's what makes Flock different:** In most frameworks, security is something you remember to add. In Flock, **it's architecturally impossible to forget.**

Every context provider in Flock inherits from `BaseContextProvider`, which enforces visibility filtering **automatically**. You literally cannot create a provider that forgets to check permissions—the security logic is baked into the base class and executes before your custom code even runs.

**What this means in practice:**

```python
# ❌ Other frameworks: Security is your responsibility (easy to forget!)
class MyProvider:
    async def get_context(self, agent):
        artifacts = store.get_all()  # OOPS! Forgot to check visibility!
        return artifacts  # 🔥 Security vulnerability

# ✅ Flock: Security is enforced automatically (impossible to bypass!)
class MyProvider(BaseContextProvider):
    async def get_artifacts(self, request):
        artifacts = await store.query_artifacts(...)
        return artifacts  # ✨ Visibility filtering happens automatically!
        # BaseContextProvider calls .visibility.allows() for you
        # You CANNOT bypass this - it's enforced by the architecture
```

**Built-in providers (all inherit BaseContextProvider):**
- `DefaultContextProvider` - Full blackboard access (visibility-filtered)
- `CorrelatedContextProvider` - Workflow isolation (visibility-filtered)
- `RecentContextProvider` - Token cost control (visibility-filtered)
- `TimeWindowContextProvider` - Time-based filtering (visibility-filtered)
- `EmptyContextProvider` - Stateless agents (zero context)
- `FilteredContextProvider` - Custom filtering (visibility-filtered)

**Every single one enforces visibility automatically. Zero chance of accidentally leaking data.**

This isn't just convenient—it's **security by design**. When you're building HIPAA-compliant healthcare systems or SOC2-certified SaaS platforms, "impossible to bypass even by accident" is the only acceptable standard.

---

### Context Providers (The Smart Filter)

**Control what agents see with custom Context Providers:**

```python
from flock.context_provider import FilteredContextProvider, PasswordRedactorProvider
from flock.store import FilterConfig

# Global filtering - all agents see only urgent items
flock = Flock(
    "openai/gpt-4.1",
    context_provider=FilteredContextProvider(FilterConfig(tags={"urgent"}))
)

# Per-agent overrides - specialized context per agent
error_agent = flock.agent("errors").consumes(Log).publishes(Alert)
error_agent.context_provider = FilteredContextProvider(FilterConfig(tags={"ERROR"}))

# Production-ready password filtering
from examples.context_provider import PasswordRedactorProvider
flock = Flock(
    "openai/gpt-4.1",
    context_provider=PasswordRedactorProvider()  # Auto-redacts sensitive data!
)
```

**What just happened:**
- ✅ **Filtered context** - Agents see only relevant artifacts (save tokens, improve performance)
- ✅ **Security boundary** - Visibility enforcement + custom filtering (mandatory, cannot bypass)
- ✅ **Sensitive data protection** - Auto-redact passwords, API keys, credit cards, SSN, JWT tokens
- ✅ **Per-agent specialization** - Different agents, different context rules

**Production patterns:**
```python
# Password/secret redaction (copy-paste ready!)
provider = PasswordRedactorProvider(
    custom_patterns={"internal_id": r"ID-\d{6}"},
    redaction_text="[REDACTED]"
)

# Role-based access control
junior_agent.context_provider = FilteredContextProvider(FilterConfig(tags={"ERROR"}))
senior_agent.context_provider = FilteredContextProvider(FilterConfig(tags={"ERROR", "WARN"}))
admin_agent.context_provider = None  # See everything (uses default)

# Multi-tenant isolation
agent.context_provider = FilteredContextProvider(
    FilterConfig(tags={"tenant:customer_123"})
)
```

**Why this matters:** Reduce token costs (90%+ with smart filtering), protect sensitive data (auto-redact secrets), improve performance (agents see only what they need).

**📖 [Learn more: Context Providers Guide](https://whiteducksoftware.github.io/flock/guides/context-providers/) | [Steal production code →](examples/08-context-provider/)**

### Persistent Blackboard History

The in-memory store is great for local development, but production teams need durability. The `SQLiteBlackboardStore` turns the blackboard into a persistent event log with first-class ergonomics:

**What you get:**
- **Long-lived artifacts** — Every field (payload, tags, partition keys, visibility) stored for replay, audits, and postmortems
- **Historical APIs** — `/api/v1/artifacts`, `/summary`, and `/agents/{agent_id}/history-summary` expose pagination, filtering, and consumption counts
- **Dashboard integration** — The **Historical Blackboard** view preloads persisted history, enriches the graph with consumer metadata, and highlights retention windows
- **Operational tooling** — CLI helpers (`init-sqlite-store`, `sqlite-maintenance --delete-before ... --vacuum`) make schema setup and retention policies scriptable

**Quick start:**
```python
from flock import Flock
from flock.store import SQLiteBlackboardStore

store = SQLiteBlackboardStore(".flock/blackboard.db")
await store.ensure_schema()
flock = Flock("openai/gpt-4.1", store=store)
```

**Try it:** Run `examples/02-the-blackboard/01_persistent_pizza.py` to generate history, then launch `examples/03-the-dashboard/04_persistent_pizza_dashboard.py` to explore previous runs, consumption trails, and retention banners.

### Batching Pattern: Parallel Execution Control

**A key differentiator:** The separation of `publish()` and `run_until_idle()` enables parallel execution.

```python
# ✅ EFFICIENT: Batch publish, then run in parallel
for review in customer_reviews:
    await flock.publish(review)  # Just scheduling work

await flock.run_until_idle()  # All sentiment_analyzer agents run concurrently!

# Get all results
analyses = await flock.store.get_by_type(SentimentAnalysis)
# 100 analyses completed in ~1x single review processing time!
```

**Why this separation matters:**
- ⚡ **Parallel execution** - Process 100 customer reviews concurrently
- 🎯 **Batch control** - Publish multiple artifacts, execute once
- 🔄 **Multi-type workflows** - Publish different types, trigger different agents in parallel
- 📊 **Better performance** - Process 1000 items in the time it takes to process 1

**Comparison to other patterns:**
```python
# ❌ If run_until_idle() was automatic (like most frameworks):
for review in customer_reviews:
    await flock.publish(review)  # Would wait for completion each time!
# Total time: 100x single execution (sequential)

# ✅ With explicit batching:
for review in customer_reviews:
    await flock.publish(review)  # Fast: just queuing
await flock.run_until_idle()
# Total time: ~1x single execution (parallel)
```

### Agent Components (Agent Lifecycle Hooks)

**Extend agent behavior through composable lifecycle hooks:**

Agent components let you inject custom logic at specific points in an agent's execution without modifying core agent code:

```python
from flock.components import AgentComponent

# Custom component: Log inputs/outputs
class LoggingComponent(AgentComponent):
    async def on_pre_evaluate(self, agent, ctx, inputs):
        logger.info(f"Agent {agent.name} evaluating: {inputs}")
        return inputs  # Pass through unchanged

    async def on_post_evaluate(self, agent, ctx, inputs, result):
        logger.info(f"Agent {agent.name} produced: {result}")
        return result

# Attach to any agent
analyzer = (
    flock.agent("analyzer")
    .consumes(Data)
    .publishes(Report)
    .with_utilities(LoggingComponent())
)
```

**Built-in components**: Rate limiting, caching, metrics collection, budget tracking, guardrails

**📖 [Learn more: Agent Components Guide](https://whiteducksoftware.github.io/flock/guides/components/)**

---

### Orchestrator Components (Orchestrator Lifecycle Hooks)

**Extend orchestrator behavior through composable lifecycle hooks:**

Orchestrator components let you inject custom logic into the orchestrator's scheduling pipeline:

```python
from flock.orchestrator_component import OrchestratorComponent, ScheduleDecision

# Custom component: Skip scheduling during maintenance window
class MaintenanceWindowComponent(OrchestratorComponent):
    async def on_before_schedule(self, orch, artifact, agent, subscription):
        if self.is_maintenance_window():
            logger.info(f"Deferring {agent.name} during maintenance")
            return ScheduleDecision.DEFER
        return ScheduleDecision.CONTINUE

# Add to orchestrator
flock = Flock("openai/gpt-4.1")
flock.add_component(MaintenanceWindowComponent())
```

**Built-in components**:
- `CircuitBreakerComponent` - Prevent runaway agent execution
- `DeduplicationComponent` - Skip duplicate artifact/agent processing

**8 Lifecycle Hooks**: Artifact publication, scheduling decisions, artifact collection, agent scheduling, idle/shutdown

---

### Production Safety Features

**Built-in safeguards prevent common production failures:**

```python
# Circuit breakers prevent runaway costs (via OrchestratorComponent)
flock = Flock("openai/gpt-4.1")  # Auto-adds CircuitBreakerComponent(max_iterations=1000)

# Feedback loop protection
critic = (
    flock.agent("critic")
    .consumes(Essay)
    .publishes(Critique)
    .prevent_self_trigger(True)  # Won't trigger itself infinitely
)

# Best-of-N execution (run 5x, pick best)
agent.best_of(5, score=lambda result: result.metrics["confidence"])

# Configuration validation
agent.best_of(150, ...)  # ⚠️ Warns: "best_of(150) is very high - high LLM costs"
```

---

## Production-Ready Observability

### Sophisticated REST API

**Production-ready HTTP endpoints with comprehensive OpenAPI documentation:**

Flock includes a fully-featured REST API for programmatic access to the blackboard, agents, and workflow orchestration. Perfect for integration with external systems, building custom UIs, or monitoring production deployments.

**Key endpoints:**
- `POST /api/v1/artifacts` - Publish artifacts to the blackboard
- `GET /api/v1/artifacts` - Query artifacts with filtering, pagination, and consumption metadata
- `POST /api/v1/agents/{name}/run` - Direct agent invocation
- `GET /api/v1/correlations/{correlation_id}/status` - Workflow completion tracking
- `GET /api/v1/agents` - List all registered agents with subscriptions
- `GET /health` and `GET /metrics` - Production monitoring

**Start the API server:**
```python
await flock.serve(dashboard=True)  # API + Dashboard on port 8344
# API docs: http://localhost:8344/docs
```

**Features:**
- ✅ **OpenAPI 3.0** - Interactive documentation at `/docs`
- ✅ **Pydantic validation** - Type-safe request/response models
- ✅ **Correlation tracking** - Monitor workflow completion with polling
- ✅ **Consumption metadata** - Full artifact lineage and agent execution trails
- ✅ **Production monitoring** - Health checks and Prometheus-compatible metrics

**📖 [Explore the API →](http://localhost:8344/docs)** (start the server first!)

### Real-Time Dashboard

**Start the dashboard with one line:**

```python
await flock.serve(dashboard=True)
```

The dashboard provides comprehensive real-time visibility into your agent system with professional UI/UX:

<p align="center">
  <img alt="Flock Agent View" src="docs/assets/images/flock_ui_agent_view.png" width="1000">
  <i>Agent View: See agent communication patterns and message flows in real-time</i>
</p>

**Key Features:**

- **Dual Visualization Modes:**
  - **Agent View** - Agents as nodes with message flows as edges
  - **Blackboard View** - Messages as nodes with data transformations as edges

<p align="center">
  <img alt="Flock Blackboard View" src="docs/assets/images/flock_ui_blackboard_view.png" width="1000">
  <i>Blackboard View: Track data lineage and transformations across the system</i>
</p>

- **Real-Time Updates:**
  - WebSocket streaming with 2-minute heartbeat
  - Live agent activation and message publication
  - Auto-layout with Dagre algorithm

- **Interactive Graph:**
  - Drag nodes, zoom, pan, and explore topology
  - Double-click nodes to open detail windows
  - Right-click for context menu with auto-layout options:
    - **5 Layout Algorithms**: Hierarchical (Vertical/Horizontal), Circular, Grid, and Random
    - **Smart Spacing**: Dynamic 200px minimum clearance based on node dimensions
    - **Viewport Centering**: Layouts always center around current viewport
  - Add modules dynamically from context menu

- **Advanced Filtering:**
  - Correlation ID tracking for workflow tracing
  - Time range filtering (last 5/10/60 minutes or custom)
  - Active filter pills with one-click removal
  - Autocomplete search with metadata preview

- **Control Panel:**
  - Publish artifacts from the UI
  - Invoke agents manually
  - Monitor system health

- **Keyboard Shortcuts:**
  - `Ctrl+M` - Toggle view mode
  - `Ctrl+F` - Focus filter
  - `Ctrl+/` - Show shortcuts help
  - WCAG 2.1 AA compliant accessibility

### Production-Grade Trace Viewer

The dashboard includes a **Jaeger-style trace viewer** with 7 powerful visualization modes:

<p align="center">
  <img alt="Trace Viewer" src="docs/assets/images/trace_1.png" width="1000">
  <i>Trace Viewer: Timeline view showing span hierarchies and execution flow</i>
</p>

**7 Trace Viewer Modes:**

1. **Timeline** - Waterfall visualization with parent-child relationships
2. **Statistics** - Sortable table view with durations and error tracking
3. **RED Metrics** - Rate, Errors, Duration monitoring for service health
4. **Dependencies** - Service-to-service communication analysis
5. **DuckDB SQL** - Interactive SQL query editor with CSV export
6. **Configuration** - Real-time service/operation filtering
7. **Guide** - Built-in documentation and query examples

**Additional Features:**

- **Full I/O Capture** - Complete input/output data for every operation
- **JSON Viewer** - Collapsible tree structure with expand all/collapse all
- **Multi-Trace Support** - Open and compare multiple traces simultaneously
- **Smart Sorting** - Sort by date, span count, or duration
- **CSV Export** - Download query results for offline analysis

<p align="center">
  <img alt="Trace Viewer" src="docs/assets/images/trace_2.png" width="1000">
  <i>Trace Viewer: Dependency Analysis</i>
</p>


### OpenTelemetry + DuckDB Tracing

**One environment variable enables comprehensive tracing:**

```bash
export FLOCK_AUTO_TRACE=true
export FLOCK_TRACE_FILE=true

python your_app.py
# Traces stored in .flock/traces.duckdb
```

**AI-queryable debugging:**

```python
import duckdb
conn = duckdb.connect('.flock/traces.duckdb', read_only=True)

# Find bottlenecks
slow_ops = conn.execute("""
    SELECT name, AVG(duration_ms) as avg_ms, COUNT(*) as count
    FROM spans
    WHERE duration_ms > 1000
    GROUP BY name
    ORDER BY avg_ms DESC
""").fetchall()

# Find errors with full context
errors = conn.execute("""
    SELECT name, status_description,
           json_extract(attributes, '$.input') as input,
           json_extract(attributes, '$.output') as output
    FROM spans
    WHERE status_code = 'ERROR'
""").fetchall()
```

**Real debugging session:**
```
You: "My pizza agent is slow"
AI: [queries DuckDB]
    "DSPyEngine.evaluate takes 23s on average.
     Input size: 50KB of conversation history.
     Recommendation: Limit context to last 5 messages."
```

**Why DuckDB?** 10-100x faster than SQLite for analytical queries. Zero configuration. AI agents can debug your AI agents.

<p align="center">
  <img alt="Trace Viewer" src="docs/assets/images/trace_3.png" width="1000">
  <i>Trace Viewer: DuckDB Query</i>
</p>

---

## Framework Comparison

### Architectural Differences

Flock uses a fundamentally different coordination pattern than most multi-agent frameworks:

| Dimension | Graph-Based Frameworks | Chat-Based Frameworks | Flock (Blackboard) |
|-----------|------------------------|----------------------|-------------------|
| **Core Pattern** | Directed graph with explicit edges | Round-robin conversation | Blackboard subscriptions |
| **Coordination** | Manual edge wiring | Message passing | Type-based subscriptions |
| **Parallelism** | Manual (split/join nodes) | Sequential turn-taking | Automatic (concurrent consumers) |
| **Type Safety** | Varies (often TypedDict) | Text-based messages | Pydantic + runtime validation |
| **Coupling** | Tight (hardcoded successors) | Medium (conversation context) | Loose (type subscriptions only) |
| **Adding Agents** | Rewrite graph topology | Update conversation flow | Just subscribe to types |
| **Testing** | Requires full graph | Requires full group | Individual agent isolation |
| **Security Model** | DIY implementation | DIY implementation | Built-in (5 visibility types) |
| **Scalability** | O(n²) edge complexity | Limited by turn-taking | O(n) subscription complexity |

### When Flock Wins

**✅ Use Flock when you need:**

- **Parallel agent execution** - Agents consuming the same type run concurrently automatically
- **Type-safe outputs** - Pydantic validation catches errors at runtime
- **Minimal prompt engineering** - Schemas define behavior, not natural language
- **Dynamic agent addition** - Subscribe new agents without rewiring existing workflows
- **Testing in isolation** - Unit test individual agents with mock inputs
- **Built-in security** - 5 visibility types for compliance (HIPAA, SOC2, multi-tenancy)
- **10+ agents** - Linear complexity stays manageable at scale

### When Alternatives Win

**⚠️ Consider graph-based frameworks when:**
- You need extensive ecosystem integration with existing tools
- Your workflow is inherently sequential (no parallelism needed)
- You want battle-tested maturity (larger communities, more documentation)
- Your team has existing expertise with those frameworks

**⚠️ Consider chat-based frameworks when:**
- You prefer conversation-based development patterns
- Your use case maps naturally to turn-taking dialogue
- You need features specific to those ecosystems

### Honest Trade-offs

**You trade:**
- Ecosystem maturity (established frameworks have larger communities)
- Extensive documentation (we're catching up)
- Battle-tested age (newer architecture means less production history)

**You gain:**
- Better scalability (O(n) vs O(n²) complexity)
- Type safety (runtime validation vs hope)
- Cleaner architecture (loose coupling vs tight graphs)
- Production safety (circuit breakers, feedback prevention built-in)
- Security model (5 visibility types vs DIY)

**Different frameworks for different priorities. Choose based on what matters to your team.**

---

## Production Readiness

### What Works Today (v0.5.0)

**✅ Production-ready core:**
- More than 700 tests, with >75% coverage (>90% on critical paths)
- Blackboard orchestrator with typed artifacts
- Parallel + sequential execution (automatic)
- Zero-trust security (5 visibility types)
- Circuit breakers and feedback loop prevention
- OpenTelemetry distributed tracing with DuckDB storage
- Real-time dashboard with 7-mode trace viewer
- MCP integration (Model Context Protocol)
- Best-of-N execution, batch processing, join operations
- Type-safe retrieval API (`get_by_type()`)

**⚠️ What's missing for large-scale production:**
- **Advanced retry logic** - Basic only (exponential backoff planned)
- **Event replay** - No Kafka integration yet
- **Kubernetes-native deployment** - No Helm chart yet
- **OAuth/RBAC** - Dashboard has no auth

**✅ Available today:**
- **Persistent blackboard** - SQLiteBlackboardStore (see above)

All missing features planned for v1.0

### Recommended Use Cases Today

**✅ Good fit right now:**
- **Startups/MVPs** - Fast iteration, type safety, built-in observability
- **Internal tools** - Where in-memory blackboard is acceptable
- **Research/prototyping** - Rapid experimentation with clean architecture
- **Medium-scale systems** (10-50 agents, 1000s of artifacts)

**⚠️ Wait for 1.0 if you need:**
- **Enterprise persistence** (multi-region, high availability)
- **Compliance auditing** (immutable event logs)
- **Multi-tenancy SaaS** (with OAuth/SSO)
- **Mission-critical systems** with 99.99% uptime requirements

**Flock 0.5.0 is production-ready for the right use cases. Know your requirements.**

---

## Roadmap to 1.0

We're building enterprise infrastructure for AI agents and tracking the work publicly. Check [ROADMAP.md](ROADMAP.md) for deep dives and status updates.

### 0.5.0 Beta (In Flight)
- **Core data & governance:** [#271](https://github.com/whiteducksoftware/flock/issues/271), [#274](https://github.com/whiteducksoftware/flock/issues/274), [#273](https://github.com/whiteducksoftware/flock/issues/273), [#281](https://github.com/whiteducksoftware/flock/issues/281)
- **Execution patterns & scheduling:** [#282](https://github.com/whiteducksoftware/flock/issues/282), [#283](https://github.com/whiteducksoftware/flock/issues/283)
- **REST access & integrations:** [#286](https://github.com/whiteducksoftware/flock/issues/286), [#287](https://github.com/whiteducksoftware/flock/issues/287), [#288](https://github.com/whiteducksoftware/flock/issues/288), [#289](https://github.com/whiteducksoftware/flock/issues/289), [#290](https://github.com/whiteducksoftware/flock/issues/290), [#291](https://github.com/whiteducksoftware/flock/issues/291), [#292](https://github.com/whiteducksoftware/flock/issues/292), [#293](https://github.com/whiteducksoftware/flock/issues/293)
- **Docs & onboarding:** [#270](https://github.com/whiteducksoftware/flock/issues/270), [#269](https://github.com/whiteducksoftware/flock/issues/269)

### 1.0 Release Goals (Target Q4 2025)
- **Reliability & operations:** [#277](https://github.com/whiteducksoftware/flock/issues/277), [#278](https://github.com/whiteducksoftware/flock/issues/278), [#279](https://github.com/whiteducksoftware/flock/issues/279), [#294](https://github.com/whiteducksoftware/flock/issues/294)
- **Platform validation & quality:** [#275](https://github.com/whiteducksoftware/flock/issues/275), [#276](https://github.com/whiteducksoftware/flock/issues/276), [#284](https://github.com/whiteducksoftware/flock/issues/284), [#285](https://github.com/whiteducksoftware/flock/issues/285)
- **Security & access:** [#280](https://github.com/whiteducksoftware/flock/issues/280)

---

## Example: Multi-Modal Clinical Decision Support

```python
import os
from flock import Flock, flock_type
from flock.visibility import PrivateVisibility, TenantVisibility, LabelledVisibility
from flock.identity import AgentIdentity
from pydantic import BaseModel

@flock_type
class PatientScan(BaseModel):
    patient_id: str
    scan_type: str
    image_data: bytes

@flock_type
class XRayAnalysis(BaseModel):
    findings: list[str]
    confidence: float

@flock_type
class LabResults(BaseModel):
    markers: dict[str, float]

@flock_type
class Diagnosis(BaseModel):
    condition: str
    reasoning: str
    confidence: float

# Create HIPAA-compliant blackboard
flock = Flock(os.getenv("DEFAULT_MODEL", "openai/gpt-4.1"))

# Radiologist with privacy controls
radiologist = (
    flock.agent("radiologist")
    .consumes(PatientScan)
    .publishes(
        XRayAnalysis,
        visibility=PrivateVisibility(agents={"diagnostician"})  # HIPAA!
    )
)

# Lab tech with multi-tenancy
lab_tech = (
    flock.agent("lab_tech")
    .consumes(PatientScan)
    .publishes(
        LabResults,
        visibility=TenantVisibility(tenant_id="patient_123")  # Isolation!
    )
)

# Diagnostician with explicit access
diagnostician = (
    flock.agent("diagnostician")
    .identity(AgentIdentity(name="diagnostician", labels={"role:physician"}))
    .consumes(XRayAnalysis, LabResults)  # Waits for BOTH
    .publishes(
        Diagnosis,
        visibility=LabelledVisibility(required_labels={"role:physician"})
    )
)

# Run with tracing
async with flock.traced_run("patient_123_diagnosis"):
    await flock.publish(PatientScan(patient_id="123", ...))
    await flock.run_until_idle()

    # Get diagnosis (type-safe retrieval)
    diagnoses = await flock.store.get_by_type(Diagnosis)
    # Returns list[Diagnosis] directly - no .data access, no casting
```

**What this demonstrates:**
- Multi-modal data fusion (images + labs + history)
- Built-in access controls (HIPAA compliance)
- Parallel agent execution (radiology + labs run concurrently)
- Automatic dependency resolution (diagnostician waits for both)
- Full audit trail (traced_run + DuckDB storage)
- Type-safe data retrieval (no Artifact wrappers)

---

## Production Use Cases

Flock's architecture shines in production scenarios requiring parallel execution, security, and observability. Here are common patterns:

### Financial Services: Multi-Signal Trading

**The Challenge:** Analyze multiple market signals in parallel, correlate them within time windows, maintain SEC-compliant audit trails.

**The Solution:** 20+ signal analyzers run concurrently, join operations correlate signals, DuckDB provides complete audit trails.

```python
# Parallel signal analyzers
volatility = flock.agent("volatility").consumes(MarketData).publishes(VolatilityAlert)
sentiment = flock.agent("sentiment").consumes(NewsArticle).publishes(SentimentAlert)

# Trade execution waits for CORRELATED signals (within 5min window)
trader = flock.agent("trader").consumes(
    VolatilityAlert, SentimentAlert,
    join=JoinSpec(within=timedelta(minutes=5))
).publishes(TradeOrder)
```

### Healthcare: HIPAA-Compliant Diagnostics

**The Challenge:** Multi-modal data fusion with strict access controls, complete audit trails, zero-trust security.

**The Solution:** Built-in visibility controls for HIPAA compliance, automatic parallel execution, full data lineage tracking.

```python
# Privacy controls built-in
radiology.publishes(XRayAnalysis, visibility=PrivateVisibility(agents={"diagnostician"}))
lab.publishes(LabResults, visibility=TenantVisibility(tenant_id="patient_123"))

# Diagnostician waits for BOTH inputs with role-based access
diagnostician = flock.agent("diagnostician").consumes(XRayAnalysis, LabResults).publishes(Diagnosis)
```

### E-Commerce: 50-Agent Personalization

**The Challenge:** Analyze dozens of independent signals, support dynamic signal addition, process millions of events daily.

**The Solution:** O(n) scaling to 50+ analyzers, batch processing for efficiency, zero graph rewiring when adding signals.

```python
# 50+ signal analyzers (all run in parallel!)
for signal in ["browsing", "purchase", "cart", "reviews", "email", "social"]:
    flock.agent(f"{signal}_analyzer").consumes(UserEvent).publishes(Signal)

# Recommender batches signals for efficient LLM calls
recommender = flock.agent("recommender").consumes(Signal, batch=BatchSpec(size=50))
```

### Multi-Tenant SaaS: Content Moderation

**The Challenge:** Complete data isolation between tenants, multi-agent consensus, full audit trails.

**The Solution:** Tenant visibility ensures zero cross-tenant leakage, parallel checks provide diverse signals, traces show complete reasoning.

**See [USECASES.md](USECASES.md) for complete code examples and production metrics.**

---

## Getting Started

```bash
# Install
pip install flock-core

# Set API key
export OPENAI_API_KEY="sk-..."

# Try the examples
git clone https://github.com/whiteducksoftware/flock-flow.git
cd flock-flow

# CLI examples with detailed output
uv run python examples/01-cli/01_declarative_pizza.py

# Dashboard examples with visualization
uv run python examples/02-dashboard/01_declarative_pizza.py
```

**Learn by doing:**
- 📚 [Examples README](examples/README.md) - 12-step learning path from basics to advanced
- 🖥️ [CLI Examples](examples/01-cli/) - Detailed console output examples (01-12)
- 📊 [Dashboard Examples](examples/02-dashboard/) - Interactive visualization examples (01-12)
- 📖 [Documentation](https://whiteducksoftware.github.io/flock) - Complete online documentation
- 📘 [AGENTS.md](AGENTS.md) - Development guide

**Architecture & Patterns:**
- 📐 [Architecture Overview](docs/architecture.md) - Understand the refactored codebase structure
- 🔧 [Error Handling](docs/patterns/error_handling.md) - Production-ready error patterns
- ⚡ [Async Patterns](docs/patterns/async_patterns.md) - Async/await best practices

---

## Contributing

We're building Flock in the open. See **[Contributing Guide](https://whiteducksoftware.github.io/flock/about/contributing/)** for development setup, or check [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) locally.

**Before contributing, familiarize yourself with:**
- [Architecture Overview](docs/architecture.md) - Codebase organization (Phase 1-7 refactoring)
- [Error Handling](docs/patterns/error_handling.md) - Required error patterns
- [Async Patterns](docs/patterns/async_patterns.md) - Async/await standards

**We welcome:**
- Bug reports and feature requests
- Documentation improvements
- Example contributions
- Architecture discussions

**Quality standards:**
- All tests must pass
- Coverage requirements met
- Code formatted with Ruff

---

## Why "0.5"?

We're calling this 0.5 to signal:

1. **Core is production-ready** - real-world client deployments, comprehensive features
2. **Ecosystem is evolving** - Documentation growing, community building, features maturing
3. **Architecture is proven** - Blackboard pattern is 50+ years old, declarative contracts are sound
4. **Enterprise features are coming** - Persistence, auth, Kubernetes deployment in roadmap

**1.0 will arrive** when we've delivered persistence, advanced error handling, and enterprise deployment patterns (targeting Q4 2025).

---

## The Bottom Line

**Flock is different because it makes different architectural choices:**

**Instead of:**
- ❌ Prompt engineering → ✅ Declarative type contracts
- ❌ Workflow graphs → ✅ Blackboard subscriptions
- ❌ Manual parallelization → ✅ Automatic concurrent execution
- ❌ Bolt-on security → ✅ Zero-trust visibility controls
- ❌ Hope-based debugging → ✅ AI-queryable distributed traces

**These aren't marketing slogans. They're architectural decisions with real tradeoffs.**

**You trade:**
- Ecosystem maturity (established frameworks have larger communities)
- Extensive documentation (we're catching up)
- Battle-tested age (newer architecture means less production history)

**You gain:**
- Better scalability (O(n) vs O(n²) complexity)
- Type safety (runtime validation vs hope)
- Cleaner architecture (loose coupling vs tight graphs)
- Production safety (circuit breakers, feedback prevention built-in)
- Security model (5 visibility types vs DIY)

**Different frameworks for different priorities. Choose based on what matters to your team.**

---

<div align="center">

**Built with ❤️ by white duck GmbH**

**"Declarative contracts eliminate prompt hell. Blackboard architecture eliminates graph spaghetti. Proven patterns applied to modern LLMs."**

[⭐ Star on GitHub](https://github.com/whiteducksoftware/flock-flow) | [📖 Documentation](https://whiteducksoftware.github.io/flock) | [🚀 Try Examples](examples/) | [💼 Enterprise Support](mailto:support@whiteduck.de)

</div>

---

**Last Updated:** October 19, 2025
**Version:** Flock 0.5.0 (Blackboard Edition)
**Status:** Production-Ready Core, Enterprise Features Roadmapped
