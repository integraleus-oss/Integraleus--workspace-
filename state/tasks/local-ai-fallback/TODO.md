# Local AI fallback switch - 2026-07-07

## Goal

Use `qwen3.5:9b` as the normal local OpenClaw fallback and compare `gemma4:e4b`
against `qwen3.5:9b` on small practical tasks.

## Checklist

- [x] Capture current OpenClaw model fallback config.
- [x] Switch fallback from `ollama/phi3:instruct` to `ollama/qwen3.5:9b`.
- [x] Verify OpenClaw reports the new fallback.
- [x] Run smoke prompt through `qwen3.5:9b`.
- [x] Run smoke prompt through `gemma4:e4b`.
- [x] Run structured extraction prompt on both models.
- [x] Run sysadmin/log-triage prompt on both models.
- [x] Summarize recommendation.

## Notes

- Avoid Alpha product/licensing prompts during this comparison to keep the test
  independent of product guardrails.
- OpenClaw fallback list is now `ollama/qwen3.5:9b`.
- Direct Ollama API with `think:false` works for both `qwen3.5:9b` and
  `gemma4:e4b`.
- Direct Ollama API without `think:false` is not suitable for fallback testing:
  `qwen3.5:9b` can emit only `thinking` and an empty `response` until it reaches
  the final answer.
- Direct API timings with `think:false`:
  - `qwen3.5:9b` JSON extraction: 17.3s, correct JSON.
  - `gemma4:e4b` JSON extraction: 13.8s, correct JSON.
  - Parallel sysadmin prompt: `qwen3.5:9b` 56.7s / 180 tokens, answer included
    one unsafe generic command for this host; `gemma4:e4b` 35.4s / 136 tokens,
    safer but generic.
- Full OpenClaw main-agent smoke with the large bootstrap timed out at 120s for
  all tested local models: `qwen3.5:9b`, `gemma4:e4b`, and `phi3:instruct`.
  The local CPU path is therefore not yet a practical full `main` fallback.

## Recommendation

Keep `qwen3.5:9b` configured as requested, but do not treat it as production-ready
for the full `main` agent. The practical next step is a lightweight local agent
profile with a much smaller bootstrap, `--thinking off`, and local-only tools.
