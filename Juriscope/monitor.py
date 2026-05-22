#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitor Judicial - Python Edition
Consulta:
- Rama Judicial Colombia (casos 1-6)
- SAMAI Consejo de Estado (caso 7)

Envía reportes HTML por correo a:
acidburn11235@gmail.com

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
# CONFIGURACIÓN
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
# SMTP GMAIL
# ============================================================
# IMPORTANTE:
# Usa una APP PASSWORD de Gmail
# NO tu contraseña normal.
#
# https://myaccount.google.com/apppasswords
#
# Exporta estas variables:
#
# export GMAIL_USER="acidburn11235@gmail.com"
# export GMAIL_PASS="TU_APP_PASSWORD"
# ============================================================

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

if not GMAIL_USER or not GMAIL_PASS:
    print("ERROR: faltan variables GMAIL_USER y GMAIL_PASS")
    exit(1)

# ============================================================
# CASOS RAMA JUDICIAL
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
        "filt": "CORTE SUPREMA DE JUSTICIA"
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
        "filt": "JUZGADO DE CIRCUITO"
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
        r = requests.get(url, timeout=TIMEOUT)
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

    m = re.search(r"(\d{2}/\d{2}/\d{4})", raw)

    if m:
        return m.group(1)

    return raw


# ============================================================
# CONSULTA RAMA JUDICIAL
# ============================================================

prev = load_state()

first_run = prev.get("fecha", "") == ""

today_iso = datetime.now().strftime("%Y-%m-%d")
today_str = datetime.now().strftime("%d/%m/%Y")
now_str = datetime.now().strftime("%d/%m/%Y %H:%M")

print(f"Iniciando monitoreo judicial - {now_str}")

blocks = []
new_proc_state = {}

for case in RJ_CASES:

    print(f"Consultando caso {case['n']}...")

    url = (
        f"{API}/Procesos/Consulta/NumeroRadicacion"
        f"?numero={case['rad']}&pagina=1&soloActivos=false"
    )

    proc_resp = get_json(url)

    procesos = proc_resp.get("procesos", []) if proc_resp else []

    if case["filt"]:
        procesos = [
            p for p in procesos
            if case["filt"].lower() in p.get("despacho", "").lower()
        ]

    if not procesos:
        blocks.append({
            "n": case["n"],
            "nm": case["nm"],
            "rad": case["rad"],
            "st": "no_results"
        })
        continue

    procesos.sort(key=lambda x: int(x["idProceso"]), reverse=True)

    proc = procesos[0]

    act_url = f"{API}/Proceso/Actuaciones/{proc['idProceso']}?pagina=1"

    act_resp = get_json(act_url)

    acts = act_resp.get("actuaciones", []) if act_resp else []

    if not acts:
        blocks.append({
            "n": case["n"],
            "nm": case["nm"],
            "rad": case["rad"],
            "st": "no_actuaciones"
        })
        continue

    top_id = int(acts[0]["idRegActuacion"])

    id_proc = str(proc["idProceso"])

    new_proc_state[id_proc] = top_id

    prev_id = prev.get("procesos", {}).get(
        id_proc,
        {}
    ).get("ultimoIdRegActuacion", top_id)

    novedad = (not first_run) and top_id > prev_id

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

print("Consultando SAMAI...")

s7 = {
    "n": 7,
    "nm": "APELACION TRIBUNAL TOLIMA",
    "rad": "73001333301220200018101",
    "st": "error"
}

