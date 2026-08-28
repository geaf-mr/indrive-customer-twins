"""
Module for systematic qualitative synthesis and evidence matrix generation.
Maps: tema -> patron -> entrevistados -> evidencia textual -> interpretacion.
Aligned with inDrive BHT Driver Segmentation (Disciplined Hard Work, Tactical Cash Optimizer, Low-Pressure Flexibles).
"""

import json
import os
import re

THEMES_DEFINITIONS = [
    {
        "tema": "Elección y Preferencia de Plataforma (inDrive vs Yango vs Calle)",
        "patrones": [
            {
                "patron_id": "P_IND_01",
                "patron": "Valoración de la negociación manual de tarifa y autonomía (Disciplined Hard Work)",
                "keywords": ["proponer", "contraoferta", "negociar", "tarifa", "libertad", "yo pongo", "tarifa justa"],
                "profile_affinity": "twin_a",
                "interpretacion": "Los conductores estructurados (Disciplined Hard Work / Twin A) valoran inDrive porque les permite ajustar el precio al esfuerzo exigido por el terreno (cerros, trocha) o el tráfico."
            },
            {
                "patron_id": "P_YAN_01",
                "patron": "Preferencia por asignación automática inmediata y bonos (Tactical Cash Optimizer)",
                "keywords": ["automatico", "automática", "directo", "cae rápido", "no pierdo tiempo", "suena y sale", "bono", "garantizado"],
                "profile_affinity": "twin_b",
                "interpretacion": "Los conductores tácticos (Tactical Cash Optimizer / Twin B) prefieren Yango porque la asignación instantánea elimina los tiempos muertos de negociación y acelera el logro de metas diarias de bonos."
            },
            {
                "patron_id": "P_CAL_01",
                "patron": "Preferencia por carreras de paradero formal y calle sin estrés de app (Low-Pressure Flexibles)",
                "keywords": ["paradero", "calle", "tranquilo", "asociación", "sin apuro", "esperar", "horas muertas"],
                "profile_affinity": "twin_c",
                "interpretacion": "Los conductores de bajo estrés (Low-Pressure Flexibles / Twin C) prefieren trabajar en su paradero o recogiendo pasajeros en la calle, activando la app solo en horas muertas o para asegurar el retorno."
            }
        ]
    },
    {
        "tema": "Seguridad y Evaluación de Riesgo de Zona",
        "patrones": [
            {
                "patron_id": "P_SEG_01",
                "patron": "Ver el destino completo antes de aceptar como filtro de seguridad imprescindible",
                "keywords": ["destino", "zona roja", "zona peligrosa", "collique", "añashuayco", "cerro", "peligro", "robo"],
                "profile_affinity": "twin_a",
                "interpretacion": "Ver el punto final es un requisito no negociable para conductores precavidos en zonas de alto riesgo de Comas/cerros, previniendo asaltos o extorsiones."
            },
            {
                "patron_id": "P_SEG_02",
                "patron": "Tolerancia al riesgo por incentivos monetarios rápidos",
                "keywords": ["arriesgar", "meterse", "cuidado", "conozco", "rapido", "bono"],
                "profile_affinity": "twin_b",
                "interpretacion": "Conductores enfocados en maximizar el efectivo diario asumen mayor incertidumbre si los bonos o tarifas compensan la cuota."
            },
            {
                "patron_id": "P_SEG_03",
                "patron": "Evitación total de zonas complicadas y rutas nocturnas de alto riesgo",
                "keywords": ["evito", "no subo", "noche", "tranquilo", "cerca", "conocido"],
                "profile_affinity": "twin_c",
                "interpretacion": "Conductores de baja presión prefieren evitar cualquier viaje que implique tensión, peligro o desplazamientos largos a cerros sin luz."
            }
        ]
    },
    {
        "tema": "Comisiones e Incentivos Económicos",
        "patrones": [
            {
                "patron_id": "P_COM_01",
                "patron": "Percepción de la comisión como pago por servicio que debe mantenerse bajo (10% o menos)",
                "keywords": ["comision", "comisión", "porcentaje", "justo", "descuento", "ganancia", "pagar"],
                "profile_affinity": "twin_a",
                "interpretacion": "El conductor formal considera que la comisión debe ser mínima porque él asume la inversión del vehículo, combustible, mantenimiento y SOAT."
            },
            {
                "patron_id": "P_BON_01",
                "patron": "Fascinación por los bonos de metas diarias y garantizados de app",
                "keywords": ["bono", "bonos", "garantizado", "meta", "completar", "15 viajes", "extra"],
                "profile_affinity": "twin_b",
                "interpretacion": "Los bonos actúan como un motor psicológico que incentiva al conductor a mantenerse activo encadenando carreras en la plataforma."
            }
        ]
    },
    {
        "tema": "Documentación, Regulación y Fiscalización Municipal",
        "patrones": [
            {
                "patron_id": "P_DOC_01",
                "patron": "Cumplimiento estricto de documentos (SOAT, Licencia B2C, Permiso Municipal) para evitar fiscalización",
                "keywords": ["soat", "licencia", "breve", "permiso", "municipal", "fiscalizacion", "papeleta", "policia"],
                "profile_affinity": "twin_a",
                "interpretacion": "El conductor formal valora la tranquilidad de trabajar en regla para no perder el ingreso del día en multas o internamiento del vehículo."
            }
        ]
    }
]

def build_evidence_matrix(corpus_path: str = "data/processed/corpus.json", output_path: str = "evidence/evidence_matrix.json"):
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus file missing at {corpus_path}")

    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    matrix = []

    for theme_info in THEMES_DEFINITIONS:
        tema = theme_info["tema"]
        for pat_info in theme_info["patrones"]:
            patron_id = pat_info["patron_id"]
            patron = pat_info["patron"]
            keywords = pat_info["keywords"]
            affinity = pat_info["profile_affinity"]
            interpretacion = pat_info["interpretacion"]

            matching_evidence = []
            interviewees_set = set()

            for chunk in corpus:
                text_lower = chunk["text"].lower()
                if any(kw in text_lower for kw in keywords):
                    interviewees_set.add(chunk["transcript_id"])
                    if len(matching_evidence) < 6:
                        matching_evidence.append({
                            "transcript_id": chunk["transcript_id"],
                            "interviewee_label": chunk["interviewee_label"],
                            "app_affiliation": chunk["app_affiliation"],
                            "chunk_id": chunk["id"],
                            "evidencia_textual": chunk["text"][:350] + ("..." if len(chunk["text"]) > 350 else "")
                        })

            matrix.append({
                "patron_id": patron_id,
                "tema": tema,
                "patron": patron,
                "profile_affinity": affinity,
                "entrevistados": sorted(list(interviewees_set)),
                "total_menciones": len(interviewees_set),
                "evidencia": matching_evidence,
                "interpretacion": interpretacion
            })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)

    print(f"Built evidence matrix with {len(matrix)} patterns in {output_path}")
    return matrix

if __name__ == "__main__":
    build_evidence_matrix()
