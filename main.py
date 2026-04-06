import sys
import json
from pathlib import Path
from extractor import FacturaExtractor, save_to_excel

def main():
    """
    Procesa facturas de forma masiva desde la carpeta 'bills' o un archivo individual.
    """
    
    # Definimos la carpeta de facturas por defecto
    bills_dir = Path("bills")
    
    # Si se pasa un argumento, procesamos ese archivo/directorio específico
    if len(sys.argv) >= 2:
        target = Path(sys.argv[1])
    else:
        target = bills_dir

    # Verificamos la existencia del objetivo
    if not target.exists():
        if target == bills_dir:
            target.mkdir()
            print(f"[INFO] Carpeta '{bills_dir}' creada. Coloca tus facturas allí.")
        else:
            print(f"[ERROR] No se encontró: {target}")
        return

    # Identificamos los archivos a procesar (PDF e imágenes)
    valid_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
    if target.is_dir():
        files_to_process = [f for f in target.iterdir() if f.suffix.lower() in valid_extensions]
    else:
        files_to_process = [target] if target.suffix.lower() in valid_extensions else []

    if not files_to_process:
        print(f"[INFO] No se encontraron archivos válidos para procesar en {target}")
        return

    print(f"--- Iniciando procesamiento de {len(files_to_process)} archivo(s) ---")
    extractor = FacturaExtractor()
    
    for file_path in files_to_process:
        print(f"\nProcesando: {file_path.name}...")
        data = extractor.extract(str(file_path))
        
        if data:
            print(f"[SUCCESS] {file_path.name} procesado correctamente.")
            save_to_excel(data)
        else:
            print(f"[ERROR] Falló el procesamiento de {file_path.name}")

    print("\n--- Proceso finalizado ---")

if __name__ == "__main__":
    main()
