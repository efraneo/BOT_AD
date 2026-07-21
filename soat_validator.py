"""
soat_validator.py
Validación de imágenes de SOAT usando RapidOCR y PIL (Sin OpenCV).
"""
import re
import io
import numpy as np
from PIL import Image
from datetime import date
from config import Config


class SOATValidator:
    def __init__(self):
        self.min_quality = Config.MIN_IMAGE_QUALITY_SCORE
        self.min_width = Config.MIN_IMAGE_WIDTH
        self.min_height = Config.MIN_IMAGE_HEIGHT
        self.dias_alerta = Config.SOAT_ALERTA_DIAS
        self._engine = None

    @property
    def engine(self):
        if self._engine is None:
            from rapidocr_onnxruntime import RapidOCR
            self._engine = RapidOCR()
        return self._engine

    def validar_archivo(self, archivo_bytes: bytes, nombre_archivo: str) -> dict:
        resultado = {"calidad_ok": False, "calidad_score": 0.0, "calidad_mensaje": "", "texto_extraido": "", "fecha_vencimiento": None, "estado": "No legible", "mensaje_general": ""}
        ext = nombre_archivo.lower().rsplit(".", 1)[-1] if "." in nombre_archivo else ""
        if f".{ext}" not in {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}:
            resultado["calidad_mensaje"] = "Formato no válido. Use JPG, PNG, BMP, TIFF o WEBP."
            resultado["mensaje_general"] = resultado["calidad_mensaje"]
            return resultado
        try:
            imagen_pil = Image.open(io.BytesIO(archivo_bytes))
            if imagen_pil.mode != 'RGB': imagen_pil = imagen_pil.convert('RGB')
        except Exception as e:
            resultado["calidad_mensaje"] = f"Error al leer la imagen: {e}"
            resultado["mensaje_general"] = resultado["calidad_mensaje"]
            return resultado

        calidad = self._evaluar_calidad(imagen_pil)
        resultado["calidad_score"], resultado["calidad_ok"], resultado["calidad_mensaje"] = calidad["score"], calidad["ok"], calidad["mensaje"]
        if not calidad["ok"]:
            resultado["mensaje_general"] = f"❌ Imagen no apta: {calidad['mensaje']}."
            resultado["estado"] = "No legible"
            return resultado

        texto = self._extraer_texto(imagen_pil)
        resultado["texto_extraido"] = texto
        if not texto or len(texto.strip()) < 15:
            resultado["estado"] = "No legible"
            resultado["mensaje_general"] = "❌ No se pudo extraer texto del SOAT."
            return resultado

        fecha_venc = self._buscar_fecha_vencimiento(texto)
        resultado["fecha_vencimiento"] = fecha_venc
        if not fecha_venc:
            resultado["estado"] = "No legible"
            resultado["mensaje_general"] = "⚠️ Se extrajo texto pero no se encontró la fecha de vencimiento."
            return resultado

        estado = self._determinar_estado(fecha_venc)
        resultado["estado"] = estado
        fecha_str = fecha_venc.strftime("%d/%m/%Y")
        if estado == "Vigente": resultado["mensaje_general"] = f"✅ SOAT VIGENTE. Vence: {fecha_str}."
        elif estado == "Por vencer": resultado["mensaje_general"] = f"⚠️ SOAT POR VENCER. Vence: {fecha_str} ({(fecha_venc - date.today()).days} días)."
        else: resultado["mensaje_general"] = f"🚨 SOAT VENCIDO. Venció: {fecha_str}."
        return resultado

    def _evaluar_calidad(self, imagen_pil: Image.Image) -> dict:
        resultados = {"score": 0.0, "ok": False, "mensaje": ""}
        w, h = imagen_pil.size
        if w < self.min_width or h < self.min_height:
            resultados["mensaje"] = f"Resolución muy baja ({w}x{h})."
            return resultados
        gris_np = np.array(imagen_pil.convert('L'), dtype=np.float64)
        laplacian = (gris_np[:-2, 1:-1] + gris_np[2:, 1:-1] + gris_np[1:-1, :-2] + gris_np[1:-1, 2:] - 4 * gris_np[1:-1, 1:-1])
        varianza = np.var(laplacian)
        score = round(varianza, 2)
        resultados["score"] = score
        if varianza < self.min_quality: resultados["mensaje"] = f"Imagen borrosa (índice: {score})."; return resultados
        brillo = np.mean(gris_np)
        if brillo < 40: resultados["mensaje"] = "Imagen demasiado oscura."; return resultados
        if brillo > 240: resultados["mensaje"] = "Imagen sobreexpuesta."; return resultados
        resultados["ok"] = True
        resultados["mensaje"] = f"Calidad aceptable (nitidez: {score})."
        return resultados

    def _extraer_texto(self, imagen_pil: Image.Image) -> str:
        try:
            resultados, _ = self.engine(imagen_pil)
            if not resultados: return ""
            return " ".join([txt for (_, txt, conf) in resultados if conf > 0.4]).strip()
        except Exception as e:
            print(f"Error en OCR: {e}"); return ""

    def _buscar_fecha_vencimiento(self, texto: str) -> date | None:
        texto_upper = texto.upper()
        for kw in ["VENCIMIENTO", "VIGENCIA", "EXPIRA", "FECHA DE VENC", "VENCE", "VALIDO HASTA", "VIGENTE HASTA", "HASTA", "FIN DE VIGENCIA", "TERMINO", "VTO"]:
            idx = texto_upper.find(kw)
            if idx != -1:
                fecha = self._extraer_fecha_de_texto(texto[idx:idx+80])
                if fecha: return fecha
        todas = self._extraer_todas_fechas(texto)
        return sorted(todas, reverse=True)[0] if todas else None

    def _extraer_fecha_de_texto(self, texto: str) -> date | None:
        for pat in [r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})']:
            m = re.search(pat, texto)
            if m:
                try:
                    nums = [int(x) for x in m.groups()]
                    d, mo, y = (nums[2], nums[1], nums[0]) if len(m.group(1)) == 4 else (nums[0], nums[1], nums[2])
                    if 1 <= d <= 31 and 1 <= mo <= 12 and 2000 <= y <= 2035: return date(y, mo, d)
                except: pass
        return None

    def _extraer_todas_fechas(self, texto: str) -> list:
        fechas = []
        for pat in [r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})']:
            for m in re.finditer(pat, texto):
                try:
                    nums = [int(x) for x in m.groups()]
                    d, mo, y = (nums[2], nums[1], nums[0]) if len(m.group(1)) == 4 else (nums[0], nums[1], nums[2])
                    if 1 <= d <= 31 and 1 <= mo <= 12 and 2000 <= y <= 2035: fechas.append(date(y, mo, d))
                except: pass
        return fechas

    def _determinar_estado(self, fecha_vencimiento: date) -> str:
        diff = (fecha_vencimiento - date.today()).days
        if diff < 0: return "Vencido"
        if diff <= self.dias_alerta: return "Por vencer"
        return "Vigente"
