#!/usr/bin/env python3
"""Add the MIX01 application object to the staged PS01 Alpha.Server project."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


NS = {
    "system": "system",
    "ct": "automation.control",
    "dp": "automation.deployment",
    "eth": "automation.ethernet",
    "srv": "server",
    "hist": "history",
}


for prefix, uri in NS.items():
    ET.register_namespace("" if prefix == "system" else prefix, uri)


def find_one(root: ET.Element, path: str) -> ET.Element:
    match = root.find(path, NS)
    if match is None:
        raise SystemExit(f"not found: {path}")
    return match


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: merge_mix01_into_ps01_server.py <ps01-server.omx> <mixing-runtime.omx> <output.omx>"
        )

    ps01_path = Path(sys.argv[1])
    mix_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    ps01_tree = ET.parse(ps01_path)
    mix_tree = ET.parse(mix_path)

    ps01_app = find_one(
        ps01_tree.getroot(),
        ".//srv:io-server[@name='Server']/dp:application-object[@name='Application']",
    )
    mix_app = find_one(
        mix_tree.getroot(),
        ".//srv:io-server[@name='Server']/dp:application-object[@name='Application']",
    )
    mix01 = find_one(mix_app, "ct:object[@name='MIX01']")

    if ps01_app.find("ct:object[@name='MIX01']", NS) is not None:
        raise SystemExit("MIX01 already exists in target project")

    ps01_app.append(mix01)
    ps01_tree.write(output_path, encoding="utf-8", xml_declaration=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
