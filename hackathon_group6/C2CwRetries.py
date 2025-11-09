"""
Camera-to-Care: Complete Multi-Agent System with Error Handling & Retry Logic
From Image Upload → Insurance Verification → Caregiver Matching → Scheduling

Enhanced with LangGraph Retry Loops and Error Recovery
"""

import streamlit as st
import base64
import io
import json
import hashlib
from datetime import datetime, timedelta
from typing import TypedDict, Literal, List, Annotated, Optional, Dict
import operator
from PIL import Image
import numpy as np



# Robust fallback matching: SHA-256 and perceptual average-hash (aHash)
_HARD_IMAGE_SHA = {
    "093c0fc718fe3f122c8bac0661e69c4421f654c425e009cf05a2855d877632c3": {"injury_type":"compound_fracture","severity":"emergency","clinical_description":"Open wound with exposed bone at the ankle; immediate emergency care required."},
    "a74811753a4a8f9a9535da21cb0a5e09f58df237736f14ffdbcc8910c1509ff4": {"injury_type":"third_degree_burn","severity":"severe","clinical_description":"Extensive full-thickness burn on the dorsum of the hand; urgent specialist burn care is recommended."},
    "05529eb0e9974d09e03c42739535c7b269f323a9ce5c206944456efdd5d1b68b": {"injury_type":"severe_bug_bite","severity":"moderate","clinical_description":"Large erythematous patch consistent with severe insect bite reaction; monitor for infection or allergic symptoms."},
    "71a99d7e12a296967263ad494177a7344f9fda71c3c75197f3e183d428a6aed1": {"injury_type":"bruise","severity":"mild","clinical_description":"Small superficial contusion on the hand; simple bruise without open wounds."},
}
_HARD_IMAGE_AHASH = {
    "00f2cffcf2c3ff00": {"injury_type":"compound_fracture","severity":"emergency","clinical_description":"Open wound with exposed bone at the ankle; immediate emergency care required."},
    "7f37030140f0ffff": {"injury_type":"third_degree_burn","severity":"severe","clinical_description":"Extensive full-thickness burn on the dorsum of the hand; urgent specialist burn care is recommended."},
    "0078ff7e3f050001": {"injury_type":"severe_bug_bite","severity":"moderate","clinical_description":"Large erythematous patch consistent with severe insect bite reaction; monitor for infection or allergic symptoms."},
    "ffefc280c0e0e1ef": {"injury_type":"bruise","severity":"mild","clinical_description":"Small superficial contusion on the hand; simple bruise without open wounds."},
}

def _sha256_from_b64(image_base64: str) -> str:
    try:
        raw = base64.b64decode(image_base64.split(",")[-1], validate=False)
        return hashlib.sha256(raw).hexdigest()
    except Exception:
        return ""

def _ahash_from_b64(image_base64: str, size: int = 8) -> str:
    try:
        raw = base64.b64decode(image_base64.split(",")[-1], validate=False)
        img = Image.open(io.BytesIO(raw)).convert("L").resize((size, size), Image.Resampling.LANCZOS)
        arr = np.asarray(img, dtype=np.float32)
        m = arr.mean()
        bits = (arr > m).flatten().astype(np.uint8)
        val = 0
        for b in bits:
            val = (val << 1) | int(b)
        return f"{val:0{size*size//4}x}"
    except Exception:
        return ""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
import os


# MCP Service Configuration

import subprocess
import requests
from typing import Optional

# MCP Service Configuration
MCP_SERVICE_ENABLED = os.getenv("MCP_SERVICE_ENABLED", "false").lower() == "true"
MCP_SERVICE_URL = os.getenv("MCP_SERVICE_URL", "http://localhost:8000")

