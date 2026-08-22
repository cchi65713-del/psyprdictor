# Scoring and Arbitration Review

## What currently works

The model has achieved a meaningful structural milestone: it is no longer a single linear predictor. It now has a layered decision process:

- PersonState holds the current situation and internal state.
- Goal-directed, Habitual, and Reactive systems each generate an action tendency.
- SystemMemory adjusts those tendencies according to beliefs, values, rules, relationships, and environmental context.
- Arbitration combines them and selects one action.
- That selected action feeds outcome and learning.

This is structurally aligned with the intended architecture:

- tendency generation
- competition between tendencies
- arbitration
- behavior selection
- outcome
- learning and adaptation

The five scenario runs demonstrated that this process is materially real:

- repeated conflict pushed RespondImmediately
- minor disagreement produced Negotiation
- walk-away situations produced WalkAway
- a conflict between habit and goal produced a real internal dispute

This is a genuine improvement over a single score-based action rule.

## What is structurally correct

The current implementation does represent the right conceptual sequence, at least at a high level:

1. Different internal systems produce separate action proposals.
2. Each proposal carries some reason and some magnitude.
3. SystemMemory acts as a modulatory layer rather than a separate action generator.
4. Arbitration resolves competition by selecting the strongest aggregate action.
5. Learning and habit formation occur after the selected behavior.

This is structurally correct for the architecture that we have been building:

- Goal-directed system = current goals / needs / values / constraints
- Habitual system = previously learned repeated response pattern
- Reactive system = current emotional and arousal state
- SystemMemory = identity-level memory and learned rules
- Arbitration = action selection between competing tendencies

The system is therefore not simply a scoring hack; it is at least representing an internal competition model.

## What is an artificial shortcut

The main issue is not that the model is conceptually wrong; it is that the implementation is still using a very simplified numerical approximation of psychological competition.

### 1. Raw score summation

Each system emits a score for each action, and the implementation adds them together in a single aggregate vector. This is a useful prototype, but it is an artificial shortcut. It assumes: 

- all systems are operating on the same scale;
- different systems are commensurate;
- additive combination is a reasonable approximation of competition.

This may be acceptable as a first pass, but it is not psychologically faithful by itself.

### 2. Score comparability

Goal-directed scores, Reactive scores, and Habit scores are not obviously on the same scale.

Examples:

- a goal may represent a long-term strategic objective;
- a habit may represent a repeated response tendency;
- a reactive signal may represent immediate salience and arousal.

Those are not necessarily comparable in the same way as direct action utility values. Yet they are currently treated as additive numeric values with no explicit calibration or normalization.

### 3. SystemMemory score scale

SystemMemory is especially vulnerable to scale distortion.

It is implemented as a fixed set of weighted increments such as:

- +0.8 for a rule
- +0.5 for a belief
- +0.6 for a rule about confrontation avoidance

These increments are not normalized relative to the strength of other systems. Because of this, SystemMemory can dominate arbitration simply because it has a large additional score even when it is not the deepest or most context-sensitive factor.

This is a real risk: the architectural role of SystemMemory is to reshape tendencies, but the current code sometimes makes it behave like a stronger system by raw arithmetic.

### 4. Habit strength treated like action utility

Habit strength is meant to represent a learned tendency, not the direct probability of the best action. But in current code, it is used as a value added directly to a proposal score.

That means the system is treating a habit as if it were a direct action payoff estimate, rather than a learned tendency that competes with other tendencies. This is not completely wrong, but it is conceptually simplified.

A habit should ideally be treated as:

- a tendency with context dependency
- perhaps a bias or prior
- not automatically equivalent to action probability or best action choice

The current implementation blurs that boundary.

## Potential scoring problems

### 1. No normalization across systems

The most important problem is that the systems are not normalized before they are added. Each system uses its own heuristics and roughly similar value ranges, but not necessarily calibrated ranges.

This creates the danger that one system's raw scoring scale overwhelms another.

### 2. Same action can be boosted by multiple systems without representing distinct causes

