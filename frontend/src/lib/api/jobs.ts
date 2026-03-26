import { apiFetch } from "./http";
import type { JobCreateInput, JobPosting, JobUpdateInput } from "./types";

export async function getJobs(): Promise<JobPosting[]> {
  return (await apiFetch<JobPosting[]>("/api/jobs", { method: "GET" })) ?? [];
}

export async function createJob(input: JobCreateInput): Promise<JobPosting> {
  return (await apiFetch<JobPosting>("/api/jobs", { method: "POST", body: input })) as JobPosting;
}

export async function getJob(jobId: number): Promise<JobPosting> {
  return (await apiFetch<JobPosting>(`/api/jobs/${jobId}`, { method: "GET" })) as JobPosting;
}

export async function updateJob(
  jobId: number,
  input: JobUpdateInput
): Promise<JobPosting> {
  return (await apiFetch<JobPosting>(`/api/jobs/${jobId}`, { method: "PUT", body: input })) as JobPosting;
}

export async function deleteJob(jobId: number): Promise<void> {
  await apiFetch<unknown>(`/api/jobs/${jobId}`, { method: "DELETE" });
}

// Applications endpoints live in a separate file for organization, but we keep types imported here if needed later.

