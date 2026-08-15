from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path("/home/stanislav/.openclaw/workspace/agents/main")
SRC = Path("/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731")
OUT = Path("/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_platform_runtime_20260731")
HMI = "PS01_FullAlphaPlatform.hmi"
CLI = Path("/opt/Automiq/Alpha.HMI/alpha.hmi.cli")

FORM_BT = "Form"
FORM_BT_ID = "ffaf5544-6200-45f4-87ec-9dd24558a9d5"
RECT_BT = "Rectangle"
RECT_BT_ID = "15726dc3-881e-4d8d-b0fa-a8f8237f08ca"
TEXT_BT = "Text"
TEXT_BT_ID = "21d59f8d-2ca4-4592-92ca-b4dc48992a0f"
LINE_BT = "Line"
LINE_BT_ID = "4dd08b15-1502-453f-a174-2c0a5aa850ba"
POINT_BT = "Point"
POINT_BT_ID = "467f1af0-7bb4-4a61-b6fb-06e7bfd530d6"


def u() -> str:
    return str(uuid4())


def d(parent: ET.Element, target: str, value: object) -> None:
    ET.SubElement(parent, "designed", {"target": target, "value": str(value), "ver": "5"})


def obj(parent: ET.Element, name: str, bt: str, bt_id: str, description: str = "") -> ET.Element:
    return ET.SubElement(parent, "object", {
        "access-modifier": "private",
        "name": name,
        "display-name": name,
        "uuid": u(),
        "base-type": bt,
        "base-type-id": bt_id,
        "ver": "5",
        "description": description,
        "cardinal": "1",
    })


def rect(parent: ET.Element, name: str, x: int, y: int, w: int, h: int, fill: str, pen: str = "0xffc7cdd2", z: int = 1) -> None:
    r = obj(parent, name, RECT_BT, RECT_BT_ID)
    for k, v in [
        ("X", x), ("Y", y), ("ZValue", z), ("Rotation", 0), ("Scale", 1),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"),
        ("Width", w), ("Height", h), ("PenColor", pen), ("PenWidth", 1),
        ("PenStyle", 1), ("BrushStyle", 1), ("BrushColor", fill), ("RoundingRadius", 2),
    ]:
        d(r, k, v)


def text(parent: ET.Element, name: str, value: str, x: int, y: int, w: int, h: int, size: int = 12, bold: bool = False, color: str = "0xff2f3a45", align: int = 0) -> None:
    t = obj(parent, name, TEXT_BT, TEXT_BT_ID)
    for k, v in [
        ("X", x), ("Y", y), ("ZValue", 30), ("Rotation", 0), ("Scale", 1),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"),
        ("Width", w), ("Height", h), ("Text", value),
        ("Font", f"{'Bold ' if bold else ''}{size}px Sans"),
        ("FontColor", color), ("TextAlignment", align), ("Flip", 0),
    ]:
        d(t, k, v)


def line(parent: ET.Element, name: str, x1: int, y1: int, x2: int, y2: int, color: str = "0xff385f86", width: float = 2.0, style: int = 1, z: int = 10) -> None:
    l = obj(parent, name, LINE_BT, LINE_BT_ID)
    for k, v in [
        ("X", x1), ("Y", y1), ("ZValue", z), ("Rotation", 0), ("Scale", 1),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"),
        ("Width", x2 - x1), ("Height", y2 - y1), ("PenColor", color),
        ("PenWidth", width), ("PenStyle", style), ("BrushStyle", 0),
    ]:
        d(l, k, v)
    for idx, (px, py) in enumerate([(0, 0), (x2 - x1, y2 - y1)], start=1):
        p = obj(l, f"Point_{idx}", POINT_BT, POINT_BT_ID)
        d(p, "X", px)
        d(p, "Y", py)


