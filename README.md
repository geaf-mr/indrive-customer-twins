# Digital Customer Twins MVP (inDrive Qualitative Research)

MVP funcional de **Digital Customer Twins** derivado de forma sistemática a partir de 25 transcripciones de entrevistas en profundidad y guías de moderación realizadas para **inDrive** con conductores de mototaxi en Lima, Perú (Comas, Collique, Añashuayco).

El sistema permite pasar de informes cualitativos estáticos a **perfiles sintéticos interactivos y explorables**, capaces de responder preguntas, simular escenarios comerciales y justificar sus posturas con **trazabilidad directa a los transcripts originales**.

---

## 🚀 Inicio Rápido

### 1. Requisitos Previos
- Python 3.9+
- Dependencias listadas en `requirements.txt` (Streamlit, scikit-learn, python-docx, PyYAML, python-dotenv).

### 2. Instalación de Dependencias
```bash
pip install streamlit scikit-learn python-docx PyYAML python-dotenv pandas numpy requests
```

### 3. Configuración del Proveedor LLM (`.env`)
El sistema está diseñado **local-first** y funciona out-of-the-box sin necesidad de una API key externa utilizando el motor local offline (`mock`).

Para utilizar modelos externos como OpenAI o Gemini:
1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edita `.env`:
   ```env
   # Opciones: 'mock' (offline sin API key), 'openai', o 'gemini'
   LLM_PROVIDER=mock

   # Si usas OpenAI:
   OPENAI_API_KEY=tu_api_key_aqui
   OPENAI_MODEL=gpt-4o-mini

   # Si usas Gemini:
   GEMINI_API_KEY=tu_api_key_aqui
   GEMINI_MODEL=gemini-1.5-flash
   ```

### 4. Ejecutar la Aplicación Web
```bash
streamlit run app.py
```
Abre tu navegador en `http://localhost:8501`.

---

## 📁 Estructura de Carpetas

```
Indrive/
├── data/                       # [CONFIDENCIAL - GITIGNORED]
│   ├── raw/
│   │   ├── transcripts/        # Archivos .docx de transcripciones
│   │   ├── guides/             # Guías de discusión de la investigación
│   │   ├── brief/              # Briefing y objetivos del estudio
│   │   └── reports/            # Presentaciones o entregables previos
│   └── processed/
│       └── corpus.json         # Corpus indexado y fragmentado
├── evidence/
│   └── evidence_matrix.json    # Matriz estructurada: Tema -> Patrón -> Citas -> Interpretación
├── profiles/
│   ├── twin_a_autonomo_precavido.yaml  # Definición YAML del Twin A (Marcos)
│   └── twin_b_volumen_bonos.yaml       # Definición YAML del Twin B (Julio)
├── docs/
│   └── candidate_profiles.md   # Análisis cualitativo de perfiles candidatos
├── src/
│   ├── ingestion.py            # Ingesta y fragmentación de archivos .docx
│   ├── synthesis.py            # Generador de la matriz de evidencia cualitativa
│   ├── retrieval.py            # Motor local de búsqueda vectorial TF-IDF + Cosine Similarity
│   ├── llm_provider.py         # Capa desacoplada de LLM (Mock / OpenAI / Gemini)
│   ├── twin_engine.py          # Motor de ejecución del Digital Twin y Grounding
│   └── evaluation.py           # Suite automatizada de pruebas y validación
├── reports/
│   └── validation_report.md    # Reporte de validación de calidad y trazabilidad
├── app.py                      # Interfaz web interactiva en Streamlit
├── VALUE_PROPOSITION.md        # Argumentación comercial y de valor para CRIBA / inDrive
├── README.md                   # Documentación principal del sistema
├── .env.example                # Plantilla de variables de entorno
└── .gitignore                  # Protección estricta de datos confidenciales (/data/)
```

---

## 🛠️ Guía Operativa

### ¿Cómo cargar nuevos transcripts?
1. Coloca los archivos `.docx` de las nuevas entrevistas en la carpeta `data/raw/transcripts/`.
2. Ejecuta la reingesta y reconstrucción de corpus y evidencia:
   ```bash
   python src/ingestion.py
   python src/synthesis.py
   ```

### ¿Cómo modificar las fichas de los Twins?
Los perfiles de los Digital Twins están definidos en archivos **YAML fácilmente editables** dentro de `/profiles/`:
- `profiles/twin_a_autonomo_precavido.yaml`
- `profiles/twin_b_volumen_bonos.yaml`

Cada archivo distingue estrictamente tres secciones fundamentales:
- **`EVIDENCE`**: Hechos y citas directas de las entrevistas.
- **`INTERPRETATION`**: Síntesis analítica realizada por el investigador.
- **`UNKNOWN`**: Temas sobre los cuales la evidencia cualitativa es insuficiente o nula.

### ¿Cómo agregar un nuevo Twin?
1. Crea un nuevo archivo YAML en `profiles/`, por ejemplo: `profiles/twin_c_oportunista.yaml`.
2. Asigna un `id` único (ej. `twin_c_oportunista`) y completa las dimensiones de `EVIDENCE`, `INTERPRETATION` y `UNKNOWN`.
3. El motor `DigitalTwinEngine` detectará automáticamente el nuevo perfil al reiniciar o recargar la aplicación.

---

## 🔍 Recuperación y Grounding (RAG Local)

El pipeline de respuesta de cada Digital Customer Twin sigue un flujo estricto:

```
[Pregunta del Usuario] 
        ↓
[Digital Twin Seleccionado] 
        ↓
[Búsqueda Vectorial Local (TF-IDF + Cosine Similarity)] ──> Recupera fragmentos de evidence_matrix y corpus.json
        ↓
[Filtro de Grounding y Verificación de UNKNOWN] 
        ↓  (Si la evidencia es insuficiente) ──> Emitir advertencia: "El material disponible no permite inferir..."
        ↓  (Si es escenario hipotético) ───────> Etiquetar como: [EXPLORATORY SCENARIO]
[Construcción de Prompt Contextualizado]
        ↓
[Generación de Respuesta por el LLM Provider]
        ↓
[Despliegue en UI con Panel Interactivo de Evidencia Sustentante]
```

### Privacidad y Confidencialidad
- La arquitectura es **Local-First**.
- El directorio `/data/` está ignorado en `.gitignore`.
- Al utilizar proveedores LLM externos (OpenAI / Gemini), el sistema **NUNCA sube el corpus completo**: envía únicamente los 3 a 5 fragmentos mínimos de evidencia requeridos para responder la consulta específica.

---

## 📊 Evaluación y Validación Automatizada

Para ejecutar la suite de pruebas de calidad metodológica (Groundedness, Consistencia, Diferenciación, Unsupported Inference y Trazabilidad):

```bash
python src/evaluation.py
```
El reporte detallado se actualizará en `reports/validation_report.md`.

---

## ⚠️ Limitaciones Metodológicas

1. **Naturaleza Cualitativa**: Los Digital Customer Twins representan síntesis cualitativas explorares de patrones encontrados en 25 entrevistas. No constituyen una muestra probabilística ni un modelo cuantitativo estadístico.
2. **Límites de Inferencia**: El agente reconoce explícitamente cuando una consulta supera la evidencia recolectada y no debe tratarse una hipótesis exploratoria como un hallazgo cualitativo consolidado.
3. **Modelos Locales vs APIs Externa**: Para obtener respuestas con lenguaje natural hiper-fluido en jerga peruana, se recomienda configurar una API Key de OpenAI o Gemini en `.env`, aunque la app cuenta con un motor `mock` 100% funcional para demostraciones sin conexión.