try:

    session = requests.Session()

    r1 = session.get(SAMAI_URL, timeout=TIMEOUT)

    html = r1.text

    d1 = re.search(r'Lbldato1[^>]*>([^<]+)<', html)
    d2 = re.search(r'Lbldato2[^>]*>([^<]+)<', html)
    d3 = re.search(r'Lbldato3[^>]*>([^<]+)<', html)

    captcha = (
        (d1.group(1).strip() if d1 else "") +
        (d2.group(1).strip() if d2 else "") +
        (d3.group(1).strip() if d3 else "")
    ).replace(" ", "")

    print(f"CAPTCHA: {captcha}")

    viewstate = re.search(
        r'__VIEWSTATE" value="([^"]+)"',
        html
    )

    eventvalidation = re.search(
        r'__EVENTVALIDATION" value="([^"]+)"',
        html
    )

    vsg = re.search(
        r'__VIEWSTATEGENERATOR" value="([^"]+)"',
        html
    )

    payload = {
        "__VIEWSTATE":
            viewstate.group(1) if viewstate else "",
        "__EVENTVALIDATION":
            eventvalidation.group(1) if eventvalidation else "",
        "__VIEWSTATEGENERATOR":
            vsg.group(1) if vsg else "",
        "ctl00$MainContent$TxtCaptcha2":
            captcha,
        "ctl00$MainContent$CmdNoRobot":
            "Continuar"
    }

    r2 = session.post(
        SAMAI_URL,
        data=payload,
        timeout=TIMEOUT
    )

    html2 = r2.text

    acts7 = []

    rows = re.findall(
        r'(?s)<tr[^>]*>(.*?)</tr>',
        html2
    )

    for row in rows:

        cells = re.findall(
            r'(?s)<td[^>]*>(.*?)</td>',
            row
        )

        if len(cells) >= 8:

            idx_raw = re.sub(r"<[^>]+>", "", cells[7]).strip()

            if re.match(r"^\d{5}$", idx_raw):

                fecha = re.sub(r"<[^>]+>", "", cells[2]).strip()

                actuacion = re.sub(
                    r"<[^>]+>",
                    "",
                    cells[3]
                ).strip()

                anotacion = re.sub(
                    r"<[^>]+>",
                    "",
                    cells[4]
                ).strip()

                acts7.append({
                    "idx": int(idx_raw),
                    "fecha": fecha,
                    "actuacion": actuacion,
                    "anotacion": anotacion
                })

    if acts7:

        acts7.sort(
            key=lambda x: x["idx"],
            reverse=True
        )

        max_idx = acts7[0]["idx"]

        prev_idx = prev.get("samai", {}).get(
            "730013333012202000181017300123",
            {}
        ).get("ultimoIndice", max_idx)

        nov7 = (not first_run) and max_idx > prev_idx

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

except Exception as e:

    s7["st"] = "error"
    s7["errMsg"] = str(e)

# ============================================================
# HTML REPORT
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
        <h3>{b['n']}. {escape_html(b['nm'])}</h3>
        <p><b>Radicado:</b> {b['rad']}</p>
        <p><b>Estado:</b> {b['st']}</p>
    """)

    if b.get("last"):

        last = b["last"]

        html_parts.append(f"""
            <p><b>Última actuación:</b>
            {format_date(last.get("fechaActuacion", ""))}</p>

            <p><b>Tipo:</b>
            {escape_html(last.get("actuacion", ""))}</p>

            <p><b>Anotación:</b>
            {escape_html(last.get("anotacion", ""))}</p>
        """)

    if b.get("newActs"):

        html_parts.append("<ul>")

        for na in b["newActs"]:

            html_parts.append(f"""
            <li>
            {format_date(na.get("fechaActuacion", ""))}
            -
            {escape_html(na.get("actuacion", ""))}
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
    <p><b>Fecha:</b> {last7.get('fecha', '')}</p>
    <p><b>Actuación:</b>
    {escape_html(last7.get('actuacion', ''))}</p>

    <p><b>Anotación:</b>
    {escape_html(last7.get('anotacion', ''))}</p>
    """)

html_parts.append("</div>")
html_parts.append("</body></html>")

html_report = "\n".join(html_parts)

# ============================================================
# ENVIAR EMAIL
# ============================================================

print("Enviando correo...")

msg = MIMEMultipart("alternative")

msg["Subject"] = f"Informe Rama Judicial - {today_str}"
msg["From"] = EMAIL_FROM
msg["To"] = EMAIL_TO

part = MIMEText(html_report, "html", "utf-8")

msg.attach(part)

try:

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(GMAIL_USER, GMAIL_PASS)

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

print("Estado guardado.")
print("Completado.")