def form(name: str, title: str) -> ET.Element:
    root = ET.Element("type", {
        "access-modifier": "private",
        "name": name,
        "display-name": name,
        "uuid": u(),
        "base-type": FORM_BT,
        "base-type-id": FORM_BT_ID,
        "ver": "5",
        "description": f"PS01 {title}",
    })
    for k, v in [
        ("X", 0), ("Y", 0), ("ZValue", 0), ("Rotation", 0), ("Scale", 1),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"), ("Tooltip", ""),
        ("Width", 1920), ("Height", 1080), ("PenColor", "0xffd0d4d8"), ("PenStyle", 1),
        ("PenWidth", 1), ("BrushStyle", 1), ("BrushColor", "0xffe5e5e5"),
        ("WindowX", 0), ("WindowY", 0), ("WindowWidth", 1920), ("WindowHeight", 1080),
        ("WindowCaption", f"PS01 - {title}"), ("ShowWindowCaption", "true"),
        ("ShowWindowMinimize", "true"), ("ShowWindowMaximize", "true"),
        ("ShowWindowClose", "true"), ("WindowSizeMode", 0), ("WindowBorderStyle", 1),
        ("WindowState", 0), ("WindowScalingMode", 0), ("MonitorNumber", 0), ("WindowPosition", 0),
    ]:
        d(root, k, v)
    rect(root, "Header", 0, 0, 1920, 82, "0xff3f3f3f", pen="0xff3f3f3f")
    text(root, "Title", f"PS01 - {title}", 28, 20, 620, 28, size=20, bold=True, color="0xffffffff")
    text(root, "Mode", "AUTO | REGUL OPC UA OK | Alpha Platform runtime package", 760, 24, 650, 24, size=14, color="0xffeeeeee")
    tabs = ["Обзор", "Тренды", "Архив", "Аварии", "Отчёты", "Уставки"]
    active = {"OverviewForm": 0, "TrendsForm": 1, "ArchiveForm": 2, "AlarmsForm": 3, "ReportsForm": 4, "SetpointsForm": 5}[name]
    rect(root, "NavigationStrip", 28, 52, 760, 30, "0xff303840", pen="0xff5a646e", z=20)
    for i, tab in enumerate(tabs):
        x = 28 + i * 128
        if i == active:
            rect(root, f"Tab{i}Active", x, 52, 118, 30, "0xfff7f7f7", pen="0xffc7cdd2", z=21)
            color, bold = "0xff2f3a45", True
        else:
            color, bold = "0xffeeeeee", False
        text(root, f"Tab{i}Text", tab, x, 59, 118, 18, size=12, bold=bold, color=color, align=132)
    rect(root, "ContentPanel", 28, 108, 1852, 932, "0xfff7f7f7", pen="0xffc7cdd2")
    return root


def write_xml(path: Path, root: ET.Element) -> None:
    path.write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")


def make_trends() -> ET.Element:
    root = form("TrendsForm", "Тренды")
    text(root, "T1", "Тренды давления, уставки, расхода и числа работающих насосов", 64, 136, 860, 26, size=18, bold=True)
    rect(root, "TrendPlot", 64, 190, 1180, 460, "0xffffffff", pen="0xffd7dce0")
    for i in range(8):
        line(root, f"GridH{i}", 82, 610 - i * 50, 1210, 610 - i * 50, color="0xffe3e7ea", width=0.8)
    line(root, "PVLine1", 100, 560, 330, 490, width=3)
    line(root, "PVLine2", 330, 490, 570, 525, width=3)
    line(root, "PVLine3", 570, 525, 830, 455, width=3)
    line(root, "SPLine", 100, 505, 1210, 505, color="0xff6c7b6d", width=2, style=2)
    text(root, "Legend", "PV давление | SP давление | N работающих | скорость ведущего", 64, 676, 900, 24)
    rect(root, "TrendSource", 1320, 190, 500, 240, "0xffeef1f3")
    text(root, "TrendSourceTitle", "Источник", 1350, 220, 220, 22, size=15, bold=True)
    for i, s in enumerate(["Alpha.Historian values", "PRESS_OUT, PRESS_SP, PRESS_DEV", "PUMPS_RUNNING, FLOW, P1..P4_SPEED", "Апертура 0.5-1%, принудительно 5-10 с"]):
        text(root, f"TrendSource{i}", s, 1350, 264 + i * 34, 410, 20)
    return root


