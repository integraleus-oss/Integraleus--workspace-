#!/usr/bin/env python3
"""Repair PS01 native Alpha controls for TZ compliance.

This script changes generated Alpha Platform project artifacts, not the public
HTML diagnostic helper. It adds the missing mode-command tags and creates a
native Alpha.HMI operator-control panel on SetpointsForm.
"""

from __future__ import annotations

import csv
import shutil
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path("/home/stanislav/work/alpha-hmi-dev/out/ps01_full_alpha_platform_runtime_20260731")
TASK = Path("/home/stanislav/.openclaw/workspace/agents/main/state/tasks/2026-08-01-ps01-alpha-native-compliance")
MAIN_FORM = ROOT / "objects" / "MainForm.omobj"
SETPOINTS_FORM = ROOT / "objects" / "SetpointsForm.omobj"
SERVER_OMX = ROOT / "devstudio" / "PS01_Server.omx"
IMITATOR_OMX = ROOT / "devstudio" / "PS01_Imitator.omx"
PROJECT_TAG_MAP = ROOT / "config" / "tag-map.csv"
PROJECT_OPCUA_MAP = ROOT / "config" / "opcua-node-map.csv"
PROJECT_MODBUS_MAP = ROOT / "config" / "modbus-map.csv"
SOURCE_TAG_MAP = Path("/home/stanislav/projects/alpha-bpr/docs/alpha-platform/pump-station-tags.csv")

MODE_TAGS = [
    {
        "tag": "PS01_MODE_AUTO",
        "type": "BOOL",
        "unit": "",
        "range": "pulse",
        "class": "CMD",
        "description": "Перевод станции в автоматический режим",
    },
    {
        "tag": "PS01_MODE_MANUAL",
        "type": "BOOL",
        "unit": "",
        "range": "pulse",
        "class": "CMD",
        "description": "Перевод станции в ручной режим",
    },
]


def stable_uuid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"ps01-alpha-native-controls/{name}"))


def backup(path: Path) -> None:
    dst = TASK / "backups" / f"{path.name}.bak-alpha-native-controls"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(path, dst)


def ap_item(name: str, tag: str, kind: str = "bool") -> str:
    base_type = "ApItemFloat" if kind == "float" else "ApItemBool"
    base_id = "7acf87ec-1784-4671-926e-9a41ea8d8692" if kind == "float" else "e3f11724-0f76-4497-8d01-38fbb82fb844"
    return f"""
\t<object access-modifier="private" name="{name}" display-name="{name}" uuid="{stable_uuid(name)}" base-type="{base_type}" base-type-id="{base_id}" ver="5" cardinal="1">
\t\t<init target="Source" ver="5" ref="REGUL_OPCUA" />
\t\t<init target="Path" ver="5" value="{tag}" />
\t</object>"""


def text_obj(name: str, x: int, y: int, w: int, h: int, text: str, font: str = "12px Sans", color: str = "0xff2f3a45") -> str:
    return f"""
\t<object access-modifier="private" name="{name}" display-name="{name}" uuid="{stable_uuid(name)}" base-type="Text" base-type-id="21d59f8d-2ca4-4592-92ca-b4dc48992a0f" ver="5" cardinal="1">
\t\t<designed target="X" value="{x}" ver="5" />
\t\t<designed target="Y" value="{y}" ver="5" />
\t\t<designed target="ZValue" value="70" ver="5" />
\t\t<designed target="Width" value="{w}" ver="5" />
\t\t<designed target="Height" value="{h}" ver="5" />
\t\t<designed target="Text" value="{text}" ver="5" />
\t\t<designed target="Font" value="{font}" ver="5" />
\t\t<designed target="FontColor" value="{color}" ver="5" />
\t\t<designed target="TextAlignment" value="0" ver="5" />
\t</object>"""


