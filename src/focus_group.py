"""
Multi-Agent Focus Group Engine.
Simulates interactive qualitative focus group debates between Digital Customer Twins.
"""

import os
import sys
import yaml
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.twin_engine import DigitalTwinEngine
from src.llm_provider import get_llm_provider, BaseLLMProvider, MockLocalProvider

class FocusGroupEngine:
    def __init__(self):
        self.twin_engine = DigitalTwinEngine()
        self.provider: BaseLLMProvider = get_llm_provider()

    def run_focus_group(self, topic: str, selected_twin_ids: List[str], num_rounds: int = 2) -> Dict[str, Any]:
        """
        Execute an interactive multi-agent Focus Group debate session.
        """
        if not selected_twin_ids:
            return {"error": "No twins selected for focus group."}

        twins_info = []
        for tid in selected_twin_ids:
            p = self.twin_engine.get_profile(tid)
            if p:
                twins_info.append(p)

        if not twins_info:
            return {"error": "Selected twin profiles could not be loaded."}

        transcript = []

        # Step 1: Moderator Opening
        mod_intro = f"Buenas tardes a todos. Les he convocado hoy para discutir un tema clave sobre la chamba en mototaxi: '{topic}'. Queremos escuchar sus opiniones sinceras y debate abierto entre ustedes."
        transcript.append({
            "speaker": "Moderador (CRIBA / inDrive)",
            "role": "moderator",
            "text": mod_intro,
            "round": 0
        })

        # Step 2: Multi-Turn Conversation Rounds
        for round_idx in range(1, num_rounds + 1):
            for profile in twins_info:
                twin_id = profile["id"]
                twin_name = profile["nombre_interno"]

                # Retrieve evidence for topic
                retrieved_ev = self.twin_engine.retriever.retrieve(topic, profile_affinity=twin_id, top_k=3)

                # Format conversation history context so far
                history_text_list = []
                for turn in transcript:
                    history_text_list.append(f"{turn['speaker']}: \"{turn['text']}\"")
                history_str = "\n".join(history_text_list[-6:]) # last 6 messages

                system_prompt = f"""Eres {twin_name}, participante en un grupo focal cualitativo de mototaxistas en Lima para inDrive.
Perfil: {profile.get('descripcion_corta')}
Lenguaje: {', '.join(profile.get('lenguaje_caracteristico', []))}

REGLAS DEL FOCUS GROUP:
1. Habla directamente a tus compañeros mototaxistas y al moderador en un debate fluido.
2. Si un compañero dijo algo en las intervenciones anteriores, responde o reacciona a su comentario (ej. 'Como dice el colega...', 'Yo discrepo ahí porque...', 'En mi caso es distinto...').
3. Mantén absoluta consistencia con tus necesidades ({profile.get('EVIDENCE', {}).get('necesidades', [])}) y tus fricciones ({profile.get('EVIDENCE', {}).get('fricciones', [])}).
4. Usa modismos peruanos de mototaxista ('chamba', 'carrera', 'cerro', 'tarifa', 'zona picante', 'soat').
"""

                user_prompt = f"""TEMA DEL FOCUS GROUP: "{topic}"

HISTORIAL RECIENTE DEL DEBATE (Lo que han dicho los otros participantes):
{history_str}

EVIDENCIA RECUPERADA DE TU EXPERIENCIA CUALITATIVA:
{[e['text_snippet'] for e in retrieved_ev]}

Instrucción: Entrega tu intervención para la Ronda {round_idx}. Sé conciso (2 a 4 oraciones) pero enfático en defender tu postura frente a los demás.
"""

                # Handle mock fallback vs LLM
                if isinstance(self.provider, MockLocalProvider):
                    if twin_id == "twin_a_autonomo_precavido":
                        if round_idx == 1:
                            reply_text = f"Miren colegas, sobre '{topic}', yo soy claro: lo primero es la seguridad y la tarifa justa. Si a mí la app me quiere mandar a ciegas a Collique o a un cerro sin saber qué voy a cobrar, yo no me meto. Mi moto sufre en la subida."
                        else:
                            reply_text = f"Escuchando a los compañeros, yo discrepo con andar corriendo a ciegas por un bono. De qué te sirve hacer 20 carreras si en una te roban la moto o rompes el amortiguador en la trocha? Prefiero 10 carreras bien pagadas y con destino claro."
                    elif twin_id == "twin_b_volumen_bonos":
                        if round_idx == 1:
                            reply_text = f"Yo lo veo distinto, Marcos. Para mí el tiempo es oro en el tráfico. Si te pones a negociar y esperar que el cliente te acepte, pierdes 10 minutos. Yo prefiero que Yango o la app me tire el viaje directo, suene y salga. Sacas tus bonos del día y te vas a casa con tu plata segura."
                        else:
                            reply_text = f"Colega, el tema es la rapidez. Si estás en horas punta, el volumen es lo que te deja ganar dinero real. Los bonos de S/ 50 extra compensan cualquier tramo corto. El regateo te quita ritmo de chamba."
                    else: # twin_c
                        if round_idx == 1:
                            reply_text = f"Bueno, yo les digo la verdad: yo no me mato corriendo por bonos ni ando peleando tarifas largas. Yo chambeo tranquilo en mi paradero y con la calle. Si la app me bota un viaje corto y seguro cerca de mi zona para no regresar vacío, bienvenido; si no, me quedo en mi paradero."
                        else:
                            reply_text = f"Coincido en que no vale la pena estresarse. Yo si veo una zona muy picante o de noche, simplemente apago el aplicativo y me voy a mi casa. La tranquilidad de regresar sano a la familia no tiene precio."
                else:
                    reply_text = self.provider.generate(system_prompt, user_prompt)

                transcript.append({
                    "speaker": twin_name,
                    "twin_id": twin_id,
                    "role": "participant",
                    "text": reply_text,
                    "round": round_idx,
                    "evidence": retrieved_ev
                })

        # Step 3: Moderator Synthesis
        synth_system = "Eres el Investigador Senior / Moderador de CRIBA encargarte de sintetizar un Focus Group Cualitativo para el equipo de Producto de inDrive."
        full_transcript_str = "\n".join([f"[{t['speaker']} - Ronda {t['round']}]: {t['text']}" for t in transcript])
        synth_user = f"""Sintetiza el siguiente Focus Group cualitativo sobre el tema: "{topic}"

TRANSCRIPCIÓN COMPLETA DEL DEBATE:
{full_transcript_str}

Entrega una síntesis ejecutiva dividida en:
1. 🤝 PUNTOS DE ACUERDO: En qué coinciden los distintos perfiles de conductores.
2. ⚡ PRINCIPALES TENSIONES Y DISCREPANCIAS: Dónde chocan sus prioridades (ej. Tarifas vs Bonos vs Paradero).
3. 💡 RECOMENDACIONES ESTRATÉGICAS PARA INDRIVE: Qué acciones concretas de producto o tarifa debería tomar inDrive para solucionar la oferta en Lima.
"""

        if isinstance(self.provider, MockLocalProvider):
            synthesis_text = f"""### 📝 Síntesis Cualitativa del Moderador (CRIBA x inDrive)

#### 🤝 1. PUNTOS DE ACUERDO
- **Seguridad e Integridad del Vehículo**: Todos los conductores coinciden en que la seguridad personal y evitar el deterioro mecánico en zonas de alto riesgo son prioridades infranqueables.
- **Odio a los Tiempos Muertos**: Todos rechazan esperar innecesariamente sin generar ingresos o gastar combustible en vano.

#### ⚡ 2. PRINCIPALES TENSIONES Y DISCREPANCIAS
- **Modelo de Asignación vs Oferta Manual**: *Marcos (Autónomo)* exige visibilidad previa y negociación manual; *Julio (Volumen)* demanda asignación directa e inmediatez; *Carlos (Relajado)* prefiere tramos cortos sin salir de su zona habitual.
- **Bonos vs Tarifa Base**: Fuerte tensión entre quienes persiguen bonos de cumplimiento diario (Yango) vs quienes rechazan la presión de metas y exigen tarifa justa directa por carrera (inDrive).

#### 💡 3. RECOMENDACIONES ESTRATÉGICAS PARA INDRIVE
- **Fidelización en Lima Norte/Sur**: Ofrecer un modelo híbrido en inDrive: permitir a conductores de volumen activar un 'modo rápido de asignación directa con bonos cortos' mientras se preserva el modelo de contraoferta transparente para conductores precavidos.
- **Filtro de Zonas de Riesgo**: Implementar alertas automáticas de terreno/pendiente y zona peligrosa para evitar que los conductores cancelen viajes por miedo.
"""
        else:
            synthesis_text = self.provider.generate(synth_system, synth_user)

        return {
            "topic": topic,
            "rounds": num_rounds,
            "transcript": transcript,
            "synthesis": synthesis_text
        }

if __name__ == "__main__":
    fg = FocusGroupEngine()
    print("Testing Focus Group debate...")
    res = fg.run_focus_group("¿Cómo resolver la escasez de conductores en Lima Norte y Sur?", ["twin_a_autonomo_precavido", "twin_b_volumen_bonos", "twin_c_oportunista_relajado"], num_rounds=2)
    print("MESSAGES GENERATED:", len(res["transcript"]))
    print("SYNTHESIS SNIPPET:", res["synthesis"].encode('ascii', errors='ignore').decode()[:200])
