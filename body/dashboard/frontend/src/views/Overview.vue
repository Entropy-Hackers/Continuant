<script setup>
import { computed, ref } from "vue";
import { useStatusStore } from "../stores/status.js";
import { api } from "../api.js";

const status = useStatusStore();
const busy = ref(false);
const actionError = ref(null);

const data = computed(() => status.data);
const phase = computed(() => data.value?.phase);
const matrixContact = computed(() => data.value?.contacts?.matrix);
const matrixEnabled = computed(() => matrixContact.value?.enabled === true);

function fmtDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("de-AT", { dateStyle: "medium", timeStyle: "short" });
}

async function runAction(fn) {
  busy.value = true;
  actionError.value = null;
  try {
    await fn();
    // The action is only QUEUED here — control-exec runs asynchronously
    // (systemd path unit), so give it a moment before refreshing.
    setTimeout(() => status.refresh(), 2500);
  } catch (e) {
    actionError.value = e.message;
  } finally {
    busy.value = false;
  }
}

const stopMatrix = () => runAction(() => api.stopChannel("matrix"));
const resumeMatrix = () => runAction(() => api.resumeChannel("matrix"));

async function toggleCron(job) {
  await runAction(() => api.setCronEnabled(job.id, !job.enabled));
}
</script>

<template>
  <div v-if="data" class="overview">
    <div class="card-grid">
      <div class="panel">
        <div class="panel-title">Phase</div>
        <div class="phase-row">
          <span class="badge" :class="phase?.phase === 'muendig' ? 'good' : 'neutral'">
            {{ phase?.phase === "muendig" ? "mündig" : "unmündig" }}
          </span>
          <span class="muted">seit {{ phase?.since || "—" }}</span>
        </div>
        <p class="muted" style="margin-top: 0.6em">{{ phase?.notes }}</p>
      </div>

      <div class="panel">
        <div class="panel-title">Beobachtung (audit-tap)</div>
        <div class="phase-row">
          <span class="badge" :class="data.stale ? 'warn' : 'good'">
            {{ data.stale ? "veraltet" : "aktuell" }}
          </span>
        </div>
        <p class="muted" style="margin-top:0.6em">
          Letzter Poll: {{ fmtDate(data.last_poll_at) }}<br />
          {{ data.audit_event_count }} Audit-Events insgesamt
        </p>
      </div>

      <div class="panel">
        <div class="panel-title">Matrix — Not-Stopp</div>
        <div class="phase-row">
          <span class="badge" :class="matrixEnabled ? 'good' : 'bad'">
            {{ matrixEnabled ? "aktiv" : "gestoppt" }}
          </span>
        </div>
        <div style="margin-top: 0.8em; display: flex; gap: 0.6em">
          <button v-if="matrixEnabled" class="danger" :disabled="busy" @click="stopMatrix">
            STOPP
          </button>
          <button v-else class="primary" :disabled="busy" @click="resumeMatrix">
            Wieder aktivieren
          </button>
        </div>
        <p v-if="actionError" class="error">{{ actionError }}</p>
        <p class="muted" style="margin-top: 0.5em">
          Wirkt live über die Control-Queue — kein Container-Neustart.
        </p>
      </div>
    </div>

    <div class="panel" style="margin-top: 1em">
      <div class="panel-title">Cron-Jobs</div>
      <table class="cron-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in data.cron_jobs" :key="job.id">
            <td>{{ job.name }}</td>
            <td>
              <span class="badge" :class="job.enabled ? 'good' : 'neutral'">
                {{ job.enabled ? "aktiv" : "pausiert" }}
              </span>
            </td>
            <td>
              <button :disabled="busy" @click="toggleCron(job)">
                {{ job.enabled ? "Pausieren" : "Aktivieren" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!data.cron_jobs?.length" class="muted">Keine Cron-Jobs bekannt.</p>
    </div>
  </div>
  <p v-else class="muted">Lade…</p>
</template>

<style scoped>
.panel-title { font-weight: 600; margin-bottom: 0.6em; }
.phase-row { display: flex; align-items: center; gap: 0.6em; }
.error { color: var(--bad); margin: 0.5em 0 0; }
.cron-table { width: 100%; border-collapse: collapse; }
.cron-table th { text-align: left; color: var(--text-dim); font-weight: 500; font-size: 0.85em; padding: 0.4em 0.6em; border-bottom: 1px solid var(--border); }
.cron-table td { padding: 0.5em 0.6em; border-bottom: 1px solid var(--border); }
</style>
