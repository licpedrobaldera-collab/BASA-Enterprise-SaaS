"""
=============================================================================
BASA ENTERPRISE SAAS SUITE - PRODUCCIÓN 10/10 (NIC/NIIF/NIF + AUDITORÍA FULL)
Autor / Licenciatario: Lic. Pedro Baldera (licpedrobaldera@gmail.com)
WhatsApp Soporte: +1 (829) 771-7390
Mensualidad Estándar: RD$ 2,500.00
=============================================================================
LISTO PARA PRODUCCIÓN:
 - Cero datos de muestra/demo precargados (base limpia de producción).
 - Solo acceso Maestro ('862600') y Plan de Cuentas Base NIC/NIIF/NIF.
 - Base de Datos Dual: PostgreSQL (Nube vía DATABASE_URL) + SQLite Local.
 - Conector Real API e-CF DGII (.p12 + XMLDSig + TrackId) y Reportes PDF.
 - Estados Financieros NIC 1 / NIC 7 / NIIF / NIF en tiempo real:
   Situación Financiera, Resultados Integral, Flujos de Efectivo y Patrimonio.
 - Auditoría Forense y Cumplimiento Normativo: detección automática de
   descuadres de partida doble, violaciones NIC/NIIF, precios bajo costo,
   stock negativo, RNC/ITBIS DGII inválido y anomalías de seguridad.
=============================================================================
"""

import io
import json
import os
import random
import sqlite3
import urllib.parse
import zipfile
from datetime import date, datetime

import pandas as pd
import streamlit as st

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# =============================================================================
# 1. CONFIGURACIÓN DE PÁGINA E IDENTIDAD CORPORATIVA
# =============================================================================
st.set_page_config(
    page_title="BASA Enterprise Producción | Lic. Pedro Baldera",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

CORREO_ADMIN = "licpedrobaldera@gmail.com"
WHATSAPP_ADMIN = "18297717390"
PRECIO_MENSUALIDAD = "RD$ 2,500.00"
TARIFA_MENSUAL_NUM = 2500.00
DB_PATH = "basa_saas_produccion.db"
CLAVE_MAESTRA_ADMIN = "862600"

DGII_ENDPOINTS = {
    "TesteCF (Pruebas)": "https://ecf.dgii.gov.do/TesteCF",
    "CerteCF (Certificación)": "https://ecf.dgii.gov.do/CerteCF",
    "eCF (Producción)": "https://ecf.dgii.gov.do/eCF",
}

st.markdown(
    """
    <style>
    .basa-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: #f8fafc;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #334155;
    }
    .basa-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        background-color: #059669;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# 2. MOTOR DE BASE DE DATOS DUAL (POSTGRESQL NUBE + SQLITE LOCAL)
# =============================================================================
def get_database_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    if not url:
        try:
            url = st.secrets.get("DATABASE_URL", "")
        except Exception:
            url = ""
    return url.strip()


class UnifiedCursor:
    def __init__(self, cursor, is_postgres: bool):
        self._cur = cursor
        self._pg = is_postgres

    def execute(self, sql: str, params=None):
        query = sql.replace("?", "%s") if self._pg else sql
        if params is None:
            self._cur.execute(query)
        else:
            self._cur.execute(query, params)
        return self

    def executemany(self, sql: str, seq_of_params):
        query = sql.replace("?", "%s") if self._pg else sql
        self._cur.executemany(query, seq_of_params)
        return self

    def fetchone(self):
        row = self._cur.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        return [dict(r) for r in self._cur.fetchall()]


class UnifiedDB:
    def __init__(self):
        db_url = get_database_url()
        if db_url and HAS_PSYCOPG2:
            self.is_postgres = True
            self.conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        else:
            self.is_postgres = False
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

    def cursor(self):
        return UnifiedCursor(self.conn.cursor(), self.is_postgres)

    def execute(self, sql: str, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        self.conn.close()


def get_db():
    return UnifiedDB()


def motor_db_activo() -> str:
    return "PostgreSQL (Nube)" if (get_database_url() and HAS_PSYCOPG2) else "SQLite (Local Producción)"


def ddl_auto_id(is_pg: bool) -> str:
    return "SERIAL PRIMARY KEY" if is_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"


def inicializar_db():
    """Inicializa esquema limpio de producción (sin datos de muestra)."""
    with get_db() as conn:
        pk_auto = ddl_auto_id(conn.is_postgres)
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                telefono TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT,
                fecha_registro TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'ACTIVO',
                rango INTEGER DEFAULT 1,
                codigo_6_digitos TEXT UNIQUE NOT NULL
            )
            """
        )

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS repositorios (
                id {pk_auto},
                titulo TEXT NOT NULL,
                descripcion TEXT,
                categoria TEXT,
                fecha TEXT NOT NULL,
                generado_por TEXT NOT NULL,
                codigo_base TEXT
            )
            """
        )

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS crm_oportunidades (
                id {pk_auto},
                empresa TEXT NOT NULL,
                contacto TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                etapa TEXT NOT NULL DEFAULT 'Prospecto',
                valor_estimado REAL NOT NULL DEFAULT 0.0,
                probabilidad INTEGER NOT NULL DEFAULT 20,
                responsable TEXT NOT NULL,
                notas TEXT,
                fecha_creacion TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS inventario (
                sku TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                stock_minimo INTEGER NOT NULL DEFAULT 5,
                costo_unitario REAL NOT NULL DEFAULT 0.0,
                precio_venta REAL NOT NULL DEFAULT 0.0,
                itbis_aplica INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS facturas_ecf (
                id {pk_auto},
                encf TEXT UNIQUE NOT NULL,
                tipo_ecf TEXT NOT NULL,
                rnc_cliente TEXT NOT NULL,
                nombre_cliente TEXT NOT NULL,
                subtotal REAL NOT NULL,
                itbis REAL NOT NULL,
                total REAL NOT NULL,
                moneda TEXT NOT NULL DEFAULT 'DOP',
                estado_dgii TEXT NOT NULL DEFAULT 'ACEPTADO e-CF',
                track_id TEXT,
                xml_contenido TEXT,
                fecha TEXT NOT NULL,
                creado_por TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS plan_cuentas (
                codigo TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                subtipo TEXT NOT NULL DEFAULT 'Corriente'
            )
            """
        )

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS asientos_contables (
                id {pk_auto},
                fecha TEXT NOT NULL,
                referencia TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                cuenta_codigo TEXT NOT NULL,
                debito REAL NOT NULL DEFAULT 0.0,
                credito REAL NOT NULL DEFAULT 0.0,
                creado_por TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS empleados (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                cedula TEXT NOT NULL,
                departamento TEXT NOT NULL,
                cargo TEXT NOT NULL,
                salario_bruto REAL NOT NULL,
                estado TEXT NOT NULL DEFAULT 'ACTIVO',
                fecha_ingreso TEXT NOT NULL
            )
            """
        )

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS office_docs (
                id {pk_auto},
                titulo TEXT NOT NULL,
                tipo TEXT NOT NULL,
                contenido TEXT NOT NULL,
                autor TEXT NOT NULL,
                actualizado_en TEXT NOT NULL
            )
            """
        )

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS proyectos_tareas (
                id {pk_auto},
                proyecto TEXT NOT NULL,
                titulo TEXT NOT NULL,
                prioridad TEXT NOT NULL DEFAULT 'Media',
                estado TEXT NOT NULL DEFAULT 'Por Hacer',
                asignado_a TEXT NOT NULL,
                fecha_limite TEXT NOT NULL
            )
            """
        )

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS auditoria (
                id {pk_auto},
                fecha TEXT NOT NULL,
                usuario TEXT NOT NULL,
                modulo TEXT NOT NULL,
                accion TEXT NOT NULL,
                detalle TEXT
            )
            """
        )

        # Únicamente el Catálogo Contable Estándar NIC / NIIF / NIF (sin datos de prueba)
        if cur.execute("SELECT COUNT(*) AS c FROM plan_cuentas").fetchone()["c"] == 0:
            cuentas_niif = [
                ("1101", "Efectivo y Equivalentes (NIC 7)", "Activo", "Corriente"),
                ("1102", "Cuentas por Cobrar Comerciales (NIIF 9)", "Activo", "Corriente"),
                ("1103", "Inventarios (NIC 2)", "Activo", "Corriente"),
                ("1201", "Propiedad, Planta y Equipo (NIC 16)", "Activo", "No Corriente"),
                ("1202", "Activos Intangibles y Software (NIC 38)", "Activo", "No Corriente"),
                ("2101", "Cuentas por Pagar Comerciales", "Pasivo", "Corriente"),
                ("2102", "ITBIS por Pagar (DGII)", "Pasivo", "Corriente"),
                ("2103", "Retenciones TSS e ISR por Pagar", "Pasivo", "Corriente"),
                ("2201", "Préstamos Financieros a Largo Plazo (NIIF 9)", "Pasivo", "No Corriente"),
                ("3101", "Capital Social Suscrito y Pagado (NIC 1)", "Patrimonio", "Patrimonio"),
                ("3102", "Resultados Acumulados", "Patrimonio", "Patrimonio"),
                ("4101", "Ingresos de Actividades Ordinarias (NIIF 15)", "Ingreso", "Operacional"),
                ("5101", "Costo de Ventas (NIC 2)", "Costo", "Operacional"),
                ("6101", "Gastos de Personal y Beneficios (NIC 19)", "Gasto", "Operacional"),
                ("6102", "Gastos Generales y Administrativos", "Gasto", "Operacional"),
            ]
            cur.executemany(
                "INSERT INTO plan_cuentas (codigo, nombre, tipo, subtipo) VALUES (?, ?, ?, ?)",
                cuentas_niif,
            )

        conn.commit()


