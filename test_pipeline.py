import requests

payload = {
    "title": "ఐఎస్ఆర్వో చంద్రయాన్ విజయం",
    "summary": "ఐఎస్ఆర్వో శ్రీహరికోట నుండి చంద్రయాన్ మిషన్‌ను విజయవంతంగా ప్రారంభించింది. అంతరిక్ష నౌక చంద్రుడి చుట్టూ తిరుగుతూ డేటా సేకరిస్తుంది. Bangalore లోని scientists ఈ విజయాన్ని జరుపుకున్నారు.",
    "source": "test"
}

print("Step 1: NLP pipeline...")
r = requests.post("http://localhost:8002/process/article", json=payload)
nlp_result = r.json()
print(f"Sentences: {nlp_result['sentence_count']}")
print(f"Language ratio: {nlp_result['language_ratio']}")
for i, s in enumerate(nlp_result['sentences']):
    print(f"\nSentence {i+1} original: {s['original'][:80]}")
    print(f"Sentence {i+1} final:    {s['final'][:80]}")
    print(f"OOV tokens: {s['oov_tokens']}")

print("\nStep 2: Full pipeline audio...")
r2 = requests.post("http://localhost:8000/process/article/audio", json=payload)
if r2.status_code == 200:
    with open("final_telugu.wav", "wb") as f:
        f.write(r2.content)
    print(f"Audio saved. Size: {len(r2.content)} bytes")
    print(f"RTF: {r2.headers.get('X-RTF')}")
    print(f"Sentence: {r2.headers.get('X-Sentence')}")
    print(f"OOV count: {r2.headers.get('X-OOV-Count')}")
else:
    print(f"Error {r2.status_code}: {r2.text}")