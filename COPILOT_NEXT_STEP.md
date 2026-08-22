> **Next step: connect `SystemMemory` to the existing Action Selection + Arbitration pipeline.**
>
> Do not redesign the architecture or remove existing functionality.
>
> Use the current `PersonState`, `SystemMemory`, `action_selection.py`, `arbitration.py`, `PatternLearner`, and `PatternAdaptation`.
>
> ### Goal
>
> Make the person's internal system influence which candidate behaviors/actions are selected.
>
> The flow should become:
>
> `PersonState → Pattern Recognition → Candidate Actions → System Memory Influence → Arbitration → Selected Action → Outcome → Learning`
>
> `SystemMemory` should influence action scores using the person's:
>
> * beliefs
> * values
> * needs
> * goals
> * preferences
> * personality
> * identity
> * history
> * relationships
> * rules
> * environment
>
> For example, a rule such as **"When attacked, respond immediately"** should increase the tendency toward an immediate-response action, while a conflicting internal preference such as avoiding confrontation could increase another action.
>
> **Important:** do not hard-code one specific person or one specific outcome. Build it as a reusable mechanism that can work with different `PersonState`/`SystemMemory` configurations.
>
> Keep the existing prediction and learning pipeline working.
>
> Add clear printed output showing:
>
> 1. Candidate actions
> 2. Base action scores
> 3. System-memory influences
> 4. Adjusted action scores
> 5. Arbitration result
> 6. Selected action
> 7. Simulated outcome
> 8. Feedback/learning update
>
> Run `main.py` after the changes and verify that the complete pipeline works.
>
> **Do not move on to probabilistic/softmax arbitration yet.** We want to verify the deterministic system-memory influence first.
>
> Before changing anything, inspect the existing files and preserve the architecture we already built.
