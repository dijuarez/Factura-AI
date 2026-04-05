import sys
import json
from extractor import FacturaExtractor, save_to_excel

def main():
    """
    Interfaz de línea de comandos (CLI) para procesar facturas localmente.
    Sirve como entorno de pruebas para validar la extracción con Gemini 1.5 Flash 
    antes de integrar el archivo en el flujo automatizado de n8n.
    """
    
    # --- CONFIGURACIÓN DE RUTA ---
    # Puedes definir un archivo por defecto para pruebas rápidas aquí:
    file_path = "factura_test.pdf" 

    # Si pasas un argumento (ej: uv run main.py mi_factura.jpg), tiene prioridad
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]

    if not file_path:
        print("Uso: uv run main.py <ruta_del_archivo>")
        return

    print(f"--- Iniciando procesamiento de {file_path} ---")
    
    # Instanciamos el motor de extracción (requiere GOOGLE_API_KEY en .env)
    extractor = FacturaExtractor()
    
    # Ejecutamos la llamada multimodal a Gemini
    data = extractor.extract(file_path)
    
    if data:
        print("\n[SUCCESS] Extracción exitosa. Datos recuperados:")
        # Mostramos el JSON formateado para validación visual
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Persistimos la información en el archivo Excel local
        save_to_excel(data)
    else:
        print("\n[ERROR] No se pudo extraer la información del documento.")

if __name__ == "__main__":
    main()