inicializar_db()


# =============================================================================
# 3. CONECTOR REAL API e-CF DGII, AUDITORÍA FORENSE Y REPORTES PDF
# =============================================================================
class DGIIConnector:
    def __init__(self, ambiente_url: str, rnc_emisor: str, p12_bytes: bytes = None, p12_pass: str = ""):
        self.base_url = ambiente_url.rstrip("/")
        self.rnc_emisor = rnc_emisor.strip()
        self.p12_bytes = p12_bytes
        self.p12_pass = p12_pass
        self.token = None

    def tiene_certificado(self) -> bool:
        return bool(self.p12_bytes and self.p12_pass)

    def obtener_semilla(self) -> str:
        if not HAS_REQUESTS:
            raise RuntimeError("Instale 'requests' para conectar con la API de la DGII.")
        resp = requests.get(f"{self.base_url}/autenticacion/api/autenticacion/semilla", timeout=15)
        resp.raise_for_status()
        return resp.text

    def firmar_xml_con_p12(self, xml_str: str) -> str:
        from cryptography.hazmat.primitives.serialization import Encoding, pkcs12
        from lxml import etree
        from signxml import XMLSigner

        private_key, certificate, _ = pkcs12.load_key_and_certificates(
            self.p12_bytes, self.p12_pass.encode("utf-8")
        )
        root = etree.fromstring(xml_str.encode("utf-8"))
        signer = XMLSigner(method=XMLSigner.Methods.enveloped)
        signed_root = signer.sign(root, key=private_key, cert=certificate.public_bytes(Encoding.PEM))
        return etree.tostring(signed_root, encoding="utf-8", xml_declaration=True).decode("utf-8")

    def autenticar(self) -> str:
        semilla_xml = self.obtener_semilla()
        semilla_firmada = self.firmar_xml_con_p12(semilla_xml)
        files = {"xml": ("semilla.xml", semilla_firmada.encode("utf-8"), "text/xml")}
        resp = requests.post(
            f"{self.base_url}/autenticacion/api/autenticacion/validacioncertificado",
            files=files,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        self.token = data.get("token")
        if not self.token:
            raise RuntimeError(f"DGII no retornó token: {data}")
        return self.token

    def enviar_ecf(self, encf: str, xml_sin_firma: str) -> dict:
        if not self.tiene_certificado():
            return {
                "modo": "LOCAL",
                "trackId": f"LOC-{encf}-{random.randint(1000,9999)}",
                "estado": "GENERADO LOCAL (Falta .p12)",
                "xml_final": xml_sin_firma,
            }
        token = self.autenticar()
        xml_firmado = self.firmar_xml_con_p12(xml_sin_firma)
        headers = {"Authorization": f"Bearer {token}"}
        files = {"xml": (f"{encf}.xml", xml_firmado.encode("utf-8"), "text/xml")}
        resp = requests.post(
            f"{self.base_url}/recepcion/api/facturaselectronicas",
            headers=headers,
            files=files,
            timeout=25,
        )
        resp.raise_for_status()
        res_json = resp.json()
        return {
            "modo": "DGII_API",
            "trackId": res_json.get("trackId", ""),
            "estado": res_json.get("estado", "ENVIADO DGII"),
            "xml_final": xml_firmado,
        }

    def consultar_trackid(self, track_id: str) -> dict:
        if not self.tiene_certificado() or str(track_id).startswith("LOC-"):
            return {"trackId": track_id, "estado": "Generado localmente (Cargue .p12 para validar en DGII)"}
        token = self.autenticar()
        resp = requests.get(
            f"{self.base_url}/consultaresultado/api/consultas/estado",
            params={"TrackId": track_id},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()


def ejecutar_auditoria_forense() -> list:
    """Audita integridad contable (NIC/NIIF), fiscal (DGII), inventario, RRHH y seguridad."""
    hallazgos = []
    with get_db() as conn:
        # 1. Partida doble por referencia
        descuadres = conn.execute(
            """
            SELECT referencia, ROUND(SUM(debito) - SUM(credito), 2) AS diff
            FROM asientos_contables
            GROUP BY referencia
            HAVING ABS(SUM(debito) - SUM(credito)) > 0.01
            """
        ).fetchall()
        for d in descuadres:
            hallazgos.append({
                "Severidad": "CRÍTICA",
                "Norma": "NIC 1 / Partida Doble",
                "Irregularidad": f"Asiento {d['referencia']} descuadrado por RD$ {d['diff']:,.2f}",
                "Prevención": "Corregir o reversar el asiento para garantizar Débito = Crédito.",
            })

        # 2. Ecuación Patrimonial (Activo = Pasivo + Patrimonio + Resultado)
        saldos = conn.execute(
            """
            SELECT p.tipo, COALESCE(SUM(a.debito) - SUM(a.credito), 0) AS neto
            FROM plan_cuentas p
            LEFT JOIN asientos_contables a ON p.codigo = a.cuenta_codigo
            GROUP BY p.tipo
            """
        ).fetchall()
        mapa_t = {r["tipo"]: r["neto"] for r in saldos}
        activos = mapa_t.get("Activo", 0.0)
        pasivos = -mapa_t.get("Pasivo", 0.0)
        patrimonio = -mapa_t.get("Patrimonio", 0.0)
        ingresos = -mapa_t.get("Ingreso", 0.0)
        costos_gastos = mapa_t.get("Costo", 0.0) + mapa_t.get("Gasto", 0.0)
        utilidad = ingresos - costos_gastos
        diff_eq = round(activos - (pasivos + patrimonio + utilidad), 2)
        if abs(diff_eq) > 0.01:
            hallazgos.append({
                "Severidad": "CRÍTICA",
                "Norma": "NIC 1 / Ecuación Patrimonial",
                "Irregularidad": f"Desequilibrio Activo vs Pasivo+Patrimonio de RD$ {diff_eq:,.2f}",
                "Prevención": "Auditar cuentas sin clasificar o asientos unilaterales.",
            })

        # 3. Inventario negativo o precio bajo costo (NIC 2 / Fraude)
        inv_anom = conn.execute(
            "SELECT sku, nombre, stock, stock_minimo, costo_unitario, precio_venta FROM inventario"
        ).fetchall()
        for p in inv_anom:
            if p["stock"] < 0:
                hallazgos.append({
                    "Severidad": "ALTA",
                    "Norma": "NIC 2 (Inventarios)",
                    "Irregularidad": f"SKU {p['sku']} ({p['nombre']}) con stock negativo ({p['stock']})",
                    "Prevención": "Bloquear ventas sin existencia y realizar conteo físico.",
                })
            if p["precio_venta"] < p["costo_unitario"]:
                hallazgos.append({
                    "Severidad": "ALTA",
                    "Norma": "NIC 2 / Control Interno",
                    "Irregularidad": f"SKU {p['sku']} con precio de venta ({p['precio_venta']:,.2f}) menor al costo ({p['costo_unitario']:,.2f})",
                    "Prevención": "Ajustar lista de precios o registrar deterioro VNR.",
                })

        # 4. Cumplimiento Fiscal DGII (e-CF 31 sin RNC válido o sin TrackId real)
        facts = conn.execute("SELECT encf, tipo_ecf, rnc_cliente, subtotal, itbis, track_id FROM facturas_ecf").fetchall()
        for f in facts:
            rnc_clean = "".join(ch for ch in str(f["rnc_cliente"]) if ch.isdigit())
            if str(f["tipo_ecf"]).startswith("31") and len(rnc_clean) not in (9, 11):
                hallazgos.append({
                    "Severidad": "ALTA",
                    "Norma": "DGII Norma 06-18 / Ley 32-23",
                    "Irregularidad": f"e-CF {f['encf']} tipo 31 con RNC/Cédula inválido ({f['rnc_cliente']})",
                    "Prevención": "Validar RNC de 9 u 11 dígitos antes de timbrar Crédito Fiscal.",
                })
            if not f["track_id"] or str(f["track_id"]).startswith("LOC-"):
                hallazgos.append({
                    "Severidad": "MEDIA",
                    "Norma": "DGII e-CF Transmisión",
                    "Irregularidad": f"e-CF {f['encf']} emitido en modo local sin TrackId oficial DGII",
                    "Prevención": "Cargar certificado .p12 en Conector DGII y retransmitir.",
                })

        # 5. Cumplimiento Laboral (NIC 19 / TSS)
        emps = conn.execute("SELECT id, nombre, cedula, salario_bruto FROM empleados WHERE estado = 'ACTIVO'").fetchall()
        for e in emps:
            if len("".join(ch for ch in str(e["cedula"]) if ch.isdigit())) < 9:
                hallazgos.append({
                    "Severidad": "MEDIA",
                    "Norma": "TSS / Código de Trabajo RD",
                    "Irregularidad": f"Empleado {e['id']} ({e['nombre']}) sin Cédula/NSS válido",
                    "Prevención": "Completar documento de identidad antes de reportar TSS.",
                })

    if not hallazgos:
        hallazgos.append({
            "Severidad": "OK",
            "Norma": "NIC / NIIF / DGII / TSS",
            "Irregularidad": "0 irregularidades detectadas en el sistema.",
            "Prevención": "Mantener auditorías periódicas y respaldo de base de datos.",
        })
    return hallazgos


def generar_pdf_factura(factura: dict, rnc_emisor: str = "131000001") -> bytes:
    if not HAS_REPORTLAB:
        return b""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    elementos = [
        Paragraph("<b>BASA ENTERPRISE SAAS - REPRESENTACIÓN IMPRESA e-CF</b>", styles["Title"]),
        Paragraph(f"Emisor: Lic. Pedro Baldera | RNC Emisor: {rnc_emisor} | Soporte: {CORREO_ADMIN}", styles["Normal"]),
        Spacer(1, 14),
    ]
    datos_cab = [
        ["Comprobante (e-NCF):", factura["encf"], "Fecha:", factura["fecha"]],
        ["Tipo e-CF:", factura["tipo_ecf"], "Estado DGII:", factura["estado_dgii"]],
        ["Cliente:", factura["nombre_cliente"], "RNC / Cédula:", factura["rnc_cliente"]],
        ["TrackId DGII:", factura.get("track_id") or "N/A", "Moneda:", factura["moneda"]],
    ]
    t_cab = Table(datos_cab, colWidths=[1.5 * inch, 2.2 * inch, 1.2 * inch, 1.9 * inch])
    t_cab.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e2e8f0")), ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e2e8f0")), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")), ("FONTSIZE", (0, 0), (-1, -1), 9), ("PADDING", (0, 0), (-1, -1), 6)]))
    elementos.extend([t_cab, Spacer(1, 18)])

    datos_tot = [
        ["Descripción", "Subtotal", "ITBIS (18%)", "Total"],
        [f"Servicios / Bienes ({factura['encf']})", f"{factura['moneda']} {factura['subtotal']:,.2f}", f"{factura['moneda']} {factura['itbis']:,.2f}", f"{factura['moneda']} {factura['total']:,.2f}"],
    ]
    t_tot = Table(datos_tot, colWidths=[3.1 * inch, 1.2 * inch, 1.2 * inch, 1.3 * inch])
    t_tot.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("ALIGN", (1, 0), (-1, -1), "RIGHT"), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")), ("FONTSIZE", (0, 0), (-1, -1), 10), ("PADDING", (0, 0), (-1, -1), 8)]))
    elementos.extend([t_tot, Spacer(1, 20), Paragraph(f"Verificación DGII: https://ecf.dgii.gov.do/consultatimbres?RncEmisor={rnc_emisor}&ENCF={factura['encf']}", styles["Italic"])])
    doc.build(elementos)
    return buf.getvalue()


