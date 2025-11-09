import { useCallback, useMemo, useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Upload,
  Image as ImageIcon,
  Trash2,
  Wand2,
  Play,
  Loader2,
  FolderOpen,
  Link2,
} from "lucide-react";

// Helper types
interface UploadFile {
  id: string;
  file: File;
  previewUrl: string;
  name: string;
  sizeKB: number;
  type: string;
}

const MAX_FILES = 12;
const MAX_SIZE_MB = 15; // per file
const ACCEPTED = ["image/png", "image/jpeg", "image/webp"];

function formatBytes(bytes: number) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"] as const;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

interface ExistingProject {
  id: string;
  name: string;
  design_type?: string;
  created_at: string;
}

export default function DesignUploadScreen() {
  const navigate = useNavigate();
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [compareMode, setCompareMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [pollingStatus, setPollingStatus] = useState<string>("");
  const [projectId, setProjectId] = useState<string | null>(null);

  const [mode, setMode] = useState<"new" | "existing">("new");
  const [existingProjects, setExistingProjects] = useState<ExistingProject[]>([]);
  const [selectedProject, setSelectedProject] = useState("");

  const [projectName, setProjectName] = useState("");
  const [designType, setDesignType] = useState<"mobile" | "web" | "marketing">(
    "mobile"
  );
  const [depth, setDepth] = useState<"basic" | "deep" | "benchmark">("basic");
  const [persona, setPersona] = useState("Growth-focused PM at SaaS startup");
  const [goals, setGoals] = useState("Increase trial conversions by 10%.");

  const [agents, setAgents] = useState({
    visual: true,
    ux: true,
    accessibility: true,
    research: false,
    personaFit: false,
  });

  const [batchMode, setBatchMode] = useState(true);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const pollingIntervalRef = useRef<number | null>(null);

  // Input method: files upload or Figma URL
  const [inputMethod, setInputMethod] = useState<"files" | "figma">("files");
  const [figmaUrl, setFigmaUrl] = useState("");
  const [figmaToken, setFigmaToken] = useState("");

  // Fetch existing projects on page load
  useEffect(() => {
    async function loadProjects() {
      try {
        const res = await fetch("http://localhost:8000/api/projects");
        const data = await res.json();
        setExistingProjects(data.projects || []);
      } catch (err) {
        console.error("Failed to load projects:", err);
      }
    }
    loadProjects();
  }, []);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, []);

  const onSelectFiles = useCallback((list: FileList | null) => {
    if (!list) return;

    const next: UploadFile[] = [];
    for (const f of Array.from(list)) {
      if (!ACCEPTED.includes(f.type)) continue;
      if (f.size > MAX_SIZE_MB * 1024 * 1024) continue;
      next.push({
        id: crypto.randomUUID(),
        file: f,
        previewUrl: URL.createObjectURL(f),
        name: f.name,
        sizeKB: Math.round(f.size / 1024),
        type: f.type,
      });
    }
    setFiles((prev) => {
      const merged = [...prev, ...next].slice(0, MAX_FILES);
      return merged;
    });
  }, []);

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    onSelectFiles(e.dataTransfer.files);
  }, [onSelectFiles]);

  const onDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback(() => setIsDragging(false), []);

  const totalSize = useMemo(
    () => files.reduce((acc, f) => acc + f.file.size, 0),
    [files]
  );

  const isProjectInfoValid = (mode === "new"
    ? projectName.trim().length > 1
    : selectedProject !== "");

  const isValidUrl = useCallback((value: string) => {
    try {
      const u = new URL(value);
      return u.protocol === "http:" || u.protocol === "https:";
    } catch {
      return false;
    }
  }, []);

  const hasInput = inputMethod === "files" ? files.length > 0 : isValidUrl(figmaUrl);

  const canSubmit = hasInput && isProjectInfoValid;

  // // Debug logging
  // console.log("Upload validation:", {
  //   filesCount: files.length,
  //   mode,
  //   projectName,
  //   selectedProject,
  //   canSubmit
  // });

  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current !== null) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);
  async function handleSubmit() {
    if (!canSubmit) return;

    // Clear any previous polling
    stopPolling();

    setLoading(true);
    setProgress(12);

    try {
      let responseData;

      // If Figma URL is provided, use import-figma endpoint
      if (inputMethod === "figma") {
        setPollingStatus("Importing from Figma...");
        setProgress(30);

        const payload = {
          figmaUrl: figmaUrl.replace("/design/", "/file/"),
          figmaToken: figmaToken.trim() || undefined,
          projectName: mode === "new" ? projectName : undefined,
          project_id: mode === "existing" ? selectedProject : undefined,
          designType,
          depth,
          persona,
          goals,
          agents,
          batchMode: batchMode ? "yes" : "no"
        };

        const res = await fetch("http://localhost:8000/api/import-figma", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          throw new Error(`Figma import failed (${res.status})`);
        }

        responseData = await res.json();
        setProgress(100);
        setPollingStatus("Figma import complete. Analysis queued!");
      } else {
        // Original file upload flow
        setPollingStatus("Uploading files...");

        const form = new FormData();
        files.forEach((f) => form.append("files", f.file, f.name));

        if (mode === "new") {
          form.append("projectName", projectName);
        } else {
          form.append("project_id", selectedProject);
        }

        form.append("designType", designType);
        form.append("depth", depth);
        form.append("persona", persona);
        form.append("goals", goals);
        form.append("agents", JSON.stringify(agents));
        form.append("batchMode", batchMode ? "yes" : "no");

        // Upload files
        const req = new XMLHttpRequest();
        req.open("POST", "http://localhost:8000/api/analyze");
        req.upload.onprogress = (e) => {
          if (e.lengthComputable) {
            const pct = Math.round((e.loaded / e.total) * 60) + 20; // up to 80% during upload
            setProgress(Math.min(pct, 95));
          }
        };

        const done = await new Promise<{ ok: boolean; status: number; response: string }>((res) => {
          req.onload = () => res({
            ok: req.status >= 200 && req.status < 300,
            status: req.status,
            response: req.responseText
          });
          req.onerror = () => res({ ok: false, status: 0, response: "" });
          req.send(form);
        });

        if (!done.ok) {
          throw new Error(`Upload failed (${done.status})`);
        }

        setProgress(100);
        setPollingStatus("Upload complete. Analysis queued!");
        responseData = JSON.parse(done.response);
      }

      // Handle both new and append responses
      const newProjectId = responseData.project_id || responseData.id;
      const status = responseData.status; // Should be "queued"

      if (!newProjectId) {
        throw new Error("No project ID received from server");
      }

      console.log("Analysis queued:", { projectId: newProjectId, status });

      // Navigate to dashboard immediately with project context
      navigate("/projects", {
        state: {
          newProjectId,
          projectName: responseData.projectName || projectName,
          status: status || "queued"
        }
      });

    } catch (err: any) {
      console.error(err);
      setLoading(false);
      setPollingStatus("");
      setProgress(0);
      alert(err?.message ?? "Something went wrong");
    }
  }

  function toggleAgent(key: keyof typeof agents) {
    setAgents((a) => ({ ...a, [key]: !a[key] }));
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-xl border-b border-slate-200 shadow-sm">
        <div className="mx-auto max-w-6xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
                Design Analysis Platform
              </h1>
              <p className="text-sm text-slate-500 mt-0.5">AI-powered UI/UX audits & insights</p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={() => navigate("/projects")} className="shadow-sm">
                <FolderOpen className="mr-2 h-4 w-4" />
                My Projects
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl px-6 py-8 space-y-6">

      <div className="grid gap-6 md:grid-cols-3">
        {/* Left column: form */}
        <Card className="md:col-span-1 border-0 shadow-xl bg-white">
          <CardHeader>
            <CardTitle className="text-base">Project</CardTitle>
            <CardDescription>Basic info to tailor analysis</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Project Target</Label>

              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    checked={mode === "new"}
                    onChange={() => setMode("new")}
                    className="cursor-pointer"
                  />
                  <span className="text-sm">Create New</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    checked={mode === "existing"}
                    onChange={() => setMode("existing")}
                    className="cursor-pointer"
                  />
                  <span className="text-sm">Add to Existing</span>
                </label>
              </div>

              {mode === "new" && (
                <Input
                  id="projectName"
                  placeholder="e.g., Onboarding redesign – v2"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                />
              )}

              {mode === "existing" && (
                <select
                  className="w-full border border-input bg-background px-3 py-2 text-sm rounded-md ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  value={selectedProject}
                  onChange={(e) => setSelectedProject(e.target.value)}
                >
                  <option value="">Select project...</option>
                  {existingProjects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              )}
            </div>

            <div className="flex items-center gap-2">
              <Switch checked={batchMode} onCheckedChange={setBatchMode} />
              <Label>Batch Optimize (Recommended)</Label>
            </div>

            <div className="grid grid-cols-3 gap-2">
              {[
                { key: "mobile", label: "Mobile" },
                { key: "web", label: "Web" },
                { key: "marketing", label: "Marketing" },
              ].map((opt) => (
                <Button
                  key={opt.key}
                  type="button"
                  variant={designType === (opt.key as any) ? "default" : "outline"}
                  className="w-full"
                  onClick={() => setDesignType(opt.key as any)}
                >
                  {opt.label}
                </Button>
              ))}
            </div>

            <div className="space-y-2">
              <Label>Analysis depth</Label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { key: "basic", label: "Basic" },
                  { key: "deep", label: "Deep" },
                  { key: "benchmark", label: "Benchmark" },
                ].map((opt) => (
                  <Button
                    key={opt.key}
                    type="button"
                    variant={depth === (opt.key as any) ? "default" : "outline"}
                    className="w-full"
                    onClick={() => setDepth(opt.key as any)}
                  >
                    {opt.label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="persona">Target persona</Label>
              <Input
                id="persona"
                placeholder="Who is this for?"
                value={persona}
                onChange={(e) => setPersona(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="goals">Goals</Label>
              <Textarea
                id="goals"
                placeholder="What outcomes are you chasing?"
                value={goals}
                onChange={(e) => setGoals(e.target.value)}
                className="min-h-[88px]"
              />
            </div>

            <div className="space-y-3">
              <Label className="text-sm font-semibold">Analysis Agents</Label>
              <p className="text-xs text-slate-500 mb-3">Select which AI agents to include in your analysis</p>
              <div className="space-y-2">
                <AgentToggle
                  label="Visual design"
                  checked={agents.visual}
                  onChange={() => toggleAgent("visual")}
                />
                <AgentToggle
                  label="UX critique"
                  checked={agents.ux}
                  onChange={() => toggleAgent("ux")}
                />
                <AgentToggle
                  label="Accessibility"
                  checked={agents.accessibility}
                  onChange={() => toggleAgent("accessibility")}
                />
                <AgentToggle
                  label="Market research"
                  checked={agents.research}
                  onChange={() => toggleAgent("research")}
                />
                <AgentToggle
                  label="Persona fit"
                  checked={agents.personaFit}
                  onChange={() => toggleAgent("personaFit")}
                />
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex-col items-stretch gap-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Switch checked={compareMode} onCheckedChange={setCompareMode} id="compare" />
                <Label htmlFor="compare">Compare multiple screens</Label>
              </div>
              <Badge variant="outline">{files.length}/{MAX_FILES}</Badge>
            </div>
            <Button
              type="button"
              disabled={!canSubmit || loading}
              onClick={handleSubmit}
              className="w-full"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {pollingStatus || "Uploading…"}
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" /> Start analysis
                </>
              )}
            </Button>
            {(progress > 0 || pollingStatus) && (
              <div className="space-y-2">
                {progress > 0 && <Progress value={progress} />}
                <p className="text-xs text-muted-foreground">
                  {pollingStatus || `Preparing & uploading assets… ${progress}%`}
                </p>
                {projectId && (
                  <p className="text-xs text-muted-foreground">
                    Project ID: <code className="bg-muted px-1 py-0.5 rounded">{projectId}</code>
                  </p>
                )}
              </div>
            )}
          </CardFooter>
        </Card>

        {/* Right column: uploader */}
        <Card className="md:col-span-2 border-0 shadow-xl bg-white">
          <CardHeader>
            <CardTitle className="text-base">Upload designs</CardTitle>
            <CardDescription>
              {inputMethod === "files"
                ? <>PNG, JPG, WEBP. Max {MAX_SIZE_MB}MB each. Up to {MAX_FILES} files.</>
                : <>Provide a public Figma file or prototype URL</>
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            

            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-slate-600">Use Figma URL</div>
              <Switch
                checked={inputMethod === "figma"}
                onCheckedChange={(v) => setInputMethod(v ? "figma" : "files")}
              />
            </div>

            {inputMethod === "figma" ? (
              <div className="space-y-2">
                <div className="space-y-2 mb-6">
                  <Label htmlFor="figmaUrl">Import from Figma Link</Label>
                  <Input
                    id="figmaUrl"
                    placeholder="https://www.figma.com/file/..."
                    value={figmaUrl}
                    onChange={(e) => setFigmaUrl(e.target.value)}
                  />
                </div>
                <div className="space-y-2 mb-6">
                  <Label htmlFor="figmaToken">Enter Figma Access Token</Label>
                  <Input
                    id="figmaToken"
                    type="password"
                    value={figmaToken}
                    onChange={(e) => setFigmaToken(e.target.value)}
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Ensure the link is accessible. Workspace auth-protected links
                  may fail.
                </p>
              </div>
            ) : (
            <div
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              className={[
                "relative flex h-48 w-full items-center justify-center rounded-2xl border border-dashed",
                isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/20",
              ].join(" ")}
            >
              <div className="text-center space-y-2">
                <Upload className="mx-auto h-8 w-8" />
                <p className="text-sm">
                  Drag & drop your images here
                </p>
                <p className="text-xs text-muted-foreground">or</p>
                <div className="flex items-center justify-center gap-2">
                  <Button type="button" variant="secondary" onClick={() => inputRef.current?.click()}>
                    <ImageIcon className="mr-2 h-4 w-4" /> Choose files
                  </Button>
                  <input
                    ref={inputRef}
                    type="file"
                    accept={ACCEPTED.join(",")}
                    multiple={compareMode}
                    className="hidden"
                    onChange={(e) => onSelectFiles(e.target.files)}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-2">{files.length > 0 ? `${files.length} selected • ${formatBytes(totalSize)}` : `No files selected`}</p>
              </div>
            </div>
            )}

            {/* Previews */}
            {inputMethod === "files" && (
              <AnimatePresence>
                {files.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className="mt-5 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4"
                  >
                    {files.map((f) => (
                      <motion.div
                        layout
                        key={f.id}
                        className="group relative overflow-hidden rounded-2xl border"
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                      >
                        <img
                          src={f.previewUrl}
                          alt={f.name}
                          className="h-44 w-full object-cover"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                        <div className="absolute bottom-0 left-0 right-0 p-2 text-xs text-white flex items-center justify-between">
                          <span className="truncate pr-2">{f.name}</span>
                          <span className="opacity-80">{formatBytes(f.file.size)}</span>
                        </div>
                        <div className="absolute right-2 top-2 flex gap-2">
                          <Button size="icon" variant="secondary" className="h-8 w-8" onClick={() => removeFile(f.id)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            )}
          </CardContent>
          <CardFooter className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <Wand2 className="h-4 w-4" />
              Tips: Clear device chrome, include before/after variants, and ensure readable text.
            </div>
            <div>
              {inputMethod === "files"
                ? <>Accepted: PNG, JPG, WEBP • Max {MAX_SIZE_MB}MB each</>
                : <>Enter a public Figma URL</>}
            </div>
          </CardFooter>
        </Card>
      </div>
      </div>
    </div>
  );
}

function AgentToggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: () => void }) {
  return (
    <div className={`flex items-center justify-between rounded-lg border p-3 transition-all duration-200 ${
      checked
        ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 shadow-sm'
        : 'bg-white border-slate-200 hover:border-slate-300'
    }`}>
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div className={`flex items-center justify-center w-8 h-8 rounded-lg transition-colors ${
          checked ? 'bg-blue-100' : 'bg-slate-100'
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            checked ? 'bg-blue-600' : 'bg-slate-400'
          }`} />
        </div>
        <Label htmlFor={label} className="text-sm font-medium text-slate-900 cursor-pointer flex-1">
          {label}
        </Label>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Switch id={label} checked={checked} onCheckedChange={onChange} />
      </div>
    </div>
  );
}
