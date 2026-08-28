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
        return val
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
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
        else:
            return (
                f"{prefix}Para mí lo que importa es la rapidez y sacar la cuota del día sin perder tiempo. Yo prefiero que la app me asigne el viaje directo, "
                f"como hace Yango, porque estar ofreciendo precio y esperando a que el cliente acepte me quita minutos valiosos. A mí me mueven los bonos y los "
                f"garantizados diarios: si cumplo mis 15 o 20 viajes me llevo mi dinero extra seguro a casa."
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
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise RuntimeError(f"OpenAI API Error ({response.status_code}): {response.text}")

class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = get_env_or_secret("GEMINI_API_KEY")
        self.model = get_env_or_secret("GEMINI_MODEL", "gemini-1.5-flash")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY missing.")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Array of candidate models to try if default model fails
        models_to_try = [self.model, "gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
        # Remove duplicates while preserving order
        models_to_try = list(dict.fromkeys(models_to_try))

        last_error = ""

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "system_instruction": {
                    "parts": [{"text": system_prompt}]
                },
                "contents": [
                    {
                        "parts": [{"text": user_prompt}]
                    }
                ],
                "generationConfig": {"temperature": 0.3}
            }
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    res_data = response.json()
                    candidates = res_data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                
                # If v1beta with system_instruction returned 400, fallback payload format
                fallback_payload = {
                    "contents": [
                        {
                            "parts": [{"text": f"INSTRUCCIONES DEL SISTEMA:\n{system_prompt}\n\nPREGUNTA/CONTEXTO DEL USUARIO:\n{user_prompt}"}]
                        }
                    ],
                    "generationConfig": {"temperature": 0.3}
                }
                response2 = requests.post(url, headers=headers, json=fallback_payload, timeout=30)
                if response2.status_code == 200:
                    res_data = response2.json()
                    candidates = res_data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]

                last_error = f"Status {response.status_code}: {response.text[:200]}"
            except Exception as e:
                last_error = str(e)

        # Fallback if API Key was invalid or quota exceeded, so the app doesn't crash ungracefully
        print(f"Gemini API Error: {last_error}")
        return (
            f"[Error Gemini API - HTTP Details: {last_error}]\n\n"
            f"Por favor verifica que la GEMINI_API_KEY ingresada en Streamlit Secrets sea válida y esté activa en Google AI Studio."
        )

def get_llm_provider() -> BaseLLMProvider:
    provider_type = get_env_or_secret("LLM_PROVIDER", "mock").lower().strip()
    if provider_type == "openai":
        try:
            return OpenAIProvider()
        except Exception as e:
            print(f"Warning: OpenAI provider failed ({e}), falling back to MockLocalProvider.")
            return MockLocalProvider()
    elif provider_type == "gemini":
        try:
            return GeminiProvider()
        except Exception as e:
            print(f"Warning: Gemini provider failed ({e}), falling back to MockLocalProvider.")
            return MockLocalProvider()
    else:
        return MockLocalProvider()
