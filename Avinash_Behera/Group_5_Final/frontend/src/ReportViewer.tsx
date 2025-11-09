import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, ArrowLeft, FolderOpen, Eye, MousePointer, Accessibility, CheckCircle2, AlertTriangle, Download, TrendingUp, Zap, Target, Users, TrendingDown, Lightbulb, UserCheck, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

interface ScreenResult {
  visual?: {
    _meta?: any;
    issues?: any[];
    strengths?: string[];
    recommendations?: string[];
  };
  ux?: {
    _meta?: any;
    usability_problems?: any[];
    confusing_elements?: string[];
  };
  accessibility?: {
    _meta?: any;
    score?: number;
    issues?: any[];
  };
  market?: {
    _meta?: any;
    design_positioning?: string;
    closest_comparisons?: string[];
    conversion_risk_points?: string[];
    differentiation_opportunities?: string[];
  };
  persona?: {
    _meta?: any;
    trust_score?: number;
    clarity_score?: number;
    recommendations?: string[];
    confusion_points?: string[];
  };
  research?: {
    _meta?: any;
    design_positioning?: string;
    closest_comparisons?: string[];
    conversion_risk_points?: string[];
    differentiation_opportunities?: string[];
  };
}


const priorityStyles: Record<string, string> = {
  "Do Now": "bg-red-600 text-white border-red-700",
  "Quick Win": "bg-green-600 text-white border-green-700",
  "Plan": "bg-blue-600 text-white border-blue-700",
  "Low Value": "bg-gray-300 text-gray-800 border-gray-400",
};

const priorityOrder = {
  "Do Now": 1,
  "Quick Win": 2,
  "Plan": 3,
  "Low Value": 4,
};

function classifyPriority(impact: string, effort: string) {
  if (impact === "High" && effort === "Low") return "Do Now";
  if (impact === "High" && effort === "High") return "Plan";
  if (impact === "Low" && effort === "Low") return "Quick Win";
  return "Low Value";
}

function sortByPriority(items: any[]) {
  return [...items].sort(
    (a, b) =>
      priorityOrder[classifyPriority(a.impact, a. effort)] -
      priorityOrder[classifyPriority(b.impact, b.effort)]
  );
}


// Helper function to parse JSON from markdown code blocks
function parseJsonString(jsonStr: string): any {
  try {
    // Remove markdown code blocks if present
    const cleaned = jsonStr.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    return JSON.parse(cleaned);
  } catch (err) {
    console.error("Failed to parse JSON:", err);
    return null;
  }
}

