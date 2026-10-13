/* Offline UI smoke checks using only the Node.js standard library. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync("web/index.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, "A browser script must exist");

const fields = Object.create(null);
const values = {
  outputConsole: "",
  task_id: "SMOKE-01",
  target_id: "KEY-01",
  primary_metric: "29.4",
  secondary_metric: "14.8",
  status_descriptor: "DISCORDANT_ANOMALY",
  execution_mode: "local",
  "m-status": "READY",
  "m-tasks": "0",
  "m-audit": "0",
  "m-phi": "0"
};
for (const [id, value] of Object.entries(values)) {
  fields[id] = { value, textContent: value, checked: id === "is_critical" };
}
fields.is_critical = { checked: true };
const context = vm.createContext({
  document: { getElementById: id => fields[id] },
  fetch: async () => { throw new Error("Local preview unexpectedly called fetch"); }
});
vm.runInContext(match[1], context);

async function run() {
  await vm.runInContext("runAudit()", context);
  const local = JSON.parse(fields.outputConsole.textContent);
  assert.equal(local.mode, "LOCAL_PREVIEW");
  assert.equal(local.overall_urgency, "CRITICAL_STAT_PANIC");
  assert.equal(local.total_alerts, 3);
  assert.ok(!("audit_hash" in local));
  assert.equal(fields["m-audit"].textContent, "0");

  fields.is_critical.checked = false;
  fields.primary_metric.value = "10";
  fields.secondary_metric.value = "2";
  fields.status_descriptor.value = "NOMINAL";
  await vm.runInContext("runAudit()", context);
  assert.equal(JSON.parse(fields.outputConsole.textContent).overall_urgency, "ROUTINE");

  fields.execution_mode.value = "server";
  context.fetch = async (url, options) => {
    assert.equal(url, "./api/audit");
    assert.equal(options.method, "POST");
    assert.equal(JSON.parse(options.body).task_id, "SMOKE-01");
    return { ok: true, json: async () => ({
      overall_urgency: "ROUTINE", audit_hash: "a".repeat(64)
    }) };
  };
  await vm.runInContext("runAudit()", context);
  assert.equal(fields["m-audit"].textContent, "1");

  context.fetch = async () => { throw new Error("Server unavailable"); };
  await vm.runInContext("runAudit()", context);
  assert.match(fields.outputConsole.textContent, /No local simulation has been substituted/);
  assert.equal(fields["m-audit"].textContent, "1");
  assert.equal(fields["m-status"].textContent, "ERROR");
}

run().catch(error => { console.error(error); process.exitCode = 1; });
