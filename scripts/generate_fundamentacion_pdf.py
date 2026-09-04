"""
Script to generate the updated Fundamentacion_Metodologica_Digital_Twins_inDrive.pdf
including Section 5: Protocolos de Confidencialidad y Gobernanza de Datos en IA.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header line
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 750, 558, 750)
        
        self.drawString(54, 755, "CRIBA RESEARCH • Digital Customer Twins (inDrive Perú)")
        
        # Footer line
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Confidencial • Preparado para CRIBA Research & inDrive")
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 32, page_text)
        self.restoreState()

def build_pdf(filename="Fundamentacion_Metodologica_Digital_Twins_inDrive.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#10B981"),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        leftIndent=12,
        spaceAfter=4
    )

    meta_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )
    
    meta_val_style = ParagraphStyle(
        'MetaValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569")
    )

    story = []

    # Document Header
    story.append(Spacer(1, 10))
    story.append(Paragraph("FUNDAMENTACIÓN METODOLÓGICA Y TRAZABILIDAD", title_style))
    story.append(Paragraph("Digital Customer Twins • Estudio Cualitativo de Mototaxis (inDrive, Lima)", subtitle_style))

    # Metadata Table
    meta_data = [
        [Paragraph("Proyecto:", meta_style), Paragraph("Digital Customer Twins (inDrive Perú)", meta_val_style),
         Paragraph("Fecha:", meta_style), Paragraph("Septiembre 2026", meta_val_style)],
        [Paragraph("Metodología:", meta_style), Paragraph("Grounded Qualitative AI & RAG Local", meta_val_style),
         Paragraph("Muestra:", meta_style), Paragraph("25 Entrevistas en Profundidad", meta_val_style)],
        [Paragraph("Objetivo:", meta_style), Paragraph("Sustento analítico y trazabilidad empírica", meta_val_style),
         Paragraph("Estado:", meta_style), Paragraph("Entregable Técnico de Validación", meta_val_style)]
    ]
    t_meta = Table(meta_data, colWidths=[65, 200, 50, 189])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#F1F5F9")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1
    story.append(Paragraph("1. Marco Metodológico y Procesamiento del Corpus", h2_style))
    story.append(Paragraph("El desarrollo del sistema de Digital Customer Twins responde a la necesidad de transformar el material cualitativo de campo en un modelo analítico interactivo y explorable en tiempo real, superando el carácter estático de las presentaciones tradicionales. El sistema no genera conocimiento abstracto ni especulativo; opera estrictamente sobre la evidencia recolectada en el trabajo de campo.", body_style))
    
    story.append(Paragraph("• <b>Base empírica primaria:</b> El corpus del sistema está constituido por 25 transcripciones integrales de entrevistas en profundidad realizadas a conductores de mototaxis en zonas clave de Lima (Comas, Collique, Añashuayco), además de las guías de moderación y el informe de investigación.", bullet_style))
    story.append(Paragraph("• <b>Estructuración e ingesta:</b> Cada entrevista fue fragmentada e indexada preservando metadatos clave como ID de participante, distrito, antigüedad en el rubro y temas abordados.", bullet_style))
    story.append(Paragraph("• <b>Matriz de evidencia estructurada:</b> Se construyó una matriz relacional que vincula temas críticos (tarifas, comisiones, zonas peligrosas, bonos) con los testimonios empíricos de los conductores.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 2
    story.append(Paragraph("2. Calibración de los Digital Customer Twins", h2_style))
    story.append(Paragraph("A partir del análisis inductivo de las transcripciones, se sintetizaron tres perfiles sintéticos diferenciados que representan los arquetipos dominantes de la muestra:", body_style))

    twins_table_data = [
        [Paragraph("<b>Perfil Sintético</b>", meta_style), Paragraph("<b>Foco Operativo y Actitudinal</b>", meta_style), Paragraph("<b>Patrón de Comportamiento Dominante</b>", meta_style)],
        [Paragraph("<b>Twin A</b><br/>Disciplined Hard Work<br/>(Marcos)", meta_val_style), Paragraph("Control de margen neto diario y predictibilidad.", meta_val_style), Paragraph("Exige conocer el destino antes de aceptar la carrera. Rechaza viajes a zonas peligrosas (cerros/sin luz) y prioriza tarifas justas sobre volumen.", meta_val_style)],
        [Paragraph("<b>Twin B</b><br/>Tactical Cash Optimizer<br/>(Julio)", meta_val_style), Paragraph("Velocidad de rotación y flujo continuo de caja.", meta_val_style), Paragraph("Orientado a la acumulación rápida de efectivo. Maximiza bonos diarios por cuota de viajes y negocia tarifas de forma agresiva.", meta_val_style)],
        [Paragraph("<b>Twin C</b><br/>Low-Pressure Flexibles<br/>(Carlos)", meta_val_style), Paragraph("Flexibilidad horaria y reducción del estrés.", meta_val_style), Paragraph("Combina el paradero físico tradicional con solicitudes de la app. Trabaja a su propio ritmo y evita jornadas extensas o competitivas.", meta_val_style)]
    ]
    t_twins = Table(twins_table_data, colWidths=[120, 134, 250])
    t_twins.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F0FDF4")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#A7F3D0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_twins)
    story.append(Spacer(1, 10))

    # Section 3
    story.append(Paragraph("3. Arquitectura de Anclaje a la Evidencia (Grounding y RAG Local)", h2_style))
    story.append(Paragraph("El principal diferencial metodológico de la herramienta es su mecanismo de anclaje (grounding), diseñado para prevenir alucinaciones o respuestas genéricas fuera de contexto:", body_style))
    story.append(Paragraph("1. <b>Recuperación Semántica Acotada:</b> Ante cada consulta del usuario, un motor de búsqueda cualitativa (TF-IDF + Cosine Similarity) extrae de forma prioritaria los fragmentos de transcripción más pertinentes del corpus.", bullet_style))
    story.append(Paragraph("2. <b>Trazabilidad Explícita:</b> Cada respuesta emitida por un Twin incluye una ventana de trazabilidad que muestra la cita textual exacta, el participante y el código de la entrevista de origen (ej. EP01, EP05, EP18).", bullet_style))
    story.append(Paragraph("3. <b>Detección de Límites de Información (Out-of-Scope Protection):</b> Si se le formula una pregunta al Twin sobre un tema no abordado en el trabajo de campo (ej. vehículos eléctricos), el sistema emite una advertencia formal notificando que el material disponible no contiene evidencia suficiente.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 4
    story.append(Paragraph("4. Modos de Análisis y Aplicabilidad Estratégica", h2_style))
    story.append(Paragraph("• <b>Modo Chat Individual:</b> Permite profundizar en la psicología y motivaciones de un perfil específico frente a preguntas puntuales.", bullet_style))
    story.append(Paragraph("• <b>Modo Matriz Side-by-Side:</b> Permite ingresar un cambio de propuesta comercial (ej. modificación de comisión o filtro de seguridad) y contrastar la reacción simultánea de los perfiles lado a lado con disparadores de 1-clic.", bullet_style))
    story.append(Paragraph("• <b>Modo Focus Group Interactivo:</b> Orquesta un debate simulado entre los tres Twins sobre problemáticas complejas con síntesis cualitativa del moderador.", bullet_style))
    story.append(Paragraph("• <b>Modo Cuadros & Matriz:</b> Ofrece tablas sintetizadas de 7 dimensiones estratégicas y comparativa de marcas exportables a Excel/CSV.", bullet_style))
    story.append(Spacer(1, 10))

    # Section 5 (Confidencialidad y Gobernanza)
    story.append(KeepTogether([
        Paragraph("5. Protocolos de Confidencialidad, Gobernanza de Datos y Seguridad en IA", h2_style),
        Paragraph("Garantizar el cumplimiento de las normativas de protección de datos y la salvaguarda de secretos comerciales constituye un pilar estructural de la plataforma. La arquitectura de seguridad del proyecto contempla dos niveles operativos actuales (MVP) y dos vías de escalamiento corporativo para inDrive:", body_style),
        Paragraph("1. <b>Anonimización en Origen (Nivel MVP Aplicado):</b> El 100% de los datos de identificación personal (PII) —nombres de entrevistados, números de teléfono, DNI y direcciones exactas— fueron purgados de las transcripciones y reemplazados por códigos anonimizados estandarizados (ej. <i>[PARTICIPANTE_01]</i>), eliminando cualquier riesgo de filtración de datos personales.", bullet_style),
        Paragraph("2. <b>Procesamiento Híbrido y Motor Cualitativo Local (Nivel MVP Aplicado):</b> La plataforma cuenta con un motor cualitativo local propio (TF-IDF / Búsqueda Semántica local) que consulta el corpus directamente en el servidor sin depender de enviar información sensible a servicios externos de IA.", bullet_style),
        Paragraph("3. <b>Escalamiento a APIs Empresariales (Opción Enterprise Futura):</b> Para un despliegue corporativo a escala, la plataforma permite conectar conectores comerciales (Google Vertex AI / OpenAI Enterprise) amparados por contratos de no-retención de datos (<i>Zero Data Retention</i>).", bullet_style),
        Paragraph("4. <b>Servidor Privado Dedicado On-Premise (Opción Enterprise Futura):</b> En caso de que inDrive exija aislamiento absoluto sobre sus datos estratégicos, la solución permite montarse en un servidor privado dedicado (VPS/VPC en AWS, GCP o Azure) ejecutando modelos de código abierto (Open Source) en un entorno 100% <i>Air-Gapped</i> sin conexión externa.", bullet_style),
        Spacer(1, 8),
        Paragraph("<b>Principio de Rigurosidad Quali-AI & Privacidad:</b><br/><i>\"Un Digital Customer Twin protege la privacidad de los participantes en origen y garantiza la confidencialidad estratégica del cliente, permitiendo que los equipos de Producto exploren evidencia real sin exponer datos sensibles.\"</i>", ParagraphStyle('QuoteCustom', parent=body_style, fontName='Helvetica-Oblique', fontSize=9, textColor=colors.HexColor("#065F46"), backColor=colors.HexColor("#ECFDF5"), borderColor=colors.HexColor("#A7F3D0"), borderWidth=0.5, borderPadding=6))
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    build_pdf()
