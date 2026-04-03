"""Калькулятор тегов и подбор редакций Альфа платформы.
Точные вычисления в коде — LLM только собирает данные и оформляет."""

import json
import logging

logger = logging.getLogger(__name__)

# Коэффициенты информационной мощности
POWER_LEVELS = {
    "simple":  {"DI": 1, "DO": 1, "AI": 2, "AO": 2},
    "medium":  {"DI": 2, "DO": 2, "AI": 4, "AO": 4},
    "complex": {"DI": 3, "DO": 3, "AI": 6, "AO": 6},
}

# Тарифные ступени (внешние теги) — ближайшая верхняя
TAG_TIERS = [32, 64, 128, 256, 512, 1024, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000]

# Ступени Historian
HISTORIAN_TIERS = [150, 300, 500, 1000, 1500, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000]


def find_tier(value: int, tiers: list[int]) -> int:
    """Находит ближайшую верхнюю ступень."""
    for t in tiers:
        if value <= t:
            return t
    return tiers[-1]


def calculate_tags(di: int = 0, do: int = 0, ai: int = 0, ao: int = 0,
                   power: str = "medium", custom_coeffs: dict = None) -> dict:
    """Рассчитывает внешние теги из сигналов."""
    if custom_coeffs:
        coeffs = custom_coeffs
    elif power in POWER_LEVELS:
        coeffs = POWER_LEVELS[power]
    else:
        coeffs = POWER_LEVELS["medium"]

    tags_di = di * coeffs["DI"]
    tags_do = do * coeffs["DO"]
    tags_ai = ai * coeffs["AI"]
    tags_ao = ao * coeffs["AO"]
    total_tags = tags_di + tags_do + tags_ai + tags_ao

    return {
        "signals": {"DI": di, "DO": do, "AI": ai, "AO": ao},
        "power_level": power,
        "coefficients": coeffs,
        "breakdown": {
            "DI": f"{di} x {coeffs['DI']} = {tags_di}",
            "DO": f"{do} x {coeffs['DO']} = {tags_do}",
            "AI": f"{ai} x {coeffs['AI']} = {tags_ai}",
            "AO": f"{ao} x {coeffs['AO']} = {tags_ao}",
        },
        "total_tags": total_tags,
        "tag_tier": find_tier(total_tags, TAG_TIERS),
    }


def recommend_edition(total_tags: int, reserve: bool = False,
                      clients: int = 1, web_clients: int = 0) -> list[dict]:
    """Подбирает подходящие редакции."""
    options = []
    tag_tier = find_tier(total_tags, TAG_TIERS)

    # Alpha.One+
    if total_tags <= 50000 and not reserve and clients <= 1 and web_clients == 0:
        options.append({
            "edition": "Alpha.One+",
            "recommended": True,
            "reason": f"Подходит: {total_tags} тегов (лимит 50 000), без резерва, {clients} клиент",
            "server_tier": tag_tier,
            "note": "Самый доступный вариант",
        })

    # Alpha.SCADA
    scada = {
        "edition": "Alpha.SCADA",
        "recommended": not options,  # рекомендован если One+ не подошёл
        "server_tier": tag_tier,
        "note": "",
    }
    reasons = []
    if reserve:
        reasons.append("резервирование")
        scada["reserve_tier"] = tag_tier
        scada["note"] = "Резервный сервер: отдельная лицензия того же уровня"
    if clients > 1:
        reasons.append(f"{clients} клиентов")
    if total_tags > 50000:
        reasons.append(f"{total_tags} тегов (больше лимита One+)")
    if not reasons:
        reasons.append("с запасом на рост, возможность добавить резерв")
    scada["reason"] = ", ".join(reasons)
    scada["clients"] = {"full": clients, "web": web_clients}
    if web_clients > 5:
        scada["web_note"] = "Рекомендуется выделенный WEB-сервер + WEB-PORTAL"
    options.append(scada)

    # Alpha.Platform (если мультисервер или >100k тегов)
    if total_tags > 100000 or reserve or clients > 3:
        options.append({
            "edition": "Alpha.Platform",
            "recommended": False,
            "reason": "Для сложных архитектур, все драйверы включены",
            "server_tier": tag_tier,
            "note": "Рассмотреть при масштабировании",
        })

    return options


def calculate_historian(tags: int) -> dict:
    """Рассчитывает ступень Historian."""
    tier = find_tier(tags, HISTORIAN_TIERS)
    return {
        "historian_tags": tags,
        "historian_tier": tier,
    }


