Guía Paso a Paso: Producción 10/10, Estados Financieros (NIC/NIIF/NIF) y Auditoría Forense — BASA Enterprise SaaS
Autor / Licenciatario: Lic. Pedro Baldera (⁠licpedrobaldera@gmail.com⁠)
WhatsApp Soporte: ⁠+1 (829) 771-7390⁠
Paso 1: Arranque Limpio en Producción (Cero Datos de Muestra)
1. Base de datos limpia: Tanto ⁠basa_enterprise_suite.py⁠ (⁠basa_saas_produccion.db⁠) como ⁠basa_enterprise_online.html⁠ inician sin clientes ficticios, sin facturas de prueba y sin empleados demo. Solo se precargan:
￼ La Clave Maestra de Administrador (⁠862600⁠).
￼ El Plan de Cuentas Estándar NIC / NIIF / NIF (⁠1101⁠ a ⁠6102⁠).
2. Si tenías datos anteriores en navegador: En la versión HTML5, pulsa el botón 🧹 Reiniciar Base Limpia en la barra lateral para limpiar el ⁠localStorage⁠.
3. Si despliegas en la nube (PostgreSQL): Configura la variable de entorno o secreto ⁠DATABASE_URL⁠ (⁠postgresql://usuario:clave@host:5432/basa_prod⁠) para persistencia multi-usuario en línea.
Paso 2: Publicación Rápida (GitHub → Streamlit Cloud y HTML5)
1. Opción WebApp Instantánea (Celular / PC): Abre ⁠basa_enterprise_online.html⁠ en cualquier navegador o súbelo a GitHub Pages / Vercel / Netlify como archivo estático.
2. Opción Full Python + PostgreSQL (Streamlit Cloud):
￼ Crea un repositorio en GitHub y sube ⁠basa_enterprise_suite.py⁠, ⁠requirements.txt⁠ y ⁠run_online.sh⁠.
￼ En ⁠share.streamlit.io⁠ selecciona New app, apunta a ⁠basa_enterprise_suite.py⁠ y agrega ⁠DATABASE_URL⁠ en Secrets.
￼ Para servidor VPS / Docker propio, ejecuta ⁠bash run_online.sh⁠.
Paso 3: Estados Financieros bajo NIC, NIIF y NIF
El módulo 📑 Estados Financieros (NIC/NIIF/NIF) consolida en tiempo real los asientos del Libro Mayor:
￼ Estado de Situación Financiera (NIC 1): Clasifica Activos (⁠Corrientes⁠ / ⁠No Corrientes⁠), Pasivos y Patrimonio, validando automáticamente la ecuación ⁠Activo = Pasivo + Patrimonio⁠.
￼ Estado de Resultados Integral (NIC 1 / NIIF 15 / NIC 2): Calcula Ingresos Ordinarios menos Costo de Ventas, Gastos Operativos (NIC 19) e ISR Corporativo estimado (27% RD, NIC 12).
￼ Estado de Flujos de Efectivo (NIC 7): Mide entradas, salidas y flujo neto de la cuenta ⁠1101 - Efectivo y Equivalentes⁠.
￼ Cambios en el Patrimonio y Notas Revelatorias: Resume las políticas contables aplicadas.
Paso 4: Protocolo de Auditoría Forense y Prevención de Irregularidades
Ejecuta el módulo 🛡️ Auditoría Forense & Cumplimiento antes de cada cierre mensual o declaración fiscal:
Control Automático
Norma Aplicable
Irregularidad Detectada
Acción Preventiva
Cuadre de Asientos
NIC 1 / Partida Doble
Diferencia Débito != Crédito
Bloquear o reversar asientos descuadrados
Ecuación Patrimonial
NIC 1
Activo != Pasivo + Patrimonio
Revisar cuentas sin clasificar o cierres
Stock y Margen
NIC 2 (Inventarios)
Stock < 0 o Precio < Costo
Prohibir ventas sin stock; ajustar VNR
Validación RNC / TrackId
DGII Norma 06-18 / Ley 32-23
e-CF 31 sin RNC 9/11 dígitos o sin TrackId
Exigir RNC válido y cargar .p12 oficial
Nómina y Documentos
NIC 19 / TSS RD
Colaborador sin Cédula/NSS válido
Completar ficha antes de generar TSS