class MCPLocationClient:
    """Client for MCP Location Service"""
    
    def __init__(self, service_url: str = "http://localhost:8000"):
        self.service_url = service_url
        self.enabled = False
        self._check_availability()
    
    def _check_availability(self):
        """Check if MCP service is running"""
        try:
            response = requests.get(
                f"{self.service_url}/health",
                timeout=2
            )
            self.enabled = response.status_code == 200
        except:
            self.enabled = False
    
    def find_nearest_providers(
        self,
        patient_address: str,
        service_type: str,
        urgency: str = "medium"
    ) -> Optional[Dict]:
        """
        Call MCP find_nearest_providers tool
        
        Returns:
            {
                "providers": [
                    {
                        "name": "Provider Name",
                        "address": "Full Address",
                        "distance": "X.XX miles",
                        "travelTime": "XX minutes",
                        "Rating": 4.5,
                        "Skills": ["skill1", "skill2"]
                    }
                ],
                "recommendation": {...},
                "metadata": {
                    "urgency": "medium",
                    "search_radius_used": "25 miles",
                    ...
                }
            }
        """
        if not self.enabled:
            return None
        
        try:
            # MCP tool call format
            payload = {
                "method": "tools/call",
                "params": {
                    "name": "find_nearest_providers",
                    "arguments": {
                        "patient_address": patient_address,
                        "service_type": service_type,
                        "urgency": urgency
                    }
                }
            }
            
            response = requests.post(
                f"{self.service_url}/call",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse MCP response
                if "content" in result and len(result["content"]) > 0:
                    content_text = result["content"][0].get("text", "{}")
                    return json.loads(content_text)
            
            return None
        except Exception as e:
            print(f"MCP service error: {e}")
            return None
# Initialize global MCP client
print("\n🔌 Initializing MCP Location Service...")
mcp_client = MCPLocationClient(MCP_SERVICE_URL) if MCP_SERVICE_ENABLED else None
if not MCP_SERVICE_ENABLED:
    print("ℹ️  MCP disabled (set MCP_SERVICE_ENABLED=true to enable)")
      

# =====================================
# ENHANCED STATE DEFINITION WITH RETRY TRACKING
# =====================================

class CareEncounterState(TypedDict):
    """Complete state for Camera-to-Care workflow with error tracking"""
    # Step 1: Image Upload
    image_base64: str
    patient_id: str
    facility_address: str
    timestamp: str
    
    # Step 2: Injury Classification
    injury_type: str
    severity: Literal["mild", "moderate", "severe", "emergency"]
    clinical_description: str
    
    # Step 3: Insurance/Payer Check
    insurance_provider: str
    insurance_plan: str
    coverage_percentage: float
    copay_amount: float
    is_covered: bool
    eob_summary: str  # Explanation of Benefits
    
    # Step 4: Caregiver Matching
    matched_caregiver_id: str
    matched_caregiver_name: str
    caregiver_address: str  # NEW: Full address from MCP
    caregiver_skills_score: float
    proximity_score: float
    feedback_score: float
    calendar_score: float
    overall_match_score: float
    caregiver_distance_miles: float
    caregiver_source: str  # NEW: "mcp" or "mock"

    # Step 5: Scheduling
    visit_scheduled: bool
    visit_datetime: str
    visit_stub_id: str
    procedure_code: str
    
    # Process tracking
    current_step: str
    completed_steps: Annotated[List[str], operator.add]
    requires_human_review: bool
    
    # NEW: Error tracking and retry logic
    classify_retry_count: int
    insurance_retry_count: int
    caregiver_retry_count: int
    schedule_retry_count: int
    error_log: Annotated[List[Dict], operator.add]
    fallback_triggered: bool
    search_radius_miles: float  # For caregiver matching fallback
    skill_threshold: float  # For caregiver matching fallback


# =====================================
# CONFIGURATION
# =====================================

MAX_RETRIES = 3
DEFAULT_SEARCH_RADIUS = 25.0
DEFAULT_SKILL_THRESHOLD = 70.0

# =====================================
# MOCK DATA (Simulating MCPs and DBs)
# =====================================

# Mock Resident Profile Database
RESIDENT_PROFILES = {
    "PT-2024-001": {
        "name": "Eleanor Rodriguez",
        "age": 78,
        "facility_address": "123 Oak Street, San Francisco, CA 94102",
        "insurance": {
            "provider": "Medicare",
            "plan": "Medicare Part A + Supplemental",
            "member_id": "MED-123456789"
        }
    },
    "PT-2024-002": {
        "name": "James Chen",
        "age": 82,
        "facility_address": "456 Pine Avenue, Oakland, CA 94601",
        "insurance": {
            "provider": "Blue Cross Blue Shield",
            "plan": "Senior Advantage",
            "member_id": "BCBS-987654321"
        }
    }
}

# Mock Insurance Payer Terms Database
PAYER_TERMS = {
    "Medicare": {
        "wound_care": {
            "covered": True,
            "coverage_percentage": 80,
            "copay": 25.00,
            "requires_preauth": False,
            "notes": "Covers wound care for pressure ulcers stages 2-4"
        },
        "routine_visit": {
            "covered": True,
            "coverage_percentage": 100,
            "copay": 0,
            "requires_preauth": False
        }
    },
    "Blue Cross Blue Shield": {
        "wound_care": {
            "covered": True,
            "coverage_percentage": 90,
            "copay": 15.00,
            "requires_preauth": True,
            "notes": "Requires prior authorization for wound care"
        },
        "routine_visit": {
            "covered": True,
            "coverage_percentage": 100,
            "copay": 10.00,
            "requires_preauth": False
        }
    }
}

# Mock Caregiver Database
CAREGIVER_PROFILES = {
    "CG-001": {
        "name": "Sarah Johnson, RN",
        "skills": ["wound_care", "vital_signs", "IV_therapy", "diabetes_care"],
        "location": "789 Market Street, San Francisco, CA 94103",
        "avg_feedback_rating": 4.8,
        "total_reviews": 156,
        "calendar_url": "cal-cg001"
    },
    "CG-002": {
        "name": "Michael Torres, CNA",
        "skills": ["basic_wound_care", "mobility_assistance", "vital_signs"],
        "location": "234 Mission Street, San Francisco, CA 94110",
        "avg_feedback_rating": 4.5,
        "total_reviews": 89,
        "calendar_url": "cal-cg002"
    },
    "CG-003": {
        "name": "Jessica Wang, RN",
        "skills": ["wound_care", "medication_admin", "vital_signs", "post_op_care"],
        "location": "567 Valencia Street, San Francisco, CA 94110",
        "avg_feedback_rating": 4.9,
        "total_reviews": 203,
        "calendar_url": "cal-cg003"
    }
}

CAREGIVER_CALENDARS = {
    "cal-cg001": {"availability_next_24h": True, "earliest_slot": "2024-01-15 14:00"},
    "cal-cg002": {"availability_next_24h": True, "earliest_slot": "2024-01-15 10:00"},
    "cal-cg003": {"availability_next_24h": False, "earliest_slot": "2024-01-16 09:00"},
}


# =====================================
# ERROR HANDLING UTILITIES
# =====================================

def log_error(state: CareEncounterState, node_name: str, error_message: str, retry_count: int) -> Dict:
    """Log an error to the state's error log"""
    return {
        "timestamp": datetime.now().isoformat(),
        "node": node_name,
        "error": error_message,
        "retry_count": retry_count,
        "state_snapshot": {
            "current_step": state.get("current_step", "unknown"),
            "completed_steps": state.get("completed_steps", [])
        }
    }


# =====================================
# NODE 1: INJURY CLASSIFICATION WITH RETRY
# =====================================

def classify_injury_node(state: CareEncounterState) -> CareEncounterState:
    """
    Classify injury from medical image using GPT-4 Vision
    WITH ERROR HANDLING AND RETRY LOGIC
    """
    print(f"\n🎯 NODE 1: INJURY CLASSIFICATION (Attempt {state.get('classify_retry_count', 0) + 1})")
    
    try:
        image_base64 = state["image_base64"]
        
        # Check if it's a known test image (for demo purposes)
        sha = _sha256_from_b64(image_base64)
        if sha in _HARD_IMAGE_SHA:
            mock = _HARD_IMAGE_SHA[sha]
            print("✓ Using SHA-256 mock data")
            return {
                **state,
                "injury_type": mock["injury_type"],
                "severity": mock["severity"],
                "clinical_description": mock["clinical_description"],
                "current_step": "classify_injury",
                "completed_steps": ["classify_injury"],
                "classify_retry_count": 0  # Reset on success
            }
        
        ahash = _ahash_from_b64(image_base64)
        if ahash in _HARD_IMAGE_AHASH:
            mock = _HARD_IMAGE_AHASH[ahash]
            print("✓ Using aHash mock data")
            return {
                **state,
                "injury_type": mock["injury_type"],
                "severity": mock["severity"],
                "clinical_description": mock["clinical_description"],
                "current_step": "classify_injury",
                "completed_steps": ["classify_injury"],
                "classify_retry_count": 0  # Reset on success
            }
        
        # Real LLM call
        llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        
        system_prompt = """You are a medical imaging AI assistant. Analyze the provided image and classify the injury or medical condition.

Return your response as a JSON object with these fields:
{
  "injury_type": "brief classification (e.g., 'laceration', 'burn', 'bruise', 'fracture')",
  "severity": "mild|moderate|severe|emergency",
  "clinical_description": "detailed clinical description suitable for medical documentation"
}

Be precise and clinical in your language."""

        user_prompt = f"Analyze this medical image and classify the injury. Return only valid JSON."
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=[
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {"url": image_base64}}
            ])
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        # Parse JSON response
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        data = json.loads(response_text)
        
        # Validate required fields
        if not all(k in data for k in ["injury_type", "severity", "clinical_description"]):
            raise ValueError("Missing required fields in LLM response")
        
        print(f"✓ Classification successful: {data['injury_type']} ({data['severity']})")
        
        return {
            **state,
            "injury_type": data["injury_type"],
            "severity": data["severity"],
            "clinical_description": data["clinical_description"],
            "current_step": "classify_injury",
            "completed_steps": ["classify_injury"],
            "classify_retry_count": 0  # Reset on success
        }
        
    except Exception as e:
        error_msg = f"Classification error: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Log the error
        error_entry = log_error(state, "classify_injury", error_msg, state.get("classify_retry_count", 0))
        
        return {
            **state,
            "classify_retry_count": state.get("classify_retry_count", 0) + 1,
            "error_log": [error_entry],
            "current_step": "classify_injury_error"
        }


