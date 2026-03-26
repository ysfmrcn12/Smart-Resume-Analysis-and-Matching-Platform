export type JobPosting = {
  id: number;
  title: string;
  description: string;
  requirements: string;
  company: string;
  location: string;
  created_at: string | null;
  updated_at: string | null;
};

export type Application = {
  id: number;
  job_posting_id: number;
  candidate_name: string | null;
  candidate_email: string | null;
  resume_filename: string | null;
  compatibility_score: number;
  extracted_skills: unknown[]; // backend returns JSON (often an array)
  extracted_experience: unknown[]; // backend returns JSON (often an array)
  created_at: string | null;
};

export type RankedApplication = Application & {
  // kept for readability; `compatibility_score` is already part of `Application`
  compatibility_score: number;
};

export type JobCreateInput = {
  title: string;
  description: string;
  requirements?: string;
  company?: string;
  location?: string;
};

export type JobUpdateInput = Partial<JobCreateInput>;

