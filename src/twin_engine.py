"""
Digital Customer Twin Execution Engine.
Manages context building, retrieval pipeline, grounding checks, and agent responses.
"""

import os
import sys
import yaml
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval import LocalRetriever
from src.llm_provider import get_llm_provider, BaseLLMProvider

UNSUPPORTED_FALLBACK_PHRASE = "El material disponible no permite inferir con suficiente confianza cómo reaccionaría este perfil ante esta situación."

class DigitalTwinEngine:
    def __init__(self, profiles_dir: str = "profiles"):
        self.retriever = LocalRetriever()
        self.provider: BaseLLMProvider = get_llm_provider()
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self._load_profiles(profiles_dir)

    def _load_profiles(self, profiles_dir: str):
        if not os.path.exists(profiles_dir):
            return
        for fname in os.listdir(profiles_dir):
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                fpath = os.path.join(profiles_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    pdata = yaml.safe_load(f)
                    pid = pdata.get("id")
                    if pid:
                        self.profiles[pid] = pdata

    def get_profile(self, twin_id: str) -> Dict[str, Any]:
        return self.profiles.get(twin_id, {})

    def ask(self, twin_id: str, question: str, is_exploratory: bool = False) -> Dict[str, Any]:
        """
        Execute full Digital Twin pipeline:
        1. Retrieve relevant evidence
        2. Check profile unknown topics / grounding thresholds
        3. Build system & user prompts with strict evidence separation
        4. Generate response
        5. Return response + used evidence metadata
        """
        profile = self.get_profile(twin_id)
        if not profile:
            return {
                "response": f"Perfil '{twin_id}' no encontrado.",
                "evidence_used": [],
                "grounded": False,
                "is_exploratory": is_exploratory
            }

        # Step 1: Retrieve evidence
        retrieved = self.retriever.retrieve(question, profile_affinity=twin_id, top_k=4)

        # Step 2: Grounding & Unknown check
        unknown_topics = profile.get("UNKNOWN", {}).get("temas_sin_evidencia", [])
        
        # Simple keyword matching against explicitly declared unsupported topics
        is_unsupported = False
        for unk in unknown_topics:
            words = [w for w in unk.lower().split() if len(w) > 4]
            if words and any(w in question.lower() for w in words):
                is_unsupported = True
                break

        # Check maximum retrieval score threshold
        max_score = max([r["score"] for r in retrieved]) if retrieved else 0.0
        if max_score < 0.02 and not is_unsupported:
            # Low relevance match
            is_unsupported = True

        if is_unsupported and not is_exploratory:
            response_text = (
                f"{UNSUPPORTED_FALLBACK_PHRASE}\n\n"
                f"*(Nota analítica: Este tema no fue explorado explícitamente en el corpus de entrevistas cualitativas para este perfil.)*"
            )
            return {
                "response": response_text,
                "evidence_used": [],
                "grounded": False,
                "is_unsupported": True,
                "is_exploratory": False
            }

        # Step 3: Build Prompt Context
        system_prompt = f"""Eres un Digital Customer Twin sintético derivado de una investigación cualitativa real para inDrive con mototaxistas en Perú.
Tu perfil interno es: {profile.get('nombre_interno')}
Descripción: {profile.get('descripcion_corta')}
Lenguaje característico: {', '.join(profile.get('lenguaje_caracteristico', []))}

REGLAS DE GROUNDING Y COMPORTAMIENTO:
1. Responde SIEMPRE desde la perspectiva de tu perfil manteniendo consistencia.
2. Fundamenta tus opiniones estrictamente en la evidencia cualitativa disponible.
3. Distingue claramente entre:
   - HECHOS / EVIDENCIA DIRECTA: Lo expresado en las entrevistas.
   - INTERPRETACIÓN ANALÍTICA: La síntesis de tus actitudes y drivers.
   - HIPÓTESIS EXPLORATORIA: Si la pregunta es un escenario hipotético, márcalo explícitamente como [EXPLORATORY SCENARIO].
4. Mantén el tono, jerga y lenguaje natural de un mototaxista peruano (ej. 'chamba', 'carrera', 'tarifa justo', 'zona picante', 'cerro').
"""

        evidence_str_list = []
        for i, item in enumerate(retrieved, 1):
            evidence_str_list.append(
                f"Evidencia #{i} [{item['transcript_id']} - {item['interviewee_label']}]:\n"
                f"\"...{item['text_snippet']}...\"\n"
                f"Interpretación: {item['interpretacion']}\n"
            )

        user_prompt = f"""PREGUNTA DEL USUARIO: "{question}"

CONTEXTO DE EVIDENCIA RECUPERADA DE LAS ENTREVISTAS:
{"".join(evidence_str_list)}

SÍNTESIS DEL PERFIL (YAML):
- Necesidades: {profile.get('EVIDENCE', {}).get('necesidades', [])}
- Drivers: {profile.get('EVIDENCE', {}).get('drivers', [])}
- Fricciones: {profile.get('EVIDENCE', {}).get('fricciones', [])}
- Interpretación analítica: {profile.get('INTERPRETATION', {}).get('perfil_analitico')}

Instrucciones finales: Responde de forma concisa, directa y natural como {profile.get('nombre_interno')}.
"""
        if is_exploratory:
            user_prompt += "\nNOTA: Esta pregunta representa un ESCENARIO HIPOTÉTICO NO PREGUNTADO LITERALMENTE. Comienza tu respuesta con '[EXPLORATORY SCENARIO]' y formula una hipótesis plausible basada en tus drivers."

        if is_unsupported:
            user_prompt += "\nNOTA: Existe muy baja evidencia sobre este tema. Si respondes, indica primero: '" + UNSUPPORTED_FALLBACK_PHRASE + "' y luego plantea una breve hipótesis explícita."

        # Step 4: Generate response
        response_text = self.provider.generate(system_prompt, user_prompt)

        return {
            "response": response_text,
            "evidence_used": retrieved,
            "grounded": not is_unsupported,
            "is_unsupported": is_unsupported,
            "is_exploratory": is_exploratory
        }

if __name__ == "__main__":
    engine = DigitalTwinEngine()
    print("Testing Twin A response...")
    res_a = engine.ask("twin_a_autonomo_precavido", "¿Por qué prefieres negociar la tarifa?")
    print("TWIN A RESPONSE:", res_a["response"])
    print("EVIDENCE COUNT:", len(res_a["evidence_used"]))