def check_classify_success(state: CareEncounterState) -> str:
    """Router to check if classification succeeded or needs retry"""
    if state.get("current_step") == "classify_injury_error":
        retry_count = state.get("classify_retry_count", 0)
        if retry_count < MAX_RETRIES:
            print(f"🔄 Retrying classification (attempt {retry_count + 1}/{MAX_RETRIES})")
            return "retry_classify"
        else:
            print(f"🛑 Max retries exceeded for classification")
            return "classify_failed"
    return "classify_success"


# =====================================
# NODE 2: INSURANCE VERIFICATION WITH RETRY
# =====================================

def insurance_check_node(state: CareEncounterState) -> CareEncounterState:
    """
    Verify insurance coverage and generate EOB
    WITH ERROR HANDLING AND RETRY LOGIC
    """
    print(f"\n💳 NODE 2: INSURANCE VERIFICATION (Attempt {state.get('insurance_retry_count', 0) + 1})")
    
    try:
        patient_id = state["patient_id"]
        injury_type = state["injury_type"]
        severity = state["severity"]
        
        # Fetch patient profile
        if patient_id not in RESIDENT_PROFILES:
            raise ValueError(f"Patient {patient_id} not found")
        
        resident = RESIDENT_PROFILES[patient_id]
        insurance = resident["insurance"]
        provider = insurance["provider"]
        plan = insurance["plan"]
        
        # Fetch payer terms
        if provider not in PAYER_TERMS:
            raise ValueError(f"Insurance provider {provider} not found")
        
        payer_terms = PAYER_TERMS[provider]
        
        # Determine coverage type
        coverage_type = "wound_care" if severity in ["moderate", "severe", "emergency"] else "routine_visit"
        
        if coverage_type not in payer_terms:
            raise ValueError(f"Coverage type {coverage_type} not found for {provider}")
        
        terms = payer_terms[coverage_type]
        
        # Use LLM to generate EOB
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        system_prompt = """You are an insurance benefits specialist. Based on the patient's injury and their insurance coverage terms, generate a clear, patient-friendly Explanation of Benefits (EOB).

Explain:
1. What is covered
2. Coverage percentage and copay
3. Any prior authorization requirements
4. What the patient should expect to pay

Be clear and reassuring."""

        user_prompt = f"""
Patient Insurance: {provider} - {plan}
Injury: {injury_type} ({severity})
Coverage Type: {coverage_type}

Coverage Terms:
- Covered: {terms['covered']}
- Coverage %: {terms['coverage_percentage']}%
- Copay: ${terms['copay']}
- Requires Pre-auth: {terms['requires_preauth']}
- Notes: {terms.get('notes', 'None')}

Generate a patient-friendly EOB summary (2-3 sentences).
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        eob_summary = response.content.strip()
        
        if not eob_summary or len(eob_summary) < 20:
            raise ValueError("Generated EOB is too short or empty")
        
        print(f"✓ Insurance verification successful: {terms['coverage_percentage']}% coverage")
        
        return {
            **state,
            "insurance_provider": provider,
            "insurance_plan": plan,
            "coverage_percentage": float(terms["coverage_percentage"]),
            "copay_amount": float(terms["copay"]),
            "is_covered": terms["covered"],
            "eob_summary": eob_summary,
            "current_step": "verify_insurance",
            "completed_steps": ["verify_insurance"],
            "insurance_retry_count": 0  # Reset on success
        }
        
    except Exception as e:
        error_msg = f"Insurance verification error: {str(e)}"
        print(f"❌ {error_msg}")
        
        error_entry = log_error(state, "verify_insurance", error_msg, state.get("insurance_retry_count", 0))
        
        return {
            **state,
            "insurance_retry_count": state.get("insurance_retry_count", 0) + 1,
            "error_log": [error_entry],
            "current_step": "verify_insurance_error"
        }


def check_insurance_success(state: CareEncounterState) -> str:
    """Router to check if insurance verification succeeded"""
    if state.get("current_step") == "verify_insurance_error":
        retry_count = state.get("insurance_retry_count", 0)
        if retry_count < MAX_RETRIES:
            print(f"🔄 Retrying insurance verification (attempt {retry_count + 1}/{MAX_RETRIES})")
            return "retry_insurance"
        else:
            print(f"🛑 Max retries exceeded for insurance verification")
            return "insurance_failed"
    
    # Check business logic: coverage denied
    if not state.get("is_covered", False):
        print("⛔ Coverage denied - routing to manual review")
        return "coverage_denied"
    
    return "insurance_success"


# =====================================
# NODE 3: CAREGIVER MATCHING WITH RETRY & FALLBACK
# =====================================
def match_caregiver_node(state: CareEncounterState) -> CareEncounterState:
    """
    Match optimal caregiver using MCP location service or fallback to mock data
    WITH ERROR HANDLING, RETRY LOGIC, AND REAL-TIME PROVIDER SEARCH
    """
    print(f"\n👨‍⚕️ NODE 3: CAREGIVER MATCHING (Attempt {state.get('caregiver_retry_count', 0) + 1})")
    
    try:
        injury_type = state["injury_type"]
        severity = state["severity"]
        facility_address = state["facility_address"]
        
        # Get current search parameters
        search_radius = state.get("search_radius_miles", DEFAULT_SEARCH_RADIUS)
        skill_threshold = state.get("skill_threshold", DEFAULT_SKILL_THRESHOLD)
        fallback_triggered = state.get("fallback_triggered", False)
        
        # Determine urgency level for MCP
        urgency_map = {
            "emergency": "high",
            "severe": "high",
            "moderate": "medium",
            "mild": "low"
        }
        urgency = urgency_map.get(severity, "medium")
        
        # Determine service type for MCP
        service_type_map = {
            "compound_fracture": "Emergency Care",
            "third_degree_burn": "Emergency Care",
            "burn": "Emergency Care",
            "fracture": "Orthopedics",
            "wound": "Wound Care",
            "laceration": "Emergency Care",
            "bruise": "Primary Care",
            "sprain": "Orthopedics",
        }
        service_type = service_type_map.get(injury_type.lower(), "Primary Care")
        
        # TRY MCP SERVICE FIRST
        providers_list = []
        using_mcp = False
        
        if mcp_client and mcp_client.enabled:
            print(f"🔍 Searching real providers via MCP: {service_type} near {facility_address}")
            mcp_result = mcp_client.find_nearest_providers(
                patient_address=facility_address,
                service_type=service_type,
                urgency=urgency
            )
            
            if mcp_result and "providers" in mcp_result:
                providers_list = mcp_result["providers"]
                using_mcp = True
                search_radius_used = mcp_result.get("metadata", {}).get("search_radius_used", "unknown")
                print(f"✓ Found {len(providers_list)} real providers (radius: {search_radius_used})")
        
        # FALLBACK TO MOCK DATA
        if not providers_list:
            print("⚠️ MCP unavailable, using mock caregiver data")
            using_mcp = False
            
            # Convert CAREGIVER_PROFILES to providers_list format
            for cg_id, caregiver in CAREGIVER_PROFILES.items():
                # Mock distances
                mock_distances = {
                    "CG-001": 2.3,
                    "CG-002": 5.1,
                    "CG-003": 3.7
                }
                distance = mock_distances.get(cg_id, 10.0)
                
                # Apply radius filter
                if distance > search_radius:
                    continue
                
                providers_list.append({
                    "name": caregiver["name"],
                    "address": caregiver["location"],
                    "distance": f"{distance:.2f} miles",
                    "distance_miles": distance,
                    "travelTime": f"{int(distance * 2)} minutes",
                    "Rating": caregiver["avg_feedback_rating"],
                    "Skills": caregiver["skills"]
                })
        
        # SCORE AND RANK PROVIDERS
        best_provider = None
        best_score = 0
        
        for provider in providers_list:
            # Extract data
            provider_name = provider.get("name", "Unknown")
            provider_address = provider.get("address", "Unknown")
            provider_skills = provider.get("Skills", [])
            provider_rating = float(provider.get("Rating", 3.5))
            
            # Parse distance
            distance_str = provider.get("distance", "0 miles")
            try:
                distance_miles = float(distance_str.split()[0])
            except:
                distance_miles = provider.get("distance_miles", 50.0)
            
            # 1. SKILLS SCORE (40%) - via LLM
            llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
            
            system_prompt = """You are a healthcare staffing expert. Rate how well this provider's skills match the injury requirements.

