"use client";

import { useEffect, useState } from "react";
import { getApplicationHighlightReport } from "@/lib/api/applications";
import type { HighlightReport } from "@/lib/api/types";

export default function ResumeHighlightModal({
  isOpen,
  onClose,
  applicationId,
  candidateName,
  jobTitle,
  jobDescription,
  jobRequirements,
  score,
}: {
  isOpen: boolean;
  onClose: () => void;
  applicationId: number;
  candidateName: string;
  jobTitle: string;
  jobDescription: string;
  jobRequirements: string[];
  score: number;
}) {
  const [data, setData] = useState<HighlightReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hoveredKeyword, setHoveredKeyword] = useState<string | null>(null);

  // Score color logic
  const getScoreColor = (s: number) => {
    if (s >= 80) return "bg-green-50 text-green-800 border-green-800";
    if (s >= 50) return "bg-yellow-50 text-yellow-900 border-yellow-900";
    return "bg-red-50 text-red-800 border-red-800";
  };

  useEffect(() => {
    if (!isOpen) return;

    setLoading(true);
    setError(null);

    getApplicationHighlightReport(applicationId)
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Error loading resume");
        setLoading(false);
      });
  }, [isOpen, applicationId]);

  useEffect(() => {
    if (!isOpen) return;

    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="relative flex max-h-[90vh] w-[90vw] max-w-7xl flex-col rounded-lg bg-white shadow-lg">
        {/* Header */}
        <div className="border-b border-zinc-200 px-6 py-4">
          <div className="flex items-start justify-between gap-6">
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-zinc-900">
                Resume - {candidateName}
              </h2>
              <p className="mt-1 text-sm font-medium text-zinc-800">
                Applying for: {jobTitle}
              </p>
              {data && (
                <p className="mt-1 text-sm text-zinc-600">
                  {data.matched_count} matching skills out of {data.job_skill_count} required
                </p>
              )}
            </div>

            {/* Score Circle */}
            <div className="flex flex-col items-center gap-3">
              <div className={`flex h-24 w-24 items-center justify-center rounded-full border-4 ${getScoreColor(score)}`}>
                <span className="text-4xl font-bold">
                  {Math.round(score)}
                </span>
              </div>
              <button
                onClick={() => window.open("/resume_job_pipeline.html", "_blank")}
                className="flex flex-col items-center gap-1"
                title="View scoring pipeline diagram"
              >
                <div className="flex h-6 w-6 items-center justify-center rounded-full border border-zinc-300 text-sm font-bold text-zinc-600 hover:bg-zinc-100 hover:border-zinc-400">
                  ?
                </div>
                <span className="text-xs text-zinc-600 max-w-28 text-center">
                  How is score calculated?
                </span>
              </button>
            </div>

            <button
              onClick={onClose}
              className="rounded-md p-1 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-700"
            >
              <span className="text-xl">×</span>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="grid grid-cols-2 gap-6 p-6">
            {/* Left Column: Description & Requirements */}
            <div className="flex flex-col gap-6">
              {/* Description */}
              <div className="flex flex-col gap-3">
                <h3 className="font-semibold text-zinc-900">Job Description</h3>
                <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-4">
                  <div className="whitespace-pre-wrap text-sm text-zinc-700">
                    <JobTextHighlighter text={jobDescription || "No description provided."} keyword={hoveredKeyword} />
                  </div>
                </div>
              </div>

              {/* Requirements */}
              <div className="flex flex-col gap-3">
                <h3 className="font-semibold text-zinc-900">Job Requirements</h3>
                {Array.isArray(jobRequirements) && jobRequirements.length > 0 ? (
                  <ul className="list-inside list-disc space-y-2 text-sm text-zinc-700">
                    {jobRequirements.map((req, i) => (
                      <li key={i}><JobTextHighlighter text={req} keyword={hoveredKeyword} /></li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-zinc-500">No requirements specified</p>
                )}
              </div>
            </div>

            {/* Resume */}
            <div className="flex flex-col gap-3">
              <h3 className="font-semibold text-zinc-900">Resume (Highlighted Keywords)</h3>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="text-sm text-zinc-600">Loading resume...</div>
                </div>
              ) : error ? (
                <div className="rounded bg-red-50 p-3 text-sm text-red-700">
                  {error}
                </div>
              ) : data ? (
                <div className="whitespace-pre-wrap text-sm text-zinc-800">
                  <HighlightedText
                    text={data.resume_text}
                    keywords={[...data.matched_skills, ...data.lexical_overlap_keywords]}
                    onHover={setHoveredKeyword}
                  />
                </div>
              ) : null}
            </div>
          </div>
          {data ? <ScoringReportCard data={data} /> : null}
        </div>

        {/* Footer */}
        <div className="border-t border-zinc-200 px-6 py-3 flex items-center justify-between">
          <a
            href={`/api/applications/${applicationId}/resume`}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold text-zinc-700 hover:bg-zinc-50"
          >
            Open Resume
          </a>
          <button
            onClick={onClose}
            className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function ScoringReportCard({ data }: { data: HighlightReport }) {
  const r = data.scoring_report;
  const calc = (r as any).calculation_breakdown ?? {};
  const baseScore = ((r as any).base_score_percent ?? 0).toFixed(2);
  const skillMultiplier = (r.skill_multiplier ?? 1).toFixed(2);
  const expMultiplier = ((r as any).experience_multiplier ?? 1).toFixed(2);
  const finalScore = r.final_score_percent.toFixed(2);
  const preClampScore = Number(calc.pre_clamp_score_percent ?? r.final_score_percent ?? 0).toFixed(2);
  const wasClamped = Boolean(calc.was_clamped);
  const breakdownSteps = Array.isArray(calc.steps) ? calc.steps : [];

  return (
    <div className="border-t border-zinc-200 px-6 py-8 bg-zinc-50/30">
      <h3 className="text-xl font-bold text-zinc-900 mb-6">Score Calculation Breakdown</h3>

      {/* Formula Visualization */}
      <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm mb-8">
        <div className="flex flex-col items-center text-center">
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Base Score</span>
          <span className="mt-1 text-3xl font-extrabold text-blue-600">{baseScore}%</span>
        </div>
        <div className="text-2xl font-bold text-zinc-300">×</div>
        <div className="flex flex-col items-center text-center">
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Skill Multiplier</span>
          <span className="mt-1 text-3xl font-extrabold text-emerald-600">{skillMultiplier}</span>
        </div>
        <div className="text-2xl font-bold text-zinc-300">×</div>
        <div className="flex flex-col items-center text-center">
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Exp. Multiplier</span>
          <span className="mt-1 text-3xl font-extrabold text-purple-600">{expMultiplier}</span>
        </div>
        <div className="text-2xl font-bold text-zinc-300">=</div>
        <div className="flex flex-col items-center text-center rounded-xl bg-zinc-900 px-6 py-3 text-white shadow-lg">
          <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400">Final Score</span>
          <span className="mt-1 text-4xl font-black">{finalScore}%</span>
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

        <div className="flex flex-col sm:flex-row gap-4 rounded-xl border border-blue-100 bg-blue-50/50 p-5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-200 text-blue-800 font-bold text-sm shadow-sm">
            1
          </div>
          <div>
            <h3 className="text-base font-bold text-blue-900">The AI Base Score (The "New" TF-IDF)</h3>
            <p className="mt-1 text-sm text-zinc-700 leading-relaxed">
              Instead of just counting word frequencies, the AI reads the entire job description and the entire resume to understand their overall meaning.
            </p>
            <ul className="mt-2 list-disc pl-5 text-sm text-zinc-700 space-y-1 marker:text-blue-400">
              <li>The AI spits out a raw "similarity" number.</li>
              <li>The system mathematically scales this number so it looks like a normal grade (e.g., 80%). This is your starting point.</li>
            </ul>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 rounded-xl border border-emerald-100 bg-emerald-50/50 p-5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-200 text-emerald-800 font-bold text-sm shadow-sm">
            2
          </div>
          <div>
            <h3 className="text-base font-bold text-emerald-900">The Skill Multiplier (The Keyword Check)</h3>
            <p className="mt-1 text-sm text-zinc-700 leading-relaxed">
              Because the AI sometimes gets a little too creative with context, the system still demands hard keyword matches (which is the part of TF-IDF we wanted to keep!).
            </p>
            <ul className="mt-2 list-disc pl-5 text-sm text-zinc-700 space-y-1 marker:text-emerald-400">
              <li>It extracts the required skills from the job and compares them to the resume.</li>
              <li>If you have <strong>zero exact matches</strong>, your Base Score gets multiplied by <strong>0.75x</strong> (a 25% penalty).</li>
              <li>If you match all of them, your Base Score gets multiplied by up to <strong>1.15x</strong> (a 15% bonus).</li>
            </ul>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 rounded-xl border border-purple-100 bg-purple-50/50 p-5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-purple-200 text-purple-800 font-bold text-sm shadow-sm">
            3
          </div>
          <div>
            <h3 className="text-base font-bold text-purple-900">The Experience Multiplier (The Seniority Check)</h3>
            <p className="mt-1 text-sm text-zinc-700 leading-relaxed">
              Finally, it checks the years of experience.
            </p>
            <ul className="mt-2 list-disc pl-5 text-sm text-zinc-700 space-y-1 marker:text-purple-400">
              <li>If the job asks for 5 years and the candidate has 5+ years, they get a <strong>1.1x multiplier</strong> (10% bonus).</li>
              <li>If the candidate has fewer years, they get a <strong>penalty multiplier</strong> (dropping down to 0.85x).</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="mt-10 grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="rounded-lg border border-zinc-200 bg-white p-3">
          <div className="text-sm font-semibold text-zinc-900">Matched skills</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {data.matched_skills.length ? (
              data.matched_skills.map((skill) => (
                <span
                  key={skill}
                  className="rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800"
                >
                  {skill}
                </span>
              ))
            ) : (
              <span className="text-xs text-zinc-500">No direct skill matches detected.</span>
            )}
          </div>
        </div>
        <div className="rounded-lg border border-zinc-200 bg-white p-3">
          <div className="text-sm font-semibold text-zinc-900">Other matched keywords</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {data.lexical_overlap_keywords.length ? (
              data.lexical_overlap_keywords.map((keyword) => (
                <span
                  key={keyword}
                  className="rounded-full bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-800"
                >
                  {keyword}
                </span>
              ))
            ) : (
              <span className="text-xs text-zinc-500">No lexical overlap keywords detected.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function HighlightedText({
  text,
  keywords,
  onHover,
}: {
  text: string;
  keywords: string[];
  onHover: (keyword: string | null) => void;
}) {
  if (!keywords || keywords.length === 0) return <>{text}</>;

  // Sort keywords by length descending so longer phrases match first
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
      {parts.map((part, i) => {
        // Every odd index is a matched keyword because of the single capture group in the regex
        if (i % 2 === 1) {
          return (
            <mark
              key={i}
              className="bg-yellow-300 px-0.5 rounded-sm font-medium cursor-pointer"
              onMouseEnter={() => onHover(part.toLowerCase())}
              onMouseLeave={() => onHover(null)}
            >
              {part}
            </mark>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}

function JobTextHighlighter({ text, keyword }: { text: string; keyword: string | null }) {
  if (!keyword || !text) {
    return <>{text}</>;
  }

  // Escape keyword for regex, and ensure it's treated as a whole word.
  const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`(\\b${escapedKeyword}\\b)`, "gi");

  if (!regex.test(text)) {
    return <>{text}</>;
  }

  const parts = text.split(regex);

  return (
    <>
      {parts.map((part, i) =>
        i % 2 === 1 ? (
          <mark
            key={i}
            className="bg-blue-300 px-0.5 rounded-sm font-medium transition-colors"
          >
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}
