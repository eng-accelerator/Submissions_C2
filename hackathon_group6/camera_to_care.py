"""
Camera-to-Care: Complete Multi-Agent System
From Image Upload → Insurance Verification → Caregiver Matching → Scheduling

Revised Architecture with LangGraph + MCPs
"""

import streamlit as st
import base64
import io
import json
from datetime import datetime, timedelta
from typing import TypedDict, Literal, List, Annotated, Optional
import operator
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
import os

# =====================================
# STATE DEFINITION
# =====================================

class CareEncounterState(TypedDict):
    """Complete state for Camera-to-Care workflow"""
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
    caregiver_skills_score: float
    proximity_score: float
    feedback_score: float
    calendar_score: float
    overall_match_score: float
    caregiver_distance_miles: float
    
    # Step 5: Scheduling
    visit_scheduled: bool
    visit_datetime: str
    visit_stub_id: str
    procedure_code: str
    
    # Process tracking
    current_step: str
    completed_steps: Annotated[List[str], operator.add]
    requires_human_review: bool


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
        "location": "321 Broadway, Oakland, CA 94612",
        "avg_feedback_rating": 4.6,
        "total_reviews": 89,
        "calendar_url": "cal-cg002"
    },
    "CG-003": {
        "name": "Dr. Emily Martinez, MD",
        "skills": ["wound_care", "IV_therapy", "emergency_care", "surgical_wound_care"],
        "location": "555 California Street, San Francisco, CA 94104",
        "avg_feedback_rating": 4.9,
        "total_reviews": 234,
        "calendar_url": "cal-cg003"
    }
}

# Mock Calendar Availability (simulating MCP)
CAREGIVER_CALENDARS = {
    "cal-cg001": {
        "available_slots": [
            "2024-11-08 10:00",
            "2024-11-08 14:00",
            "2024-11-09 09:00"
        ]
    },
    "cal-cg002": {
        "available_slots": [
            "2024-11-08 11:00",
            "2024-11-08 15:00"
        ]
    },
    "cal-cg003": {
        "available_slots": [
            "2024-11-08 16:00",
            "2024-11-09 10:00"
        ]
    }
}


# =====================================
# AGENT 1: INJURY CLASSIFIER
# =====================================

class InjuryClassifierAgent:
    """Classifies injury type and severity from image"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
    
    def classify(self, image_base64: str) -> dict:
        """Analyze image and classify injury"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a clinical AI assistant specializing in injury classification for elderly care.

Analyze the provided image and determine:
1. **Injury Type**: pressure_ulcer, skin_tear, bruise, rash, burn, surgical_wound, or other
2. **Severity**: mild, moderate, severe, or emergency
3. **Clinical Description**: Detailed description including size, stage, location

Return ONLY valid JSON format:
{{
    "injury_type": "pressure_ulcer",
    "severity": "moderate",
    "clinical_description": "3cm stage 2 pressure ulcer on left heel with surrounding erythema"
}}"""),
            ("user", [
                {"type": "text", "text": "Classify this injury:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ])
        ])
        
        response = self.llm.invoke(prompt.format_messages())
        
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except:
            return {
                "injury_type": "unknown",
                "severity": "moderate",
                "clinical_description": "Unable to classify - requires human review"
            }


# =====================================
# AGENT 2: INSURANCE VERIFICATION
# =====================================

class InsuranceVerificationAgent:
    """Verifies insurance eligibility and coverage"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
    
    def verify_coverage(self, patient_id: str, injury_type: str, severity: str) -> dict:
        """Check insurance coverage for the injury"""
        
        # Step 1: Read resident profile
        resident = RESIDENT_PROFILES.get(patient_id, {})
        if not resident:
            return {
                "is_covered": False,
                "error": "Patient not found"
            }
        
        insurance = resident.get("insurance", {})
        provider = insurance.get("provider", "Unknown")
        
        # Step 2: Read payer terms (simulating PDF parsing with MCP)
        service_type = self._map_injury_to_service(injury_type, severity)
        payer_terms = PAYER_TERMS.get(provider, {}).get(service_type, {})
        
        if not payer_terms:
            return {
                "insurance_provider": provider,
                "insurance_plan": insurance.get("plan", "Unknown"),
                "is_covered": False,
                "coverage_percentage": 0,
                "copay_amount": 0,
                "eob_summary": "Service not covered under current plan"
            }
        
        # Step 3: Generate EOB (Explanation of Benefits)
        eob = self._generate_eob(
            patient_id,
            provider,
            insurance.get("plan"),
            service_type,
            payer_terms
        )
        
        return {
            "insurance_provider": provider,
            "insurance_plan": insurance.get("plan", "Unknown"),
            "is_covered": payer_terms.get("covered", False),
            "coverage_percentage": payer_terms.get("coverage_percentage", 0),
            "copay_amount": payer_terms.get("copay", 0),
            "eob_summary": eob
        }
    
    def _map_injury_to_service(self, injury_type: str, severity: str) -> str:
        """Map injury type to billable service"""
        if injury_type in ["pressure_ulcer", "surgical_wound"]:
            return "wound_care"
        return "routine_visit"
    
    def _generate_eob(self, patient_id: str, provider: str, plan: str, 
                      service: str, terms: dict) -> str:
        """Generate Explanation of Benefits summary"""
        
        covered = "COVERED" if terms.get("covered") else "NOT COVERED"
        coverage = terms.get("coverage_percentage", 0)
        copay = terms.get("copay", 0)
        
        eob = f"""
EXPLANATION OF BENEFITS (EOB)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patient: {patient_id}
Insurance: {provider} - {plan}
Service: {service.replace('_', ' ').title()}
Status: {covered}

Coverage Details:
• Plan Pays: {coverage}%
• Patient Copay: ${copay:.2f}
• Requires Pre-Auth: {'Yes' if terms.get('requires_preauth') else 'No'}

Notes: {terms.get('notes', 'Standard coverage applies')}
"""
        return eob.strip()


# =====================================
# AGENT 3: CAREGIVER MATCHER
# =====================================

