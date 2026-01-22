from engine.calculator import ProcurementCalculator

def test_routing_logic():
    calc = ProcurementCalculator()
    
    test_cases = [
        # Should TRIGGER calculator (Pure calculation intent)
        ("Calculame procedimiento para 50000 soles", True, "Pure calculation"),
        ("Tengo S/ 100000 para obras", True, "Amount + Type"),
        
        # Should BYPASS calculator (Legal/Complex intent despite numbers)
        ("Tengo un servicio de S/ 100,000. ¿Puedo convocar una Adjudicación Simplificada?", False, "Contains 'simplificada'"),
        ("Soy cuñado del alcalde, monto menor a 1 UIT", False, "Contains 'cuñado'/'alcalde'"),
        ("Llevo acumulado el 9.5% de penalidad", False, "Contains 'penalidad'"),
        ("Cual es la garantía de fiel cumplimiento", False, "Contains 'garantía'"),
        ("Es legal contratar por 50000 soles si estoy impedido", False, "Contains 'impedido'/'legal'"),
        ("Plazo para apelacion de buena pro de 5 millones", False, "Contains 'apelacion'")
    ]
    
    print("Running Routing Logic Tests...")
    print("-" * 60)
    failed = False
    
    for message, expected_trigger, desc in test_cases:
        result = calc.detect_and_calculate(message)
        triggered = result is not None
        
        status = "PASS" if triggered == expected_trigger else "FAIL"
        if status == "FAIL":
            failed = True
            
        print(f"[{status}] '{message}'")
        print(f"   Expected Trigger: {expected_trigger}, Got: {triggered}")
        print("-" * 60)

    if failed:
        print("\n❌ Summary: Routing tests FAILED.")
    else:
        print("\n✅ Summary: All routing tests PASSED.")

if __name__ == "__main__":
    test_routing_logic()
