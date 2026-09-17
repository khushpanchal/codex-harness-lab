# What I would run next (designed, not run — budget exhausted)
Ordered by expected information per dollar. Each keeps the frozen benchmark and adds arms beside it.

1. **N-version validation on long-horizon tasks.** Every null here is on <10-minute single-file tasks where the agent
   already verifies well (83% mutation kill, self-check in 96% of runs). The mechanism should matter where the agent
   cannot hold the whole spec: multi-file repo tasks with 30+ minute budgets. Needs a task family with hidden tests over
   a real repo (e.g. mutate a pure-python library and hide its suite), ~40 tasks x 3 seeds x 2 arms, ~$25 at glm prices.
2. **Cross-model replication of the alarm-precision result** (the one solid finding): tester+independent implementation
   from 3 model families x 30 tasks, scored offline against reference solutions. ~$3, no agent runs needed.
3. **Raise the alarm rate.** Validated alarms fired in only 18% of runs because the independent implementation shares the
   agent's misreadings. Try: (a) independent implementation from a *different model family*, (b) k=3 impls with any-of-3
   (offline: precision 66%, recall 83%), (c) generating tests from the spec's worked examples only (highest-precision subset).
4. **Spend the same money on the actual bottleneck: convention ambiguity.** 25% -> 91% pass when half the tests are
   visible. A harness mechanism that surfaces *interface* ambiguity (e.g. proposing the 2-3 plausible API contracts and
   asking one cheap question, or probing existing callers) plausibly beats any verification feature. Measure: pass rate
   on the original (zero-visible-test) variant, where all four ideas tested here are irrelevant.
5. **Probe replay on regression-prone work.** It was a no-op here because single-file tasks have nothing to regress.
   Re-test on tasks that require editing code with existing passing behavior (library mutation tasks from #1).
