<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useAuthStore } from "./stores/auth.js";
import { useStatusStore } from "./stores/status.js";
import Login from "./views/Login.vue";
import Overview from "./views/Overview.vue";
import Contacts from "./views/Contacts.vue";
import Life from "./views/Life.vue";
import Settings from "./views/Settings.vue";

const auth = useAuthStore();
const status = useStatusStore();

const TABS = [
  { id: "overview", label: "Übersicht", component: Overview },
  { id: "contacts", label: "Kontakte", component: Contacts },
  { id: "life", label: "Leben", component: Life },
  { id: "settings", label: "Einstellungen", component: Settings },
];
const activeTab = ref("overview");
const activeComponent = computed(() => TABS.find((t) => t.id === activeTab.value)?.component);

let pollHandle = null;

onMounted(async () => {
  await status.refresh();
  auth.authenticated = status.error ? false : true;
});

watch(
  () => auth.authenticated,
  (isAuthed) => {
    if (pollHandle) clearInterval(pollHandle);
    if (isAuthed) {
      status.refresh();
      pollHandle = setInterval(() => status.refresh(), 30000);
    }
  },
);

async function doLogout() {
  await auth.logout();
}
</script>

<template>
  <Login v-if="auth.authenticated === false" />
  <div v-else-if="auth.authenticated === true" class="app-shell">
    <header class="topbar">
      <div class="brand">{{ status.data?.instance || "Continuant" }} — Dashboard</div>
      <nav class="tabs">
        <button
          v-for="tab in TABS"
          :key="tab.id"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </nav>
      <button @click="doLogout">Abmelden</button>
    </header>
    <main class="content">
      <component :is="activeComponent" />
    </main>
  </div>
  <div v-else class="loading-screen">Lade…</div>
</template>

<style scoped>
.app-shell { min-height: 100vh; }
.topbar {
  display: flex;
  align-items: center;
  gap: 1.5em;
  padding: 0.8em 1.5em;
  border-bottom: 1px solid var(--border);
  background: var(--bg-panel);
}
.brand { font-weight: 700; margin-right: auto; }
.tabs { display: flex; gap: 0.4em; }
.tabs button { background: transparent; border-color: transparent; }
.tabs button.active { background: var(--bg-panel-alt); border-color: var(--border); }
.content { padding: 1.5em; max-width: 1100px; margin: 0 auto; }
.loading-screen { display: flex; align-items: center; justify-content: center; min-height: 100vh; color: var(--text-dim); }
</style>
