# qwen2.5:3b local eval - 2026-06-24

## Checklist

- [x] Confirm initial Ollama model list
- [x] Remove `qwen3:4b`
- [x] Confirm `qwen2.5:3b` is available
- [x] Run Russian text test
- [x] Run Alpha-doc test
- [x] Run short code test
- [x] Run message classification test
- [x] Run RAG-style question test
- [x] Record timings and verdict

## Starting State

- `qwen3:4b` present before cleanup.
- `qwen2.5:3b` already installed.
- Workspace had pre-existing uncommitted changes; this eval only adds this report.

## Cleanup

`qwen3:4b` removed with `ollama rm qwen3:4b`.

`ollama list` after cleanup:

```text
kimi-k2.7-code:cloud
qwen2.5:3b
nomic-embed-text:latest
```

## Test Summary

Runtime: Ollama local API on CPU-only host.

Options: `temperature=0.2`, `top_p=0.9`; `num_predict` 128-256 depending on task.

| Test | Wall time | Speed | Result |
| --- | ---: | ---: | --- |
| Russian text summary | 7.42 s | 22.48 tok/s | Passed |
| Alpha document answer | 3.64 s | 22.82 tok/s | Passed |
| Short code | 4.78 s | 22.56 tok/s | Partial: correct function, but added markdown/explanation despite "only code" |
| Message classification | 2.58 s | 22.87 tok/s | Passed |
| RAG-style question | 2.05 s | 24.99 tok/s | Passed |

Total wall time for the five generation calls: about 20.47 s.

## Outputs

Russian text summary:

```text
Локальный AI fallback необходим для OpenClaw:

1. Отвечает на простые служебные запросы.
2. Классифицирует сообщения.
3. Помогает с короткими техническими задачами.

Важны скорость, предсказуемый формат ответа и отсутствие длинных рассуждений.
```

Alpha document answer:

```text
Для тревог использовать Alpha.HMI.Alarms 3.3, а для графиков - alpha.hmi.charts.
```

Short code output:

````text
```python
def parse_kv(line):
    key, value = line.split('=', 1)
    return (key.strip(), value.strip())
```

This function splits the input string `line` at the first occurrence of the character '=', and returns a tuple containing the stripped values of `key` and `value`. If there is no '=' in the input string, it raises a ValueError.
````

Message classification output:

```json
{
  "category": "server_incident",
  "urgency": "high"
}
```

RAG retrieval used `nomic-embed-text`. Top retrieved snippet:

```text
Alpha.HMI.WebViewer 2.0 предоставляет веб-интерфейс для HMI-проектов через браузер и может работать через IIS/Apache/NGINX.
```

RAG answer:

```text
Alpha.HMI.WebViewer 2.0
```

## Verdict

`qwen2.5:3b` is a much better local fallback candidate than `qwen3:4b` on this host:

- Faster observed generation: about 22-25 tok/s vs qwen3:4b's about 15-16 tok/s.
- No long reasoning overhead.
- Four of five tests passed cleanly.
- The short-code test needs stronger prompt/template discipline if exact "code only" output matters.

Recommendation: keep `qwen2.5:3b` installed for fallback experiments and keep `qwen3:4b` removed unless there is a separate reasoning-model experiment.
