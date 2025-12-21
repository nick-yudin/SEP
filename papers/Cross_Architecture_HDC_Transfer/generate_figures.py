#!/usr/bin/env python3
"""
Generate publication-quality figures for Paper 1.
Run this script after copying result JSON files to results/ folder.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # For headless environments

# Style settings
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'legend.fontsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
})

# Colors
COLORS = {
    'blue': '#2980b9',
    'orange': '#e67e22',
    'green': '#27ae60',
    'red': '#c0392b',
    'purple': '#8e44ad',
    'gray': '#7f8c8d',
}


def load_results():
    """Load experiment results from JSON files."""
    with open('results/experiment1_complete.json', 'r') as f:
        exp1 = json.load(f)
    
    # Experiment 2 data (from logs since JSON didn't save)
    exp2 = {
        'teachers': ['DistilBERT', 'GPT-2', 'Llama 8B', 'Qwen 14B'],
        'sizes': [66, 124, 8000, 14000],  # in millions
        'accuracy': [0.789, 0.743, 0.777, 0.756],
        'efficiency': [0.988, 0.939, 0.983, 0.960],
        'std': [0.013, 0.012, 0.010, 0.007],
    }
    
    return exp1, exp2


def figure1_hdc_dimension(exp1):
    """Stage 1: HDC dimension effect."""
    fig, ax = plt.subplots(figsize=(6, 4))
    
    dims = [1024, 2048, 4096, 8192]
    
    for model, color in [('distilbert', COLORS['blue']), ('gpt2', COLORS['orange'])]:
        accs = [exp1['stage1'][model]['hdc_results'][str(d)] for d in dims]
        ax.plot(dims, accs, 'o-', color=color, label=model.upper(), markersize=8, linewidth=2)
    
    # Ceiling lines
    ax.axhline(exp1['stage0']['distilbert'], color=COLORS['blue'], linestyle='--', alpha=0.5, label='DistilBERT ceiling')
    ax.axhline(exp1['stage0']['gpt2'], color=COLORS['orange'], linestyle='--', alpha=0.5, label='GPT-2 ceiling')
    
    ax.set_xlabel('HDC Dimension')
    ax.set_ylabel('Accuracy')
    ax.set_title('Effect of HDC Dimension on Classification Accuracy')
    ax.legend(loc='lower right')
    ax.set_ylim(0.70, 0.92)
    
    plt.savefig('figures/stage1_hdc_dimension.png')
    plt.savefig('figures/stage1_hdc_dimension.pdf')
    plt.close()
    print('✓ Figure 1: HDC dimension')


def figure2_alignment_methods(exp1):
    """Stage 2: Alignment methods comparison."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    methods = ['none', 'procrustes', 'cca', 'contrastive']
    method_labels = ['None', 'Procrustes', 'CCA', 'Contrastive']
    anchor_sizes = [100, 500, 1000]
    colors = [COLORS['gray'], COLORS['orange'], COLORS['green'], COLORS['red']]
    
    for method, label, color in zip(methods, method_labels, colors):
        means = []
        stds = []
        for size in anchor_sizes:
            accs = [e['accuracy'] for e in exp1['stage2']['experiments'] 
                   if e['method'] == method and e['anchor_size'] == size]
            means.append(np.mean(accs))
            stds.append(np.std(accs))
        
        ax.errorbar(anchor_sizes, means, yerr=stds, marker='o', label=label, 
                   color=color, capsize=4, markersize=7, linewidth=2)
    
    ax.axhline(exp1['stage2']['student_ceiling'], color=COLORS['green'], 
               linestyle='--', alpha=0.7, label='Student ceiling')
    ax.axhline(0.5, color=COLORS['gray'], linestyle=':', alpha=0.5, label='Random')
    
    ax.set_xlabel('Number of Anchor Samples')
    ax.set_ylabel('Accuracy')
    ax.set_title('Alignment Method Comparison')
    ax.legend(loc='center right')
    ax.set_ylim(0.4, 0.85)
    
    plt.savefig('figures/stage2_alignment_methods.png')
    plt.savefig('figures/stage2_alignment_methods.pdf')
    plt.close()
    print('✓ Figure 2: Alignment methods')


