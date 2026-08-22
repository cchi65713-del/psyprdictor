# Competition Architecture Design for PsyPredictor

## Current Architecture (As Implemented)

The current system follows this flow:

```
PersonState
    ↓
Goal-directed proposals → Raw score for each action
Habitual proposals → Raw score for each action
Reactive proposals → Raw score for each action
    ↓
SystemMemory → Adds modifier scores
    ↓
Aggregate scores (simple addition)
    ↓
Arbitration (argmax)
    ↓
Selected action
    ↓
Outcome simulation
    ↓
Learning updates
```

**Current mechanism:**
- Each subsystem generates an action with a numeric score (roughly 0-100 range, variable)
- SystemMemory adds fixed increments based on rules (+0.8, +0.5, etc.)
- All scores are summed into a single action-score vector
- Arbitration selects the action with the highest aggregate score
- Confidence = (chosen_score / total_score) × 100

**Problems identified in review:**
1. No normalization across systems
2. Score comparability is assumed, not enforced
3. SystemMemory can dominate by arithmetic scale
4. Conflict between tendencies is not preserved
5. Confidence is a numerical ratio, not decision certainty
6. Habit is treated as direct action value, not learned tendency

---

## Proposed Architecture

### High-Level Flow

```
PersonState
    ↓
─────────────────────────────────────────────────
│ PROPOSAL STAGE: Generate behavioral tendencies │
─────────────────────────────────────────────────
    ↓
Goal-directed system   → Behavioral Tendency [action, strength, evidence, reason]
Habitual system        → Behavioral Tendency [action, strength, evidence, reason]
Reactive system        → Behavioral Tendency [action, strength, evidence, reason]
    ↓
─────────────────────────────────────────────────
│ NORMALIZATION STAGE: Make signals comparable  │
─────────────────────────────────────────────────
    ↓
Normalize each tendency to canonical scale (e.g., 0-1)
Track normalization metadata
    ↓
─────────────────────────────────────────────────
│ COMPETITION STAGE: Weigh and resolve          │
─────────────────────────────────────────────────
    ↓
SystemMemory influence layer
    → Modulate or adjust tendencies without dominating by scale
    → Apply contextual weights
    ↓
Arbitration mechanism
    → Identify convergence vs. conflict
    → Select winning action
    → Preserve conflict information
    ↓
─────────────────────────────────────────────────
│ DECISION STAGE: Confidence and certainty      │
─────────────────────────────────────────────────
    ↓
Calculate decision confidence
    → Based on: margin of victory, conflict magnitude, evidence quality
    → NOT based on: raw score ratio
    ↓
Selected action + confidence + conflict info + reason
    ↓
─────────────────────────────────────────────────
│ FEEDBACK STAGE: Outcome and learning          │
─────────────────────────────────────────────────
    ↓
Outcome simulation (as currently)
    ↓
Learning updates:
    → Pattern adaptation
    → Habit strength updates
    → SystemMemory belief updates
```

---

## Data Structures

### BehavioralTendency

Each subsystem returns a structured proposal containing:

```python
class BehavioralTendency:
    action: str                      # e.g., "RespondImmediately", "WalkAway"
    raw_strength: float              # Raw strength from source system (0-100 scale, uncalibrated)
    normalized_strength: float       # Normalized to canonical scale (0-1)
    source: str                      # "goal" | "habit" | "reactive"
    supporting_evidence: list[str]   # Evidence for this tendency
    reason: str                      # Human-readable explanation
    confidence_in_proposal: float    # How confident is the source system? (0-1)
    context_tags: dict               # {"conflict_level": int, "urgency": int, ...}
```

### NormalizedTendency (after normalization stage)

```python
class NormalizedTendency:
    action: str
    strength: float                  # Canonical normalized scale (0-1)
    source: str
    supporting_evidence: list[str]
    reason: str
    source_confidence: float         # Original confidence from source
    normalization_factor: float      # What scale factor was applied?
    raw_before_norm: float           # Original raw value
    context_tags: dict
```

### CompetitionResult (after arbitration)

```python
class CompetitionResult:
    selected_action: str
    selected_source: str             # Which subsystem won?
    final_strength: float            # Strength of winning tendency (0-1)
    decision_confidence: float       # Confidence in decision (0-1)
    conflict_level: str              # "none" | "mild" | "moderate" | "high"
    conflict_sources: list[str]      # Which systems disagreed?
    conflict_margin: float           # How close was the competition?
    all_proposals: list[NormalizedTendency]  # All proposals for transparency
    reasoning: str                   # Full explanation including conflict info
    system_memory_influence: dict    # What did SystemMemory do?
```

---

## Normalization Stage

**Goal:** Make different subsystem signals comparable without arithmetic dominance.

### Current Problem Example