def generar_pdf_nomina(filas_nomina: list) -> bytes:
    if not HAS_REPORTLAB:
        return b""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, rightMargin=30, leftMargin=30, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    elementos = [
        Paragraph("<b>BASA ENTERPRISE - NÓMINA Y VOLANTES DE PAGO (TSS / ISR RD)</b>", styles["Title"]),
        Paragraph(f"Fecha de emisión: {date.today()} | Generado por BASA SaaS Producción", styles["Normal"]),
        Spacer(1, 14),
    ]
    cuerpo = [["ID", "Colaborador", "Bruto", "AFP 2.87%", "SFS 3.04%", "ISR", "Neto a Pagar"]]
    for f in filas_nomina:
        cuerpo.append([f["ID"], f["Nombre"][:22], f"{f['Salario Bruto']:,.2f}", f"{f['AFP (2.87%)']:,.2f}", f"{f['SFS (3.04%)']:,.2f}", f"{f['ISR Mensual']:,.2f}", f"{f['Salario Neto']:,.2f}"])
    tabla = Table(cuerpo, colWidths=[0.7 * inch, 1.7 * inch, 1.0 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 1.1 * inch])
    tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("ALIGN", (2, 1), (-1, -1), "RIGHT"), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")), ("FONTSIZE", (0, 0), (-1, -1), 8.5), ("PADDING", (0, 0), (-1, -1), 6)]))
    elementos.append(tabla)
    doc.build(elementos)
    return buf.getvalue()


