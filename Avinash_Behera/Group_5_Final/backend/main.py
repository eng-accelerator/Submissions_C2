from fastapi import FastAPI, UploadFile, BackgroundTasks, Form, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from typing import List, Optional
import json
import os
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv
from agents.orchestrator import run_langgraph_pipeline
from supabase import create_client
import os
import uuid
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
import requests


from export_pdf import router as export_router





# Load environment variables
load_dotenv()

# Load supabase
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")

app = FastAPI()

# add router for pdf requests
app.include_router(export_router, prefix="/api")

# Custom validation error handler to debug 422 errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"[VALIDATION ERROR] Path: {request.url.path}")
    print(f"[VALIDATION ERROR] Errors: {exc.errors()}")
    print(f"[VALIDATION ERROR] Body: {exc.body}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(exc.body) if exc.body else None
        }
    )

# Serve images in storage/ as /files/<filename>
app.mount("/files", StaticFiles(directory="storage"), name="files")

def parse_figma_file_key(url: str) -> str:
    return url.split("/file/")[1].split("/")[0]



# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORAGE_PATH = Path("storage")
STORAGE_PATH.mkdir(exist_ok=True)

JOBS = {}  # simple in-memory queue (for now)

# Pydantic models for request validation
class ImportFigmaRequest(BaseModel):
    figmaUrl: str
    figmaToken: str
    projectName: Optional[str] = None
    project_id: Optional[str] = None
    designType: Optional[str] = None
    depth: Optional[str] = None
    persona: Optional[str] = None
    goals: Optional[str] = None
    agents: Dict[str, bool]
    batchMode: str

def save_images(files):
    saved_files = []

    for f in files:
        ext = f.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"  # unique filename
        filepath = STORAGE_PATH / filename

        with open(filepath, "wb") as out:
            out.write(f.file.read())  # save file

        saved_files.append(str(filepath))

    return saved_files


def get_real_screens(figma_file):
    screens = []

    def walk(node, parent_type=None):
        # A REAL SCREEN = FRAME directly under a PAGE
        if node.get("type") == "FRAME" and parent_type == "CANVAS":
            width = node.get("absoluteBoundingBox", {}).get("width", 0)
            height = node.get("absoluteBoundingBox", {}).get("height", 0)

            # Skip tiny frames (icons, elements, cards)
            if width < 200 or height < 200:
                return

            screens.append(node["id"])

        for child in node.get("children", []):
            walk(child, node.get("type"))

    walk(figma_file["document"])
    return screens

@app.post("/api/import-figma")
async def import_figma(
    background_tasks: BackgroundTasks,
    request: ImportFigmaRequest
):
    try:
        file_key = parse_figma_file_key(request.figmaUrl)
        figma_token = request.figmaToken or FIGMA_TOKEN
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid Figma URL: {str(e)}")

    # print("[FIGMA] file_key:", file_key)

    # Step 1: Get document tree
    file_data = requests.get(
        f"https://api.figma.com/v1/files/{file_key}",
        headers={"X-Figma-Token":figma_token}
    ).json()

    frames = []
    frames = get_real_screens(file_data)
    print(f"[FIGMA] Detected {len(frames)} real screens:", frames)

    # Step 2: Get thumbnails
    images = requests.get(
        f"https://api.figma.com/v1/images/{file_key}",
        params={"ids": ",".join(frames), "format": "png"},
        headers={"X-Figma-Token": figma_token}
    ).json()["images"]

    saved_files = []
    for node_id, img_url in images.items():
        img_data = requests.get(img_url).content
        filename = f"{uuid.uuid4()}.png"
        filepath = STORAGE_PATH / filename
        with open(filepath, "wb") as f:
            f.write(img_data)
        saved_files.append(str(filepath))

    # ✅ Append to existing project
    if request.project_id:
        background_tasks.add_task(
            start_analysis_job_append,
            request.project_id,
            saved_files,
            request.agents,
            request.batchMode
        )
        return {
            "status": "queued",
            "project_id": request.project_id,
            "mode": "append",
            "batchMode": request.batchMode
        }

    # ✅ New project
    new_project_id = str(uuid.uuid4())
    project_data = {
        "projectName": request.projectName,
        "designType": request.designType,
        "persona": request.persona,
        "goals": request.goals,
    }

    JOBS[new_project_id] = {"status": "queued", "result": None}

    background_tasks.add_task(
        start_analysis_job,
        new_project_id,
        saved_files,
        request.agents,
        project_data,
        request.batchMode
    )

    return {
        "status": "queued",
        "projectName": request.projectName,
        "mode": "new",
        "project_id": new_project_id,
        "batchMode": request.batchMode
    }