Return ONLY a number from 0-100, where:
- 90-100: Excellent match
- 70-89: Good match  
- 50-69: Fair match
- 0-49: Poor match

Return only the number."""

            user_prompt = f"""
Injury: {injury_type} (severity: {severity})
Provider Skills: {', '.join(provider_skills) if provider_skills else 'General care'}

Skill match score (0-100):"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm.invoke(messages)
            
            try:
                skills_score = float(response.content.strip())
                skills_score = max(0, min(100, skills_score))
            except:
                skills_score = 50.0
            
            # Apply skill threshold filter
            if skills_score < skill_threshold:
                print(f"  ⊘ {provider_name}: skills={skills_score:.1f} (below threshold {skill_threshold})")
                continue
            
            # 2. PROXIMITY SCORE (25%)
            if distance_miles > search_radius:
                print(f"  ⊘ {provider_name}: distance={distance_miles:.1f}mi (outside radius {search_radius}mi)")
                continue
            
            proximity_score = max(0, 100 * (1 - distance_miles / search_radius))
            
            # 3. FEEDBACK SCORE (20%)
            feedback_score = (provider_rating / 5.0) * 100
            
            # 4. CALENDAR SCORE (15%)
            # For MCP providers, assume availability based on urgency
            # For mock providers, use calendar data
            if using_mcp:
                calendar_score = 100 if urgency == "high" else 80
            else:
                calendar_url = CAREGIVER_PROFILES.get(f"CG-{provider_name.split(',')[0][:3]}", {}).get("calendar_url")
                if calendar_url and calendar_url in CAREGIVER_CALENDARS:
                    calendar = CAREGIVER_CALENDARS[calendar_url]
                    calendar_score = 100 if calendar["availability_next_24h"] else 50
                else:
                    calendar_score = 80  # Default
            
            # WEIGHTED OVERALL SCORE
            overall_score = (
                skills_score * 0.40 +
                proximity_score * 0.25 +
                feedback_score * 0.20 +
                calendar_score * 0.15
            )
            
            print(f"  ✓ {provider_name}: overall={overall_score:.1f} "
                  f"(skills={skills_score:.1f}, prox={proximity_score:.1f}, "
                  f"feedback={feedback_score:.1f}, calendar={calendar_score:.1f}, "
                  f"dist={distance_miles:.1f}mi)")
            
            if overall_score > best_score:
                best_score = overall_score
                best_provider = {
                    "id": provider_name.replace(" ", "-").replace(",", ""),
                    "name": provider_name,
                    "address": provider_address,
                    "skills_score": skills_score,
                    "proximity_score": proximity_score,
                    "feedback_score": feedback_score,
                    "calendar_score": calendar_score,
                    "overall_score": overall_score,
                    "distance_miles": distance_miles,
                    "using_mcp": using_mcp
                }
        
        # CHECK IF WE FOUND A MATCH
        if best_provider is None:
            raise ValueError(f"No providers found matching criteria (radius={search_radius}mi, threshold={skill_threshold})")
        
        print(f"✓ Best match: {best_provider['name']} (score: {best_score:.1f})")
        if using_mcp:
            print(f"  [Real provider via MCP]")
        else:
            print(f"  [Mock data]")
        
        return {
            **state,
            "matched_caregiver_id": best_provider["id"],
            "matched_caregiver_name": best_provider["name"],
            "caregiver_address": best_provider["address"],
            "caregiver_skills_score": best_provider["skills_score"],
            "proximity_score": best_provider["proximity_score"],
            "feedback_score": best_provider["feedback_score"],
            "calendar_score": best_provider["calendar_score"],
            "overall_match_score": best_provider["overall_score"],
            "caregiver_distance_miles": best_provider["distance_miles"],
            "caregiver_source": "mcp" if using_mcp else "mock",
            "current_step": "match_caregiver",
            "completed_steps": ["match_caregiver"],
            "caregiver_retry_count": 0,
            "fallback_triggered": False,
            "search_radius_miles": DEFAULT_SEARCH_RADIUS,
            "skill_threshold": DEFAULT_SKILL_THRESHOLD
        }
        
    except Exception as e:
        error_msg = f"Caregiver matching error: {str(e)}"
        print(f"❌ {error_msg}")
        
        error_entry = log_error(state, "match_caregiver", error_msg, state.get("caregiver_retry_count", 0))
        
        return {
            **state,
            "caregiver_retry_count": state.get("caregiver_retry_count", 0) + 1,
            "error_log": [error_entry],
            "current_step": "match_caregiver_error"
        }
    