# =============================================================================
# 4. UTILIDADES DE NEGOCIO, AUDITORÍA Y LICENCIAS
# =============================================================================
def registrar_auditoria(usuario: str, modulo: str, accion: str, detalle: str = ""):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO auditoria (fecha, usuario, modulo, accion, detalle) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), usuario, modulo, accion, detalle),
        )
        conn.commit()


def verificar_licencia(codigo: str):
    codigo = codigo.strip()
    if codigo == CLAVE_MAESTRA_ADMIN:
        return {
            "id": "ADMIN",
            "nombre": "Lic. Pedro Baldera",
            "email": CORREO_ADMIN,
            "telefono": WHATSAPP_ADMIN,
            "estado": "ACTIVO",
            "fecha_registro": "Acceso Maestro Perpetuo",
            "es_admin": True,
        }
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, nombre, email, telefono, estado, fecha_registro FROM clientes WHERE codigo_6_digitos = ?",
            (codigo,),
        ).fetchone()
        if row:
            return {**row, "es_admin": False}
    return None


def generar_token_unico():
    with get_db() as conn:
        while True:
            t = f"{random.randint(100000, 999999)}"
            if t == CLAVE_MAESTRA_ADMIN:
                continue
            if conn.execute("SELECT COUNT(*) AS c FROM clientes WHERE codigo_6_digitos = ?", (t,)).fetchone()["c"] == 0:
                return t


def calcular_nomina_rd(salario_bruto: float) -> dict:
    afp_empleado = round(salario_bruto * 0.0287, 2)
    sfs_empleado = round(salario_bruto * 0.0304, 2)
    anual = (salario_bruto - afp_empleado - sfs_empleado) * 12
    if anual <= 416220.00:
        isr_anual = 0.0
    elif anual <= 624329.00:
        isr_anual = (anual - 416220.01) * 0.15
    elif anual <= 867123.00:
        isr_anual = 31216.00 + (anual - 624329.01) * 0.20
    else:
        isr_anual = 79776.00 + (anual - 867123.01) * 0.25
    isr_mensual = round(isr_anual / 12, 2)
    total_deducciones = round(afp_empleado + sfs_empleado + isr_mensual, 2)
    salario_neto = round(salario_bruto - total_deducciones, 2)
    costo_total_empresa = round(salario_bruto * (1 + 0.0710 + 0.0709 + 0.0110 + 0.0100), 2)
    return {
        "afp_emp": afp_empleado,
        "sfs_emp": sfs_empleado,
        "isr_emp": isr_mensual,
        "total_ded": total_deducciones,
        "neto": salario_neto,
        "costo_empresa": costo_total_empresa,
    }


def generar_xml_ecf(encf: str, tipo_ecf: str, rnc: str, nombre: str, subtotal: float, itbis: float, total: float, rnc_emisor: str = "131000001") -> str:
    fecha_emision = datetime.now().strftime("%d-%m-%Y")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ECF>
  <Encabezado>
    <Version>1.0</Version>
    <IdDoc><TipoeCF>{tipo_ecf[:2]}</TipoeCF><eNCF>{encf}</eNCF><FechaVencimientoSecuencia>31-12-2027</FechaVencimientoSecuencia></IdDoc>
    <Emisor><RNCEmisor>{rnc_emisor}</RNCEmisor><RazonSocialEmisor>BASA ENTERPRISE SAAS - LIC. PEDRO BALDERA</RazonSocialEmisor><FechaEmision>{fecha_emision}</FechaEmision></Emisor>
    <Comprador><RNCComprador>{rnc}</RNCComprador><RazonSocialComprador>{nombre}</RazonSocialComprador></Comprador>
    <Totales><MontoGravadoTotal>{subtotal:.2f}</MontoGravadoTotal><ITBIS1>18</ITBIS1><TotalITBIS>{itbis:.2f}</TotalITBIS><MontoTotal>{total:.2f}</MontoTotal></Totales>
  </Encabezado>
</ECF>"""


# =============================================================================
# 5. PORTAL DE ACCESO (PRODUCCIÓN)
# =============================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "cliente_info" not in st.session_state:
    st.session_state.cliente_info = None
if "dgii_cfg" not in st.session_state:
    st.session_state.dgii_cfg = {"ambiente": "eCF (Producción)", "rnc_emisor": "", "p12_bytes": None, "p12_pass": ""}

if not st.session_state.autenticado:
    st.markdown(
        """
        <div class="basa-banner" style="text-align:center;">
            <span class="basa-badge">ENTORNO DE PRODUCCIÓN • NIC / NIIF / NIF • AUDITORÍA FORENSE</span>
            <h1 style="margin:0.4rem 0 0.2rem 0;">🏦 BASA ENTERPRISE SAAS SUITE</h1>
            <p style="margin:0; color:#cbd5e1; font-size:1.05rem;">
                ERP NIIF • Estados Financieros NIC 1/7 • e-CF DGII • CRM • Nómina TSS/ISR • Office 365
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        col_l, col_r = st.columns([1.15, 1.0], gap="large")
        with col_l:
            st.subheader("🔑 Validación de Licencia")
            token_input = st.text_input("Token de 6 dígitos", type="password", max_chars=6, placeholder="Ingrese su token corporativo")
            if st.button("🚀 Iniciar Sesión", use_container_width=True, type="primary"):
                res = verificar_licencia(token_input) if token_input else None
                if res and res["estado"] == "ACTIVO":
                    st.session_state.autenticado = True
                    st.session_state.cliente_info = res
                    registrar_auditoria(res["nombre"], "Autenticación", "Inicio de sesión", f"ID: {res['id']}")
                    st.rerun()
                elif res:
                    st.error(f"❌ Cuenta en estado: {res['estado']}. Contacte administración.")
                else:
                    st.error("❌ Token inválido o no registrado.")
        with col_r:
            st.subheader("💳 Soporte y Licenciamiento")
            st.markdown(f"**Mensualidad Estándar:** `{PRECIO_MENSUALIDAD}`")
            st.info(f"📧 **Correo:** {CORREO_ADMIN}\n\n📱 **WhatsApp:** +{WHATSAPP_ADMIN}")
            msj_ws = urllib.parse.quote("Hola Lic. Pedro Baldera, solicito activación de licencia BASA Enterprise.")
            st.markdown(f'<a href="https://wa.me/{WHATSAPP_ADMIN}?text={msj_ws}" target="_blank" style="display:inline-block; padding:10px 16px; background-color:#22c55e; color:white; text-decoration:none; border-radius:6px; font-weight:600; text-align:center; width:100%;">💬 Contactar por WhatsApp</a>', unsafe_allow_html=True)
    st.stop()


