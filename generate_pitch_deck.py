"""
Script to generate the official CrowdSafe AI hackathon pitch presentation
using the SDGI Global University / TechSpireX template.
"""

import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE_PATH = r"C:\Users\Admin\.gemini\antigravity\brain\4608ac69-ebde-4189-970a-3ba54663a9de\.user_uploaded\media_1792784284542_1abf3e4a.pptx"
OUTPUT_PATH = r"C:\Users\Admin\.gemini\antigravity\scratch\crowdsafe-ai\CrowdSafe_AI_InnovatX_SGU.pptx"

# Color Palette matching TechSpireX & SGU Theme
NAVY_DARK = RGBColor(15, 30, 54)       # Deep Navy
BLUE_ACCENT = RGBColor(2, 132, 199)    # Tech Cyan/Blue
TEXT_DARK = RGBColor(30, 41, 59)       # Slate 800
TEXT_MUTED = RGBColor(100, 116, 139)   # Slate 500
WHITE = RGBColor(255, 255, 255)
GOLD_SGU = RGBColor(217, 119, 6)       # SGU Crest Gold
EMERALD = RGBColor(16, 185, 129)       # Safety Green
CARD_BG = RGBColor(248, 250, 252)      # Light Slate Box
CARD_BORDER = RGBColor(226, 232, 240)  # Border


def style_card(shape, bg_color=CARD_BG, border_color=CARD_BORDER):
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)


def add_bullet_point(tf, bold_prefix, text_content, font_size=14, bold_color=BLUE_ACCENT, text_color=TEXT_DARK):
    p = tf.add_paragraph()
    p.space_after = Pt(8)
    p.space_before = Pt(4)
    run1 = p.add_run()
    run1.text = "▪ " + bold_prefix + ": "
    run1.font.bold = True
    run1.font.size = Pt(font_size)
    run1.font.color.rgb = bold_color
    run1.font.name = "Arial"

    run2 = p.add_run()
    run2.text = text_content
    run2.font.bold = False
    run2.font.size = Pt(font_size)
    run2.font.color.rgb = text_color
    run2.font.name = "Arial"


