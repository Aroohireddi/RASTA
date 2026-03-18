import sys
sys.path.insert(0, "services/tts-server/src")
from model import synthesize

print("Test 1: Pure Telugu")
wav, rtf, sr = synthesize("నమస్కారం")
with open("test_telugu.wav", "wb") as f:
    f.write(wav)
print(f"Success. RTF={rtf}, Size={len(wav)} bytes")

print("Test 2: Mixed")
wav2, rtf2, sr2 = synthesize("ఇస్రో లాంచ్ చేసింది")
with open("test_mixed.wav", "wb") as f:
    f.write(wav2)
print(f"Success. RTF={rtf2}, Size={len(wav2)} bytes")
