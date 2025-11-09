import { useEffect, useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Plus, Clock, CheckCircle, XCircle, ArrowLeft, Trash2, FolderOpen, Bell } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Project {
  id: string;
  name: string;
  status?: "queued" | "pending" | "processing" | "complete" | "failed";
  created_at: string;
  design_type?: string;
  depth?: string;
  goals?: string;
  persona?: string;
}

export default function ProjectsDashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState<Array<{id: string, message: string}>>([]);
  const navigate = useNavigate();
  const location = useLocation();
  const previousStatusRef = useRef<Map<string, string>>(new Map());

  // Extract navigation state
  const navigationState = location.state as {
    newProjectId?: string;
    projectName?: string;
    status?: string;
  } | null;

  const newProjectId = navigationState?.newProjectId;

  const loadProjects = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/projects");
      const data = await res.json();
      setProjects(data.projects || []);
    } catch (err) {
      console.error("Failed to load projects:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  // Merge virtual project with real projects
  const displayProjects = (() => {
    // If we have navigation state for a new project and it's not in the API response yet
    if (navigationState?.newProjectId && navigationState?.projectName) {
      const existsInApi = projects.some((p) => p.id === navigationState.newProjectId);

      if (!existsInApi) {
        // Create a virtual project to show in the UI
        const virtualProject: Project = {
          id: navigationState.newProjectId,
          name: navigationState.projectName,
          status: (navigationState.status as Project["status"]) || "queued",
          created_at: new Date().toISOString(),
        };

        // Add virtual project to the beginning of the list
        return [virtualProject, ...projects];
      }
    }

    return projects;
  })();

  // Auto-refresh for projects with queued or processing status
  useEffect(() => {
    // Check both real projects and virtual project from navigation state
    const hasActiveProjects = displayProjects.some(
      (p) => p.status === "queued" || p.status === "processing"
    );

    if (!hasActiveProjects) return;

    const interval = setInterval(() => {
      loadProjects();
    }, 3000); // Refresh every 3 seconds

    return () => clearInterval(interval);
  }, [displayProjects]);

  // Detect status changes and show notifications
  useEffect(() => {
    projects.forEach((project) => {
      const previousStatus = previousStatusRef.current.get(project.id);

      // If project was processing/queued and is now complete
      if (
        previousStatus &&
        (previousStatus === "queued" || previousStatus === "processing") &&
        project.status === "complete"
      ) {
        // Add notification
        const notificationId = `${project.id}-${Date.now()}`;
        setNotifications((prev) => [
          ...prev,
          {
            id: notificationId,
            message: `Report available for "${project.name}"`,
          },
        ]);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
          setNotifications((prev) => prev.filter((n) => n.id !== notificationId));
        }, 5000);
      }

      // Update previous status
      if (project.status) {
        previousStatusRef.current.set(project.id, project.status);
      }
    });
  }, [projects]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "complete":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "processing":
        return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />;
      case "queued":
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      complete: "bg-green-100 text-green-700 border-green-200",
      processing: "bg-blue-100 text-blue-700 border-blue-200 animate-pulse",
      failed: "bg-red-100 text-red-700 border-red-200",
      queued: "bg-yellow-100 text-yellow-700 border-yellow-200",
      pending: "bg-slate-100 text-slate-700 border-slate-200",
    };

    const labels: Record<string, string> = {
      complete: "Report Available",
      processing: "Under Progress",
      queued: "Under Progress",
      failed: "Failed",
      pending: "Pending",
    };

    return (
      <Badge
        variant="outline"
        className={`capitalize font-semibold ${styles[status] || styles.pending}`}
      >
        {labels[status] || status}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-white to-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-xl border-b border-slate-200 shadow-sm">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
                Projects Dashboard
              </h1>
              <p className="text-sm text-slate-500 mt-0.5">
                View and manage your design analysis projects
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" size="sm" onClick={() => navigate("/")} className="shadow-sm">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
              <Button size="sm" onClick={() => navigate("/")} className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg shadow-blue-500/30">
                <Plus className="mr-2 h-4 w-4" />
                New Analysis
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-6 py-8 space-y-6">

      {/* Notifications */}
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mb-4"
          >
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3 shadow-lg">
              <Bell className="h-5 w-5 text-green-600" />
              <p className="text-green-800 font-medium flex-1">{notification.message}</p>
              <Button
                size="sm"
                variant="ghost"
                onClick={() =>
                  setNotifications((prev) => prev.filter((n) => n.id !== notification.id))
                }
                className="text-green-600 hover:text-green-800"
              >
                Dismiss
              </Button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* New project banner */}
      {(() => {
        if (!newProjectId) return null;

        // Find the project in displayProjects
        const project = displayProjects.find((p) => p.id === newProjectId);

        // Don't show banner if project is complete or failed
        if (project && (project.status === "complete" || project.status === "failed")) {
          return null;
        }

        return (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4"
          >
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center gap-3 shadow-lg">
              <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
              <p className="text-blue-800 font-medium">
                Analysis started! Your project "{navigationState?.projectName}" is now under progress.
              </p>
            </div>
          </motion.div>
        );
      })()}

      {displayProjects.length === 0 ? (
        <Card className="border-0 shadow-xl bg-white">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center mb-4">
              <FolderOpen className="h-8 w-8 text-blue-600" />
            </div>
            <p className="text-slate-600 mb-4 text-lg font-semibold">No projects yet</p>
            <p className="text-slate-500 text-sm mb-6 text-center max-w-sm">
              Start by creating your first design analysis to get actionable insights
            </p>
            <Button onClick={() => navigate("/")} className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg shadow-blue-500/30">
              <Plus className="mr-2 h-4 w-4" />
              Create Your First Analysis
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {displayProjects.map((project, idx) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <Card
                className={`group relative border-0 shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer bg-white overflow-hidden ${
                  project.id === newProjectId ? "ring-2 ring-blue-500 ring-offset-2" : ""
                }`}
                onClick={() => {
                  navigate(`/project/${project.id}`);
                }}
              >
                <div className={`absolute inset-0 bg-gradient-to-br transition-opacity duration-300 pointer-events-none ${
                  project.id === newProjectId
                    ? "from-blue-50 to-purple-50 opacity-100"
                    : "from-blue-50/50 to-purple-50/50 opacity-0 group-hover:opacity-100"
                }`} />

                <button
                  onClick={async (e) => {
                    e.preventDefault();
                    e.stopPropagation();

                    if (!window.confirm(`Are you sure you want to delete "${project.name}"? This action cannot be undone.`)) return;

                    try {
                      const response = await fetch(`http://localhost:8000/api/project/${project.id}`, {
                        method: "DELETE"
                      });

                      if (!response.ok) {
                        throw new Error(`Failed to delete project: ${response.statusText}`);
                      }

                      // Remove from UI (reload to get fresh data)
                      await loadProjects();
                    } catch (error) {
                      console.error("Error deleting project:", error);
                      alert(`Failed to delete project: ${error instanceof Error ? error.message : 'Unknown error'}`);
                    }
                  }}
                  className="absolute top-3 right-3 z-50 opacity-0 group-hover:opacity-100 transition-all duration-200 bg-red-500 hover:bg-red-600 text-white p-2 rounded-lg shadow-lg hover:scale-110 pointer-events-auto"
                  title="Delete project"
                  type="button"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
                <CardHeader className="relative z-10">
                  <div className="flex items-start justify-between mb-3">
                    <CardTitle className="text-lg font-bold text-slate-900 truncate flex-1 pr-8">
                      {project.name || "Untitled Project"}
                    </CardTitle>
                    {project.status && (
                      <div className="shrink-0">
                        {getStatusIcon(project.status)}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    {project.status && getStatusBadge(project.status)}
                    {project.design_type && (
                      <Badge variant="outline" className="capitalize bg-blue-50 text-blue-700 border-blue-200">
                        {project.design_type}
                      </Badge>
                    )}
                    {project.depth && (
                      <Badge variant="outline" className="capitalize bg-purple-50 text-purple-700 border-purple-200">
                        {project.depth}
                      </Badge>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="relative z-10">
                  <div className="space-y-3 text-sm">
                    {project.persona && (
                      <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                        <span className="text-slate-500 text-xs font-semibold uppercase tracking-wider">Persona</span>
                        <p className="text-sm text-slate-700 mt-1">{project.persona}</p>
                      </div>
                    )}
                    {project.goals && (
                      <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                        <span className="text-slate-500 text-xs font-semibold uppercase tracking-wider">Goals</span>
                        <p className="text-sm text-slate-700 mt-1">{project.goals}</p>
                      </div>
                    )}
                    <div className="flex justify-between items-center pt-3 border-t border-slate-200">
                      <span className="text-slate-500 text-xs font-semibold">ID</span>
                      <code className="text-xs bg-slate-100 px-2 py-1 rounded font-mono text-slate-700">
                        {project.id.slice(0, 8)}...
                      </code>
                    </div>
                    {project.created_at && (
                      <div className="flex justify-between items-center">
                        <span className="text-slate-500 text-xs font-semibold">Created</span>
                        <span className="text-xs text-slate-700">
                          {new Date(project.created_at).toLocaleDateString(undefined, {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                          })}
                        </span>
                      </div>
                    )}
                  </div>
                  <Button
                    variant="secondary"
                    size="sm"
                    className={`w-full mt-4 font-semibold shadow-sm ${
                      project.status === "complete"
                        ? "bg-gradient-to-r from-green-100 to-green-200 hover:from-green-200 hover:to-green-300 text-green-900"
                        : project.status === "queued" || project.status === "processing"
                        ? "bg-gradient-to-r from-blue-100 to-blue-200 hover:from-blue-200 hover:to-blue-300 text-blue-900"
                        : "bg-gradient-to-r from-slate-100 to-slate-200 hover:from-slate-200 hover:to-slate-300 text-slate-900"
                    }`}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/project/${project.id}`);
                    }}
                  >
                    {project.status === "complete"
                      ? "View Report"
                      : project.status === "queued" || project.status === "processing"
                      ? "View Progress"
                      : "View Details"}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
      </div>
    </div>
  );
}
