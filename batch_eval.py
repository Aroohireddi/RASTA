import requests
import json
import time

# 30 Telugu-English code-mixed test sentences
# Covering: news, politics, technology, sports, finance domains
TEST_SENTENCES = [
    {
        "text": "ఐఎస్ఆర్వో శ్రీహరికోట నుండి Chandrayaan మిషన్‌ను విజయవంతంగా ప్రారంభించింది.",
        "domain": "space", "has_oov": True
    },
    {
        "text": "Telangana ముఖ్యమంత్రి హైదరాబాద్‌లో నూతన IT పార్క్ ప్రారంభించారు.",
        "domain": "politics", "has_oov": True
    },
    {
        "text": "భారత Cricket జట్టు World Cup టోర్నమెంట్‌లో విజయం సాధించింది.",
        "domain": "sports", "has_oov": True
    },
    {
        "text": "Reserve Bank of India వడ్డీ రేట్లను యథాతథంగా కొనసాగిస్తుందని ప్రకటించింది.",
        "domain": "finance", "has_oov": True
    },
    {
        "text": "Hyderabad లోని Software కంపెనీలు AI ఆధారిత products అభివృద్ధి చేస్తున్నాయి.",
        "domain": "technology", "has_oov": True
    },
    {
        "text": "Andhra Pradesh ప్రభుత్వం రైతులకు నూతన scheme ప్రకటించింది.",
        "domain": "agriculture", "has_oov": True
    },
    {
        "text": "Supreme Court న్యాయమూర్తులు రాజ్యాంగ సవరణపై తీర్పు వెలువరించారు.",
        "domain": "law", "has_oov": True
    },
    {
        "text": "Visakhapatnam పోర్టులో నూతన container terminal నిర్మాణం ప్రారంభమైంది.",
        "domain": "infrastructure", "has_oov": True
    },
    {
        "text": "తెలుగు విశ్వవిద్యాలయంలో Online courses ప్రారంభించారు.",
        "domain": "education", "has_oov": True
    },
    {
        "text": "Amaravati రాజధాని నిర్మాణ పనులు పూర్తి వేగంతో జరుగుతున్నాయి.",
        "domain": "infrastructure", "has_oov": True
    },
    {
        "text": "భారత ఆర్థిక వ్యవస్థ GDP వృద్ధి రేటు అంతర్జాతీయ అంచనాలను మించింది.",
        "domain": "finance", "has_oov": True
    },
    {
        "text": "Bangalore లోని startup కంపెనీలు global investors దృష్టిని ఆకర్షిస్తున్నాయి.",
        "domain": "technology", "has_oov": True
    },
    {
        "text": "తెలంగాణ రాష్ట్రంలో Solar energy ప్రాజెక్టులు అభివృద్ధి చెందుతున్నాయి.",
        "domain": "energy", "has_oov": True
    },
    {
        "text": "IPL సీజన్‌లో SRH జట్టు అద్భుతమైన ప్రదర్శన కనబరిచింది.",
        "domain": "sports", "has_oov": True
    },
    {
        "text": "WhatsApp ద్వారా డిజిటల్ చెల్లింపులు చేయడం సులభతరం అయింది.",
        "domain": "technology", "has_oov": True
    },
    {
        "text": "Modi ప్రభుత్వం Digital India కార్యక్రమాన్ని మరింత విస్తరించింది.",
        "domain": "politics", "has_oov": True
    },
    {
        "text": "YouTube channels ద్వారా తెలుగు కళాకారులు ప్రపంచవ్యాప్త గుర్తింపు పొందుతున్నారు.",
        "domain": "entertainment", "has_oov": True
    },
    {
        "text": "UPI payments వ్యవస్థ భారతదేశంలో విప్లవాత్మక మార్పులు తెచ్చింది.",
        "domain": "finance", "has_oov": True
    },
    {
        "text": "Vijayawada లో metro rail project కు కేంద్ర ప్రభుత్వం ఆమోదం తెలిపింది.",
        "domain": "infrastructure", "has_oov": True
    },
    {
        "text": "తెలుగు సినిమా industry లో OTT platforms ప్రాముఖ్యత పెరుగుతోంది.",
        "domain": "entertainment", "has_oov": True
    },
    {
        "text": "అంతరిక్ష పరిశోధనలో భారత్ అగ్ర దేశాలతో సమానంగా నిలబడుతోంది.",
        "domain": "space", "has_oov": False
    },
    {
        "text": "రైతులకు సకాలంలో పంట రుణాలు అందించాలని ప్రభుత్వం ఆదేశించింది.",
        "domain": "agriculture", "has_oov": False
    },
    {
        "text": "విద్యార్థులకు ఉపకార వేతనాలు పెంచాలని విద్యా శాఖ నిర్ణయించింది.",
        "domain": "education", "has_oov": False
    },
    {
        "text": "నదీ జలాల పంపకంలో రెండు రాష్ట్రాల మధ్య ఒప్పందం కుదిరింది.",
        "domain": "politics", "has_oov": False
    },
    {
        "text": "గ్రామీణ ప్రాంతాలలో విద్యుత్ సరఫరా మెరుగుపరచాలని ప్రభుత్వం నిర్ణయించింది.",
        "domain": "infrastructure", "has_oov": False
    },
    {
        "text": "COVID తర్వాత ఆర్థిక వ్యవస్థ పుంజుకుంటోందని నిపుణులు అభిప్రాయపడుతున్నారు.",
        "domain": "health", "has_oov": True
    },
    {
        "text": "Google India కార్యాలయంలో తెలుగు language support మెరుగుపరిచారు.",
        "domain": "technology", "has_oov": True
    },
    {
        "text": "BJP Congress మధ్య రాజకీయ పోటీ ముమ్మరంగా సాగుతోంది.",
        "domain": "politics", "has_oov": True
    },
    {
        "text": "Amazon Flipkart వంటి e-commerce platforms తెలుగు వినియోగదారులను ఆకర్షిస్తున్నాయి.",
        "domain": "technology", "has_oov": True
    },
    {
        "text": "CBI దర్యాప్తు తర్వాత అధికారులపై FIR నమోదు చేశారు.",
        "domain": "law", "has_oov": True
    },
]