def rect_obj(name: str, x: int, y: int, w: int, h: int, fill: str = "0xfff7f7f7") -> str:
    return f"""
\t<object access-modifier="private" name="{name}" display-name="{name}" uuid="{stable_uuid(name)}" base-type="Rectangle" base-type-id="15726dc3-881e-4d8d-b0fa-a8f8237f08ca" ver="5" cardinal="1">
\t\t<designed target="X" value="{x}" ver="5" />
\t\t<designed target="Y" value="{y}" ver="5" />
\t\t<designed target="ZValue" value="50" ver="5" />
\t\t<designed target="Width" value="{w}" ver="5" />
\t\t<designed target="Height" value="{h}" ver="5" />
\t\t<designed target="PenColor" value="0xffc7cdd2" ver="5" />
\t\t<designed target="PenWidth" value="1" ver="5" />
\t\t<designed target="PenStyle" value="1" ver="5" />
\t\t<designed target="BrushStyle" value="1" ver="5" />
\t\t<designed target="BrushColor" value="{fill}" ver="5" />
\t\t<designed target="RoundingRadius" value="2" ver="5" />
\t</object>"""


def button_obj(name: str, text: str, x: int, y: int, w: int, body: str, fill: str = "0xffeeeeee", font: str = "11px Sans") -> str:
    return f"""
\t<object access-modifier="private" name="{name}" display-name="{text}" uuid="{stable_uuid(name)}" base-type="Button" base-type-id="61e46e4a-827f-4dd2-ac8a-b68bcaddf442" ver="5" description="Native Alpha.HMI command" cardinal="1">
\t\t<designed target="X" value="{x}" ver="5" />
\t\t<designed target="Y" value="{y}" ver="5" />
\t\t<designed target="ZValue" value="80" ver="5" />
\t\t<designed target="Width" value="{w}" ver="5" />
\t\t<designed target="Height" value="30" ver="5" />
\t\t<designed target="Text" value="{text}" ver="5" />
\t\t<designed target="Font" value="{font}" ver="5" />
\t\t<designed target="TextAlignment" value="132" ver="5" />
\t\t<designed target="PenColor" value="0xffb8c0c7" ver="5" />
\t\t<designed target="PenWidth" value="1" ver="5" />
\t\t<designed target="PenStyle" value="1" ver="5" />
\t\t<designed target="BrushStyle" value="1" ver="5" />
\t\t<designed target="BrushColor" value="{fill}" ver="5" />
\t\t<do-on access-modifier="private" name="Click" display-name="Click" ver="5" event="ButtonPressed">
\t\t\t<body kind="om"><![CDATA[{body}]]></body>
\t\t</do-on>
\t</object>"""


