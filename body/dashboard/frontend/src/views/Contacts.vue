<script setup>
import { computed } from "vue";
import { useStatusStore } from "../stores/status.js";

const status = useStatusStore();
const channels = computed(() => status.data?.contacts || {});
</script>

<template>
  <div class="card-grid">
    <div v-for="(cfg, name) in channels" :key="name" class="panel">
      <div class="panel-title">
        {{ name }}
        <span class="badge" :class="cfg.enabled ? 'good' : 'neutral'" style="margin-left: 0.5em">
          {{ cfg.enabled ? "aktiv" : "deaktiviert" }}
        </span>
      </div>
      <p class="muted" v-if="cfg.homeserver || cfg.url">{{ cfg.homeserver || cfg.url }}</p>
      <div v-if="cfg.dm?.allowFrom?.length" style="margin-top: 0.8em">
        <div class="muted" style="margin-bottom: 0.3em">Direktnachrichten erlaubt von:</div>
        <ul class="contact-list">
          <li v-for="who in cfg.dm.allowFrom" :key="who">{{ who }}</li>
        </ul>
      </div>
      <div v-if="cfg.groupAllowFrom?.length" style="margin-top: 0.8em">
        <div class="muted" style="margin-bottom: 0.3em">Gruppen-Zugriff erlaubt von:</div>
        <ul class="contact-list">
          <li v-for="who in cfg.groupAllowFrom" :key="who">{{ who }}</li>
        </ul>
      </div>
    </div>
  </div>
  <p v-if="!Object.keys(channels).length" class="muted">Keine Kontaktdaten verfügbar.</p>
</template>

<style scoped>
.panel-title { font-weight: 600; }
.contact-list { margin: 0; padding-left: 1.2em; }
.contact-list li { font-family: ui-monospace, monospace; font-size: 0.9em; margin-bottom: 0.2em; }
</style>