Suppose:
- Goal-directed → WalkAway: 45.0 (strength estimate from goals)
- Reactive → RespondImmediately: 65.0 (arousal-based strength)
- Habit → RespondImmediately: 3.2 (habit strength multiplier)
- SystemMemory → +0.8 (rule bonus for conflict avoidance)

Sum for WalkAway: 45.0 + 0.8 = 45.8
Sum for RespondImmediately: 65.0 + 3.2 = 68.2

**Problem:** These numbers come from incomparable scales:
- 45.0 is a goal-satisfaction estimate
- 65.0 is an arousal measure
- 3.2 is a learned habit repetition count
- 0.8 is a rule support increment

Treating them as equivalent numeric values is an artificial shortcut.

### Proposed Normalization Solution

**Step 1: Understand the source scale for each subsystem**

- Goal-directed: 0-100 scale (goal satisfaction / feasibility)
- Reactive: 0-100 scale (arousal / urgency / salience)
- Habit: typically 0-10 scale (repetition frequency / strength)

**Step 2: Normalize each to 0-1 canonical scale**

Goal-directed:
```
normalized_strength = raw_strength / 100.0
```

Reactive:
```
normalized_strength = raw_strength / 100.0
```

Habit:
```
normalized_strength = min(raw_strength / 10.0, 1.0)
```

**Step 3: Optionally apply sub-system-level confidence adjustments**

Each subsystem also reports its own confidence in the proposal:

```
adjusted_strength = normalized_strength * source_confidence
```

For example:
- Goal says WalkAway with 50% normalized strength and 90% confidence
  → 0.50 × 0.90 = 0.45
- Reactive says RespondImmediately with 65% normalized strength and 95% confidence
  → 0.65 × 0.95 = 0.6175

**Step 4: Track metadata for transparency**

Each normalized tendency records:
- What was the raw value?
- What scale was it on?
- What normalization factor was applied?
- What was the confidence adjustment?

This allows post-hoc inspection of how competition was decided without losing the original signals.

---

## Competition Stage

**Goal:** Conduct the internal competition in a way that preserves each subsystem's actual influence and pressure toward actions, while preventing numeric dominance.

### Tendency Competition Model (Primary Approach)

Instead of vote-counting, evaluate each normalized tendency as a direct expression of internal pressure from that subsystem. Each subsystem maintains its own influence regardless of how many systems propose the same action.

**Principle:** The strength of each tendency represents the actual psychological pressure from that source. Arbitration must evaluate all competing pressures and resolve them.

**Example:**

Three normalized proposals after SystemMemory adjustment:
- Goal-directed: WalkAway (tendency strength 0.38, confidence 0.85)
- Reactive: RespondImmediately (tendency strength 0.65, confidence 0.95)
- Habit: RespondImmediately (tendency strength 0.32, confidence 0.80)

**Competing tendencies structure:**

```
Tendency 1 (Goal-directed):
  action: "WalkAway"
  strength: 0.38
  source: "goal_directed"
  evidence: ["conflict avoidance goal", "relationship preservation"]
  confidence: 0.85
  reason: "Goal is to avoid conflict"

Tendency 2 (Reactive):
  action: "RespondImmediately"
  strength: 0.65
  source: "reactive"
  evidence: ["high arousal (7/10)", "social threat perceived"]
  confidence: 0.95
  reason: "Immediate threat requires immediate response"

Tendency 3 (Habitual):
  action: "RespondImmediately"
  strength: 0.32
  source: "habit"
  evidence: ["learned response pattern", "repetition count: 12"]
  confidence: 0.80
  reason: "Previous responses to similar situations were immediate"
```

**Key difference from voting:**

Voting model would count:
- WalkAway: 1 vote (1/3)
- RespondImmediately: 2 votes (2/3)
→ RespondImmediately wins by source count

Tendency model preserves:
- WalkAway has actual internal pressure of 0.38
- RespondImmediately has total internal pressure of 0.65 + 0.32 = 0.97
- The difference (0.59) represents the actual strength of conflict
- This is psychologically richer than just counting sources

**Conflict detection and representation:**

```
Competing actions detected:
  WalkAway (1 source, total strength 0.38)
  RespondImmediately (2 sources, total strength 0.97)

Conflict magnitude:
  Different actions proposed: YES
  Pressure differential: 0.97 - 0.38 = 0.59
  Conflict percentage: 0.59 / 0.97 = 61% margin in favor of RespondImmediately

Conflict sources:
  Goal-directed alone wants: WalkAway
  Reactive + Habit want: RespondImmediately

Conflict type: "Multi-source opposition"
Conflict level: "high" (60%+ margin, but clear internal disagreement)
```

### Explicit Model Parameters (NOT Hidden Assumptions)

The tendency competition model does NOT assume one subsystem is universally stronger. Instead, it uses explicit, tunable parameters:

