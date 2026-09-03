"""
Streamlit MVP Application: Digital Customer Twins (inDrive Qualitative Research).
Includes 3 BHT Twins & Interactive Focus Group Debate Module.
Supports Dynamic Theme Switcher: inDrive Electric Dark vs CRIBA Classic Light.
"""

import os
import sys
import json
import streamlit as st
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.twin_engine import DigitalTwinEngine
from src.focus_group import FocusGroupEngine

st.set_page_config(
    page_title="CRIBA Research - Digital Customer Twins",
    page_icon="https://cribaresearch.com/wp-content/uploads/2024/07/cropped-FAVICON-Verde@300x-32x32.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# AUTENTICACIÓN Y SEGURIDAD (PILOTO CRIBA x inDrive)
# ---------------------------------------------------------
def check_password():
    """Retorna True si el usuario ha iniciado sesión con credenciales válidas."""
    def password_entered():
        valid_passwords = st.secrets.get("passwords", {
            "admin": "Criba2026*",
            "indrive": "InDrivePiloto2026",
            "Criba": "InDrive2026",
            "criba": "InDrive2026"
        })
        user = st.session_state.get("login_username", "").strip()
        passwd = st.session_state.get("login_password", "").strip()
        
        matched_user = next((k for k in valid_passwords if k.lower() == user.lower()), None)
        
        if matched_user and valid_passwords[matched_user] == passwd:
            st.session_state["authenticated"] = True
            st.session_state["authenticated_user"] = matched_user
            if "login_password" in st.session_state:
                del st.session_state["login_password"]
        else:
            st.session_state["authenticated"] = False

    if st.session_state.get("authenticated", False):
        return True

    st.markdown("""
    <div style="max-width: 440px; margin: 4rem auto 1.5rem auto; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); border-top: 5px solid #10B981; text-align: center;">
        <img src="https://cribaresearch.com/wp-content/uploads/2024/07/cropped-FAVICON-Verde@300x-192x192.png" width="64" style="margin-bottom: 0.8rem;">
        <h2 style="color: #0F172A; margin-bottom: 0.2rem; font-weight: 700;">CRIBA Research</h2>
        <p style="color: #64748B; font-size: 0.9rem; margin-bottom: 1.5rem;">Plataforma Analítica de Digital Customer Twins (inDrive)</p>
    </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        with st.form("login_form"):
            st.markdown("##### 🔒 Acceso Restringido")
            st.text_input("Usuario", key="login_username", placeholder="Ej: indrive o admin")
            st.text_input("Contraseña", type="password", key="login_password")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            if submit:
                password_entered()
                if not st.session_state.get("authenticated", False):
                    st.error("❌ Usuario o contraseña incorrectos")
                else:
                    st.rerun()

    return False

if not check_password():
    st.stop()

def load_engines():
    return DigitalTwinEngine(), FocusGroupEngine()

engine, fg_engine = load_engines()

from src.llm_provider import test_gemini_connection

# Sidebar Setup with CRIBA Research Logo
st.sidebar.image("https://cribaresearch.com/wp-content/uploads/2024/07/cropped-FAVICON-Verde@300x-192x192.png", width=70)
st.sidebar.markdown("### **CRIBA Research**")
st.sidebar.caption("Qualitative AI Platform | inDrive Customer Twins")

user_logged = st.session_state.get("authenticated_user", "Usuario")
st.sidebar.success(f"👤 Sesión: `{user_logged}`")

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.markdown("---")
selected_mode = st.sidebar.radio(
    "Selecciona un Modo de Análisis:",
    [
        "📊 Cuadros y Matriz",
        "💬 Modo Chat Individual",
        "⚡ Matriz Side-by-Side",
        "🎙️ Modo Focus Group Interactivo",
        "🔍 Panel de Evidencia Cualitativa"
    ]
)

st.sidebar.markdown("---")
provider_name = os.getenv("LLM_PROVIDER", "mock").upper()
st.sidebar.info(f"**Motor LLM**: `{provider_name}`\n\n**Segmentos inDrive**: 3 Twins\n\n*(Evidencia: 25 entrevistas + PDF 58 pág.)*")

if user_logged.lower() == "admin":
    with st.sidebar.expander("🔧 Diagnóstico Conexión Gemini (Admin)"):
        if st.button("🧪 Probar Conexión API"):
            with st.spinner("Enviando paquete de prueba a Google Gemini..."):
                diag = test_gemini_connection()
                if diag["success"]:
                    st.success(f"✅ {diag['message']}")
                    st.caption(f"Clave detectada: `{diag.get('key_prefix')}`")
                else:
                    st.error(f"❌ {diag['message']}")
                    st.caption(f"Clave detectada: `{diag.get('key_prefix', 'NO_ENCONTRADA')}`")
                    if "details" in diag:
                        st.markdown("**Detalles HTTP de Google:**")
                        for d in diag["details"]:
                            st.caption(f"• {d}")

# Theme Selector buttons at the very bottom of sidebar
if "current_theme" not in st.session_state:
    st.session_state["current_theme"] = "inDrive Dark (Electric Lime)"

st.sidebar.markdown("---")
st.sidebar.caption("🎨 Estilo Visual:")
t_col1, t_col2 = st.sidebar.columns(2)

with t_col1:
    if st.button("🟢 inDrive Dark", key="btn_theme_dark", use_container_width=True):
        st.session_state["current_theme"] = "inDrive Dark (Electric Lime)"
        st.rerun()

with t_col2:
    if st.button("🌿 CRIBA Light", key="btn_theme_light", use_container_width=True):
        st.session_state["current_theme"] = "CRIBA Classic (Emerald Light)"
        st.rerun()

theme_choice = st.session_state["current_theme"]

# Dynamic Theme CSS Application
if theme_choice == "inDrive Dark (Electric Lime)":
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
            color: #F1F5F9;
        }
        
        .stAppViewMain {
            background-color: #0B0F17 !important;
        }

        .stSidebar {
            background-color: #111827 !important;
        }
        
        .criba-header {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            padding: 1.2rem 1.8rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1.5rem;
            border-left: 6px solid #B5FF00;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }
        
        .criba-header h1 {
            color: #B5FF00 !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
        }
        
        .criba-header p {
            color: #CBD5E1 !important;
            font-size: 0.95rem !important;
            margin-top: 0.3rem !important;
            margin-bottom: 0 !important;
        }

        .twin-card-header {
            font-size: 1.15rem;
            font-weight: 600;
            color: #F8FAFC;
            background-color: #1E293B;
            border: 1px solid #334155;
            padding: 0.7rem 1.1rem;
            border-radius: 8px;
            margin-bottom: 0.8rem;
        }

        .stButton>button {
            background-color: #B5FF00 !important;
            color: #000000 !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.55rem 1.3rem !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            background-color: #9CE000 !important;
            box-shadow: 0 4px 16px rgba(181, 255, 0, 0.4) !important;
            transform: translateY(-1px);
        }
        
        .unsupported-badge {
            background-color: #450A0A;
            color: #FCA5A5;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        .exploratory-badge {
            background-color: #451A03;
            color: #FDE68A;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85rem;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
        }
        
        .stAppViewMain {
            background-color: #F8FAFC;
        }
        
        .criba-header {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            padding: 1.2rem 1.8rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1.5rem;
            border-left: 6px solid #10B981;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
        }
        
        .criba-header h1 {
            color: #FFFFFF !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
        }
        
        .criba-header p {
            color: #94A3B8 !important;
            font-size: 0.95rem !important;
            margin-top: 0.3rem !important;
            margin-bottom: 0 !important;
        }

        .twin-card-header {
            font-size: 1.15rem;
            font-weight: 600;
            color: #0F172A;
            background-color: #F0FDF4;
            border: 1px solid #A7F3D0;
            padding: 0.7rem 1.1rem;
            border-radius: 8px;
            margin-bottom: 0.8rem;
        }
        
        .stButton>button {
            background-color: #10B981 !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1.2rem !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            background-color: #059669 !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        }
        
        .unsupported-badge {
            background-color: #FEF2F2;
            color: #991B1B;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        .exploratory-badge {
            background-color: #FFFBEB;
            color: #B45309;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85rem;
        }
    </style>
    """, unsafe_allow_html=True)

DEMO_QUESTIONS = [
    "¿Por qué prefieres proponer y negociar la tarifa manualmente en lugar de una tarifa fija?",
    "¿Qué tan importante es ver la dirección exacta del destino del pasajero antes de aceptar?",
    "¿Qué opinas de los bonos por metas diarias de viajes (ej. 15 viajes por S/ 50 extra)?",
    "¿Cómo influye la comisión que cobra la app en tu decisión de seguir usándola?",
    "¿Qué haces cuando un viaje te lleva a una zona considerada peligrosa como Collique o Añashuayco?",
    "¿Qué te haría apagar inDrive y encender Yango (o viceversa) durante tu jornada?",
    "¿Qué tan formal eres con tus documentos (SOAT, breve B2C, permiso municipal) y por qué?",
    "¿Cómo combinas las carreras de la app con los pasajeros que recoges en la calle o paradero?",
    "[EXPLORATORY SCENARIO] ¿Cómo reaccionarías si inDrive cobrara una comisión mensual fija en lugar de porcentaje por viaje?",
    "[EXPLORATORY SCENARIO] ¿Aceptarías un filtro de seguridad nocturno que requiera foto de DNI del pasajero aunque reduzca un 15% los viajes?"
]

FOCUS_GROUP_TOPICS = [
    "¿Cómo solucionar la escasez de oferta de conductores en Lima Norte y Sur para aumentar la disponibilidad?",
    "¿Qué modelo prefieren: Negociación manual de tarifa (inDrive) vs Asignación directa con bonos de cuota (Yango)?",
    "¿Estarían dispuestos a pagar un 15% de comisión si inDrive incluyera un seguro médico de salud y botón de pánico policial?",
    "¿Cómo manejar la seguridad al transportar pasajeros hacia cerros y zonas sin iluminación en Comas/Collique?",
    "¿Qué haría que usen inDrive como su app principal el 100% de su jornada laboral?"
]

st.markdown("""
<div class="criba-header">
    <h1>CRIBA Research • Digital Customer Twins</h1>
    <p>Motor de Investigación Cualitativa con IA derivado de 25 entrevistas en profundidad + Informe General PDF (58 pág) | Estudio inDrive Mototaxis</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODO 1: CUADROS Y MATRIZ (CON FICHAS INTEGRADAS)
# ---------------------------------------------------------
if selected_mode == "📊 Cuadros y Matriz":
    st.subheader("📊 Cuadros Sintéticos, Fichas de Perfil & Matriz Comparativa")
    st.caption("Resumen estructurado en tablas e indicadores derivados del informe completo (58 páginas PDF) y las 25 entrevistas en profundidad.")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Entrevistas Cualitativas", "25 IDIs", "Lima Norte & Sur")
    with m2:
        st.metric("Informe General PDF", "58 Páginas", "Agosto 2026")
    with m3:
        st.metric("Economía de Ticket", "S/ 3.50 - 8.00", "Micro-ticket L5")
    with m4:
        st.metric("Marcas Evaluadas", "3 Apps", "inDrive, Yango, Uber")

    st.markdown("---")

    tab_c1, tab_c2, tab_c3, tab_c4 = st.tabs([
        "📋 Cuadro Comparativo por Segmentos",
        "👤 Fichas de Perfil Detalladas",
        "⚔️ Matriz Competitiva de Apps",
        "💡 Resumen Ejecutivo & Oportunidades"
    ])

    with tab_c1:
        st.markdown("### 📋 Cuadro Comparativo Integrado por Segmentos de Conductor")
        st.caption("Matriz sintética que contrasta las 7 dimensiones estratégicas clave entre los perfiles de conductores Tuk Tuk / Mototaxi.")

        segment_data = {
            "Dimensión Estratégica": [
                "1. Modelo Tarifario Preferido",
                "2. Principal Motivador / Driver",
                "3. Mayor Fricción Operativa",
                "4. Actitud ante Tarifa Fija",
                "5. Sensibilidad a Bonos y Cuotas",
                "6. Comportamiento en Zonas Riesgosas",
                "7. Relación y Lealtad con inDrive"
            ],
            "Marcos (Autónomo y Precavido)": [
                "Negociación manual abierta ('Fair Fare')",
                "Control total del destino, precio y autonomía",
                "Temor a carreras a cerros peligrosos (Collique/Añashuayco)",
                "Rechazo rotundo; exige ver destino antes de ofertar",
                "Baja; prefiere asegurar margen por viaje sin presiones",
                "Filtra severamente destinos; eleva tarifa si hay trocha",
                "Alta preferencia por el modelo de contraoferta de inDrive"
            ],
            "Julio (Volumen y Bonos)": [
                "Asignación automática directa (Modelo Yango)",
                "Maximización del ingreso diario por volumen de viajes",
                "Pérdida de tiempo ofertando y esperando confirmación",
                "Aceptación alta si viene respaldada por bonos",
                "Alta; se mueve 100% por metas y garantizados en soles",
                "Acepta riesgos si la cuota del día lo exige",
                "Usa inDrive como respaldo; migra a Yango por incentivos"
            ],
            "Carlos (Oportunista Relajado)": [
                "Híbrido (App + Paradero tradicional)",
                "Ingreso complementario sin horario fijo ni estrés",
                "Comisiones altas o sistemas complejos de scoring",
                "Indiferente; acepta si la tarifa cubre la distancia",
                "Media-Baja; no trabaja suficientes horas para metas",
                "Evita zonas de alto riesgo; prefiere rutas tranquilas",
                "Usa inDrive de forma esporádica cuando le conviene"
            ]
        }
        df_segmentos = pd.DataFrame(segment_data)

        st.dataframe(
            df_segmentos,
            use_container_width=True,
            hide_index=True
        )

        csv_data = df_segmentos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Cuadro Comparativo en CSV (Excel)",
            data=csv_data,
            file_name="cuadro_comparativo_segmentos_indrive.csv",
            mime="text/csv"
        )

    with tab_c2:
        st.markdown("### 👤 Fichas de Perfil - Segmentos inDrive")

        p_tabs = st.tabs([
            "🔵 Twin A: Marcos (Disciplined Hard Work)",
            "🟢 Twin B: Julio (Tactical Cash Optimizer)",
            "🟡 Twin C: Carlos (Low-Pressure Flexibles)"
        ])

        for tab, pid in zip(p_tabs, ["twin_a_autonomo_precavido", "twin_b_volumen_bonos", "twin_c_oportunista_relajado"]):
            with tab:
                pdata = engine.get_profile(pid)
                st.markdown(f"### {pdata.get('nombre_interno')}")
                st.markdown(f"**Segmento inDrive**: `{pdata.get('bht_segment')}`")
                st.markdown(f"*{pdata.get('descripcion_corta')}*")

                st.markdown("---")
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.markdown("#### 🟢 EVIDENCE (Del Corpus)")
                    st.markdown("**Necesidades Centrales**:")
                    for item in pdata.get("EVIDENCE", {}).get("necesidades", []):
                        st.markdown(f"- {item}")
                    st.markdown("**Drivers Principales**:")
                    for item in pdata.get("EVIDENCE", {}).get("drivers", []):
                        st.markdown(f"- {item}")
                    st.markdown("**Fricciones Críticas**:")
                    for item in pdata.get("EVIDENCE", {}).get("fricciones", []):
                        st.markdown(f"- {item}")

                with c2:
                    st.markdown("#### 🔵 INTERPRETATION (Síntesis Analítica)")
                    st.info(pdata.get("INTERPRETATION", {}).get("perfil_analitico", ""))
                    st.markdown("**Tensiones Internas**:")
                    st.write(pdata.get("INTERPRETATION", {}).get("tensiones_internas", ""))
                    st.markdown("**Lenguaje Característico**:")
                    for lang in pdata.get("lenguaje_caracteristico", []):
                        st.markdown(f"- *\"{lang}\"*")

                with c3:
                    st.markdown("#### 🔴 UNKNOWN (Sin Evidencia Suficiente)")
                    st.warning("Temas sin evidencia suficiente en el estudio:")
                    for unk in pdata.get("UNKNOWN", {}).get("temas_sin_evidencia", []):
                        st.markdown(f"- ❌ {unk}")

                st.markdown("---")
                st.markdown(f"**Fuentes / Transcripts Sustentantes**: `{', '.join(pdata.get('fuentes_evidencia', {}).get('transcripts', []))}`")

    with tab_c3:
        st.markdown("### ⚔️ Matriz Competitiva de Plataformas (inDrive vs Yango vs Uber)")
        st.caption("Comparativo de posicionamiento de marca extraído del capítulo 05 del informe de investigación (Páginas 26-53 del PDF).")

        brand_data = {
            "Atributo / Dimensión": [
                "Posicionamiento percibido",
                "Mecanismo de captura",
                "Estructura de ganancias",
                "Fortaleza principal",
                "Barrera / Fricción mayor",
                "Nivel de adopción en mototaxis"
            ],
            "inDrive (Fair Fare)": [
                "Autonomía y precio justo",
                "Negociación bidireccional de tarifa",
                "Comisión porcentual por viaje",
                "Conductor elige ruta, precio y pasajero",
                "Poca densidad en zonas periféricas lejanas",
                "Líder en reputación y equidad de marca"
            ],
            "Yango (Volume Leader)": [
                "Rapidez y bonos de volumen",
                "Asignación automática directa",
                "Bonos por cumplimiento de cuotas diarias",
                "Alta liquidez y flujo continuo de pedidos",
                "Sensación de pérdida de control en tarifa",
                "Crecimiento agresivo impulsado por incentivos"
            ],
            "Uber (Auto-Centric)": [
                "Seguridad y marca corporativa",
                "Algoritmo de asignación dinámica",
                "Tarifa calculada por tiempo y distancia",
                "Reconocimiento de marca masivo en autos",
                "Interfaz no optimizada para mototaxis (L5)",
                "Uso secundario y limitado en el segmento Tuk Tuk"
            ]
        }
        df_brands = pd.DataFrame(brand_data)
        st.dataframe(df_brands, use_container_width=True, hide_index=True)

    with tab_c4:
        st.markdown("### 💡 Hallazgos Clave & Oportunidades del Informe PDF (Agosto 2026)")
        
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.info("""
            **📌 Realidad del Mercado L5 (Pág. 3-4 del PDF):**
            - **Economía de Micro-ticket**: Las carreras oscilan entre **S/ 3.50 y S/ 8.00**.
            - **Rutina Híbrida**: El conductor alterna el recojo en calle (*Street pick-up*) con el encendido de la app.
            - **Boca a Boca & WhatsApp**: La adopción se propaga mostrando capturas de pantalla de ganancias diarias en grupos de mecánica.
            """)
        with col_h2:
            st.success("""
            **🎯 Oportunidad de Crecimiento inDrive:**
            - **Desbloquear la UX**: Adaptar la interfaz para operaciones rápidas en mototaxis (L5) sin requerir clicks complejos.
            - **Push de Pasajeros**: Aumentar la densidad de pedidos en distritos periféricos (Comas, Carabayllo, S.J.L.).
            - **Incentivos Transparentes**: Crear esquemas de fidelización que mantengan el modelo "Fair Fare" sin forzar la asignación a ciegas.
            """)

# ---------------------------------------------------------
# MODO 2: CHAT INDIVIDUAL
# ---------------------------------------------------------
elif selected_mode == "💬 Modo Chat Individual":
    st.subheader("💬 Interacción Individual con un Digital Customer Twin")

    twin_choice = st.selectbox(
        "Selecciona el Digital Customer Twin:",
        [
            ("twin_a_autonomo_precavido", "Marcos - Disciplined Hard Work (Autónomo y Precavido)"),
            ("twin_b_volumen_bonos", "Julio - Tactical Cash Optimizer (Volumen y Bonos)"),
            ("twin_c_oportunista_relajado", "Carlos - Low-Pressure Flexibles (Oportunista y Relajado)")
        ],
        format_func=lambda x: x[1]
    )
    twin_id = twin_choice[0]
    profile_info = engine.get_profile(twin_id)

    with st.expander(f"ℹ️ Ver Resumen de Perfil: {profile_info.get('nombre_interno')}"):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"**Segmento inDrive**: `{profile_info.get('bht_segment', 'N/A')}`")
            st.markdown(f"**Descripción**: {profile_info.get('descripcion_corta', '')}")
        with col_p2:
            st.markdown("**Drivers Principales**:")
            for d in profile_info.get('EVIDENCE', {}).get('drivers', []):
                st.markdown(f"- {d}")

    history_key = f"chat_history_{twin_id}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    user_query = st.chat_input("Escribe tu pregunta para este perfil...")

    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("evidence"):
                with st.expander("🔎 Evidencia Cualitativa"):
                    for ev in msg["evidence"]:
                        st.markdown(f"**Source**: `{ev['transcript_id']}` ({ev['interviewee_label']})")
                        st.markdown(f"> *\"{ev['text_snippet']}\"*")

    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)

        is_exploratory = "[EXPLORATORY SCENARIO]" in user_query.upper()
        with st.spinner("Consultando corpus..."):
            result = engine.ask(twin_id, user_query, is_exploratory=is_exploratory)

        with st.chat_message("assistant"):
            if result.get("is_unsupported"):
                st.markdown("<span class='unsupported-badge'>⚠️ SIN EVIDENCIA SUFICIENTE EN CORPUS</span>", unsafe_allow_html=True)
            elif result.get("is_exploratory"):
                st.markdown("<span class='exploratory-badge'>🧪 ESCENARIO EXPLORATORIO HIPOTÉTICO</span>", unsafe_allow_html=True)

            st.markdown(result["response"])

            if result.get("evidence_used"):
                with st.expander("🔎 Ver Evidencia Cualitativa Detrás de esta Respuesta"):
                    for ev in result["evidence_used"]:
                        st.markdown(f"**Transcripción Source**: `{ev['transcript_id']}` ({ev['interviewee_label']})")
                        st.markdown(f"> *\"{ev['text_snippet']}\"*")
                        st.caption(f"Interpretación: {ev['interpretacion']}")

        st.session_state[history_key].append({"role": "user", "content": user_query})
        st.session_state[history_key].append({"role": "assistant", "content": result["response"], "evidence": result.get("evidence_used", [])})

# ---------------------------------------------------------
# MODO 3: MATRIZ SIDE-BY-SIDE (EJECUTIVA + CLÁSICA)
# ---------------------------------------------------------
elif selected_mode == "⚡ Matriz Side-by-Side":
    st.subheader("⚡ Matriz Side-by-Side Ejecutiva en Tiempo Real")
    st.caption("Diseñada para la Presentación a inDrive: Haz clic en las preguntas de dilema estratégico o escribe tu propia consulta para comparar posturas sintetizadas en 3 columnas.")

    st.markdown("##### 💡 Dilemas Estratégicos de Negocio (Disparadores de 1 Clic):")
    
    prompt_col1, prompt_col2, prompt_col3 = st.columns(3)
    selected_prompt = None
    
    with prompt_col1:
        if st.button("🔥 ¿Yango regala S/ 100 de bono diario?", use_container_width=True):
            selected_prompt = "¿Cómo reaccionarías si Yango lanza una campaña agresiva regalando S/ 100 diarios por completar 15 carreras en tu zona?"
        if st.button("🛡️ ¿Filtro obligatorio de DNI a pasajeros?", use_container_width=True):
            selected_prompt = "[EXPLORATORY SCENARIO] ¿Aceptarías un filtro de seguridad nocturno que requiera foto de DNI del pasajero antes de pedir la moto aunque reduzca 15% los viajes?"
        if st.button("💳 ¿QR Yape/Plin en app sin dar celular?", use_container_width=True):
            selected_prompt = "¿Te ayudaría que inDrive integre un QR de cobro digital (Yape/Plin) en la pantalla para evitar dictarle tu número de celular personal al pasajero?"

    with prompt_col2:
        if st.button("💵 ¿Comisión fija mensual vs % por viaje?", use_container_width=True):
            selected_prompt = "[EXPLORATORY SCENARIO] ¿Cómo reaccionarías si inDrive cobrara una comisión mensual fija en lugar de un porcentaje por viaje?"
        if st.button("⛰️ ¿Tarifa extra automática por cerros/trocha?", use_container_width=True):
            selected_prompt = "¿Aceptarías que la app calcule automáticamente un recargo por zonas empinadas o trochas como Collique en lugar de negociarlo manualmente?"
        if st.button("🔧 ¿Descuento repuestos Bajaj o súper?", use_container_width=True):
            selected_prompt = "¿Qué programa de lealtad te motivaría más a usar inDrive: descuentos en gasocentros y mantenimiento de mototaxi (Bajaj/TVS) o vales de supermercado/cine para tu familia?"

    with prompt_col3:
        if st.button("⏱️ ¿Asignación directa en horas punta?", use_container_width=True):
            selected_prompt = "¿Estarías dispuesto a activar asignación directa automática durante horas punta si inDrive garantiza una tarifa mínima de S/ 6.00?"
        if st.button("🤝 ¿Seguro de salud a cambio de 15% comisión?", use_container_width=True):
            selected_prompt = "¿Estarías dispuesto a pagar un 15% de comisión si inDrive incluyera un seguro médico de salud y botón de pánico policial?"
        if st.button("🏦 ¿Microcréditos in-app para llantas/SOAT?", use_container_width=True):
            selected_prompt = "¿Aceptarías un microcrédito pre-aprobado dentro de la app para comprar llantas o renovar tu SOAT/AFOCAT si se descuenta automáticamente con un pequeño monto por viaje?"

    st.markdown("---")
    
    default_query = selected_prompt if selected_prompt else st.session_state.get("active_matrix_query", "")
    user_query = st.text_input("✍️ O escribe tu propia pregunta o escenario estratégico:", value=default_query, key="matrix_query_input")
    
    if selected_prompt:
        st.session_state["active_matrix_query"] = selected_prompt

    exec_button = st.button("🚀 Ejecutar Matriz Comparativa", type="primary")

    if exec_button or selected_prompt:
        query_to_run = selected_prompt if selected_prompt else user_query
        
        if not query_to_run:
            st.warning("Por favor selecciona una pregunta disparadora o escribe una consulta propia.")
        else:
            is_exploratory = "[EXPLORATORY SCENARIO]" in query_to_run.upper() or "EXPLORATORIO" in query_to_run.upper()
            
            st.markdown(f"### 📋 Matriz Sintética Ejecutiva: *\"{query_to_run}\"*")
            
            with st.spinner("Consultando perfiles y sintetizando matriz de posturas..."):
                res_a = engine.ask("twin_a_autonomo_precavido", query_to_run, is_exploratory=is_exploratory)
                res_b = engine.ask("twin_b_volumen_bonos", query_to_run, is_exploratory=is_exploratory)
                res_c = engine.ask("twin_c_oportunista_relajado", query_to_run, is_exploratory=is_exploratory)

            col_a, col_b, col_c = st.columns(3)

            def extract_verdict(resp_text, twin_id):
                txt_lower = resp_text.lower()
                if "Marcos" in twin_id or "autonomo" in twin_id:
                    if "no aceptaría" in txt_lower or "rechaz" in txt_lower or "control" in txt_lower:
                        return "🔴 RECHAZA / PREFIERE CONTROL Y AUTONOMÍA"
                    elif "aceptaría" in txt_lower or "de acuerdo" in txt_lower:
                        return "🟢 ACEPTA / CON BUEN PRECIO"
                    else:
                        return "🟡 CONDICIONADO A SEGURIDAD Y TARIFA"
                elif "Julio" in twin_id or "volumen" in twin_id:
                    if "bonos" in txt_lower or "volumen" in txt_lower or "acepto" in txt_lower or "ganancia" in txt_lower:
                        return "🟢 ACEPTA / MOVIDO POR BONOS Y VOLUMEN"
                    else:
                        return "🟡 EVALÚA COSTO-BENEFICIO RÁPIDO"
                else:
                    if "ritmo" in txt_lower or "tranquilo" in txt_lower or "paso" in txt_lower:
                        return "🟡 INDIFERENTE / SEGÚN CONVENIENCIA"
                    else:
                        return "🔵 ADAPTABLE SIN ESTRÉS"

            with col_a:
                v_a = extract_verdict(res_a["response"], "twin_a")
                st.markdown(
                    f"""
                    <div style='background-color:{'#1E293B' if theme_choice.startswith('inDrive') else '#EFF6FF'}; border:1px solid {'#3B82F6' if theme_choice.startswith('inDrive') else '#BFDBFE'}; padding:0.8rem; border-radius:8px; margin-bottom:0.8rem;'>
                        <div style='font-size:1.05rem; font-weight:700; color:{'#93C5FD' if theme_choice.startswith('inDrive') else '#1E40AF'};'>🔵 Twin A: Marcos</div>
                        <div style='font-size:0.82rem; color:#3B82F6; font-weight:600;'>Disciplined Hard Work</div>
                        <div style='margin-top:0.4rem; font-size:0.85rem; font-weight:700; color:{'#EFF6FF' if theme_choice.startswith('inDrive') else '#1E3A8A'}; background-color:{'#1E3A8A' if theme_choice.startswith('inDrive') else '#DBEAFE'}; padding:0.3rem 0.6rem; border-radius:4px;'>
                            {v_a}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.markdown(res_a["response"])
                with st.expander("🔎 Evidencia Cualitativa"):
                    for ev in res_a.get("evidence_used", []):
                        st.markdown(f"**[{ev['transcript_id']}]** *\"{ev['text_snippet'][:110]}...\"*")

            with col_b:
                v_b = extract_verdict(res_b["response"], "twin_b")
                st.markdown(
                    f"""
                    <div style='background-color:{'#064E3B' if theme_choice.startswith('inDrive') else '#F0FDF4'}; border:1px solid {'#10B981' if theme_choice.startswith('inDrive') else '#BBF7D0'}; padding:0.8rem; border-radius:8px; margin-bottom:0.8rem;'>
                        <div style='font-size:1.05rem; font-weight:700; color:{'#A7F3D0' if theme_choice.startswith('inDrive') else '#166534'};'>🟢 Twin B: Julio</div>
                        <div style='font-size:0.82rem; color:#10B981; font-weight:600;'>Tactical Cash Optimizer</div>
                        <div style='margin-top:0.4rem; font-size:0.85rem; font-weight:700; color:{'#ECFDF5' if theme_choice.startswith('inDrive') else '#14532D'}; background-color:{'#047857' if theme_choice.startswith('inDrive') else '#DCFCE7'}; padding:0.3rem 0.6rem; border-radius:4px;'>
                            {v_b}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.markdown(res_b["response"])
                with st.expander("🔎 Evidencia Cualitativa"):
                    for ev in res_b.get("evidence_used", []):
                        st.markdown(f"**[{ev['transcript_id']}]** *\"{ev['text_snippet'][:110]}...\"*")

            with col_c:
                v_c = extract_verdict(res_c["response"], "twin_c")
                st.markdown(
                    f"""
                    <div style='background-color:{'#78350F' if theme_choice.startswith('inDrive') else '#FFFBEB'}; border:1px solid {'#F59E0B' if theme_choice.startswith('inDrive') else '#FDE68A'}; padding:0.8rem; border-radius:8px; margin-bottom:0.8rem;'>
                        <div style='font-size:1.05rem; font-weight:700; color:{'#FDE68A' if theme_choice.startswith('inDrive') else '#92400E'};'>🟡 Twin C: Carlos</div>
                        <div style='font-size:0.82rem; color:#F59E0B; font-weight:600;'>Low-Pressure Flexibles</div>
                        <div style='margin-top:0.4rem; font-size:0.85rem; font-weight:700; color:{'#FEF3C7' if theme_choice.startswith('inDrive') else '#78350F'}; background-color:{'#B45309' if theme_choice.startswith('inDrive') else '#FEF3C7'}; padding:0.3rem 0.6rem; border-radius:4px;'>
                            {v_c}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
                st.markdown(res_c["response"])
                with st.expander("🔎 Evidencia Cualitativa"):
                    for ev in res_c.get("evidence_used", []):
                        st.markdown(f"**[{ev['transcript_id']}]** *\"{ev['text_snippet'][:110]}...\"*")

# ---------------------------------------------------------
# MODO 4: FOCUS GROUP INTERACTIVO
# ---------------------------------------------------------
elif selected_mode == "🎙️ Modo Focus Group Interactivo":
    st.subheader("🎙️ Simulación de Focus Group Cualitativo en Tiempo Real")
    st.caption("Plateale una problemática de producto o propuesta estratégica a los Digital Customer Twins y observa cómo conversan, debaten y responden directamente a sus argumentos.")

    c1, c2 = st.columns([3, 1])
    with c1:
        preset_fg = st.selectbox("💡 Selecciona una problemática clave del Brief de inDrive:", FOCUS_GROUP_TOPICS)
        topic_input = st.text_input("O ingresa un tema de debate personalizado:", value=preset_fg)
    with c2:
        num_rounds = st.slider("Rondas de debate:", min_value=1, max_value=4, value=2)

    st.markdown("##### Participantes del Focus Group:")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.checkbox("🔵 Marcos (Disciplined Hard Work)", value=True, disabled=True)
    with col_t2:
        st.checkbox("🟢 Julio (Tactical Cash Optimizer)", value=True, disabled=True)
    with col_t3:
        st.checkbox("🟡 Carlos (Low-Pressure Flexibles)", value=True, disabled=True)

    selected_twins = ["twin_a_autonomo_precavido", "twin_b_volumen_bonos", "twin_c_oportunista_relajado"]

    if st.button("🚀 Iniciar Sesión de Focus Group", type="primary"):
        with st.spinner("Convocando a los Digital Twins y ejecutando el debate multi-agente..."):
            res_fg = fg_engine.run_focus_group(topic_input, selected_twins, num_rounds=num_rounds)

        st.markdown("---")
        st.markdown(f"### 💬 Transcripción del Debate en Vivo: *\"{topic_input}\"*")

        for turn in res_fg.get("transcript", []):
            role = turn.get("role")
            speaker = turn.get("speaker")
            text = turn.get("text")
            r_idx = turn.get("round", 0)

            if role == "moderator":
                st.info(f"🎙️ **{speaker}**: {text}")
            else:
                color_border = "#3B82F6" if "Marcos" in speaker else ("#10B981" if "Julio" in speaker else "#F59E0B")
                st.markdown(
                    f"""
                    <div style='background-color:{'#1E293B' if theme_choice.startswith('inDrive') else '#FFFFFF'}; border-left:4px solid {color_border}; padding:0.8rem 1rem; border-radius:6px; margin-bottom:0.8rem; box-shadow:0 1px 3px rgba(0,0,0,0.05);'>
                        <div style='font-size:0.85rem; color:{'#94A3B8' if theme_choice.startswith('inDrive') else '#64748B'}; font-weight:600;'>Ronda {r_idx} | {speaker}</div>
                        <div style='font-size:0.98rem; color:{'#F8FAFC' if theme_choice.startswith('inDrive') else '#1E293B'}; margin-top:0.3rem;'>{text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if turn.get("evidence"):
                    with st.expander(f"🔎 Ver Evidencia Cualitativa detras de la intervención de {speaker}"):
                        for ev in turn["evidence"]:
                            st.markdown(f"**Source**: `{ev['transcript_id']}` ({ev['interviewee_label']})")
                            st.markdown(f"> *\"{ev['text_snippet']}\"*")
                            st.caption(f"Interpretación: {ev['interpretacion']}")

        st.markdown("---")
        st.markdown("### 📝 Síntesis Cualitativa del Moderador (Conclusiones de Producto)")
        st.markdown(res_fg.get("synthesis", ""))

# ---------------------------------------------------------
# MODO 5: PANEL DE EVIDENCIA CUALITATIVA
# ---------------------------------------------------------
elif selected_mode == "🔍 Panel de Evidencia Cualitativa":
    st.subheader("🔍 Explorador de Matriz de Evidencia Cualitativa")
    matrix_file = "evidence/evidence_matrix.json"
    if os.path.exists(matrix_file):
        with open(matrix_file, "r", encoding="utf-8") as f:
            mdata = json.load(f)
        for item in mdata:
            with st.expander(f"📌 [{item['patron_id']}] {item['patron']} ({item['total_menciones']} Entrevistados)"):
                st.markdown(f"**Tema**: {item['tema']}")
                st.markdown(f"**Afinidad de Perfil**: `{item['profile_affinity']}`")
                st.markdown(f"**Entrevistados**: `{', '.join(item['entrevistados'])}`")
                st.markdown(f"**Interpretación**: {item['interpretacion']}")
                for ev in item["evidencia"]:
                    st.markdown(f"- **[{ev['transcript_id']}] {ev['evidencia_textual']}\"*")