def full_calculation(di: int = 0, do: int = 0, ai: int = 0, ao: int = 0,
                     power: str = "medium", reserve: bool = False,
                     clients: int = 1, web_clients: int = 0,
                     historian: bool = False, historian_tags: int = 0) -> str:
    """Полный расчёт — возвращает текстовый блок для вставки в ответ LLM."""
    # Расчёт тегов
    calc = calculate_tags(di, do, ai, ao, power)
    total = calc["total_tags"]
    tier = calc["tag_tier"]

    result = []
    result.append("=== РАСЧЁТ (выполнен калькулятором) ===")
    result.append("")
    result.append(f"Исходные данные: DI={di}, DO={do}, AI={ai}, AO={ao}")
    result.append(f"Информационная мощность: {power}")
    result.append(f"Коэффициенты: DI={calc['coefficients']['DI']}, DO={calc['coefficients']['DO']}, AI={calc['coefficients']['AI']}, AO={calc['coefficients']['AO']}")
    result.append("")
    result.append("Расчёт тегов:")
    for sig, detail in calc["breakdown"].items():
        result.append(f"  {sig}: {detail}")
    result.append(f"  ИТОГО: {total} внешних тегов")
    result.append(f"  Тарифная ступень: {tier}")
    result.append("")

    # Подбор редакций
    options = recommend_edition(total, reserve, clients, web_clients)
    result.append(f"Резервирование: {'да' if reserve else 'нет'}")
    result.append(f"Клиенты: {clients} Full" + (f", {web_clients} WEB" if web_clients else ""))
    result.append("")

    for i, opt in enumerate(options):
        label = "РЕКОМЕНДОВАН" if opt["recommended"] else "Альтернатива"
        result.append(f"Вариант {chr(65+i)} — {opt['edition']} ({label}):")
        result.append(f"  Сервер: {opt['edition']} {opt['server_tier']} тегов")
        if opt.get("reserve_tier"):
            result.append(f"  Резервный сервер: {opt['reserve_tier']} тегов")
        if opt.get("clients"):
            cl = opt["clients"]
            parts = []
            if cl.get("full"): parts.append(f"{cl['full']} Full")
            if cl.get("web"): parts.append(f"{cl['web']} WEB")
            result.append(f"  Клиенты: {', '.join(parts)}")
        if opt.get("web_note"):
            result.append(f"  ⚠ {opt['web_note']}")
        result.append(f"  Причина: {opt['reason']}")
        if opt.get("note"):
            result.append(f"  Примечание: {opt['note']}")
        result.append("")

    # Historian
    if historian and historian_tags > 0:
        hist = calculate_historian(historian_tags)
        result.append(f"Historian: {hist['historian_tags']} тегов → ступень {hist['historian_tier']}")
        result.append("")

    result.append("=== КОНЕЦ РАСЧЁТА ===")
    return "\n".join(result)


# Маркер для LLM — если в ответе есть этот JSON-блок, бот перехватит и подставит расчёт
CALC_MARKER = "[CALC:"


def parse_calc_request(text: str) -> dict | None:
    """Ищет маркер калькулятора в тексте LLM.
    Формат: [CALC:DI=200,DO=50,AI=150,AO=80,power=medium,reserve=no,clients=1,web=0,historian=yes,hist_tags=1000]
    """
    if CALC_MARKER not in text:
        return None

    try:
        start = text.index(CALC_MARKER) + len(CALC_MARKER)
        end = text.index("]", start)
        params_str = text[start:end]

        params = {}
        for pair in params_str.split(","):
            key, value = pair.strip().split("=")
            key = key.strip()
            value = value.strip()
            params[key] = value

        return {
            "di": int(params.get("DI", params.get("di", 0))),
            "do": int(params.get("DO", params.get("do", 0))),
            "ai": int(params.get("AI", params.get("ai", 0))),
            "ao": int(params.get("AO", params.get("ao", 0))),
            "power": params.get("power", "medium"),
            "reserve": params.get("reserve", "no").lower() in ("yes", "true", "да", "1"),
            "clients": int(params.get("clients", 1)),
            "web_clients": int(params.get("web", 0)),
            "historian": params.get("historian", "no").lower() in ("yes", "true", "да", "1"),
            "historian_tags": int(params.get("hist_tags", params.get("historian_tags", 0))),
        }
    except Exception as e:
        logger.error(f"Failed to parse calc request: {e}")
        return None


def process_llm_response(response: str) -> str:
    """Если LLM вставил маркер калькулятора — заменяет его на точный расчёт."""
    params = parse_calc_request(response)
    if not params:
        return response

    # Выполняем расчёт
    calc_result = full_calculation(**params)

    # Заменяем маркер на результат
    start = response.index(CALC_MARKER)
    end = response.index("]", start) + 1
    marker_text = response[start:end]

    return response.replace(marker_text, "\n" + calc_result + "\n")
