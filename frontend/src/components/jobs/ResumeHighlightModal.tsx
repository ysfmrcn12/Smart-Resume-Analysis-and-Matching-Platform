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
      <div className="relative flex max-h-[90vh] w-full max-w-4xl flex-col rounded-lg bg-white shadow-lg">
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
                  <p className="whitespace-pre-wrap text-sm text-zinc-700">
                    {jobDescription || "No description provided."}
                  </p>
                </div>
              </div>

              {/* Requirements */}
              <div className="flex flex-col gap-3">
                <h3 className="font-semibold text-zinc-900">Job Requirements</h3>
                {Array.isArray(jobRequirements) && jobRequirements.length > 0 ? (
                  <ul className="list-inside list-disc space-y-2 text-sm text-zinc-700">
                    {jobRequirements.map((req, i) => (
                      <li key={i}>{req}</li>
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
  return (
    <div className="border-t border-zinc-200 px-6 py-5">
      <h3 className="text-base font-semibold text-zinc-900">How this score was obtained</h3>
      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-3 text-sm text-zinc-700">
          <div className="font-semibold text-zinc-900">Final Score</div>
          <div className="mt-1">{r.final_score_percent.toFixed(2)}%</div>
          <div className="mt-2 text-xs text-zinc-600">
            Base score {r.base_score_percent.toFixed(2)}% x skill multiplier {r.skill_multiplier.toFixed(2)}
          </div>
        </div>
        <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-3 text-sm text-zinc-700">
          <div className="font-semibold text-zinc-900">TF-IDF Component</div>
          <div className="mt-1">
            {r.tfidf_percent.toFixed(2)}% (raw cosine: {r.tfidf_raw.toFixed(4)})
          </div>
          <div className="mt-2 text-xs text-zinc-600">
            Weight in final base score: {((r.weights.tfidf ?? 1) * 100).toFixed(0)}%
          </div>
        </div>
        <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-3 text-sm text-zinc-700">
          <div className="font-semibold text-zinc-900">Skill Alignment</div>
          <div className="mt-1">
            {(r.skill_overlap_ratio * 100).toFixed(2)}% overlap ({data.matched_count}/{data.job_skill_count})
          </div>
          <div className="mt-2 text-xs text-zinc-600">
            Multiplier applied to base score: {r.skill_multiplier.toFixed(2)}
          </div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
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
}: {
  text: string;
  keywords: string[];
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
            <mark key={i} className="bg-yellow-300 px-0.5 rounded-sm font-medium">
              {part}
            </mark>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}
