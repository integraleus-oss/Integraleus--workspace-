Review the complete observed change against the sealed manifest acceptance
criteria and gate evidence. Inspect every changed path. Return only one exact,
schema-valid review-verdict JSON object, with no prose or Markdown fences.

Follow `review-verdict.schema.json` literally and include every required field.
Preserve trusted digests exactly. Evidence with an `artifact_ref` must include
the matching trusted `content_digest`.

Every JSON string must contain no decoded U+0000 through U+001F control
characters. Encode intended line breaks as the two characters `\\n` or replace
them with ` | `; never emit literal tabs, newlines, or other controls inside a
JSON string value.