**Parameter Set 1: Subsystem Weighting (per-subsystem influence)**

```python
subsystem_weights = {
    "goal_directed": 1.0,    # baseline
    "reactive": 1.0,         # baseline
    "habit": 1.0,            # baseline
}

# These weights allow us to say:
# "In this model, Goal-directed and Reactive have equal influence"
# 
# Later, these can be learned/adapted based on outcome quality:
# "When we weight Reactive 1.5× more heavily, outcomes improve"
```

**Weighted tendency calculation:**

```
weighted_tendency = normalized_strength * subsystem_weights[source]

Example:
  Goal-directed WalkAway: 0.38 × 1.0 = 0.38
  Reactive RespondImmediately: 0.65 × 1.0 = 0.65
  Habit RespondImmediately: 0.32 × 1.0 = 0.32
```

**Parameter Set 2: Convergence Bonus (optional)**

```python
convergence_bonus = 0.0  # Initially off

# If enabled, multiple sources toward same action could get a small boost:
# This would say: "agreement across independent systems adds some confidence"
# But this is OPTIONAL and EXPLICIT, not hidden in the voting mechanism
```

**Parameter Set 3: Confidence Modulation (per-subsystem)**

```python
confidence_impact = {
    "goal_directed": 0.85,   # How confident are we in goal system's assessment?
    "reactive": 0.95,        # How confident are we in reactive assessment?
    "habit": 0.80,           # How confident are we in habit prediction?
}

# Each subsystem reports its own confidence
# But the model can have a baseline about which subsystems to trust more
# This is explicit and can be tuned
```

**Key principle:**

Every weighting decision is explicit and written as a parameter. There are no hidden assumptions that "Reactive is always stronger" or "two sources always beat one." Those are design choices, not buried in the algorithm.

### Arbitration Process

Input to arbitration:
- All competing tendencies (not aggregated, each preserved)
- All normalized strengths
- All weights
- All confidence values
- All evidence and reasoning

Arbitration algorithm:

```
1. Calculate weighted strength for each tendency:
   weighted_strength[i] = tendency[i].normalized_strength * 
                          subsystem_weights[tendency[i].source] *
                          tendency[i].confidence

2. Group tendencies by action:
   actions_map = {}
   for tendency in tendencies:
       if tendency.action not in actions_map:
           actions_map[tendency.action] = []
       actions_map[tendency.action].append(tendency)

3. Calculate aggregate pressure for each action:
   action_pressure = {}
   for action, tendency_list in actions_map.items():
       action_pressure[action] = sum(t.weighted_strength for t in tendency_list)

4. Detect convergence and conflict:
   if all tendencies propose same action:
       conflict_level = "none"
   elif action_pressure values are very close (< 10% margin):
       conflict_level = "high"
   elif action_pressure has clear winner (> 50% margin):
       conflict_level = "moderate" or "mild"
   else:
       conflict_level = "high"

5. Select winning action:
   winning_action = action with highest action_pressure

6. Calculate margin of victory:
   pressure_values = sorted(action_pressure.values(), reverse=True)
   margin = pressure_values[0] - pressure_values[1] if len(pressure_values) > 1 else 1.0
   margin_percentage = margin / pressure_values[0]

7. Build competition result with full transparency:
   - Which action won
   - What was the total pressure for that action
   - Which systems contributed to it
   - What alternatives existed
   - How much margin of victory
   - What was the conflict structure
```

**Arbitration does NOT collapse tendencies into votes.** It evaluates competing psychological pressures and selects the action with the strongest aggregate internal pressure, while preserving all the information about WHY there was conflict and HOW it was resolved.

---

## SystemMemory Influence Stage

**Current problem:** SystemMemory adds fixed increments that can dominate by scale.

**Proposed solution:** SystemMemory acts as a context modulator, not a score adder.

**Mechanism: Multiplicative Adjustment**

Instead of adding points, SystemMemory scales the tendencies:

```
adjusted_strength = normalized_strength * system_memory_factor

where system_memory_factor is computed as:

base_factor = 1.0

if memory_supports_action:
    base_factor += 0.1  (up to +10% boost)
    
if memory_opposes_action:
    base_factor = max(0.5, base_factor - 0.3)  (down to 50%, not zero)

if action_violates_rule:
    base_factor = max(0.3, base_factor - 0.5)

final_factor = clamp(base_factor, 0.3, 1.3)  (keep factor in reasonable range)
```

**Example:**

- Goal-directed proposes WalkAway with normalized 0.45
- SystemMemory has a rule: "avoid looking weak" (opposes WalkAway in conflict situations)
- Memory factor: 0.8
- Adjusted strength: 0.45 × 0.8 = 0.36

This is a more subtle influence than adding +0.8 arbitrarily.