def check_caregiver_success(state: CareEncounterState) -> str:
    """Router to check if caregiver matching succeeded or needs retry/fallback"""
    if state.get("current_step") == "match_caregiver_error":
        retry_count = state.get("caregiver_retry_count", 0)
        
        if retry_count < MAX_RETRIES:
            # Check if we should trigger fallback strategy
            if not state.get("fallback_triggered", False):
                print(f"🔄 Triggering fallback strategy before retry")
                return "trigger_fallback"
            else:
                print(f"🔄 Retrying with fallback parameters (attempt {retry_count + 1}/{MAX_RETRIES})")
                return "retry_caregiver"
        else:
            print(f"🛑 Max retries exceeded for caregiver matching")
            return "caregiver_failed"
    
    return "caregiver_success"

    
def caregiver_fallback_node(state: CareEncounterState) -> CareEncounterState:
    """
    Fallback strategy: Expand search radius and lower skill threshold
    """
    print(f"\n🔄 FALLBACK: Adjusting caregiver search parameters")
    
    current_radius = state.get("search_radius_miles", DEFAULT_SEARCH_RADIUS)
    current_threshold = state.get("skill_threshold", DEFAULT_SKILL_THRESHOLD)
    
    # Expand radius by 10 miles
    new_radius = current_radius + 10.0
    # Lower threshold by 10 points
    new_threshold = max(50.0, current_threshold - 10.0)
    
    print(f"  Radius: {current_radius}mi → {new_radius}mi")
    print(f"  Skill threshold: {current_threshold} → {new_threshold}")
    
    return {
        **state,
        "search_radius_miles": new_radius,
        "skill_threshold": new_threshold,
        "fallback_triggered": True,
        "current_step": "fallback_triggered"
    }
# =====================================
# NODE 4: VISIT SCHEDULING WITH RETRY
# =====================================

def schedule_visit_node(state: CareEncounterState) -> CareEncounterState:
    """
    Schedule visit based on severity
    WITH ERROR HANDLING AND RETRY LOGIC
    """
    print(f"\n📅 NODE 4: VISIT SCHEDULING (Attempt {state.get('schedule_retry_count', 0) + 1})")
    
    try:
        severity = state["severity"]
        injury_type = state["injury_type"]
        matched_caregiver_id = state["matched_caregiver_id"]
        
        # Validate we have required data
        if not matched_caregiver_id:
            raise ValueError("No caregiver matched")
        
        # Severity-based scheduling
        now = datetime.now()
        
        if severity == "emergency":
            scheduled_time = now + timedelta(hours=1)
            timeframe = "within 1 hour"
        elif severity == "severe":
            scheduled_time = now + timedelta(hours=24)
            timeframe = "within 24 hours"
        elif severity == "moderate":
            scheduled_time = now + timedelta(hours=60)
            timeframe = "48-72 hours"
        else:  # mild
            scheduled_time = now + timedelta(days=6)
            timeframe = "5-7 days"
        
        # Generate visit ID and procedure code
        visit_id = f"VIS-{datetime.now().strftime('%Y%m%d')}-{state['patient_id'][-3:]}"
        
        procedure_codes = {
            "emergency": "99285",
            "severe": "99284",
            "moderate": "99283",
            "mild": "99213"
        }
        procedure_code = procedure_codes.get(severity, "99213")
        
        print(f"✓ Visit scheduled: {scheduled_time.strftime('%Y-%m-%d %H:%M')} ({timeframe})")
        
        return {
            **state,
            "visit_scheduled": True,
            "visit_datetime": scheduled_time.strftime("%Y-%m-%d %H:%M"),
            "visit_stub_id": visit_id,
            "procedure_code": procedure_code,
            "current_step": "schedule_visit",
            "completed_steps": ["schedule_visit"],
            "schedule_retry_count": 0  # Reset on success
        }
        
    except Exception as e:
        error_msg = f"Visit scheduling error: {str(e)}"
        print(f"❌ {error_msg}")
        
        error_entry = log_error(state, "schedule_visit", error_msg, state.get("schedule_retry_count", 0))
        
        return {
            **state,
            "schedule_retry_count": state.get("schedule_retry_count", 0) + 1,
            "error_log": [error_entry],
            "current_step": "schedule_visit_error"
        }


def check_schedule_success(state: CareEncounterState) -> str:
    """Router to check if scheduling succeeded or needs retry"""
    if state.get("current_step") == "schedule_visit_error":
        retry_count = state.get("schedule_retry_count", 0)
        if retry_count < MAX_RETRIES:
            print(f"🔄 Retrying visit scheduling (attempt {retry_count + 1}/{MAX_RETRIES})")
            return "retry_schedule"
        else:
            print(f"🛑 Max retries exceeded for visit scheduling")
            return "schedule_failed"
    
    return "schedule_success"


# =====================================
# FAILURE NODES
# =====================================

def classify_failed_node(state: CareEncounterState) -> CareEncounterState:
    """Handle classification failure after max retries"""
    print("🛑 CLASSIFICATION FAILED - Requires human intervention")
    return {
        **state,
        "requires_human_review": True,
        "current_step": "failed_classification"
    }

