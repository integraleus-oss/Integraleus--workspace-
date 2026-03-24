"""CLI для управления агентом — миссии, статистика."""

import sys
import json
from memory import (
    init_db, set_chat_mission, get_chat_mission,
    get_chat_stats, get_all_missions, toggle_mission, delete_mission,
)
from config import MISSION_TEMPLATES

init_db()


def cmd_mission(args):
    """Установить миссию: manage.py mission <chat_id> <template> [persona_name]"""
    if len(args) < 2:
        print("Usage: manage.py mission <chat_id> <template> [persona_name]")
        print(f"Templates: {', '.join(MISSION_TEMPLATES.keys())}")
        return

    chat_id = int(args[0])
    template_name = args[1]

    if template_name not in MISSION_TEMPLATES:
        print(f"Unknown template: {template_name}")
        print(f"Available: {', '.join(MISSION_TEMPLATES.keys())}")
        return

    template = MISSION_TEMPLATES[template_name]
    persona = template["persona"]
    if len(args) > 2:
        custom_name = " ".join(args[2:])
        persona = f"{custom_name}. {persona}"

    set_chat_mission(
        chat_id,
        mission=template["mission"],
        persona=persona,
        style=template["style"],
        goals=template["goals"],
        triggers=template["triggers"],
    )

    print(f"✅ Mission set for chat {chat_id}: {template_name}")
    print(f"  Persona: {persona}")
    print(f"  Style: {template['style'][:60]}")
    print(f"  Triggers: {', '.join(template['triggers'][:5])}")


def cmd_stats(args):
    """Статистика: manage.py stats <chat_id>"""
    if not args:
        print("Usage: manage.py stats <chat_id>")
        return

    chat_id = int(args[0])
    stats = get_chat_stats(chat_id)
    mission = get_chat_mission(chat_id)

    print(f"Chat {chat_id}:")
    print(f"  Total messages: {stats['total_messages']}")
    print(f"  Agent messages: {stats['agent_messages']}")
    print(f"  Unique users: {stats['unique_users']}")
    if mission:
        print(f"  Mission: {mission['mission']}")
        print(f"  Active: {mission['active']}")


def cmd_list():
    """Список всех миссий."""
    missions = get_all_missions()
    if not missions:
        print("No missions configured.")
        return

    for m in missions:
        status = "✅" if m.get("active", True) else "⏸"
        print(f"{status} {m['chat_id']}: {m['mission']} — {m.get('persona', '-')[:50]}")
    print(f"\nTotal: {len(missions)}")


def cmd_pause(args):
    if not args:
        print("Usage: manage.py pause <chat_id>")
        return
    toggle_mission(int(args[0]), False)
    print(f"⏸ Mission paused for {args[0]}")


def cmd_resume(args):
    if not args:
        print("Usage: manage.py resume <chat_id>")
        return
    toggle_mission(int(args[0]), True)
    print(f"✅ Mission resumed for {args[0]}")


def cmd_delete(args):
    if not args:
        print("Usage: manage.py delete <chat_id>")
        return
    delete_mission(int(args[0]))
    print(f"🗑 Mission deleted for {args[0]}")


def cmd_help():
    print("""
HumanLike Agent Manager

Commands:
  mission <chat_id> <template> [name]  — Set chat mission from template
  stats <chat_id>                      — Show chat statistics
  list                                 — List all missions
  pause <chat_id>                      — Pause mission
  resume <chat_id>                     — Resume mission
  delete <chat_id>                     — Delete mission
  help                                 — This help

Templates: """ + ", ".join(MISSION_TEMPLATES.keys()) + """

Examples:
  python manage.py mission -100123456 expert Алексей
  python manage.py mission -100123456 salesman Дмитрий
  python manage.py list
  python manage.py stats -100123456
  python manage.py pause -100123456
    """)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "help":
        cmd_help()
    elif args[0] == "mission":
        cmd_mission(args[1:])
    elif args[0] == "stats":
        cmd_stats(args[1:])
    elif args[0] == "list":
        cmd_list()
    elif args[0] == "pause":
        cmd_pause(args[1:])
    elif args[0] == "resume":
        cmd_resume(args[1:])
    elif args[0] == "delete":
        cmd_delete(args[1:])
    else:
        print(f"Unknown command: {args[0]}")
        cmd_help()
