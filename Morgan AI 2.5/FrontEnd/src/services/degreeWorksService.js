// Degree Works service layer
// Provides functions to interact with backend Degree Works API endpoints.
// Assumes JWT bearer token stored in localStorage under key 'token'.

const API_BASE = '/api/degree-works';

function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function handle(res) {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try { const data = await res.json(); detail = data.detail || JSON.stringify(data); } catch {}
    throw new Error(detail);
  }
  return res.json();
}

export async function uploadDegreeWorks(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/upload`, { method: 'POST', headers: { ...authHeaders() }, body: form });
  return handle(res);
}

export async function getLatestAnalysis() {
  const res = await fetch(`${API_BASE}/analysis`, { headers: { ...authHeaders() } });
  return handle(res);
}

export async function listVersions() {
  const res = await fetch(`${API_BASE}/versions`, { headers: { ...authHeaders() } });
  return handle(res);
}

export async function getVersion(versionId) {
  const res = await fetch(`${API_BASE}/versions/${versionId}`, { headers: { ...authHeaders() } });
  return handle(res);
}

export async function diffVersions(targetVersionId, baseVersionId) {
  const res = await fetch(`${API_BASE}/versions/${targetVersionId}/diff/${baseVersionId}`, { headers: { ...authHeaders() } });
  return handle(res);
}

export async function deleteVersion(versionId) {
  const res = await fetch(`${API_BASE}/versions/${versionId}`, { method: 'DELETE', headers: { ...authHeaders() } });
  return handle(res);
}

export async function getTimeline() {
  const res = await fetch(`${API_BASE}/timeline`, { headers: { ...authHeaders() } });
  return handle(res);
}

export async function deleteAllDegreeWorks() {
  const res = await fetch(`${API_BASE}/analysis`, { method: 'DELETE', headers: { ...authHeaders() } });
  return handle(res);
}

export function summarizeDiff(diff) {
  if (!diff || typeof diff !== 'object') return null;
  return {
    completedCreditsDelta: diff.completed_credits_delta ?? diff.credits_completed_delta ?? null,
    inProgressCreditsDelta: diff.in_progress_credits_delta ?? null,
    gpaDelta: diff.gpa_delta ?? null,
    classificationChanged: diff.classification_changed || false,
    previousClassification: diff.previous_classification ?? null,
    currentClassification: diff.current_classification ?? null,
    newlyCompleted: diff.newly_completed_courses || [],
    newlyInProgress: diff.new_in_progress_courses || [],
    resolvedRemaining: diff.remaining_courses_resolved || [],
    gradeChanges: diff.grade_changes || [],
    termsAdded: diff.terms_added || [],
    termsRemoved: diff.terms_removed || []
  };
}

// Default export for convenience
export default {
  uploadDegreeWorks,
  getLatestAnalysis,
  listVersions,
  getVersion,
  diffVersions,
  deleteVersion,
  getTimeline,
  deleteAllDegreeWorks,
  summarizeDiff
};