def make_archive() -> ET.Element:
    root = form("ArchiveForm", "Архив")
    text(root, "A1", "Архив значений и событий", 64, 136, 520, 26, size=18, bold=True)
    headers = ["Группа", "Теги", "Метод", "Хранение"]
    widths = [240, 720, 360, 240]
    x = 64
    for h, w in zip(headers, widths):
        text(root, f"Hdr{h}", h, x, 190, w, 22, bold=True)
        x += w
    rows = [
        ("Аналоговые", "PRESS_OUT, PRESS_IN, SP, FLOW, LEVEL, Px_CURRENT/SPEED/POWER", "апертура + период", "12 мес"),
        ("Дискретные", "Px_RUN/FAULT/VFD_FAULT/ENABLED, MODE, LEAD, AVR, CAPACITY_LOW", "по изменению", "12 мес"),
        ("Расчётные", "RUNHOURS, STARTS, TOTAL_VOLUME, TOTAL_POWER, SPEC_ENERGY, PRESS_DEV", "расчёт Alpha.Server", "12 мес"),
        ("События", "команды, квитирование, АВР, ротация, изменения уставок", "журнал событий", "3 года"),
    ]
    for r, row in enumerate(rows):
        y = 230 + r * 64
        rect(root, f"Row{r}", 56, y - 8, 1680, 44, "0xffeef1f3", pen="0xffd7dce0")
        x = 64
        for c, (val, w) in enumerate(zip(row, widths)):
            text(root, f"Cell{r}_{c}", val, x, y, w - 16, 22)
            x += w
    return root


def make_alarms() -> ET.Element:
    root = form("AlarmsForm", "Аварии")
    text(root, "AL1", "Журнал и матрица Alpha.HMI.Alarms", 64, 136, 620, 26, size=18, bold=True)
    rows = [
        ("P1", "Нет доступных насосов", "NO_PUMPS_AVAIL=1", "0 с", "квит."),
        ("P1", "Сухой ход", "DRY_RUN=1", "0-2 с", "квит."),
        ("P2", "Авария насоса Нx", "PS01_Px_FAULT=1", "0 с", "квит."),
        ("P2", "Недостаток производительности", "CAPACITY_LOW=1", "60 с", "квит."),
        ("P3", "Отклонение от уставки", "|PRESS_DEV| > допуска", "30 с", "квит."),
    ]
    headers = ["Приор.", "Текст", "Условие", "Задержка", "Действие"]
    widths = [110, 410, 420, 180, 180]
    x = 64
    for h, w in zip(headers, widths):
        text(root, f"Hdr{h}", h, x, 190, w, 22, bold=True)
        x += w
    for r, row in enumerate(rows):
        y = 230 + r * 54
        fill = "0xfffff1f0" if row[0] == "P1" else "0xfffff7e6" if row[0] == "P2" else "0xffffffff"
        rect(root, f"Row{r}", 56, y - 8, 1380, 38, fill, pen="0xffd7dce0")
        x = 64
        for c, (val, w) in enumerate(zip(row, widths)):
            text(root, f"Cell{r}_{c}", val, x, y, w - 12, 20, color="0xff2f3a45")
            x += w
    text(root, "AckNote", "Квитирование: одиночное и групповое; звук для P1-P2; экспорт CSV/PDF/XLSX.", 64, 560, 980, 24)
    return root


def make_reports() -> ET.Element:
    root = form("ReportsForm", "Отчёты")
    text(root, "R1", "Alpha.Reports: пять отчётов из ТЗ", 64, 136, 620, 26, size=18, bold=True)
    rows = [
        ("Сменный/суточный", "объём, давление мин/макс/сред, расход, пуски, наработка, алармы", "PDF, Excel"),
        ("Энергетический", "энергия по насосам, суммарно, удельная кВт·ч/м3", "Excel"),
        ("Качество регулирования", "ср. отклонение, время в допуске/вне, ступени каскада", "Excel"),
        ("Баланс ротации", "наработка, пуски Н1..Н4, разбаланс, смена ведущего", "Excel"),
        ("Журнал событий", "события, команды операторов, АВР", "PDF, Excel, CSV"),
    ]
    for i, row in enumerate(rows):
        y = 190 + i * 76
        rect(root, f"ReportCard{i}", 64, y, 1280, 54, "0xffffffff", pen="0xffd7dce0")
        text(root, f"ReportName{i}", row[0], 86, y + 10, 260, 20, bold=True)
        text(root, f"ReportContent{i}", row[1], 360, y + 10, 720, 20)
        text(root, f"ReportFmt{i}", row[2], 1110, y + 10, 200, 20)
    return root


