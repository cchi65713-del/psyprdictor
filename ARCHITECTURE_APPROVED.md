# Tendency Competition Architecture - Final Approved Design

## Summary of Key Adjustments (From Initial Proposal)

**Original design had:** Vote-based competition model  
**Approved design has:** Tendency competition model

The adjustment preserves the psychological reality of internal pressures rather than collapsing everything into vote counts.

---

## The Tendency Competition Model (NOT Voting)

### What This Means

Each internal subsystem generates a **tendency** — a distinct psychological pressure toward an action.

- Goal-directed system: "I think we should WalkAway (pressure: 0.38)"
- Reactive system: "I think we should RespondImmediately (pressure: 0.65)"
- Habitual system: "I think we should RespondImmediately (pressure: 0.20)"

These are not votes. They are expressions of internal pressure that need to be **evaluated and resolved**, not counted.

### Complete Data Flow

```
PersonState (current emotion, goals, context)
    ↓
PROPOSAL STAGE
├─ Goal-directed → BehavioralTendency(action, raw_strength, confidence, evidence)
├─ Reactive → BehavioralTendency(action, raw_strength, confidence, evidence)
└─ Habitual → BehavioralTendency(action, raw_strength, confidence, evidence)
    ↓
NORMALIZATION STAGE
├─ Scale all raw_strength values to 0-1 canonical scale
├─ Goal/Reactive: divide by 100
├─ Habit: divide by 10 (clamped to 1.0)
└─ Track what scale each came from (for transparency)
    ↓
WEIGHTING STAGE (Explicit Parameters)
├─ Apply subsystem_weights to each normalized tendency
├─ subsystem_weights = {goal: 1.0, reactive: 1.0, habit: 1.0}  ← tunable, not hidden
├─ weighted_strength = normalized_strength × subsystem_weight
└─ All weights start equal; can be learned later
    ↓
SYSTEMMEMORY ADJUSTMENT STAGE
├─ Apply multiplicative modulation factors (range 0.3-1.3)
├─ memory_adjusted = weighted_strength × memory_factor
├─ Factors based on beliefs, rules, relationships
└─ SystemMemory influences but does NOT dominate
    ↓
PRESSURE AGGREGATION STAGE
├─ Group adjusted tendencies by action
├─ For each action: sum all pressures contributing to it
├─ Example: RespondImmediately = Reactive(0.65) + Habit(0.20) = 0.85 total pressure
└─ WalkAway = Goal(0.38) total pressure
    ↓
ARBITRATION STAGE (CORE DECISION POINT)
├─ Compare action pressures: 0.85 vs 0.38
├─ Select highest-pressure action: RespondImmediately
├─ Calculate margin: 0.85 - 0.38 = 0.47 (55% margin)
├─ Detect conflict: different sources want different actions = HIGH CONFLICT
├─ Preserve all details: what each wanted, why, how much pressure
└─ Return CompetitionResult with full metadata
    ↓
CONFIDENCE CALCULATION
├─ NOT just "winner / total" ratio
├─ Multi-factor: margin (40%) + convergence (30%) + source_confidence (20%) + evidence (10%)
├─ Margin: 0.47/0.85 = 55% → high score
├─ Convergence: 2/3 sources want winner → moderate score  
├─ Source confidence: Reactive(0.95) + Habit(0.80) avg → high
├─ Evidence: 3+ items supporting → high
└─ Final: weighted combination of all factors
    ↓
BEHAVIOR EXECUTION
└─ Selected action + confidence + conflict details + reasoning
    ↓
OUTCOME SIMULATION
└─ Execute action, observe result
    ↓
LEARNING UPDATES
├─ Pattern learner: did this pattern lead to good/bad outcome?
├─ Habit formation: was this action good? How does it interact with goals?
├─ SystemMemory: did our rules predict correctly?
└─ Conflict learning: WHEN conflict occurred and was overridden, was outcome good?
```

---

## Key Design Principles

### 1. Tendencies Are Evaluated, Not Voted

**WRONG (voting model):**
```
Goal votes: WalkAway (1 vote)
Reactive votes: RespondImmediately (1 vote)
Habit votes: RespondImmediately (1 vote)
Result: RespondImmediately wins 2-1 by voting
```
This hides the PRESSURE. It says all votes are equal.

**CORRECT (tendency model):**
```
Goal pressure toward WalkAway: 0.38
Reactive pressure toward RespondImmediately: 0.65
Habit pressure toward RespondImmediately: 0.20
Total RespondImmediately pressure: 0.85
Total WalkAway pressure: 0.38
Winner: RespondImmediately (0.85 > 0.38)
Margin: 55%
```
This preserves the MAGNITUDE of each internal pressure.

### 2. Explicit Parameters, Not Hidden Assumptions

**Subsystem weights are EXPLICIT configuration:**
```python
subsystem_weights = {
    "goal_directed": 1.0,    # baseline influence
    "reactive": 1.0,         # baseline influence
    "habit": 1.0,            # baseline influence
}
```