### Key principle: 
SystemMemory influence should never be larger than the original subsystem tendencies. It should modulate and adjust, not dominate.

**Important:** SystemMemory influences the TENDENCY, not the arbitration outcome directly. The arbitration process still evaluates all competing tendencies and selects the action with the strongest aggregate pressure. SystemMemory is a member of the competition process, not a separate layer.

---

## Arbitration Stage

**Goal:** Evaluate competing psychological pressures and select the action with the strongest aggregate internal pressure, while explicitly preserving all conflict information.

### Arbitration does NOT use voting; it evaluates tendencies

The arbitration algorithm preserves each subsystem's independent tendency and evaluates competing pressures rather than collapsing them into votes.

Input to arbitration:
- All BehavioralTendency objects (not aggregated)
- Normalized strengths for each
- All weights, confidence values, evidence
- SystemMemory influence information

Algorithm:

```
1. Apply weights to each tendency:
   weighted_strength[i] = tendency[i].normalized_strength * 
                          subsystem_weights[tendency[i].source] *
                          (1.0 + system_memory_adjustment)

   where:
   - subsystem_weights is explicit configuration (goal=1.0, reactive=1.0, habit=1.0)
   - system_memory_adjustment is the modulation factor (ranges -0.3 to +0.1)

2. Group tendencies by action and sum pressures:
   action_pressure = {}
   for each tendency:
       action = tendency.action
       pressure = weighted_strength + confidence_boost
       action_pressure[action] += pressure

3. Rank actions by aggregate pressure:
   ranked_actions = sort(action_pressure.items(), descending)

4. Analyze conflict structure:
   IF all tendencies point to same action:
       conflict_level = "none"
   ELIF top two actions are within 10% margin:
       conflict_level = "high"
   ELIF top action has 50%+ margin over runner-up:
       conflict_level = "mild" or "moderate"
   ELSE:
       conflict_level = "moderate"

5. Select action:
   selected_action = ranked_actions[0].action

6. Build CompetitionResult with full metadata:
   - selected_action and source systems that supported it
   - all competing alternatives and their pressures
   - margin of victory
   - conflict type and magnitude
   - evidence and reasoning for each contributing tendency
   - which systems disagreed and how
```

### Key Principle: Tendencies are Evaluated, Not Voted

**NOT this:**
```
Goal votes for WalkAway (1 vote)
Reactive votes for RespondImmediately (1 vote)
Habit votes for RespondImmediately (1 vote)
Result: RespondImmediately wins 2-1 by vote count
```

**THIS:**
```
Goal has internal pressure toward WalkAway: 0.38
Reactive has internal pressure toward RespondImmediately: 0.65
Habit has internal pressure toward RespondImmediately: 0.32

WalkAway total pressure: 0.38
RespondImmediately total pressure: 0.97

RespondImmediately is selected because aggregate internal pressure is stronger,
but we preserve:
- Goal had significant but overridden tendency (0.38)
- Reactive and Habit converged (0.65 + 0.32)
- Margin of victory (0.97 - 0.38 = 0.59, or 61%)
- Conflict type: Multi-source opposition
```

This preserves the psychological reality of internal competition.

### Conflict Representation

The arbitration result explicitly preserves conflict information:

```python
conflict_info = {
    exists: bool,                           # Was there internal disagreement?
    level: "none" | "mild" | "moderate" | "high",
    type: str,  # "unanimous", "coalition_override", "close_competition", etc.
    winning_action: str,
    runner_up_action: str,                  # What was the alternative?
    winning_pressure: float,                # Total internal pressure for winner
    runner_up_pressure: float,              # Total internal pressure for alternative
    margin_of_victory: float,               # Winner pressure - runner-up pressure
    margin_percentage: float,               # Margin / winner pressure
    
    # Detailed conflict structure:
    proposals_by_source: {
        "goal_directed": {action: str, pressure: float, confidence: float},
        "reactive": {action: str, pressure: float, confidence: float},
        "habit": {action: str, pressure: float, confidence: float},
    },
    
    system_memory_influence: {              # What did memory do?
        adjustments_applied: list[str],
        total_adjustment_factor: float,
    },
    
    reasons: {
        why_winner_won: list[str],          # Sources supporting winner
        why_runner_up_lost: list[str],      # What alternative existed
        conflict_resolution: str,            # How was conflict handled?
    }
}
```

**Example from insult scenario:**

