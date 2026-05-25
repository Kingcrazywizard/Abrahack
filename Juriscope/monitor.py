#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitor Judicial - Python Edition
Consulta:
- Rama Judicial Colombia (casos 1-6)
- SAMAI Consejo de Estado (caso 7)

Envía reportes HTML por correo.

Autor: Abrahack
"""

import os
import re
import json
import smtplib
import requests

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path.home() / "RamaJudicial"
BASE_DIR.mkdir(exist_ok=True)

STATE_FILE = BASE_DIR / "estado.json"

API = "https://consultaprocesos.ramajudicial.gov.co:448/api/v2"

SAMAI_URL = (
    "https://samai.consejodeestado.gov.co/"
    "Vistas/Casos/list_procesos.aspx?"
    "guid=730013333012202000181017300123"
)

TIMEOUT = 30

EMAIL_FROM = "acidburn11235@gmail.com"
EMAIL_TO = "acidburn11235@gmail.com"

# ============================================================
# GMAIL
# ============================================================

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

if not GMAIL_USER or not GMAIL_PASS:
    print("ERROR: faltan variables GMAIL_USER y GMAIL_PASS")
    exit(1)

# ============================================================
# HEADERS IMPORTANTES
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) "
        "Gecko/20100101 Firefox/151.0"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://consultaprocesos.ramajudicial.gov.co/",
    "Origin": "https://consultaprocesos.ramajudicial.gov.co"
}

# ============================================================
# CASOS
# ============================================================

RJ_CASES = [
    {
        "n": 1,
        "rad": "11001400305220120094800",
        "nm": "BODEGA JUZGADOS CIVILES MUNICIPALES",
        "filt": ""
    },
    {
        "n": 2,
        "rad": "11001310500420140027201",
        "nm": "CORTE SUPREMA DE JUSTICIA SALA LABORAL ECOPETROL",
        "filt": "CORTE SUPREMA"
    },
    {
        "n": 3,
        "rad": "11001311000720210063800",
        "nm": "SUCESION JHON MORENO",
        "filt": ""
    },
    {
        "n": 4,
        "rad": "11001311000720250096000",
        "nm": "REIVINDICATORIO PONTEVEDRA",
        "filt": ""
    },
    {
        "n": 5,
        "rad": "11001311001820230079100",
        "nm": "PROCESO UNION MARITAL AMPARO",
        "filt": ""
    },
    {
        "n": 6,
        "rad": "73001418900520230067300",
        "nm": "EJECUTIVO GLORIA",
        "filt": ""
    }
]

# ============================================================
# HELPERS
# ============================================================

def load_state():

    if not STATE_FILE.exists():
        return {
            "fecha": "",
            "procesos": {},
            "samai": {}
        }

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return {
            "fecha": "",
            "procesos": {},
            "samai": {}
        }


def save_state(data):

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_json(url):

    try:

        r = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        print(f"[HTTP {r.status_code}] {url}")

        r.raise_for_status()

        return r.json()

    except Exception as e:

        print(f"ERROR GET JSON: {e}")

        return None


def escape_html(text):

    if not text:
        return ""

    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def format_date(raw):

    if not raw:
        return ""

    if "T" in raw:

        try:
            dt = datetime.fromisoformat(raw)
            return dt.strftime("%d/%m/%Y")
        except Exception:
            pass

    m = re.search(r"(\d{2}/\d{2}/\d{4})", raw)

    if m:
        return m.group(1)

    return raw


# ============================================================
# INICIO
# ============================================================

prev = load_state()

first_run = prev.get("fecha", "") == ""

today_iso = datetime.now().strftime("%Y-%m-%d")
today_str = datetime.now().strftime("%d/%m/%Y")
now_str = datetime.now().strftime("%d/%m/%Y %H:%M")

print(f"\nIniciando monitoreo judicial - {now_str}\n")

blocks = []
new_proc_state = {}

# ============================================================
# CONSULTA RAMA JUDICIAL
# ============================================================

for case in RJ_CASES:

    print(f"Consultando caso {case['n']}...")

    url = (
        f"{API}/Procesos/Consulta/NumeroRadicacion"
        f"?numero={case['rad']}"
        f"&SoloActivos=false"
        f"&pagina=1"
    )

    proc_resp = get_json(url)

    procesos = []

    if proc_resp:
        procesos = proc_resp.get("procesos", [])

    # DEBUG
    print(f"Procesos encontrados: {len(procesos)}")

    if case["filt"]:

        procesos = [
            p for p in procesos
            if case["filt"].lower()
            in p.get("despacho", "").lower()
        ]

    if not procesos:

        blocks.append({
            "n": case["n"],
            "nm": case["nm"],
            "rad": case["rad"],
            "st": "no_results"
        })

        continue

    procesos.sort(
        key=lambda x: int(x.get("idProceso", 0)),
        reverse=True
    )

    proc = procesos[0]

    print(f"ID PROCESO: {proc['idProceso']}")

    act_url = (
        f"{API}/Proceso/Actuaciones/"
        f"{proc['idProceso']}?pagina=1"
    )

    act_resp = get_json(act_url)

    acts = []

    if act_resp:
        acts = act_resp.get("actuaciones", [])

    print(f"Actuaciones encontradas: {len(acts)}")

    if not acts:

        blocks.append({
            "n": case["n"],
            "nm": case["nm"],
            "rad": case["rad"],
            "st": "no_actuaciones"
        })

        continue

    acts.sort(
        key=lambda x: int(x.get("idRegActuacion", 0)),
        reverse=True
    )

    top_id = int(acts[0]["idRegActuacion"])

    id_proc = str(proc["idProceso"])

    new_proc_state[id_proc] = top_id

    prev_id = prev.get("procesos", {}).get(
        id_proc,
        {}
    ).get("ultimoIdRegActuacion", top_id)

    novedad = (
        (not first_run)
        and
        top_id > prev_id
    )

    new_acts = []

    if novedad:

        new_acts = [
            a for a in acts
            if int(a["idRegActuacion"]) > prev_id
        ]

    blocks.append({
        "n": case["n"],
        "nm": case["nm"],
        "rad": case["rad"],
        "st": "novedad" if novedad else "ok",
        "desp": proc.get("despacho", ""),
        "dep": proc.get("departamento", ""),
        "par": proc.get("sujetosProcesales", ""),
        "last": acts[0],
        "newActs": new_acts
    })

# ============================================================
# CONSULTA SAMAI
# ============================================================

print("\nConsultando SAMAI...\n")

s7 = {
    "n": 7,
    "nm": "APELACION TRIBUNAL TOLIMA",
    "rad": "73001333301220200018101",
    "st": "error"
}

try:

    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) "
            "Gecko/20100101 Firefox/151.0"
        )
    })

    # ========================================================
    # PASO 1 - GET
    # ========================================================

    r1 = session.get(
        SAMAI_URL,
        timeout=TIMEOUT
    )

    html = r1.text

    print(f"GET SAMAI STATUS: {r1.status_code}")

    # ========================================================
    # EXTRAER CAPTCHA
    # ========================================================

    d1 = re.search(
        r'id="MainContent_Lbldato1"[^>]*>([^<]+)<',
        html
    )

    d2 = re.search(
        r'id="MainContent_Lbldato2"[^>]*>([^<]+)<',
        html
    )

    d3 = re.search(
        r'id="MainContent_Lbldato3"[^>]*>([^<]+)<',
        html
    )

    captcha = (
        (d1.group(1).strip() if d1 else "") +
        (d2.group(1).strip() if d2 else "") +
        (d3.group(1).strip() if d3 else "")
    )

    captcha = captcha.replace(" ", "")

    print(f"CAPTCHA: [{captcha}]")

    # ========================================================
    # VIEWSTATE
    # ========================================================

    def extract(name):

        m = re.search(
            rf'id="{name}" value="([^"]+)"',
            html
        )

        return m.group(1) if m else ""

    viewstate = extract("__VIEWSTATE")

    eventvalidation = extract("__EVENTVALIDATION")

    viewstategenerator = extract("__VIEWSTATEGENERATOR")

    print(f"VIEWSTATE OK: {bool(viewstate)}")

    # ========================================================
    # PAYLOAD
    # ========================================================

    payload = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",

        "__VIEWSTATE": viewstate,

        "__VIEWSTATEGENERATOR":
            viewstategenerator,

        "__EVENTVALIDATION":
            eventvalidation,

        "ctl00$MainContent$TxtCaptcha2":
            captcha,

        "ctl00$MainContent$CmdNoRobot":
            "Continuar"
    }

    headers_post = {
        "Referer": SAMAI_URL,
        "Origin": "https://samai.consejodeestado.gov.co"
    }

    # ========================================================
    # PASO 2 - POST
    # ========================================================

    r2 = session.post(
        SAMAI_URL,
        data=payload,
        headers=headers_post,
        timeout=TIMEOUT
    )

    html2 = r2.text

    print(f"POST SAMAI STATUS: {r2.status_code}")

    # DEBUG HTML
    debug_file = BASE_DIR / "samai_debug.html"

    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(html2)

    print(f"DEBUG HTML: {debug_file}")

    # ========================================================
    # DETECTAR CAPTCHA FALLIDO
    # ========================================================

    if (
        "captcha" in html2.lower()
        and
        "incorrect" in html2.lower()
    ):

        s7["st"] = "captcha_error"

    # ========================================================
    # PARSEAR ACTUACIONES
    # ========================================================

    acts7 = []

    rows = re.findall(
        r'(?is)<tr[^>]*>(.*?)</tr>',
        html2
    )

    print(f"ROWS ENCONTRADAS: {len(rows)}")

    for row in rows:

        cells = re.findall(
            r'(?is)<td[^>]*>(.*?)</td>',
            row
        )

        if len(cells) < 8:
            continue

        clean = []

        for c in cells:

            txt = re.sub(r"<[^>]+>", "", c)

            txt = (
                txt
                .replace("&nbsp;", " ")
                .strip()
            )

            clean.append(txt)

        idx_raw = clean[7]

        if not re.match(r"^\d+$", idx_raw):
            continue

        try:

            acts7.append({
                "idx": int(idx_raw),
                "fecha": clean[2],
                "actuacion": clean[3],
                "anotacion": clean[4]
            })

        except Exception:
            pass

    print(f"ACTUACIONES SAMAI: {len(acts7)}")

    # ========================================================
    # RESULTADOS
    # ========================================================

    if acts7:

        acts7.sort(
            key=lambda x: x["idx"],
            reverse=True
        )

        max_idx = acts7[0]["idx"]

        prev_idx = prev.get(
            "samai",
            {}
        ).get(
            "730013333012202000181017300123",
            {}
        ).get(
            "ultimoIndice",
            max_idx
        )

        nov7 = (
            (not first_run)
            and
            max_idx > prev_idx
        )

        new_acts7 = []

        if nov7:

            new_acts7 = [
                a for a in acts7
                if a["idx"] > prev_idx
            ]

        s7["st"] = "novedad" if nov7 else "ok"

        s7["last"] = acts7[0]

        s7["newActs"] = new_acts7

        s7["maxIdx"] = max_idx

    else:

        s7["st"] = "sin_resultados"

except Exception as e:

    s7["st"] = "error"

    s7["errMsg"] = str(e)

    print(f"SAMAI ERROR: {e}")

# ============================================================
# HTML
# ============================================================

html_parts = []

html_parts.append(f"""
<html>
<body style="font-family:Arial;padding:20px;">

