import os
import json
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

class FacturaExtractor:
    """Motor de extracción de datos para facturas usando Gemini 1.5 Flash."""
    
    def __init__(self):
        # Cargamos el entorno y verificamos la API Key
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            print("[DEBUG] Variables de entorno actuales:", list(os.environ.keys()))
            raise ValueError("GOOGLE_API_KEY no encontrada. Asegúrate de que el archivo .env exista y contenga la clave.")
            
        self.client = genai.Client(api_key=api_key)

    def _get_prompt(self) -> str:
        """Define el prompt estructurado con los campos requeridos por AFIP."""
        fields = [
            "Fecha", "Tipo", "Punto de Venta", "Número Desde", "Número Hasta",
            "Cód. Autorización", "Tipo Doc. Emisor", "Nro. Doc. Emisor",
            "Denominación Emisor", "Tipo Doc. Receptor", "Nro. Doc. Receptor",
            "Tipo Cambio", "Moneda", "Neto Grav. IVA 0%", "IVA 2,5%",
            "Neto Grav. IVA 2,5%", "IVA 5%", "Neto Grav. IVA 5%", "IVA 10,5%",
            "Neto Grav. IVA 10,5%", "IVA 21%", "Neto Grav. IVA 21%", "IVA 27%",
            "Neto Grav. IVA 27%", "Neto Gravado Total", "Neto No Gravado",
            "Op. Exentas", "Otros Tributos", "Total IVA", "Imp. Total"
        ]
        return f"""
        Actúa como un experto contable argentino. Analiza el documento y extrae los siguientes campos: {', '.join(fields)}.
        
        REGLAS CRÍTICAS:
        1. Responde ÚNICAMENTE con un objeto JSON válido.
        2. Formato de fecha: AAAA-MM-DD.
        3. Valores numéricos: usa punto para decimales (ej: 1250.50). Si el valor no existe, usa 0.
        4. Para Facturas B o C, desglosa el IVA según las alícuotas detectadas.
        """

    def extract(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Procesa una factura (PDF/Imagen) y devuelve los datos en formato diccionario."""
        path = Path(file_path)
        if not path.exists():
            return None

        # Gemini detecta automáticamente si es PDF o imagen por el MIME type
        mime_type = "application/pdf" if path.suffix.lower() == ".pdf" else "image/jpeg"
        
        try:
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    types.Part.from_bytes(data=path.read_bytes(), mime_type=mime_type),
                    self._get_prompt()
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            return json.loads(response.text)
        except Exception as e:
            print(f"[ERROR] Falló la extracción en {file_path}: {e}")
            return None

def save_to_excel(data: Dict[str, Any], output_path: str = "Mis Comprobantes Recibidos.xlsx"):
    """Guarda los datos en un archivo Excel, anexando si ya existe."""
    df_new = pd.DataFrame([data])
    
    if Path(output_path).exists():
        try:
            df_existing = pd.read_excel(output_path)
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        except Exception:
            df_final = df_new
    else:
        df_final = df_new
        
    df_final.to_excel(output_path, index=False)
    print(f"[INFO] Datos persistidos en {output_path}")