```
Scenario: Person insulted, goal is to avoid conflict, habit is to respond immediately

Input tendencies (after normalization, before SystemMemory):
  Goal-directed: WalkAway (normalized 0.45, confidence 0.85)
  Reactive: RespondImmediately (normalized 0.65, confidence 0.95)
  Habit: RespondImmediately (normalized 0.32, confidence 0.80)

Weights applied (all subsystems at 1.0):
  Goal: 0.45 × 1.0 × 0.85 = 0.3825
  Reactive: 0.65 × 1.0 × 0.95 = 0.6175
  Habit: 0.32 × 1.0 × 0.80 = 0.256

SystemMemory influence (factor 0.8 for immediate response in conflicts):
  Goal: 0.3825 (no adjustment, memory is neutral)
  Reactive: 0.6175 × 0.8 = 0.494
  Habit: 0.256 × 0.8 = 0.205

Action pressures:
  WalkAway: 0.3825
  RespondImmediately: 0.494 + 0.205 = 0.699

Winner: RespondImmediately (0.699 > 0.3825)
Margin: 0.699 - 0.3825 = 0.3165 (45% margin)

Conflict representation:
{
    exists: true,
    level: "high",
    type: "coalition_override",
    winning_action: "RespondImmediately",
    runner_up_action: "WalkAway",
    winning_pressure: 0.699,
    runner_up_pressure: 0.3825,
    margin_of_victory: 0.3165,
    margin_percentage: 0.45,
    
    proposals_by_source: {
        "goal_directed": {"action": "WalkAway", "pressure": 0.3825, "confidence": 0.85},
        "reactive": {"action": "RespondImmediately", "pressure": 0.494, "confidence": 0.95},
        "habit": {"action": "RespondImmediately", "pressure": 0.205, "confidence": 0.80},
    },
    
    system_memory_influence: {
        adjustments_applied: ["multiplied by 0.8 (conflict-response dampening)"],
        total_adjustment_factor: 0.8,
    },
    
    reasons: {
        why_winner_won: [
            "Reactive system: high arousal (7/10), perceives social threat",
            "Habit system: learned pattern from previous similar situations",
            "Two subsystems converge on immediate response"
        ],
        why_runner_up_lost: [
            "Goal system: conflict avoidance goal is present but weaker than emotional pressure",
            "SystemMemory slightly dampened immediate response but not enough to override"
        ],
        conflict_resolution: "Emotional arousal + learned habit override strategic goal. \
SystemMemory attempted to modulate but did not prevent selection."
    }
}
```

This makes it explicit that there WAS internal conflict, what each system wanted, and HOW the conflict was resolved.

---

## Confidence Calculation Concept

**Current problem:** Confidence is computed as a ratio of aggregate scores, which doesn't actually measure decision certainty.

**Proposed solution:** Confidence is multi-factor, based on actual decision quality.

### Confidence Components:

1. **Margin of Victory Component** (40% weight)
   ```
   margin_score = min(margin_of_victory / 0.5, 1.0)
   
   (If margin > 0.5, full points; if margin < 0.1, low points)
   ```
   
   Rationale: Large margin means clear winner, higher confidence.

2. **Convergence Component** (30% weight)
   ```
   convergence_score = number_of_sources_agreeing / total_sources
   
   (If 2/2 sources agree, 1.0; if 1/3, 0.33)
   ```
   
   Rationale: Agreement across sources increases confidence.

3. **Source Confidence Component** (20% weight)
   ```
   source_confidence_score = average of source_confidence values
   
   (Each subsystem reports its own confidence; we average them)
   ```
   
   Rationale: If the winning source is itself uncertain, overall confidence is lower.

4. **Evidence Quality Component** (10% weight)
   ```
   evidence_score = length(supporting_evidence) / 3  (capped at 1.0)
   
   (Each piece of evidence supports the decision)
   ```
   
   Rationale: More supporting evidence = higher confidence.

### Final Confidence:

```
confidence = (
    0.40 * margin_score +
    0.30 * convergence_score +
    0.20 * source_confidence_score +
    0.10 * evidence_score
)

confidence = clamp(confidence, 0.0, 1.0)
```

**Example:**

```
RespondImmediately wins with:
- margin_score: 0.8 (52% margin)
- convergence_score: 0.67 (2 out of 3 sources agree)
- source_confidence_score: 0.8 (Reactive and Habit are both confident)
- evidence_score: 0.67 (2 pieces of evidence)

confidence = 0.40 * 0.8 + 0.30 * 0.67 + 0.20 * 0.8 + 0.10 * 0.67
confidence = 0.32 + 0.201 + 0.16 + 0.067
confidence = 0.748 → 75% confidence

This is more meaningful than "0.97 / 1.375 = 71%"
```

---

## Conflict Representation (Detailed)

The system should explicitly track and report internal conflict, not hide it.

### Types of Conflict:

1. **Direct Opposition**
   ```
   Goal wants: WalkAway (0.45)
   Reactive wants: RespondImmediately (0.65)
   
   Conflict type: "Direct opposition"
   Magnitude: high (different actions proposed)
   ```