<h2>Informe Judicial - {now_str}</h2>
""")

for b in blocks:

    color = "#1a3c6b"

    if b["st"] == "novedad":
        color = "#e07b00"

    html_parts.append(f"""
    <div style="
        border-left:5px solid {color};
        padding:10px;
        margin-bottom:15px;
        background:#f7f7f7;
    ">
    """)

    html_parts.append(f"""
        <h3>{b['n']}. {escape_html(b['nm'])}</h3>
        <p><b>Radicado:</b> {b['rad']}</p>
        <p><b>Estado:</b> {b['st']}</p>
    """)

    if b.get("desp"):

        html_parts.append(f"""
        <p><b>Despacho:</b>
        {escape_html(b['desp'])}</p>
        """)

    if b.get("last"):

        last = b["last"]

        html_parts.append(f"""
        <p><b>Última actuación:</b>
        {format_date(last.get('fechaActuacion', ''))}</p>

        <p><b>Tipo:</b>
        {escape_html(last.get('actuacion', ''))}</p>

        <p><b>Anotación:</b>
        {escape_html(last.get('anotacion', ''))}</p>
        """)

    if b.get("newActs"):

        html_parts.append("<ul>")

        for na in b["newActs"]:

            html_parts.append(f"""
            <li>
            {format_date(na.get('fechaActuacion', ''))}
            -
            {escape_html(na.get('actuacion', ''))}
            </li>
            """)

        html_parts.append("</ul>")

    html_parts.append("</div>")

# ============================================================
# SAMAI
# ============================================================

html_parts.append("""
<hr>
<h2>SAMAI - Consejo de Estado</h2>
""")

html_parts.append(f"""
<div style="
    border-left:5px solid #444;
    padding:10px;
    background:#f4f4f4;
