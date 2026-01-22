from engine.calculator import ProcurementCalculator

def test_calculator_regex():
    calc = ProcurementCalculator()
    
    test_cases = [
        # Should trigger (True)
        ("Calculame el procedimiento para 50000 soles", True, "Explicit amount"),
        ("Tengo un monto de 100000 para obras", True, "Amount with context"),
        ("S/ 45000 en bienes", True, "Currency symbol"),
        
        # Should NOT trigger (False)
        ("Cual es el 10% de garantia", False, "Percentage symbol"),
        ("garantia del 10 por ciento", False, "Percentage text"),
        ("el 10% de 50000", True, "Percentage of amount - should technically trigger on 50000?"), # This is tricky, let's see behavior
        ("10% de adelanto", False, "Just percentage"),
        ("cual es la garantia de fiel cumplimiento", False, "No numbers")
    ]
    
    print("Running Calculator Regex Tests...")
    print("-" * 60)
    failed = False
    
    for message, expected, desc in test_cases:
        result = calc.detect_and_calculate(message)
        triggered = result is not None
        
        status = "PASS" if triggered == expected else "FAIL"
        if status == "FAIL":
            failed = True
            
        print(f"[{status}] '{message}'")
        print(f"   Expected: {expected}, Got: {triggered}")
        if result and not expected:
            print(f"   Incorrectly returned: {result[:50]}...")
        print("-" * 60)

    if failed:
        print("\n❌ Summary: Some tests FAILED.")
    else:
        print("\n✅ Summary: All tests PASSED.")

if __name__ == "__main__":
    test_calculator_regex()