2. **Partial Support**
   ```
   Goal wants: WalkAway (0.45)
   Reactive wants: RespondImmediately (0.65)
   Habit wants: RespondImmediately (0.32)
   
   Conflict type: "Majority override" or "Coalition"
   Magnitude: high (1 source vs. 2 sources)
   ```

3. **Weak Consensus**
   ```
   Goal wants: Negotiation (0.50)
   Reactive wants: Negotiation (0.48)
   Habit wants: Negotiation (0.49)
   
   Conflict type: "Weak consensus" or "Mild disagreement"
   Magnitude: none (all agree, but margins are small)
   ```

### Conflict Recording:

The arbitration result includes:

```python
conflict_report = {
    exists: bool,
    type: str,  # "direct_opposition", "coalition_override", "weak_consensus", etc.
    magnitude: str,  # "none", "mild", "moderate", "high"
    reasons: list[str],  # Why each system wanted what it wanted
    resolution: str,  # How was it resolved?
}
```

This is output to logs and available for learning (e.g., "when we override the goal, what's the outcome?").

---

## Feedback and Learning Connection

After the action is executed and outcome is observed:

### Pattern Adaptation (Unchanged core logic, but with new input)

```
Pattern learner receives:
  - Which behavioral tendency won (source system)
  - What was the conflict magnitude?
  - What was the selected action?
  - What was the observed outcome?

Pattern learner updates:
  - Pattern weight based on outcome
  - Conflict history (did this conflict pattern occur before?)
  - Outcome quality given the conflict state
```

### Habit Strength Updates (Refined)

```
Habit strength update receives:
  - Was this action proposed by Habit?
  - Did it win arbitration?
  - What was the outcome?
  - Was there conflict, and if so, what kind?

Updated habit strength formula could consider:
  - How often does this action succeed?
  - Does it succeed more when there's conflict?
  - Does it succeed more when reactive agrees?
  - How does it interact with goals?
```

### SystemMemory Belief Updates (New opportunity)

```
SystemMemory can track:
  - Did our rules/beliefs predict the right action?
  - When SystemMemory influence changed the outcome, was it good or bad?
  - Should we adjust our rules based on this conflict resolution?
```

### Conflict Learning (New)

```
A new learning path could emerge:
  - Track when conflicts occur
  - Track how they are resolved
  - Track outcomes of different conflict resolutions
  - Build a "conflict history" that informs future decisions

Example: "When Goal and Reactive disagree, Reactive usually wins and outcomes are mixed. 
When they agree, outcomes are good. Perhaps we should weight goal-directed more heavily 
when there's agreement."
```

---

## Example: Insult Scenario Walkthrough (Tendency Competition Model)

### Setup

```
PersonState:
  - Current emotion: angry (arousal 7/10)
  - Active goal: avoid conflict
  - Relationship: friendly (with insulter)
  - Habit history: respond to insults immediately
  - Config: subsystem_weights = {goal: 1.0, reactive: 1.0, habit: 1.0}
```

### Proposal Stage (Raw Tendencies)

**Goal-directed system:**
- Active goal: avoid conflict
- Proposes: WalkAway
- Raw strength: 45.0 (goal-satisfaction estimate)
- Confidence: 0.85 (goal is clear, action is feasible)
- Reasoning: "Goal is to avoid conflict; WalkAway achieves this."

**Reactive system:**
- Current emotion: angry
- Arousal level: 7/10
- Proposes: RespondImmediately
- Raw strength: 70.0 (high arousal, social threat)
- Confidence: 0.95 (arousal is clear)
- Reasoning: "Immediate social threat; respond to defend."

**Habitual system:**
- Learned pattern: respond to insults
- Pattern strength: 3.2 (learned habit from repetition)
- Proposes: RespondImmediately
- Raw strength: 32.0 (habit strength scaled up)
- Confidence: 0.80 (pattern is clear)
- Reasoning: "This situation triggers learned response."

### Normalization Stage

```
Goal-directed:
  Raw: 45.0 (scale: 0-100)
  Normalized: 45.0 / 100.0 = 0.45
  Confidence: 0.85
  
  BehavioralTendency {
    action: "WalkAway",
    raw_strength: 45.0,
    normalized_strength: 0.45,
    source: "goal_directed",
    confidence_in_proposal: 0.85,
    evidence: ["conflict avoidance goal", "strategy is clear"]
  }

Reactive:
  Raw: 70.0 (scale: 0-100)
  Normalized: 70.0 / 100.0 = 0.70
  Confidence: 0.95
  
  BehavioralTendency {
    action: "RespondImmediately",
    raw_strength: 70.0,
    normalized_strength: 0.70,
    source: "reactive",
    confidence_in_proposal: 0.95,
    evidence: ["high arousal (7/10)", "social threat perceived"]
  }

Habitual:
  Raw: 32.0 (scale: 0-10, scaled up to 0-100 range)
  Normalized: min(32.0 / 10.0, 1.0) = 0.32
  Confidence: 0.80
  
  BehavioralTendency {
    action: "RespondImmediately",
    raw_strength: 32.0,
    normalized_strength: 0.32,
    source: "habit",
    confidence_in_proposal: 0.80,
    evidence: ["learned response pattern", "12 previous similar situations"]
  }
```