@app.post("/api/analyze")
async def analyze_designs(
    background_tasks: BackgroundTasks,
    files: Optional[List[UploadFile]] = File(None),
    figmaUrl: Optional[str] = Form(None),
    figmaToken: Optional[str] = Form(None),
    projectName: str = Form(None),
    project_id: str = Form(None),
    designType: str = Form(None),
    depth: str = Form(None),
    persona: str = Form(None),
    goals: str = Form(None),
    agents: str = Form(...),
    batchMode: str = Form(...)
):
    
    agents = json.loads(agents)

    # Validate input: must have either files OR figmaUrl
    if not files and not figmaUrl:
        raise HTTPException(status_code=400, detail="Must provide either files or figmaUrl")
    
    if figmaUrl and not figmaToken:
        raise HTTPException(status_code=400, detail="figmaToken required when using figmaUrl")

    # Save uploaded images or prepare for Figma fetch
    saved_files = []
    if files:
        saved_files = save_images(files)

    # ✅ Append to existing project
    if project_id:
        print("start_analysis_job_append")
        background_tasks.add_task(
            start_analysis_job_append,
            project_id,
            saved_files,
            agents, batchMode,
            figmaUrl, figmaToken
        )
        return {
            "status": "queued",
            "project_id": project_id,
            "mode": "append",
            "batchMode": batchMode
        }

    # ✅ Create new project

    print("start_analysis_job_append create new ")
    project_id = str(uuid.uuid4())  # Used as both project ID and job ID

    project_data = {
        "projectName": projectName,
        "designType": designType,
        "persona": persona,
        "goals": goals,
    }

    JOBS[project_id] = {"status": "queued", "result": None}

    background_tasks.add_task(
        start_analysis_job,
        project_id,
        saved_files,
        agents,
        project_data,
        batchMode,
        figmaUrl, figmaToken
    )

    return {
        "status": "queued",
        "projectName": projectName,
        "mode": "new",
        "project_id": project_id,
        "batchMode": batchMode
    }

@app.get("/api/job/{job_id}")
def get_job_status(job_id: str):
    if job_id not in JOBS:
        return {"error": "unknown job"}
    return JOBS[job_id]


@app.get("/api/projects")
def get_all_projects():
    projects = supabase.table("projects").select("*").execute().data
    return {"projects": projects}


@app.get("/api/project/{project_id}")
def get_project(project_id: str):
    project = supabase.table("projects").select("*").eq("id", project_id).single().execute().data
    screens = supabase.table("screens").select("*").eq("project_id", project_id).execute().data
    analysis = supabase.table("analysis_results").select("*").eq("project_id", project_id).execute().data

    return {
        "project": project,
        "screens": screens,
        "analysis": analysis
    }

@app.delete("/api/project/{project_id}")
def delete_project(project_id: str):
    # Check exists
    project = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete (cascade removes screens + analysis automatically)
    supabase.table("projects").delete().eq("id", project_id).execute()

    return {"status": "deleted", "project_id": project_id}