">
<p><b>Estado:</b> {s7['st']}</p>
""")

if s7.get("last"):

    last7 = s7["last"]

    html_parts.append(f"""
    <p><b>Fecha:</b>
    {last7.get('fecha', '')}</p>

    <p><b>Actuación:</b>
    {escape_html(last7.get('actuacion', ''))}</p>

    <p><b>Anotación:</b>
    {escape_html(last7.get('anotacion', ''))}</p>
    """)

if s7.get("errMsg"):

    html_parts.append(f"""
    <p><b>Error:</b>
    {escape_html(s7['errMsg'])}</p>
    """)

html_parts.append("</div>")
html_parts.append("</body></html>")

html_report = "\n".join(html_parts)

# ============================================================
# EMAIL
# ============================================================

print("\nEnviando correo...\n")

msg = MIMEMultipart("alternative")

msg["Subject"] = f"Informe Rama Judicial - {today_str}"
msg["From"] = EMAIL_FROM
msg["To"] = EMAIL_TO

part = MIMEText(
    html_report,
    "html",
    "utf-8"
)

msg.attach(part)

try:

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(
        GMAIL_USER,
        GMAIL_PASS
    )

    server.sendmail(
        EMAIL_FROM,
        EMAIL_TO,
        msg.as_string()
    )

    server.quit()

    print("Correo enviado correctamente.")

except Exception as e:

    print(f"ERROR SMTP: {e}")

# ============================================================
# GUARDAR ESTADO
# ============================================================

state = {
    "fecha": today_iso,
    "procesos": {},
    "samai": {
        "730013333012202000181017300123": {
            "ultimoIndice": s7.get("maxIdx", 0)
        }
    }
}

for pid, val in new_proc_state.items():

    state["procesos"][pid] = {
        "ultimoIdRegActuacion": val
    }

save_state(state)

print("\nEstado guardado.")
print("Completado.\n")