The current aggregation is additive and non-differentiated. If Reactive and Habit both push RespondImmediately, the final score is inflated, but the code does not distinguish between:

- a true convergence of independent causes
- a duplication of the same underlying tendency
- a contextually redundant boost

This may be okay for a prototype, but it is not a subtle representation of competing processes.

### 3. Goal-directed and Habitual are not always measured on the same basis

Goal-directed proposals use context, values, beliefs, and needs. Habitual proposals use learned action supports from past patterns. Reactive proposals use emotional and arousal measures.

These are conceptually different categories of evidence. The fact that they are numerically summed does not mean they are equivalent evidence types.

### 4. Confidence is not meaningful in the current form

The arbitration confidence is computed as:

- chosen_score / total_score * 100

This produces a number, but it is not a psychologically meaningful confidence. It is simply a normalized score ratio.

This does not mean:

- the system is more certain;
- the action is more justified;
- the action is more likely to succeed in a real-world sense.

It only means the chosen score was large relative to other scores. That is not the same thing as informed or calibrated confidence.

## Potential arbitration problems

### 1. Argmax is a shortcut, not a decision-theoretic model

The current arbitration is effectively:

- compute total score for each action
- choose the largest score

This is a valid prototype, but it is not equivalent to a full arbitration strategy that distinguishes:

- strong conflicting tendencies
- low confidence due to conflicting evidence
- uncertainty in the signal itself
- action cost vs. action value

The model still collapses the entire internal competitive process into a single winner without preserving conflict information.

### 2. The arbitration reason is descriptive, but not explanatory enough

The current reason string is useful for debugging, but it is still a summary of numerical contributions, not a representation of the actual competition dynamics.

It says which systems contributed to the final action, but not:

- whether those contributions were complementary or contradictory
- whether the system was a first-order or second-order influence
- whether the winning action was selected despite a strong opposing tendency

That is useful for observability, but it does not yet represent the full decision-making structure.

### 3. The model may be overvaluing a single large tendency

Because the additive model can produce dominance from one large source, the selected action may simply reflect the largest numerical contribution rather than the most coherent decision profile.

This matters because the architecture intends to represent internal process competition, not just largest-number-wins.

## What should remain unchanged

Several parts of the design are already correct and should remain as-is for now:

- The separation of Goal-directed, Habitual, Reactive systems
- The use of PersonState as the central state container
- SystemMemory as a source of persistent rules and values
- PatternLearner and PatternAdaptation as the learning/adaptation layer
- The fact that arbitration happens after proposal generation
- The fact that action selection feeds outcome and feedback

These are worth preserving because they reflect the actual architecture we want to test.

## What needs refinement later

The next refinement should not be a new psychological model; it should be a more faithful representation of the same architecture.

Likely areas for later refinement:

1. Normalize system scores before aggregation
   - calibrate each system's scale
   - permit comparison without artificial raw-score dominances

2. Separate tendency strength from action utility
   - habit and reactive tendencies should not necessarily be treated as direct action payoffs

3. Add a true arbitration representation
   - preserve conflict and uncertainty rather than only argmax

4. Make SystemMemory influence context-sensitive and proportional
   - not just a fixed rule bonus

5. Represent habit as stateful tendency, not simply a scalar support value
   - include context, recency, and contradictory evidence more explicitly

6. Clarify confidence semantics
   - if confidence is kept, it should reflect decision certainty, not simply numerical spread

## Final assessment

The current architecture is closer to a valid competing-subsystems model than it is to a single scoring function. It is meaningfully representing the intended flow:

- tendency generation
- competition
- arbitration
- behavior
- learning

But the present implementation is still a simplified additive approximation of competition. That is acceptable for a prototype, but it is not yet a strong representation of how different internal processes should truly be compared and resolved.

In other words:

- The model is conceptually right.
- The implementation is structurally promising.
- The numerical combination process is still an artificial shortcut.
- The architecture is good to keep, but the scoring and arbitration layer is the first place that needs more careful design before further expansion.

That is the main architectural conclusion from the current state: the structure is right, but the numerical competition mechanism is still a prototype approximation rather than a psychologically grounded arbitration model.
