import { API_BASE_URL } from "./config";

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

function buildUrl(path: string): string {
  // `path` is expected to be absolute from the API root, e.g. `/api/jobs`.
  if (API_BASE_URL) return `${API_BASE_URL}${path}`;
  return path;
}

type ApiFetchOptions = {
  method: "GET" | "POST" | "PUT" | "DELETE";
  headers?: Record<string, string>;
  body?: unknown;
  formData?: FormData;
  signal?: AbortSignal;
};

export async function apiFetch<T>(
  path: string,
  options: ApiFetchOptions
): Promise<T | undefined> {
  const url = buildUrl(path);

  const headers: Record<string, string> = {
    ...(options.headers ?? {}),
  };

  let body: BodyInit | undefined;
  if (options.formData) {
    body = options.formData;
    // Do not set Content-Type for FormData; fetch will set boundary.
  } else if (options.body !== undefined) {
    headers["Content-Type"] = headers["Content-Type"] ?? "application/json";
    body = JSON.stringify(options.body);
  }

  const res = await fetch(url, {
    method: options.method,
    headers,
    body,
    signal: options.signal,
    cache: "no-store",
  });

  if (res.status === 204) {
    return undefined;
  }

  const contentType = res.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await res.json().catch(() => null) : await res.text().catch(() => null);

  if (!res.ok) {
    const message =
      (payload &&
      typeof payload === "object" &&
      payload !== null &&
      "error" in payload &&
      typeof (payload as { error?: unknown }).error === "string"
        ? (payload as { error: string }).error
        : undefined) ??
      res.statusText ??
      "Request failed";
    throw new ApiError(message, res.status, payload);
  }

  return payload as T;
}

