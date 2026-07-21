<script setup>
import { onMounted, ref } from "vue";
import { api } from "../api.js";

const phaseInfo = ref(null);
const controlLog = ref([]);
const newPhase = ref("unmuendig");
const newNotes = ref("");
const saving = ref(false);
const error = ref(null);

async function load() {
  phaseInfo.value = await api.phase();
  newPhase.value = phaseInfo.value.current?.phase || "unmuendig";
  newNotes.value = phaseInfo.value.current?.notes || "";
  controlLog.value = (await api.controlLog()).entries;
}

async function save() {
  saving.value = true;
  error.value = null;
  try {
    await api.setPhase(newPhase.value, newNotes.value);
    await load();
  } catch (e) {
    error.value = e.message;
  } finally {
    saving.value = false;
  }
}

function fmtDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("de-AT", { dateStyle: "medium", timeStyle: "short" });
}

onMounted(load);
</script>

<template>
  <div class="settings">
    <div class="panel">
      <div class="panel-title">Mündigkeits-Status ändern</div>
      <p class="muted">
        Laut Exposé (A.9) ein bewusster Väterrats-Akt, kein automatischer Übergang —
        wird hier manuell gesetzt, nie vom Agenten selbst.
      </p>
      <div class="form-row">
        <label>
          <input type="radio" value="unmuendig" v-model="newPhase" /> unmündig
        </label>
        <label>
          <input type="radio" value="muendig" v-model="newPhase" /> mündig
        </label>
      </div>
      <textarea v-model="newNotes" rows="3" placeholder="Begründung / Notizen" style="width:100%; margin-top:0.6em"></textarea>
      <div style="margin-top: 0.8em">
        <button class="primary" :disabled="saving" @click="save">Speichern</button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <div class="panel" style="margin-top: 1em">
      <div class="panel-title">Phasen-Historie</div>
      <table class="log-table">
        <tbody>
          <tr v-for="(h, i) in phaseInfo?.history || []" :key="i">
            <td class="muted">{{ h.ts }}</td>
            <td><span class="badge neutral">{{ h.phase }}</span></td>
            <td>{{ h.notes }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="!phaseInfo?.history?.length" class="muted">Noch keine Änderungen protokolliert.</p>
    </div>

    <div class="panel" style="margin-top: 1em">
      <div class="panel-title">Control-Log (letzte Aktionen)</div>
      <table class="log-table">
        <tbody>
          <tr v-for="(e, i) in controlLog" :key="i">
            <td class="muted">{{ fmtDate(e.ts) }}</td>
            <td>{{ e.command?.action }}</td>
            <td>
              <span class="badge" :class="e.accepted ? 'good' : 'bad'">
                {{ e.accepted ? "ok" : "fehlgeschlagen" }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!controlLog.length" class="muted">Noch keine Aktionen.</p>
    </div>
  </div>
</template>

<style scoped>
.panel-title { font-weight: 600; margin-bottom: 0.6em; }
.form-row { display: flex; gap: 1.2em; }
.error { color: var(--bad); }
.log-table { width: 100%; border-collapse: collapse; }
.log-table td { padding: 0.4em 0.6em; border-bottom: 1px solid var(--border); font-size: 0.9em; }
</style>
