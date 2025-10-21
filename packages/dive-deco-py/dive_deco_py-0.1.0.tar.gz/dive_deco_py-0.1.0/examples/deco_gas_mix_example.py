import matplotlib.pyplot as plt
import numpy as np
from dive_deco_py import BuhlmannModel, Gas
from pathlib import Path

# Create output directory if it doesn't exist
output_dir = Path(__file__).parent / "out"
output_dir.mkdir(exist_ok=True)

# Define gas mixtures
air = Gas(0.21, 0.)
ean50 = Gas(0.50, 0.)
oxygen = Gas(1.0, 0.)

model = BuhlmannModel()
model.record(40, 30, air)
print(model.supersaturation().gf_surf)

# Scenario 1: Deco on air only
deco1 = model.deco([air])

tts1 = deco1.tts
tts1_plus5 = deco1.tts_at_5
delta1 = deco1.tts_delta_at_5

# Scenario 2: Deco on air + EAN50
deco2 = model.deco([air, ean50])
tts2 = deco2.tts
print(tts2)
tts2_plus5 = deco2.tts_at_5
delta2 = deco2.tts_delta_at_5

# Scenario 3: Deco on air + EAN50 + oxygen
deco3 = model.deco([air, ean50, oxygen])
tts3 = deco3.tts
tts3_plus5 = deco3.tts_at_5
delta3 = deco3.tts_delta_at_5

# Print results
print("=" * 70)
print("DECOMPRESSION COMPARISON: 30 min at 40m on Air")
print("=" * 70)
print(f"\nScenario 1: Air only")
print(f"  TTS:              {tts1:.2f} minutes")
print(f"  TTS+5:            {tts1_plus5:.2f} minutes")
print(f"  Delta (TTS+5):    {delta1:.2f} minutes")

print(f"\nScenario 2: Air + EAN50")
print(f"  TTS:              {tts2:.2f} minutes")
print(f"  TTS+5:            {tts2_plus5:.2f} minutes")
print(f"  Delta (TTS+5):    {delta2:.2f} minutes")

print(f"\nScenario 3: Air + EAN50 + O2")
print(f"  TTS:              {tts3:.2f} minutes")
print(f"  TTS+5:            {tts3_plus5:.2f} minutes")
print(f"  Delta (TTS+5):    {delta3:.2f} minutes")
print("=" * 70)

# Create grouped bar plot
scenarios = ['Air only', 'Air + EAN50', 'Air + EAN50 + O2']
tts_times = [tts1, tts2, tts3]
tts_plus5_times = [tts1_plus5, tts2_plus5, tts3_plus5]
delta_times = [delta1, delta2, delta3]

x = np.arange(len(scenarios))
width = 0.25

fig, ax = plt.subplots(figsize=(14, 8))

bars1 = ax.bar(x - width, tts_times, width, label='TTS',
               color='#FF6B6B', edgecolor='black', linewidth=1.5)
bars2 = ax.bar(x, tts_plus5_times, width, label='TTS+5',
               color='#4ECDC4', edgecolor='black', linewidth=1.5)
bars3 = ax.bar(x + width, delta_times, width, label='Delta (TTS+5 - TTS)',
               color='#45B7D1', edgecolor='black', linewidth=1.5)

# Add value labels on bars
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.set_ylabel('Time (minutes)', fontsize=12, fontweight='bold')
ax.set_xlabel('Decompression Gas Mix Configuration', fontsize=12, fontweight='bold')
ax.set_title('Decompression Time Comparison\n30 min dive at 40m on Air (GF 30/70)',
             fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios)
ax.legend(fontsize=11, loc='upper right')
ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()

# Save the plot
output_path = output_dir / 'deco_comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nPlot saved as '{output_path}'")

# Show the plot
plt.show()