# =============================================================================
# 6. BARRA LATERAL Y NAVEGACIÓN
# =============================================================================
cliente = st.session_state.cliente_info
with st.sidebar:
    st.title("🏦 BASA Producción")
    st.markdown(f"**Operador:** {cliente['nombre']}")
    st.caption(f"Rol: {'👑 Administrador Maestro' if cliente['es_admin'] else '👤 Suscriptor'}")
    st.caption(f"Motor BD: **{motor_db_activo()}**")
    st.markdown("---")
    modulo_activo = st.radio(
        "Módulos del Ecosistema",
        [
            "📊 Dashboard Ejecutivo BI",
            "📑 Estados Financieros (NIC/NIIF/NIF)",
            "🛡️ Auditoría Forense & Cumplimiento",
            "🧾 Facturación e-CF & Contabilidad",
            "📈 CRM & Pipeline Ventas",
            "📦 Inventario & POS Omnicanal",
            "👥 RRHH & Nómina RD (TSS/ISR)",
            "💼 BASA Office 365 Suite",
            "🚀 Master IA & Inyector",
            "👤 Control SaaS & Tokens",
        ],
    )
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        registrar_auditoria(cliente["nombre"], "Autenticación", "Cierre de sesión", "")
        st.session_state.autenticado = False
        st.session_state.cliente_info = None
        st.rerun()

hoy = datetime.now()
if not cliente["es_admin"] and hoy.day > 25:
    st.warning(f"⚠️ ALERTA DE COBRO: Faltan {30 - hoy.day} días para el vencimiento de su mensualidad ({PRECIO_MENSUALIDAD}).")


# =============================================================================
# 7. MÓDULOS DE PRODUCCIÓN
# =============================================================================
if modulo_activo == "📊 Dashboard Ejecutivo BI":
    st.title("📊 Centro de Comando Ejecutivo (BI)")
    with get_db() as conn:
        tot_fact = conn.execute("SELECT COALESCE(SUM(total), 0) AS v FROM facturas_ecf").fetchone()["v"]
        crm_pond = conn.execute("SELECT COALESCE(SUM(valor_estimado * probabilidad / 100.0), 0) AS v FROM crm_oportunidades WHERE etapa != 'Perdido'").fetchone()["v"]
        val_inv = conn.execute("SELECT COALESCE(SUM(stock * costo_unitario), 0) AS v FROM inventario").fetchone()["v"]
        nom_bruta = conn.execute("SELECT COALESCE(SUM(salario_bruto), 0) AS v FROM empleados WHERE estado = 'ACTIVO'").fetchone()["v"]
        activos = conn.execute("SELECT COUNT(*) AS v FROM clientes WHERE estado = 'ACTIVO'").fetchone()["v"]
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Facturación e-CF", f"RD$ {tot_fact:,.2f}")
    k2.metric("Pipeline CRM", f"RD$ {crm_pond:,.2f}")
    k3.metric("Inventario", f"RD$ {val_inv:,.2f}")
    k4.metric("Nómina Bruta", f"RD$ {nom_bruta:,.2f}")
    k5.metric("MRR SaaS", f"RD$ {activos * TARIFA_MENSUAL_NUM:,.2f}", f"{activos} activos")


elif modulo_activo == "📑 Estados Financieros (NIC/NIIF/NIF)":
    st.title("📑 Estados Financieros bajo NIC, NIIF y NIF")
    st.caption("Generados automáticamente desde el Libro Mayor en tiempo real conforme a NIC 1, NIC 7, NIIF 9 y NIIF 15.")

    with get_db() as conn:
        df_mayor = pd.DataFrame(
            conn.execute(
                """
                SELECT p.codigo, p.nombre, p.tipo, p.subtipo,
                       COALESCE(SUM(a.debito), 0) AS debito,
                       COALESCE(SUM(a.credito), 0) AS credito
                FROM plan_cuentas p
                LEFT JOIN asientos_contables a ON p.codigo = a.cuenta_codigo
                GROUP BY p.codigo, p.nombre, p.tipo, p.subtipo
                ORDER BY p.codigo
                """
            ).fetchall()
        )
        flujo_caja = conn.execute(
            "SELECT COALESCE(SUM(debito), 0) AS entradas, COALESCE(SUM(credito), 0) AS salidas FROM asientos_contables WHERE cuenta_codigo = '1101'"
        ).fetchone()

    t_bg, t_er, t_fe, t_pat = st.tabs(["⚖️ Situación Financiera (NIC 1)", "📈 Resultados Integral (NIC 1 / NIIF 15)", "💵 Flujos de Efectivo (NIC 7)", "🏛️ Cambios en el Patrimonio & Notas"])

    act_df = df_mayor[df_mayor["tipo"] == "Activo"].copy()
    act_df["Saldo"] = act_df["debito"] - act_df["credito"]
    pas_df = df_mayor[df_mayor["tipo"] == "Pasivo"].copy()
    pas_df["Saldo"] = pas_df["credito"] - pas_df["debito"]
    pat_df = df_mayor[df_mayor["tipo"] == "Patrimonio"].copy()
    pat_df["Saldo"] = pat_df["credito"] - pat_df["debito"]
    ing_df = df_mayor[df_mayor["tipo"] == "Ingreso"].copy()
    ing_df["Saldo"] = ing_df["credito"] - ing_df["debito"]
    cos_df = df_mayor[df_mayor["tipo"] == "Costo"].copy()
    cos_df["Saldo"] = cos_df["debito"] - cos_df["credito"]
    gas_df = df_mayor[df_mayor["tipo"] == "Gasto"].copy()
    gas_df["Saldo"] = gas_df["debito"] - gas_df["credito"]

    tot_ing = ing_df["Saldo"].sum()
    tot_cos = cos_df["Saldo"].sum()
    tot_gas = gas_df["Saldo"].sum()
    utilidad_bruta = tot_ing - tot_cos
    utilidad_antes_imp = utilidad_bruta - tot_gas
    isr_est = round(utilidad_antes_imp * 0.27, 2) if utilidad_antes_imp > 0 else 0.0
    utilidad_neta = utilidad_antes_imp - isr_est

    tot_act = act_df["Saldo"].sum()
    tot_pas = pas_df["Saldo"].sum()
    tot_pat = pat_df["Saldo"].sum() + utilidad_antes_imp

    with t_bg:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Activos (NIC 1)")
            st.dataframe(act_df[["codigo", "nombre", "subtipo", "Saldo"]], use_container_width=True)
            st.metric("Total Activos", f"RD$ {tot_act:,.2f}")
        with c2:
            st.subheader("Pasivos y Patrimonio (NIC 1)")
            st.dataframe(pd.concat([pas_df, pat_df])[["codigo", "nombre", "tipo", "Saldo"]], use_container_width=True)
            st.metric("Total Pasivo + Patrimonio + Resultado", f"RD$ {tot_pas + tot_pat:,.2f}")
        diff_bg = round(tot_act - (tot_pas + tot_pat), 2)
        if abs(diff_bg) <= 0.01:
            st.success("✅ Ecuación Patrimonial Cuadrada (Activo = Pasivo + Patrimonio).")
        else:
            st.error(f"🚨 Descuadre detectado en Balance General: RD$ {diff_bg:,.2f}")

    with t_er:
        st.subheader("Estado de Resultados Integral")
        er_rows = [
            {"Concepto": "Ingresos de Actividades Ordinarias (NIIF 15)", "Monto (RD$)": tot_ing},
            {"Concepto": "(-) Costo de Ventas (NIC 2)", "Monto (RD$)": -tot_cos},
            {"Concepto": "(=) Utilidad Bruta", "Monto (RD$)": utilidad_bruta},
            {"Concepto": "(-) Gastos Operativos y de Personal (NIC 19)", "Monto (RD$)": -tot_gas},
            {"Concepto": "(=) Utilidad Antes de Impuestos", "Monto (RD$)": utilidad_antes_imp},
            {"Concepto": "(-) ISR Corporativo Estimado (27% RD - NIC 12)", "Monto (RD$)": -isr_est},
            {"Concepto": "(=) Utilidad Neta del Período", "Monto (RD$)": utilidad_neta},
        ]
        st.dataframe(pd.DataFrame(er_rows), use_container_width=True)

    with t_fe:
        st.subheader("Estado de Flujos de Efectivo (NIC 7)")
        ent = flujo_caja["entradas"]
        sal = flujo_caja["salidas"]
        f1, f2, f3 = st.columns(3)
        f1.metric("Entradas de Efectivo (1101)", f"RD$ {ent:,.2f}")
        f2.metric("Salidas de Efectivo (1101)", f"RD$ {sal:,.2f}")
        f3.metric("Flujo Neto de Efectivo", f"RD$ {ent - sal:,.2f}")

    with t_pat:
        st.subheader("Cambios en el Patrimonio y Notas Revelatorias")
        st.dataframe(pat_df[["codigo", "nombre", "Saldo"]], use_container_width=True)
        st.info(
            "**Notas a los Estados Financieros:**\n"
            "- **Base de preparación:** Normas Internacionales de Información Financiera (NIIF / NIC 1) y NIF locales.\n"
            "- **Reconocimiento de ingresos (NIIF 15):** Al emitir el comprobante fiscal electrónico (e-CF).\n"
            "- **Inventarios (NIC 2):** Valuados al costo promedio o valor neto realizable, el menor."
        )