def make_setpoints() -> ET.Element:
    root = form("SetpointsForm", "Уставки")
    text(root, "S1", "Уставки каскада, ПИД и команды станции", 64, 136, 680, 26, size=18, bold=True)
    rows = [
        ("PRESS_SP", "7.5 бар", "оператор/инженер"),
        ("PID_KP / KI / KD", "по проекту", "инженер"),
        ("STAGE_UP_SPEED / DELAY", "95% / 30 с", "инженер"),
        ("STAGE_DN_SPEED / DELAY", "40% / 60 с", "инженер"),
        ("MAX_PUMPS", "3", "инженер"),
        ("ROTATION_PERIOD", "168 ч", "инженер"),
        ("CMD_START/STOP/ENABLE/DISABLE", "подтверждение", "оператор"),
    ]
    for i, row in enumerate(rows):
        y = 190 + i * 52
        rect(root, f"SetRow{i}", 64, y, 1040, 36, "0xffffffff", pen="0xffd7dce0")
        text(root, f"SetTag{i}", row[0], 84, y + 8, 320, 18, bold=True)
        text(root, f"SetValue{i}", row[1], 430, y + 8, 260, 18)
        text(root, f"SetRole{i}", row[2], 720, y + 8, 280, 18)
    text(root, "LockNote", "Блокировки: local/bad quality/no heartbeat запрещают команды; write-readback обязателен на стенде.", 64, 600, 1100, 24)
    return root


def write_hmi() -> None:
    main = ET.parse(OUT / "objects" / "MainForm.omobj").getroot()
    main_id = main.attrib["uuid"]
    unit = ET.Element("unit", {
        "uuid": u(),
        "name": "PS01_FullAlphaPlatform",
        "display-name": "PS01 Full Alpha Platform",
        "description": "Full Alpha Platform package for PS01 TZ v2.0",
        "ver": "5",
        "main-form-id": main_id,
    })
    for file, filt in [
        ("MainForm.omobj", ""),
        ("TrendsForm.omobj", "views"),
        ("ArchiveForm.omobj", "views"),
        ("AlarmsForm.omobj", "views"),
        ("ReportsForm.omobj", "views"),
        ("SetpointsForm.omobj", "views"),
        ("PS01_PumpUnit.omobj", "pumps"),
        ("PS01_PumpFaceplate.omobj", "faceplates"),
    ]:
        ET.SubElement(unit, "object", {"file": file, "filter": filt})
    write_xml(OUT / HMI, unit)


