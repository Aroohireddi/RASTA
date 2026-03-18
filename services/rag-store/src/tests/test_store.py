import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_bootstrap_runs():
    from bootstrap import bootstrap_store
    count = bootstrap_store()
    assert count >= 0

def test_disambiguate_known_token():
    from store import disambiguate_token
    result = disambiguate_token("ISRO")
    assert "token" in result
    assert "matched" in result

def test_disambiguate_unknown_token():
    from store import disambiguate_token
    result = disambiguate_token("xyzunknown123")
    assert result["matched"] == False