"use client";

import { useEffect, useState } from "react";

interface HighlightData {
  resume_text: string;
  matching_skills: Record<string, Array<[number, number]>>;
  matched_count: number;
  job_skill_count: number;
}

export default function ResumeHighlightModal({
  isOpen,
  onClose,
  applicationId,
  candidateName,
}: {
  isOpen: boolean;
  onClose: () => void;
  applicationId: number;
  candidateName: string;
}) {
  const [data, setData] = useState<HighlightData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    setLoading(true);
    setError(null);

    fetch(`/api/applications/${applicationId}/highlights`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load highlights");
        return res.json();
      })
      .then((data: HighlightData) => {
        setData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Error loading resume");
        setLoading(false);
      });
  }, [isOpen, applicationId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="relative flex max-h-[90vh] w-full max-w-2xl flex-col rounded-lg bg-white shadow-lg">
        {/* Header */}
        <div className="border-b border-zinc-200 px-6 py-4">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-lg font-semibold text-zinc-900">
                Resume - {candidateName}
              </h2>
              {data && (
                <p className="mt-1 text-sm text-zinc-600">
                  {data.matched_count} matching skills out of {data.job_skill_count} required
                </p>
              )}
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
        <div className="flex-1 overflow-y-auto px-6 py-4">
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
                matchingSkills={data.matching_skills}
              />
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="border-t border-zinc-200 px-6 py-3 text-right">
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

function HighlightedText({
  text,
  matchingSkills,
}: {
  text: string;
  matchingSkills: Record<string, Array<[number, number]>>;
}) {
  // Build a set of all position ranges to highlight
  const highlightRanges = new Set<number>();
  const positionToSkill: Record<number, string> = {};

  Object.entries(matchingSkills).forEach(([skill, positions]) => {
    positions.forEach(([start, end]) => {
      for (let i = start; i < end; i++) {
        highlightRanges.add(i);
      }
      positionToSkill[start] = skill;
    });
  });

  const elements = [];
  let currentPos = 0;
  const sortedPositions = Array.from(highlightRanges).sort((a, b) => a - b);

  // Group consecutive positions into ranges
  let rangeStart = null;
  let prevPos = -2;

  for (const pos of sortedPositions) {
    if (pos !== prevPos + 1) {
      if (rangeStart !== null && prevPos !== null) {
        // End of a range, add non-highlighted text before and highlighted after
        if (rangeStart > currentPos) {
          elements.push(
            <span key={`text-${currentPos}`}>
              {text.slice(currentPos, rangeStart)}
            </span>
          );
        }
        elements.push(
          <mark key={`highlight-${rangeStart}`} className="bg-yellow-300">
            {text.slice(rangeStart, prevPos + 1)}
          </mark>
        );
        currentPos = prevPos + 1;
      }
      rangeStart = pos;
    }
    prevPos = pos;
  }

  // Handle remaining ranges
  if (rangeStart !== null && prevPos !== null) {
    if (rangeStart > currentPos) {
      elements.push(
        <span key={`text-${currentPos}`}>{text.slice(currentPos, rangeStart)}</span>
      );
    }
    elements.push(
      <mark key={`highlight-${rangeStart}`} className="bg-yellow-300">
        {text.slice(rangeStart, prevPos + 1)}
      </mark>
    );
    currentPos = prevPos + 1;
  }

  // Add remaining text
  if (currentPos < text.length) {
    elements.push(
      <span key={`text-${currentPos}`}>{text.slice(currentPos)}</span>
    );
  }

  return <>{elements}</>;
}
