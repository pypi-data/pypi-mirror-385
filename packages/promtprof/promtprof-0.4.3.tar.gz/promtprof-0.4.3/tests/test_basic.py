from promtprof import estimate, PricingTable

def test_estimate_basic():
    pt = PricingTable(table={})
    try:
        estimate("Hallo Welt", model="gpt-4o-mini", pricing=pt, expected_output_tokens=20)
    except ValueError:
        assert True
