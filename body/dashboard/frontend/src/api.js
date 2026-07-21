async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let body = null;
  try {
    body = await res.json();
  } catch {
    // no body
  }
  if (!res.ok) {
    const err = new Error(body?.detail || `HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return body;
}

export const api = {
  login: (password) => request("/login", { method: "POST", body: JSON.stringify({ password }) }),
  logout: () => request("/logout", { method: "POST" }),
  status: () => request("/status"),
  phase: () => request("/phase"),
  setPhase: (phase, notes) =>
    request("/phase", { method: "PUT", body: JSON.stringify({ phase, notes }) }),
  controlLog: () => request("/control/log"),
  stopChannel: (channel) =>
    request("/control/stop", { method: "POST", body: JSON.stringify({ channel }) }),
  resumeChannel: (channel) =>
    request("/control/resume", { method: "POST", body: JSON.stringify({ channel }) }),
  setCronEnabled: (job_id, enabled) =>
    request("/control/cron", { method: "POST", body: JSON.stringify({ job_id, enabled }) }),
};