class CaregiverMatcherAgent:
    """Matches optimal caregiver based on multiple criteria"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.2
        )
    
    def match_caregiver(self, injury_type: str, severity: str, 
                        facility_address: str, patient_id: str) -> dict:
        """Find best caregiver match using 4 scoring criteria"""
        
        best_match = None
        best_score = 0
        
        for cg_id, caregiver in CAREGIVER_PROFILES.items():
            # Calculate all 4 scores
            skills_score = self._calculate_skills_score(
                caregiver["skills"], injury_type, severity
            )
            
            proximity_score = self._calculate_proximity_score(
                caregiver["location"], facility_address
            )
            
            feedback_score = self._calculate_feedback_score(
                caregiver["avg_feedback_rating"]
            )
            
            calendar_score = self._calculate_calendar_score(
                caregiver["calendar_url"]
            )
            
            # Overall weighted score
            overall_score = (
                skills_score * 0.40 +      # 40% weight on skills
                proximity_score * 0.25 +    # 25% weight on proximity
                feedback_score * 0.20 +     # 20% weight on feedback
                calendar_score * 0.15       # 15% weight on availability
            )
            
            if overall_score > best_score:
                best_score = overall_score
                best_match = {
                    "caregiver_id": cg_id,
                    "caregiver_name": caregiver["name"],
                    "skills_score": skills_score,
                    "proximity_score": proximity_score,
                    "feedback_score": feedback_score,
                    "calendar_score": calendar_score,
                    "overall_score": overall_score,
                    "distance_miles": self._get_distance(
                        caregiver["location"], facility_address
                    ),
                    "calendar_url": caregiver["calendar_url"]
                }
        
        return best_match or {}
    
    def _calculate_skills_score(self, caregiver_skills: List[str], 
                                 injury_type: str, severity: str) -> float:
        """Score based on skill match (0-100)"""
        
        required_skills = {
            "pressure_ulcer": ["wound_care"],
            "surgical_wound": ["wound_care", "surgical_wound_care"],
            "skin_tear": ["basic_wound_care"],
        }
        
        needed = required_skills.get(injury_type, ["basic_wound_care"])
        
        if severity == "severe":
            needed.append("IV_therapy")
        if severity == "emergency":
            needed.append("emergency_care")
        
        matched = sum(1 for skill in needed if skill in caregiver_skills)
        score = (matched / len(needed)) * 100 if needed else 50
        
        return min(score, 100)
    
    def _calculate_proximity_score(self, cg_location: str, 
                                     resident_location: str) -> float:
        """Score based on distance (0-100, closer = higher)"""
        
        # Simulate MCP call to get distance
        distance = self._get_distance(cg_location, resident_location)
        
        # Score: 100 for <1 mile, decreasing to 0 at 20+ miles
        if distance < 1:
            return 100
        elif distance < 5:
            return 100 - (distance - 1) * 10  # 90-100 for 1-5 miles
        elif distance < 10:
            return 50 - (distance - 5) * 5    # 50-75 for 5-10 miles
        else:
            return max(0, 50 - (distance - 10) * 5)  # 0-50 for 10+ miles
    
    def _get_distance(self, location1: str, location2: str) -> float:
        """Simulate MCP distance calculation"""
        # In real implementation, this would call Google Maps API or similar
        # For demo, we'll use simple city-based distances
        
        if "San Francisco" in location1 and "San Francisco" in location2:
            return 2.5
        elif "Oakland" in location1 and "Oakland" in location2:
            return 3.0
        elif ("San Francisco" in location1 and "Oakland" in location2) or \
             ("Oakland" in location1 and "San Francisco" in location2):
            return 12.5
        else:
            return 8.0
    
    def _calculate_feedback_score(self, avg_rating: float) -> float:
        """Score based on feedback rating (0-100)"""
        # Convert 0-5 star rating to 0-100 scale
        return (avg_rating / 5.0) * 100
    
    def _calculate_calendar_score(self, calendar_url: str) -> float:
        """Score based on availability (0-100)"""
        # Simulate MCP call to caregiver calendar
        calendar = CAREGIVER_CALENDARS.get(calendar_url, {})
        available_slots = calendar.get("available_slots", [])
        
        # More available slots = higher score
        if len(available_slots) >= 3:
            return 100
        elif len(available_slots) == 2:
            return 70
        elif len(available_slots) == 1:
            return 40
        else:
            return 10


# =====================================
# AGENT 4: VISIT SCHEDULER
# =====================================

class VisitSchedulerAgent:
    """Schedules visit and creates billing stub"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
    
    def schedule_visit(self, caregiver_calendar: str, injury_type: str, 
                       severity: str) -> dict:
        """Create visit stub with procedure code"""
        
        # Get first available slot
        calendar = CAREGIVER_CALENDARS.get(caregiver_calendar, {})
        available_slots = calendar.get("available_slots", [])
        
        if not available_slots:
            return {
                "visit_scheduled": False,
                "error": "No available slots"
            }
        
        visit_datetime = available_slots[0]
        
        # Assign procedure code (CPT code)
        procedure_code = self._get_procedure_code(injury_type, severity)
        
        # Create visit stub
        visit_stub = {
            "visit_scheduled": True,
            "visit_datetime": visit_datetime,
            "visit_stub_id": f"VISIT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "procedure_code": procedure_code,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        return visit_stub
    
    def _get_procedure_code(self, injury_type: str, severity: str) -> str:
        """Map injury to CPT procedure code"""
        
        codes = {
            "pressure_ulcer": {
                "mild": "99213",      # Office visit, level 3
                "moderate": "97597",  # Debridement
                "severe": "97602",    # Wound care with selective debridement
                "emergency": "99285"  # Emergency dept visit
            },
            "surgical_wound": {
                "mild": "99213",
                "moderate": "97597",
                "severe": "97598",
                "emergency": "99285"
            },
            "skin_tear": {
                "mild": "12001",  # Simple wound repair
                "moderate": "12002",
                "severe": "12004"
            }
        }
        
        return codes.get(injury_type, {}).get(severity, "99213")


# =====================================
# LANGGRAPH WORKFLOW
# =====================================

def create_camera_to_care_workflow(api_key: str):
    """Build the complete LangGraph workflow"""
    
    # Initialize agents
    injury_classifier = InjuryClassifierAgent(api_key)
    insurance_verifier = InsuranceVerificationAgent(api_key)
    caregiver_matcher = CaregiverMatcherAgent(api_key)
    visit_scheduler = VisitSchedulerAgent(api_key)
    
    # Define workflow nodes
    def classify_injury_node(state: CareEncounterState) -> CareEncounterState:
        """Step 2: Classify injury type and severity"""
        st.write("🔍 **Step 2:** Classifying injury...")
        
        classification = injury_classifier.classify(state['image_base64'])
        
        return {
            **state,
            "injury_type": classification['injury_type'],
            "severity": classification['severity'],
            "clinical_description": classification['clinical_description'],
            "current_step": "classification",
            "completed_steps": ["classification"]
        }
    
    def verify_insurance_node(state: CareEncounterState) -> CareEncounterState:
        """Step 3: Verify insurance coverage"""
        st.write("💳 **Step 3:** Verifying insurance coverage...")
        
        coverage = insurance_verifier.verify_coverage(
            state['patient_id'],
            state['injury_type'],
            state['severity']
        )
        
        return {
            **state,
            **coverage,
            "current_step": "insurance",
            "completed_steps": ["insurance"]
        }
    
    def coverage_router(state: CareEncounterState) -> str:
        """Route based on insurance coverage"""
        if not state.get('is_covered', False):
            return "coverage_denied"
        return "match_caregiver"
    
    def coverage_denied_node(state: CareEncounterState) -> CareEncounterState:
        """Handle denied coverage"""
        st.error("⚠️ Insurance does not cover this service")
        
        return {
            **state,
            "requires_human_review": True,
            "current_step": "coverage_denied",
            "completed_steps": ["coverage_denied"]
        }
    
    def match_caregiver_node(state: CareEncounterState) -> CareEncounterState:
        """Step 4: Match optimal caregiver"""
        st.write("🔎 **Step 4:** Matching caregiver...")
        st.write("   • Analyzing skills...")
        st.write("   • Calculating proximity...")
        st.write("   • Checking feedback scores...")
        st.write("   • Reviewing calendar availability...")
        
        match = caregiver_matcher.match_caregiver(
            state['injury_type'],
            state['severity'],
            state['facility_address'],
            state['patient_id']
        )
        
        return {
            **state,
            "matched_caregiver_id": match.get('caregiver_id', ''),
            "matched_caregiver_name": match.get('caregiver_name', ''),
            "caregiver_skills_score": match.get('skills_score', 0),
            "proximity_score": match.get('proximity_score', 0),
            "feedback_score": match.get('feedback_score', 0),
            "calendar_score": match.get('calendar_score', 0),
            "overall_match_score": match.get('overall_score', 0),
            "caregiver_distance_miles": match.get('distance_miles', 0),
            "current_step": "matching",
            "completed_steps": ["matching"]
        }
    
    def schedule_visit_node(state: CareEncounterState) -> CareEncounterState:
        """Step 5: Schedule the visit"""
        st.write("📅 **Step 5:** Scheduling visit...")
        
        # Get caregiver calendar URL
        caregiver_id = state.get('matched_caregiver_id', '')
        calendar_url = CAREGIVER_PROFILES.get(caregiver_id, {}).get('calendar_url', '')
        
        visit = visit_scheduler.schedule_visit(
            calendar_url,
            state['injury_type'],
            state['severity']
        )
        
        return {
            **state,
            **visit,
            "current_step": "scheduling",
            "completed_steps": ["scheduling"]
        }
    
    # Build graph
    workflow = StateGraph(CareEncounterState)
    
    # Add nodes
    workflow.add_node("classify_injury", classify_injury_node)
    workflow.add_node("verify_insurance", verify_insurance_node)
    workflow.add_node("coverage_denied", coverage_denied_node)
    workflow.add_node("match_caregiver", match_caregiver_node)
    workflow.add_node("schedule_visit", schedule_visit_node)
    
    # Define flow
    workflow.set_entry_point("classify_injury")
    workflow.add_edge("classify_injury", "verify_insurance")
    workflow.add_conditional_edges(
        "verify_insurance",
        coverage_router,
        {
            "coverage_denied": "coverage_denied",
            "match_caregiver": "match_caregiver"
        }
    )
    workflow.add_edge("coverage_denied", END)
    workflow.add_edge("match_caregiver", "schedule_visit")
    workflow.add_edge("schedule_visit", END)
    
    return workflow.compile()


# =====================================
# STREAMLIT UI
# =====================================

def encode_image(image_file):
    """Encode uploaded image to base64"""
    image = Image.open(image_file)
    max_size = (1024, 1024)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


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
            font-size: 2.5rem;
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
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Camera-to-Care System</h1>', unsafe_allow_html=True)
    st.markdown("### *From Image → Insurance → Caregiver Match → Visit Scheduled*")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x120/2c5aa0/ffffff?text=Camera-to-Care", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### 🔐 Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", "")
        )
        
        st.markdown("---")
        st.markdown("### 📊 Workflow Steps")
        st.markdown("""
        1. **📸 Upload** - Image capture
        2. **🔍 Classify** - Injury type & severity
        3. **💳 Verify** - Insurance coverage
        4. **👥 Match** - Optimal caregiver
        5. **📅 Schedule** - Book visit
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 Matching Criteria")
        st.info("""
        **40%** Skills Match  
        **25%** Proximity  
        **20%** Feedback Rating  
        **15%** Calendar Availability
        """)
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key to continue")
        st.stop()
    
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
        **Patient:** {resident['name']}  
        **Age:** {resident['age']}  
        **Insurance:** {resident['insurance']['provider']}  
        **Location:** {resident['facility_address']}
        """)
        
        # Image upload
        uploaded_file = st.file_uploader(
            "Upload injury image",
            type=['jpg', 'jpeg', 'png']
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            process_btn = st.button(
                "🚀 Process Camera-to-Care Workflow",
                type="primary",
                use_container_width=True
            )
        else:
            process_btn = False
    
    with col2:
        st.markdown("## 📊 Workflow Status")
        status_placeholder = st.empty()
    
    # Process workflow
    if process_btn and uploaded_file:
        image_base64 = encode_image(uploaded_file)
        
        # Initialize state
        initial_state = {
            "image_base64": image_base64,
            "patient_id": patient_id,
            "facility_address": resident['facility_address'],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_steps": [],
            "requires_human_review": False
        }
        
        # Run workflow
        with st.spinner("🔄 Running Camera-to-Care workflow..."):
            workflow = create_camera_to_care_workflow(api_key)
            
            try:
                final_state = workflow.invoke(initial_state)
                
                # Display results
                st.markdown("---")
                st.markdown("## ✅ Workflow Complete!")
                
                # Summary metrics
                col_a, col_b, col_c, col_d = st.columns(4)
                
                with col_a:
                    st.metric(
                        "Injury Classification",
                        final_state.get('injury_type', 'N/A').replace('_', ' ').title(),
                        delta=final_state.get('severity', 'N/A').upper()
                    )
                
                with col_b:
                    coverage = final_state.get('coverage_percentage', 0)
                    st.metric(
                        "Insurance Coverage",
                        f"{coverage}%",
                        delta="Covered ✓" if final_state.get('is_covered') else "Not Covered ✗"
                    )
                
                with col_c:
                    match_score = final_state.get('overall_match_score', 0)
                    st.metric(
                        "Caregiver Match",
                        f"{match_score:.1f}/100",
                        delta=final_state.get('matched_caregiver_name', 'N/A')
                    )
                
                with col_d:
                    st.metric(
                        "Visit Status",
                        "Scheduled ✓" if final_state.get('visit_scheduled') else "Pending",
                        delta=final_state.get('visit_datetime', 'N/A')
                    )
                
                # Detailed tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "🔍 Classification",
                    "💳 Insurance",
                    "👥 Caregiver Match",
                    "📅 Visit Details",
                    "📊 Complete Summary"
                ])
                
                with tab1:
                    st.markdown("### Injury Classification Results")
                    
                    col_x, col_y = st.columns(2)
                    
                    with col_x:
                        st.markdown("**Classification:**")
                        st.info(f"""
                        **Type:** {final_state.get('injury_type', 'N/A').replace('_', ' ').title()}  
                        **Severity:** {final_state.get('severity', 'N/A').upper()}  
                        """)
                    
                    with col_y:
                        st.markdown("**Clinical Description:**")
                        st.write(final_state.get('clinical_description', 'N/A'))
                
                with tab2:
                    st.markdown("### Insurance Verification Results")
                    
                    if final_state.get('is_covered'):
                        st.success("✅ Service is COVERED by insurance")
                    else:
                        st.error("❌ Service is NOT COVERED by insurance")
                    
                    col_ins1, col_ins2 = st.columns(2)
                    
                    with col_ins1:
                        st.markdown("**Insurance Details:**")
                        st.info(f"""
                        **Provider:** {final_state.get('insurance_provider', 'N/A')}  
                        **Plan:** {final_state.get('insurance_plan', 'N/A')}  
                        **Coverage:** {final_state.get('coverage_percentage', 0)}%  
                        **Copay:** ${final_state.get('copay_amount', 0):.2f}
                        """)
                    
                    with col_ins2:
                        st.markdown("**Explanation of Benefits (EOB):**")
                        eob = final_state.get('eob_summary', 'N/A')
                        st.text_area("EOB Summary", eob, height=200)
                
                with tab3:
                    st.markdown("### Caregiver Matching Analysis")
                    
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
                            # Color code based on score
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
                    
                    # Overall score
                    overall = final_state.get('overall_match_score', 0)
                    st.markdown(f"### Overall Match Score: **{overall:.1f}/100**")
                    st.progress(overall / 100)
                    
                    # Distance
                    distance = final_state.get('caregiver_distance_miles', 0)
                    st.info(f"📍 Distance to facility: **{distance:.1f} miles**")
                    
                    # Caregiver details
                    cg_id = final_state.get('matched_caregiver_id', '')
                    if cg_id and cg_id in CAREGIVER_PROFILES:
                        caregiver = CAREGIVER_PROFILES[cg_id]
                        st.markdown("#### Caregiver Profile")
                        st.json({
                            "Name": caregiver['name'],
                            "Skills": caregiver['skills'],
                            "Location": caregiver['location'],
                            "Avg Rating": caregiver['avg_feedback_rating'],
                            "Total Reviews": caregiver['total_reviews']
                        })
                
                with tab4:
                    st.markdown("### Visit Scheduling Details")
                    
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
                            
                            # Calculate estimated costs
                            coverage_pct = final_state.get('coverage_percentage', 0)
                            copay = final_state.get('copay_amount', 0)
                            
                            # Estimated service cost (simplified)
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
                    
                    # Create comprehensive summary
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
                            "Description": final_state.get('clinical_description')
                        },
                        "Insurance": {
                            "Provider": final_state.get('insurance_provider'),
                            "Plan": final_state.get('insurance_plan'),
                            "Covered": final_state.get('is_covered'),
                            "Coverage %": final_state.get('coverage_percentage'),
                            "Copay": final_state.get('copay_amount')
                        },
                        "Caregiver Match": {
                            "Name": final_state.get('matched_caregiver_name'),
                            "Overall Score": final_state.get('overall_match_score'),
                            "Skills Score": final_state.get('caregiver_skills_score'),
                            "Proximity Score": final_state.get('proximity_score'),
                            "Feedback Score": final_state.get('feedback_score'),
                            "Calendar Score": final_state.get('calendar_score'),
                            "Distance": final_state.get('caregiver_distance_miles')
                        },
                        "Visit": {
                            "Scheduled": final_state.get('visit_scheduled'),
                            "Visit ID": final_state.get('visit_stub_id'),
                            "Date/Time": final_state.get('visit_datetime'),
                            "Procedure Code": final_state.get('procedure_code')
                        },
                        "Workflow": {
                            "Steps Completed": final_state.get('completed_steps', []),
                            "Current Step": final_state.get('current_step'),
                            "Requires Review": final_state.get('requires_human_review', False)
                        }
                    }
                    
                    st.json(summary)
                    
                    # Download summary
                    summary_json = json.dumps(summary, indent=2)
                    st.download_button(
                        "📥 Download Complete Summary (JSON)",
                        summary_json,
                        file_name=f"camera_to_care_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"Error processing workflow: {str(e)}")
                st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #718096;'>
            <p>🏥 Camera-to-Care System | Multi-Agent AI with LangGraph<br>
            Insurance Verification • Caregiver Matching • Automated Scheduling</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


# =====================================
# INSTALLATION & RUN
# =====================================
"""
SETUP:
pip install streamlit langchain langchain-openai langgraph pillow openai

RUN:
streamlit run camera_to_care_revised.py

FEATURES:
✅ Image-based injury classification (GPT-4o Vision)
✅ Insurance eligibility verification with EOB generation
✅ Multi-criteria caregiver matching (4 scoring algorithms)
✅ Automated visit scheduling with CPT codes
✅ Complete audit trail and JSON export
✅ LangGraph workflow with conditional routing

SCORING WEIGHTS:
• Skills Match: 40%
• Proximity: 25%
• Feedback Rating: 20%
• Calendar Availability: 15%

SIMULATED MCPs:
• Distance calculation (would use Google Maps API)
• Caregiver calendar access
• Insurance eligibility verification
• Resident profile database

NEXT ENHANCEMENTS:
• Real MCP integrations (Google Maps, calendar APIs)
• Voice input with WhisperFlow
• SMS notifications via Twilio
• Real-time audit logging
• Mobile app integration
""""""
Camera-to-Care: Complete Multi-Agent System
From Image Upload → Insurance Verification → Caregiver Matching → Scheduling

Revised Architecture with LangGraph + MCPs
"""

import streamlit as st
import base64
import io
import json
from datetime import datetime, timedelta
from typing import TypedDict, Literal, List, Annotated, Optional
import operator
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
import os

# =====================================
# STATE DEFINITION
# =====================================

class CareEncounterState(TypedDict):
    """Complete state for Camera-to-Care workflow"""
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
    caregiver_skills_score: float
    proximity_score: float
    feedback_score: float
    calendar_score: float
    overall_match_score: float
    caregiver_distance_miles: float
    
    # Step 5: Scheduling
    visit_scheduled: bool
    visit_datetime: str
    visit_stub_id: str
    procedure_code: str
    
    # Process tracking
    current_step: str
    completed_steps: Annotated[List[str], operator.add]
    requires_human_review: bool


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
        "location": "321 Broadway, Oakland, CA 94612",
        "avg_feedback_rating": 4.6,
        "total_reviews": 89,
        "calendar_url": "cal-cg002"
    },
    "CG-003": {
        "name": "Dr. Emily Martinez, MD",
        "skills": ["wound_care", "IV_therapy", "emergency_care", "surgical_wound_care"],
        "location": "555 California Street, San Francisco, CA 94104",
        "avg_feedback_rating": 4.9,
        "total_reviews": 234,
        "calendar_url": "cal-cg003"
    }
}