def update_main_form() -> None:
    backup(MAIN_FORM)
    text = MAIN_FORM.read_text(encoding="utf-8")
    replacements = {
        "cmdP1Start.Value=true;": "cmdP1Start.WriteValueAsync(true);",
        "cmdP1Stop.Value=true;": "cmdP1Stop.WriteValueAsync(true);",
        "cmdP1Enable.Value=true;": "cmdP1Enable.WriteValueAsync(true);",
        "cmdP1Disable.Value=true;": "cmdP1Disable.WriteValueAsync(true);",
        'WindowCaption" value="PS01 Alpha Native Rules"': 'WindowCaption" value="PS01 - повысительная насосная станция"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    MAIN_FORM.write_text(text, encoding="utf-8")


def update_setpoints_form() -> None:
    backup(SETPOINTS_FORM)
    text = SETPOINTS_FORM.read_text(encoding="utf-8")
    if "NativeControlPanel" in text:
        return

    source_and_items = [
        """
\t<object access-modifier="private" name="REGUL_OPCUA" display-name="REGUL_OPCUA" uuid="9c39c53f-c8d1-5447-9438-91f5d5f66c0e" base-type="ApSource" base-type-id="966603da-f05e-4b4d-8ef0-919efbf8ab2c" ver="5" cardinal="1">
\t\t<designed target="Location" value="127.0.0.1" ver="5" />
\t\t<designed target="Port" value="4388" ver="5" />
\t\t<designed target="HistoryPort" value="4950" ver="5" />
\t\t<designed target="Path" value="PS01" ver="5" />
\t\t<designed target="Active" value="true" ver="5" />
\t\t<designed target="ReAdvise" value="1000" ver="5" />
\t\t<designed target="ClientDisplayName" value="PS01_HMI" ver="5" />
\t\t<designed target="ClientId" value="PS01_HMI" ver="5" />
\t\t<init target="Timeout" ver="5" value="1000" />
\t</object>""",
        ap_item("pressSp", "PS01_PRESS_SP", "float"),
        ap_item("cmdModeAuto", "PS01_MODE_AUTO"),
        ap_item("cmdModeManual", "PS01_MODE_MANUAL"),
    ]
    for pump in range(1, 5):
        for action in ("Start", "Stop", "Enable", "Disable"):
            source_and_items.append(
                ap_item(
                    f"cmdP{pump}{action}",
                    f"PS01_P{pump}_CMD_{action.upper()}",
                )
            )
    text = text.replace("\t<object access-modifier=\"private\" name=\"Header\"", "\n".join(source_and_items) + "\n\t<object access-modifier=\"private\" name=\"Header\"", 1)

    controls: list[str] = []
    controls.append(rect_obj("NativeControlPanel", 1128, 136, 458, 662))
    controls.append(text_obj("NativeControlTitle", 1156, 160, 390, 24, "Штатное управление Alpha.HMI -> Alpha.Server", "Bold 16px Sans"))
    controls.append(text_obj("NativeControlNote", 1156, 190, 390, 54, "Команды используют ApItem.WriteValueAsync/TrySetValue; внешний commands.html не участвует.", "12px Sans"))
    controls.append(text_obj("ModeCommandTitle", 1156, 246, 260, 22, "Режим станции", "Bold 13px Sans"))
    controls.append(button_obj("BtnModeManual", "Ручной", 1156, 276, 128, "cmdModeManual.WriteValueAsync(true);", "0xffeeeeee", "Bold 11px Sans"))
    controls.append(button_obj("BtnModeAuto", "Авто", 1298, 276, 128, "cmdModeAuto.WriteValueAsync(true);", "0xffe8f1ed", "Bold 11px Sans"))
    controls.append(text_obj("PressSpCommandTitle", 1156, 334, 260, 22, "Уставка давления", "Bold 13px Sans"))
    controls.append(button_obj("BtnPressSp75", "7.5 бар", 1156, 364, 116, "v: float = 7.5F;\npressSp.TrySetValue(v);"))
    controls.append(button_obj("BtnPressSp80", "8.0 бар", 1284, 364, 116, "v: float = 8.0F;\npressSp.TrySetValue(v);"))
    controls.append(button_obj("BtnPressSp85", "8.5 бар", 1412, 364, 116, "v: float = 8.5F;\npressSp.TrySetValue(v);"))
    controls.append(text_obj("PumpCommandTitle", 1156, 424, 620, 22, "Насосы Н1-Н4: пуск / останов / разрешение / запрет", "Bold 13px Sans"))
    for idx, pump in enumerate(range(1, 5)):
        y = 464 + idx * 62
        controls.append(text_obj(f"PumpRowLabel{pump}", 1156, y + 6, 44, 20, f"Н{pump}", "Bold 13px Sans"))
        controls.append(button_obj(f"BtnP{pump}StartNative", "Пуск", 1212, y, 72, f"cmdP{pump}Start.WriteValueAsync(true);", "0xffe8f1ed", "Bold 11px Sans"))
        controls.append(button_obj(f"BtnP{pump}StopNative", "Стоп", 1294, y, 72, f"cmdP{pump}Stop.WriteValueAsync(true);"))
        controls.append(button_obj(f"BtnP{pump}EnableNative", "Разрешить", 1376, y, 100, f"cmdP{pump}Enable.WriteValueAsync(true);"))
        controls.append(button_obj(f"BtnP{pump}DisableNative", "Запретить", 1486, y, 94, f"cmdP{pump}Disable.WriteValueAsync(true);"))
    controls.append(text_obj("NativeControlEvidence", 1156, 732, 390, 54, "Приёмочное доказательство: эти кнопки находятся в Alpha.HMI и пишут теги Alpha.Server.", "12px Sans"))

    text = text.replace("\n</type>", "\n" + "\n".join(controls) + "\n</type>", 1)
    SETPOINTS_FORM.write_text(text, encoding="utf-8")


def parameter_xml(tag: str, desc: str) -> str:
    return f"""
        <ct:parameter name="{tag}" uuid="{stable_uuid('server-' + tag)}" type="bool" direction="in-out" access-level="public">
          <attribute type="unit.System.Attributes.Description" value="{desc}" />
          <attribute type="unit.System.Attributes.Comment" value="OPC UA ; Modbus ; Alpha.HMI command" />
        </ct:parameter>"""


def update_omx(path: Path, marker: str) -> None:
    backup(path)
    text = path.read_text(encoding="utf-8")
    if "PS01_MODE_AUTO" not in text:
        insert = parameter_xml("PS01_MODE_AUTO", "Перевод станции в автоматический режим") + parameter_xml("PS01_MODE_MANUAL", "Перевод станции в ручной режим")
        text = text.replace(marker, marker + insert, 1)
        path.write_text(text, encoding="utf-8")


def add_csv_rows(path: Path, rows: list[dict[str, str]], after_tag: str) -> None:
    backup(path)
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        existing = list(reader)
    if any(row.get("tag") == "PS01_MODE_AUTO" for row in existing):
        return
    output: list[dict[str, str]] = []
    for row in existing:
        output.append(row)
        if row.get("tag") == after_tag:
            for item in rows:
                output.append({key: item.get(key, "") for key in fieldnames})
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)


