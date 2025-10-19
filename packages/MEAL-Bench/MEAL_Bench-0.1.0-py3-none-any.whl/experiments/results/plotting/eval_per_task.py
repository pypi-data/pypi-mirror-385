#!/usr/bin/env python3
"""
One subplot per CL method, one coloured line per environment/task.

* Directory layout, --metric switch, baseline normalisation and every other
  CLI flag are identical to plot_avg.py.
* Colours are auto-generated; the first task is blue, the next green … (husl).

Additional features:
1. X-axis ticks plotted on every subplot.
2. Vertical dividing lines between tasks.
3. Top x-axis labels reading "Task 1", "Task 2", …, colored to match lines for each method.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from experiments.results.plotting.utils import (
    collect_env_curves, smooth_and_ci, add_task_boundaries,
    save_plot, create_eval_parser
)


def parse_args():
    """Parse command line arguments for the per-task evaluation plot script."""
    p = create_eval_parser(
        description="Plot per-task evaluation metrics for MARL continual-learning benchmark",
        metric_choices=['reward', 'soup']
    )
    # Set default metric to 'soup' (overriding the default from create_eval_parser)
    p.set_defaults(metric='soup')
    return p.parse_args()


def plot():
    """
    Main plotting function for per-task evaluation metrics.

    Creates one subplot per method, with one colored line per environment/task.
    Adds task boundaries and colored task labels.
    """
    args = parse_args()
    data_root = Path(__file__).resolve().parent.parent / args.data_root

    # Calculate total steps and set up boundaries
    total_steps = args.seq_len * args.steps_per_task
    task_colors = sns.color_palette("hls", args.seq_len)
    boundaries = [i * args.steps_per_task for i in range(args.seq_len + 1)]
    mids = [(boundaries[i] + boundaries[i + 1]) / 2 for i in range(args.seq_len)]

    # Set up figure with one subplot per method
    methods = args.methods
    fig_height = 2.5 * len(methods) if len(methods) > 1 else 2.8
    fig, axes = plt.subplots(len(methods), 1, sharex=False, sharey=True, figsize=(12, fig_height))
    if len(methods) == 1:
        axes = [axes]

    # Create one subplot per method
    for m_idx, method in enumerate(methods):
        ax = axes[m_idx]

        # Collect data for this method
        envs, curves = collect_env_curves(
            data_root, args.algo, method, args.strategy,
            args.seq_len, args.seeds, args.metric, args.level
        )

        # Add task boundaries
        add_task_boundaries(ax, boundaries, color='gray', linewidth=0.5)

        # Set up x-axis ticks
        ax.set_xticks(boundaries)
        ax.ticklabel_format(style='scientific', axis='x', scilimits=(0, 0))

        # Plot one curve per environment/task
        for i, curve in enumerate(curves):
            mean, ci = smooth_and_ci(curve, args.sigma, args.confidence)
            x = np.linspace(0, total_steps, len(mean))
            ax.plot(x, mean, color=task_colors[i])
            ax.fill_between(x, mean - ci, mean + ci, alpha=0.2, color=task_colors[i])

        # Set axis limits and labels
        ax.set_xlim(0, total_steps)
        ax.set_ylim(0, 1)
        ax.set_ylabel(f"Normalized Score")
        # Only set title if there are multiple methods
        if len(methods) > 1:
            ax.set_title(method, fontsize=11)

        # Set up secondary x-axis with task labels
        twin = ax.twiny()
        twin.set_xlim(ax.get_xlim())
        twin.set_xticks(mids)
        labels = [f"Task {i + 1}" for i in range(args.seq_len)]
        twin.set_xticklabels(labels, fontsize=10)
        twin.tick_params(axis='x', length=0)

        # Color task labels to match task curves
        for idx, label in enumerate(twin.get_xticklabels()):
            label.set_color(task_colors[idx])

    # Set x-axis label on the bottom subplot
    axes[-1].set_xlabel('Environment Steps')

    # Finalize and save the plot
    plt.tight_layout()
    out_dir = Path(__file__).resolve().parent.parent / 'plots'
    name = args.plot_name or f"per_task_norm_score"
    # Add method name to filename if only a single method is given
    if len(methods) == 1:
        name += f"_{methods[0]}"
    name += f"_seq_{args.seq_len}"
    # Add level suffix if not already present
    if "_level" not in name:
        name += f"_level_{args.level}"
    save_plot(fig, out_dir, name)

    # Display the plot
    plt.show()


if __name__ == '__main__':
    plot()