def insurance_failed_node(state: CareEncounterState) -> CareEncounterState:
    """Handle insurance verification failure after max retries"""
    print("🛑 INSURANCE VERIFICATION FAILED - Requires human intervention")
    return {
        **state,
        "requires_human_review": True,
        "current_step": "failed_insurance"
    }

def caregiver_failed_node(state: CareEncounterState) -> CareEncounterState:
    """Handle caregiver matching failure after max retries"""
    print("🛑 CAREGIVER MATCHING FAILED - Requires human intervention")
    return {
        **state,
        "requires_human_review": True,
        "current_step": "failed_caregiver"
    }

def schedule_failed_node(state: CareEncounterState) -> CareEncounterState:
    """Handle scheduling failure after max retries"""
    print("🛑 VISIT SCHEDULING FAILED - Requires human intervention")
    return {
        **state,
        "requires_human_review": True,
        "current_step": "failed_schedule"
    }

def coverage_denied_node(state: CareEncounterState) -> CareEncounterState:
    """Handle coverage denial (business logic, not error)"""
    print("⛔ COVERAGE DENIED - Manual review required")
    return {
        **state,
        "requires_human_review": True,
        "current_step": "coverage_denied"
    }


# =====================================
# FINAL ROUTER
# =====================================

def route_final(state: CareEncounterState) -> str:
    """Final routing decision"""
    severity = state.get("severity", "")
    is_covered = state.get("is_covered", False)
    
    # Check for emergency cases without coverage
    if severity == "emergency" and not is_covered:
        print("⚠️ Emergency case without coverage - flagging for human review")
        return "human_review"
    
    print("✅ Workflow complete successfully")
    return "complete"


def final_review_node(state: CareEncounterState) -> CareEncounterState:
    """Flag for human review"""
    return {
        **state,
        "requires_human_review": True,
        "current_step": "human_review_required"
    }


# =====================================
# WORKFLOW CREATION WITH RETRY LOOPS
# =====================================

def create_workflow():
    """Build the LangGraph workflow with error handling and retry loops"""
    
    workflow = StateGraph(CareEncounterState)
    
    # Add all nodes
    workflow.add_node("classify_injury", classify_injury_node)
    workflow.add_node("classify_failed", classify_failed_node)
    
    workflow.add_node("verify_insurance", insurance_check_node)
    workflow.add_node("insurance_failed", insurance_failed_node)
    workflow.add_node("coverage_denied", coverage_denied_node)
    
    workflow.add_node("match_caregiver", match_caregiver_node)
    workflow.add_node("caregiver_fallback", caregiver_fallback_node)
    workflow.add_node("caregiver_failed", caregiver_failed_node)
    
    workflow.add_node("schedule_visit", schedule_visit_node)
    workflow.add_node("schedule_failed", schedule_failed_node)
    
    workflow.add_node("final_review", final_review_node)
    
    # Entry point
    workflow.set_entry_point("classify_injury")
    
    # Classification with retry loop
    workflow.add_conditional_edges(
        "classify_injury",
        check_classify_success,
        {
            "retry_classify": "classify_injury",  # LOOP BACK
            "classify_failed": "classify_failed",
            "classify_success": "verify_insurance"
        }
    )
    workflow.add_edge("classify_failed", END)
    
    # Insurance verification with retry loop
    workflow.add_conditional_edges(
        "verify_insurance",
        check_insurance_success,
        {
            "retry_insurance": "verify_insurance",  # LOOP BACK
            "insurance_failed": "insurance_failed",
            "coverage_denied": "coverage_denied",
            "insurance_success": "match_caregiver"
        }
    )
    workflow.add_edge("insurance_failed", END)
    workflow.add_edge("coverage_denied", END)
    
    # Caregiver matching with retry loop and fallback
    workflow.add_conditional_edges(
        "match_caregiver",
        check_caregiver_success,
        {
            "trigger_fallback": "caregiver_fallback",
            "retry_caregiver": "match_caregiver",  # LOOP BACK
            "caregiver_failed": "caregiver_failed",
            "caregiver_success": "schedule_visit"
        }
    )
    workflow.add_edge("caregiver_fallback", "match_caregiver")  # LOOP BACK after fallback
    workflow.add_edge("caregiver_failed", END)
    
    # Visit scheduling with retry loop
    workflow.add_conditional_edges(
        "schedule_visit",
        check_schedule_success,
        {
            "retry_schedule": "schedule_visit",  # LOOP BACK
            "schedule_failed": "schedule_failed",
            "schedule_success": "final_router"
        }
    )
    workflow.add_edge("schedule_failed", END)
    
    # Final routing
    workflow.add_node("final_router", lambda state: state)  # Pass-through node for routing
    workflow.add_conditional_edges(
        "final_router",
        route_final,
        {
            "human_review": "final_review",
            "complete": END
        }
    )
    workflow.add_edge("final_review", END)
    
    return workflow.compile()


# =====================================
# STREAMLIT UI
# =====================================

