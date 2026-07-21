<script setup>
import { ref } from "vue";
import { useAuthStore } from "../stores/auth.js";

const auth = useAuthStore();
const password = ref("");
const submitting = ref(false);

async function submit() {
  submitting.value = true;
  await auth.login(password.value);
  submitting.value = false;
  password.value = "";
}
</script>

<template>
  <div class="login-screen">
    <form class="panel login-box" @submit.prevent="submit">
      <h1>Continuant Dashboard</h1>
      <p class="muted">Anmelden mit dem gemeinsamen Admin-Passwort.</p>
      <input
        type="password"
        v-model="password"
        placeholder="Passwort"
        autofocus
        required
      />
      <button type="submit" class="primary" :disabled="submitting">
        {{ submitting ? "…" : "Anmelden" }}
      </button>
      <p v-if="auth.error" class="error">{{ auth.error }}</p>
    </form>
  </div>
</template>

<style scoped>
.login-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-box {
  display: flex;
  flex-direction: column;
  gap: 0.9em;
  width: 320px;
}
.login-box h1 { margin: 0; font-size: 1.3em; }
.error { color: var(--bad); margin: 0; font-size: 0.9em; }
</style>
