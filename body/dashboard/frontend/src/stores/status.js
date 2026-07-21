import { defineStore } from "pinia";
import { api } from "../api.js";

export const useStatusStore = defineStore("status", {
  state: () => ({
    data: null,
    loading: false,
    error: null,
    lastFetchedAt: null,
  }),
  actions: {
    async refresh() {
      this.loading = true;
      this.error = null;
      try {
        this.data = await api.status();
        this.lastFetchedAt = new Date();
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },
  },
});
