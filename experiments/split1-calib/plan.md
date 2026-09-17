# split1 calibration (setup)
Benchmark variant tasks_split1: agent sees only the FIRST test (API shape), grader runs full suite.
Held-out-half variant (tasks_split) hit the ceiling: base 21/23 = 91% pass (vs ~25% on original) -> unusable for A/B.
Run: base (codex-lab-all, no flags), 2 seeds x 56 tasks, glm-5.3-flash, $0.03/run cap. Budget <= $0.70, <= 40 min.
Goal: find tasks with mixed outcomes for the repeated-seed A/B.
