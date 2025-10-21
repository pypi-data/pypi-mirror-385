from dive_deco_py import BuhlmannModel, Gas
import time

model = BuhlmannModel()
air = Gas(0.21, 0.)
ean50 = Gas(0.50, 0.)
depth = 40
bottom_time = 10000.

# start
start_time = time.perf_counter()
model.record(depth, bottom_time, air)
deco = model.deco([air, ean50])
end_time = time.perf_counter()
# stop

print("tts:", deco.tts)
elapsed_ms = (end_time - start_time) * 1000
print(f"Execution time: {elapsed_ms:.3f} ms")