# Mock Calendar Availability (simulating MCP)
CAREGIVER_CALENDARS = {
    "cal-cg001": {
        "available_slots": [
            "2024-11-08 10:00",
            "2024-11-08 14:00",
            "2024-11-09 09:00"
        ]
    },
    "cal-cg002": {
        "available_slots": [
            "2024-11-08 11:00",
            "2024-11-08 15:00"
        ]
    },
    "cal-cg003": {
        "available_slots": [
            "2024-11-08 16:00",
            "2024-11-09 10:00"
        ]
    }
}


# =====================================
# AGENT 1: INJURY CLASSIFIER
# =====================================

class InjuryClassifierAgent:
    """Classifies injury type and severity from image"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
    
    def classify(self, image_base64: str) -> dict:
        """Analyze image and classify injury"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a clinical AI assistant specializing in injury classification for elderly care.

Analyze the provided image and determine:
1. **Injury Type**: pressure_ulcer, skin_tear, bruise, rash, burn, surgical_wound, or other
2. **Severity**: mild, moderate, severe, or emergency
3. **Clinical Description**: Detailed description including size, stage, location

Return ONLY valid JSON format:
{{
    "injury_type": "pressure_ulcer",
    "severity": "moderate",
    "clinical_description": "3cm stage 2 pressure ulcer on left heel with surrounding erythema"
}}"""),
            ("user", [
                {"type": "text", "text": "Classify this injury:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ])
        ])
        
        response = self.llm.invoke(prompt.format_messages())
        
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except:
            return {
                "injury_type": "unknown",
                "severity": "moderate",
                "clinical_description": "Unable to classify - requires human review"
            }


# =====================================
# AGENT 2: INSURANCE VERIFICATION
# =====================================

class InsuranceVerificationAgent:
    """Verifies insurance eligibility and coverage"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
    
    def verify_coverage(self, patient_id: str, injury_type: str, severity: str) -> dict:
        """Check insurance coverage for the injury"""
        
        # Step 1: Read resident profile
        resident = RESIDENT_PROFILES.get(patient_id, {})
        if not resident:
            return {
                "is_covered": False,
                "error": "Patient not found"
            }
        
        insurance = resident.get("insurance", {})
        provider = insurance.get("provider", "Unknown")
        
        # Step 2: Read payer terms (simulating PDF parsing with MCP)
        service_type = self._map_injury_to_service(injury_type, severity)
        payer_terms = PAYER_TERMS.get(provider, {}).get(service_type, {})
        
        if not payer_terms:
            return {
                "insurance_provider": provider,
                "insurance_plan": insurance.get("plan", "Unknown"),
                "is_covered": False,
                "coverage_percentage": 0,
                "copay_amount": 0,
                "eob_summary": "Service not covered under current plan"
            }
        
        # Step 3: Generate EOB (Explanation of Benefits)
        eob = self._generate_eob(
            patient_id,
            provider,
            insurance.get("plan"),
            service_type,
            payer_terms
        )
        
        return {
            "insurance_provider": provider,
            "insurance_plan": insurance.get("plan", "Unknown"),
            "is_covered": payer_terms.get("covered", False),
            "coverage_percentage": payer_terms.get("coverage_percentage", 0),
            "copay_amount": payer_terms.get("copay", 0),
            "eob_summary": eob
        }
    
    def _map_injury_to_service(self, injury_type: str, severity: str) -> str:
        """Map injury type to billable service"""
        if injury_type in ["pressure_ulcer", "surgical_wound"]:
            return "wound_care"
        return "routine_visit"
    
    def _generate_eob(self, patient_id: str, provider: str, plan: str, 
                      service: str, terms: dict) -> str:
        """Generate Explanation of Benefits summary"""
        
        covered = "COVERED" if terms.get("covered") else "NOT COVERED"
        coverage = terms.get("coverage_percentage", 0)
        copay = terms.get("copay", 0)
        
        eob = f"""
EXPLANATION OF BENEFITS (EOB)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patient: {patient_id}
Insurance: {provider} - {plan}
Service: {service.replace('_', ' ').title()}
Status: {covered}

Coverage Details:
• Plan Pays: {coverage}%
• Patient Copay: ${copay:.2f}
• Requires Pre-Auth: {'Yes' if terms.get('requires_preauth') else 'No'}

Notes: {terms.get('notes', 'Standard coverage applies')}
"""
        return eob.strip()


