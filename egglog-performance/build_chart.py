#!/usr/bin/env python3
"""Render the published before/after measurements; no benchmarks are executed.

uv run --with matplotlib --with scipy python build_chart.py
"""
import hashlib
import json
import math
import statistics
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import t

root = Path(__file__).resolve().parent
data = json.loads((root / 'measurements.json').read_text())
rows = data['benchmarks']
assert len(rows) == 33 and len({r['name'] for r in rows}) == 33
for row in rows:
    before, after = row['before_blocks_ms'], row['after_blocks_ms']
    assert len(before) == len(after) == 4
    a, b = statistics.fmean(before), statistics.fmean(after)
    va, vb = statistics.variance(before) / 4, statistics.variance(after) / 4
    q = float(t.ppf(.975, 3)) ** 2
    aa, dd = a * a - q * va, b * b - q * vb
    assert aa > 0
    delta = math.sqrt((a * b) ** 2 - aa * dd)
    recomputed = (b / a, (a * b - delta) / aa, (a * b + delta) / aa)
    assert all(math.isclose(x, row[k], rel_tol=1e-12, abs_tol=1e-12)
               for x, k in zip(recomputed, ['ratio', 'ci_low', 'ci_high']))

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.labelcolor': '#30343b', 'text.color': '#20252c',
                     'xtick.color': '#505761', 'ytick.color': '#30343b',
                     'svg.fonttype': 'none'})
fig, ax = plt.subplots(figsize=(10.4, 14.0), facecolor='white')
fig.subplots_adjust(left=.49, right=.955, top=.89, bottom=.10)
blue = '#2165a8'
y = list(range(len(rows)))
for i in y:
    if i % 2 == 0:
        ax.axhspan(i - .48, i + .48, facecolor='#f5f7f9', zorder=0)
ax.axvline(1, color='#555d68', linestyle=(0, (4, 3)), linewidth=1.15, zorder=1)
ax.errorbar([r['ratio'] for r in rows], y,
            xerr=[[r['ratio']-r['ci_low'] for r in rows],
                  [r['ci_high']-r['ratio'] for r in rows]],
            fmt='o', markersize=4.6, capsize=2.5, linewidth=1.35,
            color=blue, ecolor=blue, zorder=3)
ax.set_yticks(y, [textwrap.fill(r['name'], width=44, break_long_words=False) for r in rows])
ax.tick_params(axis='y', length=0, pad=11, labelsize=10.5)
ax.set_ylim(len(rows)-.4, -.6)
ax.set_xlim(.72, 1.07)
ax.set_xticks([.75, .80, .85, .90, .95, 1, 1.05],
              ['0.75', '0.80', '0.85', '0.90', '0.95', '1.00', '1.05'])
ax.tick_params(axis='x', length=3, pad=6, labelsize=10.5)
ax.xaxis.grid(True, color='#e3e7ec', linewidth=.65)
ax.set_axisbelow(True)
for name in ('left', 'top', 'right'):
    ax.spines[name].set_visible(False)
ax.spines['bottom'].set_color('#aab2bc')
ax.set_xlabel('Execution-time ratio  (after / before)', labelpad=10, fontsize=12)
fig.text(.035, .967, 'Egglog performance in Herbie', fontsize=19, fontweight='bold', va='top')
fig.text(.035, .939, 'One point per benchmark · 95% Fieller confidence intervals', fontsize=12, va='top')
fig.text(.035, .914, 'Before: current dependency     After: this PR', fontsize=11.5, va='top')
ax.text(.72, 1.012, '← Faster', transform=ax.get_xaxis_transform(), fontsize=10.5, ha='left')
ax.text(1, 1.012, 'No change', transform=ax.get_xaxis_transform(), fontsize=10.5, ha='center')
fig.text(.035, .045, '211 fixed .egg files across 33 benchmarks · 4 measured blocks per endpoint', fontsize=10.5)
fig.text(.035, .029, 'Each benchmark sums its standalone file executions. Single thread; proofs off.', fontsize=10.5)
fig.text(.035, .013, 'Marginal 95% intervals; no multiple-comparison correction. No overall average.', fontsize=10.5)
fig.savefig(root/'ratios.png', dpi=160, facecolor='white')
fig.savefig(root/'ratios.svg', facecolor='white')
plt.close(fig)
print(json.dumps({'benchmarks':len(rows),'data_sha256':hashlib.sha256((root/'measurements.json').read_bytes()).hexdigest(),
                  'png_sha256':hashlib.sha256((root/'ratios.png').read_bytes()).hexdigest()},indent=2))