### SystemMemory Influence Stage

SystemMemory analysis:
- Belief: "Relationships are valuable; protect them"
- Rule: "In conflict, consider stepping back"
- For RespondImmediately in this context: memory factor = 0.8 (slightly dampens immediate response)
- For WalkAway in this context: memory factor = 1.0 (neutral, doesn't oppose)

```
Goal-directed WalkAway:
  Pre-adjustment: 0.45
  Memory factor: 1.0
  Post-adjustment: 0.45 × 1.0 = 0.45

Reactive RespondImmediately:
  Pre-adjustment: 0.70
  Memory factor: 0.8
  Post-adjustment: 0.70 × 0.8 = 0.56

Habitual RespondImmediately:
  Pre-adjustment: 0.32
  Memory factor: 0.8
  Post-adjustment: 0.32 × 0.8 = 0.256
```

### Weighting Stage (Apply subsystem weights)

Subsystem weights (all baseline 1.0):
```
Goal-directed: 1.0
Reactive: 1.0
Habit: 1.0
```

Weighted tendencies:
```
Goal WalkAway:
  weighted = 0.45 × 1.0 × 0.85 = 0.3825

Reactive RespondImmediately:
  weighted = 0.56 × 1.0 × 0.95 = 0.532

Habitual RespondImmediately:
  weighted = 0.256 × 1.0 × 0.80 = 0.2048
```

### Competition Stage (Pressure Aggregation)

All tendencies are evaluated; those for the same action are aggregated:

```
WalkAway total pressure:
  From Goal-directed: 0.3825
  Total: 0.3825

RespondImmediately total pressure:
  From Reactive: 0.532
  From Habitual: 0.2048
  Total: 0.7368

Ranking:
  1. RespondImmediately: 0.7368 (61% of total competition)
  2. WalkAway: 0.3825 (39% of total competition)
```

### Conflict Detection

```
Different actions proposed: YES
Margin: 0.7368 - 0.3825 = 0.3543
Margin percentage: 0.3543 / 0.7368 = 48%

Conflict structure:
  Goal-directed wants: WalkAway (0.3825)
  Reactive + Habitual want: RespondImmediately (0.7368)

Conflict level: "high"
  (Clear opposition, but not a razor-thin margin)

Conflict type: "Coalition override"
  (Two systems agree; they override one system)
```

### Arbitration Decision

Winner: RespondImmediately (0.7368 > 0.3825)

CompetitionResult:
```
{
    selected_action: "RespondImmediately",
    selected_source: "reactive + habit coalition",
    final_strength: 0.7368,
    conflict_level: "high",
    conflict_sources: ["goal_directed", "reactive", "habit"],
    conflict_margin: 0.48,
    
    all_proposals: [
        BehavioralTendency(goal_directed, WalkAway, 0.3825),
        BehavioralTendency(reactive, RespondImmediately, 0.532),
        BehavioralTendency(habit, RespondImmediately, 0.2048)
    ],
    
    reasoning: """
    CONFLICT DETECTED: Goal system (WalkAway, 0.38) opposes Reactive+Habit coalition (RespondImmediately, 0.74).
    
    Two internal systems converge:
      - Reactive (high arousal, social threat): 0.532 pressure
      - Habit (learned pattern): 0.205 pressure
    
    One internal system opposes:
      - Goal (conflict avoidance): 0.382 pressure
    
    SystemMemory slightly modulated the immediate-response systems (×0.8 factor) due to 
    relationship-preservation beliefs, but the coalition remained stronger.
    
    RESOLUTION: Emotional arousal + learned habit (total 0.737) > Strategic conflict-avoidance goal (0.382).
    Margin of victory: 48%. High confidence in execution because two subsystems agree.
    """,
    
    conflict_info: {
        exists: true,
        level: "high",
        type: "coalition_override",
        winning_action: "RespondImmediately",
        runner_up_action: "WalkAway",
        winning_pressure: 0.7368,
        runner_up_pressure: 0.3825,
        margin_of_victory: 0.3543,
        margin_percentage: 0.48
    }
}
```

### Outcome and Learning

Person responds immediately → escalation → argument → relationship damage

Feedback received by learning systems:

```
Pattern learner:
  - Pattern "respond_to_insult" → outcome "escalation"
  - This outcome was negative (damages relationship)
  - Update: weaken pattern weight

Habit formation:
  - Habit was used; outcome was negative
  - This was a high-conflict override situation (goal was strongly opposed)
  - Update: habit strength slightly decremented; mark as "conflicts with goal"

SystemMemory learning:
  - Our belief (protect relationship) was correct
  - Our influence (0.8 factor) was not strong enough
  - Could later adapt: increase influence weight, OR recognize immediate
    emotions are hard to override

Conflict learning:
  - Recorded: Goal vs. Reactive+Habit conflict → Reactive+Habit won → Negative outcome
  - This builds a history: "When goal is overridden by emotional+habitual coalition, 
    outcomes tend to be negative. Perhaps need to strengthen goal-directed system?"
```

This walkthrough shows how tendencies are evaluated as competing internal pressures, 
not votes. The system preserves the detailed structure of the conflict and can learn 
from how it was resolved.

---

## What Changes in Python Code

### Files that will need modification (do not change yet):

1. **action_selection.py**
   - Change `propose_goal_directed()`, `propose_habitual()`, `propose_reactive()` to return `BehavioralTendency` objects instead of simple scores
   - Include confidence estimates in each proposal
   - Remove the simple scoring; return structured data

2. **arbitration.py**
   - Replace additive score aggregation with normalization stage
   - Implement vote-based competition model
   - Add conflict detection and representation
   - Calculate multi-factor confidence
   - Return `CompetitionResult` with full metadata

3. **system_memory.py**
   - Change from additive score modification to multiplicative factor adjustment
   - OR use preference adjustment mode
   - Return influence metadata with the adjusted strengths

4. **New file: normalization.py** (optional but recommended)
   - Isolate normalization logic in a dedicated module
   - Make it easy to tune scales for each subsystem
   - Provide visibility into normalization process

5. **pattern_adaptation.py**
   - Extend to receive conflict information
   - Allow learning based on conflict type and resolution

6. **habit_formation.py**
   - Extend to receive conflict information
   - Allow habit strength updates to account for conflict history

### Files that should NOT change (yet):

- `main.py` - Flow remains the same, just passes richer data structures
- `pattern_learner.py` - Core learning logic remains similar
- `person_state.py` - State tracking remains similar

### New concepts to track:

- Normalized vs. raw strengths (for transparency)
- Conflict history (for learning)
- System influence metadata (for debugging)

---

## Architecture Principles (Preserved)

1. **Modularity:** Each subsystem (Goal, Habit, Reactive) remains independent and generates its own proposal.

2. **Staged pipeline:** PersonState → Proposal → Normalization → Competition → Arbitration → Behavior → Learning.

3. **Transparency:** Every decision can be inspected: raw strengths, normalized values, conflict info, margin, confidence basis.

4. **Deterministic:** No randomness; same input → same output.

5. **Learning:** Outcomes feed back to adapt patterns, habits, and system memory.

---

## Summary: The Core Shift

| Aspect | Current | Proposed |
|--------|---------|----------|
| Subsystem signals | Raw, incomparable scores | Normalized tendencies with metadata |
| Competition | Addition of raw scores | Vote-based weighted aggregation |
| SystemMemory role | Fixed score additions | Contextual multiplicative adjustment |
| Conflict handling | Ignored; hidden in score | Explicitly detected and preserved |
| Confidence | Numeric ratio of totals | Multi-factor quality measure |
| Habit representation | Direct action value | Behavioral tendency with learned strength |
| Arbitration result | Just the winning action | Full `CompetitionResult` with conflict info |
| Learning input | Simple outcome signal | Outcome + conflict context + source info |

---

## Next Steps (After Design Approval)

1. Implement BehavioralTendency and related data classes
2. Create normalization stage and test scale calibration
3. Refactor arbitration to use vote-based competition
4. Add conflict detection and representation
5. Implement multi-factor confidence calculation
6. Update SystemMemory influence to multiplicative model
7. Test with existing scenarios to verify behavior
8. Update habit and pattern learning to use conflict context
9. Validate that the architecture still behaves as expected

---

## Questions for Review

Before implementation:

1. **Normalization scales:** Are the proposed scales (0-100 for goal/reactive, 0-10 for habit) accurate, or should they be different?

2. **Multiplicative vs. additive:** Is multiplicative adjustment (Mode A) the right model for SystemMemory influence, or should we use additive (Mode B)?

3. **Confidence weights:** Should the weights (40% margin, 30% convergence, 20% source, 10% evidence) be different?

4. **Conflict priority:** When there is conflict, should goal-directed have priority in tie-breaking, or should this be different?

5. **Learning scope:** Should habit strength learning include conflict history, or is outcome-based learning sufficient?

6. **Future subsystems:** Are there any constraints on how a new behavioral subsystem should be added to preserve modularity?

