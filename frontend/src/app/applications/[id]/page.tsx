"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getApplicationHighlightReport } from "@/lib/api/applications";

export default function ApplicationDetailsPage() {
  const params = useParams();
  const applicationId = Number(params.id);

  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hoveredKeyword, setHoveredKeyword] = useState<string | null>(null);
  const [calculationModalOpen, setCalculationModalOpen] = useState(false);

  const getScoreColor = (s: number) => {
    if (s >= 80) return "bg-green-50 text-green-800 border-green-800";
    if (s >= 50) return "bg-yellow-50 text-yellow-900 border-yellow-900";
    return "bg-red-50 text-red-800 border-red-800";
  };

  useEffect(() => {
    if (!applicationId) return;
    setLoading(true);
    setError(null);

    getApplicationHighlightReport(applicationId)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Error loading analysis");
        setLoading(false);
      });
  }, [applicationId]);

  if (loading) {
    return <div className="p-8 text-sm text-zinc-600">Loading analysis details...</div>;
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <Link href="/jobs" className="text-sm font-semibold text-blue-600 hover:underline">← Back to Jobs</Link>
        <div className="mt-4 rounded bg-red-50 p-3 text-sm text-red-700">{error || "Data not found"}</div>
      </div>
    );
  }

  const score = data.scoring_report.final_score_percent;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header Panel */}
      <div className="mb-6 flex items-start justify-between gap-6 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="flex-1">
          <Link href={`/jobs/${data.job_id}`} className="mb-4 inline-flex items-center text-sm font-semibold text-zinc-500 hover:text-zinc-800">
            ← Back to Job
          </Link>
          <p className="text-lg font-semibold text-blue-700">
            {data.job_title}
          </p>
          <div className="mt-2 flex items-center gap-4">
            <h1 className="text-3xl font-bold text-zinc-900">
              Candidate: {data.candidate_name}
            </h1>
            <a
              href={`/api/applications/${applicationId}/resume`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center self-end rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50 hover:text-zinc-900 shadow-sm transition-colors"
            >
              <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              View Original PDF
            </a>
          </div>
          <p className="mt-2 text-sm text-zinc-600">
            {data.matched_count} matching skills out of {data.job_skill_count} required
          </p>
        </div>

        {/* Score Circle & Show Calculation */}
        <div className="flex flex-col items-center gap-3">
          <div className={`flex h-24 w-24 items-center justify-center rounded-full border-4 ${getScoreColor(score)}`}>
            <span className="text-4xl font-bold">
              {Math.round(score)}
            </span>
          </div>
          <button
            onClick={() => setCalculationModalOpen(true)}
            className="mt-1 rounded-md bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800 shadow-sm transition-colors"
          >
            Show Calculation
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Left Column: Description & Requirements */}
        <div className="flex flex-col gap-6">
          <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-zinc-900">Job Description</h3>
            <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-4">
              <div className="whitespace-pre-wrap text-sm text-zinc-700">
                <JobTextHighlighter text={data.job_description || "No description provided."} keyword={hoveredKeyword} />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-zinc-900">Job Requirements</h3>
            {Array.isArray(data.job_requirements) && data.job_requirements.length > 0 ? (
              <ul className="list-inside list-disc space-y-2 text-sm text-zinc-700">
                {data.job_requirements.map((req: string, i: number) => (
                  <li key={i}><JobTextHighlighter text={req} keyword={hoveredKeyword} /></li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-zinc-500">No requirements specified</p>
            )}
          </div>
        </div>

        {/* Right Column: Resume Highlights */}
        <div className="flex flex-col gap-6">
          <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-zinc-900">Resume Breakdown</h3>
            <div className="whitespace-pre-wrap text-sm text-zinc-800">
              <HighlightedText
                text={data.resume_text}
                keywords={[...data.matched_skills, ...data.lexical_overlap_keywords]}
                onHover={setHoveredKeyword}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-zinc-200 bg-white p-4">
          <div className="mb-3 text-sm font-semibold text-zinc-900">Required Skills Checklist</div>
          {data.job_skills && data.job_skills.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <div className="mb-2 text-xs font-medium uppercase text-zinc-500">Matched</div>
                <div className="flex flex-wrap gap-2">
                  {data.job_skills.filter((s: string) => data.matched_skills.includes(s)).map((skill: string) => (
                    <span key={skill} className="rounded-full border border-green-200 bg-green-100 px-3 py-1 text-xs font-medium text-green-800">
                      {skill}
                    </span>
                  ))}
                  {data.job_skills.filter((s: string) => data.matched_skills.includes(s)).length === 0 && (
                    <span className="text-xs text-zinc-400">None</span>
                  )}
                </div>
              </div>
              <div>
                <div className="mb-2 text-xs font-medium uppercase text-zinc-500">Missing</div>
                <div className="flex flex-wrap gap-2">
                  {data.job_skills.filter((s: string) => !data.matched_skills.includes(s)).map((skill: string) => (
                    <span key={skill} className="rounded-full border border-red-200 bg-red-50 px-3 py-1 text-xs font-medium text-red-700">
                      {skill}
                    </span>
                  ))}
                  {data.job_skills.filter((s: string) => !data.matched_skills.includes(s)).length === 0 && (
                    <span className="text-xs text-zinc-400">None</span>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <span className="text-xs text-zinc-500">No specific skills detected in job description.</span>
          )}
        </div>

        <div className="rounded-lg border border-zinc-200 bg-white p-4">
          <div className="text-sm font-semibold text-zinc-900">Other Matched Keywords</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {data.lexical_overlap_keywords && data.lexical_overlap_keywords.length > 0 ? (
              data.lexical_overlap_keywords.map((keyword: string) => (
                <span
                  key={keyword}
                  className="rounded-full bg-yellow-100 px-3 py-1 text-xs font-medium text-yellow-800 border border-yellow-200"
                >
                  {keyword}
                </span>
              ))
            ) : (
              <span className="text-xs text-zinc-500">No additional lexical overlap detected.</span>
            )}
          </div>
        </div>
      </div>

      {calculationModalOpen && (
        <ScoreCalculationModal
          data={data}
          onClose={() => setCalculationModalOpen(false)}
        />
      )}
    </div>
  );
}

function ScoreCalculationModal({ data, onClose }: { data: any; onClose: () => void }) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  const r = data.scoring_report;
  const calc = r.calculation_breakdown ?? {};
  const baseScore = (r.base_score_percent ?? 0).toFixed(2);
  const skillMultiplier = (r.skill_multiplier ?? 1).toFixed(2);
  const expMultiplier = (r.experience_multiplier ?? 1).toFixed(2);
  const finalScore = r.final_score_percent.toFixed(2);
  const preClampScore = Number(calc.pre_clamp_score_percent ?? r.final_score_percent ?? 0).toFixed(2);
  const wasClamped = Boolean(calc.was_clamped);
  const breakdownSteps = Array.isArray(calc.steps) ? calc.steps : [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm transition-opacity">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-zinc-200 bg-white/80 px-6 py-4 backdrop-blur-md">
          <h2 className="text-xl font-bold text-zinc-900">Score Calculation Breakdown</h2>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900 transition-colors"
          >
            <span className="text-2xl leading-none">&times;</span>
          </button>
        </div>

        <div className="p-6 md:p-8">
          {/* Formula Visualization */}
          <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8 rounded-2xl border border-zinc-200 bg-zinc-50 p-6 shadow-inner mb-10">
            <div className="flex flex-col items-center text-center">
              <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Base Score</span>
              <span className="mt-1 text-4xl font-extrabold text-blue-600">{baseScore}%</span>
            </div>
            <div className="text-3xl font-bold text-zinc-300">×</div>
            <div className="flex flex-col items-center text-center">
              <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Skill Multiplier</span>
              <span className="mt-1 text-4xl font-extrabold text-emerald-600">{skillMultiplier}</span>
              <span className="mt-2 text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-1 rounded-md">{data.matched_count} / {data.job_skill_count} matched</span>
            </div>
            <div className="text-3xl font-bold text-zinc-300">×</div>
            <div className="flex flex-col items-center text-center">
              <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Exp. Multiplier</span>
              <span className="mt-1 text-4xl font-extrabold text-purple-600">{expMultiplier}</span>
              <span className="mt-2 text-xs font-medium text-purple-700 bg-purple-50 px-2 py-1 rounded-md">{r.candidate_years} / {r.required_years} years</span>
            </div>
            <div className="text-3xl font-bold text-zinc-300">=</div>
            <div className="flex flex-col items-center text-center rounded-xl bg-zinc-900 px-8 py-4 text-white shadow-lg">
              <span className="text-xs font-bold uppercase tracking-wider text-zinc-400">Final Score</span>
              <span className="mt-1 text-5xl font-black">{finalScore}%</span>
            </div>
          </div>

          {/* Detailed Explanations */}
          <div className="flex flex-col gap-6">
            <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-5">
              <h3 className="text-base font-bold text-zinc-900">Applied Formula</h3>
              <p className="mt-1 text-sm text-zinc-700">
                {(calc.formula as string) || "clamp(base_score * skill_multiplier * experience_multiplier)"}
              </p>
              <div className="mt-3 grid grid-cols-1 gap-2 text-sm text-zinc-700 sm:grid-cols-2">
                {breakdownSteps.map((step: any) => (
                  <div key={step.name} className="rounded-md border border-zinc-200 bg-white px-3 py-2">
                    <span className="font-semibold">{step.name}</span>
                    <span className="ml-2">
                      {step.percent_value != null ? `${Number(step.percent_value).toFixed(2)}%` : Number(step.value ?? 0).toFixed(4)}
                    </span>
                  </div>
                ))}
                <div className="rounded-md border border-zinc-200 bg-white px-3 py-2">
                  <span className="font-semibold">pre_clamp_score</span>
                  <span className="ml-2">{preClampScore}%</span>
                </div>
                <div className="rounded-md border border-zinc-200 bg-white px-3 py-2">
                  <span className="font-semibold">clamped</span>
                  <span className="ml-2">{wasClamped ? "yes" : "no"}</span>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 rounded-xl border border-blue-100 bg-blue-50/50 p-6">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-200 text-blue-800 font-bold text-lg shadow-sm">
                1
              </div>
              <div>
                <h3 className="text-lg font-bold text-blue-900">The AI Base Score</h3>
                <p className="mt-2 text-sm text-zinc-700 leading-relaxed">
                  Instead of just counting word frequencies, the AI reads the entire job description and the entire resume to understand their overall meaning.
                </p>
                <ul className="mt-3 list-disc pl-5 text-sm text-zinc-700 space-y-1.5 marker:text-blue-400">
                  <li>The AI spits out a raw "similarity" number.</li>
                  <li>The system mathematically scales this number so it looks like a normal grade (e.g., 80%). This is your starting point.</li>
                </ul>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 rounded-xl border border-emerald-100 bg-emerald-50/50 p-6">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-200 text-emerald-800 font-bold text-lg shadow-sm">
                2
              </div>
              <div>
                <h3 className="text-lg font-bold text-emerald-900">The Skill Multiplier</h3>
                <p className="mt-2 text-sm text-zinc-700 leading-relaxed">
                  Because the AI sometimes gets a little too creative with context, the system still demands hard keyword matches .
                </p>
                <ul className="mt-3 list-disc pl-5 text-sm text-zinc-700 space-y-1.5 marker:text-emerald-400">
                  <li>It extracts the required skills from the job and compares them to the resume.</li>
                  <li>If you have <strong>zero exact matches</strong>, your Base Score gets multiplied by <strong>0.75x</strong> (a 25% penalty).</li>
                  <li>If you match all required skills, your score is multiplied by <strong>1.10x</strong>, plus a small bonus for each matched skill (up to a max of <strong>1.25x</strong>).</li>
                </ul>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 rounded-xl border border-purple-100 bg-purple-50/50 p-6">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-purple-200 text-purple-800 font-bold text-lg shadow-sm">
                3
              </div>
              <div>
                <h3 className="text-lg font-bold text-purple-900">The Experience Multiplier</h3>
                <p className="mt-2 text-sm text-zinc-700 leading-relaxed">
                  Finally, it checks the years of experience.
                </p>
                <ul className="mt-3 list-disc pl-5 text-sm text-zinc-700 space-y-1.5 marker:text-purple-400">
                  <li>If the job asks for 5 years and the candidate has 5+ years, they get a <strong>1.1x multiplier</strong> (10% bonus).</li>
                  <li>If the candidate has fewer years, they get a <strong>penalty multiplier</strong> (dropping down to 0.85x).</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function HighlightedText({ text, keywords, onHover }: { text: string; keywords: string[]; onHover: (k: string | null) => void }) {
  if (!keywords || keywords.length === 0) return <>{text}</>;

  const sortedKeywords = [...keywords].sort((a, b) => b.length - a.length);
  const escapedKeywords = sortedKeywords.map((kw) => {
    let escaped = kw.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    if (/^\w/.test(kw)) escaped = `\\b${escaped}`;
    if (/\w$/.test(kw)) escaped = `${escaped}\\b`;
    return escaped;
  });
  
  const regex = new RegExp(`(${escapedKeywords.join("|")})`, "gi");
  const parts = text.split(regex);

  return (
    <>
      {parts.map((part, i) => (
        i % 2 === 1 ? (
          <mark
            key={i}
            className="bg-yellow-300 px-0.5 rounded-sm font-medium cursor-pointer"
            onMouseEnter={() => onHover(part.toLowerCase())}
            onMouseLeave={() => onHover(null)}
          >
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      ))}
    </>
  );
}

function JobTextHighlighter({ text, keyword }: { text: string; keyword: string | null }) {
  if (!keyword || !text) return <>{text}</>;

  const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`(\\b${escapedKeyword}\\b)`, "gi");

  if (!regex.test(text)) return <>{text}</>;

  const parts = text.split(regex);

  return (
    <>
      {parts.map((part, i) => (
        i % 2 === 1 ? (
          <mark key={i} className="bg-blue-300 px-0.5 rounded-sm font-medium transition-colors">
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      ))}
    </>
  );
}
