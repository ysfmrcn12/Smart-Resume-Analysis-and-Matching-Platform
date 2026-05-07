export type JobPosting = {
  id: number;
  title: string;
  description: string;
  requirements: string[];
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

export type ScoringReport = {
  final_score_percent: number;
  base_score_percent: number;
  weights: {
    semantic?: number;
  };
  semantic_raw: number;
  semantic_percent: number;
  skill_overlap_ratio: number;
  skill_multiplier: number;
  experience_multiplier: number;
  required_years: number;
  candidate_years: number;
  calculation_breakdown: {
    formula: string;
    pre_clamp_score_percent: number;
    final_score_percent: number;
    was_clamped: boolean;
    steps: Array<{
      name: string;
      value: number;
      percent_value: number | null;
    }>;
  };
};

export type HighlightReport = {
  resume_text: string;
  matching_skills: Record<string, Array<[number, number]>>;
  matching_keywords: Record<string, Array<[number, number]>>;
  matched_count: number;
  job_skill_count: number;
  matched_skills: string[];
  lexical_overlap_keywords: string[];
  sections: Record<string, string>;
  scoring_report: ScoringReport;
};

export type RankedApplication = Application & {
  // kept for readability; `compatibility_score` is already part of `Application`
  compatibility_score: number;
};

export type JobCreateInput = {
  title: string;
  description: string;
  requirements?: string[];
  company?: string;
  location?: string;
};

export type JobUpdateInput = Partial<JobCreateInput>;