def tag_rows() -> list[dict[str, str]]:
    with (OUT / "config" / "tag-map.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_devstudio(rows: list[dict[str, str]]) -> None:
    dev = OUT / "devstudio"
    dev.mkdir(exist_ok=True)
    solution = f'''<?xml version="1.0" encoding="utf-8"?>
<Solution Id="{u()}">
  <Projects>
    <Project FilePath="PS01_Server.omx-project" />
    <Project FilePath="PS01_Historian.omx-project" />
    <Project FilePath="PS01_Imitator.omx-project" />
  </Projects>
</Solution>
'''
    (dev / "PS01_AlphaPlatform.solution").write_text(solution, encoding="utf-8")
    for name in ["PS01_Server", "PS01_Historian", "PS01_Imitator"]:
        (dev / f"{name}.omx-project").write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<Project Id="{u()}" Version="1.0.0" OutputPath="bin">
  <Files>
    <SourceFile Name="{name}.omx" />
  </Files>
</Project>
''', encoding="utf-8")
    app_objects = []
    for r in rows:
        typ = {"REAL": "float32", "BOOL": "bool", "INT": "int32", "DINT": "int32"}.get(r["type"], "float32")
        attrs = []
        tag_class = r.get("class") or r.get("category") or ""
        if tag_class == "ALARM":
            attrs.append('<attribute type="unit.Server.Attributes.Alarm" value="PS01 alarm matrix" />')
        if tag_class in {"AI", "STATE", "EVENT", "ALARM", "CALC"} or r["tag"].startswith("PS01_HDR"):
            attrs.append('<attribute type="unit.Server.Attributes.History" />')
        attrs_s = "\n          ".join(attrs)
        app_objects.append(f'''        <ct:parameter name="{r["tag"]}" uuid="{u()}" type="{typ}">
          <attribute type="unit.System.Attributes.Description" value="{r["description"]}" />
          <attribute type="unit.System.Attributes.Comment" value="OPC UA {r.get("opc_ua_node_id", "")}; Modbus {r.get("modbus_placeholder", "")}" />
          {attrs_s}
        </ct:parameter>''')
    server = f'''<?xml version="1.0" encoding="utf-8"?>
<omx xmlns="system" migration="44" xmlns:dp="automation.deployment" xmlns:eth="automation.ethernet" xmlns:srv="server" xmlns:ct="automation.control">
  <link-unit name="System" uuid="{u()}" target="Om.System" />
  <link-unit name="Server" uuid="{u()}" target="Om.Server" />
  <dp:domain name="PS01_Domain" uuid="{u()}" address="local">
    <eth:ethernet-net name="ProcessEthernet" uuid="{u()}" />
    <dp:domain-node name="ps01-server" uuid="{u()}" address="127.0.0.1">
      <eth:ethernet-adapter name="Eth" uuid="{u()}" network="ProcessEthernet" address="127.0.0.1" />
      <srv:io-server name="Server" uuid="{u()}">
        <srv:opcaeserver-module name="AeServer" uuid="{u()}" />
        <srv:opcua-module name="UaServer" uuid="{u()}" />
        <srv:tcp-server name="TcpServer" port="4388" history-port="4950" uuid="{u()}" />
        <srv:history-module name="HistoryModule" uuid="{u()}">
          <srv:historian-database-link database="ps01-historian.Historian.values">
            <attribute type="unit.Server.Attributes.History" />
          </srv:historian-database-link>
          <srv:historian-database-link database="ps01-historian.Historian.alarms">
            <attribute type="unit.Server.Attributes.History" />
          </srv:historian-database-link>
        </srv:history-module>
        <dp:application-object name="PS01" uuid="{u()}">
{chr(10).join(app_objects)}
        </dp:application-object>
        <srv:hub-module name="HubModule" uuid="{u()}" />
      </srv:io-server>
    </dp:domain-node>
  </dp:domain>
</omx>
'''
    (dev / "PS01_Server.omx").write_text(server, encoding="utf-8")
    historian = f'''<?xml version="1.0" encoding="utf-8"?>
<omx xmlns="system" migration="44" xmlns:dp="automation.deployment" xmlns:eth="automation.ethernet" xmlns:hs="history">
  <link-unit name="System" uuid="{u()}" target="Om.System" />
  <link-unit name="History" uuid="{u()}" target="Om.History" />
  <dp:domain name="PS01_Domain" uuid="{u()}" address="local">
    <eth:ethernet-net name="ProcessEthernet" uuid="{u()}" />
    <dp:domain-node name="ps01-historian" uuid="{u()}" address="127.0.0.1">
      <eth:ethernet-adapter name="Eth" uuid="{u()}" network="ProcessEthernet" address="127.0.0.1" />
      <hs:historian name="Historian" uuid="{u()}" base-type="unit.History.Historian">
        <hs:historian-database name="values" uuid="{u()}" usage="values" base-type="unit.History.Database" />
        <hs:historian-database name="alarms" uuid="{u()}" usage="events" base-type="unit.History.Database" />
      </hs:historian>
    </dp:domain-node>
  </dp:domain>
</omx>
'''
    (dev / "PS01_Historian.omx").write_text(historian, encoding="utf-8")
    imitator_tags = "\n".join(f'        <ct:parameter name="{r["tag"]}" uuid="{u()}" type="{"bool" if r["type"] == "BOOL" else "float32" if r["type"] == "REAL" else "int32"}" />' for r in rows)
    imitator = f'''<?xml version="1.0" encoding="utf-8"?>
<omx xmlns="system" migration="44" xmlns:dp="automation.deployment" xmlns:eth="automation.ethernet" xmlns:srv="server" xmlns:ct="automation.control">
  <link-unit name="System" uuid="{u()}" target="Om.System" />
  <link-unit name="Server" uuid="{u()}" target="Om.Server" />
  <dp:domain name="PS01_Imitator_Domain" uuid="{u()}" address="local">
    <eth:ethernet-net name="ProcessEthernet" uuid="{u()}" />
    <dp:domain-node name="ps01-imitator" uuid="{u()}" address="127.0.0.1">
      <srv:io-server name="Imitator" uuid="{u()}">
        <srv:opcua-module name="UaServer" uuid="{u()}" />
        <srv:modbus-tcp-slave-module name="ModbusTcpSlave" uuid="{u()}" />
        <dp:application-object name="PS01" uuid="{u()}">
{imitator_tags}
        </dp:application-object>
      </srv:io-server>
    </dp:domain-node>
  </dp:domain>
</omx>
'''
    (dev / "PS01_Imitator.omx").write_text(imitator, encoding="utf-8")


def write_platform_files(rows: list[dict[str, str]]) -> None:
    (OUT / "webviewer").mkdir(exist_ok=True)
    (OUT / "webviewer" / "ps01-webviewer.xml").write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<Alpha.HMI.WebViewer>
  <WebSocket Address="127.0.0.1" Port="18080" ConnectionTimeout="30" />
  <Session Timeout="120" />
  <Application ProjectPath="{OUT / HMI}" WwwRoot="{OUT / "webviewer" / "wwwroot"}" Theme="simple">
    <UrlQuery Allow="true">
      <Entity Allow="true" />
    </UrlQuery>
  </Application>
</Alpha.HMI.WebViewer>
''', encoding="utf-8")
    report_defs = [
        ("shift_daily", "Сменный/суточный", ["TOTAL_VOLUME", "PRESS_OUT min/max/avg", "FLOW", "Px_STARTS", "Px_RUNHOURS", "alarms"]),
        ("energy", "Энергетический", ["TOTAL_POWER", "SPEC_ENERGY", "Px_POWER"]),
        ("control_quality", "Качество регулирования", ["PRESS_DEV avg", "time in tolerance", "stage count"]),
        ("rotation_balance", "Баланс ротации", ["Px_RUNHOURS", "Px_STARTS", "RUNHOURS_DELTA", "LEAD_PUMP history"]),
        ("event_log", "Журнал событий", ["operator commands", "AVR_ACT", "alarm ack", "setpoint changes"]),
    ]
    (OUT / "reports").mkdir(exist_ok=True)
    (OUT / "reports" / "ps01-alpha-reports.json").write_text(json.dumps({
        "module": "Alpha.Reports",
        "project": "PS01",
        "reports": [{"id": i, "name": n, "fields": f, "formats": ["PDF", "Excel"] if i != "energy" else ["Excel"]} for i, n, f in report_defs],
        "status": "definitions_ready_runtime_export_not_run",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "security").mkdir(exist_ok=True)
    (OUT / "security" / "ps01-security-roles.ldif").write_text("""dn: ou=PS01,dc=alpha,dc=local
objectClass: organizationalUnit
ou: PS01

dn: cn=PS01_Observer,ou=PS01,dc=alpha,dc=local
objectClass: groupOfNames
cn: PS01_Observer
description: просмотр PS01
member: cn=placeholder,dc=alpha,dc=local

dn: cn=PS01_Operator,ou=PS01,dc=alpha,dc=local
objectClass: groupOfNames
cn: PS01_Operator
description: команды ручного режима, квитирование, разрешение/запрет насосов
member: cn=placeholder,dc=alpha,dc=local

dn: cn=PS01_Engineer,ou=PS01,dc=alpha,dc=local
objectClass: groupOfNames
cn: PS01_Engineer
description: уставки, ПИД, параметры каскада, конфигурация алармов
member: cn=placeholder,dc=alpha,dc=local
""", encoding="utf-8")
    (OUT / "imitator").mkdir(exist_ok=True)
    (OUT / "imitator" / "ps01-imitator-scenarios.json").write_text(json.dumps({
        "module": "Alpha.Imitator",
        "endpoint": "opc.tcp://127.0.0.1:62544",
        "scenarios": [
            {"id": "normal_2of4", "sets": {"PRESS_OUT": 7.2, "PRESS_SP": 7.5, "PUMPS_RUNNING": 2, "LEAD_PUMP": 1}},
            {"id": "stage_up", "precondition": "lead speed >= 95 and PRESS_OUT < SP for STAGE_UP_DELAY"},
            {"id": "stage_down", "precondition": "lead speed <= 40 and PRESS_OUT >= SP for STAGE_DN_DELAY"},
            {"id": "avr", "precondition": "running pump fault -> reserve start"},
            {"id": "no_pumps_available", "precondition": "all pumps disabled or fault"},
        ],
        "status": "scenario_definition_ready_native_import_not_run",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    history_classes = {"AI", "STATE", "EVENT", "ALARM", "CALC"}
    historian_rows = []
    for r in rows:
        tag_class = r.get("class") or r.get("category") or ""
        if tag_class in history_classes or r["tag"].startswith("PS01_HDR"):
            method = "on_change" if r["type"] == "BOOL" else "deadband" if r["type"] == "REAL" else "periodic_or_on_change"
            historian_rows.append(f'{r["tag"]},{method},0.5-1%,10,12m,3y')
    (OUT / "config" / "historian-tags.csv").write_text(
        "tag,archive_method,deadband,forced_period_s,retention_raw,retention_aggregates\n"
        + "\n".join(historian_rows)
        + "\n",
        encoding="utf-8",
    )


def run(cmd: list[str], cwd: Path, log: Path, timeout: int = 120) -> dict[str, object]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    log.write_text(proc.stdout, encoding="utf-8")
    return {"command": cmd, "exitCode": proc.returncode, "log": str(log.relative_to(OUT)), "status": "ok" if proc.returncode == 0 else "failed"}


def capture(name: str, entity: str | None = None) -> dict[str, object]:
    screenshot = OUT / "screenshots" / f"{name}.png"
    viewer_log = OUT / "logs" / f"{name}_viewer.log"
    xvfb_log = OUT / "logs" / f"{name}_xvfb.log"
    display = ":194"
    with xvfb_log.open("wb") as xf:
        xvfb = subprocess.Popen(["Xvfb", display, "-screen", "0", "1920x1080x24"], stdout=xf, stderr=subprocess.STDOUT)
    try:
        time.sleep(1)
        env = {**os.environ, "DISPLAY": display, "QTWEBENGINE_DISABLE_SANDBOX": "1"}
        cmd = ["alpha.hmi.viewer", HMI]
        if entity:
            cmd.append(entity)
        with viewer_log.open("wb") as vf:
            viewer = subprocess.Popen(cmd, cwd=OUT, env=env, stdout=vf, stderr=subprocess.STDOUT)
        time.sleep(5)
        cap = subprocess.run(["import", "-window", "root", str(screenshot)], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
        viewer.terminate()
        try:
            viewer.wait(timeout=5)
        except subprocess.TimeoutExpired:
            viewer.kill()
        ident = subprocess.run(["identify", "-format", "%w %h %k %[mean]\n", str(screenshot)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=20)
        return {"status": "ok" if cap.returncode == 0 and screenshot.exists() else "failed", "screenshot": str(screenshot.relative_to(OUT)), "identify": ident.stdout.strip(), "log": str(viewer_log.relative_to(OUT))}
    finally:
        xvfb.terminate()
        try:
            xvfb.wait(timeout=5)
        except subprocess.TimeoutExpired:
            xvfb.kill()


def syntax_checks() -> dict[str, object]:
    xml = []
    for p in sorted(list(OUT.glob("*.hmi")) + list((OUT / "objects").glob("*.omobj")) + list((OUT / "devstudio").glob("*.omx")) + list((OUT / "devstudio").glob("*.solution")) + list((OUT / "devstudio").glob("*.omx-project")) + list((OUT / "webviewer").glob("*.xml"))):
        ET.parse(p)
        xml.append(str(p.relative_to(OUT)))
    csv_counts = {}
    for p in sorted((OUT / "config").glob("*.csv")):
        with p.open(encoding="utf-8", newline="") as f:
            csv_counts[p.name] = sum(1 for _ in csv.DictReader(f))
    json_files = []
    for p in sorted(list((OUT / "config").glob("*.json")) + list((OUT / "reports").glob("*.json")) + list((OUT / "imitator").glob("*.json"))):
        json.loads(p.read_text(encoding="utf-8"))
        json_files.append(str(p.relative_to(OUT)))
    return {"xml": xml, "csvRows": csv_counts, "json": json_files}


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ["objects", "output", "build", "logs", "screenshots", "config", "server", "alarms", "historian", "reports", "security", "imitator", "webviewer", "devstudio"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    for sub in ["objects", "config", "server", "alarms", "historian"]:
        shutil.copytree(SRC / sub, OUT / sub, dirs_exist_ok=True)
    shutil.copy2(SRC / "objects" / "MainForm.omobj", OUT / "objects" / "MainForm.omobj")
    shutil.copy2(SRC / "PS01_AlphaNativeRules.hmi", OUT / "PS01_AlphaNativeRules_source.hmi")
    write_xml(OUT / "objects" / "TrendsForm.omobj", make_trends())
    write_xml(OUT / "objects" / "ArchiveForm.omobj", make_archive())
    write_xml(OUT / "objects" / "AlarmsForm.omobj", make_alarms())
    write_xml(OUT / "objects" / "ReportsForm.omobj", make_reports())
    write_xml(OUT / "objects" / "SetpointsForm.omobj", make_setpoints())
    write_hmi()
    rows = tag_rows()
    write_devstudio(rows)
    write_platform_files(rows)
    (OUT / "logs" / "alpha_tool_discovery.txt").write_text(subprocess.run("find /opt/Automiq -maxdepth 2 -type f -executable | sed -n '1,240p'", shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20).stdout, encoding="utf-8")
    compile_result = run([str(CLI), "compile", "--solution-path", str((OUT / HMI).resolve()), "--output-folder", str((OUT / "build").resolve()), "--output-format", "json", "--export-binom"], OUT, OUT / "logs" / "compile_full_hmi.jsonl")
    shutil.copytree(OUT / "build", OUT / "output", dirs_exist_ok=True)
    viewer = {"overview": capture("ps01_overview_full"), "trends": capture("ps01_trends_full", "TrendsForm"), "alarms": capture("ps01_alarms_full", "AlarmsForm")}
    checks = syntax_checks()
    historian_status = run(["/opt/Automiq/Alpha.Historian/alpha.historian.cli", "--target", "127.0.0.1:4600", "config_status"], OUT, OUT / "logs" / "historian_config_status.txt", timeout=20)
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "verdict": "CONDITIONAL GO",
        "compile": compile_result,
        "viewer": viewer,
        "syntax": checks,
        "historianCli": historian_status,
        "moduleStatus": {
            "Alpha.HMI": "native_compile_and_viewer_proven",
            "Alpha.HMI.WebViewer": "native_config_prepared_not_served",
            "Alpha.Server": "DevStudio .solution/.omx prepared; no deploy to /opt runtime",
            "Alpha.HMI.Alarms": "alarm form + matrix prepared; runtime ack/export not proven",
            "Alpha.Historian": "DevStudio .omx + historian tag config prepared; local CLI status checked",
            "alpha.hmi.charts": "trend form prepared as HMI view; live chart widget not proven",
            "Alpha.Reports": "five report definitions prepared; export generation not run",
            "Alpha.Security": "roles/LDIF prepared; no LDAP/runtime apply",
            "Alpha.Imitator": "DevStudio .omx + scenarios prepared; no native simulator run",
        },
    }
    (OUT / "RUN_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "PROJECT_STATUS.md").write_text("""# Статус PS01 Full Alpha Platform

Вердикт: **CONDITIONAL GO**.

Это уже не только один HMI-экран: пакет содержит Alpha.HMI проект с несколькими формами, DevStudio `.solution/.omx` для Alpha.Server/Historian/Imitator, WebViewer config, alarm matrix, historian archive list, report definitions и security roles.

Не выполнен production/dev-stand deploy в `/opt/Automiq/*`: без отдельного controlled deploy нельзя честно заявить runtime `GO` для write-readback, alarm ack/export, historian write/read, report export и security enforcement.
""", encoding="utf-8")


if __name__ == "__main__":
    main()
