from dive_deco_py import BuhlmannModel, Gas
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Create output directory if it doesn't exist
output_dir = Path(__file__).parent / "out"
output_dir.mkdir(exist_ok=True)

model = BuhlmannModel()
air = Gas(0.21, 0)

model.record(40, 30, air)
ceiling = model.ceiling()

# Get tissue compartments after bottom time
tissues_bottom = model.tissues()

# Extract data from tissues after bottom time
compartment_numbers = [t.no for t in tissues_bottom]
n2_pressures_bottom = [t.n2_ip for t in tissues_bottom]
he_pressures_bottom = [t.he_ip for t in tissues_bottom]
total_pressures_bottom = [t.total_ip for t in tissues_bottom]
m_values_calc_bottom = [t.m_value_calc for t in tissues_bottom]

# Calculate saturation ratios after bottom time
saturation_ratios_bottom = [total_pressures_bottom[i] / m_values_calc_bottom[i] * 100 for i in range(len(tissues_bottom))]

# Create a second model to simulate instant ascent to ceiling
model_ceiling = BuhlmannModel()
model_ceiling.record(40, 30, air)
# Instantly ascend to ceiling depth (simulated as very short time)
if ceiling > 0:
    model_ceiling.record(ceiling, 0.01, air)
tissues_ceiling = model_ceiling.tissues()

# Extract data from tissues at ceiling
total_pressures_ceiling = [t.total_ip for t in tissues_ceiling]
m_values_calc_ceiling = [t.m_value_calc for t in tissues_ceiling]

# Calculate saturation ratios at ceiling
saturation_ratios_ceiling = [total_pressures_ceiling[i] / m_values_calc_ceiling[i] * 100 for i in range(len(tissues_ceiling))]

# Create the plot with 3 subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 14))

x = np.arange(len(compartment_numbers))
width = 0.35

# Plot 1: Inert gas pressures after bottom time
bars1 = ax1.bar(x - width/2, n2_pressures_bottom, width, label='N2 Pressure', alpha=0.8, color='skyblue')
bars2 = ax1.bar(x + width/2, he_pressures_bottom, width, label='He Pressure', alpha=0.8, color='lightcoral')
ax1.plot(x, total_pressures_bottom, 'ro-', label='Total Inert Pressure', linewidth=2, markersize=6)
ax1.plot(x, m_values_calc_bottom, 'g^--', label='M-Value (with GF)', linewidth=2, markersize=6)

ax1.set_xlabel('Tissue Compartment', fontsize=12)
ax1.set_ylabel('Pressure (bar)', fontsize=12)
ax1.set_title('Tissue Saturation After Bottom Time (40m for 30min)', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(compartment_numbers)
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Saturation percentage after bottom time
bars3 = ax2.bar(x, saturation_ratios_bottom, color='steelblue', alpha=0.8)
ax2.axhline(y=100, color='r', linestyle='--', linewidth=2, label='100% Saturation (M-Value)')
ax2.set_xlabel('Tissue Compartment', fontsize=12)
ax2.set_ylabel('Saturation (%)', fontsize=12)
ax2.set_title(f'Saturation After Bottom Time (Ceiling: {ceiling}m, GF99: {model.supersaturation().gf_99:.1f}%)', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(compartment_numbers)
ax2.legend()
ax2.grid(True, alpha=0.3)

# Color bars based on saturation level
for i, bar in enumerate(bars3):
    if saturation_ratios_bottom[i] >= 100:
        bar.set_color('red')
    elif saturation_ratios_bottom[i] >= 80:
        bar.set_color('orange')
    else:
        bar.set_color('steelblue')

# Plot 3: Saturation percentage if instantly at ceiling
bars4 = ax3.bar(x, saturation_ratios_ceiling, color='steelblue', alpha=0.8)
ax3.axhline(y=100, color='r', linestyle='--', linewidth=2, label='100% Saturation (M-Value)')
ax3.set_xlabel('Tissue Compartment', fontsize=12)
ax3.set_ylabel('Saturation (%)', fontsize=12)
title_text = f'Saturation If Instantly at Ceiling ({ceiling}m)' if ceiling > 0 else 'Saturation If Instantly at Surface (No Ceiling)'
ax3.set_title(title_text, fontsize=14, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(compartment_numbers)
ax3.legend()
ax3.grid(True, alpha=0.3)

# Color bars based on saturation level
for i, bar in enumerate(bars4):
    if saturation_ratios_ceiling[i] >= 100:
        bar.set_color('red')
    elif saturation_ratios_ceiling[i] >= 80:
        bar.set_color('orange')
    else:
        bar.set_color('steelblue')

plt.tight_layout()
output_path = output_dir / 'tissue_saturation.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Plot saved as '{output_path}'")
print(f"\nAfter bottom time:")
print(f"  Ceiling: {ceiling}m")
print(f"  GF99: {model.supersaturation().gf_99:.1f}%")
print(f"  Max saturation: {max(saturation_ratios_bottom):.1f}%")
print(f"\nAt ceiling depth ({ceiling}m):")
print(f"  Max saturation: {max(saturation_ratios_ceiling):.1f}%")
plt.show()