results = []
print("=" * 60)
print("RASTA Batch Evaluation — 30 Sentences")
print("=" * 60)

for i, item in enumerate(TEST_SENTENCES):
    text = item["text"]
    domain = item["domain"]

    try:
        # Step 1: NLP process
        r_nlp = requests.post(
            "http://localhost:8002/process/sentence",
            json={"text": text, "source": domain},
            timeout=30
        )
        if r_nlp.status_code != 200:
            print(f"[{i+1:02d}] NLP failed: {text[:40]}")
            continue

        nlp_result = r_nlp.json()
        final_text = nlp_result.get("final_sentence", text)
        oov_tokens = nlp_result.get("oov_tokens", [])

        # Step 2: TTS synthesis
        r_tts = requests.post(
            "http://localhost:8004/synthesize",
            json={"text": final_text, "return_metadata": True},
            timeout=60
        )
        if r_tts.status_code != 200:
            print(f"[{i+1:02d}] TTS failed: {text[:40]}")
            continue

        rtf = float(r_tts.headers.get("X-RTF", 0))
        audio_size = len(r_tts.content)

        # Step 3: Evaluate
        r_eval = requests.post(
            "http://localhost:8005/evaluate/quick",
            json={
                "original_text": text,
                "transcription": final_text,
                "rtf": rtf,
                "oov_tokens": oov_tokens,
                "switch_count": len(oov_tokens),
                "source": domain
            },
            timeout=30
        )

        if r_eval.status_code == 200:
            eval_result = r_eval.json()
            results.append({
                "id": i + 1,
                "domain": domain,
                "has_oov": item["has_oov"],
                "oov_count": len(oov_tokens),
                "cer": eval_result["cer"],
                "rtf": rtf,
                "audio_size": audio_size
            })
            print(f"[{i+1:02d}] {domain:15s} | OOV:{len(oov_tokens)} | CER:{eval_result['cer']:.4f} | RTF:{rtf:.4f} | {text[:40]}...")
        else:
            print(f"[{i+1:02d}] Eval failed")

    except Exception as e:
        print(f"[{i+1:02d}] Error: {e}")

    time.sleep(0.5)

# Summary statistics
print("\n" + "=" * 60)
print("EVALUATION RESULTS TABLE")
print("=" * 60)

if results:
    total = len(results)
    avg_cer = sum(r["cer"] for r in results) / total
    avg_rtf = sum(r["rtf"] for r in results) / total
    min_rtf = min(r["rtf"] for r in results)
    max_rtf = max(r["rtf"] for r in results)

    oov_results = [r for r in results if r["has_oov"]]
    no_oov_results = [r for r in results if not r["has_oov"]]

    avg_cer_oov = sum(r["cer"] for r in oov_results) / len(oov_results) if oov_results else 0
    avg_cer_no_oov = sum(r["cer"] for r in no_oov_results) / len(no_oov_results) if no_oov_results else 0

    print(f"Total sentences evaluated:  {total}")
    print(f"Sentences with OOV tokens:  {len(oov_results)}")
    print(f"Sentences without OOV:      {len(no_oov_results)}")
    print(f"")
    print(f"Average CER (all):          {avg_cer:.4f}")
    print(f"Average CER (with OOV):     {avg_cer_oov:.4f}")
    print(f"Average CER (without OOV):  {avg_cer_no_oov:.4f}")
    print(f"")
    print(f"Average RTF:                {avg_rtf:.4f}")
    print(f"Min RTF:                    {min_rtf:.4f}")
    print(f"Max RTF:                    {max_rtf:.4f}")
    print(f"Real-time capable:          {'YES' if avg_rtf < 1.0 else 'NO'}")

    # Domain breakdown
    print(f"\nDomain Breakdown:")
    domains = {}
    for r in results:
        d = r["domain"]
        if d not in domains:
            domains[d] = []
        domains[d].append(r)

    for domain, domain_results in sorted(domains.items()):
        d_cer = sum(r["cer"] for r in domain_results) / len(domain_results)
        d_rtf = sum(r["rtf"] for r in domain_results) / len(domain_results)
        print(f"  {domain:15s}: CER={d_cer:.4f} RTF={d_rtf:.4f} n={len(domain_results)}")

    # Save results to JSON
    with open("data/eval_results/batch_eval_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total": total,
                "avg_cer": avg_cer,
                "avg_rtf": avg_rtf,
                "min_rtf": min_rtf,
                "max_rtf": max_rtf,
                "avg_cer_with_oov": avg_cer_oov,
                "avg_cer_without_oov": avg_cer_no_oov
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to data/eval_results/batch_eval_results.json")

print("=" * 60)