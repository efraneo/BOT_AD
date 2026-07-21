"""
database.py
Operaciones de base de datos con Supabase.
"""
import uuid
from datetime import datetime, timezone, date
from supabase import create_client, Client
from config import Config


class Database:
    """Clase para interactuar con Supabase."""

    def __init__(self):
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )

    # ═══════════════════════════════════════════════════
    #  OPERACIONES 2FA
    # ═══════════════════════════════════════════════════

    def guardar_codigo_2fa(self, correo: str, codigo: str, expiracion: datetime) -> bool:
        try:
            self.client.table("codigos_2fa").insert({
                "correo": correo, "codigo": codigo,
                "expiracion": expiracion.isoformat(), "verificado": False
            }).execute()
            return True
        except Exception as e:
            print(f"Error guardando código 2FA: {e}")
            return False

    def verificar_codigo_2fa(self, correo: str, codigo_ingresado: str) -> dict:
        try:
            ahora = datetime.now(timezone.utc).isoformat()
            response = (
                self.client.table("codigos_2fa").select("*")
                .eq("correo", correo).eq("codigo", codigo_ingresado)
                .eq("verificado", False).gte("expiracion", ahora)
                .order("creado_en", desc=True).limit(1).execute()
            )
            if response.data:
                self.client.table("codigos_2fa").update(
                    {"verificado": True}
                ).eq("id", response.data[0]["id"]).execute()
                return {"valido": True, "mensaje": "Código verificado correctamente."}

            response_exp = (
                self.client.table("codigos_2fa").select("*")
                .eq("correo", correo).eq("codigo", codigo_ingresado)
                .eq("verificado", False).lt("expiracion", ahora)
                .order("creado_en", desc=True).limit(1).execute()
            )
            if response_exp.data:
                return {"valido": False, "mensaje": "El código ha expirado. Solicita uno nuevo."}
            return {"valido": False, "mensaje": "Código incorrecto."}
        except Exception as e:
            return {"valido": False, "mensaje": f"Error de verificación: {e}"}

    def limpiar_codigos_antiguos(self):
        try:
            ahora = datetime.now(timezone.utc).isoformat()
            self.client.table("codigos_2fa").delete().lt("expiracion", ahora).execute()
        except Exception:
            pass

    # ═══════════════════════════════════════════════════
    #  OPERACIONES TRABAJADORES
    # ═══════════════════════════════════════════════════

    def existe_identificacion(self, identificacion: str) -> bool:
        try:
            response = self.client.table("trabajadores").select("id").eq("identificacion", identificacion).execute()
            return len(response.data) > 0
        except Exception:
            return False

    def existe_correo(self, correo: str) -> bool:
        try:
            response = self.client.table("trabajadores").select("id").eq("correo", correo).execute()
            return len(response.data) > 0
        except Exception:
            return False

    def subir_archivo_soat(self, archivo_bytes: bytes, nombre_archivo: str) -> str:
        try:
            extension = nombre_archivo.rsplit(".", 1)[-1] if "." in nombre_archivo else "jpg"
            nombre_unico = f"{uuid.uuid4().hex}_{nombre_archivo}"
            self.client.storage.from_(Config.SOAT_STORAGE_BUCKET).upload(
                path=nombre_unico,
                file=archivo_bytes,
                file_options={"content-type": "application/octet-stream"}
            )
            return self.client.storage.from_(Config.SOAT_STORAGE_BUCKET).get_public_url(nombre_unico)
        except Exception as e:
            print(f"Error subiendo archivo SOAT: {e}")
            raise Exception(f"No se pudo subir el archivo: {e}")

    def registrar_trabajador(self, datos: dict) -> dict:
        try:
            response = self.client.table("trabajadores").insert(datos).execute()
            if response.data:
                return {"exito": True, "datos": response.data[0]}
            return {"exito": False, "mensaje": "No se recibieron datos del servidor."}
        except Exception as e:
            error_msg = str(e)
            if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                return {"exito": False, "mensaje": "Ya existe un registro con esa identificación o correo."}
            return {"exito": False, "mensaje": f"Error al registrar: {error_msg}"}

    def obtener_todos_trabajadores(self) -> list:
        try:
            response = self.client.table("trabajadores").select("*").order("fecha_registro", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo trabajadores: {e}")
            return []

    def eliminar_trabajador(self, trabajador_id: str) -> bool:
        try:
            self.client.table("trabajadores").delete().eq("id", trabajador_id).execute()
            return True
        except Exception as e:
            print(f"Error eliminando trabajador: {e}")
            return False

    def obtener_trabajador_por_id(self, trabajador_id: str) -> dict | None:
        try:
            response = self.client.table("trabajadores").select("*").eq("id", trabajador_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error buscando por ID: {e}")
            return None

    def actualizar_trabajador(self, trabajador_id: str, datos: dict, archivo_bytes: bytes = None, nombre_archivo: str = None) -> dict:
        """Actualiza datos de un trabajador. Si se pasa un archivo, sube el nuevo SOAT."""
        try:
            if archivo_bytes and nombre_archivo:
                url_soat = self.subir_archivo_soat(archivo_bytes, nombre_archivo)
                datos["soat_url"] = url_soat
                datos["soat_nombre_archivo"] = nombre_archivo
                
                # Si actualiza la imagen, re-validamos
                from soat_validator import SOATValidator
                validator = SOATValidator()
                res_soat = validator.validar_archivo(archivo_bytes, nombre_archivo)
                datos["soat_estado"] = res_soat.get("estado", "No legible")
                datos["soat_vigencia"] = res_soat.get("fecha_vencimiento").isoformat() if res_soat.get("fecha_vencimiento") else None
                datos["soat_calidad_imagen"] = res_soat.get("calidad_score", 0)
                datos["calidad_imagen_ok"] = res_soat.get("calidad_ok", False)

            response = self.client.table("trabajadores").update(datos).eq("id", trabajador_id).execute()
            if response.data:
                return {"exito": True, "datos": response.data[0]}
            return {"exito": False, "mensaje": "No se recibieron datos del servidor."}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

    # ═══════════════════════════════════════════════════
    #  OPERACIONES GARITA Y SST
    # ═══════════════════════════════════════════════════

    def buscar_por_placa(self, placa: str) -> dict | None:
        try:
            placa = placa.upper().strip()
            response = self.client.table("trabajadores").select("*").eq("placa", placa).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error buscando placa: {e}")
            return None

    def registrar_ingreso_garita(self, placa: str, nombre: str, cargo: str, estado: str, correo: str):
        try:
            self.client.table("historial_garita").insert({
                "placa": placa.upper().strip(), "nombre_trabajador": nombre,
                "cargo": cargo, "estado_soat": estado, "correo_trabajador": correo
            }).execute()
        except Exception as e:
            print(f"Error guardando historial garita: {e}")

    def obtener_historial_hoy(self) -> list:
        try:
            hoy = date.today().isoformat()
            response = (
                self.client.table("historial_garita").select("*")
                .gte("fecha_ingreso", hoy).order("fecha_ingreso", desc=True).execute()
            )
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo historial de hoy: {e}")
            return []

    # ═══════════════════════════════════════════════════
    #  INDICADORES
    # ═══════════════════════════════════════════════════

    def obtener_indicadores(self) -> dict:
        try:
            todos = self.obtener_todos_trabajadores()
            if not todos:
                return {"total": 0, "vigentes": 0, "vencidos": 0, "por_vencer": 0, "no_legibles": 0, "pendientes": 0,
                        "pct_vigentes": 0, "pct_vencidos": 0, "pct_por_vencer": 0, "pct_no_legibles": 0,
                        "por_tipo_vehiculo": {}, "por_cargo": {}, "por_mes": {}, "ultimos_registros": [], "alertas": []}

            total = len(todos)
            vigentes = [t for t in todos if t["soat_estado"] == "Vigente"]
            vencidos = [t for t in todos if t["soat_estado"] == "Vencido"]
            por_vencer = [t for t in todos if t["soat_estado"] == "Por vencer"]
            no_legibles = [t for t in todos if t["soat_estado"] == "No legible"]
            pendientes = [t for t in todos if t["soat_estado"] == "Pendiente"]

            por_tipo, por_cargo, por_mes, alertas = {}, {}, {}, []
            for t in todos:
                tv = t.get("tipo_vehiculo", "Sin dato"); por_tipo[tv] = por_tipo.get(tv, 0) + 1
                cargo = t.get("cargo", "Sin dato"); por_cargo[cargo] = por_cargo.get(cargo, 0) + 1
                if t.get("fecha_registro"):
                    try:
                        clave = datetime.fromisoformat(t["fecha_registro"].replace("Z", "+00:00")).strftime("%Y-%m")
                        por_mes[clave] = por_mes.get(clave, 0) + 1
                    except Exception: pass

            for t in vencidos: alertas.append({"tipo": "danger", "mensaje": f"SOAT VENCIDO - {t['nombres']} ({t['placa']})"})
            for t in por_vencer: alertas.append({"tipo": "warning", "mensaje": f"SOAT POR VENCER - {t['nombres']} ({t['placa']})"})
            for t in no_legibles: alertas.append({"tipo": "info", "mensaje": f"SOAT NO LEGIBLE - {t['nombres']} ({t['placa']})"})

            return {
                "total": total, "vigentes": len(vigentes), "vencidos": len(vencidos),
                "por_vencer": len(por_vencer), "no_legibles": len(no_legibles), "pendientes": len(pendientes),
                "pct_vigentes": round(len(vigentes)/total*100, 1), "pct_vencidos": round(len(vencidos)/total*100, 1),
                "pct_por_vencer": round(len(por_vencer)/total*100, 1), "pct_no_legibles": round(len(no_legibles)/total*100, 1),
                "por_tipo_vehiculo": por_tipo, "por_cargo": por_cargo,
                "por_mes": dict(sorted(por_mes.items(), reverse=True)[:6]),
                "ultimos_registros": todos[:10], "alertas": alertas
            }
        except Exception as e:
            print(f"Error generando indicadores: {e}")
            return {"total": 0, "vigentes": 0, "vencidos": 0, "por_vencer": 0, "no_legibles": 0, "pendientes": 0,
                    "pct_vigentes": 0, "pct_vencidos": 0, "pct_por_vencer": 0, "pct_no_legibles": 0,
                    "por_tipo_vehiculo": {}, "por_cargo": {}, "por_mes": {}, "ultimos_registros": [], "alertas": []}