export default function ReportViewer() {
  const { jobId: projectId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedScreen, setSelectedScreen] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<string>("visual");

  useEffect(() => {
    if (!projectId) {
      console.error("No jobId provided");
      setLoading(false);
      return;
    }

    // console.log("Loading report for jobId:", projectId);

    async function load() {
      try {
        const res = await fetch(`http://localhost:8000/api/project/${projectId}`);

        if (!res.ok) {
          throw new Error(`Failed to fetch job: ${res.status} ${res.statusText}`);
        }

        const json = await res.json();
        // console.log("Received job data:", json);

        // Parse the JSON strings in the response
        if (json.analysis && json.analysis.length > 0) {
          json.analysis.forEach((analysisItem:any) => {
            const screens = analysisItem.result_json?.screens;
            if (!screens) return;

            Object.keys(screens).forEach((screenKey) => {
              const screen = screens[screenKey];

              

              // Parse visual data if it's a string
              if (typeof screen.visual === "string") {
                screen.visual = parseJsonString(screen.visual);
              }

              // Parse ux data if it's a string
              if (typeof screen.ux === "string") {
                screen.ux = parseJsonString(screen.ux);
              }

              // Parse accessibility data if it's a string
              if (typeof screen.accessibility === "string") {
                screen.accessibility = parseJsonString(screen.accessibility);
              }

              // Parse market data if it's a string
              if (typeof screen.market === "string") {
                screen.market = parseJsonString(screen.market);
              }

              // Parse persona data if it's a string
              if (typeof screen.persona === "string") {
                screen.persona = parseJsonString(screen.persona);
              }

              // Parse research data if it's a string
              if (typeof screen.research === "string") {
                screen.research = parseJsonString(screen.research);
              }
            });
          });
        }

        setData(json);
      } catch (err) {
        console.error("Error loading report:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [projectId]);

  if (loading) {
    return (
      <div className="flex h-60 items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  // Validate data and ensure there are analysis results
  if (!data || !Array.isArray(data.analysis) || data.analysis.length === 0) {
    return (
      <div className="p-6 text-center text-muted-foreground">
        Report not ready or job not found.
      </div>
    );
  }

  // Ensure at least one has status complete
  const isComplete = data.analysis.some((a:any) => a.result_json?.status === "complete");
  if (!isComplete) {
    return (
      <div className="p-6 text-center text-muted-foreground">
        Report not ready or processing...
      </div>
    );
  }

      // Flatten screens across all analysis entries
    let totalCost = 0;
    let totalTokens = 0;

    // Track if a dimension has already been charged (per analysis)
    data.analysis.forEach((analysis: any) => {
      const dimensionSeen: Record<string, boolean> = {};

      const screens = analysis.result_json?.screens;
      if (!screens) return;

      Object.values(screens).forEach((screen: any) => {
        ["ux", "visual", "market", "accessibility"].forEach((dim) => {
          const meta = screen[dim]?._meta;
          if (!meta) return;

          const { cost_usd, tokens, batchMode } = meta;

          if (batchMode === "yes") {
            // Count this dimension only once per analysis
            if (!dimensionSeen[dim]) {
              dimensionSeen[dim] = true;
              totalCost += cost_usd;
              totalTokens += tokens;
            }
          } else {
            // Normal counting
            totalCost += cost_usd;
            totalTokens += tokens;
          }
        });
      });
    });

    console.log("Total Cost:", totalCost);
    console.log("Total Tokens:", totalTokens);

  // Extract screens from the first analysis result that has screens
  const screens = data.analysis.find((a: any) => a.result_json?.screens)?.result_json?.screens || {};

  const screenCount = Object.keys(screens).length;

  // Get the selected screen data first
  const screensArray = Object.entries<ScreenResult>(screens);
  const [selectedPath, selectedResult] = screensArray[selectedScreen] || [undefined, undefined] as [string | undefined, ScreenResult | undefined];

  // Calculate summary stats from ALL screens
  const allIssues: any[] = [];
  const allStrengths: string[] = [];

  Object.values<ScreenResult>(screens).forEach((screenResult) => {
    if (screenResult.visual?.issues) allIssues.push(...screenResult.visual.issues);
    if (screenResult.ux?.usability_problems) allIssues.push(...screenResult.ux.usability_problems);
    if (screenResult.visual?.strengths) allStrengths.push(...screenResult.visual.strengths);
  });

  const criticalIssues = allIssues.filter(i => classifyPriority(i.impact, i.effort) === "Do Now").length;
  const quickWins = allIssues.filter(i => classifyPriority(i.impact, i.effort) === "Quick Win").length;

  // Available tabs based on data
  const tabs = [
    { id: "visual", label: "Visual Design", icon: Eye, available: !!selectedResult?.visual, color: "from-pink-500 to-purple-600", bgColor: "bg-pink-50", borderColor: "border-pink-200" },
    { id: "ux", label: "UX Heuristics", icon: MousePointer, available: !!selectedResult?.ux, color: "from-blue-500 to-cyan-600", bgColor: "bg-blue-50", borderColor: "border-blue-200" },
    { id: "accessibility", label: "Accessibility", icon: Accessibility, available: !!selectedResult?.accessibility, color: "from-emerald-500 to-teal-600", bgColor: "bg-emerald-50", borderColor: "border-emerald-200" },
    { id: "persona", label: "Persona Fit", icon: UserCheck, available: !!selectedResult?.persona, color: "from-violet-500 to-indigo-600", bgColor: "bg-violet-50", borderColor: "border-violet-200" },
    { id: "research", label: "Market Research", icon: BarChart3, available: !!selectedResult?.research, color: "from-cyan-500 to-sky-600", bgColor: "bg-cyan-50", borderColor: "border-cyan-200" },
    { id: "market", label: "Competitive Analysis", icon: Target, available: !!selectedResult?.market, color: "from-orange-500 to-amber-600", bgColor: "bg-orange-50", borderColor: "border-orange-200" },
  ].filter(t => t.available);

  // Ensure active tab exists in available tabs
  const currentActiveTab = tabs.find(t => t.id === activeTab) ? activeTab : (tabs[0]?.id || "visual");

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-xl border-b border-slate-200 shadow-sm">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
                Design Audit Report
              </h1>
              <p className="text-sm text-slate-500 mt-0.5">Professional UI/UX Analysis</p>
            </div>

            <div className="flex gap-3">
              <Button variant="outline" size="sm" onClick={() => navigate("/projects")} className="shadow-sm">
                <FolderOpen className="mr-2 h-4 w-4" />
                All Projects
              </Button>
              <Button variant="outline" size="sm" onClick={() => navigate("/")} className="shadow-sm">
                <ArrowLeft className="mr-2 h-4 w-4" />
                New Analysis
              </Button>
              <Button size="sm" className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg shadow-blue-500/30">
                <a href={`http://localhost:8000/api/project/${projectId}/export-pdf`} target="_blank" rel="noreferrer" className="flex items-center">
                  <Download className="mr-2 h-4 w-4" />
                  Export PDF
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area with Sidebars */}
      <div className="flex">
        {/* Left Sidebar - Thumbnail Navigation */}
        <div className="hidden lg:block w-32 sticky top-20 h-[calc(100vh-5rem)] overflow-y-auto border-r border-slate-200 bg-white/50 backdrop-blur-sm">
          <div className="p-3 space-y-2">
            <h3 className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-3">
              Screens ({screenCount})
            </h3>
            {screensArray.map(([path], idx) => {
              const isSelected = selectedScreen === idx;
              return (
                <button
                  key={path}
                  onClick={() => setSelectedScreen(idx)}
                  className="w-full relative rounded-lg overflow-hidden"
                  style={{
                    transform: 'translateZ(0)',
                    backfaceVisibility: 'hidden' as const,
                    outline: isSelected ? '2px solid rgb(59 130 246)' : 'none',
                    outlineOffset: '0px',
                    boxShadow: isSelected ? '0 10px 15px -3px rgb(0 0 0 / 0.1)' : 'none'
                  }}
                >
                  <div className="aspect-[3/4] bg-gradient-to-br from-slate-100 to-slate-200">
                    <img
                      src={`http://localhost:8000/files/${path.replace(/\\/g, "/").replace("storage/", "")}`}
                      alt={`Screen ${idx + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  {isSelected && (
                    <>
                      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent">
                        <div className="absolute bottom-0 left-0 right-0 p-1.5">
                          <p className="text-[10px] font-semibold text-white text-center">#{idx + 1}</p>
                        </div>
                      </div>
                      <div className="absolute top-1.5 right-1.5">
                        <div className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse"></div>
                      </div>
                    </>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Middle Content - Analysis */}
        <div className="flex-1 min-w-0">
          <div className="mx-auto max-w-6xl px-6 py-8 space-y-8">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-600">Screens Analyzed</p>
                        <p className="text-3xl font-bold text-slate-900 mt-1">{screenCount}</p>
                      </div>
                      <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                        <Eye className="h-6 w-6 text-blue-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card className="border-0 shadow-lg bg-gradient-to-br from-red-50 to-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-600">Critical Issues</p>
                        <p className="text-3xl font-bold text-red-600 mt-1">{criticalIssues}</p>
                      </div>
                      <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
                        <AlertTriangle className="h-6 w-6 text-red-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-600">Quick Wins</p>
                        <p className="text-3xl font-bold text-green-600 mt-1">{quickWins}</p>
                      </div>
                      <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                        <Zap className="h-6 w-6 text-green-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-600">Total Cost</p>
                        <p className="text-3xl font-bold text-purple-600 mt-1">${totalCost.toFixed(3)}</p>
                      </div>
                      <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
                        <TrendingUp className="h-6 w-6 text-purple-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* Single Screen Analysis Card */}
            {selectedResult && (
              <motion.div
                key={selectedScreen}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="overflow-hidden border-0 shadow-xl bg-white">
                  <CardHeader className="bg-gradient-to-r from-slate-50 to-white border-b border-slate-200 pb-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-lg font-semibold text-slate-900 truncate">
                          Screen {selectedScreen + 1} of {screenCount}
                        </CardTitle>
                        <p className="text-xs text-slate-500 truncate mt-1">{selectedPath}</p>
                      </div>
                      <Badge className="bg-blue-100 text-blue-700 border-blue-200">Screen Analysis</Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="p-0">
                    {/* Tab Navigation */}
                    <div className="border-b border-slate-200 bg-white px-6 sticky top-20 z-10">
                      <div className="flex gap-1 overflow-x-auto">
                        {tabs.map((tab) => {
                          const Icon = tab.icon;
                          return (
                            <button
                              key={tab.id}
                              onClick={() => setActiveTab(tab.id)}
                              className={`flex items-center gap-2 px-6 py-4 text-sm font-semibold transition-all duration-200 whitespace-nowrap border-b-2 ${
                                currentActiveTab === tab.id
                                  ? 'border-slate-900 text-slate-900'
                                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                              }`}
                            >
                              <Icon className="h-4 w-4" />
                              <span>{tab.label}</span>
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {/* Tab Content */}
                    <div className="p-8">
                      {/* Visual Design */}
                      {currentActiveTab === "visual" && selectedResult.visual && (
                        <motion.section
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3 }}
                          className="space-y-4"
                        >
                          <div className="flex items-center gap-3 mb-4">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center shadow-lg">
                              <Eye className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <h2 className="text-lg font-bold text-slate-900">Visual Design</h2>
                              <p className="text-xs text-slate-500">Aesthetic & brand consistency analysis</p>
                            </div>
                          </div>

                          {selectedResult.visual.strengths && Array.isArray(selectedResult.visual.strengths) && selectedResult.visual.strengths.length > 0 && (
                            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <CheckCircle2 className="h-4 w-4 text-green-600" />
                                <h3 className="font-semibold text-sm text-green-900">Strengths</h3>
                              </div>
                              <ul className="space-y-2 text-sm text-green-800">
                                {selectedResult.visual.strengths.map((i: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-green-600 mt-0.5">•</span>
                                    <span>{i}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {selectedResult.visual?.issues && selectedResult.visual.issues.length > 0 && (
                            <div>
                              <h3 className="font-semibold text-sm text-slate-700 mb-3">Issues by Priority</h3>
                              <IssueList list={selectedResult.visual.issues} />
                            </div>
                          )}

                          {selectedResult.visual.recommendations && Array.isArray(selectedResult.visual.recommendations) && selectedResult.visual.recommendations.length > 0 && (
                            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <TrendingUp className="h-4 w-4 text-blue-600" />
                                <h3 className="font-semibold text-sm text-blue-900">Recommendations</h3>
                              </div>
                              <ul className="space-y-2 text-sm text-blue-800">
                                {selectedResult.visual.recommendations.map((i: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-blue-600 mt-0.5">•</span>
                                    <span>{i}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </motion.section>
                      )}

                      {/* UX Heuristics */}
                      {currentActiveTab === "ux" && selectedResult.ux && (
                        <motion.section
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3 }}
                          className="space-y-4"
                        >
                          <div className="flex items-center gap-3 mb-4">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center shadow-lg">
                              <MousePointer className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <h2 className="text-lg font-bold text-slate-900">UX Heuristics</h2>
                              <p className="text-xs text-slate-500">Usability & interaction patterns</p>
                            </div>
                          </div>

                          {selectedResult.ux?.usability_problems && selectedResult.ux.usability_problems.length > 0 && (
                            <div>
                              <h3 className="font-semibold text-sm text-slate-700 mb-3">Usability Findings</h3>
                              <IssueList list={selectedResult.ux.usability_problems} />
                            </div>
                          )}

                          {selectedResult.ux.confusing_elements && Array.isArray(selectedResult.ux.confusing_elements) && selectedResult.ux.confusing_elements.length > 0 && (
                            <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <AlertTriangle className="h-4 w-4 text-orange-600" />
                                <h3 className="font-semibold text-sm text-orange-900">Confusing Elements</h3>
                              </div>
                              <ul className="space-y-2 text-sm text-orange-800">
                                {selectedResult.ux.confusing_elements.map((i: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-orange-600 mt-0.5">•</span>
                                    <span>{i}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </motion.section>
                      )}

                      {/* Accessibility */}
                      {currentActiveTab === "accessibility" && selectedResult.accessibility && (
                        <motion.section
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3 }}
                          className="space-y-4"
                        >
                          <div className="flex items-center gap-3 mb-4">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg">
                              <Accessibility className="h-5 w-5 text-white" />
                            </div>
                            <div className="flex-1">
                              <h2 className="text-lg font-bold text-slate-900">Accessibility</h2>
                              <p className="text-xs text-slate-500">WCAG compliance & inclusive design</p>
                            </div>
                            {selectedResult.accessibility.score !== undefined && (
                              <div className="flex items-center gap-2">
                                <div className={`px-4 py-2 rounded-lg font-bold text-lg ${
                                  selectedResult.accessibility.score >= 80 ? 'bg-green-100 text-green-700' :
                                  selectedResult.accessibility.score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                                  'bg-red-100 text-red-700'
                                }`}>
                                  {selectedResult.accessibility.score}/100
                                </div>
                              </div>
                            )}
                          </div>

                          {selectedResult.accessibility.issues && Array.isArray(selectedResult.accessibility.issues) && selectedResult.accessibility.issues.length > 0 && (
                            <div>
                              <h3 className="font-semibold text-sm text-slate-700 mb-3">WCAG Issues</h3>
                              <IssueList
                                list={selectedResult.accessibility.issues.map((issue: any) => ({
                                  description: issue.description,
                                  recommendation: issue.suggestion,
                                  wcag_rule: issue.wcag_rule,
                                  impact: issue.impact,
                                  effort: issue.effort
                                }))}
                              />
                            </div>
                          )}
                        </motion.section>
                      )}

                      {/* Persona Fit */}
                      {currentActiveTab === "persona" && selectedResult.persona && (
                        <motion.section
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3 }}
                          className="space-y-4"
                        >
                          <div className="flex items-center gap-3 mb-4">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg">
                              <UserCheck className="h-5 w-5 text-white" />
                            </div>
                            <div className="flex-1">
                              <h2 className="text-lg font-bold text-slate-900">Persona Fit</h2>
                              <p className="text-xs text-slate-500">Target audience alignment & clarity</p>
                            </div>
                          </div>

                          {/* Score Cards */}
                          <div className="grid grid-cols-2 gap-4">
                            {selectedResult.persona.trust_score !== undefined && (
                              <div className={`rounded-xl p-4 border ${
                                selectedResult.persona.trust_score >= 70 ? 'bg-green-50 border-green-200' :
                                selectedResult.persona.trust_score >= 50 ? 'bg-yellow-50 border-yellow-200' :
                                'bg-red-50 border-red-200'
                              }`}>
                                <div className="flex items-center gap-2 mb-2">
                                  <CheckCircle2 className={`h-4 w-4 ${
                                    selectedResult.persona.trust_score >= 70 ? 'text-green-600' :
                                    selectedResult.persona.trust_score >= 50 ? 'text-yellow-600' :
                                    'text-red-600'
                                  }`} />
                                  <h3 className="font-semibold text-sm text-slate-900">Trust Score</h3>
                                </div>
                                <p className={`text-3xl font-bold ${
                                  selectedResult.persona.trust_score >= 70 ? 'text-green-700' :
                                  selectedResult.persona.trust_score >= 50 ? 'text-yellow-700' :
                                  'text-red-700'
                                }`}>{selectedResult.persona.trust_score}/100</p>
                              </div>
                            )}

                            {selectedResult.persona.clarity_score !== undefined && (
                              <div className={`rounded-xl p-4 border ${
                                selectedResult.persona.clarity_score >= 70 ? 'bg-green-50 border-green-200' :
                                selectedResult.persona.clarity_score >= 50 ? 'bg-yellow-50 border-yellow-200' :
                                'bg-red-50 border-red-200'
                              }`}>
                                <div className="flex items-center gap-2 mb-2">
                                  <Eye className={`h-4 w-4 ${
                                    selectedResult.persona.clarity_score >= 70 ? 'text-green-600' :
                                    selectedResult.persona.clarity_score >= 50 ? 'text-yellow-600' :
                                    'text-red-600'
                                  }`} />
                                  <h3 className="font-semibold text-sm text-slate-900">Clarity Score</h3>
                                </div>
                                <p className={`text-3xl font-bold ${
                                  selectedResult.persona.clarity_score >= 70 ? 'text-green-700' :
                                  selectedResult.persona.clarity_score >= 50 ? 'text-yellow-700' :
                                  'text-red-700'
                                }`}>{selectedResult.persona.clarity_score}/100</p>
                              </div>
                            )}
                          </div>

                          {selectedResult.persona.confusion_points && Array.isArray(selectedResult.persona.confusion_points) && selectedResult.persona.confusion_points.length > 0 && (
                            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <AlertTriangle className="h-4 w-4 text-red-600" />
                                <h3 className="font-semibold text-sm text-red-900">Confusion Points</h3>
                              </div>
                              <ul className="space-y-2 text-sm text-red-800">
                                {selectedResult.persona.confusion_points.map((point: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-red-600 mt-0.5">•</span>
                                    <span>{point}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {selectedResult.persona.recommendations && Array.isArray(selectedResult.persona.recommendations) && selectedResult.persona.recommendations.length > 0 && (
                            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <Lightbulb className="h-4 w-4 text-blue-600" />
                                <h3 className="font-semibold text-sm text-blue-900">Recommendations</h3>
                              </div>
                              <ul className="space-y-2 text-sm text-blue-800">
                                {selectedResult.persona.recommendations.map((rec: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-blue-600 mt-0.5">•</span>
                                    <span>{rec}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </motion.section>
                      )}

                      {/* Market Research */}
                      {currentActiveTab === "research" && selectedResult.research && (
                        <motion.section
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3 }}
                          className="space-y-4"
                        >
                          <div className="flex items-center gap-3 mb-4">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-500 to-sky-600 flex items-center justify-center shadow-lg">
                              <BarChart3 className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <h2 className="text-lg font-bold text-slate-900">Market Research</h2>
                              <p className="text-xs text-slate-500">Competitive positioning & market analysis</p>
                            </div>
                          </div>

                          {selectedResult.research.design_positioning && (
                            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-2">
                                <Target className="h-4 w-4 text-purple-600" />
                                <h3 className="font-semibold text-sm text-purple-900">Design Positioning</h3>
                              </div>
                              <p className="text-sm text-purple-800 font-medium">{selectedResult.research.design_positioning}</p>
                            </div>
                          )}

                          {selectedResult.research.closest_comparisons && Array.isArray(selectedResult.research.closest_comparisons) && selectedResult.research.closest_comparisons.length > 0 && (
                            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <Users className="h-4 w-4 text-blue-600" />
                                <h3 className="font-semibold text-sm text-blue-900">Closest Comparisons</h3>
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {selectedResult.research.closest_comparisons.map((comp: string, idx: number) => (
                                  <Badge key={idx} className="bg-blue-100 text-blue-700 border-blue-300 px-3 py-1">
                                    {comp}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          {selectedResult.research.conversion_risk_points && Array.isArray(selectedResult.research.conversion_risk_points) && selectedResult.research.conversion_risk_points.length > 0 && (
                            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <TrendingDown className="h-4 w-4 text-red-600" />
                                <h3 className="font-semibold text-sm text-red-900">Conversion Risk Points</h3>
                              </div>
                              <ul className="space-y-2 text-sm text-red-800">
                                {selectedResult.research.conversion_risk_points.map((point: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-red-600 mt-0.5">•</span>
                                    <span>{point}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {selectedResult.research.differentiation_opportunities && Array.isArray(selectedResult.research.differentiation_opportunities) && selectedResult.research.differentiation_opportunities.length > 0 && (
                            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <Lightbulb className="h-4 w-4 text-green-600" />
                                <h3 className="font-semibold text-sm text-green-900">Differentiation Opportunities</h3>
                              </div>
                              <ul className="space-y-2 text-sm text-green-800">
                                {selectedResult.research.differentiation_opportunities.map((opp: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-green-600 mt-0.5">•</span>
                                    <span>{opp}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </motion.section>
                      )}

                      {/* Competitive Analysis */}
                      {currentActiveTab === "market" && selectedResult.market && (
                        <motion.section
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3 }}
                          className="space-y-4"
                        >
                          <div className="flex items-center gap-3 mb-4">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg">
                              <Target className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <h2 className="text-lg font-bold text-slate-900">Competitive Analysis</h2>
                              <p className="text-xs text-slate-500">Competitive positioning & differentiation</p>
                            </div>
                          </div>

                          {selectedResult.market.design_positioning && (
                            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-2">
                                <Target className="h-4 w-4 text-purple-600" />
                                <h3 className="font-semibold text-sm text-purple-900">Design Positioning</h3>
                              </div>
                              <p className="text-sm text-purple-800 font-medium">{selectedResult.market.design_positioning}</p>
                            </div>
                          )}

                          {selectedResult.market.closest_comparisons && Array.isArray(selectedResult.market.closest_comparisons) && selectedResult.market.closest_comparisons.length > 0 && (
                            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <Users className="h-4 w-4 text-blue-600" />
                                <h3 className="font-semibold text-sm text-blue-900">Closest Comparisons</h3>
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {selectedResult.market.closest_comparisons.map((comp: string, idx: number) => (
                                  <Badge key={idx} className="bg-blue-100 text-blue-700 border-blue-300 px-3 py-1">
                                    {comp}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          {selectedResult.market.conversion_risk_points && Array.isArray(selectedResult.market.conversion_risk_points) && selectedResult.market.conversion_risk_points.length > 0 && (
                            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <TrendingDown className="h-4 w-4 text-red-600" />
                                <h3 className="font-semibold text-sm text-red-900">Conversion Risk Points</h3>
                              </div>
                              <ul className="space-y-2 text-sm text-red-800">
                                {selectedResult.market.conversion_risk_points.map((point: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-red-600 mt-0.5">•</span>
                                    <span>{point}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {selectedResult.market.differentiation_opportunities && Array.isArray(selectedResult.market.differentiation_opportunities) && selectedResult.market.differentiation_opportunities.length > 0 && (
                            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <Lightbulb className="h-4 w-4 text-green-600" />
                                <h3 className="font-semibold text-sm text-green-900">Differentiation Opportunities</h3>
                              </div>
                              <ul className="space-y-2 text-sm text-green-800">
                                {selectedResult.market.differentiation_opportunities.map((opp: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2">
                                    <span className="text-green-600 mt-0.5">•</span>
                                    <span>{opp}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </motion.section>
                      )}
                    </div>

                    {/* Metadata - Below tabs */}
                    <div className="px-8 pb-8 pt-0">
                      <div className="pt-6 border-t border-slate-200">
                        <div className="text-xs text-slate-500 space-y-1">
                          {selectedResult.visual?._meta && (
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">Visual</Badge>
                              <span>{selectedResult.visual._meta.model} • {selectedResult.visual._meta.tokens.toLocaleString()} tokens • ${selectedResult.visual._meta.cost_usd.toFixed(4)}</span>
                            </div>
                          )}
                          {selectedResult.ux?._meta && (
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">UX</Badge>
                              <span>{selectedResult.ux._meta.model} • {selectedResult.ux._meta.tokens.toLocaleString()} tokens • ${selectedResult.ux._meta.cost_usd.toFixed(4)}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>
        </div>

        {/* Right Sidebar - Active Image */}
        <div className="hidden lg:block w-96 sticky top-20 h-[calc(100vh-5rem)] border-l border-slate-200 bg-gradient-to-br from-slate-50 to-slate-100">
          <div className="h-full flex items-center justify-center p-8">
            <div className="w-full">
              {selectedPath && (
                <img
                  src={`http://localhost:8000/files/${selectedPath.replace(/\\/g, "/").replace("storage/", "")}`}
                  alt="Active Screen"
                  className="w-full rounded-2xl shadow-2xl border-4 border-white"
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function IssueList({ list }: { list: any[] }) {
  const sorted = sortByPriority(list);

  return (
    <div className="space-y-3">
      {sorted.map((item, idx) => {
        const priority = classifyPriority(item.impact, item.effort);
        const style = priorityStyles[priority];

        return (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="group rounded-xl border-l-4 bg-white shadow-md hover:shadow-xl transition-all duration-300 p-4"
            style={{
              borderLeftColor: priority === "Do Now" ? "#dc2626" :
                                priority === "Quick Win" ? "#16a34a" :
                                priority === "Plan" ? "#2563eb" : "#9ca3af"
            }}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-900 leading-relaxed">
                  {item.description}
                </p>

                {item.wcag_rule && (
                  <div className="mt-2">
                    <Badge variant="outline" className="text-[10px] bg-emerald-50 text-emerald-700 border-emerald-300">
                      {item.wcag_rule}
                    </Badge>
                  </div>
                )}

                {item.recommendation && (
                  <div className="mt-3 pl-3 border-l-2 border-slate-200">
                    <p className="text-xs text-slate-600 leading-relaxed">
                      <span className="font-semibold text-slate-700">→ </span>
                      {item.recommendation}
                    </p>
                  </div>
                )}

                {item.improvement && (
                  <div className="mt-3 pl-3 border-l-2 border-blue-200">
                    <p className="text-xs text-blue-700 leading-relaxed">
                      <span className="font-semibold">💡 </span>
                      {item.improvement}
                    </p>
                  </div>
                )}

                <div className="flex items-center gap-3 mt-3">
                  <Badge variant="outline" className="text-[10px] px-2 py-0.5">
                    Impact: {item.impact}
                  </Badge>
                  <Badge variant="outline" className="text-[10px] px-2 py-0.5">
                    Effort: {item.effort}
                  </Badge>
                </div>
              </div>

              <span
                className={`shrink-0 text-[10px] px-3 py-1.5 rounded-lg border font-bold uppercase tracking-wide shadow-sm ${style}`}
              >
                {priority}
              </span>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

