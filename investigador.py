import pandas as pd

# --- IMPORTANTE ---
# Escribe aquí el nombre EXACTO de tu archivo de datos grande
# (Probablemente 'db-ens-bc.csv' o 'denue_inegi_02_.csv')
nombre_de_tu_archivo = 'db-ens-bc.csv'

print(f"--- Iniciando el Investigador de Archivos ---")
print(f"Voy a analizar el archivo: '{nombre_de_tu_archivo}'")

try:
    # Cargar solo las primeras 5 filas para que sea rápido
    df = pd.read_csv(nombre_de_tu_archivo, encoding='latin1', nrows=5)

    print("\n¡Archivo leído con éxito! Estas son las columnas que encontré:")
    
    # Imprimir la lista de todas las columnas
    print("--------------------------------------------------")
    for columna in df.columns:
        print(f"- {columna}")
    print("--------------------------------------------------")
    
    print("\nCopia esta lista de columnas y muéstramela para poder darte el script de filtrado final.")

except FileNotFoundError:
    print(f"\nERROR: No encontré el archivo '{nombre_de_tu_archivo}'.")
    print("Asegúrate de que el nombre esté bien escrito y que el archivo esté en esta misma carpeta.")
except Exception as e:
    print(f"\nOcurrió un error inesperado: {e}")