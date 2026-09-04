const PACKAGE_STATES = new Set(["PENDING", "RUNNING", "PASSED", "FAILED", "BLOCKED"]);
const GATE_STATES = new Set(["PENDING", "PASSED", "FAILED"]);
const OUTCOMES = new Set(["CONTINUE", "SUCCEEDED", "BLOCKED"]);

function nonEmpty(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function validEvidence(item) {
  if (!item || typeof item !== "object") return false;
  if (item.kind === "file") return nonEmpty(item.path) && /^[a-f0-9]{64}$/i.test(item.sha256 || "");
  return false;
}

export function validateManagedOutcome(value) {
  const errors = [];
  if (!value || typeof value !== "object" || Array.isArray(value)) return { valid: false, errors: ["outcome must be an object"] };
  if (value.schemaVersion !== 1) errors.push("schemaVersion must be 1");
  const status = String(value.status || "").toUpperCase();
  if (!OUTCOMES.has(status)) errors.push("status must be CONTINUE, SUCCEEDED, or BLOCKED");
  if (!nonEmpty(value.summary)) errors.push("summary is required");
  if (!Array.isArray(value.packages) || value.packages.length === 0) errors.push("at least one work package is required");
  else for (const [index, item] of value.packages.entries()) {
    if (!nonEmpty(item?.id) || !nonEmpty(item?.title)) errors.push(`package ${index + 1} requires id and title`);
    if (!PACKAGE_STATES.has(String(item?.status || "").toUpperCase())) errors.push(`package ${index + 1} has invalid status`);
    if (String(item?.status).toUpperCase() === "PASSED" && (!Array.isArray(item.evidence) || item.evidence.length === 0 || item.evidence.some(x => !validEvidence(x)))) errors.push(`package ${index + 1} passed without verifiable evidence`);
  }
  if (!Array.isArray(value.gates) || value.gates.length === 0) errors.push("at least one acceptance gate is required");
  else for (const [index, item] of value.gates.entries()) {
    if (!nonEmpty(item?.id) || !nonEmpty(item?.title)) errors.push(`gate ${index + 1} requires id and title`);
    if (!GATE_STATES.has(String(item?.status || "").toUpperCase())) errors.push(`gate ${index + 1} has invalid status`);
    if (String(item?.status).toUpperCase() === "PASSED" && (!Array.isArray(item.evidence) || item.evidence.length === 0 || item.evidence.some(x => !validEvidence(x)))) errors.push(`gate ${index + 1} passed without verifiable evidence`);
  }
  for (const kind of ["packages", "gates"]) if (Array.isArray(value[kind])) {
    const ids = value[kind].map(item => item?.id).filter(nonEmpty);
    if (new Set(ids).size !== ids.length) errors.push(`${kind} ids must be unique`);
  }
  const openPackages = Array.isArray(value.packages) ? value.packages.filter(x => String(x?.status).toUpperCase() !== "PASSED") : [];
  const openGates = Array.isArray(value.gates) ? value.gates.filter(x => String(x?.status).toUpperCase() !== "PASSED") : [];
  if (status === "SUCCEEDED") {
    if (value.objectiveComplete !== true) errors.push("SUCCEEDED requires objectiveComplete=true");
    if (openPackages.length) errors.push("SUCCEEDED requires every package PASSED");
    if (openGates.length) errors.push("SUCCEEDED requires every gate PASSED");
    if (Array.isArray(value.gates) && value.gates.some(x => !Array.isArray(x?.evidence) || !x.evidence.some(e => e?.kind === "file"))) errors.push("SUCCEEDED requires a durable verification artifact for every gate");
    if (value.blocker) errors.push("SUCCEEDED cannot contain a blocker");
  }
  if (status === "BLOCKED") {
    const blocker = value.blocker;
    if (!blocker || blocker.external !== true || !nonEmpty(blocker.reason)
      || !Array.isArray(blocker.evidence) || blocker.evidence.length === 0 || blocker.evidence.some(x => !validEvidence(x))
      || !nonEmpty(blocker.ownerAction)) errors.push("BLOCKED requires an external blocker with reason, evidence, and ownerAction");
    if (!Array.isArray(value.packages) || !value.packages.some(x => String(x?.status).toUpperCase() === "BLOCKED")) errors.push("BLOCKED requires a blocked work package");
    if (!Array.isArray(value.packages) || !value.packages.some(x => String(x?.status).toUpperCase() === "PASSED")) errors.push("BLOCKED requires at least one completed work package with verified evidence");
    if (Array.isArray(value.packages) && value.packages.some(x => ["PENDING", "RUNNING"].includes(String(x?.status).toUpperCase()))) errors.push("BLOCKED requires every package to be resolved as PASSED or BLOCKED");
    if (Array.isArray(value.packages) && value.packages.some(x => String(x?.status).toUpperCase() === "FAILED")) errors.push("internal failed packages must be fixed or continued, not BLOCKED");
    if (Array.isArray(value.gates) && value.gates.some(x => String(x?.status).toUpperCase() === "FAILED")) errors.push("failed gates must be fixed or continued, not BLOCKED");
    if (!Array.isArray(value.gates) || value.gates.some(x => String(x?.status).toUpperCase() !== "PASSED")) errors.push("BLOCKED requires every acceptance gate reached so far to be PASSED with evidence");
  }
  if (status === "CONTINUE" && value.objectiveComplete === true) errors.push("CONTINUE cannot mark the objective complete");
  return { valid: errors.length === 0, errors, status, openPackages, openGates };
}

export function terminalStatus(value) {
  const checked = validateManagedOutcome(value);
  if (!checked.valid) return null;
  if (checked.status === "SUCCEEDED") return "SUCCEEDED";
  if (checked.status === "BLOCKED") return "BLOCKED";
  return null;
}
