# Herbie egglog performance chart

Figure for https://github.com/herbie-fp/herbie/pull/1697. This artifact branch hosts the PR-description image and its source data separately from the code change.

`ratios.png` and `ratios.svg` show one after/before ratio and independent-sample 95% Fieller interval per benchmark. Before is Herbie main's current experimental dependency; after is the optimized dependency and the default launch flags in the PR. `measurements.json` records the exact revisions, four complete block sums per endpoint, estimates, interval endpoints, and source evidence hash. The main-only upgrade control is retained as a mean in that data.

Each block value sums standalone CLI wall times for every captured egglog file belonging to that benchmark. It includes startup, extraction and output. All 33 benchmarks and 211 captured programs are retained. Engine runs use one thread and proofs off. Warmups are excluded. Intervals use Student t with 3 degrees of freedom; they are marginal and have no multiple-comparison correction. No overall mean is computed, and these are not end-to-end Herbie or native egg timings.

Render and verify the confidence intervals from the stored block measurements:

```sh
uv run --with matplotlib --with scipy python build_chart.py
```

No benchmarks are executed by the rendering script.
