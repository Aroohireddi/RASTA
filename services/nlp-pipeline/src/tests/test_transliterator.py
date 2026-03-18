import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from transliterator import transliterate_english_to_telugu, reconstruct_sentence

def test_transliterate_basic():
    result = transliterate_english_to_telugu("hello")
    assert len(result) > 0
    assert result != "hello"

def test_reconstruct_sentence():
    tokens = [
        {"final_token": "నమస్కారం", "tag": "TE"},
        {"final_token": "హెల్లో", "tag": "EN"}
    ]
    result = reconstruct_sentence(tokens)
    assert "నమస్కారం" in result
    assert "హెల్లో" in result