elif modulo_activo == "🛡️ Auditoría Forense & Cumplimiento":
    st.title("🛡️ Auditoría Forense, Cumplimiento Normativo y Prevención")
    st.caption("Escaneo automático de irregularidades contables (NIC/NIIF), fiscales (DGII), laborales (TSS) y control interno.")

    if st.button("🔍 Ejecutar Auditoría Full del Sistema", type="primary"):
        registrar_auditoria(cliente["nombre"], "Auditoría Forense", "Escaneo completo ejecutado", "")

    hallazgos = ejecutar_auditoria_forense()
    df_h = pd.DataFrame(hallazgos)
    criticas = sum(1 for h in hallazgos if h["Severidad"] == "CRÍTICA")
    altas = sum(1 for h in hallazgos if h["Severidad"] == "ALTA")
    medias = sum(1 for h in hallazgos if h["Severidad"] == "MEDIA")

    a1, a2, a3 = st.columns(3)
    a1.metric("Violaciones Críticas", criticas)
    a2.metric("Riesgos Altos", altas)
    a3.metric("Alertas Medias", medias)
    st.dataframe(df_h, use_container_width=True)

    st.subheader("📜 Bitácora Inmutable de Operaciones")
    with get_db() as conn:
        df_aud = pd.DataFrame(conn.execute("SELECT id, fecha, usuario, modulo, accion, detalle FROM auditoria ORDER BY id DESC LIMIT 200").fetchall())
    st.dataframe(df_aud, use_container_width=True)


