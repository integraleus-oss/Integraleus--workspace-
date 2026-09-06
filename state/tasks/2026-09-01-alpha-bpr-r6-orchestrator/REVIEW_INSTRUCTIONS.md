# Independent R6 review

Review on two axes.

Standards: transactional integrity, TOCTOU resistance, immutable provenance,
deterministic canonicalization/hash validation, PostgreSQL constraints and safe
legacy migration, fail-closed malformed data handling, bounded audit behavior,
authorization, stable issue codes, test quality, and repository conventions.

Spec: verify exact pinned ontology rather than ambient tables; complete recipe
graph coverage; Draft-only explicit preview-bound re-pin with impact diff and
optimistic concurrency; lifecycle rejection audit; useful API/HMI projection;
deprecated `POST /publish` removed while `POST /make-effective` remains; no
silent pinning, frozen-byte mutation, second migration, production action, or
scope expansion.

Reject for any open blocker/major, bypass, ambient ontology dependency, partial
pin acceptance, unaudited rejection, TOCTOU window, unverifiable preview/apply
binding, missing negative tests, or changed path outside the allowlist.
