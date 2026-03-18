import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from codemixer import extract_protected_tokens, restore_protected_tokens, codemix

def test_protect_tokens():
    text = "ISRO launched Chandrayaan successfully"
    protected, mapping = extract_protected_tokens(text)
    assert "ORSI" in protected or "ISRO"[::-1] in protected
    assert "ISRO" in mapping.values()

def test_restore_tokens():
    mapping = {"ORSI": "ISRO"}
    text = "ORSI launched successfully"
    restored = restore_protected_tokens(text, mapping)
    assert "ISRO" in restored

def test_codemix_returns_required_keys():
    result = codemix("The Prime Minister visited Hyderabad today")
    assert "original" in result
    assert "codemixed" in result
    assert "tagged_tokens" in result
    assert "oov_tokens" in result