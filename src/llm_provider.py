"""
Decoupled LLM Provider layer.
Supports 'mock' (offline), 'openai', and 'gemini' via lightweight HTTP requests.
Sends ONLY minimal evidence snippets to external APIs for privacy.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class BaseLLMProvider:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

class MockLocalProvider(BaseLLMProvider):
    """Zero API key offline provider for demonstration and local testing."""
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Extract twin name from system prompt if possible
        twin_name = "el conductor"
        if "Marcos" in system_prompt or "twin_a" in system_prompt:
            twin_name = "Marcos (Autónomo y Precavido)"
        elif "Julio" in system_prompt or "twin_b" in system_prompt:
            twin_name = "Julio (Volumen y Bonos)"

        # Check if context contains explicit unsupported marker
        if "SIN EVIDENCIA SUFICIENTE" in user_prompt or "UNSUPPORTED" in user_prompt:
            return (
                f"Como {twin_name}, debo ser claro: El material disponible de la investigación cualitativa no permite inferir con suficiente confianza "
                f"cómo reaccionaría mi perfil ante este punto específico. Sin embargo, como hipótesis exploratoria basada en mi patrón general..."
            )

        # Check if exploratory scenario tag is needed
        is_exploratory = "EXPLORATORY" in user_prompt.upper() or "HIPOTETICO" in user_prompt.upper()
        prefix = "[EXPLORATORY SCENARIO] " if is_exploratory else ""

        # Construct grounded response based on user prompt content
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
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY missing in environment variables.")

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
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY missing in environment variables.")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER PROMPT:\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.3}
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            res_data = response.json()
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise RuntimeError(f"Gemini API Error ({response.status_code}): {response.text}")

def get_llm_provider() -> BaseLLMProvider:
    provider_type = os.getenv("LLM_PROVIDER", "mock").lower().strip()
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
