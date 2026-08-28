"""
Streamlit MVP Application: Digital Customer Twins (inDrive Qualitative Research).
Includes 3 BHT Twins & Interactive Focus Group Debate Module.
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
    page_title="Digital Customer Twins & Focus Group - inDrive MVP",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished commercial demo feel
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .twin-card-header {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0F172A;
        background-color: #F1F5F9;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    .fg-speaker-card {
        background-color: #FFFFFF;
        border-left: 4px solid #3B82F6;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
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

@st.cache_resource
def load_engines():
    return DigitalTwinEngine(), FocusGroupEngine()

engine, fg_engine = load_engines()

# Sidebar Setup
st.sidebar.image("https://img.icons8.com/color/96/user-credentials.png", width=64)
st.sidebar.title("Digital Customer Twins")
st.sidebar.caption("Plataforma Analítica de Gemelos Digitales | inDrive")

st.sidebar.markdown("---")
selected_mode = st.sidebar.radio(
    "Selecciona un Modo de Análisis:",
    [
        "🎙️ Modo Focus Group Interactivo",
        "⚔️ Modo Comparación Side-by-Side",
        "💬 Modo Chat Individual",
        "📑 Fichas de Perfil (Taxonomía BHT)",
        "🔍 Panel de Evidencia Cualitativa"
    ]
)

st.sidebar.markdown("---")
provider_name = os.getenv("LLM_PROVIDER", "mock").upper()
st.sidebar.info(f"**Motor LLM**: `{provider_name}`\n\n**Segmentos BHT**: 3 Twins\n\n*(Transcripts preservados localmente en `/data/`)*")

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

st.markdown("<div class='main-title'>Digital Customer Twins & Focus Group Interactivo</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Agentes sintéticos cualitativos derivados de 25 entrevistas reales en Lima | Alineados con la Segmentación BHT de inDrive</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODO 1: FOCUS GROUP INTERACTIVO (NUEVO)
# ---------------------------------------------------------
if selected_mode == "🎙️ Modo Focus Group Interactivo":
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
                    <div style='background-color:#FFFFFF; border-left:4px solid {color_border}; padding:0.8rem 1rem; border-radius:6px; margin-bottom:0.8rem; box-shadow:0 1px 3px rgba(0,0,0,0.05);'>
                        <div style='font-size:0.85rem; color:#64748B; font-weight:600;'>Ronda {r_idx} | {speaker}</div>
                        <div style='font-size:0.98rem; color:#1E293B; margin-top:0.3rem;'>{text}</div>
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
# MODO 2: COMPARACIÓN SIDE-BY-SIDE (3 TWINS)
# ---------------------------------------------------------
elif selected_mode == "⚔️ Modo Comparación Side-by-Side":
    st.subheader("⚔️ Comparación Simultánea Side-by-Side (3 Perfiles BHT)")
    st.caption("Formula una pregunta y compara en tres columnas cómo respondería cada segmento de la taxonomía BHT de inDrive.")

    comp_preset = st.selectbox("💡 Preguntas de demostración:", ["-- Selecciona o escribe abajo --"] + DEMO_QUESTIONS)
    comp_query = st.text_input("Ingresa tu pregunta:", value=comp_preset if comp_preset != "-- Selecciona o escribe abajo --" else "")

    if st.button("🚀 Comparar 3 Perfiles", type="primary"):
        if not comp_query:
            st.warning("Por favor ingresa una pregunta.")
        else:
            is_exploratory = "[EXPLORATORY SCENARIO]" in comp_query.upper()

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.markdown("<div class='twin-card-header'>🔵 Twin A: Marcos<br><small>Disciplined Hard Work</small></div>", unsafe_allow_html=True)
                with st.spinner("Generando..."):
                    res_a = engine.ask("twin_a_autonomo_precavido", comp_query, is_exploratory=is_exploratory)
                st.write(res_a["response"])
                with st.expander("🔎 Evidencia Twin A"):
                    for ev in res_a.get("evidence_used", []):
                        st.markdown(f"**[{ev['transcript_id']}]** *\"{ev['text_snippet'][:120]}...\"*")

            with col_b:
                st.markdown("<div class='twin-card-header'>🟢 Twin B: Julio<br><small>Tactical Cash Optimizer</small></div>", unsafe_allow_html=True)
                with st.spinner("Generando..."):
                    res_b = engine.ask("twin_b_volumen_bonos", comp_query, is_exploratory=is_exploratory)
                st.write(res_b["response"])
                with st.expander("🔎 Evidencia Twin B"):
                    for ev in res_b.get("evidence_used", []):
                        st.markdown(f"**[{ev['transcript_id']}]** *\"{ev['text_snippet'][:120]}...\"*")

            with col_c:
                st.markdown("<div class='twin-card-header'>🟡 Twin C: Carlos<br><small>Low-Pressure Flexibles</small></div>", unsafe_allow_html=True)
                with st.spinner("Generando..."):
                    res_c = engine.ask("twin_c_oportunista_relajado", comp_query, is_exploratory=is_exploratory)
                st.write(res_c["response"])
                with st.expander("🔎 Evidencia Twin C"):
                    for ev in res_c.get("evidence_used", []):
                        st.markdown(f"**[{ev['transcript_id']}]** *\"{ev['text_snippet'][:120]}...\"*")

# ---------------------------------------------------------
# MODO 3: CHAT INDIVIDUAL
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
            st.markdown(f"**Segmento BHT**: `{profile_info.get('bht_segment', 'N/A')}`")
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
# MODO 4: FICHAS DE PERFIL (3 TWINS)
# ---------------------------------------------------------
elif selected_mode == "📑 Fichas de Perfil (Taxonomía BHT)":
    st.subheader("📑 Fichas Estructuradas de Perfiles Sintéticos (BHT Alignment)")

    p_tabs = st.tabs([
        "🔵 Twin A: Marcos (Disciplined Hard Work)",
        "🟢 Twin B: Julio (Tactical Cash Optimizer)",
        "🟡 Twin C: Carlos (Low-Pressure Flexibles)"
    ])

    for tab, pid in zip(p_tabs, ["twin_a_autonomo_precavido", "twin_b_volumen_bonos", "twin_c_oportunista_relajado"]):
        with tab:
            pdata = engine.get_profile(pid)
            st.markdown(f"### {pdata.get('nombre_interno')}")
            st.markdown(f"**Segmento BHT de inDrive**: `{pdata.get('bht_segment')}`")
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

# ---------------------------------------------------------
# MODO 5: PANEL DE EVIDENCIA
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
                    st.markdown(f"- **[{ev['transcript_id']}] {ev['interviewee_label']}**: *\"{ev['evidencia_textual']}\"*")


