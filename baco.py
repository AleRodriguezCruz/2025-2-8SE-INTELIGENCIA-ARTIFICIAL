# -*- Alejandra Rodriguez de la Cruz -*-
#  22760049

# --- Base de Conocimiento (BANCO) ---
# hechos que consideramos verdaderos sobre nuestro banco.
hechos = {
    # Personas y sus roles
    "cliente('Ana')",
    "cliente('Carlos')",
    "cliente('Sofia')",
    "asesor('Luis')",

    # Qué tipo de cuentas tiene cada cliente
    "tiene_cuenta('Ana', 'ahorros')",
    "tiene_cuenta('Ana', 'credito')",
    "tiene_cuenta('Carlos', 'ahorros')",
    "tiene_cuenta('Sofia', 'nomina')",

    # Relaciones y estados de cuenta
    "es_asesor_de('Luis', 'Ana')",
    "tiene_saldo_suficiente('Ana')",
    "tiene_saldo_suficiente('Sofia')",
}

# --- LEYES / REGLAS ---

"""
    Ley 1: Una persona es un cliente activo si tiene al menos una cuenta.
    """
def es_cliente_activo(persona):
    
    # Recorremos todos los hechos para ver si la persona tiene alguna cuenta.
    for hecho in hechos:
        if hecho.startswith(f"tiene_cuenta('{persona}',"):
            return True # Encontramos al menos una cuenta, es cliente activo.
    return False # No encontramos ninguna cuenta para esa persona.

def es_cliente_premium(persona):
    """
    Ley 2: Un cliente es "premium" si tiene más de un tipo de cuenta.
    """
    # Creamos una lista para contar las cuentas de la persona.
    cuentas_encontradas = []
    for hecho in hechos:
        if hecho.startswith(f"tiene_cuenta('{persona}',"):
            cuentas_encontradas.append(hecho)

    # Si el número de cuentas en la lista es mayor que 1, es premium.
    if len(cuentas_encontradas) > 1:
        return True
    else:
        return False

def puede_recibir_prestamo(persona):
    """
    Ley 3: Un cliente puede recibir un préstamo si es un cliente activo
    Y además tiene saldo suficiente.
    """
    # Verificamos si ambas condiciones se cumplen usando las otras leyes y hechos.
    condicion1 = es_cliente_activo(persona)
    condicion2 = f"tiene_saldo_suficiente('{persona}')" in hechos

    if condicion1 and condicion2:
        return True # Se cumplen ambas, sí puede.
    else:
        return False # Falla al menos una, no puede.

def es_atendido_por(cliente, asesor):
    """
    Ley 4: Un cliente es atendido por un asesor si existe un hecho que los relacione.
    """
    # Construimos el texto del hecho que buscamos.
    texto_a_buscar = f"es_asesor_de('{asesor}', '{cliente}')"

    # Si ese hecho exacto existe, la ley es verdadera.
    if texto_a_buscar in hechos:
        return True
    else:
        return False


# --- CONSULTAS ---

if __name__ == "__main__":
    print("--- CONSULTAS VERDADERAS ---")
    print(f"1. ¿Es Ana una cliente premium? \n   Respuesta: {es_cliente_premium('Ana')}\n")
    print(f"2. ¿Puede Sofia recibir un préstamo? \n   Respuesta: {puede_recibir_prestamo('Sofia')}\n")
    print(f"3. ¿Es Ana atendida por Luis? \n   Respuesta: {es_atendido_por('Ana', 'Luis')}\n")

    print("--- CONSULTAS FALSAS ---")
    print(f"4. ¿Es Carlos un cliente premium? \n   Respuesta: {es_cliente_premium('Carlos')}\n")
    print(f"5. ¿Puede Carlos recibir un préstamo? \n   Respuesta: {puede_recibir_prestamo('Carlos')}\n")
    print(f"6. ¿Es Sofia atendida por Luis? \n   Respuesta: {es_atendido_por('Sofia', 'Luis')}\n")

    print("--- CONSULTAS INFORMATIVAS ---")
    # Para estas, creamos una lista de todas las personas que conocemos.
    personas = ['Ana', 'Carlos', 'Sofia', 'Luis']

    # Pregunta 7: ¿Quiénes son los clientes premium del banco?
    clientes_premium = []
    for persona in personas:
        # Por cada persona, verificamos si cumple la ley de ser premium.
        if es_cliente_premium(persona):
            clientes_premium.append(persona)
    print(f"7. ¿Quiénes son los clientes premium? \n   Respuesta: {clientes_premium}\n")

    # Pregunta 8: ¿Quiénes son candidatos para un préstamo?
    candidatos_prestamo = []
    for persona in personas:
        if puede_recibir_prestamo(persona):
            candidatos_prestamo.append(persona)
    print(f"8. ¿Quiénes pueden recibir un préstamo? \n   Respuesta: {candidatos_prestamo}\n")
