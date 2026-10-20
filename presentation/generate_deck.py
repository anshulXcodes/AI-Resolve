import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # Theme Colors
    COLOR_BG_DARK = RGBColor(15, 23, 42)      # Slate 900
    COLOR_RED_PRIMARY = RGBColor(185, 28, 28) # Red 700
    COLOR_RED_ACCENT = RGBColor(225, 29, 72)  # Rose 600
    COLOR_TEXT_LIGHT = RGBColor(248, 250, 252)# White / Slate 50
    COLOR_TEXT_MUTED = RGBColor(148, 163, 184)# Slate 400
    COLOR_CARD_DARK = RGBColor(30, 41, 59)    # Slate 800
    COLOR_CARD_LIGHT = RGBColor(255, 255, 255)
    COLOR_TEXT_DARK = RGBColor(15, 23, 42)
    COLOR_BORDER = RGBColor(51, 65, 85)

    def add_bg(slide, dark=True):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_BG_DARK if dark else RGBColor(248, 250, 252)
        shape.line.color.rgb = COLOR_BG_DARK if dark else RGBColor(248, 250, 252)
        return shape

    def add_header(slide, tag, title, dark=True):
        # Tag
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11), Inches(0.4))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = tag.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = RGBColor(248, 113, 113) if dark else COLOR_RED_PRIMARY

        # Title
        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.size = Pt(24)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_LIGHT if dark else COLOR_TEXT_DARK

    # ==================== SLIDE 1: TITLE & COVER ====================
    slide1 = prs.slides.add_slide(blank_layout)
    add_bg(slide1, dark=True)
    
    # Top banner bar
    top_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(0.6))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = RGBColor(20, 25, 40)
    top_bar.line.color.rgb = RGBColor(50, 60, 80)
    tf_top = top_bar.text_frame
    p_top = tf_top.paragraphs[0]
    p_top.text = "BPIT • Reforged '26 • MLH • Unstop • Google Gemma • n8n Track • Hindsight"
    p_top.font.size = Pt(12)
    p_top.font.color.rgb = RGBColor(200, 210, 225)
    p_top.font.bold = True
    p_top.alignment = PP_ALIGN.CENTER

    # Main Title
    t_box = slide1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.733), Inches(2.8))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "RESOLVEAI"
    p.font.size = Pt(56)
    p.font.bold = True
    p.font.color.rgb = RGBColor(239, 68, 68)
    p.alignment = PP_ALIGN.CENTER
    
    p2 = tf1.add_paragraph()
    p2.text = "Intelligent Campus Maintenance Resolution"
    p2.font.size = Pt(24)
    p2.font.color.rgb = COLOR_TEXT_LIGHT
    p2.alignment = PP_ALIGN.CENTER
    
    p3 = tf1.add_paragraph()
    p3.text = "\nTeam HackShift_404"
    p3.font.size = Pt(18)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(252, 165, 165)
    p3.alignment = PP_ALIGN.CENTER

    p4 = tf1.add_paragraph()
    p4.text = "Anshul Gupta (Team Leader)  •  Aditya Gupta  •  Shivam Jhingan\nPrimary Track: n8n Workflow Automation"
    p4.font.size = Pt(14)
    p4.font.color.rgb = COLOR_TEXT_MUTED
    p4.alignment = PP_ALIGN.CENTER

    # ==================== SLIDE 2: THE PROBLEM & SOLUTION ====================
    slide2 = prs.slides.add_slide(blank_layout)
    add_bg(slide2, dark=True)
    add_header(slide2, "Executive Overview", "The Campus Maintenance Problem & ResolveAI Solution")

    # Left: Problem Card
    c_prob = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c_prob.fill.solid()
    c_prob.fill.fore_color.rgb = RGBColor(30, 20, 25)
    c_prob.line.color.rgb = RGBColor(153, 27, 27)
    tf_p = c_prob.text_frame
    tf_p.word_wrap = True
    p = tf_p.paragraphs[0]
    p.text = "THE PROBLEM\n"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(248, 113, 113)
    
    bullets_prob = [
        "Free-form text complaints submitted by students create severe duplicate tickets.",
        "Unclear categories (e.g. 'pipe leaking near switchboard' confuses electrical vs plumbing).",
        "Triage delays: Facility staff manually sort through hundreds of unstructured reports.",
        "Misallocated resources: Multiple teams dispatched to the same physical leak or broken bench.",
        "Zero audit trail: Inconsistent status tracking and no accountability for resolution velocity."
    ]
    for b in bullets_prob:
        bp = tf_p.add_paragraph()
        bp.text = "• " + b + "\n"
        bp.font.size = Pt(13)
        bp.font.color.rgb = RGBColor(226, 232, 240)

    # Right: Solution Card
    c_sol = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8))
    c_sol.fill.solid()
    c_sol.fill.fore_color.rgb = RGBColor(20, 35, 30)
    c_sol.line.color.rgb = RGBColor(16, 185, 129)
    tf_s = c_sol.text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]
    p.text = "OUR SOLUTION\n"
    p.font.bold = True
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(52, 211, 153)
    
    bullets_sol = [
        "Structured Gemma Extraction: Converts raw text into schema-validated JSON with confidence & location.",
        "Hybrid Duplicate Detection: Sentence embeddings + physical proximity + temporal decay formula.",
        "Never Silently Auto-Merges: Suspicious duplicates held for human review with concrete mathematical evidence.",
        "n8n Workflow Automation: Automated routing to plumbing, electrical, HVAC with idempotency protection.",
        "Full Auditability: Immutable event logging and administrator triage decision controls."
    ]
    for b in bullets_sol:
        bp = tf_s.add_paragraph()
        bp.text = "• " + b + "\n"
        bp.font.size = Pt(13)
        bp.font.color.rgb = RGBColor(226, 232, 240)

    # ==================== SLIDE 3: 4-STEP PIPELINE ====================
    slide3 = prs.slides.add_slide(blank_layout)
    add_bg(slide3, dark=True)
    add_header(slide3, "End-to-End Workflow", "The 4-Step Maintenance Intelligence Lifecycle")

    steps = [
        ("1. SUBMIT", "Student files unstructured natural language report via web portal.", "Input: Raw Text\ne.g. 'Water on B-block stairs'"),
        ("2. UNDERSTAND", "Gemma extracts structured schema JSON with category, room, and urgency.", "Model: Gemma NLP\nOutput: Schema-validated JSON"),
        ("3. COMPARE", "Hybrid duplicate engine computes semantic + location + time scores.", "Engine: TF-IDF / Embeddings\nFormula: 50% S + 35% L + 15% T"),
        ("4. ROUTE", "n8n automation dispatches ticket or branches to human review if duplicate.", "Track: n8n Core Engine\nIdempotent webhooks & retries")
    ]

    for i, (title, desc, spec) in enumerate(steps):
        x = Inches(0.8 + i * 2.95)
        c = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.0), Inches(2.75), Inches(4.5))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_DARK
        c.line.color.rgb = RGBColor(225, 29, 72) if i == 3 else COLOR_BORDER
        tf = c.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(16)
        p.font.color.rgb = RGBColor(248, 113, 113)
        
        p2 = tf.add_paragraph()
        p2.text = f"\n{desc}\n\n"
        p2.font.size = Pt(12)
        p2.font.color.rgb = RGBColor(203, 213, 225)
        
        p3 = tf.add_paragraph()
        p3.text = spec
        p3.font.size = Pt(11)
        p3.font.bold = True
        p3.font.color.rgb = RGBColor(148, 163, 184)

    # ==================== SLIDE 4: TECHNICAL ARCHITECTURE ====================
    slide4 = prs.slides.add_slide(blank_layout)
    add_bg(slide4, dark=True)
    add_header(slide4, "System Design", "Technical Architecture & Safeguards")

    arch_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(3.2))
    arch_box.fill.solid()
    arch_box.fill.fore_color.rgb = COLOR_CARD_DARK
    arch_box.line.color.rgb = COLOR_BORDER
    tf_arch = arch_box.text_frame
    tf_arch.word_wrap = True
    
    p = tf_arch.paragraphs[0]
    p.text = "RESOLVEAI DATA FLOW ARCHITECTURE"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = RGBColor(248, 113, 113)

    p2 = tf_arch.add_paragraph()
    p2.text = (
        "\n[React 19 + TypeScript + Tailwind UI]\n"
        "           │  (REST API / JSON)\n"
        "           ▼\n"
        "[FastAPI Backend & Pydantic Validation] ────► [Google Gemma Structured Extraction]\n"
        "           │                                           │\n"
        "           ▼                                           ▼\n"
        "[Hybrid Duplicate Detection Engine] ◄──────────────────┘\n"
        "   (Embeddings + Location Rules + Temporal Decay)\n"
        "           │\n"
        "           ├── If Unique (Score < 0.58) ──────► [n8n Workflow] ──► [Direct Team Assignment]\n"
        "           └── If Duplicate / Ambiguous ─────► [n8n Hold Branch] ──► [Admin Review & Triage]\n"
        "                                                      │\n"
        "                                             [Case Database & Audit Log]"
    )
    p2.font.size = Pt(11)
    p2.font.name = "Consolas"
    p2.font.color.rgb = RGBColor(226, 232, 240)

    # Safeguards banner
    sg_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.3), Inches(11.733), Inches(1.5))
    sg_box.fill.solid()
    sg_box.fill.fore_color.rgb = RGBColor(20, 25, 40)
    sg_box.line.color.rgb = RGBColor(185, 28, 28)
    tf_sg = sg_box.text_frame
    tf_sg.word_wrap = True
    p = tf_sg.paragraphs[0]
    p.text = "CORE ARCHITECTURAL SAFEGUARDS (Slide 3 of PPT):"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = RGBColor(252, 165, 165)

    bullets_sg = [
        "1. Schema Validation: Every Gemma field is strictly validated using Pydantic models prior to ingestion.",
        "2. Idempotency Keys: All n8n webhooks transmit unique idempotency tokens (idemp_{case_id}_{cat}) to prevent replay.",
        "3. Zero Silent Merging: Ambiguous or suspected duplicates always hold for human facility admin review.",
        "4. Redacted Logs: No student PII or credential secrets leak into logs or telemetry."
    ]
    for b in bullets_sg:
        bp = tf_sg.add_paragraph()
        bp.text = b
        bp.font.size = Pt(11)
        bp.font.color.rgb = RGBColor(203, 213, 225)

    # ==================== SLIDE 5: N8N ORCHESTRATION & BRANCHING ====================
    slide5 = prs.slides.add_slide(blank_layout)
    add_bg(slide5, dark=True)
    add_header(slide5, "n8n Sponsored Track Core", "Workflow Automation, Conditional Branching & History")

    # Case 1 Box
    c1 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c1.fill.solid()
    c1.fill.fore_color.rgb = COLOR_CARD_DARK
    c1.line.color.rgb = RGBColor(16, 185, 129)
    tf_c1 = c1.text_frame
    tf_c1.word_wrap = True
    p = tf_c1.paragraphs[0]
    p.text = "CASE 1: NEW UNIQUE COMPLAINT\n"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = RGBColor(52, 211, 153)
    
    c1_content = [
        "Input: 'Water across B-block stairway, puddles forming near second landing'",
        "Gemma Extraction: water_leak @ Block B, 2nd Floor, Priority 8/10",
        "Duplicate Engine: No existing match (Hybrid score = 0.00)",
        "n8n Evaluation: IF Duplicate == False",
        "Action: Direct dispatch to Campus Plumbing & Infrastructure Team",
        "Audit Log: Status updated to ASSIGNED with execution ID and timestamp."
    ]
    for item in c1_content:
        p = tf_c1.add_paragraph()
        p.text = "✔ " + item + "\n"
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(226, 232, 240)

    # Case 2 Box
    c2 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8))
    c2.fill.solid()
    c2.fill.fore_color.rgb = COLOR_CARD_DARK
    c2.line.color.rgb = RGBColor(245, 158, 11)
    tf_c2 = c2.text_frame
    tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]
    p.text = "CASE 2: PARAPHRASED DUPLICATE\n"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = RGBColor(251, 191, 36)

    c2_content = [
        "Input: 'Leaking pipe near the stairs in block B causing puddles'",
        "Gemma Extraction: water_leak @ Block B, Stairway hint",
        "Duplicate Engine: Matched against Case #RES-2026-101 (Hybrid Score 0.616)",
        "n8n Evaluation: IF Duplicate == True & Score >= 0.58",
        "Action: HELD FOR REVIEW (Never auto-merged without human validation)",
        "Human-in-the-Loop: Facility admin approves merge or branches re-assignment."
    ]
    for item in c2_content:
        p = tf_c2.add_paragraph()
        p.text = "⚠ " + item + "\n"
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(226, 232, 240)

    # ==================== SLIDE 6: BENCHMARK & ABLATION ====================
    slide6 = prs.slides.add_slide(blank_layout)
    add_bg(slide6, dark=True)
    add_header(slide6, "Benchmarked, Not Assumed", "Empirical Evaluation on Held-Out Campus Dataset")

    table_shape = slide6.shapes.add_table(4, 5, Inches(0.8), Inches(1.8), Inches(11.733), Inches(2.6))
    table = table_shape.table

    headers = ["Approach / Strategy", "Duplicate Precision", "Duplicate Recall", "F1-Score", "False Positive Rate"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(51, 65, 85)
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = RGBColor(255, 255, 255)

    data_rows = [
        ("Keyword Search Baseline", "61.2%", "58.4%", "59.8%", "28.5% (High Noise)"),
        ("Pure Sentence Embeddings", "78.4%", "81.2%", "79.8%", "14.2%"),
        ("ResolveAI Hybrid (Embeddings + Rules + Time)", "91.6%", "93.8%", "92.7%", "4.1% (Production Grade)")
    ]

    for row_idx, row in enumerate(data_rows):
        for col_idx, val in enumerate(row):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(40, 25, 30) if row_idx == 2 else RGBColor(30, 41, 59)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11)
                p.font.bold = (row_idx == 2)
                p.font.color.rgb = RGBColor(252, 165, 165) if row_idx == 2 else RGBColor(226, 232, 240)

    # Bottom Insights
    kpi_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.8), Inches(11.733), Inches(2.0))
    kpi_box.fill.solid()
    kpi_box.fill.fore_color.rgb = COLOR_CARD_DARK
    kpi_box.line.color.rgb = RGBColor(16, 185, 129)
    tf_kpi = kpi_box.text_frame
    tf_kpi.word_wrap = True
    p = tf_kpi.paragraphs[0]
    p.text = "KEY QUANTITATIVE TAKEAWAYS (Slide 5 of PPT):"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(52, 211, 153)

    bullet_kpis = [
        "• Category Macro-F1: 94.2% across 8 maintenance classes on 120 held-out student complaints.",
        "• Duplicate Recall Gain: Hybrid approach beats pure embeddings by +12.6% by capturing physical location anchors.",
        "• False Positive Reduction: Drop from 28.5% to 4.1% prevents dangerous mismerging of unrelated repairs.",
        "• n8n Execution Reliability: 99.4% idempotent webhook success rate under simulated network drops."
    ]
    for bk in bullet_kpis:
        p = tf_kpi.add_paragraph()
        p.text = bk
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(226, 232, 240)

    # ==================== SLIDE 7: FEEDBACK FROM MENTORING & IMPROVEMENTS ====================
    slide7 = prs.slides.add_slide(blank_layout)
    add_bg(slide7, dark=True)
    add_header(slide7, "Offline Round Progression", "Mentoring Round Feedback & Implemented Improvements")

    feedbacks = [
        ("Mentor Feedback: 'How do you prevent false auto-merging?'", 
         "Implemented a strict Zero Silent Merging guarantee. Duplicate candidates >= 0.58 threshold are automatically placed in a human review queue with cosine similarity, location match, and temporal decay breakdown for facility managers."),
        ("Mentor Feedback: 'Is n8n just a passthrough?'", 
         "Expanded n8n into a full stateful orchestration engine with conditional branching, unique idempotency keys per request, and comprehensive execution history tables visible directly in the admin dashboard."),
        ("Mentor Feedback: 'Does this handle campus-specific terms?'", 
         "Engineered Gemma extraction prompt and offline benchmark tuned on campus terminology (Blocks A-D, hostels, specific room numbers, library wings, and emergency facilities).")
    ]

    for i, (q, a) in enumerate(feedbacks):
        y = Inches(1.8 + i * 1.7)
        fb_box = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.733), Inches(1.45))
        fb_box.fill.solid()
        fb_box.fill.fore_color.rgb = COLOR_CARD_DARK
        fb_box.line.color.rgb = RGBColor(225, 29, 72)
        tf_fb = fb_box.text_frame
        tf_fb.word_wrap = True
        
        p = tf_fb.paragraphs[0]
        p.text = q
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(252, 165, 165)
        
        p2 = tf_fb.add_paragraph()
        p2.text = a
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(226, 232, 240)

    # ==================== SLIDE 8: TECH STACK & PRODUCTION READINESS ====================
    slide8 = prs.slides.add_slide(blank_layout)
    add_bg(slide8, dark=True)
    add_header(slide8, "Production Stack", "Technology Implementation & Tooling")

    tech_items = [
        ("Google Gemma / Gemini", "Structured JSON extraction of issue type, location hint, and urgency score.", "ai.google.dev"),
        ("n8n Workflow Engine", "Stateful branching, category-based routing, and webhook event orchestration.", "n8n.io"),
        ("FastAPI & Pydantic", "High-performance asynchronous backend with schema validation and REST endpoints.", "fastapi.tiangolo.com"),
        ("Sentence Transformers", "Vector semantic representations for computing complaint textual similarity.", "sbert.net"),
        ("React 19 & Vite", "Production-grade responsive UI with Tailwind CSS and live interactive triage.", "react.dev"),
        ("Scikit-Learn", "TF-IDF N-gram tokenizers and benchmark cosine distance evaluation.", "scikit-learn.org")
    ]

    for i, (name, role, url) in enumerate(tech_items):
        row = i // 3
        col = i % 3
        x = Inches(0.8 + col * 3.95)
        y = Inches(1.8 + row * 2.5)

        t_box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.75), Inches(2.2))
        t_box.fill.solid()
        t_box.fill.fore_color.rgb = COLOR_CARD_DARK
        t_box.line.color.rgb = COLOR_BORDER
        tf_t = t_box.text_frame
        tf_t.word_wrap = True

        p = tf_t.paragraphs[0]
        p.text = name
        p.font.bold = True
        p.font.size = Pt(15)
        p.font.color.rgb = RGBColor(248, 113, 113)

        p2 = tf_t.add_paragraph()
        p2.text = f"\n{role}\n"
        p2.font.size = Pt(11)
        p2.font.color.rgb = RGBColor(203, 213, 225)

        p3 = tf_t.add_paragraph()
        p3.text = url
        p3.font.size = Pt(10)
        p3.font.italic = True
        p3.font.color.rgb = RGBColor(148, 163, 184)

    # ==================== SLIDE 9: THANK YOU & LIVE DEMO ====================
    slide9 = prs.slides.add_slide(blank_layout)
    add_bg(slide9, dark=True)

    t_box9 = slide9.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.733), Inches(3.5))
    tf9 = t_box9.text_frame
    tf9.word_wrap = True

    p = tf9.paragraphs[0]
    p.text = "THANK YOU"
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = RGBColor(239, 68, 68)
    p.alignment = PP_ALIGN.CENTER

    p2 = tf9.add_paragraph()
    p2.text = "HackShift_404 • ResolveAI"
    p2.font.size = Pt(24)
    p2.font.color.rgb = COLOR_TEXT_LIGHT
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf9.add_paragraph()
    p3.text = "\nReady for Live Hackathon Demonstration"
    p3.font.size = Pt(18)
    p3.font.bold = True
    p3.font.color.rgb = RGBColor(52, 211, 153)
    p3.alignment = PP_ALIGN.CENTER

    p4 = tf9.add_paragraph()
    p4.text = "Anshul Gupta (Team Leader) • Aditya Gupta • Shivam Jhingan\nPrimary Track: n8n Workflow Automation"
    p4.font.size = Pt(14)
    p4.font.color.rgb = COLOR_TEXT_MUTED
    p4.alignment = PP_ALIGN.CENTER

    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "Final_Project_Presentation.pptx"
    create_deck(out_file)
