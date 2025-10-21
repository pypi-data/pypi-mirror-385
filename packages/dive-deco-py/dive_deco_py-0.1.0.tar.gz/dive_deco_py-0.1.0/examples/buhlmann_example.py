from dive_deco_py import BuhlmannModel, Gas

model = BuhlmannModel()

air = Gas(0.21, 0.)
ean50 = Gas(0.50, 0.)

model.record(40, 15, air)

deco = model.deco([air, ean50])
ceiling = model.ceiling()
supersaturation = model.supersaturation()

print("tts:", deco.tts)
print("tts @+5:", deco.tts_at_5)
print("tts Δ+5", deco.tts_delta_at_5)
print("ceiling:", ceiling)
print("gf99:", supersaturation.gf_99)
print("surfGf:", supersaturation.gf_surf)