elif modulo_activo == "🧾 Facturación e-CF & Contabilidad":
    st.title("🧾 ERP Contabilidad NIIF & Facturación e-CF DGII")
    t_ecf, t_cfg, t_diario = st.tabs(["⚡ Emisor e-CF DGII", "🔐 Conector API DGII (.p12)", "📒 Libro Diario (Partida Doble)"])

    with t_cfg:
        amb_sel = st.selectbox("Ambiente DGII", list(DGII_ENDPOINTS.keys()), index=list(DGII_ENDPOINTS.keys()).index(st.session_state.dgii_cfg["ambiente"]))
        rnc_em = st.text_input("RNC Emisor Autorizado", value=st.session_state.dgii_cfg["rnc_emisor"])
        p12_file = st.file_uploader("Certificado Digital (.p12 / .pfx)", type=["p12", "pfx"])
        p12_pwd = st.text_input("Contraseña del Certificado", type="password", value=st.session_state.dgii_cfg["p12_pass"])
        if st.button("💾 Guardar Configuración DGII", type="primary"):
            st.session_state.dgii_cfg["ambiente"] = amb_sel
            st.session_state.dgii_cfg["rnc_emisor"] = rnc_em
            st.session_state.dgii_cfg["p12_pass"] = p12_pwd
            if p12_file is not None:
                st.session_state.dgii_cfg["p12_bytes"] = p12_file.read()
            st.success("✅ Configuración DGII guardada en sesión.")

    with t_ecf:
        with st.form("form_ecf"):
            fc1, fc2, fc3 = st.columns(3)
            tipo_ecf = fc1.selectbox("Tipo e-CF", ["31 - Crédito Fiscal", "32 - Consumo", "33 - Nota Débito", "34 - Nota Crédito", "44 - Regímenes Especiales", "45 - Gubernamental"])
            rnc_cli = fc1.text_input("RNC / Cédula Comprador")
            nom_cli = fc2.text_input("Razón Social / Nombre")
            subtotal_ecf = fc2.number_input("Subtotal (RD$)", min_value=0.0, step=100.0)
            aplica_itbis = fc3.checkbox("Aplicar ITBIS 18%", value=True)
            moneda = fc3.selectbox("Moneda", ["DOP", "USD"])

            if st.form_submit_button("⚡ Emitir y Contabilizar e-CF", type="primary"):
                rnc_digits = "".join(c for c in rnc_cli if c.isdigit())
                if tipo_ecf.startswith("31") and len(rnc_digits) not in (9, 11):
                    st.error("❌ Prevención DGII: Para Crédito Fiscal (31) el RNC/Cédula debe tener 9 u 11 dígitos.")
                elif nom_cli and subtotal_ecf > 0:
                    itbis_val = round(subtotal_ecf * 0.18, 2) if aplica_itbis else 0.0
                    total_val = round(subtotal_ecf + itbis_val, 2)
                    cfg = st.session_state.dgii_cfg
                    conector = DGIIConnector(DGII_ENDPOINTS[cfg["ambiente"]], cfg["rnc_emisor"] or "131000001", cfg["p12_bytes"], cfg["p12_pass"])
                    with get_db() as conn:
                        seq = conn.execute("SELECT COUNT(*) + 1 AS s FROM facturas_ecf").fetchone()["s"]
                        encf = f"E{tipo_ecf[:2]}{seq:010d}"
                        xml_base = generar_xml_ecf(encf, tipo_ecf, rnc_cli, nom_cli, subtotal_ecf, itbis_val, total_val, cfg["rnc_emisor"] or "131000001")
                        res_dgii = conector.enviar_ecf(encf, xml_base)
                        conn.execute(
                            "INSERT INTO facturas_ecf (encf, tipo_ecf, rnc_cliente, nombre_cliente, subtotal, itbis, total, moneda, estado_dgii, track_id, xml_contenido, fecha, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (encf, tipo_ecf, rnc_cli, nom_cli, subtotal_ecf, itbis_val, total_val, moneda, res_dgii["estado"], res_dgii["trackId"], res_dgii["xml_final"], datetime.now().strftime("%Y-%m-%d %H:%M"), cliente["nombre"]),
                        )
                        f_hoy = date.today().strftime("%Y-%m-%d")
                        conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, encf, f"Factura e-CF {nom_cli}", "1102", total_val, 0.0, cliente["nombre"]))
                        conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, encf, f"Ingreso {encf}", "4101", 0.0, subtotal_ecf, cliente["nombre"]))
                        if itbis_val > 0:
                            conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, encf, f"ITBIS {encf}", "2102", 0.0, itbis_val, cliente["nombre"]))
                        conn.commit()
                    registrar_auditoria(cliente["nombre"], "DGII e-CF", "Emisión e-CF", f"{encf} | {res_dgii['trackId']}")
                    st.success(f"✅ {encf} emitido y contabilizado ({res_dgii['estado']}).")
                else:
                    st.error("Complete cliente y monto mayor a cero.")

        with get_db() as conn:
            facturas = conn.execute("SELECT * FROM facturas_ecf ORDER BY id DESC").fetchall()
        for f in facturas:
            with st.expander(f"🧾 {f['encf']} | {f['nombre_cliente']} | {f['moneda']} {f['total']:,.2f}"):
                b1, b2 = st.columns(2)
                if f["xml_contenido"]:
                    b1.download_button("📥 XML e-CF", data=f["xml_contenido"], file_name=f"{f['encf']}.xml", mime="application/xml", key=f"xml_{f['id']}")
                if HAS_REPORTLAB:
                    b2.download_button("📄 Factura PDF", data=generar_pdf_factura(f, st.session_state.dgii_cfg["rnc_emisor"] or "131000001"), file_name=f"{f['encf']}.pdf", mime="application/pdf", key=f"pdf_{f['id']}")

    with t_diario:
        with get_db() as conn:
            cuentas = conn.execute("SELECT codigo, nombre FROM plan_cuentas ORDER BY codigo").fetchall()
        opciones = [f"{c['codigo']} - {c['nombre']}" for c in cuentas]
        with st.form("form_asiento"):
            a1, a2, a3 = st.columns(3)
            ref_a = a1.text_input("Referencia", value=f"AS-{random.randint(1000,9999)}")
            desc_a = a1.text_input("Concepto")
            cta_deb = a2.selectbox("Cuenta Débito", opciones, index=0)
            cta_cred = a2.selectbox("Cuenta Crédito", opciones, index=9 if len(opciones) > 9 else 0)
            monto_a = a3.number_input("Monto (RD$)", min_value=0.0, step=100.0)
            if st.form_submit_button("Contabilizar Asiento", type="primary"):
                if desc_a and monto_a > 0 and cta_deb != cta_cred:
                    f_hoy = date.today().strftime("%Y-%m-%d")
                    with get_db() as conn:
                        conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, ref_a, desc_a, cta_deb.split(" - ")[0], monto_a, 0.0, cliente["nombre"]))
                        conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, ref_a, desc_a, cta_cred.split(" - ")[0], 0.0, monto_a, cliente["nombre"]))
                        conn.commit()
                    registrar_auditoria(cliente["nombre"], "Contabilidad", "Asiento Manual", f"{ref_a}: RD$ {monto_a:,.2f}")
                    st.success("✅ Asiento contabilizado.")
                    st.rerun()
        with get_db() as conn:
            st.dataframe(pd.DataFrame(conn.execute("SELECT * FROM asientos_contables ORDER BY id DESC").fetchall()), use_container_width=True)


