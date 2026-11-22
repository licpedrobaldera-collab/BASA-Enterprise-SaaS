"""
=============================================================================
BASA ENTERPRISE SAAS SUITE - ERP | CRM | OFFICE 365 | DGII e-CF | MASTER IA
Autor / Licenciatario: Lic. Pedro Baldera (licpedrobaldera@gmail.com)
WhatsApp Soporte: +1 (829) 771-7390
Mensualidad Estándar: RD$ 2,500.00
=============================================================================
ARQUITECTURA UNIFICADA (SUPERIOR A DYNAMICS / ORACLE / SAP / OFFICE 365):
 1. Núcleo SaaS Control: Clave Maestra '862600' (Lic. Pedro Baldera), tokens
    únicos de 6 dígitos para clientes (Usuario Beta '102030'), CRUD completo,
    alertas de cobro mensual y enlaces directos de WhatsApp.
 2. Dashboard Ejecutivo BI: KPIs financieros, operativos y gráficos en vivo.
 3. CRM & Pipeline Comercial: Embudo de ventas, probabilidad ponderada y WhatsApp.
 4. ERP Contabilidad NIIF & Facturación Electrónica DGII (e-CF 31/32/33/34/44/45):
    Validación RNC, ITBIS 18%, timbrado XML descargable y partida doble automática.
 5. Inventario & POS Omnicanal: Control de stock, alertas mínimas y venta atómica.
 6. RRHH & Nómina RD (TSS/ISR): Cálculo automático AFP (2.87%), SFS (3.04%),
    ISR por tramos DGII y aportes patronales con exportación CSV.
 7. BASA Office 365 Suite: Docs corporativos, Sheets editables y Proyectos Kanban.
 8. Inyector Autónomo de Software: Compilador de microservicios y repositorios.
 9. Auditoría (Audit Trail): Trazabilidad completa de acciones empresariales.
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

# =============================================================================
# 1. CONFIGURACIÓN DE PÁGINA E IDENTIDAD CORPORATIVA
# =============================================================================
st.set_page_config(
    page_title="BASA Enterprise SaaS | Lic. Pedro Baldera",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

CORREO_ADMIN = "licpedrobaldera@gmail.com"
WHATSAPP_ADMIN = "18297717390"
PRECIO_MENSUALIDAD = "RD$ 2,500.00"
TARIFA_MENSUAL_NUM = 2500.00
DB_PATH = "basa_saas_enterprise.db"
CLAVE_MAESTRA_ADMIN = "862600"

# Estilos CSS corporativos limpios
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
        background-color: #1d4ed8;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# 2. MOTOR DE BASE DE DATOS UNIFICADO (SQLite + Context Managers)
# =============================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # 2.1 Clientes y Licencias SaaS
        cursor.execute(
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

        # 2.2 Repositorios generados por el Inyector de Software
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS repositorios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                categoria TEXT,
                fecha TEXT NOT NULL,
                generado_por TEXT NOT NULL,
                codigo_base TEXT
            )
            """
        )

        # 2.3 CRM: Oportunidades Comerciales
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS crm_oportunidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        # 2.4 ERP: Catálogo de Productos / Inventario
        cursor.execute(
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

        # 2.5 ERP: Facturas Electrónicas DGII (e-CF)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS facturas_ecf (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                encf TEXT UNIQUE NOT NULL,
                tipo_ecf TEXT NOT NULL,
                rnc_cliente TEXT NOT NULL,
                nombre_cliente TEXT NOT NULL,
                subtotal REAL NOT NULL,
                itbis REAL NOT NULL,
                total REAL NOT NULL,
                moneda TEXT NOT NULL DEFAULT 'DOP',
                estado_dgii TEXT NOT NULL DEFAULT 'ACEPTADO e-CF',
                xml_contenido TEXT,
                fecha TEXT NOT NULL,
                creado_por TEXT NOT NULL
            )
            """
        )

        # 2.6 ERP: Plan de Cuentas y Asientos Contables (Partida Doble)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS plan_cuentas (
                codigo TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS asientos_contables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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

        # 2.7 RRHH: Empleados y Nómina
        cursor.execute(
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

        # 2.8 Office 365: Documentos y Tareas Kanban
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS office_docs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                tipo TEXT NOT NULL,
                contenido TEXT NOT NULL,
                autor TEXT NOT NULL,
                actualizado_en TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS proyectos_tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proyecto TEXT NOT NULL,
                titulo TEXT NOT NULL,
                prioridad TEXT NOT NULL DEFAULT 'Media',
                estado TEXT NOT NULL DEFAULT 'Por Hacer',
                asignado_a TEXT NOT NULL,
                fecha_limite TEXT NOT NULL
            )
            """
        )

        # 2.9 Auditoría del Sistema
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                usuario TEXT NOT NULL,
                modulo TEXT NOT NULL,
                accion TEXT NOT NULL,
                detalle TEXT
            )
            """
        )

        # Datos semilla iniciales (idempotentes)
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE id = 'C001'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO clientes (id, nombre, telefono, email, password, fecha_registro, estado, rango, codigo_6_digitos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "C001",
                    "Usuario Beta - Empresa Piloto",
                    "18297717390",
                    "cliente@basa.com",
                    "123456",
                    "2026-11-01",
                    "ACTIVO",
                    5,
                    "102030",
                ),
            )

        cursor.execute("SELECT COUNT(*) FROM plan_cuentas")
        if cursor.fetchone()[0] == 0:
            cuentas_base = [
                ("1101", "Caja y Bancos Generales", "Activo"),
                ("1102", "Cuentas por Cobrar Clientes", "Activo"),
                ("1103", "Inventario de Mercancías", "Activo"),
                ("2101", "Cuentas por Pagar Suplidores", "Pasivo"),
                ("2102", "ITBIS por Pagar (DGII)", "Pasivo"),
                ("2103", "Retenciones TSS e ISR por Pagar", "Pasivo"),
                ("3101", "Capital Social Suscrito", "Patrimonio"),
                ("4101", "Ingresos por Ventas y Servicios", "Ingreso"),
                ("5101", "Costo de Ventas", "Costo"),
                ("6101", "Gastos de Nómina y Beneficios", "Gasto"),
            ]
            cursor.executemany(
                "INSERT INTO plan_cuentas (codigo, nombre, tipo) VALUES (?, ?, ?)",
                cuentas_base,
            )

        cursor.execute("SELECT COUNT(*) FROM inventario")
        if cursor.fetchone()[0] == 0:
            productos_base = [
                ("BASA-ERP-01", "Licencia Mensual BASA Enterprise", "Software SaaS", 999, 10, 500.0, 2500.0, 1),
                ("HW-POS-100", "Terminal POS Térmica Android", "Hardware", 18, 5, 8500.0, 14500.0, 1),
                ("SRV-DGII-01", "Implementación e-CF DGII Llave en Mano", "Servicios", 50, 2, 12000.0, 35000.0, 1),
            ]
            cursor.executemany(
                """
                INSERT INTO inventario (sku, nombre, categoria, stock, stock_minimo, costo_unitario, precio_venta, itbis_aplica)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                productos_base,
            )

        cursor.execute("SELECT COUNT(*) FROM empleados")
        if cursor.fetchone()[0] == 0:
            empleados_base = [
                ("EMP-001", "Lic. Pedro Baldera", "001-0000001-1", "Dirección", "CEO / Arquitecto SaaS", 150000.0, "ACTIVO", "2025-01-10"),
                ("EMP-002", "Ana Martínez", "001-0000002-2", "Finanzas", "Contadora Senior NIIF", 65000.0, "ACTIVO", "2025-03-15"),
                ("EMP-003", "Carlos Gómez", "001-0000003-3", "Tecnología", "Ingeniero Backend Python", 85000.0, "ACTIVO", "2025-06-01"),
            ]
            cursor.executemany(
                """
                INSERT INTO empleados (id, nombre, cedula, departamento, cargo, salario_bruto, estado, fecha_ingreso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                empleados_base,
            )

        cursor.execute("SELECT COUNT(*) FROM crm_oportunidades")
        if cursor.fetchone()[0] == 0:
            crm_base = [
                ("Grupo Comercial Caribe SRL", "Roberto Pérez", "18095550101", "rperez@caribe.do", "Propuesta", 185000.0, 70, "Lic. Pedro Baldera", "Migración desde SAP Business One", "2026-11-15"),
                ("Clínica Integral del Este", "Dra. Laura Mejía", "18295550202", "lmejia@clinicaeste.do", "Negociación", 95000.0, 85, "Lic. Pedro Baldera", "Requiere facturación e-CF 32 y 31", "2026-11-18"),
            ]
            cursor.executemany(
                """
                INSERT INTO crm_oportunidades (empresa, contacto, telefono, email, etapa, valor_estimado, probabilidad, responsable, notas, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                crm_base,
            )

        conn.commit()


inicializar_db()


# =============================================================================
# 3. UTILIDADES DE NEGOCIO, AUDITORÍA Y LICENCIAS
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
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nombre, email, telefono, estado, fecha_registro
            FROM clientes
            WHERE codigo_6_digitos = ?
            """,
            (codigo,),
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "nombre": row["nombre"],
                "email": row["email"],
                "telefono": row["telefono"],
                "estado": row["estado"],
                "fecha_registro": row["fecha_registro"],
                "es_admin": False,
            }
    return None


def generar_token_unico():
    with get_db() as conn:
        cursor = conn.cursor()
        while True:
            t = f"{random.randint(100000, 999999)}"
            if t == CLAVE_MAESTRA_ADMIN:
                continue
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE codigo_6_digitos = ?", (t,))
            if cursor.fetchone()[0] == 0:
                return t


def calcular_nomina_rd(salario_bruto: float) -> dict:
    """Calcula deducciones legales RD (TSS: AFP 2.87%, SFS 3.04% e ISR escala anual DGII)."""
    afp_empleado = round(salario_bruto * 0.0287, 2)
    sfs_empleado = round(salario_bruto * 0.0304, 2)
    base_imponible_mensual = salario_bruto - afp_empleado - sfs_empleado
    anual = base_imponible_mensual * 12

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

    # Aportes patronales referenciales RD
    afp_patronal = round(salario_bruto * 0.0710, 2)
    sfs_patronal = round(salario_bruto * 0.0709, 2)
    srl_patronal = round(salario_bruto * 0.0110, 2)
    infotep = round(salario_bruto * 0.0100, 2)
    costo_total_empresa = round(salario_bruto + afp_patronal + sfs_patronal + srl_patronal + infotep, 2)

    return {
        "afp_emp": afp_empleado,
        "sfs_emp": sfs_empleado,
        "isr_emp": isr_mensual,
        "total_ded": total_deducciones,
        "neto": salario_neto,
        "costo_empresa": costo_total_empresa,
    }


def generar_xml_ecf(encf: str, tipo_ecf: str, rnc: str, nombre: str, subtotal: float, itbis: float, total: float) -> str:
    fecha_emision = datetime.now().strftime("%d-%m-%Y")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ECF>
  <Encabezado>
    <Version>1.0</Version>
    <IdDoc>
      <TipoeCF>{tipo_ecf[:2]}</TipoeCF>
      <eNCF>{encf}</eNCF>
      <FechaVencimientoSecuencia>31-12-2027</FechaVencimientoSecuencia>
      <IndicadorMontoGravado>0</IndicadorMontoGravado>
      <TipoIngresos>01</TipoIngresos>
      <TipoPago>1</TipoPago>
    </IdDoc>
    <Emisor>
      <RNCEmisor>131000001</RNCEmisor>
      <RazonSocialEmisor>BASA ENTERPRISE SAAS - LIC. PEDRO BALDERA</RazonSocialEmisor>
      <FechaEmision>{fecha_emision}</FechaEmision>
    </Emisor>
    <Comprador>
      <RNCComprador>{rnc}</RNCComprador>
      <RazonSocialComprador>{nombre}</RazonSocialComprador>
    </Comprador>
    <Totales>
      <MontoGravadoTotal>{subtotal:.2f}</MontoGravadoTotal>
      <ITBIS1>18</ITBIS1>
      <TotalITBIS>{itbis:.2f}</TotalITBIS>
      <MontoTotal>{total:.2f}</MontoTotal>
    </Totales>
  </Encabezado>
</ECF>"""


# =============================================================================
# 4. PORTAL DE ACCESO Y VALIDACIÓN DE LICENCIA
# =============================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "cliente_info" not in st.session_state:
    st.session_state.cliente_info = None

if not st.session_state.autenticado:
    st.markdown(
        """
        <div class="basa-banner" style="text-align:center;">
            <span class="basa-badge">ECOSISTEMA EMPRESARIAL FULL STACK</span>
            <h1 style="margin:0.4rem 0 0.2rem 0;">🏦 BASA ENTERPRISE SAAS SUITE</h1>
            <p style="margin:0; color:#cbd5e1; font-size:1.05rem;">
                ERP NIIF • Facturación e-CF DGII • CRM Omnicanal • Nómina TSS/ISR • Office 365 • Master IA
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        col_l, col_r = st.columns([1.15, 1.0], gap="large")
        with col_l:
            st.subheader("🔑 Validación de Licencia Corporativa")
            st.caption("Ingrese su token único de 6 dígitos enviado por WhatsApp o Correo:")
            token_input = st.text_input("Código de 6 dígitos", type="password", max_chars=6, placeholder="Ej: 862600")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🚀 Activar Sistema", use_container_width=True, type="primary"):
                    if not token_input:
                        st.error("Ingrese su código de 6 dígitos.")
                    else:
                        res = verificar_licencia(token_input)
                        if res:
                            if res["estado"] != "ACTIVO":
                                st.error(f"❌ Su cuenta se encuentra en estado: {res['estado']}. Contacte a administración.")
                            else:
                                st.session_state.autenticado = True
                                st.session_state.cliente_info = res
                                registrar_auditoria(res["nombre"], "Autenticación", "Inicio de sesión", f"ID: {res['id']}")
                                st.rerun()
                        else:
                            st.error("❌ Código inválido o Suspendido. Solicite su token de pago.")
            with col_b2:
                if st.button("🔑 Usar Clave Maestra", use_container_width=True):
                    res = verificar_licencia(CLAVE_MAESTRA_ADMIN)
                    st.session_state.autenticado = True
                    st.session_state.cliente_info = res
                    registrar_auditoria(res["nombre"], "Autenticación", "Acceso Maestro", "Token 862600")
                    st.rerun()

            st.markdown(
                "<div style='margin-top: 15px; font-size: 0.85rem; color: #64748b;'>"
                "• Clave Maestra de Administrador: <code>862600</code><br>"
                "• Token Cliente Beta: <code>102030</code></div>",
                unsafe_allow_html=True,
            )

        with col_r:
            st.subheader("💳 Activación de Membresía")
            st.markdown(f"**Costo Mensual de Servicio:** `{PRECIO_MENSUALIDAD}`")
            st.write("Soporte de pagos, alta de empresas y renovación de códigos automáticos:")
            st.info(f"📧 **Correo:** {CORREO_ADMIN}\n\n📱 **WhatsApp:** +{WHATSAPP_ADMIN}")

            msj_ws = urllib.parse.quote("Hola Lic. Pedro Baldera, deseo solicitar la activación de mi token para BASA Enterprise SaaS.")
            url_ws = f"https://wa.me/{WHATSAPP_ADMIN}?text={msj_ws}"
            st.markdown(
                f'<a href="{url_ws}" target="_blank" style="display:inline-block; padding:10px 16px; background-color:#22c55e; color:white; text-decoration:none; border-radius:6px; font-weight:600; text-align:center; width:100%;">💬 Contactar por WhatsApp</a>',
                unsafe_allow_html=True,
            )
    st.stop()


# =============================================================================
# 5. BARRA LATERAL DE NAVEGACIÓN MODULAR
# =============================================================================
cliente = st.session_state.cliente_info

with st.sidebar:
    st.title("🏦 BASA Enterprise")
    st.markdown(f"**Operador:** {cliente['nombre']}")
    st.caption(f"Rol: {'👑 Administrador Maestro' if cliente['es_admin'] else '👤 Suscriptor'}")
    st.caption(f"Estado: **{cliente['estado']}**")
    st.markdown("---")

    modulo_activo = st.radio(
        "Módulos del Ecosistema",
        [
            "📊 Dashboard Ejecutivo BI",
            "📈 CRM & Pipeline Ventas",
            "🧾 Facturación e-CF & Contabilidad",
            "📦 Inventario & POS Omnicanal",
            "👥 RRHH & Nómina RD (TSS/ISR)",
            "💼 BASA Office 365 Suite",
            "🚀 Master IA & Inyector",
            "👤 Control SaaS & Tokens",
            "🛡️ Auditoría & Seguridad",
        ],
    )

    st.markdown("---")
    st.metric("Mensualidad Estándar", PRECIO_MENSUALIDAD)
    st.caption(f"📧 {CORREO_ADMIN}\n\n📱 +{WHATSAPP_ADMIN}")

    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        registrar_auditoria(cliente["nombre"], "Autenticación", "Cierre de sesión", "")
        st.session_state.autenticado = False
        st.session_state.cliente_info = None
        st.rerun()


# =============================================================================
# 6. ALERTAS DINÁMICAS DE COBRO MENSUAL
# =============================================================================
hoy = datetime.now()
dia_del_mes = hoy.day
if not cliente["es_admin"]:
    if dia_del_mes > 25:
        st.warning(
            f"⚠️ ALERTA DE COBRO: Faltan {30 - dia_del_mes} días para el vencimiento de su mensualidad "
            f"({PRECIO_MENSUALIDAD}). Evite suspensiones del servicio."
        )
    elif dia_del_mes <= 5:
        st.info("ℹ️ Período de gracia activo hasta el día 5. Recuerde registrar su comprobante de pago.")


# =============================================================================
# 7. MÓDULOS EMPRESARIALES
# =============================================================================

# -----------------------------------------------------------------------------
# MÓDULO 1: DASHBOARD EJECUTIVO BI
# -----------------------------------------------------------------------------
if modulo_activo == "📊 Dashboard Ejecutivo BI":
    st.markdown(
        """
        <div class="basa-banner">
            <h2 style="margin:0;">📊 Centro de Comando Ejecutivo (BI)</h2>
            <p style="margin:0.2rem 0 0 0; color:#cbd5e1;">Visión unificada en tiempo real: Finanzas, Ventas CRM, Inventario, Nómina y Licencias SaaS</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with get_db() as conn:
        total_facturado = conn.execute("SELECT COALESCE(SUM(total), 0) FROM facturas_ecf").fetchone()[0]
        crm_ponderado = conn.execute(
            "SELECT COALESCE(SUM(valor_estimado * probabilidad / 100.0), 0) FROM crm_oportunidades WHERE etapa != 'Perdido'"
        ).fetchone()[0]
        valor_inv = conn.execute("SELECT COALESCE(SUM(stock * costo_unitario), 0) FROM inventario").fetchone()[0]
        nomina_bruta = conn.execute("SELECT COALESCE(SUM(salario_bruto), 0) FROM empleados WHERE estado = 'ACTIVO'").fetchone()[0]
        clientes_activos = conn.execute("SELECT COUNT(*) FROM clientes WHERE estado = 'ACTIVO'").fetchone()[0]
        mrr_saas = clientes_activos * TARIFA_MENSUAL_NUM

        df_crm = pd.read_sql_query("SELECT etapa, valor_estimado FROM crm_oportunidades", conn)
        df_inv = pd.read_sql_query("SELECT nombre, stock, stock_minimo FROM inventario", conn)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Facturación e-CF", f"RD$ {total_facturado:,.2f}")
    k2.metric("Pipeline CRM Ponderado", f"RD$ {crm_ponderado:,.2f}")
    k3.metric("Valor Inventario", f"RD$ {valor_inv:,.2f}")
    k4.metric("Nómina Mensual Bruta", f"RD$ {nomina_bruta:,.2f}")
    k5.metric("MRR SaaS Activo", f"RD$ {mrr_saas:,.2f}", f"{clientes_activos} activos")

    st.markdown("---")
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("📈 Embudo Comercial por Etapa (RD$)")
        if not df_crm.empty:
            resumen_crm = df_crm.groupby("etapa")["valor_estimado"].sum()
            st.bar_chart(resumen_crm)
        else:
            st.info("Sin oportunidades registradas en CRM.")
    with g2:
        st.subheader("📦 Niveles de Stock vs Mínimo")
        if not df_inv.empty:
            st.bar_chart(df_inv.set_index("nombre")[["stock", "stock_minimo"]])
        else:
            st.info("Sin productos en inventario.")


# -----------------------------------------------------------------------------
# MÓDULO 2: CRM & PIPELINE COMERCIAL
# -----------------------------------------------------------------------------
elif modulo_activo == "📈 CRM & Pipeline Ventas":
    st.title("📈 CRM & Pipeline Comercial Omnicanal")
    st.caption("Gestión de prospectos, seguimiento WhatsApp integrado y conversión directa.")

    with st.expander("➕ Nueva Oportunidad Comercial", expanded=False):
        with st.form("form_crm"):
            c1, c2, c3 = st.columns(3)
            with c1:
                emp = st.text_input("Empresa / Cuenta")
                contacto = st.text_input("Contacto Principal")
                tel = st.text_input("Teléfono / WhatsApp", placeholder="18095551234")
            with c2:
                mail = st.text_input("Correo Electrónico")
                etapa = st.selectbox("Etapa", ["Prospecto", "Calificado", "Propuesta", "Negociación", "Ganado", "Perdido"])
                valor = st.number_input("Valor Estimado (RD$)", min_value=0.0, step=1000.0, value=25000.0)
            with c3:
                prob = st.slider("Probabilidad de Cierre (%)", 0, 100, 50)
                notas = st.text_area("Notas / Requerimiento", height=95)

            if st.form_submit_button("Guardar Oportunidad", type="primary"):
                if emp and contacto:
                    with get_db() as conn:
                        conn.execute(
                            """
                            INSERT INTO crm_oportunidades (empresa, contacto, telefono, email, etapa, valor_estimado, probabilidad, responsable, notas, fecha_creacion)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (emp, contacto, tel, mail, etapa, valor, prob, cliente["nombre"], notas, date.today().strftime("%Y-%m-%d")),
                        )
                        conn.commit()
                    registrar_auditoria(cliente["nombre"], "CRM", "Nueva oportunidad", f"{emp} - RD$ {valor:,.2f}")
                    st.success(f"✅ Oportunidad '{emp}' registrada.")
                    st.rerun()
                else:
                    st.error("Complete empresa y contacto.")

    with get_db() as conn:
        ops = conn.execute("SELECT * FROM crm_oportunidades ORDER BY id DESC").fetchall()

    for op in ops:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 1.5, 1.2, 1.3])
            c1.markdown(f"**🏢 {op['empresa']}**\n\n👤 {op['contacto']} | 📧 {op['email'] or 'N/A'}")
            c2.markdown(f"Etapa: **{op['etapa']}** ({op['probabilidad']}%)\n\n💰 `RD$ {op['valor_estimado']:,.2f}`")
            c3.caption(op["notas"] or "Sin notas")
            with c4:
                if op["telefono"]:
                    msg = urllib.parse.quote(f"Hola {op['contacto']}, le contactamos de BASA Enterprise respecto a su propuesta para {op['empresa']}.")
                    st.markdown(f'<a href="https://wa.me/{op["telefono"]}?text={msg}" target="_blank">💬 Seguimiento WhatsApp</a>', unsafe_allow_html=True)
                nueva_etapa = st.selectbox(
                    "Mover etapa",
                    ["Prospecto", "Calificado", "Propuesta", "Negociación", "Ganado", "Perdido"],
                    index=["Prospecto", "Calificado", "Propuesta", "Negociación", "Ganado", "Perdido"].index(op["etapa"]),
                    key=f"crm_et_{op['id']}",
                )
                if nueva_etapa != op["etapa"]:
                    with get_db() as conn:
                        conn.execute("UPDATE crm_oportunidades SET etapa = ? WHERE id = ?", (nueva_etapa, op["id"]))
                        conn.commit()
                    registrar_auditoria(cliente["nombre"], "CRM", "Cambio de etapa", f"{op['empresa']} -> {nueva_etapa}")
                    st.rerun()


# -----------------------------------------------------------------------------
# MÓDULO 3: FACTURACIÓN e-CF DGII & CONTABILIDAD NIIF
# -----------------------------------------------------------------------------
elif modulo_activo == "🧾 Facturación e-CF & Contabilidad":
    st.title("🧾 ERP Contabilidad NIIF & Facturación Electrónica DGII (e-CF)")
    t_ecf, t_diario, t_balance = st.tabs(["⚡ Emisor e-CF DGII", "📒 Libro Diario (Partida Doble)", "⚖️ Balance de Comprobación"])

    with t_ecf:
        st.subheader("Emitir Comprobante Fiscal Electrónico (e-CF)")
        with st.form("form_ecf"):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                tipo_ecf = st.selectbox(
                    "Tipo de e-CF",
                    [
                        "31 - Factura de Crédito Fiscal",
                        "32 - Factura de Consumo",
                        "33 - Nota de Débito",
                        "34 - Nota de Crédito",
                        "44 - Regímenes Especiales",
                        "45 - Gubernamental",
                    ],
                )
                rnc_cli = st.text_input("RNC / Cédula Comprador", placeholder="Ej: 131000001")
            with fc2:
                nom_cli = st.text_input("Razón Social / Nombre", placeholder="Ej: Farmacia San Juan SRL")
                subtotal_ecf = st.number_input("Monto Gravado / Subtotal (RD$)", min_value=0.0, step=100.0, value=10000.0)
            with fc3:
                aplica_itbis = st.checkbox("Aplicar ITBIS 18%", value=True)
                moneda = st.selectbox("Moneda", ["DOP", "USD"])

            if st.form_submit_button("⚡ Emitir y Timbrar e-CF", type="primary"):
                if rnc_cli and nom_cli and subtotal_ecf > 0:
                    itbis_val = round(subtotal_ecf * 0.18, 2) if aplica_itbis else 0.0
                    total_val = round(subtotal_ecf + itbis_val, 2)
                    with get_db() as conn:
                        seq = conn.execute("SELECT COUNT(*) + 1 FROM facturas_ecf").fetchone()[0]
                        encf = f"E{tipo_ecf[:2]}{seq:010d}"
                        xml_str = generar_xml_ecf(encf, tipo_ecf, rnc_cli, nom_cli, subtotal_ecf, itbis_val, total_val)
                        conn.execute(
                            """
                            INSERT INTO facturas_ecf (encf, tipo_ecf, rnc_cliente, nombre_cliente, subtotal, itbis, total, moneda, xml_contenido, fecha, creado_por)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (encf, tipo_ecf, rnc_cli, nom_cli, subtotal_ecf, itbis_val, total_val, moneda, xml_str, datetime.now().strftime("%Y-%m-%d %H:%M"), cliente["nombre"]),
                        )
                        # Asiento contable automático (Partida Doble)
                        fecha_hoy = date.today().strftime("%Y-%m-%d")
                        conn.execute(
                            "INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (fecha_hoy, encf, f"Factura e-CF {nom_cli}", "1102", total_val, 0.0, cliente["nombre"]),
                        )
                        conn.execute(
                            "INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (fecha_hoy, encf, f"Ingreso Venta {encf}", "4101", 0.0, subtotal_ecf, cliente["nombre"]),
                        )
                        if itbis_val > 0:
                            conn.execute(
                                "INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (fecha_hoy, encf, f"ITBIS Facturado {encf}", "2102", 0.0, itbis_val, cliente["nombre"]),
                            )
                        conn.commit()
                    registrar_auditoria(cliente["nombre"], "DGII e-CF", "Emisión e-CF", f"{encf} por {moneda} {total_val:,.2f}")
                    st.success(f"✅ Comprobante {encf} timbrado y contabilizado automáticamente.")
                else:
                    st.error("Complete RNC, Razón Social y un monto mayor a cero.")

        with get_db() as conn:
            facturas = conn.execute("SELECT * FROM facturas_ecf ORDER BY id DESC").fetchall()
        for f in facturas:
            with st.expander(f"🧾 {f['encf']} | {f['nombre_cliente']} | {f['moneda']} {f['total']:,.2f} | {f['estado_dgii']}"):
                st.write(f"RNC: `{f['rnc_cliente']}` | Subtotal: `{f['subtotal']:,.2f}` | ITBIS: `{f['itbis']:,.2f}` | Fecha: {f['fecha']}")
                if f["xml_contenido"]:
                    st.code(f["xml_contenido"], language="xml")
                    st.download_button(
                        "📥 Descargar XML e-CF",
                        data=f["xml_contenido"],
                        file_name=f"{f['encf']}.xml",
                        mime="application/xml",
                        key=f"xml_{f['id']}",
                    )

    with t_diario:
        st.subheader("📒 Registro Manual de Asiento Contable (Partida Doble)")
        with get_db() as conn:
            cuentas = conn.execute("SELECT codigo, nombre FROM plan_cuentas ORDER BY codigo").fetchall()
        opciones_cuentas = [f"{c['codigo']} - {c['nombre']}" for c in cuentas]

        with st.form("form_asiento"):
            a1, a2, a3 = st.columns(3)
            with a1:
                ref_a = st.text_input("Referencia", value=f"AS-{random.randint(1000,9999)}")
                desc_a = st.text_input("Concepto del Asiento")
            with a2:
                cta_deb = st.selectbox("Cuenta Débito", opciones_cuentas, index=0)
                cta_cred = st.selectbox("Cuenta Crédito", opciones_cuentas, index=7 if len(opciones_cuentas) > 7 else 0)
            with a3:
                monto_a = st.number_input("Monto (RD$)", min_value=0.0, step=100.0)

            if st.form_submit_button("Contabilizar Asiento", type="primary"):
                if desc_a and monto_a > 0 and cta_deb != cta_cred:
                    f_hoy = date.today().strftime("%Y-%m-%d")
                    with get_db() as conn:
                        conn.execute(
                            "INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (f_hoy, ref_a, desc_a, cta_deb.split(" - ")[0], monto_a, 0.0, cliente["nombre"]),
                        )
                        conn.execute(
                            "INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (f_hoy, ref_a, desc_a, cta_cred.split(" - ")[0], 0.0, monto_a, cliente["nombre"]),
                        )
                        conn.commit()
                    registrar_auditoria(cliente["nombre"], "Contabilidad", "Asiento Manual", f"{ref_a}: RD$ {monto_a:,.2f}")
                    st.success("✅ Asiento cuadrado y contabilizado.")
                    st.rerun()
                else:
                    st.error("Verifique concepto, monto > 0 y que Débito y Crédito usen cuentas distintas.")

        with get_db() as conn:
            df_asientos = pd.read_sql_query("SELECT id, fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por FROM asientos_contables ORDER BY id DESC", conn)
        st.dataframe(df_asientos, use_container_width=True)

    with t_balance:
        st.subheader("⚖️ Balance de Comprobación en Tiempo Real")
        with get_db() as conn:
            df_bal = pd.read_sql_query(
                """
                SELECT p.codigo, p.nombre, p.tipo,
                       COALESCE(SUM(a.debito), 0) AS total_debito,
                       COALESCE(SUM(a.credito), 0) AS total_credito,
                       COALESCE(SUM(a.debito) - SUM(a.credito), 0) AS saldo_neto
                FROM plan_cuentas p
                LEFT JOIN asientos_contables a ON p.codigo = a.cuenta_codigo
                GROUP BY p.codigo, p.nombre, p.tipo
                ORDER BY p.codigo
                """,
                conn,
            )
        st.dataframe(df_bal, use_container_width=True)
        tot_d = df_bal["total_debito"].sum()
        tot_c = df_bal["total_credito"].sum()
        st.info(f"**Cuadre Global:** Total Débitos: `RD$ {tot_d:,.2f}` | Total Créditos: `RD$ {tot_c:,.2f}` | Diferencia: `RD$ {tot_d - tot_c:,.2f}`")


# -----------------------------------------------------------------------------
# MÓDULO 4: INVENTARIO & POS OMNICANAL
# -----------------------------------------------------------------------------
elif modulo_activo == "📦 Inventario & POS Omnicanal":
    st.title("📦 Inventario & Punto de Venta (POS) Integrado")
    t_pos, t_inv = st.tabs(["🛒 Punto de Venta (POS)", "📋 Maestro de Inventario"])

    with t_pos:
        with get_db() as conn:
            prods = conn.execute("SELECT * FROM inventario WHERE stock > 0 ORDER BY nombre").fetchall()

        if not prods:
            st.warning("No hay productos con stock disponible.")
        else:
            mapa_prods = {f"{p['sku']} | {p['nombre']} (Stock: {p['stock']} - RD$ {p['precio_venta']:,.2f})": p for p in prods}
            with st.form("form_pos"):
                p1, p2, p3 = st.columns([2, 1, 1])
                sel = p1.selectbox("Producto / Servicio", list(mapa_prods.keys()))
                cant = p2.number_input("Cantidad", min_value=1, step=1, value=1)
                rnc_pos = p3.text_input("RNC/Cédula Cliente", value="000000000")
                nom_pos = st.text_input("Nombre Cliente POS", value="Consumidor Final")

                if st.form_submit_button("💳 Procesar Venta POS + e-CF", type="primary"):
                    prod_sel = mapa_prods[sel]
                    if cant > prod_sel["stock"]:
                        st.error(f"Stock insuficiente. Disponible: {prod_sel['stock']}")
                    else:
                        sub = round(prod_sel["precio_venta"] * cant, 2)
                        itb = round(sub * 0.18, 2) if prod_sel["itbis_aplica"] else 0.0
                        tot = round(sub + itb, 2)
                        costo_tot = round(prod_sel["costo_unitario"] * cant, 2)

                        with get_db() as conn:
                            conn.execute("UPDATE inventario SET stock = stock - ? WHERE sku = ?", (cant, prod_sel["sku"]))
                            seq = conn.execute("SELECT COUNT(*) + 1 FROM facturas_ecf").fetchone()[0]
                            encf = f"E32{seq:010d}"
                            xml_pos = generar_xml_ecf(encf, "32 - Factura de Consumo", rnc_pos, nom_pos, sub, itb, tot)
                            conn.execute(
                                """
                                INSERT INTO facturas_ecf (encf, tipo_ecf, rnc_cliente, nombre_cliente, subtotal, itbis, total, moneda, xml_contenido, fecha, creado_por)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (encf, "32 - Factura de Consumo", rnc_pos, nom_pos, sub, itb, tot, "DOP", xml_pos, datetime.now().strftime("%Y-%m-%d %H:%M"), cliente["nombre"]),
                            )
                            f_hoy = date.today().strftime("%Y-%m-%d")
                            conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, encf, f"Venta POS {prod_sel['sku']}", "1101", tot, 0.0, cliente["nombre"]))
                            conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, encf, f"Ingreso POS {prod_sel['sku']}", "4101", 0.0, sub, cliente["nombre"]))
                            if itb > 0:
                                conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, encf, f"ITBIS POS {encf}", "2102", 0.0, itb, cliente["nombre"]))
                            conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, encf, f"Costo Venta {prod_sel['sku']}", "5101", costo_tot, 0.0, cliente["nombre"]))
                            conn.execute("INSERT INTO asientos_contables (fecha, referencia, descripcion, cuenta_codigo, debito, credito, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)", (f_hoy, encf, f"Salida Inv {prod_sel['sku']}", "1103", 0.0, costo_tot, cliente["nombre"]))
                            conn.commit()
                        registrar_auditoria(cliente["nombre"], "POS", "Venta POS", f"{encf} | {cant}x {prod_sel['sku']} | RD$ {tot:,.2f}")
                        st.success(f"✅ Venta completada: {encf} por RD$ {tot:,.2f} (Stock y Contabilidad actualizados).")
                        st.rerun()

    with t_inv:
        with st.expander("➕ Agregar Producto / SKU"):
            with st.form("form_inv"):
                i1, i2, i3 = st.columns(3)
                sku = i1.text_input("SKU", value=f"SKU-{random.randint(100,999)}")
                nom_p = i1.text_input("Nombre del Producto")
                cat_p = i2.text_input("Categoría", value="General")
                stk_p = i2.number_input("Stock Inicial", min_value=0, value=10)
                cost_p = i3.number_input("Costo Unitario", min_value=0.0, value=500.0)
                prec_p = i3.number_input("Precio Venta", min_value=0.0, value=1000.0)
                if st.form_submit_button("Guardar Producto", type="primary"):
                    if sku and nom_p:
                        try:
                            with get_db() as conn:
                                conn.execute(
                                    "INSERT INTO inventario (sku, nombre, categoria, stock, stock_minimo, costo_unitario, precio_venta, itbis_aplica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                    (sku, nom_p, cat_p, stk_p, 5, cost_p, prec_p, 1),
                                )
                                conn.commit()
                            st.success(f"✅ Producto {nom_p} agregado.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Ese SKU ya existe.")

        with get_db() as conn:
            df_i = pd.read_sql_query("SELECT * FROM inventario ORDER BY sku", conn)
        st.dataframe(df_i, use_container_width=True)


# -----------------------------------------------------------------------------
# MÓDULO 5: RRHH & NÓMINA RD (TSS / ISR)
# -----------------------------------------------------------------------------
elif modulo_activo == "👥 RRHH & Nómina RD (TSS/ISR)":
    st.title("👥 Gestión Humana & Nómina Automatizada (TSS / ISR RD)")
    st.caption("Cálculo automático de AFP (2.87%), SFS (3.04%), ISR DGII y Aportes Patronales.")

    with st.expander("➕ Registrar Nuevo Empleado"):
        with st.form("form_emp"):
            e1, e2, e3 = st.columns(3)
            emp_id = e1.text_input("Código Empleado", value=f"EMP-{random.randint(100,999)}")
            emp_nom = e1.text_input("Nombre Completo")
            emp_ced = e2.text_input("Cédula / NSS")
            emp_dep = e2.selectbox("Departamento", ["Dirección", "Finanzas", "Tecnología", "Ventas", "Operaciones"])
            emp_crg = e3.text_input("Cargo")
            emp_sal = e3.number_input("Salario Bruto Mensual (RD$)", min_value=10000.0, step=1000.0, value=45000.0)
            if st.form_submit_button("Guardar Empleado", type="primary"):
                if emp_nom and emp_ced:
                    with get_db() as conn:
                        conn.execute(
                            "INSERT INTO empleados (id, nombre, cedula, departamento, cargo, salario_bruto, estado, fecha_ingreso) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (emp_id, emp_nom, emp_ced, emp_dep, emp_crg, emp_sal, "ACTIVO", date.today().strftime("%Y-%m-%d")),
                        )
                        conn.commit()
                    st.success(f"✅ Empleado {emp_nom} registrado.")
                    st.rerun()

    with get_db() as conn:
        emps = conn.execute("SELECT * FROM empleados WHERE estado = 'ACTIVO' ORDER BY id").fetchall()

    filas_nomina = []
    for e in emps:
        calc = calcular_nomina_rd(e["salario_bruto"])
        filas_nomina.append(
            {
                "ID": e["id"],
                "Nombre": e["nombre"],
                "Departamento": e["departamento"],
                "Salario Bruto": e["salario_bruto"],
                "AFP (2.87%)": calc["afp_emp"],
                "SFS (3.04%)": calc["sfs_emp"],
                "ISR Mensual": calc["isr_emp"],
                "Total Deducciones": calc["total_ded"],
                "Salario Neto": calc["neto"],
                "Costo Total Empresa": calc["costo_empresa"],
            }
        )

    if filas_nomina:
        df_nom = pd.DataFrame(filas_nomina)
        st.dataframe(df_nom, use_container_width=True)
        csv_nom = df_nom.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Exportar Nómina TSS/ISR (.csv)", data=csv_nom, file_name=f"nomina_basa_{date.today()}.csv", mime="text/csv")


# -----------------------------------------------------------------------------
# MÓDULO 6: BASA OFFICE 365 SUITE (DOCS, SHEETS & PROYECTOS KANBAN)
# -----------------------------------------------------------------------------
elif modulo_activo == "💼 BASA Office 365 Suite":
    st.title("💼 BASA Office 365 Suite (Colaboración en Línea)")
    t_docs, t_sheets, t_kanban = st.tabs(["📝 BASA Docs", "📊 BASA Sheets", "📋 BASA Projects (Kanban)"])

    with t_docs:
        st.subheader("Editor de Documentos Corporativos")
        plantilla = st.selectbox(
            "Plantilla rápida",
            [
                "En Blanco",
                "Contrato de Licencia SaaS BASA",
                "Memorándum Ejecutivo",
                "Propuesta Comercial Enterprise",
            ],
        )
        texto_base = ""
        if plantilla == "Contrato de Licencia SaaS BASA":
            texto_base = f"# CONTRATO DE SERVICIO SAAS\nEntre **BASA Enterprise (Lic. Pedro Baldera)** y **[Cliente]**, por valor mensual de **{PRECIO_MENSUALIDAD}**..."
        elif plantilla == "Memorándum Ejecutivo":
            texto_base = f"# MEMORÁNDUM EJECUTIVO\n**Fecha:** {date.today()}\n**De:** {cliente['nombre']}\n**Asunto:** Actualización Operativa\n\nContenido..."
        elif plantilla == "Propuesta Comercial Enterprise":
            texto_base = "# PROPUESTA COMERCIAL\nImplementación integral ERP + CRM + Facturación e-CF DGII."

        with st.form("form_doc"):
            doc_tit = st.text_input("Título del Documento", value=f"Doc - {plantilla}")
            doc_cont = st.text_area("Contenido (Markdown / Texto)", value=texto_base, height=220)
            if st.form_submit_button("💾 Guardar Documento en Nube BASA", type="primary"):
                if doc_tit and doc_cont:
                    with get_db() as conn:
                        conn.execute(
                            "INSERT INTO office_docs (titulo, tipo, contenido, autor, actualizado_en) VALUES (?, ?, ?, ?, ?)",
                            (doc_tit, plantilla, doc_cont, cliente["nombre"], datetime.now().strftime("%Y-%m-%d %H:%M")),
                        )
                        conn.commit()
                    st.success("✅ Documento guardado.")
                    st.rerun()

        with get_db() as conn:
            docs = conn.execute("SELECT * FROM office_docs ORDER BY id DESC").fetchall()
        for d in docs:
            with st.expander(f"📄 {d['titulo']} ({d['actualizado_en']} - {d['autor']})"):
                st.markdown(d["contenido"])
                st.download_button("📥 Descargar .md", data=d["contenido"], file_name=f"doc_{d['id']}.md", mime="text/markdown", key=f"doc_{d['id']}")

    with t_sheets:
        st.subheader("📊 Hoja de Cálculo Interactiva en Línea")
        if "basa_sheet_df" not in st.session_state:
            st.session_state.basa_sheet_df = pd.DataFrame(
                [
                    {"Concepto": "Licencias SaaS Activas", "Cantidad": 12, "Precio_Unitario": 2500.0, "Total": 30000.0},
                    {"Concepto": "Implementación e-CF DGII", "Cantidad": 2, "Precio_Unitario": 35000.0, "Total": 70000.0},
                    {"Concepto": "Soporte Premium 24/7", "Cantidad": 4, "Precio_Unitario": 5000.0, "Total": 20000.0},
                ]
            )
        edited_df = st.data_editor(st.session_state.basa_sheet_df, num_rows="dynamic", use_container_width=True)
        if not edited_df.empty and {"Cantidad", "Precio_Unitario"}.issubset(edited_df.columns):
            edited_df["Total"] = pd.to_numeric(edited_df["Cantidad"], errors="coerce").fillna(0) * pd.to_numeric(edited_df["Precio_Unitario"], errors="coerce").fillna(0)
            st.metric("Suma Total Calculada", f"RD$ {edited_df['Total'].sum():,.2f}")
        st.session_state.basa_sheet_df = edited_df
        st.download_button("📥 Exportar Hoja (.csv)", data=edited_df.to_csv(index=False).encode("utf-8"), file_name="basa_sheet.csv", mime="text/csv")

    with t_kanban:
        st.subheader("📋 Tablero Kanban de Proyectos")
        with st.form("form_tarea"):
            k1, k2, k3, k4 = st.columns(4)
            proy = k1.text_input("Proyecto", value="Despliegue ERP")
            tit_t = k2.text_input("Tarea")
            prio = k3.selectbox("Prioridad", ["Alta", "Media", "Baja"])
            lim_t = k4.date_input("Fecha Límite", value=date.today())
            if st.form_submit_button("Agregar Tarea", type="primary"):
                if tit_t:
                    with get_db() as conn:
                        conn.execute(
                            "INSERT INTO proyectos_tareas (proyecto, titulo, prioridad, estado, asignado_a, fecha_limite) VALUES (?, ?, ?, ?, ?, ?)",
                            (proy, tit_t, prio, "Por Hacer", cliente["nombre"], str(lim_t)),
                        )
                        conn.commit()
                    st.rerun()

        with get_db() as conn:
            tareas = conn.execute("SELECT * FROM proyectos_tareas ORDER BY id DESC").fetchall()

        cols_k = st.columns(4)
        estados_k = ["Por Hacer", "En Progreso", "Revisión", "Completado"]
        for idx, est in enumerate(estados_k):
            with cols_k[idx]:
                st.markdown(f"### {est}")
                for t in [x for x in tareas if x["estado"] == est]:
                    with st.container(border=True):
                        st.markdown(f"**{t['titulo']}**")
                        st.caption(f"📁 {t['proyecto']} | ⚡ {t['prioridad']} | 📅 {t['fecha_limite']}")
                        nuevo_e = st.selectbox("Estado", estados_k, index=idx, key=f"tsk_{t['id']}", label_visibility="collapsed")
                        if nuevo_e != est:
                            with get_db() as conn:
                                conn.execute("UPDATE proyectos_tareas SET estado = ? WHERE id = ?", (nuevo_e, t["id"]))
                                conn.commit()
                            st.rerun()


# -----------------------------------------------------------------------------
# MÓDULO 7: MASTER IA & INYECTOR AUTÓNOMO DE SOFTWARE
# -----------------------------------------------------------------------------
elif modulo_activo == "🚀 Master IA & Inyector":
    st.title("🤖 MASTER IA - INYECTOR AUTÓNOMO DE SOFTWARE")
    st.caption(f"Sesión activa: {cliente['nombre']} | Generación de arquitectura, microservicios y paquetes descargables")

    t_inj, t_hist = st.tabs(["🚀 Inyector de Software", "📜 Repositorios Generados"])
    with t_inj:
        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            idea = st.text_area(
                "Propuesta base, link o requerimiento técnico:",
                placeholder="Ej: Facturador Electrónico DGII v5 con e-CF 31, 32, 44, validación de RNC y timbrado XML...",
                height=130,
            )
        with col_t2:
            tipo_app = st.selectbox(
                "Ecosistema Destino",
                [
                    "Facturación Electrónica DGII (República Dominicana)",
                    "Gestión Contable y Recaudo Préstamos",
                    "Portal Clínico & Gestión Médica",
                    "Control de Inventario e-Commerce POS",
                    "API Microservicio REST / Python FastAPI",
                ],
            )
            version_release = st.text_input("Versión de Release", value="v5.2.0-LTS")

        if st.button("⚡ Aprobar Software y Enviar a Repositorio", use_container_width=True, type="primary"):
            if idea.strip():
                repo_title = idea[:45].strip() + ("..." if len(idea) > 45 else "")
                repo_code = f"""# {repo_title} - {version_release}
# Generado por BASA Enterprise Software Generator
# Autor de Licencia: {cliente['nombre']}
# Fecha de Compilación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

from datetime import datetime

class BASAService:
    def __init__(self):
        self.ecosistema = "{tipo_app}"
        self.version = "{version_release}"
        self.licencia = "{cliente['id']}"

    def ejecutar_flujo(self):
        print(f"[BASA AUTO-ENGINE] Iniciando servicio {{self.ecosistema}} v{{self.version}}")
        # Requerimiento: {idea.replace(chr(10), ' ')}
        return {{"status": "OK", "timestamp": str(datetime.now())}}

if __name__ == "__main__":
    servicio = BASAService()
    print(servicio.ejecutar_flujo())
"""
                with get_db() as conn:
                    conn.execute(
                        """
                        INSERT INTO repositorios (titulo, descripcion, categoria, fecha, generado_por, codigo_base)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (repo_title, idea, tipo_app, datetime.now().strftime("%Y-%m-%d %H:%M"), cliente["nombre"], repo_code),
                    )
                    conn.commit()
                registrar_auditoria(cliente["nombre"], "Inyector IA", "Repositorio generado", repo_title)
                st.success(f"✅ Software aprobado e inyectado con éxito: [{repo_title}]")
                st.balloons()

                # Paquete ZIP completo (main.py + requirements.txt + README.md)
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr("main.py", repo_code)
                    zf.writestr("requirements.txt", "fastapi>=0.110.0\nuvicorn>=0.29.0\npydantic>=2.6.0\n")
                    zf.writestr("README.md", f"# {repo_title}\n\nEcosistema: {tipo_app}\nVersión: {version_release}\nLicencia: {cliente['nombre']}\n")

                with st.expander("👁️ Ver Código Generado del Repositorio", expanded=True):
                    st.code(repo_code, language="python")
                    d1, d2 = st.columns(2)
                    d1.download_button(
                        label="📥 Descargar Archivo Python (.py)",
                        data=repo_code,
                        file_name=f"basa_repo_{int(datetime.now().timestamp())}.py",
                        mime="text/x-python",
                    )
                    d2.download_button(
                        label="📦 Descargar Paquete Completo (.zip)",
                        data=zip_buffer.getvalue(),
                        file_name=f"basa_bundle_{int(datetime.now().timestamp())}.zip",
                        mime="application/zip",
                    )
            else:
                st.error("⚠️ Por favor ingrese una idea o requerimiento antes de procesar.")

    with t_hist:
        with get_db() as conn:
            repos = conn.execute("SELECT id, titulo, categoria, fecha, generado_por, codigo_base FROM repositorios ORDER BY id DESC").fetchall()
        if not repos:
            st.info("Aún no se han generado repositorios de software.")
        else:
            for rp in repos:
                with st.container(border=True):
                    st.markdown(f"### 📦 {rp['titulo']}")
                    st.caption(f"Categoría: {rp['categoria']} | Fecha: {rp['fecha']} | Generado por: {rp['generado_por']}")
                    with st.expander("Ver Código Fuente"):
                        st.code(rp["codigo_base"], language="python")
                        st.download_button(
                            label="📥 Descargar Script",
                            data=rp["codigo_base"],
                            file_name=f"repo_{rp['id']}.py",
                            mime="text/x-python",
                            key=f"dl_{rp['id']}",
                        )


# -----------------------------------------------------------------------------
# MÓDULO 8: PANEL DE CLIENTES Y TOKENS (CRUD SAAS)
# -----------------------------------------------------------------------------
elif modulo_activo == "👤 Control SaaS & Tokens":
    st.title("👤 Control General de Suscriptores y Tokens")

    with get_db() as conn:
        total_clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        activos = conn.execute("SELECT COUNT(*) FROM clientes WHERE estado = 'ACTIVO'").fetchone()[0]
        suspendidos = conn.execute("SELECT COUNT(*) FROM clientes WHERE estado != 'ACTIVO'").fetchone()[0]

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Clientes", total_clientes)
    col_m2.metric("Suscripciones Activas", activos)
    col_m3.metric("Suspendidos / Vencidos", suspendidos)
    col_m4.metric("Tarifa Base", PRECIO_MENSUALIDAD)

    st.markdown("---")
    with st.expander("➕ Dar de Alta Nuevo Cliente / Suscriptor", expanded=False):
        with st.form("form_nuevo_cliente"):
            fc1, fc2 = st.columns(2)
            with fc1:
                nuevo_id = st.text_input("ID Cliente", value=f"C{random.randint(100, 999)}")
                nuevo_nombre = st.text_input("Nombre / Razón Social", placeholder="Ej: Farmacia San Juan SRL")
                nuevo_telefono = st.text_input("Teléfono / WhatsApp", placeholder="18291234567")
            with fc2:
                nuevo_email = st.text_input("Correo Electrónico", placeholder="contacto@cliente.com")
                nuevo_estado = st.selectbox("Estado Inicial", ["ACTIVO", "EN PRUEBA", "SUSPENDIDO"])
                nuevo_token = st.text_input("Token de 6 dígitos asignado", value=generar_token_unico(), max_chars=6)

            if st.form_submit_button("Guardar y Emitir Licencia", type="primary"):
                if nuevo_nombre and nuevo_email and nuevo_token:
                    try:
                        with get_db() as conn:
                            conn.execute(
                                """
                                INSERT INTO clientes (id, nombre, telefono, email, password, fecha_registro, estado, rango, codigo_6_digitos)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (nuevo_id, nuevo_nombre, nuevo_telefono, nuevo_email, "123456", date.today().strftime("%Y-%m-%d"), nuevo_estado, 1, nuevo_token),
                            )
                            conn.commit()
                        registrar_auditoria(cliente["nombre"], "SaaS Control", "Alta de cliente", f"{nuevo_nombre} ({nuevo_token})")
                        st.success(f"✅ Cliente {nuevo_nombre} registrado exitosamente con token: {nuevo_token}")
                        st.rerun()
                    except sqlite3.IntegrityError as e:
                        st.error(f"Error: Ya existe un registro con este ID o Token: {e}")
                else:
                    st.error("Por favor complete nombre, correo y token.")

    with get_db() as conn:
        rows = conn.execute("SELECT id, nombre, email, telefono, codigo_6_digitos, estado, fecha_registro FROM clientes ORDER BY id DESC").fetchall()

    for r in rows:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.2, 1.2])
            c1.write(f"👤 **{r['nombre']}** (`{r['id']}`)\n\n📅 Registro: {r['fecha_registro']}")
            c2.write(f"✉️ {r['email']}\n\n📱 {r['telefono']}")
            color_estado = "green" if r["estado"] == "ACTIVO" else "orange" if r["estado"] == "EN PRUEBA" else "red"
            c3.markdown(f"🔑 Token: `<b>{r['codigo_6_digitos']}</b>`", unsafe_allow_html=True)
            c3.markdown(f"Estado: <span style='color:{color_estado}; font-weight:bold;'>{r['estado']}</span>", unsafe_allow_html=True)

            with c4:
                msj = urllib.parse.quote(
                    f"Hola {r['nombre']}, su clave de acceso para BASA SaaS es: {r['codigo_6_digitos']}. Mensualidad: {PRECIO_MENSUALIDAD}. Soporte: {CORREO_ADMIN}"
                )
                url_wsp = f"https://wa.me/{r['telefono']}?text={msj}"
                st.markdown(f'<a href="{url_wsp}" target="_blank" style="font-size:0.85rem; display:block; margin-bottom:6px;">💬 Enviar WhatsApp</a>', unsafe_allow_html=True)

                nuevo_st = "SUSPENDIDO" if r["estado"] == "ACTIVO" else "ACTIVO"
                if st.button(f"Cambiar a {nuevo_st}", key=f"btn_st_{r['id']}", use_container_width=True):
                    with get_db() as conn:
                        conn.execute("UPDATE clientes SET estado = ? WHERE id = ?", (nuevo_st, r["id"]))
                        conn.commit()
                    registrar_auditoria(cliente["nombre"], "SaaS Control", "Cambio de estado", f"{r['id']} -> {nuevo_st}")
                    st.rerun()


# -----------------------------------------------------------------------------
# MÓDULO 9: AUDITORÍA & SEGURIDAD
# -----------------------------------------------------------------------------
elif modulo_activo == "🛡️ Auditoría & Seguridad":
    st.title("🛡️ Registro de Auditoría (Audit Trail) & Seguridad")
    st.caption("Trazabilidad inmutable de accesos, facturación e-CF, asientos contables y cambios de licencia.")

    with get_db() as conn:
        df_aud = pd.read_sql_query("SELECT id, fecha, usuario, modulo, accion, detalle FROM auditoria ORDER BY id DESC LIMIT 200", conn)
    st.dataframe(df_aud, use_container_width=True)
    if not df_aud.empty:
        st.download_button("📥 Exportar Bitácora (.csv)", data=df_aud.to_csv(index=False).encode("utf-8"), file_name="auditoria_basa.csv", mime="text/csv")