def start_analysis_job(project_id, file_paths, agents, project_data, batchMode,
                       figma_url=None, figma_token=None):
    try:
        source = "Figma" if figma_url else f"{len(file_paths)} uploaded files"
        print(f"[DEBUG] inside start_analysis_job, project_id={project_id}, source={source}, batch_mode={batchMode}")

        # Create project with initial status 'queued'
        print(f"[DEBUG] Creating project in Supabase with status 'queued'")
        project_insert = supabase.table("projects").insert([{
            "id": project_id,
            "name": project_data["projectName"],
            "design_type": project_data["designType"],
            "persona": project_data["persona"],
            "goals": project_data["goals"],
            "status": "queued"
        }]).execute()
        print(f"[DEBUG] Project created: {project_insert}")

        # Update status to 'processing'
        print(f"[DEBUG] Updating project status to 'processing'")
        supabase.table("projects").update({"status": "processing"}).eq("id", project_id).execute()
        JOBS[project_id]["status"] = "processing"

        # Convert batchMode string to boolean
        batch_mode_bool = (batchMode == "yes")

        # Use LangGraph pipeline (with optional Figma support)
        result = run_langgraph_pipeline(
            file_paths, agents, batch_mode_bool,
            figma_url=figma_url, figma_token=figma_token,
            persona=project_data.get("persona"),
            goals=project_data.get("goals")
        )

        print(f"[DEBUG] Pipeline completed")

        # Store screens
        print(f"[DEBUG] Storing {len(file_paths)} screens")
        for p in file_paths:
            screen_insert = supabase.table("screens").insert([{
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "file_path": p,
                "original_name": os.path.basename(p)
            }]).execute()
            print(f"[DEBUG] Screen stored: {p}")

        # Store analysis json
        print(f"[DEBUG] Storing analysis results")
        analysis_insert = supabase.table("analysis_results").insert([{
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "result_json": result
        }]).execute()
        print(f"[DEBUG] Analysis results stored")

        # Update status to 'complete'
        print(f"[DEBUG] Updating project status to 'complete'")
        supabase.table("projects").update({"status": "complete"}).eq("id", project_id).execute()
        JOBS[project_id]["result"] = result
        JOBS[project_id]["status"] = "complete"
        print(f"[DEBUG] Job complete: {project_id}")

    except Exception as e:
        print(f"[ERROR] start_analysis_job failed: {str(e)}")
        import traceback
        traceback.print_exc()

        # Update status to 'failed'
        print(f"[DEBUG] Updating project status to 'failed'")
        supabase.table("projects").update({"status": "failed"}).eq("id", project_id).execute()
        JOBS[project_id]["status"] = "failed"
        JOBS[project_id]["error"] = str(e)

def start_analysis_job_append(project_id, file_paths, agents, batchMode,
                              figma_url=None, figma_token=None):
    try:
        # Fetch project to get persona and goals
        project = supabase.table("projects").select("persona, goals").eq("id", project_id).single().execute()
        persona = project.data.get("persona") if project.data else None
        goals = project.data.get("goals") if project.data else None

        # Update status to 'processing'
        print(f"[DEBUG] Updating project {project_id} status to 'processing'")
        supabase.table("projects").update({"status": "processing"}).eq("id", project_id).execute()

        # Convert batchMode string to boolean
        batch_mode_bool = (batchMode == "yes")

        # Use LangGraph pipeline (with optional Figma support)
        result = run_langgraph_pipeline(
            file_paths, agents, batch_mode_bool,
            figma_url=figma_url, figma_token=figma_token,
            persona=persona,
            goals=goals
        )

        # Save new screens
        for p in file_paths:
            supabase.table("screens").insert({
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "file_path": p,
                "original_name": os.path.basename(p)
            }).execute()

        # Save new analysis results version
        supabase.table("analysis_results").insert({
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "result_json": result
        }).execute()

        # Update status to 'complete'
        print(f"[DEBUG] Updating project {project_id} status to 'complete'")
        supabase.table("projects").update({"status": "complete"}).eq("id", project_id).execute()

    except Exception as e:
        print(f"[ERROR] start_analysis_job_append failed: {str(e)}")
        import traceback
        traceback.print_exc()

        # Update status to 'failed'
        print(f"[DEBUG] Updating project {project_id} status to 'failed'")
        supabase.table("projects").update({"status": "failed"}).eq("id", project_id).execute()