elif modulo_activo == "📈 CRM & Pipeline Ventas":
    st.title("📈 CRM & Pipeline Comercial")
    with st.form("form_crm"):
        c1, c2, c3 = st.columns(3)
        emp = c1.text_input("Empresa")
        cont = c1.text_input("Contacto")
        tel = c2.text_input("WhatsApp")
        etapa = c2.selectbox("Etapa", ["Prospecto", "Calificado", "Propuesta", "Negociación", "Ganado", "Perdido"])
        val = c3.number_input("Valor Estimado (RD$)", min_value=0.0, step=1000.0)
        prob = c3.slider("Probabilidad (%)", 0, 100, 50)
        if st.form_submit_button("Guardar Oportunidad", type="primary") and emp and cont:
            with get_db() as conn:
                conn.execute("INSERT INTO crm_oportunidades (empresa, contacto, telefono, email, etapa, valor_estimado, probabilidad, responsable, notas, fecha_creacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (emp, cont, tel, "", etapa, val, prob, cliente["nombre"], "", date.today().strftime("%Y-%m-%d")))
                conn.commit()
            st.rerun()
    with get_db() as conn:
        ops = conn.execute("SELECT * FROM crm_oportunidades ORDER BY id DESC").fetchall()
    for op in ops:
        st.write(f"🏢 **{op['empresa']}** | 👤 {op['contacto']} | {op['etapa']} | RD$ {op['valor_estimado']:,.2f}")


elif modulo_activo == "📦 Inventario & POS Omnicanal":
    st.title("📦 Inventario & POS")
    t_pos, t_inv = st.tabs(["🛒 POS", "📋 Inventario"])
    with t_inv:
        with st.form("form_inv"):
            i1, i2, i3 = st.columns(3)
            sku = i1.text_input("SKU")
            nom = i1.text_input("Producto")
            stk = i2.number_input("Stock", min_value=0, value=10)
            cost = i2.number_input("Costo", min_value=0.0, value=0.0)
            prec = i3.number_input("Precio Venta", min_value=0.0, value=0.0)
            if st.form_submit_button("Guardar SKU", type="primary") and sku and nom:
                if prec < cost:
                    st.warning("⚠️ Prevención NIC 2: El precio de venta es menor al costo.")
                with get_db() as conn:
                    conn.execute("INSERT INTO inventario (sku, nombre, categoria, stock, stock_minimo, costo_unitario, precio_venta, itbis_aplica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (sku, nom, "General", stk, 5, cost, prec, 1))
                    conn.commit()
                st.rerun()
        with get_db() as conn:
            st.dataframe(pd.DataFrame(conn.execute("SELECT * FROM inventario ORDER BY sku").fetchall()), use_container_width=True)

    with t_pos:
        with get_db() as conn:
            prods = conn.execute("SELECT * FROM inventario WHERE stock > 0").fetchall()
        if not prods:
            st.info("Registre productos en la pestaña Inventario para comenzar a vender.")
        else:
            mapa = {f"{p['sku']} | {p['nombre']} (Stock: {p['stock']})": p for p in prods}
            with st.form("form_pos"):
                sel = st.selectbox("Producto", list(mapa.keys()))
                cant = st.number_input("Cantidad", min_value=1, step=1)
                if st.form_submit_button("💳 Procesar Venta POS", type="primary"):
                    p = mapa[sel]
                    if cant <= p["stock"]:
                        sub = round(p["precio_venta"] * cant, 2)
                        itb = round(sub * 0.18, 2)
                        tot = round(sub + itb, 2)
                        with get_db() as conn:
                            conn.execute("UPDATE inventario SET stock = stock - ? WHERE sku = ?", (cant, p["sku"]))
                            seq = conn.execute("SELECT COUNT(*) + 1 AS s FROM facturas_ecf").fetchone()["s"]
                            encf = f"E32{seq:010d}"
                            conn.execute("INSERT INTO facturas_ecf (encf, tipo_ecf, rnc_cliente, nombre_cliente, subtotal, itbis, total, moneda, estado_dgii, track_id, xml_contenido, fecha, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (encf, "32 - Consumo", "000000000", "Consumidor Final", sub, itb, tot, "DOP", "POS LOCAL", f"LOC-{encf}", "", datetime.now().strftime("%Y-%m-%d %H:%M"), cliente["nombre"]))
                            conn.commit()
                        st.success(f"✅ Venta {encf} por RD$ {tot:,.2f}")
                        st.rerun()


elif modulo_activo == "👥 RRHH & Nómina RD (TSS/ISR)":
    st.title("👥 RRHH & Nómina RD (TSS / ISR)")
    with st.form("form_emp"):
        e1, e2, e3 = st.columns(3)
        eid = e1.text_input("ID", value=f"EMP-{random.randint(100,999)}")
        enom = e1.text_input("Nombre Completo")
        eced = e2.text_input("Cédula / NSS")
        edep = e2.selectbox("Departamento", ["Dirección", "Finanzas", "Tecnología", "Ventas", "Operaciones"])
        esal = e3.number_input("Salario Bruto (RD$)", min_value=0.0, step=1000.0)
        if st.form_submit_button("Registrar Colaborador", type="primary") and enom and eced:
            with get_db() as conn:
                conn.execute("INSERT INTO empleados (id, nombre, cedula, departamento, cargo, salario_bruto, estado, fecha_ingreso) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (eid, enom, eced, edep, "Colaborador", esal, "ACTIVO", date.today().strftime("%Y-%m-%d")))
                conn.commit()
            st.rerun()

    with get_db() as conn:
        emps = conn.execute("SELECT * FROM empleados WHERE estado = 'ACTIVO'").fetchall()
    filas = []
    for e in emps:
        c = calcular_nomina_rd(e["salario_bruto"])
        filas.append({"ID": e["id"], "Nombre": e["nombre"], "Salario Bruto": e["salario_bruto"], "AFP (2.87%)": c["afp_emp"], "SFS (3.04%)": c["sfs_emp"], "ISR Mensual": c["isr_emp"], "Salario Neto": c["neto"]})
    if filas:
        df_n = pd.DataFrame(filas)
        st.dataframe(df_n, use_container_width=True)
        if HAS_REPORTLAB:
            st.download_button("📄 Descargar Nómina PDF", data=generar_pdf_nomina(filas), file_name="nomina_produccion.pdf", mime="application/pdf")


elif modulo_activo == "💼 BASA Office 365 Suite":
    st.title("💼 BASA Office 365 Suite")
    with st.form("form_doc"):
        tit = st.text_input("Título del Documento")
        cont = st.text_area("Contenido", height=180)
        if st.form_submit_button("💾 Guardar Documento", type="primary") and tit and cont:
            with get_db() as conn:
                conn.execute("INSERT INTO office_docs (titulo, tipo, contenido, autor, actualizado_en) VALUES (?, ?, ?, ?, ?)", (tit, "Corporativo", cont, cliente["nombre"], datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
            st.rerun()
    with get_db() as conn:
        for d in conn.execute("SELECT * FROM office_docs ORDER BY id DESC").fetchall():
            with st.expander(f"📄 {d['titulo']} ({d['actualizado_en']})"):
                st.markdown(d["contenido"])


elif modulo_activo == "🚀 Master IA & Inyector":
    st.title("🤖 Master IA & Inyector de Software")
    idea = st.text_area("Requerimiento técnico:")
    tipo_app = st.selectbox("Ecosistema", ["Facturación Electrónica DGII", "ERP Contable NIIF", "API Microservicio FastAPI"])
    if st.button("⚡ Generar Repositorio", type="primary") and idea.strip():
        code = f"# {idea[:40]}\n# Generado por {cliente['nombre']}\nprint('BASA Service Ready')\n"
        with get_db() as conn:
            conn.execute("INSERT INTO repositorios (titulo, descripcion, categoria, fecha, generado_por, codigo_base) VALUES (?, ?, ?, ?, ?, ?)", (idea[:40], idea, tipo_app, datetime.now().strftime("%Y-%m-%d %H:%M"), cliente["nombre"], code))
            conn.commit()
        st.code(code, language="python")


elif modulo_activo == "👤 Control SaaS & Tokens":
    st.title("👤 Control de Suscriptores y Tokens")
    with st.form("form_cli"):
        c1, c2 = st.columns(2)
        cid = c1.text_input("ID Cliente", value=f"C{random.randint(100,999)}")
        cnom = c1.text_input("Empresa / Cliente")
        ctel = c2.text_input("WhatsApp")
        cmail = c2.text_input("Correo")
        ctok = st.text_input("Token 6 dígitos", value=generar_token_unico(), max_chars=6)
        if st.form_submit_button("Emitir Licencia", type="primary") and cnom and cmail:
            with get_db() as conn:
                conn.execute("INSERT INTO clientes (id, nombre, telefono, email, password, fecha_registro, estado, rango, codigo_6_digitos) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (cid, cnom, ctel, cmail, "123456", date.today().strftime("%Y-%m-%d"), "ACTIVO", 1, ctok))
                conn.commit()
            registrar_auditoria(cliente["nombre"], "SaaS", "Alta cliente", f"{cnom} ({ctok})")
            st.success(f"✅ Licencia emitida: {ctok}")
            st.rerun()
    with get_db() as conn:
        for r in conn.execute("SELECT * FROM clientes ORDER BY id DESC").fetchall():
            st.write(f"👤 **{r['nombre']}** | Token: `{r['codigo_6_digitos']}` | Estado: **{r['estado']}**")