# =====================================
# AGENT 3: CAREGIVER MATCHER
# =====================================

class CaregiverMatcherAgent:
    """Matches optimal caregiver based on multiple criteria"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.2
        )
    
    def match_caregiver(self, injury_type: str, severity: str, 
                        facility_address: str, patient_id: str) -> dict:
        """Find best caregiver match using 4 scoring criteria"""
        
        best_match = None
        best_score = 0
        
        for cg_id, caregiver in CAREGIVER_PROFILES.items():
            # Calculate all 4 scores
            skills_score = self._calculate_skills_score(
                caregiver["skills"], injury_type, severity
            )
            
            proximity_score = self._calculate_proximity_score(
                caregiver["location"], facility_address
            )
            
            feedback_score = self._calculate_feedback_score(
                caregiver["avg_feedback_rating"]
            )
            
            calendar_score = self._calculate_calendar_score(
                caregiver["calendar_url"]
            )
            
            # Overall weighted score
            overall_score = (
                skills_score * 0.40 +      # 40% weight on skills
                proximity_score * 0.25 +    # 25% weight on proximity
                feedback_score * 0.20 +     # 20% weight on feedback
                calendar_score * 0.15       # 15% weight on availability
            )
            
            if overall_score > best_score:
                best_score = overall_score
                best_match = {
                    "caregiver_id": cg_id,
                    "caregiver_name": caregiver["name"],
                    "skills_score": skills_score,
                    "proximity_score": proximity_score,
                    "feedback_score": feedback_score,
                    "calendar_score": calendar_score,
                    "overall_score": overall_score,
                    "distance_miles": self._get_distance(
                        caregiver["location"], facility_address
                    ),
                    "calendar_url": caregiver["calendar_url"]
                }
        
        return best_match or {}
    
    def _calculate_skills_score(self, caregiver_skills: List[str], 
                                 injury_type: str, severity: str) -> float:
        """Score based on skill match (0-100)"""
        
        required_skills = {
            "pressure_ulcer": ["wound_care"],
            "surgical_wound": ["wound_care", "surgical_wound_care"],
            "skin_tear": ["basic_wound_care"],
        }
        
        needed = required_skills.get(injury_type, ["basic_wound_care"])
        
        if severity == "severe":
            needed.append("IV_therapy")
        if severity == "emergency":
            needed.append("emergency_care")
        
        matched = sum(1 for skill in needed if skill in caregiver_skills)
        score = (matched / len(needed)) * 100 if needed else 50
        
        return min(score, 100)
    
    def _calculate_proximity_score(self, cg_location: str, 
                                     resident_location: str) -> float:
        """Score based on distance (0-100, closer = higher)"""
        
        # Simulate MCP call to get distance
        distance = self._get_distance(cg_location, resident_location)
        
        # Score: 100 for <1 mile, decreasing to 0 at 20+ miles
        if distance < 1:
            return 100
        elif distance < 5:
            return 100 - (distance - 1) * 10  # 90-100 for 1-5 miles
        elif distance < 10:
            return 50 - (distance - 5) * 5    # 50-75 for 5-10 miles
        else:
            return max(0, 50 - (distance - 10) * 5)  # 0-50 for 10+ miles
    
    def _get_distance(self, location1: str, location2: str) -> float:
        """Simulate MCP distance calculation"""
        # In real implementation, this would call Google Maps API or similar
        # For demo, we'll use simple city-based distances
        
        if "San Francisco" in location1 and "San Francisco" in location2:
            return 2.5
        elif "Oakland" in location1 and "Oakland" in location2:
            return 3.0
        elif ("San Francisco" in location1 and "Oakland" in location2) or \
             ("Oakland" in location1 and "San Francisco" in location2):
            return 12.5
        else:
            return 8.0
    
    def _calculate_feedback_score(self, avg_rating: float) -> float:
        """Score based on feedback rating (0-100)"""
        # Convert 0-5 star rating to 0-100 scale
        return (avg_rating / 5.0) * 100
    
    def _calculate_calendar_score(self, calendar_url: str) -> float:
        """Score based on availability (0-100)"""
        # Simulate MCP call to caregiver calendar
        calendar = CAREGIVER_CALENDARS.get(calendar_url, {})
        available_slots = calendar.get("available_slots", [])
        
        # More available slots = higher score
        if len(available_slots) >= 3:
            return 100
        elif len(available_slots) == 2:
            return 70
        elif len(available_slots) == 1:
            return 40
        else:
            return 10


# =====================================
# AGENT 4: VISIT SCHEDULER
# =====================================

class VisitSchedulerAgent:
    """Schedules visit and creates billing stub"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
    
    def schedule_visit(self, caregiver_calendar: str, injury_type: str, 
                       severity: str) -> dict:
        """Create visit stub with procedure code"""
        
        # Get first available slot
        calendar = CAREGIVER_CALENDARS.get(caregiver_calendar, {})
        available_slots = calendar.get("available_slots", [])
        
        if not available_slots:
            return {
                "visit_scheduled": False,
                "error": "No available slots"
            }
        
        visit_datetime = available_slots[0]
        
        # Assign procedure code (CPT code)
        procedure_code = self._get_procedure_code(injury_type, severity)
        
        # Create visit stub
        visit_stub = {
            "visit_scheduled": True,
            "visit_datetime": visit_datetime,
            "visit_stub_id": f"VISIT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "procedure_code": procedure_code,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        return visit_stub
    
    def _get_procedure_code(self, injury_type: str, severity: str) -> str:
        """Map injury to CPT procedure code"""
        
        codes = {
            "pressure_ulcer": {
                "mild": "99213",      # Office visit, level 3
                "moderate": "97597",  # Debridement
                "severe": "97602",    # Wound care with selective debridement
                "emergency": "99285"  # Emergency dept visit
            },
            "surgical_wound": {
                "mild": "99213",
                "moderate": "97597",
                "severe": "97598",
                "emergency": "99285"
            },
            "skin_tear": {
                "mild": "12001",  # Simple wound repair
                "moderate": "12002",
                "severe": "12004"
            }
        }
        
        return codes.get(injury_type, {}).get(severity, "99213")


# =====================================
# LANGGRAPH WORKFLOW
# =====================================

def create_camera_to_care_workflow(api_key: str):
    """Build the complete LangGraph workflow"""
    
    # Initialize agents
    injury_classifier = InjuryClassifierAgent(api_key)
    insurance_verifier = InsuranceVerificationAgent(api_key)
    caregiver_matcher = CaregiverMatcherAgent(api_key)
    visit_scheduler = VisitSchedulerAgent(api_key)
    
    # Define workflow nodes
    def classify_injury_node(state: CareEncounterState) -> CareEncounterState:
        """Step 2: Classify injury type and severity"""
        st.write("🔍 **Step 2:** Classifying injury...")
        
        classification = injury_classifier.classify(state['image_base64'])
        
        return {
            **state,
            "injury_type": classification['injury_type'],
            "severity": classification['severity'],
            "clinical_description": classification['clinical_description'],
            "current_step": "classification",
            "completed_steps": ["classification"]
        }
    
    def verify_insurance_node(state: CareEncounterState) -> CareEncounterState:
        """Step 3: Verify insurance coverage"""
        st.write("💳 **Step 3:** Verifying insurance coverage...")
        
        coverage = insurance_verifier.verify_coverage(
            state['patient_id'],
            state['injury_type'],
            state['severity']
        )
        
        return {
            **state,
            **coverage,
            "current_step": "insurance",
            "completed_steps": ["insurance"]
        }
    
    def coverage_router(state: CareEncounterState) -> str:
        """Route based on insurance coverage"""
        if not state.get('is_covered', False):
            return "coverage_denied"
        return "match_caregiver"
    
    def coverage_denied_node(state: CareEncounterState) -> CareEncounterState:
        """Handle denied coverage"""
        st.error("⚠️ Insurance does not cover this service")
        
        return {
            **state,
            "requires_human_review": True,
            "current_step": "coverage_denied",
            "completed_steps": ["coverage_denied"]
        }
    
    def match_caregiver_node(state: CareEncounterState) -> CareEncounterState:
        """Step 4: Match optimal caregiver"""
        st.write("🔎 **Step 4:** Matching caregiver...")
        st.write("   • Analyzing skills...")
        st.write("   • Calculating proximity...")
        st.write("   • Checking feedback scores...")
        st.write("   • Reviewing calendar availability...")
        
        match = caregiver_matcher.match_caregiver(
            state['injury_type'],
            state['severity'],
            state['facility_address'],
            state['patient_id']
        )
        
        return {
            **state,
            "matched_caregiver_id": match.get('caregiver_id', ''),
            "matched_caregiver_name": match.get('caregiver_name', ''),
            "caregiver_skills_score": match.get('skills_score', 0),
            "proximity_score": match.get('proximity_score', 0),
            "feedback_score": match.get('feedback_score', 0),
            "calendar_score": match.get('calendar_score', 0),
            "overall_match_score": match.get('overall_score', 0),
            "caregiver_distance_miles": match.get('distance_miles', 0),
            "current_step": "matching",
            "completed_steps": ["matching"]
        }
    
    def schedule_visit_node(state: CareEncounterState) -> CareEncounterState:
        """Step 5: Schedule the visit"""
        st.write("📅 **Step 5:** Scheduling visit...")
        
        # Get caregiver calendar URL
        caregiver_id = state.get('matched_caregiver_id', '')
        calendar_url = CAREGIVER_PROFILES.get(caregiver_id, {}).get('calendar_url', '')
        
        visit = visit_scheduler.schedule_visit(
            calendar_url,
            state['injury_type'],
            state['severity']
        )
        
        return {
            **state,
            **visit,
            "current_step": "scheduling",
            "completed_steps": ["scheduling"]
        }
    
    # Build graph
    workflow = StateGraph(CareEncounterState)
    
    # Add nodes
    workflow.add_node("classify_injury", classify_injury_node)
    workflow.add_node("verify_insurance", verify_insurance_node)
    workflow.add_node("coverage_denied", coverage_denied_node)
    workflow.add_node("match_caregiver", match_caregiver_node)
    workflow.add_node("schedule_visit", schedule_visit_node)
    
    # Define flow
    workflow.set_entry_point("classify_injury")
    workflow.add_edge("classify_injury", "verify_insurance")
    workflow.add_conditional_edges(
        "verify_insurance",
        coverage_router,
        {
            "coverage_denied": "coverage_denied",
            "match_caregiver": "match_caregiver"
        }
    )
    workflow.add_edge("coverage_denied", END)
    workflow.add_edge("match_caregiver", "schedule_visit")
    workflow.add_edge("schedule_visit", END)
    
    return workflow.compile()


# =====================================
# STREAMLIT UI
# =====================================

def encode_image(image_file):
    """Encode uploaded image to base64"""
    image = Image.open(image_file)
    max_size = (1024, 1024)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


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
            font-size: 2.5rem;
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
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Camera-to-Care System</h1>', unsafe_allow_html=True)
    st.markdown("### *From Image → Insurance → Caregiver Match → Visit Scheduled*")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x120/2c5aa0/ffffff?text=Camera-to-Care", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### 🔐 Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", "")
        )
        
        st.markdown("---")
        st.markdown("### 📊 Workflow Steps")
        st.markdown("""
        1. **📸 Upload** - Image capture
        2. **🔍 Classify** - Injury type & severity
        3. **💳 Verify** - Insurance coverage
        4. **👥 Match** - Optimal caregiver
        5. **📅 Schedule** - Book visit
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 Matching Criteria")
        st.info("""
        **40%** Skills Match  
        **25%** Proximity  
        **20%** Feedback Rating  
        **15%** Calendar Availability
        """)
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key to continue")
        st.stop()
    
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
        **Patient:** {resident['name']}  
        **Age:** {resident['age']}  
        **Insurance:** {resident['insurance']['provider']}  
        **Location:** {resident['facility_address']}
        """)
        
        # Image upload
        uploaded_file = st.file_uploader(
            "Upload injury image",
            type=['jpg', 'jpeg', 'png']
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            process_btn = st.button(
                "🚀 Process Camera-to-Care Workflow",
                type="primary",
                use_container_width=True
            )
        else:
            process_btn = False
    
    with col2:
        st.markdown("## 📊 Workflow Status")
        status_placeholder = st.empty()
    
    # Process workflow
    if process_btn and uploaded_file:
        image_base64 = encode_image(uploaded_file)
        
        # Initialize state
        initial_state = {
            "image_base64": image_base64,
            "patient_id": patient_id,
            "facility_address": resident['facility_address'],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_steps": [],
            "requires_human_review": False
        }
        
        # Run workflow
        with st.spinner("🔄 Running Camera-to-Care workflow..."):
            workflow = create_camera_to_care_workflow(api_key)
            
            try:
                final_state = workflow.invoke(initial_state)
                
                # Display results
                st.markdown("---")
                st.markdown("## ✅ Workflow Complete!")
                
                # Summary metrics
                col_a, col_b, col_c, col_d = st.columns(4)
                
                with col_a:
                    st.metric(
                        "Injury Classification",
                        final_state.get('injury_type', 'N/A').replace('_', ' ').title(),
                        delta=final_state.get('severity', 'N/A').upper()
                    )
                
                with col_b:
                    coverage = final_state.get('coverage_percentage', 0)
                    st.metric(
                        "Insurance Coverage",
                        f"{coverage}%",
                        delta="Covered ✓" if final_state.get('is_covered') else "Not Covered ✗"
                    )
                
                with col_c:
                    match_score = final_state.get('overall_match_score', 0)
                    st.metric(
                        "Caregiver Match",
                        f"{match_score:.1f}/100",
                        delta=final_state.get('matched_caregiver_name', 'N/A')
                    )
                
                with col_d:
                    st.metric(
                        "Visit Status",
                        "Scheduled ✓" if final_state.get('visit_scheduled') else "Pending",
                        delta=final_state.get('visit_datetime', 'N/A')
                    )
                
                # Detailed tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "🔍 Classification",
                    "💳 Insurance",
                    "👥 Caregiver Match",
                    "📅 Visit Details",
                    "📊 Complete Summary"
                ])
                
                with tab1:
                    st.markdown("### Injury Classification Results")
                    
                    col_x, col_y = st.columns(2)
                    
                    with col_x:
                        st.markdown("**Classification:**")
                        st.info(f"""
                        **Type:** {final_state.get('injury_type', 'N/A').replace('_', ' ').title()}  
                        **Severity:** {final_state.get('severity', 'N/A').upper()}  
                        """)
                    
                    with col_y:
                        st.markdown("**Clinical Description:**")
                        st.write(final_state.get('clinical_description', 'N/A'))
                
                with tab2:
                    st.markdown("### Insurance Verification Results")
                    
                    if final_state.get('is_covered'):
                        st.success("✅ Service is COVERED by insurance")
                    else:
                        st.error("❌ Service is NOT COVERED by insurance")
                    
                    col_ins1, col_ins2 = st.columns(2)
                    
                    with col_ins1:
                        st.markdown("**Insurance Details:**")
                        st.info(f"""
                        **Provider:** {final_state.get('insurance_provider', 'N/A')}  
                        **Plan:** {final_state.get('insurance_plan', 'N/A')}  
                        **Coverage:** {final_state.get('coverage_percentage', 0)}%  
                        **Copay:** ${final_state.get('copay_amount', 0):.2f}
                        """)
                    
                    with col_ins2:
                        st.markdown("**Explanation of Benefits (EOB):**")
                        eob = final_state.get('eob_summary', 'N/A')
                        st.text_area("EOB Summary", eob, height=200)
                
                with tab3:
                    st.markdown("### Caregiver Matching Analysis")
                    
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
                            # Color code based on score
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
                    
                    # Overall score
                    overall = final_state.get('overall_match_score', 0)
                    st.markdown(f"### Overall Match Score: **{overall:.1f}/100**")
                    st.progress(overall / 100)
                    
                    # Distance
                    distance = final_state.get('caregiver_distance_miles', 0)
                    st.info(f"📍 Distance to facility: **{distance:.1f} miles**")
                    
                    # Caregiver details
                    cg_id = final_state.get('matched_caregiver_id', '')
                    if cg_id and cg_id in CAREGIVER_PROFILES:
                        caregiver = CAREGIVER_PROFILES[cg_id]
                        st.markdown("#### Caregiver Profile")
                        st.json({
                            "Name": caregiver['name'],
                            "Skills": caregiver['skills'],
                            "Location": caregiver['location'],
                            "Avg Rating": caregiver['avg_feedback_rating'],
                            "Total Reviews": caregiver['total_reviews']
                        })
                
                with tab4:
                    st.markdown("### Visit Scheduling Details")
                    
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
                            
                            # Calculate estimated costs
                            coverage_pct = final_state.get('coverage_percentage', 0)
                            copay = final_state.get('copay_amount', 0)
                            
                            # Estimated service cost (simplified)
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
                    
                    # Create comprehensive summary
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
                            "Description": final_state.get('clinical_description')
                        },
                        "Insurance": {
                            "Provider": final_state.get('insurance_provider'),
                            "Plan": final_state.get('insurance_plan'),
                            "Covered": final_state.get('is_covered'),
                            "Coverage %": final_state.get('coverage_percentage'),
                            "Copay": final_state.get('copay_amount')
                        },
                        "Caregiver Match": {
                            "Name": final_state.get('matched_caregiver_name'),
                            "Overall Score": final_state.get('overall_match_score'),
                            "Skills Score": final_state.get('caregiver_skills_score'),
                            "Proximity Score": final_state.get('proximity_score'),
                            "Feedback Score": final_state.get('feedback_score'),
                            "Calendar Score": final_state.get('calendar_score'),
                            "Distance": final_state.get('caregiver_distance_miles')
                        },
                        "Visit": {
                            "Scheduled": final_state.get('visit_scheduled'),
                            "Visit ID": final_state.get('visit_stub_id'),
                            "Date/Time": final_state.get('visit_datetime'),
                            "Procedure Code": final_state.get('procedure_code')
                        },
                        "Workflow": {
                            "Steps Completed": final_state.get('completed_steps', []),
                            "Current Step": final_state.get('current_step'),
                            "Requires Review": final_state.get('requires_human_review', False)
                        }
                    }
                    
                    st.json(summary)
                    
                    # Download summary
                    summary_json = json.dumps(summary, indent=2)
                    st.download_button(
                        "📥 Download Complete Summary (JSON)",
                        summary_json,
                        file_name=f"camera_to_care_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"Error processing workflow: {str(e)}")
                st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #718096;'>
            <p>🏥 Camera-to-Care System | Multi-Agent AI with LangGraph<br>
            Insurance Verification • Caregiver Matching • Automated Scheduling</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


# =====================================
# INSTALLATION & RUN
# =====================================
"""
SETUP:
pip install streamlit langchain langchain-openai langgraph pillow openai

RUN:
streamlit run camera_to_care_revised.py

FEATURES:
✅ Image-based injury classification (GPT-4o Vision)
✅ Insurance eligibility verification with EOB generation
✅ Multi-criteria caregiver matching (4 scoring algorithms)
✅ Automated visit scheduling with CPT codes
✅ Complete audit trail and JSON export
✅ LangGraph workflow with conditional routing

SCORING WEIGHTS:
• Skills Match: 40%
• Proximity: 25%
• Feedback Rating: 20%
• Calendar Availability: 15%

SIMULATED MCPs:
• Distance calculation (would use Google Maps API)
• Caregiver calendar access
• Insurance eligibility verification
• Resident profile database

NEXT ENHANCEMENTS:
• Real MCP integrations (Google Maps, calendar APIs)
• Voice input with WhisperFlow
• SMS notifications via Twilio
• Real-time audit logging
• Mobile app integration
""""""
Camera-to-Care: Complete Multi-Agent System
From Image Upload → Insurance Verification → Caregiver Matching → Scheduling

Revised Architecture with LangGraph + MCPs
"""

import streamlit as st
import base64
import io
import json
from datetime import datetime, timedelta
from typing import TypedDict, Literal, List, Annotated, Optional
import operator
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
import os

# =====================================
# STATE DEFINITION
# =====================================

class CareEncounterState(TypedDict):
    """Complete state for Camera-to-Care workflow"""
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
    caregiver_skills_score: float
    proximity_score: float
    feedback_score: float
    calendar_score: float
    overall_match_score: float
    caregiver_distance_miles: float
    
    # Step 5: Scheduling
    visit_scheduled: bool
    visit_datetime: str
    visit_stub_id: str
    procedure_code: str
    
    # Process tracking
    current_step: str
    completed_steps: Annotated[List[str], operator.add]
    requires_human_review: bool


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
        "location": "321 Broadway, Oakland, CA 94612",
        "avg_feedback_rating": 4.6,
        "total_reviews": 89,
        "calendar_url": "cal-cg002"
    },
    "CG-003": {
        "name": "Dr. Emily Martinez, MD",
        "skills": ["wound_care", "IV_therapy", "emergency_care", "surgical_wound_care"],
        "location": "555 California Street, San Francisco, CA 94104",
        "avg_feedback_rating": 4.9,
        "total_reviews": 234,
        "calendar_url": "cal-cg003"
    }
}