def figure3_model_pairs(exp1):
    """Stage 3: Model pairs comparison."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    pairs = exp1['stage3']['pairs']
    labels = [f"{p['teacher']}→{p['student']}" for p in pairs]
    ceilings = [p['student_ceiling'] for p in pairs]
    transfers = [p['mean_accuracy'] for p in pairs]
    
    x = np.arange(len(pairs))
    width = 0.35
    
    ax.bar(x - width/2, ceilings, width, label='Student ceiling', color=COLORS['blue'], alpha=0.7)
    ax.bar(x + width/2, transfers, width, label='Transfer accuracy', color=COLORS['orange'], alpha=0.7)
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha='right')
    ax.set_ylabel('Accuracy')
    ax.set_title('Bidirectional Transfer Across Model Pairs')
    ax.legend()
    ax.set_ylim(0, 1.0)
    
    # Add efficiency annotations
    for i, (ceil, trans) in enumerate(zip(ceilings, transfers)):
        eff = trans / ceil * 100
        ax.annotate(f'{eff:.0f}%', xy=(i + width/2, trans + 0.02), ha='center', fontsize=9)
    
    plt.savefig('figures/stage3_model_pairs.png')
    plt.savefig('figures/stage3_model_pairs.pdf')
    plt.close()
    print('✓ Figure 3: Model pairs')


def figure4_datasets(exp1):
    """Stage 4: Dataset comparison."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    datasets = ['sst2', 'ag_news', 'mnli']
    dataset_labels = ['SST-2', 'AG News', 'MNLI']
    
    pair1_accs = []
    pair2_accs = []
    
    for ds in datasets:
        ds_data = exp1['stage4']['datasets'][ds]
        pair1_accs.append(ds_data['pairs'][0]['mean_accuracy'])
        pair2_accs.append(ds_data['pairs'][1]['mean_accuracy'])
    
    x = np.arange(len(datasets))
    width = 0.35
    
    ax.bar(x - width/2, pair1_accs, width, label='DistilBERT→GPT-2', color=COLORS['blue'], alpha=0.7)
    ax.bar(x + width/2, pair2_accs, width, label='GPT-2→DistilBERT', color=COLORS['orange'], alpha=0.7)
    
    ax.set_xticks(x)
    ax.set_xticklabels(dataset_labels)
    ax.set_ylabel('Accuracy')
    ax.set_title('Transfer Performance Across Datasets')
    ax.legend()
    ax.set_ylim(0, 1.0)
    
    plt.savefig('figures/stage4_datasets.png')
    plt.savefig('figures/stage4_datasets.pdf')
    plt.close()
    print('✓ Figure 4: Datasets')


def figure5_strong_teacher(exp2):
    """Strong teacher hypothesis: size vs accuracy."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    sizes = exp2['sizes']
    accs = exp2['accuracy']
    stds = exp2['std']
    labels = exp2['teachers']
    
    ax.errorbar(sizes, accs, yerr=stds, marker='o', markersize=10, 
               capsize=5, linewidth=2, color=COLORS['blue'])
    
    # Annotate points
    for s, a, l in zip(sizes, accs, labels):
        offset = (10, 10) if l != 'DistilBERT' else (10, -15)
        ax.annotate(l, (s, a), textcoords='offset points', xytext=offset, fontsize=10)
    
    # Highlight best
    best_idx = np.argmax(accs)
    ax.scatter([sizes[best_idx]], [accs[best_idx]], s=200, facecolors='none', 
              edgecolors=COLORS['green'], linewidths=2, zorder=5)
    
    ax.set_xscale('log')
    ax.set_xlabel('Teacher Model Size (M parameters)')
    ax.set_ylabel('Transfer Accuracy')
    ax.set_title('Strong Teacher Hypothesis: Size vs Transfer Quality')
    ax.set_ylim(0.70, 0.82)
    
    # Add text annotation
    ax.text(0.95, 0.05, 'Smallest model\nachieves best transfer', 
           transform=ax.transAxes, ha='right', va='bottom',
           fontsize=10, color=COLORS['green'], style='italic')
    
    plt.savefig('figures/strong_teacher_size_vs_accuracy.png')
    plt.savefig('figures/strong_teacher_size_vs_accuracy.pdf')
    plt.close()
    print('✓ Figure 5: Strong teacher')


def figure6_architecture_diagram():
    """System architecture diagram."""
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis('off')
    
    # Boxes
    boxes = [
        (0.5, 1, 1.5, 1, 'Text\nInput'),
        (2.5, 1, 1.5, 1, 'Encoder\n(768d)'),
        (4.5, 1, 1.5, 1, 'Random\nProjection'),
        (6.5, 1, 1.5, 1, 'Ternary\n(4096d)'),
        (8.5, 1, 1.2, 1, 'Classifier'),
    ]
    
    for x, y, w, h, label in boxes:
        rect = plt.Rectangle((x, y), w, h, fill=True, facecolor=COLORS['blue'], 
                            edgecolor='black', alpha=0.3, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Arrows
    arrow_style = dict(arrowstyle='->', color='black', lw=2)
    for x1, x2 in [(2, 2.5), (4, 4.5), (6, 6.5), (8, 8.5)]:
        ax.annotate('', xy=(x2, 1.5), xytext=(x1, 1.5), arrowprops=arrow_style)
    
    # Alignment annotation
    ax.annotate('', xy=(6.5, 0.8), xytext=(6.5, 0.3), 
               arrowprops=dict(arrowstyle='<->', color=COLORS['red'], lw=2))
    ax.text(6.5, 0.1, 'Contrastive\nAlignment', ha='center', va='top', 
           fontsize=9, color=COLORS['red'])
    
    ax.set_title('HDC Transfer Pipeline', fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig('figures/architecture_diagram.png')
    plt.savefig('figures/architecture_diagram.pdf')
    plt.close()
    print('✓ Figure 6: Architecture diagram')


def main():
    print('Generating Paper 1 figures...\n')
    
    try:
        exp1, exp2 = load_results()
    except FileNotFoundError as e:
        print(f'Error: {e}')
        print('Please copy result JSON files to results/ folder first.')
        return
    
    figure1_hdc_dimension(exp1)
    figure2_alignment_methods(exp1)
    figure3_model_pairs(exp1)
    figure4_datasets(exp1)
    figure5_strong_teacher(exp2)
    figure6_architecture_diagram()
    
    print('\n✅ All figures generated in figures/ folder')


if __name__ == '__main__':
    main()