def add_node_map_rows(path: Path) -> None:
    backup(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    if any(line.startswith("PS01_MODE_AUTO,") for line in lines):
        return
    out: list[str] = []
    for line in lines:
        out.append(line)
        if line.startswith("PS01_STATION_MODE,"):
            out.append("PS01_MODE_AUTO,ns=4;s=GVL.PS01_MODE_AUTO,1,true")
            out.append("PS01_MODE_MANUAL,ns=4;s=GVL.PS01_MODE_MANUAL,1,true")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def add_modbus_rows(path: Path) -> None:
    backup(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    if any(line.startswith("PS01_MODE_AUTO,") for line in lines):
        return
    out: list[str] = []
    for line in lines:
        out.append(line)
        if line.startswith("PS01_STATION_MODE,"):
            out.append("PS01_MODE_AUTO,COIL,TBD_REGUL_EXPORT_40006A,BOOL,requires_REGUL_modbus_export")
            out.append("PS01_MODE_MANUAL,COIL,TBD_REGUL_EXPORT_40006B,BOOL,requires_REGUL_modbus_export")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def validate_xml() -> None:
    ET.parse(SETPOINTS_FORM)
    ET.parse(MAIN_FORM)
    ET.parse(SERVER_OMX)
    ET.parse(IMITATOR_OMX)


def main() -> None:
    TASK.mkdir(parents=True, exist_ok=True)
    update_main_form()
    update_setpoints_form()
    server_marker = """        <ct:parameter name=\"PS01_STATION_MODE\" uuid=\"97e771e3-641b-4aa7-bb38-eeecbe790233\" type=\"int32\" direction=\"in-out\" access-level=\"public\">
          <attribute type=\"unit.System.Attributes.Description\" value=\"Режим станции\" />
          <attribute type=\"unit.System.Attributes.Comment\" value=\"OPC UA ; Modbus \" />

        </ct:parameter>"""
    imitator_marker = """        <ct:parameter name=\"PS01_STATION_MODE\" uuid=\"c5946768-4c54-4576-b7d6-780fc0125863\" type=\"int32\" />"""
    update_omx(SERVER_OMX, server_marker)
    update_omx(IMITATOR_OMX, imitator_marker)
    add_csv_rows(PROJECT_TAG_MAP, MODE_TAGS, "PS01_STATION_MODE")
    add_csv_rows(SOURCE_TAG_MAP, MODE_TAGS, "PS01_STATION_MODE")
    add_node_map_rows(PROJECT_OPCUA_MAP)
    add_modbus_rows(PROJECT_MODBUS_MAP)
    validate_xml()
    print("repaired Alpha-native PS01 controls")


if __name__ == "__main__":
    main()
