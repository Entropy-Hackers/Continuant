import { defineStore } from "pinia";
import { api } from "../api.js";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    // Unknown until the first API call either succeeds or 401s — avoids a
    // login-screen flash for an already-authenticated returning visitor.
    authenticated: null,
    error: null,
  }),
  actions: {
    async login(password) {
      this.error = null;
      try {
        await api.login(password);
        this.authenticated = true;
      } catch (e) {
        this.error = e.message;
        this.authenticated = false;
      }
    },
    async logout() {
      await api.logout().catch(() => {});
      this.authenticated = false;
    },
  },
});
