<script setup>
import { computed } from "vue";
import { useStatusStore } from "../stores/status.js";

const status = useStatusStore();
const data = computed(() => status.data);
</script>

<template>
  <div v-if="data" class="life">
    <div class="panel">
      <div class="panel-title">Gedächtnis — MEMORY.md (jüngste Einträge)</div>
      <div v-for="entry in data.memory_recent" :key="entry.heading" class="memory-entry">
        <div class="entry-heading">{{ entry.heading }}</div>
        <pre class="readable">{{ entry.body }}</pre>
      </div>
      <p v-if="!data.memory_recent?.length" class="muted">Noch keine Einträge.</p>
    </div>

    <div class="panel">
      <div class="panel-title">Werk — zuletzt bearbeitet</div>
      <div v-for="f in data.work_recent" :key="f.name" class="memory-entry">
        <div class="entry-heading">{{ f.name }}</div>
        <pre class="readable">{{ f.preview }}</pre>
      </div>
      <p v-if="!data.work_recent?.length" class="muted">Noch nichts geschrieben.</p>
    </div>

    <div class="panel">
      <div class="panel-title">Menschen</div>
      <div v-for="p in data.people" :key="p.name" class="memory-entry">
        <div class="entry-heading">{{ p.name }}</div>
        <pre class="readable">{{ p.body }}</pre>
      </div>
      <p v-if="!data.people?.length" class="muted">Noch keine Karteikarten.</p>
    </div>

    <div class="card-grid">
      <div class="panel">
        <div class="panel-title">Lektüre</div>
        <pre class="readable">{{ data.library || "Noch nichts gelesen." }}</pre>
      </div>
      <div class="panel">
        <div class="panel-title">Journal</div>
        <pre class="readable">{{ data.journal || "Noch keine Reflexion." }}</pre>
      </div>
      <div class="panel">
        <div class="panel-title">Plan</div>
        <pre class="readable">{{ data.plan || "Noch kein Plan." }}</pre>
      </div>
    </div>
  </div>
  <p v-else class="muted">Lade…</p>
</template>

<style scoped>
.life { display: flex; flex-direction: column; gap: 1em; }
.panel-title { font-weight: 600; margin-bottom: 0.7em; }
.memory-entry { padding: 0.7em 0; border-top: 1px solid var(--border); }
.memory-entry:first-of-type { border-top: none; padding-top: 0; }
.entry-heading { font-weight: 600; font-size: 0.9em; color: var(--text-dim); margin-bottom: 0.3em; }
</style>