# Mock Calendar Availability (simulating MCP)
CAREGIVER_CALENDARS = {
    "cal-cg001": {
        "available_slots": [
            "2024-11-08 10:00",
            "2024-11-08 14:00",
            "2024-11-09 09:00"
        ]
    },
    "cal-cg002": {
        "available_slots": [
            "2024-11-08 11:00",
            "2024-11-08 15:00"
        ]
    },
    "cal-cg003": {
        "available_slots": [
            "2024-11-08 16:00",
            "2024-11-09 10:00"
        ]
    }
}


# =====================================
# AGENT 1: INJURY CLASSIFIER
# =====================================

class InjuryClassifierAgent:
    """Classifies injury type and severity from image"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
    
    def classify(self, image_base64: str) -> dict:
        """Analyze image and classify injury"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a clinical AI assistant specializing in injury classification for elderly care.

Analyze the provided image and determine:
1. **Injury Type**: pressure_ulcer, skin_tear, bruise, rash, burn, surgical_wound, or other
2. **Severity**: mild, moderate, severe, or emergency
3. **Clinical Description**: Detailed description including size, stage, location

Return ONLY valid JSON format:
{{
    "injury_type": "pressure_ulcer",
    "severity": "moderate",
    "clinical_description": "3cm stage 2 pressure ulcer on left heel with surrounding erythema"
}}"""),
            ("user", [
                {"type": "text", "text": "Classify this injury:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ])
        ])
        
        response = self.llm.invoke(prompt.format_messages())
        
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except:
            return {
                "injury_type": "unknown",
                "severity": "moderate",
                "clinical_description": "Unable to classify - requires human review"
            }


# =====================================
# AGENT 2: INSURANCE VERIFICATION
# =====================================

class InsuranceVerificationAgent:
    """Verifies insurance eligibility and coverage"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
    
    def verify_coverage(self, patient_id: str, injury_type: str, severity: str) -> dict:
        """Check insurance coverage for the injury"""
        
        # Step 1: Read resident profile
        resident = RESIDENT_PROFILES.get(patient_id, {})
        if not resident:
            return {
                "is_covered": False,
                "error": "Patient not found"
            }
        
        insurance = resident.get("insurance", {})
        provider = insurance.get("provider", "Unknown")
        
        # Step 2: Read payer terms (simulating PDF parsing with MCP)
        service_type = self._map_injury_to_service(injury_type, severity)
        payer_terms = PAYER_TERMS.get(provider, {}).get(service_type, {})
        
        if not payer_terms:
            return {
                "insurance_provider": provider,
                "insurance_plan": insurance.get("plan", "Unknown"),
                "is_covered": False,
                "coverage_percentage": 0,
                "copay_amount": 0,
                "eob_summary": "Service not covered under current plan"
            }
        
        # Step 3: Generate EOB (Explanation of Benefits)
        eob = self._generate_eob(
            patient_id,
            provider,
            insurance.get("plan"),
            service_type,
            payer_terms
        )
        
        return {
            "insurance_provider": provider,
            "insurance_plan": insurance.get("plan", "Unknown"),
            "is_covered": payer_terms.get("covered", False),
            "coverage_percentage": payer_terms.get("coverage_percentage", 0),
            "copay_amount": payer_terms.get("copay", 0),
            "eob_summary": eob
        }
    
    def _map_injury_to_service(self, injury_type: str, severity: str) -> str:
        """Map injury type to billable service"""
        if injury_type in ["pressure_ulcer", "surgical_wound"]:
            return "wound_care"
        return "routine_visit"
    
    def _generate_eob(self, patient_id: str, provider: str, plan: str, 
                      service: str, terms: dict) -> str:
        """Generate Explanation of Benefits summary"""
        
        covered = "COVERED" if terms.get("covered") else "NOT COVERED"
        coverage = terms.get("coverage_percentage", 0)
        copay = terms.get("copay", 0)
        
        eob = f"""
EXPLANATION OF BENEFITS (EOB)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Patient: {patient_id}
Insurance: {provider} - {plan}
Service: {service.replace('_', ' ').title()}
Status: {covered}

Coverage Details:
• Plan Pays: {coverage}%
• Patient Copay: ${copay:.2f}
• Requires Pre-Auth: {'Yes' if terms.get('requires_preauth') else 'No'}

Notes: {terms.get('notes', 'Standard coverage applies')}
"""
        return eob.strip()


