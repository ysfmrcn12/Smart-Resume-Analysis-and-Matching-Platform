function envStringOrUndefined(key: string): string | undefined {
  const v = process.env[key];
  if (typeof v !== "string") return undefined;
  // Allow intentionally empty string to mean "same-origin" (relative URLs).
  return v.trim();
}

export const API_BASE_URL =
  envStringOrUndefined("NEXT_PUBLIC_API_BASE_URL") ?? "http://localhost:5000";

