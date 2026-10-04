"""
Trực quan hóa kết quả bài toán CVRP.
"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from typing import List, Dict, Optional
from vrp_parser import VRPInstance

def plot_instance(instance: VRPInstance, figsize=(10, 8)):
    coords = instance.coords
    fig, ax = plt.subplots(figsize=figsize)
    customers = instance.customer_indices()
    sizes = instance.demands[customers] * 5 + 20
    ax.scatter(coords[customers, 0], coords[customers, 1],
               s=sizes, c='steelblue', alpha=0.7, edgecolors='navy', label='Khách hàng')
    for c in customers:
        ax.annotate(str(c), (coords[c, 0], coords[c, 1]),
                    textcoords="offset points", xytext=(4, 4), fontsize=7, color='gray')
    depot = instance.depot
    ax.plot(coords[depot, 0], coords[depot, 1],
            'r*', markersize=20, zorder=5, label='Depot')
    ax.set_title(f'{instance.name} — {len(customers)} khách hàng, Capacity={instance.capacity}', fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_routes(instance: VRPInstance, routes: List[List[int]], title: str = "CVRP Solution", figsize=(12, 9)):
    coords = instance.coords
    colors = cm.tab10(np.linspace(0, 1, max(len(routes), 1)))
    fig, ax = plt.subplots(figsize=figsize)
    for idx, route in enumerate(routes):
        route_coords = coords[route]
        load = sum(instance.demands[c] for c in route if c != instance.depot)
        ax.plot(route_coords[:, 0], route_coords[:, 1],
                '-o', color=colors[idx % 10], linewidth=1.8, markersize=6,
                label=f'Xe {idx+1} (tải={load}/{instance.capacity})', zorder=3)
    depot = instance.depot
    ax.plot(coords[depot, 0], coords[depot, 1],
            'r*', markersize=22, zorder=5, label='Depot', markeredgecolor='darkred')
    for i in range(instance.dimension):
        if i != depot:
            ax.annotate(str(i), (coords[i, 0], coords[i, 1]),
                        textcoords="offset points", xytext=(5, 5), fontsize=7, color='dimgray')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_convergence(convergence: List[float], optimal: Optional[float] = None, title: str = "Đường cong hội tụ"):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(convergence, 'b-', linewidth=1.5, label='Chi phí tốt nhất')
    if optimal:
        ax.axhline(y=optimal, color='red', linestyle='--', linewidth=1.2, label=f'BKS = {optimal}')
        final_cost = convergence[-1]
        gap = (final_cost / optimal - 1) * 100
        ax.annotate(f'Gap: {gap:.2f}%', xy=(len(convergence) - 1, final_cost),
                    xytext=(-80, 30), textcoords='offset points', fontsize=10, color='blue',
                    arrowprops=dict(arrowstyle='->', color='blue', lw=1.2))
    ax.set_title(title, fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_comparison(results: Dict[str, dict], optimal: Optional[float] = None, title: str = "So sánh"):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    method_colors = ['steelblue', 'coral', 'seagreen', 'orchid']
    ax1 = axes[0]
    for i, (label, data) in enumerate(results.items()):
        ax1.plot(data['convergence'], label=label, linewidth=1.5, color=method_colors[i % len(method_colors)])
    if optimal:
        ax1.axhline(y=optimal, color='red', linestyle='--', linewidth=1, label=f'BKS = {optimal}')
    ax1.set_title('Đường cong hội tụ')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    labels = list(results.keys())
    costs = [results[l]['cost'] for l in labels]
    bars = ax2.bar(labels, costs, color=method_colors[:len(labels)], edgecolor='gray')
    if optimal:
        ax2.axhline(y=optimal, color='red', linestyle='--', linewidth=1.2, label=f'BKS = {optimal}')
    for bar, cost in zip(bars, costs):
        gap_text = f"\n({(cost / optimal - 1) * 100:+.1f}%)" if optimal else ""
        ax2.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 2,
                 f'{cost:.0f}{gap_text}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax2.set_title('Chi phí cuối cùng')
    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()

def print_solution_summary(instance, routes, cost, stats=None, method_name="ACO"):
    print(f"\n{'═' * 60}\n  KẾT QUẢ: {method_name} — {instance.name}\n{'═' * 60}")
    print(f"  Tổng khoảng cách:  {cost:.2f}\n  Số tuyến (xe):     {len(routes)}")
    if instance.optimal_value:
        print(f"  Best Known (BKS):  {instance.optimal_value}")
        print(f"  Gap so với BKS:    {(cost / instance.optimal_value - 1) * 100:+.2f}%")
    if stats and 'runtime' in stats:
        print(f"  Thời gian:         {stats['runtime']:.2f}s")
    print(f"\n  Chi tiết từng tuyến:")
    for i, route in enumerate(routes):
        load = sum(instance.demands[c] for c in route if c != instance.depot)
        dist = sum(np.sqrt((instance.coords[route[j]] - instance.coords[route[j + 1]]) ** 2).sum() for j in range(len(route) - 1))
        print(f"    Xe {i+1:2d}: {' → '.join(map(str, route))}  │ tải={load}/{instance.capacity} │ dist={dist:.1f}")
    print(f"{'═' * 60}\n")
