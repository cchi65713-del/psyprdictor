# Architecture observations from the multi-scenario run

## Summary

The five scenarios show that the current architecture is producing genuine internal competition between behavioral influences rather than a single deterministic policy. The system is no longer acting like a single scorer; it is behaving like a layered arbitration problem with multiple subsystems influencing the final decision.

## 1. Which systems agreed

The clearest agreements occurred in the repeated-conflict and walk-away scenarios.

- Repeated conflict / insult:
  - Reactive pushed strongly toward RespondImmediately.
  - Habit also pushed toward RespondImmediately.
  - Goal-directed had a small push for RespondImmediately as well.
  - SystemMemory reinforced the immediate-response rule and belief.
  - Result: all major influences aligned on a single action.

- Walk away beneficial:
  - Goal-directed strongly preferred WalkAway because of the safety need.
  - Habit also preferred WalkAway because it had learned that pattern.
  - Reactive did not oppose strongly, and SystemMemory did not add a competing push.
  - Result: the action was not contested much and the winning action was consistent with the current situation.

## 2. Which systems conflicted

The strongest conflicts were in the minor disagreement, stay-quiet scenario, and the habit-vs-goal conflict scenario.

- Minor disagreement:
  - Goal-directed preferred Negotiation due to harmony/value alignment.
  - Reactive preferred StayQuiet / low-arousal response.
  - Habit suggested WalkAway because of learned patterns.
  - SystemMemory strengthened Negotiation.
  - Result: there was a true conflict between Goal, Habit, and Reactive tendencies.

- Stay quiet beneficial:
  - Goal-directed preferred Negotiation due to value alignment.
  - Reactive preferred StayQuiet.
  - SystemMemory added a rule to avoid confrontation in meetings and nudged StayQuiet/WalkAway.
  - Habit was empty in this scenario because no strong learned habit existed yet.
  - Result: Reactive and Goal directed were in tension, with SystemMemory adding a competing pressure.

- Habit vs goal conflict:
  - Habit strongly preferred RespondImmediately.
  - Reactive strongly preferred RespondImmediately.
  - Goal-directed preferred WalkAway to avoid conflict.
  - Result: the architecture demonstrated the intended pattern: different subsystems pushing in opposite directions before arbitration.

## 3. Which system dominated arbitration in each scenario

- Repeated conflict / insult: SystemMemory + Reactive dominated arbitration, with Habit also contributing. Final selection: RespondImmediately.
- Minor disagreement: Goal-directed dominated arbitration, with SystemMemory reinforcing the same choice. Final selection: Negotiation.
- Walk away beneficial: Goal-directed dominated arbitration, supported by Habit. Final selection: WalkAway.
- Stay quiet beneficial: Goal-directed dominated arbitration, but only narrowly; Reactive and SystemMemory were meaningful competing pressures. Final selection: Negotiation.
- Habit vs Goal conflict: Reactive dominated, with Habit supporting the same choice. Goal-directed was still active but weaker. Final selection: RespondImmediately.

## 4. How SystemMemory changed the competition

SystemMemory had a clear effect on how strongly certain actions were favored.

- In repeated conflict, it strengthened immediate response through the rule and belief about defending respect.
- In minor disagreement, it reinforced Negotiation by aligning with the value of harmony.
- In stay-quiet beneficial, it pushed StayQuiet and WalkAway because the rule said to avoid confrontation during meetings.
- In the habit-vs-goal conflict case, SystemMemory did not add a strong competing pressure, so the decision remained dominated by emotional and habitual tendencies.

In other words, SystemMemory is not just a static background; it actively changes the score landscape and can tilt arbitration without replacing other systems.

## 5. How habit strength affected the final decision

Habit strength had an observable effect.

- In repeated conflict, Habit increased the support for RespondImmediately and reinforced the same choice as the emotional system.
- In minor disagreement, Habit pulled toward WalkAway, but its influence was weaker than Goal-directed + SystemMemory preferences.
- In walk-away beneficial, Habit was useful because the scenario had repeated walk-away patterns.
- In the habit-vs-goal conflict case, Habit was a major factor in favoring RespondImmediately, even though the current goal was avoid_conflict.

This is a key result: habit is now a real competing force, not a manually assigned override. It emerges from repeated experiences and can oppose current goals.

## 6. Did the selected behavior follow from the competing influences?

Mostly yes.

Across the scenarios, the winning action generally matched the strongest source stack:

- When Reactive + Habit + SystemMemory agreed, the action was strongly immediate and resulted in RespondImmediately.
- When Goal-directed + SystemMemory explained the situation, the action often landed on Negotiation or WalkAway.
- When the systems disagreed, arbitration produced a winner that was consistent with the highest aggregate contribution, even when the winner was not the current goal.

This means the behavior is not arbitrary; it is a direct result of the competition itself.

## 7. Architectural problems or artificial assumptions

The current model is working as an internal-competition architecture, but several weaknesses are visible:

1. Scoring is still heuristic-heavy.
   - Many actions are rewarded by hand-written weights and simple condition checks.
   - This makes the system explainable but somewhat brittle.

2. Arbitration is still a simple argmax.
   - It chooses the strongest score, but does not represent action conflict or uncertainty explicitly.
   - It also does not surface the full qualitative tradeoff in an ideal way.

3. Habit strength is still a derived scalar, not a richer memory object.
   - It is useful, but it does not yet track why a habit formed or what context made it strong.

4. SystemMemory effect is still rule-based and coarse.
   - It serves the intended purpose, but it is still somewhat hard-coded to a few patterns.

5. The model sometimes produces results that feel artificially forced.
   - For example, in the habit-vs-goal conflict scenario, the emotional and habitual push can overpower the goal despite an explicit avoid_conflict objective.
   - This is not a bug; it is an important sign that the architecture is genuinely modeling competition.

## Bottom line

The current model is doing what we wanted it to do: it is representing internal competition between Goal, Habit, Reactive states, and SystemMemory before a behavior is selected.

The most important finding is not that one system always wins. It is that the architecture can produce meaningful disagreement between internal tendencies, and that arbitration is the place where those pressures are resolved.

This is now a genuine competing-subsystems system, not just a list of scoring heuristics.
