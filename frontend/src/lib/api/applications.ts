import { apiFetch } from "./http";
import type { Application, HighlightReport } from "./types";

export async function listApplications(jobId: number): Promise<Application[]> {
  return (
    (await apiFetch<Application[]>(`/api/applications/job/${jobId}`, { method: "GET" })) ?? []
  );
}

export async function uploadResume(jobId: number, params: {
  file: File;
  candidateName?: string;
  candidateEmail?: string;
}): Promise<Application> {
  const form = new FormData();
  // Backend accepts either `resume` or `file`; using `resume` for clarity.
  form.append("resume", params.file);
  if (params.candidateName) form.append("candidate_name", params.candidateName);
  if (params.candidateEmail) form.append("candidate_email", params.candidateEmail);

  return (await apiFetch<Application>(`/api/applications/job/${jobId}/upload`, { method: "POST", formData: form })) as Application;
}

export async function rankApplications(jobId: number): Promise<Application[]> {
  return (
    (await apiFetch<Application[]>(`/api/applications/job/${jobId}/rank`, { method: "GET" })) ?? []
  );
}

export async function getApplicationHighlightReport(applicationId: number): Promise<HighlightReport> {
  return (await apiFetch<HighlightReport>(`/api/applications/${applicationId}/highlights`, {
    method: "GET",
  })) as HighlightReport;
}

