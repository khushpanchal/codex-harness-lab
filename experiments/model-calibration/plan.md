# Exp 0 — model calibration (setup, not an idea)
Goal: pick the cheapest model that can do the tasks with a mid-range pass rate (so harness ideas can move it).
Arms: deepseek/deepseek-v4-flash, qwen/qwen3-coder-30b-a3b-instruct, openai/gpt-oss-120b, z-ai/glm-5.3-flash
Tasks: bench/subsets/calib14.txt, 1 seed each = 56 runs, parallel 8 per model.
Metrics: pass rate (hidden tests), mean tests-passed fraction, cost/run, wall/run.
Limits: 15 min per run (hard kill), total wall <= 60 min, total cost <= $1.00.
