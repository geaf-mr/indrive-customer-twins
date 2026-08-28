"""
Decoupled LLM Provider layer.
Supports 'mock' (offline), 'openai', and 'gemini' via lightweight HTTP requests.
Reads config from both environment variables (.env) and Streamlit Secrets.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def get_env_or_secret(key: str, default: str = None) -> str:
    """Helper to fetch config from os.environ first, then Streamlit Secrets."""
    val = os.getenv(key)
    if val:
        return str(val).strip()
    try:
        import streamlit as st
        if key in st.secrets:
            sec_val = st.secrets[key]
            if isinstance(sec_val, str):
                return sec_val.strip()
            elif isinstance(sec_val, dict):
                return str(sec_val.get("key", list(sec_val.values())[0])).strip()
            return str(sec_val).strip()
    except Exception:
        pass
    return default

class BaseLLMProvider:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

class MockLocalProvider(BaseLLMProvider):
    """Zero API key offline provider for demonstration and local testing."""
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        twin_name = "el conductor"
        if "Marcos" in system_prompt or "twin_a" in system_prompt:
            twin_name = "Marcos (Autónomo y Precavido)"
        elif "Julio" in system_prompt or "twin_b" in system_prompt:
            twin_name = "Julio (Volumen y Bonos)"
        elif "Carlos" in system_prompt or "twin_c" in system_prompt:
            twin_name = "Carlos (Oportunista Relajado)"

        if "SIN EVIDENCIA SUFICIENTE" in user_prompt or "UNSUPPORTED" in user_prompt:
            return (
                f"Como {twin_name}, debo ser claro: El material disponible de la investigación cualitativa no permite inferir con suficiente confianza "
                f"cómo reaccionaría mi perfil ante este punto específico. Sin embargo, como hipótesis exploratoria basada en mi patrón general..."
            )

        is_exploratory = "EXPLORATORY" in user_prompt.upper() or "HIPOTETICO" in user_prompt.upper()
        prefix = "[EXPLORATORY SCENARIO] " if is_exploratory else ""

        if "Marcos" in twin_name:
            return (
                f"{prefix}Mira, para mí lo primordial es el control y la seguridad. Yo necesito ver exactamente a dónde va el pasajero antes de mover la mototaxi, "
                f"especialmente si es hacia partes altas de Comas como Collique o Añashuayco. Además, inDrive me gusta porque me deja ofertar mi propia tarifa: "
                f"si el tramo es empinado o hay trocha, yo ajusto el precio porque la moto sufre y gasta más gasolina. No aceptaría una tarifa fija impuesta a ciegas."
            )
        elif "Julio" in twin_name:
            return (
                f"{prefix}Para mí lo que importa es la rapidez y sacar la cuota del día sin perder tiempo. Yo prefiero que la app me asigne el viaje directo, "
                f"como hace Yango, porque estar ofreciendo precio y esperando a que el cliente acepte me quita minutos valiosos. A mí me mueven los bonos y los "
                f"garantizados diarios: si cumplo mis 15 o 20 viajes me llevo mi dinero extra seguro a casa."
            )
        else:
            return (
                f"{prefix}Yo manejo la moto a mi ritmo, más que nada para complementar mis ingresos. Si la app me ofrece buena tarifa o me queda de paso, acepto el viaje. "
                f"No me estreso por metas diarias ni por andar ruteando todo el día."
            )

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = get_env_or_secret("OPENAI_API_KEY")
        self.model = get_env_or_secret("OPENAI_MODEL", "gpt-4o-mini")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY missing.")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"OpenAI Error ({response.status_code}): {response.text}")
                return MockLocalProvider().generate(system_prompt, user_prompt)
        except Exception as e:
            print(f"OpenAI Exception: {e}")
            return MockLocalProvider().generate(system_prompt, user_prompt)

class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = get_env_or_secret("GEMINI_API_KEY")
        self.model = get_env_or_secret("GEMINI_MODEL", "gemini-1.5-flash")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key or not isinstance(self.api_key, str) or len(self.api_key.strip()) < 5:
            return MockLocalProvider().generate(system_prompt, user_prompt)

        models_to_try = [self.model, "gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
        models_to_try = list(dict.fromkeys(models_to_try))

        last_error = ""

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key.strip()}"
            headers = {"Content-Type": "application/json"}
            
            # Formato Estándar de Gemini REST API
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"INSTRUCCIONES DEL SISTEMA:\n{system_prompt}\n\nPREGUNTA DEL USUARIO:\n{user_prompt}"}
                        ]
                    }
                ],
                "generationConfig": {"temperature": 0.3}
            }
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=25)
                if response.status_code == 200:
                    res_data = response.json()
                    candidates = res_data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]

                last_error = f"HTTP {response.status_code}: {response.text[:150]}"
            except Exception as e:
                last_error = str(e)

        # Fallback a respuesta local para que NUNCA colapse la aplicación
        print(f"Gemini API Error: {last_error}")
        fallback_resp = MockLocalProvider().generate(system_prompt, user_prompt)
        return f"{fallback_resp}\n\n*(Nota de diagnóstico: La API de Gemini no respondió ({last_error}). Se generó la respuesta cualitativa con el motor local de respaldo.)*"

def get_llm_provider() -> BaseLLMProvider:
    provider_type = get_env_or_secret("LLM_PROVIDER", "mock").lower().strip()
    if provider_type == "openai":
        return OpenAIProvider()
    elif provider_type == "gemini":
        return GeminiProvider()
    else:
        return MockLocalProvider()