def build_presentation():
    prs = Presentation(TEMPLATE_PATH)
    print(f"Loaded template with {len(prs.slides)} slides.")

    # =========================================================================
    # SLIDE 0: COVER PAGE
    # =========================================================================
    s0 = prs.slides[0]
    for shape in s0.shapes:
        if shape.has_text_frame:
            txt = shape.text.strip()
            if txt == "TEAM NAME:":
                tf = shape.text_frame
                tf.clear()
                p = tf.paragraphs[0]
                r1 = p.add_run()
                r1.text = "TEAM NAME: "
                r1.font.bold = True
                r1.font.size = Pt(20)
                r1.font.color.rgb = NAVY_DARK
                r2 = p.add_run()
                r2.text = "InnovatX"
                r2.font.bold = True
                r2.font.size = Pt(22)
                r2.font.color.rgb = BLUE_ACCENT

            elif txt == "PROBLEM STATEMENT:":
                tf = shape.text_frame
                tf.clear()
                p = tf.paragraphs[0]
                r1 = p.add_run()
                r1.text = "PROBLEM STATEMENT: "
                r1.font.bold = True
                r1.font.size = Pt(17)
                r1.font.color.rgb = NAVY_DARK
                r2 = p.add_run()
                r2.text = "AI-Powered Crowd Monitoring & Stampede Early Warning System (CrowdSafe AI)"
                r2.font.bold = True
                r2.font.size = Pt(17)
                r2.font.color.rgb = GOLD_SGU

            elif txt == "TEAM MEMBERS:":
                tf = shape.text_frame
                tf.clear()
                # Expand box height for 4 members
                shape.height = int(shape.height * 2.2)
                shape.width = int(shape.width * 1.3)
                p0 = tf.paragraphs[0]
                r0 = p0.add_run()
                r0.text = "TEAM MEMBERS:"
                r0.font.bold = True
                r0.font.size = Pt(17)
                r0.font.color.rgb = NAVY_DARK

                members = [
                    ("1. Abhishek Kumar", "Team Leader", "SDGI Global University, Ghaziabad"),
                    ("2. Abhishek Parmar", "Team Member", "SDGI Global University, Ghaziabad"),
                    ("3. Abhinav Shukla", "Team Member", "SDGI Global University, Ghaziabad"),
                    ("4. Abhishek Sharma", "Team Member", "SDGI Global University, Ghaziabad")
                ]
                for name, role, college in members:
                    p = tf.add_paragraph()
                    p.space_before = Pt(2)
                    r = p.add_run()
                    r.text = f"• {name} [{role}]"
                    r.font.bold = True
                    r.font.size = Pt(15)
                    r.font.color.rgb = TEXT_DARK

            elif txt == "COLLEGE:":
                tf = shape.text_frame
                tf.clear()
                p = tf.paragraphs[0]
                r1 = p.add_run()
                r1.text = "COLLEGE: "
                r1.font.bold = True
                r1.font.size = Pt(18)
                r1.font.color.rgb = NAVY_DARK
                r2 = p.add_run()
                r2.text = "SDGI GLOBAL UNIVERSITY, GHAZIABAD"
                r2.font.bold = True
                r2.font.size = Pt(18)
                r2.font.color.rgb = GOLD_SGU

    # =========================================================================
    # SLIDE 1: PROBLEM STATEMENT
    # =========================================================================
    s1 = prs.slides[1]
    # Add 3 Structured Pillar Cards
    card_width = Inches(5.6)
    card_height = Inches(4.3)
    top_pos = Inches(4.3)

    cols = [
        ("The Critical Hazard", "Silent Chokepoint Congestion", [
            ("Root Cause", "High-density crowd disasters (stadiums, transit hubs, festivals) start at localized micro-bottlenecks."),
            ("Critical Threshold", "When density exceeds 4-6 people/m², laminar movement collapses into dangerous shockwaves."),
            ("Real-World Impact", "Recent global tragedies (Itaewon, concert surges) demonstrated failure of delayed intervention.")
        ], RGBColor(239, 68, 68)), # Red

        ("Human Limitation", "Surveillance Operator Fatigue", [
            ("Cognitive Overload", "Security personnel monitor 30-50 simultaneous CCTV feeds across multiple venues."),
            ("Attention Drop", "Studies show human surveillance vigilance drops by over 70% within 20 minutes of continuous monitoring."),
            ("Reaction Latency", "Guards only notice trouble after physical panic erupts—far too late for preventative measures.")
        ], RGBColor(245, 158, 11)), # Amber

        ("Systemic Deficiency", "Passive Forensics vs Prevention", [
            ("Reactive Only", "Traditional CCTV records evidence for post-disaster audits instead of active incident prevention."),
            ("No Micro-Zone Mapping", "Existing systems lack spatial awareness of physical bottleneck capacities and duration limits."),
            ("The Urgent Need", "An automated, sub-second AI decision-support system to alert ground officers 3-5 minutes prior.")
        ], RGBColor(2, 132, 199)) # Blue
    ]

    for i, (cat, title, items, color) in enumerate(cols):
        left_pos = Inches(0.8 + i * 5.9)
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, card_width, card_height)
        style_card(card)

        tf = card.text_frame
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)
        tf.word_wrap = True

        p_cat = tf.paragraphs[0]
        r_cat = p_cat.add_run()
        r_cat.text = cat.upper()
        r_cat.font.size = Pt(11)
        r_cat.font.bold = True
        r_cat.font.color.rgb = color

        p_title = tf.add_paragraph()
        r_title = p_title.add_run()
        r_title.text = title
        r_title.font.size = Pt(16)
        r_title.font.bold = True
        r_title.font.color.rgb = NAVY_DARK
        p_title.space_after = Pt(10)

        for prefix, body in items:
            add_bullet_point(tf, prefix, body, font_size=12, bold_color=color)

    # =========================================================================
    # SLIDE 2: PROPOSED SOLUTION
    # =========================================================================
    s2 = prs.slides[2]
    # Solution Overview Header Box + 3 Capability Cards
    head_box = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(4.3), Inches(17.4), Inches(0.8))
    head_box.fill.solid()
    head_box.fill.fore_color.rgb = NAVY_DARK
    head_box.line.color.rgb = BLUE_ACCENT
    head_tf = head_box.text_frame
    p_head = head_tf.paragraphs[0]
    p_head.alignment = PP_ALIGN.CENTER
    r_head = p_head.add_run()
    r_head.text = "CrowdSafe AI: Autonomous Vision-Based Crowd Risk & Early-Warning Platform"
    r_head.font.bold = True
    r_head.font.size = Pt(17)
    r_head.font.color.rgb = WHITE

    sol_cards = [
        ("Real YOLOv8 Edge Vision", "High-Speed Autonomous Detection", [
            ("Zero Hardware Cost", "Runs frame-by-frame person detection directly on existing standard CCTV cameras."),
            ("Real-Time Throughput", "Optimized YOLOv8 nano yields 25+ FPS (~40ms) inference even on standard CPUs."),
            ("Tactical Annotations", "Extracts bounding boxes, pedestrian confidence, and ground-centroid radar positions.")
        ], EMERALD),

        ("Micro-Zone Spatial Analysis", "Targeted Risk Geometry", [
            ("Tactical Sectoring", "Divides monitored venues into configurable zones (Turnstiles, Stairs, Main Halls, Exits)."),
            ("Configurable Capacities", "Each zone has independent thresholds tailored to physical width and egress limits."),
            ("Spatial Heat Matrix", "Visual 2D topological matrix provides instant percentage capacity overview.")
        ], BLUE_ACCENT),

        ("Duration-Aware Early Alerting", "Predictive Stampede Warning", [
            ("4-Tier Threat Matrix", "Green (Normal) ➔ Yellow (Increasing) ➔ Orange (High) ➔ Red (Critical Risk)."),
            ("Congestion Timer", "Requires continuous congestion (>3-5s) before alarming, eliminating false triggers."),
            ("Audio Siren & Audit Log", "Web Audio control room sirens + immutable SQLite audit log with operator sign-off.")
        ], GOLD_SGU)
    ]

    for i, (cat, title, items, color) in enumerate(sol_cards):
        left_pos = Inches(0.8 + i * 5.9)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(5.3), Inches(5.6), Inches(3.9))
        style_card(card)
        tf = card.text_frame
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.2)
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = cat.upper()
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = color

        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = title
        r2.font.size = Pt(15)
        r2.font.bold = True
        r2.font.color.rgb = NAVY_DARK
        p2.space_after = Pt(8)

        for prefix, body in items:
            add_bullet_point(tf, prefix, body, font_size=12, bold_color=color)

    # =========================================================================
    # SLIDE 3: FLOW OF SOLUTION
    # =========================================================================
    s3 = prs.slides[3]
    # 4 Flow Steps connected sequentially
    flow_steps = [
        ("STEP 1: INGESTION", "Video Feed Decoupling", [
            ("Input Sources", "Standard RTSP CCTV streams, prerecorded surveillance MP4/AVI, or live IP camera."),
            ("OpenCV Pipeline", "Multi-threaded frame ingestion and resolution standardization.")
        ], BLUE_ACCENT),

        ("STEP 2: INFERENCE", "YOLOv8 Person Detection", [
            ("Neural Network", "Ultralytics YOLOv8 nano model targeting COCO Class 0 (Human Person)."),
            ("Coordinate Extraction", "Bounding boxes [x1, y1, x2, y2], centroid tracking, and foot point mapping.")
        ], EMERALD),

        ("STEP 3: RISK ENGINE", "Zone & Duration Analysis", [
            ("Spatial Intersection", "Counts individuals residing inside tactical micro-zone polygon bounds."),
            ("Congestion Timer", "Calculates continuous congestion duration vs safety threshold limits.")
        ], GOLD_SGU),

        ("STEP 4: INTERVENTION", "Tactical Warning & Audit", [
            ("Command Dashboard", "React Security Operations Center with live annotated HUD streaming."),
            ("Action Protocol", "Web Audio sirens, SMS/Radio alerts for ground guards, and SQLite logging.")
        ], RGBColor(239, 68, 68))
    ]

    card_w = Inches(4.15)
    card_h = Inches(4.3)
    for i, (step_lbl, title, items, color) in enumerate(flow_steps):
        left_pos = Inches(0.6 + i * 4.35)
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(4.3), card_w, card_h)
        style_card(card)
        tf = card.text_frame
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.2)
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = step_lbl
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = color

        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = title
        r2.font.size = Pt(15)
        r2.font.bold = True
        r2.font.color.rgb = NAVY_DARK
        p2.space_after = Pt(10)

        for prefix, body in items:
            add_bullet_point(tf, prefix, body, font_size=11, bold_color=color)

    # =========================================================================
    # SLIDE 4: TECH STACK
    # =========================================================================
    s4 = prs.slides[4]
    tech_categories = [
        ("Frontend & SOC Dashboard", "React 18 & TypeScript", [
            ("Tactical Dark UI", "Tailwind CSS command-center theme with high-contrast accessibility."),
            ("Real-Time Telemetry", "1-second polling synchronization with low-latency MJPEG video player."),
            ("Web Audio API", "Synthesizes tactical warning frequencies directly inside browser with zero assets.")
        ], BLUE_ACCENT),

        ("Backend & Ingestion Engine", "Python 3.14 & FastAPI", [
            ("Asynchronous API", "High-throughput asynchronous REST endpoints and background worker tasks."),
            ("Uvicorn ASGI", "Ultra-low overhead web server powering multi-threaded frame generators."),
            ("Modular Architecture", "Decoupled video ingestion, risk evaluator, and simulation engine.")
        ], EMERALD),

        ("Computer Vision & Deep Learning", "YOLOv8 & OpenCV", [
            ("Ultralytics YOLOv8n", "Lightweight state-of-the-art model; ~40ms inference on standard CPUs."),
            ("OpenCV (cv2)", "HUD crosshairs, tactical brackets, sector tints, and HOG people detector fallback."),
            ("Truth-in-AI", "Clear visual badging strictly separating Real AI Inference from Demo Simulation.")
        ], GOLD_SGU),

        ("Data Persistence & Storage", "SQLite 3 Engine", [
            ("Relational Tables", "Structured schemas for Cameras, Dynamic Zones, Observations, and Alerts."),
            ("Zero Configuration", "Serverless, embedded database operating 100% offline with zero cloud dependency."),
            ("Audit Trail", "Immutable timestamped alert log with operator sign-off and JSON export.")
        ], NAVY_DARK)
    ]

    card_w = Inches(4.15)
    card_h = Inches(4.3)
    for i, (cat, title, items, color) in enumerate(tech_categories):
        left_pos = Inches(0.6 + i * 4.35)
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(4.3), card_w, card_h)
        style_card(card)
        tf = card.text_frame
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.2)
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = cat.upper()
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = color

        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = title
        r2.font.size = Pt(15)
        r2.font.bold = True
        r2.font.color.rgb = NAVY_DARK
        p2.space_after = Pt(10)

        for prefix, body in items:
            add_bullet_point(tf, prefix, body, font_size=11, bold_color=color)

    # =========================================================================
    # SLIDE 5: UNIQUE SELLING PROPOSITION (USP)
    # =========================================================================
    s5 = prs.slides[5]
    usps = [
        ("USP 1", "Duration-Aware Risk Analysis", "Zero False Alarms Through Temporal Tracking", [
            ("The Problem", "Traditional counters alarm whenever groups briefly congregate, causing alert fatigue."),
            ("Our Innovation", "Monitors Congestion Duration. Only escalates to Critical when density persists > 4 seconds."),
            ("The Benefit", "Filters out brief pauses while catching true physical blockages.")
        ], EMERALD),

        ("USP 2", "Micro-Zone Spatial Granularity", "Pinpoint Localization of Chokepoints", [
            ("The Problem", "Legacy systems give a single count for a 50,000-seat stadium, hiding bottleneck locations."),
            ("Our Innovation", "Maps micro-sectors (turnstiles, corridors, gates) with independent capacity limits."),
            ("The Benefit", "Ground security knows exact coordinates to deploy barrier diversions immediately.")
        ], BLUE_ACCENT),

        ("USP 3", "Zero Extra Hardware Cost", "Drop-In Software On Existing CCTV", [
            ("The Problem", "LiDAR and thermal sensors cost $5,000 to $15,000 per camera unit."),
            ("Our Innovation", "100% software-based computer vision utilizing already-installed surveillance cameras."),
            ("The Benefit", "Deployable in hours across stadiums, metro stations, and public festivals at near-zero capex.")
        ], GOLD_SGU)
    ]

    for i, (badge, title, subtitle, items, color) in enumerate(usps):
        left_pos = Inches(0.8 + i * 5.9)
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(4.3), Inches(5.6), Inches(4.5))
        style_card(card)
        tf = card.text_frame
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = badge + " • " + title.upper()
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = color

        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = subtitle
        r2.font.size = Pt(15)
        r2.font.bold = True
        r2.font.color.rgb = NAVY_DARK
        p2.space_after = Pt(10)

        for prefix, body in items:
            add_bullet_point(tf, prefix, body, font_size=12, bold_color=color)

    # =========================================================================
    # SLIDE 6: FEASIBILITY & COMPETITORS
    # =========================================================================
    s6 = prs.slides[6]
    # Left side: Feasibility Breakdown (Width 7.5 in)
    # Right side: Competitor Matrix Table (Width 9.5 in)
    left_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.3), Inches(6.8), Inches(4.5))
    style_card(left_card)
    ltf = left_card.text_frame
    ltf.margin_left = Inches(0.25)
    ltf.margin_right = Inches(0.25)
    ltf.margin_top = Inches(0.25)
    ltf.word_wrap = True

    lp1 = ltf.paragraphs[0]
    lr1 = lp1.add_run()
    lr1.text = "FEASIBILITY & VIABILITY ANALYSIS"
    lr1.font.size = Pt(12)
    lr1.font.bold = True
    lr1.font.color.rgb = BLUE_ACCENT

    feasibility_points = [
        ("Technical Feasibility", "YOLOv8 nano processes 25+ FPS on commodity Intel/AMD CPUs without needing high-end GPUs."),
        ("Operational Feasibility", "Works 100% offline via local LAN and SQLite; resilient against network or internet outages."),
        ("Privacy & Compliance", "GDPR/DPDP compliant: detects generic pedestrian bounding boxes; strictly zero facial recognition or PII storage."),
        ("Economic Scalability", "B2B SaaS subscription model ($49-$99/camera/month) yields 90% savings over specialized sensors.")
    ]
    for pfx, bdy in feasibility_points:
        add_bullet_point(ltf, pfx, bdy, font_size=11, bold_color=BLUE_ACCENT)

    # Right side: Competitor Comparison Table
    table_shape = s6.shapes.add_table(5, 5, Inches(8.0), Inches(4.3), Inches(9.5), Inches(4.5))
    table = table_shape.table

    # Column widths
    table.columns[0].width = Inches(2.3)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(1.8)
    table.columns[3].width = Inches(1.8)
    table.columns[4].width = Inches(1.8)

    headers = ["Feature", "Legacy CCTV", "Retail Counters", "LiDAR Sensors", "CrowdSafe AI"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_DARK if j < 4 else BLUE_ACCENT
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(11)
        p.runs[0].font.color.rgb = WHITE

    rows_data = [
        ("Primary Goal", "Post-Incident Audit", "Customer Tracking", "Perimeter Defense", "Stampede Warning"),
        ("Congestion Duration", "None (Human eye)", "Basic Dwell Time", "High Latency", "Real-Time (>4s timer)"),
        ("Deployment Cost", "High Human Labor", "$1,500+ / sensor", "$5,000+ / unit", "Low (Software-only)"),
        ("Privacy (No Faces)", "Violated (raw face)", "Variable", "Anonymous", "100% Anonymous")
    ]

    for i, row in enumerate(rows_data):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if j < 4 else RGBColor(224, 242, 254)
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT
            if len(p.runs) > 0:
                p.runs[0].font.size = Pt(11)
                p.runs[0].font.bold = (j == 4 or j == 0)
                p.runs[0].font.color.rgb = NAVY_DARK if j < 4 else BLUE_ACCENT

    # =========================================================================
    # SLIDE 7: RESEARCH & REFERENCE
    # =========================================================================
    s7 = prs.slides[7]
    ref_cards = [
        ("Academic Research", "Crowd Dynamics & Safety Science", [
            ("Helbing & Molnar (1995)", "'Social Force Model for Pedestrian Dynamics' — Theoretical foundation for crowd pressure shockwaves."),
            ("Fruin's Levels of Service (LOS)", "Pedestrian planning standards: Normal flow (< 2 pax/m²) vs Critical crush hazard (> 4-5 pax/m²)."),
            ("Still, G. K. (2014)", "'Crowd Risk Analysis and Crowd Safety' — Guidelines for bottleneck dissipation.")
        ], BLUE_ACCENT),

        ("Technical Benchmarks", "Vision Models & Public Datasets", [
            ("Ultralytics YOLOv8 (2023)", "State-of-the-art real-time anchor-free detection engine on MS COCO benchmark."),
            ("Intel IoT Pedestrian Dataset", "Tested on standard surveillance pedestrian benchmark with frame-by-frame verification."),
            ("FastAPI & Web Audio API", "Sub-second asynchronous streaming benchmarks ensuring zero UI latency.")
        ], EMERALD),

        ("Project Links & Demo", "Live Implementation & Codebase", [
            ("GitHub Repository", "Full open-source codebase, modular architecture, and documentation."),
            ("Working Prototype", "Localhost:8000 dashboard running real-time YOLOv8 person detection & demo simulation."),
            ("Team InnovatX", "Department of Computer Applications, SDGI Global University, Ghaziabad.")
        ], GOLD_SGU)
    ]

    for i, (cat, title, items, color) in enumerate(ref_cards):
        left_pos = Inches(0.8 + i * 5.9)
        card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(4.3), Inches(5.6), Inches(4.5))
        style_card(card)
        tf = card.text_frame
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = cat.upper()
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = color

        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = title
        r2.font.size = Pt(15)
        r2.font.bold = True
        r2.font.color.rgb = NAVY_DARK
        p2.space_after = Pt(10)

        for prefix, body in items:
            add_bullet_point(tf, prefix, body, font_size=12, bold_color=color)

    # =========================================================================
    # SLIDE 8: REMOVE GUIDELINES SLIDE AS REQUESTED
    # =========================================================================
    if len(prs.slides) >= 9:
        print("Removing slide 8 (Guidelines slide) as requested...")
        rId = prs.slides._sldIdLst[8].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[8]

    prs.save(OUTPUT_PATH)
    print(f"Presentation successfully created with {len(prs.slides)} slides at: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_presentation()