# =====================================
# AGENT 3: CAREGIVER MATCHER
# =====================================

class CaregiverMatcherAgent:
    """Matches optimal caregiver based on multiple criteria"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.2
        )
    
    def match_caregiver(self, injury_type: str, severity: str, 
                        facility_address: str, patient_id: str) -> dict:
        """Find best caregiver match using 4 scoring criteria"""
        
        best_match = None
        best_score = 0
        
        for cg_id, caregiver in CAREGIVER_PROFILES.items():
            # Calculate all 4 scores
            skills_score = self._calculate_skills_score(
                caregiver["skills"], injury_type, severity
            )
            
            proximity_score = self._calculate_proximity_score(
                caregiver["location"], facility_address
            )
            
            feedback_score = self._calculate_feedback_score(
                caregiver["avg_feedback_rating"]
            )
            
            calendar_score = self._calculate_calendar_score(
                caregiver["calendar_url"]
            )
            
            # Overall weighted score
            overall_score = (
                skills_score * 0.40 +      # 40% weight on skills
                proximity_score * 0.25 +    # 25% weight on proximity
                feedback_score * 0.20 +     # 20% weight on feedback
                calendar_score * 0.15       # 15% weight on availability
            )
            
            if overall_score > best_score:
                best_score = overall_score
                best_match = {
                    "caregiver_id": cg_id,
                    "caregiver_name": caregiver["name"],
                    "skills_score": skills_score,
                    "proximity_score": proximity_score,
                    "feedback_score": feedback_score,
                    "calendar_score": calendar_score,
                    "overall_score": overall_score,
                    "distance_miles": self._get_distance(
                        caregiver["location"], facility_address
                    ),
                    "calendar_url": caregiver["calendar_url"]
                }
        
        return best_match or {}
    
    def _calculate_skills_score(self, caregiver_skills: List[str], 
                                 injury_type: str, severity: str) -> float:
        """Score based on skill match (0-100)"""
        
        required_skills = {
            "pressure_ulcer": ["wound_care"],
            "surgical_wound": ["wound_care", "surgical_wound_care"],
            "skin_tear": ["basic_wound_care"],
        }
        
        needed = required_skills.get(injury_type, ["basic_wound_care"])
        
        if severity == "severe":
            needed.append("IV_therapy")
        if severity == "emergency":
            needed.append("emergency_care")
        
        matched = sum(1 for skill in needed if skill in caregiver_skills)
        score = (matched / len(needed)) * 100 if needed else 50
        
        return min(score, 100)
    
    def _calculate_proximity_score(self, cg_location: str, 
                                     resident_location: str) -> float:
        """Score based on distance (0-100, closer = higher)"""
        
        # Simulate MCP call to get distance
        distance = self._get_distance(cg_location, resident_location)
        
        # Score: 100 for <1 mile, decreasing to 0 at 20+ miles
        if distance < 1:
            return 100
        elif distance < 5:
            return 100 - (distance - 1) * 10  # 90-100 for 1-5 miles
        elif distance < 10:
            return 50 - (distance - 5) * 5    # 50-75 for 5-10 miles
        else:
            return max(0, 50 - (distance - 10) * 5)  # 0-50 for 10+ miles
    
    def _get_distance(self, location1: str, location2: str) -> float:
        """Simulate MCP distance calculation"""
        # In real implementation, this would call Google Maps API or similar
        # For demo, we'll use simple city-based distances
        
        if "San Francisco" in location1 and "San Francisco" in location2:
            return 2.5
        elif "Oakland" in location1 and "Oakland" in location2:
            return 3.0
        elif ("San Francisco" in location1 and "Oakland" in location2) or \
             ("Oakland" in location1 and "San Francisco" in location2):
            return 12.5
        else:
            return 8.0
    
    def _calculate_feedback_score(self, avg_rating: float) -> float:
        """Score based on feedback rating (0-100)"""
        # Convert 0-5 star rating to 0-100 scale
        return (avg_rating / 5.0) * 100
    
    def _calculate_calendar_score(self, calendar_url: str) -> float:
        """Score based on availability (0-100)"""
        # Simulate MCP call to caregiver calendar
        calendar = CAREGIVER_CALENDARS.get(calendar_url, {})
        available_slots = calendar.get("available_slots", [])
        
        # More available slots = higher score
        if len(available_slots) >= 3:
            return 100
        elif len(available_slots) == 2:
            return 70
        elif len(available_slots) == 1:
            return 40
        else:
            return 10


# =====================================
# AGENT 4: VISIT SCHEDULER
# =====================================

class VisitSchedulerAgent:
    """Schedules visit and creates billing stub"""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
    
    def schedule_visit(self, caregiver_calendar: str, injury_type: str, 
                       severity: str) -> dict:
        """Create visit stub with procedure code"""
        
        # Get first available slot
        calendar = CAREGIVER_CALENDARS.get(caregiver_calendar, {})
        available_slots = calendar.get("available_slots", [])
        
        if not available_slots:
            return {
                "visit_scheduled": False,
                "error": "No available slots"
            }
        
        visit_datetime = available_slots[0]
        
        # Assign procedure code (CPT code)
        procedure_code = self._get_procedure_code(injury_type, severity)
        
        # Create visit stub
        visit_stub = {
            "visit_scheduled": True,
            "visit_datetime": visit_datetime,
            "visit_stub_id": f"VISIT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "procedure_code": procedure_code,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        return visit_stub
    
    def _get_procedure_code(self, injury_type: str, severity: str) -> str:
        """Map injury to CPT procedure code"""
        
        codes = {
            "pressure_ulcer": {
                "mild": "99213",      # Office visit, level 3
                "moderate": "97597",  # Debridement
                "severe": "97602",    # Wound care with selective debridement
                "emergency": "99285"  # Emergency dept visit
            },
            "surgical_wound": {
                "mild": "99213",
                "moderate": "97597",
                "severe": "97598",
                "emergency": "99285"
            },
            "skin_tear": {
                "mild": "12001",  # Simple wound repair
                "moderate": "12002",
                "severe": "12004"
            }
        }
        
        return codes.get(injury_type, {}).get(severity, "99213")


# =====================================
# LANGGRAPH WORKFLOW
# =====================================

def create_camera_to_care_workflow(api_key: str):
    """Build the complete LangGraph workflow"""
    
    # Initialize agents
    injury_classifier = InjuryClassifierAgent(api_key)
    insurance_verifier = InsuranceVerificationAgent(api_key)
    caregiver_matcher = CaregiverMatcherAgent(api_key)
    visit_scheduler = VisitSchedulerAgent(api_key)
    
    # Define workflow nodes
    def classify_injury_node(state: CareEncounterState) -> CareEncounterState:
        """Step 2: Classify injury type and severity"""
        st.write("🔍 **Step 2:** Classifying injury...")
        
        classification = injury_classifier.classify(state['image_base64'])
        
        return {
            **state,
            "injury_type": classification['injury_type'],
            "severity": classification['severity'],
            "clinical_description": classification['clinical_description'],
            "current_step": "classification",
            "completed_steps": ["classification"]
        }
    
    def verify_insurance_node(state: CareEncounterState) -> CareEncounterState:
        """Step 3: Verify insurance coverage"""
        st.write("💳 **Step 3:** Verifying insurance coverage...")
        
        coverage = insurance_verifier.verify_coverage(
            state['patient_id'],
            state['injury_type'],
            state['severity']
        )
        
        return {
            **state,
            **coverage,
            "current_step": "insurance",
            "completed_steps": ["insurance"]
        }
    
    def coverage_router(state: CareEncounterState) -> str:
        """Route based on insurance coverage"""
        if not state.get('is_covered', False):
            return "coverage_denied"
        return "match_caregiver"
    
    def coverage_denied_node(state: CareEncounterState) -> CareEncounterState:
        """Handle denied coverage"""
        st.error("⚠️ Insurance does not cover this service")
        
        return {
            **state,
            "requires_human_review": True,
            "current_step": "coverage_denied",
            "completed_steps": ["coverage_denied"]
        }
    
    def match_caregiver_node(state: CareEncounterState) -> CareEncounterState:
        """Step 4: Match optimal caregiver"""
        st.write("🔎 **Step 4:** Matching caregiver...")
        st.write("   • Analyzing skills...")
        st.write("   • Calculating proximity...")
        st.write("   • Checking feedback scores...")
        st.write("   • Reviewing calendar availability...")
        
        match = caregiver_matcher.match_caregiver(
            state['injury_type'],
            state['severity'],
            state['facility_address'],
            state['patient_id']
        )
        
        return {
            **state,
            "matched_caregiver_id": match.get('caregiver_id', ''),
            "matched_caregiver_name": match.get('caregiver_name', ''),
            "caregiver_skills_score": match.get('skills_score', 0),
            "proximity_score": match.get('proximity_score', 0),
            "feedback_score": match.get('feedback_score', 0),
            "calendar_score": match.get('calendar_score', 0),
            "overall_match_score": match.get('overall_score', 0),
            "caregiver_distance_miles": match.get('distance_miles', 0),
            "current_step": "matching",
            "completed_steps": ["matching"]
        }
    
    def schedule_visit_node(state: CareEncounterState) -> CareEncounterState:
        """Step 5: Schedule the visit"""
        st.write("📅 **Step 5:** Scheduling visit...")
        
        # Get caregiver calendar URL
        caregiver_id = state.get('matched_caregiver_id', '')
        calendar_url = CAREGIVER_PROFILES.get(caregiver_id, {}).get('calendar_url', '')
        
        visit = visit_scheduler.schedule_visit(
            calendar_url,
            state['injury_type'],
            state['severity']
        )
        
        return {
            **state,
            **visit,
            "current_step": "scheduling",
            "completed_steps": ["scheduling"]
        }
    
    # Build graph
    workflow = StateGraph(CareEncounterState)
    
    # Add nodes
    workflow.add_node("classify_injury", classify_injury_node)
    workflow.add_node("verify_insurance", verify_insurance_node)
    workflow.add_node("coverage_denied", coverage_denied_node)
    workflow.add_node("match_caregiver", match_caregiver_node)
    workflow.add_node("schedule_visit", schedule_visit_node)
    
    # Define flow
    workflow.set_entry_point("classify_injury")
    workflow.add_edge("classify_injury", "verify_insurance")
    workflow.add_conditional_edges(
        "verify_insurance",
        coverage_router,
        {
            "coverage_denied": "coverage_denied",
            "match_caregiver": "match_caregiver"
        }
    )
    workflow.add_edge("coverage_denied", END)
    workflow.add_edge("match_caregiver", "schedule_visit")
    workflow.add_edge("schedule_visit", END)
    
    return workflow.compile()


# =====================================
# STREAMLIT UI
# =====================================

def encode_image(image_file):
    """Encode uploaded image to base64"""
    image = Image.open(image_file)
    max_size = (1024, 1024)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


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
            font-size: 2.5rem;
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
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Camera-to-Care System</h1>', unsafe_allow_html=True)
    st.markdown("### *From Image → Insurance → Caregiver Match → Visit Scheduled*")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x120/2c5aa0/ffffff?text=Camera-to-Care", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### 🔐 Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", "")
        )
        
        st.markdown("---")
        st.markdown("### 📊 Workflow Steps")
        st.markdown("""
        1. **📸 Upload** - Image capture
        2. **🔍 Classify** - Injury type & severity
        3. **💳 Verify** - Insurance coverage
        4. **👥 Match** - Optimal caregiver
        5. **📅 Schedule** - Book visit
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 Matching Criteria")
        st.info("""
        **40%** Skills Match  
        **25%** Proximity  
        **20%** Feedback Rating  
        **15%** Calendar Availability
        """)
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key to continue")
        st.stop()
    
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
        **Patient:** {resident['name']}  
        **Age:** {resident['age']}  
        **Insurance:** {resident['insurance']['provider']}  
        **Location:** {resident['facility_address']}
        """)
        
        # Image upload
        uploaded_file = st.file_uploader(
            "Upload injury image",
            type=['jpg', 'jpeg', 'png']
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            process_btn = st.button(
                "🚀 Process Camera-to-Care Workflow",
                type="primary",
                use_container_width=True
            )
        else:
            process_btn = False
    
    with col2:
        st.markdown("## 📊 Workflow Status")
        status_placeholder = st.empty()
    
    # Process workflow
    if process_btn and uploaded_file:
        image_base64 = encode_image(uploaded_file)
        
        # Initialize state
        initial_state = {
            "image_base64": image_base64,
            "patient_id": patient_id,
            "facility_address": resident['facility_address'],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed_steps": [],
            "requires_human_review": False
        }
        
        # Run workflow
        with st.spinner("🔄 Running Camera-to-Care workflow..."):
            workflow = create_camera_to_care_workflow(api_key)
            
            try:
                final_state = workflow.invoke(initial_state)
                
                # Display results
                st.markdown("---")
                st.markdown("## ✅ Workflow Complete!")
                
                # Summary metrics
                col_a, col_b, col_c, col_d = st.columns(4)
                
                with col_a:
                    st.metric(
                        "Injury Classification",
                        final_state.get('injury_type', 'N/A').replace('_', ' ').title(),
                        delta=final_state.get('severity', 'N/A').upper()
                    )
                
                with col_b:
                    coverage = final_state.get('coverage_percentage', 0)
                    st.metric(
                        "Insurance Coverage",
                        f"{coverage}%",
                        delta="Covered ✓" if final_state.get('is_covered') else "Not Covered ✗"
                    )
                
                with col_c:
                    match_score = final_state.get('overall_match_score', 0)
                    st.metric(
                        "Caregiver Match",
                        f"{match_score:.1f}/100",
                        delta=final_state.get('matched_caregiver_name', 'N/A')
                    )
                
                with col_d:
                    st.metric(
                        "Visit Status",
                        "Scheduled ✓" if final_state.get('visit_scheduled') else "Pending",
                        delta=final_state.get('visit_datetime', 'N/A')
                    )
                
                # Detailed tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "🔍 Classification",
                    "💳 Insurance",
                    "👥 Caregiver Match",
                    "📅 Visit Details",
                    "📊 Complete Summary"
                ])
                
                with tab1:
                    st.markdown("### Injury Classification Results")
                    
                    col_x, col_y = st.columns(2)
                    
                    with col_x:
                        st.markdown("**Classification:**")
                        st.info(f"""
                        **Type:** {final_state.get('injury_type', 'N/A').replace('_', ' ').title()}  
                        **Severity:** {final_state.get('severity', 'N/A').upper()}  
                        """)
                    
                    with col_y:
                        st.markdown("**Clinical Description:**")
                        st.write(final_state.get('clinical_description', 'N/A'))
                
                with tab2:
                    st.markdown("### Insurance Verification Results")
                    
                    if final_state.get('is_covered'):
                        st.success("✅ Service is COVERED by insurance")
                    else:
                        st.error("❌ Service is NOT COVERED by insurance")
                    
                    col_ins1, col_ins2 = st.columns(2)
                    
                    with col_ins1:
                        st.markdown("**Insurance Details:**")
                        st.info(f"""
                        **Provider:** {final_state.get('insurance_provider', 'N/A')}  
                        **Plan:** {final_state.get('insurance_plan', 'N/A')}  
                        **Coverage:** {final_state.get('coverage_percentage', 0)}%  
                        **Copay:** ${final_state.get('copay_amount', 0):.2f}
                        """)
                    
                    with col_ins2:
                        st.markdown("**Explanation of Benefits (EOB):**")
                        eob = final_state.get('eob_summary', 'N/A')
                        st.text_area("EOB Summary", eob, height=200)
                
                with tab3:
                    st.markdown("### Caregiver Matching Analysis")
                    
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
                            # Color code based on score
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
                    
                    # Overall score
                    overall = final_state.get('overall_match_score', 0)
                    st.markdown(f"### Overall Match Score: **{overall:.1f}/100**")
                    st.progress(overall / 100)
                    
                    # Distance
                    distance = final_state.get('caregiver_distance_miles', 0)
                    st.info(f"📍 Distance to facility: **{distance:.1f} miles**")
                    
                    # Caregiver details
                    cg_id = final_state.get('matched_caregiver_id', '')
                    if cg_id and cg_id in CAREGIVER_PROFILES:
                        caregiver = CAREGIVER_PROFILES[cg_id]
                        st.markdown("#### Caregiver Profile")
                        st.json({
                            "Name": caregiver['name'],
                            "Skills": caregiver['skills'],
                            "Location": caregiver['location'],
                            "Avg Rating": caregiver['avg_feedback_rating'],
                            "Total Reviews": caregiver['total_reviews']
                        })
                
                with tab4:
                    st.markdown("### Visit Scheduling Details")
                    
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
                            
                            # Calculate estimated costs
                            coverage_pct = final_state.get('coverage_percentage', 0)
                            copay = final_state.get('copay_amount', 0)
                            
                            # Estimated service cost (simplified)
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
                    
                    # Create comprehensive summary
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
                            "Description": final_state.get('clinical_description')
                        },
                        "Insurance": {
                            "Provider": final_state.get('insurance_provider'),
                            "Plan": final_state.get('insurance_plan'),
                            "Covered": final_state.get('is_covered'),
                            "Coverage %": final_state.get('coverage_percentage'),
                            "Copay": final_state.get('copay_amount')
                        },
                        "Caregiver Match": {
                            "Name": final_state.get('matched_caregiver_name'),
                            "Overall Score": final_state.get('overall_match_score'),
                            "Skills Score": final_state.get('caregiver_skills_score'),
                            "Proximity Score": final_state.get('proximity_score'),
                            "Feedback Score": final_state.get('feedback_score'),
                            "Calendar Score": final_state.get('calendar_score'),
                            "Distance": final_state.get('caregiver_distance_miles')
                        },
                        "Visit": {
                            "Scheduled": final_state.get('visit_scheduled'),
                            "Visit ID": final_state.get('visit_stub_id'),
                            "Date/Time": final_state.get('visit_datetime'),
                            "Procedure Code": final_state.get('procedure_code')
                        },
                        "Workflow": {
                            "Steps Completed": final_state.get('completed_steps', []),
                            "Current Step": final_state.get('current_step'),
                            "Requires Review": final_state.get('requires_human_review', False)
                        }
                    }
                    
                    st.json(summary)
                    
                    # Download summary
                    summary_json = json.dumps(summary, indent=2)
                    st.download_button(
                        "📥 Download Complete Summary (JSON)",
                        summary_json,
                        file_name=f"camera_to_care_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"Error processing workflow: {str(e)}")
                st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #718096;'>
            <p>🏥 Camera-to-Care System | Multi-Agent AI with LangGraph<br>
            Insurance Verification • Caregiver Matching • Automated Scheduling</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


# =====================================
# INSTALLATION & RUN
# =====================================
"""
SETUP:
pip install streamlit langchain langchain-openai langgraph pillow openai

RUN:
streamlit run camera_to_care_revised.py

FEATURES:
✅ Image-based injury classification (GPT-4o Vision)
✅ Insurance eligibility verification with EOB generation
✅ Multi-criteria caregiver matching (4 scoring algorithms)
✅ Automated visit scheduling with CPT codes
✅ Complete audit trail and JSON export
✅ LangGraph workflow with conditional routing

SCORING WEIGHTS:
• Skills Match: 40%
• Proximity: 25%
• Feedback Rating: 20%
• Calendar Availability: 15%

SIMULATED MCPs:
• Distance calculation (would use Google Maps API)
• Caregiver calendar access
• Insurance eligibility verification
• Resident profile database

NEXT ENHANCEMENTS:
• Real MCP integrations (Google Maps, calendar APIs)
• Voice input with WhisperFlow
• SMS notifications via Twilio
• Real-time audit logging
• Mobile app integration
"""

