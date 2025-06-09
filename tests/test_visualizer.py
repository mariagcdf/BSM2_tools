from bsm2tools.visualizer import graficar_sankey_causas_explicaciones

def test_graficar_sankey_dummy(monkeypatch):
    # Datos simulados para una violación
    violaciones_info = [{
        'fecha': '2025-01-10',
        'causas_directas': ['TRH (d) bajo', 'F/M alto'],
        'explicaciones': ['↑Q (posible lluvia)', '↓ T'],
        'estrategias_control_reactivas': ['Ajuste en TRC tras violación']
    }]

    # Simular entrada de usuario para evitar input()
    monkeypatch.setattr("builtins.input", lambda _: "todo")

    # Simplemente se asegura de que la función corre sin error
    graficar_sankey_causas_explicaciones(violaciones_info, columna_objetivo='NH4_efluente')
