function envStringOrUndefined(key: string): string | undefined {
  const v = process.env[key];
  if (typeof v !== "string") return undefined;
  // Allow intentionally empty string to mean "same-origin" (relative URLs).
  return v.trim();
}

export const API_BASE_URL =
  // Default to same-origin relative URLs; `next.config.ts` rewrites proxy `/api/*`
  // to the Flask backend, avoiding cross-origin/CORS issues.
  envStringOrUndefined("NEXT_PUBLIC_API_BASE_URL") ?? "";

