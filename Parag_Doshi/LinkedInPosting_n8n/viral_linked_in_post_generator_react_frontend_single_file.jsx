"use client";

import React, { useMemo, useState } from "react";

// --- CONFIG ---
// You can point these directly at n8n webhooks OR at your Next.js API routes
// (recommended to avoid CORS). If using your server route, set both to 
// something like "/api/generate" and "/api/publish" respectively.
const GENERATE_WEBHOOK_URL =
  "https://pdoshi.app.n8n.cloud/webhook-test/ee3e9945-97dc-470e-9ee5-053d528e15eb";
const PUBLISH_WEBHOOK_URL =
  "https://pdoshi.app.n8n.cloud/webhook-test/20c84917-2446-49f4-9270-28efb9d31ed5";

export default function ViralLinkedInPostGenerator() {
  // Form state (matches your Bolt schema)
  const [theme, setTheme] = useState("");
  const [postType, setPostType] = useState("Thought Leadership");
  const [length, setLength] = useState("Medium (3-8 lines)");
  const [tone, setTone] = useState("Professional / Formal");

  // Generated + publish response
  const [generatedPost, setGeneratedPost] = useState("");
  const [publishResponse, setPublishResponse] = useState<any>(null);

  // UI state
  const [loading, setLoading] = useState<"generate" | "publish" | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Options (enum values from your schema)
  const postTypeOptions = useMemo(
    () => [
      "Thought Leadership",
      "Industry Insights",
      "How-to / Educational",
      "Personal Story",
      "Opinion",
      "Announcement",
      "Case Study",
    ],
    []
  );

  const lengthOptions = useMemo(
    () => ["Short (1-3 lines)", "Medium (3-8 lines)", "Long (8+ lines)"],
    []
  );

  const toneOptions = useMemo(
    () => [
      "Inspirational",
      "Personal Story",
      "Professional / Formal",
      "GenZ / Casual",
      "Humorous",
      "Motivational",
    ],
    []
  );

  const valid = theme.trim() && postType && length && tone;

  async function handleGenerate() {
    if (!valid) {
      setError("Please complete all fields before generating.");
      return;
    }
    setError(null);
    setLoading("generate");
    setPublishResponse(null);

    const payload = { theme, post_type: postType, length, tone };
    try {
      const res = await fetch(GENERATE_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      // Some n8n nodes may return text; others return JSON. Try both.
      const contentType = res.headers.get("content-type") || "";
      if (!res.ok) {
        const msg = `Generate webhook error ${res.status}`;
        throw new Error(msg);
      }

      if (contentType.includes("application/json")) {
        const data = await res.json();
        // Try a few common shapes
        const text =
          typeof data === "string"
            ? data
            : data.post || data.text || JSON.stringify(data, null, 2);
        setGeneratedPost(text);
      } else {
        const text = await res.text();
        setGeneratedPost(text);
      }
    } catch (err: any) {
      setError(err?.message || "Failed to generate post.");
    } finally {
      setLoading(null);
    }
  }

  async function handlePublish() {
    if (!generatedPost.trim()) {
      setError("Nothing to publish yet. Generate or paste a post first.");
      return;
    }
    setError(null);
    setLoading("publish");

    const payload = {
      post_text: generatedPost,
      metadata: { theme, post_type: postType, length, tone },
    };

    try {
      const res = await fetch(PUBLISH_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const contentType = res.headers.get("content-type") || "";
      if (contentType.includes("application/json")) {
        const data = await res.json();
        setPublishResponse(data);
      } else {
        const text = await res.text();
        setPublishResponse({ raw: text, status: res.status });
      }

      if (!res.ok) {
        throw new Error(
          `Publish webhook error ${res.status}: ${JSON.stringify(
            publishResponse,
            null,
            2
          )}`
        );
      }
    } catch (err: any) {
      setError(err?.message || "Failed to publish post.");
    } finally {
      setLoading(null);
    }
  }

  function FieldLabel({ children }: { children: React.ReactNode }) {
    return <label className="text-sm font-medium text-gray-700">{children}</label>;
  }

  return (
    <div className="min-h-screen w-full bg-gray-50 text-gray-900">
      <div className="mx-auto max-w-3xl p-6">
        <header className="mb-6">
          <h1 className="text-2xl font-bold">Viral LinkedIn Post Generator</h1>
          <p className="text-sm text-gray-600">
            Fill the fields, click <span className="font-semibold">Generate</span> to draft a
            LinkedIn post, edit if needed, then <span className="font-semibold">Publish</span>.
          </p>
        </header>

        {/* Form Card */}
        <div className="rounded-2xl bg-white p-6 shadow">
          <div className="grid grid-cols-1 gap-4">
            <div className="flex flex-col gap-2">
              <FieldLabel>Theme / Idea *</FieldLabel>
              <input
                className="w-full rounded-xl border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., AI in healthcare"
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
              />
            </div>

            <div className="flex flex-col gap-2">
              <FieldLabel>Post Type / Category *</FieldLabel>
              <select
                className="w-full rounded-xl border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={postType}
                onChange={(e) => setPostType(e.target.value)}
              >
                {postTypeOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <FieldLabel>Length *</FieldLabel>
              <select
                className="w-full rounded-xl border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={length}
                onChange={(e) => setLength(e.target.value)}
              >
                {lengthOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <FieldLabel>Tone *</FieldLabel>
              <select
                className="w-full rounded-xl border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={tone}
                onChange={(e) => setTone(e.target.value)}
              >
                {toneOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              onClick={handleGenerate}
              disabled={loading === "generate"}
              className="rounded-2xl px-4 py-2 shadow disabled:opacity-60 bg-blue-600 text-white hover:bg-blue-700"
            >
              {loading === "generate" ? "Generating…" : "Generate"}
            </button>
            <button
              onClick={handlePublish}
              disabled={loading === "publish" || !generatedPost}
              className="rounded-2xl px-4 py-2 shadow disabled:opacity-60 bg-green-600 text-white hover:bg-green-700"
            >
              {loading === "publish" ? "Publishing…" : "Publish"}
            </button>
            {!valid && (
              <span className="text-sm text-red-600">All fields are required.</span>
            )}
          </div>

          {/* Generated Post */}
          <div className="mt-6">
            <FieldLabel>Generated LinkedIn Post</FieldLabel>
            <textarea
              className="mt-2 h-48 w-full rounded-xl border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Generated post will appear here. You can edit before publishing."
              value={generatedPost}
              onChange={(e) => setGeneratedPost(e.target.value)}
            />
          </div>

          {/* Error / Publish response */}
          {error && (
            <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-red-700">
              {error}
            </div>
          )}

          {publishResponse && (
            <div className="mt-4 rounded-xl border border-gray-200 bg-gray-50 p-3 text-sm">
              <div className="font-semibold">Publish response</div>
              <pre className="mt-2 whitespace-pre-wrap break-words text-xs">
                {JSON.stringify(publishResponse, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Helper: Example schema + payloads */}
        <section className="mt-8 space-y-3 text-sm text-gray-700">
          <h2 className="text-base font-semibold">Integration Notes</h2>
          <ul className="list-inside list-disc space-y-1">
            <li>
              In production, consider routing through <code>/api/generate</code> and
              <code> /api/publish</code> with server-to-server calls to n8n.
            </li>
            <li>
              Add retries/backoff for publish, and consider idempotency keys to avoid duplicate
              posts.
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}