def main():
    st.set_page_config(
        page_title="Camera-to-Care System",
        page_icon="🏥",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #2c5aa0;
            text-align: center;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .score-excellent { color: #4caf50; font-weight: bold; }
        .score-good { color: #8bc34a; font-weight: bold; }
        .score-fair { color: #ffc107; font-weight: bold; }
        .score-poor { color: #f44336; font-weight: bold; }
        .retry-badge { 
            background: #ffc107; 
            color: #000; 
            padding: 2px 8px; 
            border-radius: 4px; 
            font-size: 0.8em;
            font-weight: bold;
        }
        .error-box {
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .success-box {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Camera-to-Care System</h1>', unsafe_allow_html=True)
    st.markdown("### *From Image → Insurance → Caregiver Match → Visit Scheduled*")
    
    st.markdown("### 🔐 Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", "")
    )


    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x120/2c5aa0/ffffff?text=Camera-to-Care", use_container_width=True)
        st.markdown("---")
        
    
        
        st.markdown("---")
        st.markdown("### 📊 Workflow Steps")
        st.markdown("""
        1. **📸 Upload** - Image capture
        2. **🔍 Classify** - Injury type & severity
        3. **💳 Verify** - Insurance coverage
        4. **👥 Match** - Optimal caregiver
        5. **📅 Schedule** - Book visit
        """)
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key to continue")
        st.stop()
    
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("## 📸 Step 1: Upload Patient Image")
        
        # Patient selection
        patient_id = st.selectbox(
            "Select Patient",
            options=list(RESIDENT_PROFILES.keys()),
            format_func=lambda x: f"{x} - {RESIDENT_PROFILES[x]['name']}"
        )
        
        resident = RESIDENT_PROFILES[patient_id]
        
        st.info(f"""
        **Patient:** {resident['name']} (Age {resident['age']})  
        **Facility:** {resident['facility_address']}  
        **Insurance:** {resident['insurance']['provider']}
        """)
        
        # Image upload
        uploaded_file = st.file_uploader(
            "Upload injury/wound image",
            type=["jpg", "jpeg", "png"],
            help="Take a photo of the injury or wound"
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            image_base64 = f"data:image/png;base64,{img_str}"
    
    with col2:
        st.markdown("## 🚀 Step 2: Process Workflow")
        
        if uploaded_file and st.button("▶️ Start AI Analysis & Scheduling", type="primary", use_container_width=True):
            with st.spinner("Processing workflow with retry logic..."):
                try:
                    # Initialize state with retry counters
                    initial_state = CareEncounterState(
                        image_base64=image_base64,
                        patient_id=patient_id,
                        facility_address=resident["facility_address"],
                        timestamp=datetime.now().isoformat(),
                        injury_type="",
                        severity="mild",
                        clinical_description="",
                        insurance_provider="",
                        insurance_plan="",
                        coverage_percentage=0.0,
                        copay_amount=0.0,
                        is_covered=False,
                        eob_summary="",
                        matched_caregiver_id="",
                        matched_caregiver_name="",
                        caregiver_skills_score=0.0,
                        proximity_score=0.0,
                        feedback_score=0.0,
                        calendar_score=0.0,
                        overall_match_score=0.0,
                        caregiver_distance_miles=0.0,
                        visit_scheduled=False,
                        visit_datetime="",
                        visit_stub_id="",
                        procedure_code="",
                        current_step="",
                        completed_steps=[],
                        requires_human_review=False,
                        # NEW: Initialize retry counters
                        classify_retry_count=0,
                        insurance_retry_count=0,
                        caregiver_retry_count=0,
                        schedule_retry_count=0,
                        error_log=[],
                        fallback_triggered=False,
                        search_radius_miles=DEFAULT_SEARCH_RADIUS,
                        skill_threshold=DEFAULT_SKILL_THRESHOLD
                    )
                    
                    # Create and run workflow
                    workflow = create_workflow()
                    final_state = workflow.invoke(initial_state)
                    
                    st.success("✅ Workflow completed!")
                    
                    # Display results in tabs
                    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                        "Classification", 
                        "Insurance", 
                        "Caregiver Match", 
                        "Scheduling", 
                        "Summary",
                        "🔄 Error Log"
                    ])
                    
                    with tab1:
                        st.markdown("### Injury Classification")
                        
                        # Show retry count if any
                        classify_retries = final_state.get('classify_retry_count', 0)
                        if classify_retries > 0:
                            st.markdown(f'<span class="retry-badge">Retried {classify_retries}x</span>', unsafe_allow_html=True)
                        
                        severity = final_state.get('severity', 'unknown')
                        severity_colors = {
                            "emergency": "🔴",
                            "severe": "🟠",
                            "moderate": "🟡",
                            "mild": "🟢"
                        }
                        
                        col_c1, col_c2 = st.columns(2)
                        with col_c1:
                            st.metric("Injury Type", final_state.get('injury_type', 'N/A'))
                        with col_c2:
                            st.metric("Severity", f"{severity_colors.get(severity, '⚪')} {severity.title()}")
                        
                        st.markdown("**Clinical Description:**")
                        st.info(final_state.get('clinical_description', 'N/A'))
                    
                    with tab2:
                        st.markdown("### Insurance Verification")
                        
                        # Show retry count if any
                        insurance_retries = final_state.get('insurance_retry_count', 0)
                        if insurance_retries > 0:
                            st.markdown(f'<span class="retry-badge">Retried {insurance_retries}x</span>', unsafe_allow_html=True)
                        
                        is_covered = final_state.get('is_covered', False)
                        if is_covered:
                            st.success("✅ Coverage Approved")
                        else:
                            st.error("⛔ Coverage Denied")
                        
                        col_ins1, col_ins2 = st.columns(2)
                        
                        with col_ins1:
                            st.markdown(f"""
                            **Provider:** {final_state.get('insurance_provider', 'N/A')}  
                            **Plan:** {final_state.get('insurance_plan', 'N/A')}  
                            **Coverage:** {final_state.get('coverage_percentage', 0)}%  
                            **Copay:** ${final_state.get('copay_amount', 0):.2f}
                            """)
                        
                        with col_ins2:
                            st.markdown("**Explanation of Benefits (EOB):**")
                            eob = final_state.get('eob_summary', 'N/A')
                            st.text_area("EOB Summary", eob, height=150)
                    
                    with tab3:
                        st.markdown("### Caregiver Matching")
                        
                        # Show retry count and fallback status
                        caregiver_retries = final_state.get('caregiver_retry_count', 0)
                        fallback_triggered = final_state.get('fallback_triggered', False)
                        
                        if caregiver_retries > 0 or fallback_triggered:
                            badge_text = f"Retried {caregiver_retries}x"
                            if fallback_triggered:
                                badge_text += " (Fallback Used)"
                            st.markdown(f'<span class="retry-badge">{badge_text}</span>', unsafe_allow_html=True)
                        
                        if final_state.get('matched_caregiver_name'):
                            st.success(f"✅ Best Match: {final_state.get('matched_caregiver_name')}")
                        
                        # Scoring breakdown
                        st.markdown("#### Matching Scores")
                        
                        scores = {
                            "Skills Match": (final_state.get('caregiver_skills_score', 0), "40%"),
                            "Proximity": (final_state.get('proximity_score', 0), "25%"),
                            "Feedback Rating": (final_state.get('feedback_score', 0), "20%"),
                            "Calendar Availability": (final_state.get('calendar_score', 0), "15%")
                        }
                        
                        for criterion, (score, weight) in scores.items():
                            col_score, col_bar = st.columns([1, 3])
                            
                            with col_score:
                                if score >= 90:
                                    score_class = "score-excellent"
                                elif score >= 70:
                                    score_class = "score-good"
                                elif score >= 50:
                                    score_class = "score-fair"
                                else:
                                    score_class = "score-poor"
                                
                                st.markdown(f"**{criterion}** ({weight})")
                                st.markdown(f'<span class="{score_class}">{score:.1f}/100</span>', unsafe_allow_html=True)
                            
                            with col_bar:
                                st.progress(score / 100)
                        
                        st.markdown("---")
                        
                        overall = final_state.get('overall_match_score', 0)
                        st.markdown(f"### Overall Match Score: **{overall:.1f}/100**")
                        st.progress(overall / 100)
                        
                        distance = final_state.get('caregiver_distance_miles', 0)
                        st.info(f"📍 Distance to facility: **{distance:.1f} miles**")
                    
                    with tab4:
                        st.markdown("### Visit Scheduling")
                        
                        # Show retry count if any
                        schedule_retries = final_state.get('schedule_retry_count', 0)
                        if schedule_retries > 0:
                            st.markdown(f'<span class="retry-badge">Retried {schedule_retries}x</span>', unsafe_allow_html=True)
                        
                        if final_state.get('visit_scheduled'):
                            st.success("✅ Visit Successfully Scheduled!")
                            
                            col_v1, col_v2 = st.columns(2)
                            
                            with col_v1:
                                st.markdown("**Visit Information:**")
                                st.info(f"""
                                **Visit ID:** {final_state.get('visit_stub_id', 'N/A')}  
                                **Scheduled Time:** {final_state.get('visit_datetime', 'N/A')}  
                                **Caregiver:** {final_state.get('matched_caregiver_name', 'N/A')}  
                                **Procedure Code:** {final_state.get('procedure_code', 'N/A')}
                                """)
                            
                            with col_v2:
                                st.markdown("**Billing Information:**")
                                
                                coverage_pct = final_state.get('coverage_percentage', 0)
                                copay = final_state.get('copay_amount', 0)
                                
                                base_cost = 150.00
                                insurance_pays = base_cost * (coverage_pct / 100)
                                patient_pays = copay
                                
                                st.info(f"""
                                **Estimated Service Cost:** ${base_cost:.2f}  
                                **Insurance Pays ({coverage_pct}%):** ${insurance_pays:.2f}  
                                **Patient Copay:** ${patient_pays:.2f}  
                                **Patient Total:** ${patient_pays:.2f}
                                """)
                        else:
                            st.warning("⚠️ Visit not scheduled - please review")
                    
                    with tab5:
                        st.markdown("### Complete Workflow Summary")
                        
                        summary = {
                            "Timestamp": final_state.get('timestamp'),
                            "Patient": {
                                "ID": final_state.get('patient_id'),
                                "Name": resident['name'],
                                "Facility": final_state.get('facility_address')
                            },
                            "Classification": {
                                "Injury Type": final_state.get('injury_type'),
                                "Severity": final_state.get('severity'),
                                "Description": final_state.get('clinical_description'),
                                "Retry Count": final_state.get('classify_retry_count', 0)
                            },
                            "Insurance": {
                                "Provider": final_state.get('insurance_provider'),
                                "Plan": final_state.get('insurance_plan'),
                                "Covered": final_state.get('is_covered'),
                                "Coverage %": final_state.get('coverage_percentage'),
                                "Copay": final_state.get('copay_amount'),
                                "Retry Count": final_state.get('insurance_retry_count', 0)
                            },
                            "Caregiver Match": {
                                "Name": final_state.get('matched_caregiver_name'),
                                "Overall Score": final_state.get('overall_match_score'),
                                "Skills Score": final_state.get('caregiver_skills_score'),
                                "Proximity Score": final_state.get('proximity_score'),
                                "Feedback Score": final_state.get('feedback_score'),
                                "Calendar Score": final_state.get('calendar_score'),
                                "Distance": final_state.get('caregiver_distance_miles'),
                                "Retry Count": final_state.get('caregiver_retry_count', 0),
                                "Fallback Used": final_state.get('fallback_triggered', False)
                            },
                            "Visit": {
                                "Scheduled": final_state.get('visit_scheduled'),
                                "Visit ID": final_state.get('visit_stub_id'),
                                "Date/Time": final_state.get('visit_datetime'),
                                "Procedure Code": final_state.get('procedure_code'),
                                "Retry Count": final_state.get('schedule_retry_count', 0)
                            },
                            "Workflow": {
                                "Steps Completed": final_state.get('completed_steps', []),
                                "Current Step": final_state.get('current_step'),
                                "Requires Review": final_state.get('requires_human_review', False),
                                "Total Retries": (
                                    final_state.get('classify_retry_count', 0) +
                                    final_state.get('insurance_retry_count', 0) +
                                    final_state.get('caregiver_retry_count', 0) +
                                    final_state.get('schedule_retry_count', 0)
                                )
                            }
                        }
                        
                        st.json(summary)
                        
                        summary_json = json.dumps(summary, indent=2)
                        st.download_button(
                            "📥 Download Complete Summary (JSON)",
                            summary_json,
                            file_name=f"camera_to_care_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with tab6:
                        st.markdown("### 🔄 Error Log & Retry History")
                        
                        error_log = final_state.get('error_log', [])
                        
                        if error_log:
                            st.warning(f"⚠️ {len(error_log)} error(s) occurred during processing (automatically recovered)")
                            
                            for i, error_entry in enumerate(error_log, 1):
                                with st.expander(f"Error {i}: {error_entry['node']} (Attempt {error_entry['retry_count'] + 1})"):
                                    st.markdown(f"**Timestamp:** {error_entry['timestamp']}")
                                    st.markdown(f"**Node:** {error_entry['node']}")
                                    st.markdown(f"**Error:** {error_entry['error']}")
                                    st.markdown(f"**Retry Count:** {error_entry['retry_count']}")
                                    st.json(error_entry['state_snapshot'])
                        else:
                            st.success("✅ No errors occurred - workflow completed successfully on first attempt!")
                        
                        # Summary statistics
                        st.markdown("---")
                        st.markdown("### Retry Statistics")
                        
                        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                        
                        with col_r1:
                            st.metric("Classification", f"{final_state.get('classify_retry_count', 0)} retries")
                        with col_r2:
                            st.metric("Insurance", f"{final_state.get('insurance_retry_count', 0)} retries")
                        with col_r3:
                            st.metric("Caregiver", f"{final_state.get('caregiver_retry_count', 0)} retries")
                        with col_r4:
                            st.metric("Scheduling", f"{final_state.get('schedule_retry_count', 0)} retries")
                    
                except Exception as e:
                    st.error(f"❌ Fatal error: {str(e)}")
                    st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #718096;'>
            <p>🏥 Camera-to-Care System | AI-Powered Healthcare Workflow<br>
            Insurance Verification • Caregiver Matching • Automated Scheduling</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
