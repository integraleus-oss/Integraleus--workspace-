#!/usr/bin/env python3
"""Convert Tabler SVG icons to colored PNG for pptx embedding."""

import cairosvg
import os
import sys

ICONS_DIR = "/root/.openclaw/workspace/agents/main/docs/tabler-icons/svg/outline"
OUTPUT_DIR = "/root/.openclaw/workspace/agents/main/skills/presentation-designer/assets/icons"

def svg_to_colored_png(svg_path, output_path, color="#00D4FF", size=128):
    """Convert SVG to PNG with custom stroke color."""
    with open(svg_path, 'r') as f:
        svg_content = f.read()
    # Replace stroke color (tabler icons use currentColor or stroke="currentColor")
    svg_content = svg_content.replace('stroke="currentColor"', f'stroke="{color}"')
    svg_content = svg_content.replace("stroke='currentColor'", f"stroke='{color}'")
    # Also set fill to none to keep outline style
    cairosvg.svg2png(bytestring=svg_content.encode(), write_to=output_path, 
                     output_width=size, output_height=size)

def batch_convert(icons_map, size=128):
    """Convert a dict of {output_name: (svg_name, color)}."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, (svg_name, color) in icons_map.items():
        svg_path = os.path.join(ICONS_DIR, svg_name)
        out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        if os.path.exists(svg_path):
            svg_to_colored_png(svg_path, out_path, color, size)
            print(f"  ✓ {name}.png ({svg_name}, {color})")
        else:
            print(f"  ✗ {svg_name} not found!")

if __name__ == "__main__":
    # Industrial automation icon set for Лацерта
    CYAN = "#00D4FF"
    GREEN = "#00E676"
    ORANGE = "#FF8C00"
    PURPLE = "#8B5CF6"
    PINK = "#FF0080"
    YELLOW = "#FFD600"
    WHITE = "#FFFFFF"
    LIGHT = "#B0C4D8"
    
    icons = {
        # Core platform
        "server": ("server.svg", CYAN),
        "server-spark": ("server-spark.svg", CYAN),
        "database": ("database.svg", GREEN),
        "cpu": ("cpu.svg", ORANGE),
        "settings-automation": ("settings-automation.svg", CYAN),
        "settings": ("settings-cog.svg", LIGHT),
        
        # Architecture
        "layers": ("layers-linked.svg", CYAN),
        "stack": ("stack-3.svg", PURPLE),
        "network": ("network.svg", GREEN),
        "cloud-data": ("cloud-data-connection.svg", CYAN),
        "api": ("api.svg", PURPLE),
        
        # Security
        "shield-lock": ("shield-lock.svg", PINK),
        "lock": ("lock.svg", PINK),
        "shield-check": ("shield-check.svg", GREEN),
        "key": ("key.svg", YELLOW),
        
        # Protocols & connectivity
        "plug": ("plug-connected.svg", GREEN),
        "router": ("router.svg", ORANGE),
        "bolt": ("bolt.svg", YELLOW),
        "antenna": ("antenna.svg", CYAN),
        "world": ("world.svg", CYAN),
        
        # Monitoring & analytics
        "chart-line": ("chart-line.svg", GREEN),
        "chart-bar": ("chart-bar.svg", CYAN),
        "chart-donut": ("chart-donut.svg", PURPLE),
        "chart-infographic": ("chart-infographic.svg", ORANGE),
        "gauge": ("gauge.svg", ORANGE),
        "activity": ("activity-heartbeat.svg", PINK),
        "device-analytics": ("device-analytics.svg", CYAN),
        
        # Industrial
        "building-factory": ("building-factory.svg", ORANGE),
        "circuit-motor": ("circuit-motor.svg", CYAN),
        "circuit-switch": ("circuit-switch-closed.svg", GREEN),
        "circuit-resistor": ("circuit-resistor.svg", YELLOW),
        "circuit-ammeter": ("circuit-ammeter.svg", CYAN),
        "circuit-voltmeter": ("circuit-voltmeter.svg", ORANGE),
        
        # Development
        "code": ("code.svg", PURPLE),
        "terminal": ("terminal.svg", GREEN),
        "layout-dashboard": ("layout-dashboard.svg", CYAN),
        "browser": ("browser.svg", LIGHT),
        "cube": ("cube.svg", ORANGE),
        
        # Alerts & events
        "alert-triangle": ("alert-triangle.svg", YELLOW),
        "bell-ringing": ("bell-ringing.svg", ORANGE),
        "eye": ("eye.svg", CYAN),
        "clock": ("clock.svg", LIGHT),
        
        # Data & storage
        "archive": ("archive.svg", LIGHT),
        "database-export": ("database-export.svg", GREEN),
        "database-import": ("database-import.svg", CYAN),
        
        # Devices
        "device-desktop": ("device-desktop.svg", LIGHT),
        "device-cctv": ("device-cctv.svg", ORANGE),
        "device-mobile": ("device-mobile.svg", LIGHT),
        "screen-share": ("screen-share.svg", CYAN),
        
        # White versions for dark backgrounds
        "server-w": ("server.svg", WHITE),
        "database-w": ("database.svg", WHITE),
        "shield-lock-w": ("shield-lock.svg", WHITE),
        "chart-line-w": ("chart-line.svg", WHITE),
        "building-factory-w": ("building-factory.svg", WHITE),
        "plug-w": ("plug-connected.svg", WHITE),
        "code-w": ("code.svg", WHITE),
        "gauge-w": ("gauge.svg", WHITE),
        "eye-w": ("eye.svg", WHITE),
        "layers-w": ("layers-linked.svg", WHITE),
    }
    
    print(f"Converting {len(icons)} icons...")
    batch_convert(icons, size=128)
    print(f"\nDone! Icons saved to {OUTPUT_DIR}")