There is NO hidden assumption that "Reactive is always stronger."

There is NO hidden assumption that "two sources beat one source."

These are tunable parameters. Initially all equal. Can be changed or learned later.

### 3. Conflict Is Preserved and Explicit

The arbitration result includes:

```python
conflict_info: {
    exists: True,
    level: "high",
    type: "coalition_override",
    
    proposals_by_source: {
        "goal_directed": WalkAway (0.38),
        "reactive": RespondImmediately (0.65),
        "habit": RespondImmediately (0.20),
    },
    
    winning_action: "RespondImmediately",
    winning_pressure: 0.85,
    runner_up_action: "WalkAway",
    runner_up_pressure: 0.38,
    margin_percentage: 0.55,
}
```

Learning can use this: "When goal is overridden by emotional+habitual coalition, what's the outcome?"

### 4. SystemMemory Modulates, Does Not Dominate

Multiplicative adjustment means:
- SystemMemory can't add arbitrary large numbers
- It can dampen or boost existing tendencies
- Its effect is proportional to the original tendency
- Range: 0.3× to 1.3× (can't reverse a strong tendency alone)

### 5. Data Structures Are Transparent

Every decision preserves:
- Raw strength (original signal)
- Normalized strength (comparable value)
- Weights applied (explicit parameters)
- Memory adjustments (what was modulated)
- Final pressure (result of all modifications)
- Evidence (why this tendency exists)
- Confidence from source (how sure is the subsystem)

This allows inspection and debugging at every stage.

---

## Python Implementation Checklist (Do NOT code yet)

### New Data Classes

```python
class BehavioralTendency:
    action: str
    raw_strength: float
    normalized_strength: float
    source: str  # "goal_directed" | "reactive" | "habit"
    confidence_in_proposal: float
    supporting_evidence: list[str]
    reason: str

class CompetitionResult:
    selected_action: str
    final_pressure: float
    decision_confidence: float
    conflict_level: str  # "none" | "mild" | "moderate" | "high"
    all_proposals: list[BehavioralTendency]
    all_pressures: dict  # action -> total pressure
    conflict_info: dict  # detailed conflict structure
    reasoning: str
```

### Files to Modify

1. **action_selection.py**
   - Return BehavioralTendency, not scores

2. **normalization.py** (new)
   - Scale conversion logic
   - Subsystem weight configuration
   - Tunable parameters

3. **arbitration.py**
   - Normalize tendencies
   - Apply weights
   - Apply SystemMemory adjustments
   - Aggregate pressures by action
   - Select highest pressure
   - Preserve conflict information
   - Return CompetitionResult

4. **system_memory.py**
   - Return multiplicative factors, not added scores

5. **pattern_adaptation.py** & **habit_formation.py**
   - Accept conflict information in learning updates

### Behavior Preservation

The five scenarios should still produce:
1. Repeated conflict → RespondImmediately ✓
2. Minor disagreement → Negotiation ✓
3. Walk away beneficial → WalkAway ✓
4. Stay quiet beneficial → Negotiation ✓
5. Habit vs. Goal conflict → RespondImmediately ✓

(The mechanism changes, but the outcomes should be the same.)

---

## Why This Design

### Problem It Solves

**Original problem:** Additive scoring collapsed everything into meaningless numeric sums.

**This solution:** Preserves each subsystem's distinct psychological pressure while allowing meaningful arbitration.

### Psychological Authenticity

Different internal systems don't "vote." They exert distinct pressures:
- Goals are strategic
- Emotions are immediate
- Habits are learned patterns

These compete as pressures, not as equal votes.

### Learning Opportunity

By preserving conflict information, the system can learn:
- When does emotional override lead to good outcomes?
- When does goal-directed thinking prevent harm?
- When is habit reliable?

This is impossible if conflict is hidden in the scoring.

### Modularity for Future

When a new subsystem is added (e.g., social context, peer pressure):
- It generates a BehavioralTendency
- Arbitration evaluates it alongside existing tendencies
- No rewrite of arbitration needed

---

## What Comes Next (After Approval)

**DO NOT code yet.**

This architecture document is for **design review**.

Once approved, the implementation steps are:

1. Create data classes (BehavioralTendency, CompetitionResult)
2. Implement normalization.py with configuration
3. Refactor action_selection.py to return tendencies
4. Refactor system_memory.py for multiplicative adjustment
5. Rewrite arbitration.py with the competition flow
6. Test scenarios to verify behavior
7. Connect learning layers to conflict information
8. Validate five-scenario results still hold

---

## End of Design: Ready for Implementation Review

This document specifies **how PsyPredictor represents internal competition** without assuming any subsystem is universally "stronger."

It preserves conflict, enables learning from conflict resolution, and keeps the system modular for future expansion.

**Approval status:** Design ready for Python implementation.
