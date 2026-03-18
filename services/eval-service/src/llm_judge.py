import os
import json

def judge_naturalness(
    original_text: str,
    transcription: str,
    oov_tokens: list[str] = []
) -> dict:
    """
    Use Claude as LLM-as-judge for TTS naturalness evaluation.
    Requires ANTHROPIC_API_KEY environment variable.
    Returns scores on 3 dimensions (1-5 each).
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "skipped": True,
            "reason": "ANTHROPIC_API_KEY not set",
            "fidelity": None,
            "naturalness": None,
            "intelligibility": None
        }

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""You are evaluating a Telugu-English code-mixed text-to-speech system.

Original text: {original_text}
ASR transcription of synthesized audio: {transcription}
English OOV tokens that were transliterated: {oov_tokens}

Rate on a scale of 1-5 for each dimension:
1. Transcription fidelity: How accurately does the transcription match the original? (1=very poor, 5=perfect)
2. Code-mixing naturalness: Does the mixing of Telugu and English sound natural for a Telugu-English bilingual speaker? (1=very unnatural, 5=very natural)
3. OOV intelligibility: Are the English technical terms and named entities intelligible in the Telugu script? (1=not intelligible, 5=perfectly intelligible)

Respond ONLY with a JSON object like this:
{{"fidelity": 4, "naturalness": 3, "intelligibility": 5, "reasoning": "brief explanation"}}"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()
        scores = json.loads(response_text)
        scores["skipped"] = False
        return scores

    except Exception as e:
        print(f"[llm_judge] Error: {e}")
        return {
            "skipped": True,
            "reason": str(e),
            "fidelity": None,
            "naturalness": None,
            "intelligibility": None
        }