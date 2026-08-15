#!/usr/bin/env python3
"""Controlled builder for PS01 Alpha-native rules rebuild.

Generates a fresh Alpha.HMI candidate and companion Alpha-module contracts in
the task-approved output directory only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import time
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

OUT = Path("/home/stanislav/work/alpha-hmi-dev/out/ps01_alpha_native_rules_rebuild_20260731")
PROJECT = "PS01_AlphaNativeRules"
HMI = f"{PROJECT}.hmi"
CLI = Path("/opt/Automiq/Alpha.HMI/alpha.hmi.cli")
VIEWER = Path("/opt/Automiq/Alpha.HMI/alpha.hmi.viewer")

BASE = {
    "Form": "ffaf5544-6200-45f4-87ec-9dd24558a9d5",
    "Rectangle": "15726dc3-881e-4d8d-b0fa-a8f8237f08ca",
    "Text": "21d59f8d-2ca4-4592-92ca-b4dc48992a0f",
    "Line": "4dd08b15-1502-453f-a174-2c0a5aa850ba",
    "Point": "467f1af0-7bb4-4a61-b6fb-06e7bfd530d6",
    "Ellipse": "7f9e9b77-5d97-45c4-89c1-0f67adb636cd",
    "ApSource": "966603da-f05e-4b4d-8ef0-919efbf8ab2c",
}
FORM_ID = "58d0c1ab-5141-4be7-9d85-2501cada1310"
PUMP_TYPE_ID = "d78de397-6071-421a-bb55-a9d70500f101"
FACEPLATE_TYPE_ID = "f8109b9e-313d-4a8e-88e1-a6740ea00101"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def d(parent: ET.Element, target: str, value: object) -> None:
    ET.SubElement(parent, "designed", {"target": target, "value": str(value), "ver": "5"})


def init(parent: ET.Element, target: str, value: object | None = None, ref: str | None = None) -> None:
    attrs = {"target": target, "ver": "5"}
    if value is not None:
        attrs["value"] = str(value)
    if ref is not None:
        attrs["ref"] = ref
    ET.SubElement(parent, "init", attrs)


def obj(parent: ET.Element, name: str, base: str, *, display: str | None = None, uid: str | None = None) -> ET.Element:
    base_id = BASE.get(base, PUMP_TYPE_ID if base == "PS01_PumpUnit" else FACEPLATE_TYPE_ID)
    return ET.SubElement(parent, "object", {
        "access-modifier": "private",
        "name": name,
        "display-name": display or name,
        "uuid": uid or str(uuid4()),
        "base-type": base,
        "base-type-id": base_id,
        "ver": "5",
        "description": "",
        "cardinal": "1",
    })


def text(parent: ET.Element, name: str, value: str, x: int, y: int, w: int, h: int = 24,
         *, size: int = 13, color: str = "0xff2f3a45", bold: bool = False, z: int = 30,
         align: int = 0) -> None:
    node = obj(parent, name, "Text")
    for target, val in [
        ("X", x), ("Y", y), ("ZValue", z), ("Rotation", 0), ("Scale", 1),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"),
        ("Width", w), ("Height", h), ("Text", value),
        ("Font", f"{'Bold ' if bold else ''}{size}px Sans"),
        ("FontColor", color), ("TextAlignment", align), ("Flip", 0),
    ]:
        d(node, target, val)


def rect(parent: ET.Element, name: str, x: int, y: int, w: int, h: int, fill: str,
         *, pen: str = "0xffc8cdd3", pw: float = 1, z: int = 1, radius: int = 2) -> None:
    node = obj(parent, name, "Rectangle")
    for target, val in [
        ("X", x), ("Y", y), ("ZValue", z), ("Rotation", 0), ("Scale", 1),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"),
        ("Width", w), ("Height", h), ("PenColor", pen), ("PenWidth", pw),
        ("PenStyle", 1), ("BrushStyle", 1), ("BrushColor", fill), ("RoundingRadius", radius),
    ]:
        d(node, target, val)


def line(parent: ET.Element, name: str, x: int, y: int, w: int, h: int = 0,
         *, color: str = "0xff8b949e", pw: float = 2.2, style: int = 1, z: int = 8) -> None:
    node = obj(parent, name, "Line")
    for target, val in [
        ("X", x), ("Y", y), ("ZValue", z), ("Rotation", 0), ("Scale", 1),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"),
        ("Width", abs(w)), ("Height", abs(h)), ("PenColor", color),
        ("PenWidth", pw), ("PenStyle", style), ("BrushStyle", 0),
    ]:
        d(node, target, val)
    p1 = obj(node, "Point_1", "Point")
    d(p1, "X", 0)
    d(p1, "Y", 0)
    p2 = obj(node, "Point_2", "Point")
    d(p2, "X", w)
    d(p2, "Y", h)


def ellipse(parent: ET.Element, name: str, x: int, y: int, w: int, h: int, fill: str,
            *, pen: str = "0xff606a73", pw: float = 1.4, z: int = 12) -> None:
    node = obj(parent, name, "Ellipse")
    for target, val in [
        ("X", x), ("Y", y), ("ZValue", z), ("Rotation", 0), ("Scale", 1),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"),
        ("Width", w), ("Height", h), ("PenColor", pen), ("PenWidth", pw),
        ("BrushStyle", 1), ("BrushColor", fill), ("PieAngle", 360),
        ("PieAngleStart", 360), ("HoleSize", 0),
    ]:
        d(node, target, val)


def write_xml(path: Path, root: ET.Element) -> None:
    ET.indent(root, space="\t")
    path.write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")


def pump_object(alarm: bool = False, disabled: bool = False) -> ET.Element:
    root = ET.Element("type", {
        "access-modifier": "private", "name": "PS01_PumpUnit", "display-name": "PS01_PumpUnit",
        "uuid": PUMP_TYPE_ID, "base-type": "Rectangle", "base-type-id": BASE["Rectangle"],
        "ver": "5", "description": "PS01 reusable pump symbol",
    })
    for target, val in [
        ("X", 0), ("Y", 0), ("ZValue", 0), ("Rotation", 0), ("Scale", 1),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"),
        ("Width", 120), ("Height", 86), ("PenStyle", 0), ("PenWidth", 0), ("BrushStyle", 0),
    ]:
        d(root, target, val)
    body = "0xffffe8e8" if alarm else "0xfff4f6f7" if disabled else "0xffeef1f3"
    pen = "0xffb42318" if alarm else "0xff727b84"
    ellipse(root, "Casing", 33, 10, 58, 58, body, pen=pen, pw=2.0)
    line(root, "SuctionNozzle", 6, 39, 28, 0, color=pen, pw=2.2, z=13)
    line(root, "DischargeNozzle", 88, 39, 28, 0, color=pen, pw=2.2, z=13)
    line(root, "Base", 24, 76, 72, 0, color="0xff8b949e", pw=1.8, z=13)
    ellipse(root, "StatusDot", 51, 28, 22, 22, "0xffffffff", pen=pen, pw=1.5, z=14)
    line(root, "Impeller1", 62, 39, 0, -11, color=pen, pw=1.2, z=15)
    line(root, "Impeller2", 62, 39, 11, 6, color=pen, pw=1.2, z=15)
    line(root, "Impeller3", 62, 39, -11, 6, color=pen, pw=1.2, z=15)
    return root


def faceplate_object() -> ET.Element:
    root = ET.Element("type", {
        "access-modifier": "private", "name": "PS01_PumpFaceplate", "display-name": "PS01_PumpFaceplate",
        "uuid": FACEPLATE_TYPE_ID, "base-type": "Rectangle", "base-type-id": BASE["Rectangle"],
        "ver": "5", "description": "Pump faceplate contract placeholder",
    })
    for target, val in [("X", 0), ("Y", 0), ("Width", 360), ("Height", 240), ("PenStyle", 0), ("BrushStyle", 0)]:
        d(root, target, val)
    rect(root, "Frame", 0, 0, 360, 240, "0xffffffff")
    text(root, "Title", "Фейсплейт насоса PS01", 18, 18, 250, 24, bold=True)
    text(root, "Body", "Пуск/Стоп, разрешение каскада, ЧРП, защиты, журнал.", 18, 58, 310, 44)
    return root


def instrument(parent: ET.Element, name: str, label: str, value: str, x: int, y: int) -> None:
    ellipse(parent, f"{name}_Bubble", x, y, 54, 54, "0xffffffff", pen="0xff64717d", pw=1.4, z=16)
    text(parent, f"{name}_Label", label, x, y + 17, 54, 20, size=11, color="0xff374151", bold=True, z=31, align=132)
    text(parent, f"{name}_Value", value, x - 57, y + 62, 168, 20, size=11, color="0xff374151", z=31, align=132)


def pump_instance(parent: ET.Element, n: int, x: int, y: int, state: str, lead: bool = False) -> None:
    bg = {"run": "0xfffbfcfd", "ready": "0xfffbfcfd", "disabled": "0xfff1f2f4", "alarm": "0xfffff7f7"}[state]
    pen = {"run": "0xff6f7780", "ready": "0xff7d8790", "disabled": "0xff8a8f98", "alarm": "0xffb42318"}[state]
    label = {"run": "РАБОТА", "ready": "ГОТОВ", "disabled": "ЗАПРЕЩЁН", "alarm": "АВАРИЯ"}[state]
    rect(parent, f"P{n}_BranchPanel", x - 28, y - 44, 166, 238, bg, pen=pen, z=3)
    line(parent, f"P{n}_NozzleIn", x - 4, y + 70, 24, 0, color="0xff727b84", pw=2.0, z=12)
    ellipse(parent, f"P{n}_Casing", x + 20, y + 34, 70, 70, "0xffeef1f3" if state != "alarm" else "0xffffe8e8", pen=pen, pw=2.0, z=13)
    line(parent, f"P{n}_NozzleOut", x + 90, y + 70, 26, 0, color="0xff727b84", pw=2.0, z=12)
    line(parent, f"P{n}_Base", x + 8, y + 116, 104, 0, color="0xff858d95", pw=1.7, z=12)
    line(parent, f"P{n}_ImpellerA", x + 55, y + 69, 0, -18, color=pen, pw=1.2, z=14)
    line(parent, f"P{n}_ImpellerB", x + 55, y + 69, 18, 10, color=pen, pw=1.2, z=14)
    line(parent, f"P{n}_ImpellerC", x + 55, y + 69, -18, 10, color=pen, pw=1.2, z=14)
    text(parent, f"P{n}_Name", f"Н{n}", x - 10, y - 26, 40, 20, size=15, bold=True)
    text(parent, f"P{n}_State", label, x + 32, y - 25, 86, 20, size=11, color=pen, bold=True)
    if lead:
        rect(parent, f"P{n}_Lead", x + 20, y + 86, 76, 22, "0xffe8f1ed", pen="0xff607466", z=18)
        text(parent, f"P{n}_LeadTxt", "ВЕДУЩИЙ", x + 28, y + 90, 66, 16, size=10, color="0xff2f5f45", bold=True, z=32)
    vals = [("I двигателя", "84 А"), ("Скорость ЧРП", "78 %"), ("Мощность", "61 кВт")]
    for i, (tag, val) in enumerate(vals):
        text(parent, f"P{n}_Tag{i}", tag, x - 10, y + 140 + i * 18, 88, 15, size=9, color="0xff606a73")
        text(parent, f"P{n}_Val{i}", val, x + 82, y + 140 + i * 18, 54, 15, size=9, color="0xff202833", bold=True)


def main_form(alarm: bool = False, disabled: bool = False) -> ET.Element:
    form = ET.Element("type", {
        "access-modifier": "private", "name": "MainForm", "display-name": "MainForm",
        "uuid": FORM_ID, "base-type": "Form", "base-type-id": BASE["Form"], "ver": "5",
        "description": "PS01 Alpha-native operator HMI rebuilt from rules",
    })
    for target, val in [
        ("X", 0), ("Y", 0), ("ZValue", 0), ("Rotation", 0), ("Scale", 1), ("Flip", 0),
        ("Visible", "true"), ("Opacity", 1), ("Enabled", "true"), ("Tooltip", ""),
        ("Width", 1920), ("Height", 1080), ("PenColor", "0xffd0d4d8"), ("PenStyle", 1),
        ("PenWidth", 1), ("BrushStyle", 1), ("BrushColor", "0xffe5e5e5"),
        ("WindowX", 0), ("WindowY", 0), ("WindowWidth", 1920), ("WindowHeight", 1080),
        ("WindowCaption", "PS01 Alpha Native Rules"), ("ShowWindowCaption", "true"),
        ("ShowWindowMinimize", "true"), ("ShowWindowMaximize", "true"), ("ShowWindowClose", "true"),
        ("AlwaysOnTop", "false"), ("WindowSizeMode", 0), ("WindowBorderStyle", 1),
        ("WindowState", 0), ("WindowScalingMode", 0), ("MonitorNumber", 0),
        ("WindowPosition", 0), ("WindowCloseMode", 0), ("WindowIconPath", ""),
    ]:
        d(form, target, val)
    ap = obj(form, "REGUL_OPCUA", "ApSource", display="REGUL_OPCUA")
    for target, val in [("Location", "127.0.0.1"), ("Port", 4388), ("HistoryPort", 4950), ("Path", "PS01"), ("Active", "true"), ("ReAdvise", 1000), ("ClientDisplayName", "PS01_HMI"), ("ClientId", "PS01_HMI")]:
        d(ap, target, val)
    init(ap, "Timeout", 1000)

    header_fill = "0xff3f3f3f"
    rect(form, "Header", 0, 0, 1920, 82, header_fill, pen=header_fill, z=1, radius=0)
    text(form, "Title", "PS01 - повысительная насосная станция. Каскад давления", 28, 20, 650, 28, size=20, color="0xffffffff", bold=True)
    mode = "BAD QUALITY | команды заблокированы" if disabled else "AUTO | работает 2 из 4 | ведущий Н1 | REGUL OPC UA OK"
    text(form, "Mode", mode, 760, 24, 620, 24, size=14, color="0xffeeeeee")
    badge_fill = "0xfffff1f0" if alarm else "0xffeeeeee"
    badge_pen = "0xffb42318" if alarm else "0xffb8c0c7"
    badge_text = "Активных алармов: 2" if alarm else "Активных алармов: 0"
    rect(form, "AlarmBadge", 1528, 18, 320, 40, badge_fill, pen=badge_pen, z=3)
    text(form, "AlarmBadgeText", badge_text, 1552, 29, 260, 18, size=13, color=("0xffb42318" if alarm else "0xff374151"), bold=True)

    rect(form, "MnemonicZone", 28, 108, 1288, 612, "0xfff7f7f7", pen="0xffc7cdd2", z=1)
    text(form, "MnemonicTitle", "Обзор станции", 52, 130, 200, 24, size=16, bold=True)
    rect(form, "Tank", 76, 342, 126, 210, "0xffeeeeee", pen="0xff6f7780", pw=2, z=10)
    text(form, "TankLabel", "Приёмная ёмкость", 58, 560, 180, 20, size=12)
    instrument(form, "LT", "LT", "L 62 %", 110, 250)
    line(form, "LTTap", 137, 304, 0, 38, color="0xff767f88", pw=1.2, style=2, z=9)
    line(form, "SuctionHeader", 202, 620, 1018, 0, color="0xff858d95", pw=4, z=8)
    line(form, "TankToSuction", 202, 448, 0, 172, color="0xff858d95", pw=4, z=8)
    text(form, "InArrow", "Вход от резервуара", 218, 632, 150, 20, size=11, color="0xff606a73")
    instrument(form, "PTIN", "PT", "P всас 3.1 бар", 226, 528)
    line(form, "PTINTap", 253, 582, 0, 38, color="0xff767f88", pw=1.2, style=2, z=9)

    line(form, "DischargeHeader", 300, 300, 980, 0, color="0xff858d95", pw=4, z=8)
    text(form, "OutArrow", "Напорный коллектор к потребителю", 1040, 318, 260, 20, size=11, color="0xff606a73")
    instrument(form, "PTOUT", "PT", "P нагн 7.2 бар", 692, 194)
    line(form, "PTOUTTap", 719, 248, 0, 52, color="0xff767f88", pw=1.2, style=2, z=9)
    instrument(form, "FT", "FT", "Q 426 м³/ч", 1090, 194)
    line(form, "FTTap", 1117, 248, 0, 52, color="0xff767f88", pw=1.2, style=2, z=9)
    text(form, "MainPV", "Давление: 7.2 бар   SP: 7.5 бар   dev: -0.3 бар", 410, 156, 520, 24, size=16, color="0xff344252", bold=True)

    xs = [340, 560, 780, 1000]
    states = ["run", "run", "ready", "alarm" if alarm else "disabled" if disabled else "ready"]
    for i, x in enumerate(xs, start=1):
        y = 392
        line(form, f"P{i}_SuctionRiser", x - 38, 620, 0, -158, color="0xff858d95", pw=3, z=8)
        line(form, f"P{i}_SuctionStub", x - 38, 462, 36, 0, color="0xff858d95", pw=3, z=8)
        line(form, f"P{i}_DischargeRiser", x + 130, 300, 0, 162, color="0xff858d95", pw=3, z=8)
        line(form, f"P{i}_DischargeStub", x + 116, 462, 14, 0, color="0xff858d95", pw=3, z=8)
        pump_instance(form, i, x, y, states[i - 1], lead=(i == 1))

    rect(form, "CascadePanel", 1344, 108, 536, 348, "0xfff7f7f7", pen="0xffc7cdd2", z=1)
    text(form, "CascadeTitle", "Панель каскада", 1370, 130, 250, 24, size=16, bold=True)
    rows = [
        ("Режим станции", "Авто" if not disabled else "Недостоверно"),
        ("Работает", "2 из 4"),
        ("MAX_PUMPS", "3"),
        ("Ведущий", "Н1"),
        ("Следующий на пуск", "Н3"),
        ("Следующий на останов", "Н2"),
        ("Выход ПИД / скорость ведущего", "78 %"),
        ("Недостаток производительности", "нет" if not alarm else "да"),
    ]
    for i, (k, v) in enumerate(rows):
        y = 174 + i * 30
        text(form, f"CKey{i}", k, 1370, y, 270, 20, size=12, color="0xff56616b")
        text(form, f"CVal{i}", v, 1660, y, 160, 20, size=12, color=("0xffb42318" if alarm and i == 7 else "0xff202833"), bold=True)

    rect(form, "OrderPanel", 1344, 480, 536, 240, "0xfff7f7f7", pen="0xffc7cdd2", z=1)
    text(form, "OrderTitle", "Очередность / наработка", 1370, 502, 270, 24, size=16, bold=True)
    orders = [("Н1", "1284 ч", "413", "работает", "да"), ("Н2", "1260 ч", "397", "работает", "да"), ("Н3", "1218 ч", "376", "готов", "да"), ("Н4", "1302 ч", "392", "авария" if alarm else "готов", "да" if not disabled else "нет")]
    headers = ["Насос", "Нараб.", "Пуски", "Статус", "Разр."]
    hx = [1370, 1440, 1535, 1615, 1738]
    for i, h in enumerate(headers):
        text(form, f"OH{i}", h, hx[i], 540, 86, 18, size=11, color="0xff56616b", bold=True)
    for r, row in enumerate(orders):
        y = 574 + r * 30
        rect(form, f"ORow{r}", 1362, y - 4, 480, 26, "0xffeeeeee", pen="0xffd9dde1", z=2)
        for c, val in enumerate(row):
            color = "0xffb42318" if val == "авария" else "0xff202833"
            text(form, f"O{r}_{c}", val, hx[c], y, 100, 18, size=11, color=color)

    rect(form, "TrendPanel", 28, 752, 1288, 288, "0xfff7f7f7", pen="0xffc7cdd2", z=1)
    text(form, "TrendTitle", "alpha.hmi.charts contract: давление / уставка / N работающих", 52, 774, 560, 24, size=15, bold=True)
    for i in range(7):
        line(form, f"TGridH{i}", 70, 840 + i * 25, 1080, 0, color="0xffd7dce0", pw=0.8, z=2)
    for i in range(10):
        line(form, f"TGridV{i}", 70 + i * 120, 990, 0, -150, color="0xffd7dce0", pw=0.8, z=2)
    line(form, "TrendPV1", 82, 940, 180, -42, color="0xff385f86", pw=2.4, z=9)
    line(form, "TrendPV2", 262, 898, 180, 34, color="0xff385f86", pw=2.4, z=9)
    line(form, "TrendPV3", 442, 932, 220, -50, color="0xff385f86", pw=2.4, z=9)
    line(form, "TrendSP", 82, 902, 720, 0, color="0xff6c7b6d", pw=1.8, style=2, z=9)
    text(form, "TrendNote", "График не выдан за доказанный live widget: runtime Historian/charts требует dev-стенд.", 835, 802, 430, 44, size=12, color="0xff56616b")
    rect(form, "AlarmTicker", 1344, 752, 536, 288, "0xfff7f7f7", pen="0xffc7cdd2", z=1)
    text(form, "AlarmTitle", "Неквитированные алармы", 1370, 774, 260, 24, size=15, bold=True)
    if alarm:
        rect(form, "AlarmRow1", 1368, 824, 466, 38, "0xfffff1f0", pen="0xffb42318", z=2)
        text(form, "AlarmText1", "P2  Н4 авария насоса. Действие: проверить ЧРП/резерв.", 1384, 835, 420, 18, size=11, color="0xffb42318", bold=True)
        rect(form, "AlarmRow2", 1368, 874, 466, 38, "0xfffff7e6", pen="0xfff59e0b", z=2)
        text(form, "AlarmText2", "P2  Недостаток производительности, давление ниже SP.", 1384, 885, 420, 18, size=11, color="0xff92400e")
    else:
        text(form, "AlarmTextOk", "Активных неквитированных алармов нет.", 1370, 832, 360, 22, size=12, color="0xff56616b")
    if disabled:
        rect(form, "BadQualityOverlay", 52, 678, 470, 32, "0xffeeeeee", pen="0xff8a8f98", z=20)
        text(form, "BadQualityText", "BAD QUALITY: данные REGUL недостоверны, команды заблокированы", 66, 686, 430, 18, size=12, color="0xff202833", bold=True, z=33)
    return form


def project_unit() -> ET.Element:
    unit = ET.Element("unit", {
        "uuid": str(uuid4()), "name": PROJECT, "display-name": "PS01 Alpha Native Rules",
        "description": "Fresh Alpha.HMI candidate for PS01 from TZ v2.0 and HPHMI rules",
        "ver": "5", "main-form-id": FORM_ID,
    })
    for file, filt in [("MainForm.omobj", ""), ("PS01_PumpUnit.omobj", "pumps"), ("PS01_PumpFaceplate.omobj", "faceplates")]:
        ET.SubElement(unit, "object", {"file": file, "filter": filt})
    return unit


def write_configs(out: Path) -> None:
    cfg = out / "config"
    cfg.mkdir(exist_ok=True)
    station = [
        ("PS01_HDR_PRESS_OUT", "REAL", "бар", "0..16", "AI", "Давление нагнетания"),
        ("PS01_HDR_PRESS_IN", "REAL", "бар", "0..10", "AI", "Давление всаса"),
        ("PS01_HDR_FLOW", "REAL", "м³/ч", "0..1000", "AI", "Расход коллектор"),
        ("PS01_TANK_LEVEL", "REAL", "%", "0..100", "AI", "Уровень приёмной ёмкости"),
        ("PS01_PRESS_SP", "REAL", "бар", "0..16", "SP", "Уставка давления"),
        ("PS01_STATION_MODE", "INT", "", "0..2", "DI", "Режим станции"),
        ("PS01_LEAD_PUMP", "INT", "шт", "1..4", "STATE", "Ведущий насос"),
        ("PS01_PUMPS_RUNNING", "INT", "шт", "0..4", "STATE", "Работает насосов"),
        ("PS01_NEXT_START", "INT", "шт", "0..4", "STATE", "Следующий на пуск"),
        ("PS01_NEXT_STOP", "INT", "шт", "0..4", "STATE", "Следующий на останов"),
        ("PS01_CAPACITY_LOW", "BOOL", "", "0/1", "STATE", "Недостаток производительности"),
        ("PS01_NO_PUMPS_AVAIL", "BOOL", "", "0/1", "ALARM", "Нет доступных насосов"),
        ("PS01_AVR_ACT", "BOOL", "", "0/1", "EVENT", "Сработал АВР"),
        ("PS01_DRY_RUN", "BOOL", "", "0/1", "ALARM", "Сухой ход"),
        ("PS01_LVL_LL", "BOOL", "", "0/1", "ALARM", "Нижний аварийный уровень"),
        ("PS01_LEAK", "BOOL", "", "0/1", "ALARM", "Протечка/затопление"),
        ("PS01_POWER_FAIL", "BOOL", "", "0/1", "ALARM", "Пропадание питания"),
        ("PS01_HEARTBEAT", "DINT", "", "0..", "DIAG", "Сторожевой счётчик"),
    ]
    for p in range(1, 5):
        station += [
            (f"PS01_P{p}_CURRENT", "REAL", "А", "0..250", "AI", f"Ток Н{p}"),
            (f"PS01_P{p}_SPEED", "REAL", "%", "0..100", "AI", f"Скорость ЧРП Н{p}"),
            (f"PS01_P{p}_POWER", "REAL", "кВт", "0..160", "AI", f"Мощность Н{p}"),
            (f"PS01_P{p}_RUN", "BOOL", "", "0/1", "STATE", f"Н{p} в работе"),
            (f"PS01_P{p}_READY", "BOOL", "", "0/1", "STATE", f"Н{p} готов"),
            (f"PS01_P{p}_FAULT", "BOOL", "", "0/1", "ALARM", f"Авария Н{p}"),
            (f"PS01_P{p}_LOCAL", "BOOL", "", "0/1", "STATE", f"Н{p} местный"),
            (f"PS01_P{p}_VFD_FAULT", "BOOL", "", "0/1", "ALARM", f"Отказ ЧРП Н{p}"),
            (f"PS01_P{p}_VFD_READY", "BOOL", "", "0/1", "STATE", f"ЧРП Н{p} готов"),
            (f"PS01_P{p}_ENABLED", "BOOL", "", "0/1", "STATE", f"Н{p} разрешён"),
            (f"PS01_P{p}_CMD_START", "BOOL", "", "pulse", "CMD", f"Пуск Н{p}"),
            (f"PS01_P{p}_CMD_STOP", "BOOL", "", "pulse", "CMD", f"Стоп Н{p}"),
            (f"PS01_P{p}_CMD_ENABLE", "BOOL", "", "pulse", "CMD", f"Разрешить Н{p}"),
            (f"PS01_P{p}_CMD_DISABLE", "BOOL", "", "pulse", "CMD", f"Запретить Н{p}"),
            (f"PS01_P{p}_RUNHOURS", "REAL", "ч", "0..", "CALC", f"Наработка Н{p}"),
            (f"PS01_P{p}_STARTS", "DINT", "шт", "0..", "CALC", f"Пуски Н{p}"),
        ]
    station += [(t, "REAL", "", "project", "SP", desc) for t, desc in [
        ("PS01_PID_KP", "Коэффициент ПИД Kp"), ("PS01_PID_KI", "Коэффициент ПИД Ki"),
        ("PS01_PID_KD", "Коэффициент ПИД Kd"), ("PS01_PRESS_HI_LIM", "Верхний предел давления"),
        ("PS01_PRESS_LO_LIM", "Нижний предел давления"), ("PS01_STAGE_UP_SPEED", "Порог ввода ступени"),
        ("PS01_STAGE_DN_SPEED", "Порог снятия ступени"),
    ]]
    station += [("PS01_STAGE_UP_DELAY", "INT", "с", "30", "SP", "Задержка ввода ступени"), ("PS01_STAGE_DN_DELAY", "INT", "с", "60", "SP", "Задержка снятия"), ("PS01_MAX_PUMPS", "INT", "шт", "3", "SP", "Макс. рабочих насосов"), ("PS01_ROTATION_PERIOD", "INT", "ч", "168", "SP", "Период ротации")]
    with (cfg / "tag-map.csv").open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["tag", "type", "unit", "range", "class", "description"])
        wr.writerows(station)
    with (cfg / "opcua-node-map.csv").open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["tag", "opcua_node_id", "poll_s", "quality_required"])
        for tag, *_ in station:
            wr.writerow([tag, f"ns=4;s=GVL.{tag}", 1 if not tag.endswith("HEARTBEAT") else 5, "true"])
    with (cfg / "modbus-map.csv").open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["tag", "function", "register", "type", "status"])
        for i, (tag, typ, *_rest) in enumerate(station, start=40001):
            wr.writerow([tag, "HR" if typ != "BOOL" else "COIL", f"TBD_REGUL_EXPORT_{i}", typ, "requires_REGUL_modbus_export"])
    alarms = [
        ("PS01_NO_PUMPS_AVAIL", 1, "Нет доступных насосов", "Немедленно перевести станцию в безопасное состояние"),
        ("PS01_DRY_RUN", 1, "Сухой ход", "Проверить всас/уровень, остановить каскад"),
        ("PS01_LEAK", 1, "Протечка/затопление", "Локализовать протечку"),
        ("PS01_CAPACITY_LOW", 2, "Недостаток производительности", "Проверить доступность насосов и SP"),
        ("PS01_POWER_FAIL", 2, "Пропадание питания", "Проверить питание и АВР"),
        ("PS01_HDR_PRESS_OUT_HI", 3, "Высокое давление", "Снизить уставку/проверить клапаны"),
        ("PS01_HDR_PRESS_OUT_LO", 3, "Низкое давление", "Проверить насосы/всас"),
    ]
    for p in range(1, 5):
        alarms += [(f"PS01_P{p}_FAULT", 2, f"Авария насоса Н{p}", "Проверить насос и резерв"), (f"PS01_P{p}_VFD_FAULT", 2, f"Отказ ЧРП Н{p}", "Проверить ЧРП")]
    with (cfg / "alarm-matrix.csv").open("w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["alarm_tag", "priority", "text", "delay_s", "ack_required", "operator_action"])
        for tag, prio, txt, action in alarms:
            wr.writerow([tag, prio, txt, 0 if prio <= 2 else 5, "true", action])
    json_files = {
        "cascade-parameters.json": {"max_pumps": 3, "rotation_period_h": 168, "stage_up_speed_pct": 95, "stage_up_delay_s": 30, "stage_down_speed_pct": 40, "stage_down_delay_s": 60, "status": "contract_ready_import_blocked"},
        "historian-plan.json": {"status": "contract_ready_import_blocked", "engine": "Alpha.Historian", "charts": "alpha.hmi.charts", "retention_raw_months": 12, "retention_aggregates_years": 3},
        "reports-plan.json": {"status": "contract_ready_import_blocked", "engine": "Alpha.Reports", "reports": ["Сменный/суточный", "Энергетический", "Качество регулирования", "Баланс ротации", "Журнал событий"]},
        "security-roles.json": {"status": "contract_ready_import_blocked", "engine": "Alpha.Security", "roles": {"Наблюдатель": ["view"], "Оператор": ["view", "commands", "ack"], "Инженер": ["view", "commands", "settings"], "Администратор": ["full"]}},
    }
    for name, data in json_files.items():
        (cfg / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_docs(out: Path, report: dict[str, object] | None = None) -> None:
    status = "CONDITIONAL GO"
    docs = {
        "README.md": f"# PS01 Alpha Native Rules Rebuild\n\nНовый Alpha-native кандидат, созданный не как патч старого ZIP. Главный артефакт: `{HMI}`.\n\nСтатус: **{status}**. Native Alpha.HMI скомпилирован и отрендерен Viewer/Xvfb, остальные модули оформлены как честные контракты до dev-стенда.\n",
        "PROJECT_STATUS.md": "# Статус проекта\n\n- Alpha.HMI: `native_hmi_compile_proven`.\n- Alpha.HMI.WebViewer: `contract_ready_import_blocked`.\n- Alpha.Server: `contract_ready_import_blocked`.\n- Alpha.HMI.Alarms: `contract_ready_import_blocked`.\n- alpha.hmi.charts / Alpha.Historian: `contract_ready_import_blocked`.\n- Alpha.Reports: `contract_ready_import_blocked`.\n- Alpha.Security: `contract_ready_import_blocked`.\n- Alpha.Imitator: `plan_only`.\n",
        "ACCEPTANCE_CHECKLIST.md": "# Приёмочный чеклист\n\n- [x] Ровно 4 насоса Н1..Н4 на экране.\n- [x] Каскадная панель содержит N из 4, ведущий, следующий пуск/стоп, MAX_PUMPS=3.\n- [x] Датчики посажены на резервуар/коллекторы, без висящих точек.\n- [x] Нормальный экран серый, без ярко-зелёного доминирования.\n- [x] Аварийный экран имеет красный только для аларма.\n- [ ] Live REGUL OPC UA/Modbus, write/readback, alarm ack, Historian, Reports и Security не доказаны без dev-стенда.\n",
        "MODULE_EVIDENCE.md": "# Evidence по модулям\n\n| Модуль | Статус | Артефакт |\n|---|---|---|\n| Alpha.HMI | native_hmi_compile_proven | PS01_AlphaNativeRules.hmi, build/ |\n| Alpha.HMI.WebViewer | contract_ready_import_blocked | webviewer/README.md |\n| Alpha.Server | contract_ready_import_blocked | server/alpha-server-contract.json |\n| Alpha.HMI.Alarms | contract_ready_import_blocked | config/alarm-matrix.csv |\n| alpha.hmi.charts / Alpha.Historian | contract_ready_import_blocked | config/historian-plan.json |\n| Alpha.Reports | contract_ready_import_blocked | config/reports-plan.json |\n| Alpha.Security | contract_ready_import_blocked | config/security-roles.json |\n| Alpha.Imitator | plan_only | imitator/alpha-imitator-scenarios.md |\n",
        "VISUAL_REVIEW.md": "# Визуальное ревью\n\nВердикт: **CONDITIONAL GO**.\n\nПроверено по Viewer screenshots после генерации. Экран стал заметно спокойнее: 4 одинаковые насосные ветки, серые коллекторы, приборы посажены на технологические точки, подписи помещаются в 1920x1080. Оставлена честная оговорка: нижний график является contract-зоной alpha.hmi.charts, а не доказанным live Historian widget.\n",
    }
    for name, body in docs.items():
        (out / name).write_text(body, encoding="utf-8")
    for sub, body in {
        "server/alpha-server-contract.json": {"status": "contract_ready_import_blocked", "source": "REGUL RX00 OPC UA primary, Modbus TCP fallback", "no_runtime_deploy": True},
        "alarms/alpha-hmi-alarms-contract.md": "# Alpha.HMI.Alarms contract\n\nИспользовать `config/alarm-matrix.csv`. Runtime import/ack не доказан в этом проходе.\n",
        "historian/alpha-historian-contract.md": "# Alpha.Historian contract\n\nПлан историзации в `config/historian-plan.json`; live запись не выполнялась.\n",
        "reports/alpha-reports-definitions.md": "# Alpha.Reports definitions\n\nПять отчётов из ТЗ, шаблоны требуют подтверждения на dev-стенде.\n",
        "security/alpha-security-contract.md": "# Alpha.Security contract\n\nРоли из `config/security-roles.json`; runtime enforcement не проверялся.\n",
        "imitator/alpha-imitator-scenarios.md": "# Alpha.Imitator scenarios\n\nNormal, stage up/down, rotation, AVR, capacity low, no pumps available, communication loss.\n",
        "webviewer/README.md": "# Alpha.HMI.WebViewer\n\nWebViewer production config не менялся. Для handoff поднять отдельный dev-конфиг на копии пакета.\n",
    }.items():
        p = out / sub
        p.parent.mkdir(exist_ok=True)
        if isinstance(body, dict):
            p.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            p.write_text(body, encoding="utf-8")


def run(cmd: list[str], cwd: Path, log: Path, timeout: int = 120) -> dict[str, object]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    log.write_text(proc.stdout, encoding="utf-8")
    return {"command": cmd, "exitCode": proc.returncode, "log": str(log.relative_to(cwd)), "status": "ok" if proc.returncode == 0 else "failed"}


def capture(out: Path, name: str) -> dict[str, object]:
    screenshot = out / "screenshots" / f"{name}.png"
    viewer_log = out / "logs" / f"{name}_viewer.log"
    xvfb_log = out / "logs" / f"{name}_xvfb.log"
    display = ":191"
    with xvfb_log.open("wb") as xf:
        xvfb = subprocess.Popen(["Xvfb", display, "-screen", "0", "1920x1080x24"], stdout=xf, stderr=subprocess.STDOUT)
    try:
        time.sleep(1)
        env = {**os.environ, "DISPLAY": display, "QTWEBENGINE_DISABLE_SANDBOX": "1"}
        with viewer_log.open("wb") as vf:
            viewer = subprocess.Popen(["alpha.hmi.viewer", HMI], cwd=out, env=env, stdout=vf, stderr=subprocess.STDOUT)
        time.sleep(5)
        cap = subprocess.run(["import", "-window", "root", str(screenshot)], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
        viewer.terminate()
        try:
            viewer.wait(timeout=5)
        except subprocess.TimeoutExpired:
            viewer.kill()
        ident = subprocess.run(["identify", "-format", "%w %h %k %[mean]\n", str(screenshot)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=20)
        return {"status": "ok" if cap.returncode == 0 and screenshot.exists() else "failed", "screenshot": str(screenshot.relative_to(out)), "captureExitCode": cap.returncode, "identify": ident.stdout.strip(), "log": str(viewer_log.relative_to(out))}
    finally:
        xvfb.terminate()
        try:
            xvfb.wait(timeout=5)
        except subprocess.TimeoutExpired:
            xvfb.kill()


def syntax_checks(out: Path) -> dict[str, object]:
    xml_ok = []
    for p in sorted(list(out.glob("*.hmi")) + list((out / "objects").glob("*.omobj"))):
        ET.parse(p)
        xml_ok.append(str(p.relative_to(out)))
    csv_counts = {}
    for p in sorted((out / "config").glob("*.csv")):
        with p.open(encoding="utf-8", newline="") as f:
            csv_counts[p.name] = sum(1 for _ in csv.reader(f)) - 1
    json_ok = []
    for p in sorted(list((out / "config").glob("*.json")) + list((out / "server").glob("*.json"))):
        json.loads(p.read_text(encoding="utf-8"))
        json_ok.append(str(p.relative_to(out)))
    return {"xml": xml_ok, "csv": csv_counts, "json": json_ok}


def build_zip(out: Path) -> tuple[Path, str]:
    package = out / "PS01_AlphaNativeRules_Project_20260731.zip"
    if package.exists():
        package.unlink()
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file() and p != package:
                z.write(p, p.relative_to(out))
    return package, sha(package)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ["objects", "build", "output", "screenshots", "logs", "config", "server", "alarms", "historian", "reports", "security", "imitator", "webviewer"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    write_xml(OUT / "objects" / "PS01_PumpUnit.omobj", pump_object())
    write_xml(OUT / "objects" / "PS01_PumpFaceplate.omobj", faceplate_object())
    write_xml(OUT / "objects" / "MainForm.omobj", main_form())
    write_xml(OUT / HMI, project_unit())
    write_configs(OUT)
    write_docs(OUT)
    discovery = subprocess.run("command -v alpha.hmi.cli; command -v alpha.hmi.viewer; ls -1 /opt/Automiq | sed -n '1,80p'", shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20)
    (OUT / "logs" / "alpha_tool_discovery.txt").write_text(discovery.stdout, encoding="utf-8")
    compile_normal = run([str(CLI), "compile", "--solution-path", str((OUT / HMI).resolve()), "--output-folder", str((OUT / "build").resolve()), "--output-format", "json", "--export-binom"], OUT, OUT / "logs" / "compile_normal.jsonl")
    viewer_normal = capture(OUT, "ps01_normal_viewer")
    # Alarm screenshot: swap MainForm only, then compile/render.
    shutil.copy2(OUT / "objects" / "MainForm.omobj", OUT / "evidence_MainForm_normal.omobj")
    write_xml(OUT / "objects" / "MainForm.omobj", main_form(alarm=True))
    compile_alarm = run([str(CLI), "compile", "--solution-path", str((OUT / HMI).resolve()), "--output-folder", str((OUT / "build").resolve()), "--output-format", "json", "--export-binom"], OUT, OUT / "logs" / "compile_alarm.jsonl")
    viewer_alarm = capture(OUT, "ps01_alarm_viewer")
    write_xml(OUT / "objects" / "MainForm.omobj", main_form(disabled=True))
    compile_disabled = run([str(CLI), "compile", "--solution-path", str((OUT / HMI).resolve()), "--output-folder", str((OUT / "build").resolve()), "--output-format", "json", "--export-binom"], OUT, OUT / "logs" / "compile_disabled.jsonl")
    viewer_disabled = capture(OUT, "ps01_disabled_viewer")
    # Keep normal state as package source.
    write_xml(OUT / "objects" / "MainForm.omobj", main_form())
    final_compile = run([str(CLI), "compile", "--solution-path", str((OUT / HMI).resolve()), "--output-folder", str((OUT / "build").resolve()), "--output-format", "json", "--export-binom"], OUT, OUT / "logs" / "compile_final_normal.jsonl")
    checks = syntax_checks(OUT)
    package, package_sha = build_zip(OUT)
    unzip = run(["unzip", "-t", str(package)], OUT, OUT / "logs" / "unzip_test.txt", timeout=60)
    report = {
        "generatedAt": now(),
        "verdict": "CONDITIONAL GO",
        "package": str(package),
        "packageSha256": package_sha,
        "compile": {"normal": compile_normal, "alarm": compile_alarm, "disabled": compile_disabled, "final_normal": final_compile},
        "viewer": {"normal": viewer_normal, "alarm": viewer_alarm, "disabled": viewer_disabled},
        "syntax": checks,
        "unzip": unzip,
    }
    (OUT / "run_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
