# core/investment_options_agent.py
# Investment Options Agent - Recommends investment vehicles based on goals

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

class InvestmentVehicle(str, Enum):
    """Available investment vehicle types."""
    HIGH_YIELD_SAVINGS = "high_yield_savings"
    LIQUID_FUNDS = "liquid_funds"
    SHORT_TERM_DEBT = "short_term_debt"
    BALANCED_FUNDS = "balanced_funds"
    EQUITY_MUTUAL_FUNDS = "equity_mutual_funds"
    INDEX_FUNDS = "index_funds"
    FIXED_DEPOSITS = "fixed_deposits"
    PPF = "ppf"
    NPS = "nps"
    ELSS = "elss"
    CORPORATE_BONDS = "corporate_bonds"

class RiskCategory(str, Enum):
    """Risk categories for investments."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class InvestmentOption(BaseModel):
    """Single investment option recommendation."""
    vehicle: InvestmentVehicle
    name: str
    expected_return_annual: float
    risk_category: RiskCategory
    liquidity_days: int
    min_investment: float
    allocation_percentage: float
    rationale: str
    lock_in_period_months: Optional[int] = None
    tax_benefits: Optional[str] = None

class InvestmentStrategy(BaseModel):
    """Complete investment strategy for a goal."""
    goal_id: str
    goal_name: str
    time_horizon_months: int
    target_amount: float
    current_balance: float
    monthly_contribution: float
    recommended_options: List[InvestmentOption]
    overall_expected_return: float
    rebalancing_frequency: str
    risk_assessment: str
    notes: List[str]

class InvestmentOptionsInput(BaseModel):
    """Input for investment options agent."""
    goal_id: str
    goal_name: str
    target_amount: float
    current_balance: float = 0.0
    monthly_contribution: float
    time_horizon_months: int
    due_date: Optional[date] = None
    risk_tolerance: str = "balanced"  # conservative, balanced, aggressive
    currency: str = "INR"
    country: str = "India"

class InvestmentOptionsAgent:
    """
    Agent that recommends investment vehicles based on:
    - Time horizon (emergency fund, short-term, medium-term, long-term)
    - Risk tolerance (conservative, balanced, aggressive)
    - Goal amount and monthly contribution
    - Country-specific options (India, USA, etc.)
    """
    
    def __init__(self, openai_api_key: str, base_url: str = None):
        """Initialize the investment options agent."""
        llm_params = {
            "model": "gpt-4o-mini",
            "api_key": openai_api_key,
            "temperature": 0.3
        }
        
        if base_url:
            llm_params["base_url"] = base_url
        
        self.llm = ChatOpenAI(**llm_params)
        
        # Investment vehicle database (India-specific)
        self.india_vehicles = {
            InvestmentVehicle.HIGH_YIELD_SAVINGS: {
                "name": "High Yield Savings Account",
                "expected_return": 0.035,
                "risk": RiskCategory.VERY_LOW,
                "liquidity_days": 0,
                "min_investment": 0,
                "lock_in_months": None,
                "tax_benefits": None
            },
            InvestmentVehicle.LIQUID_FUNDS: {
                "name": "Liquid Mutual Funds",
                "expected_return": 0.045,
                "risk": RiskCategory.VERY_LOW,
                "liquidity_days": 1,
                "min_investment": 500,
                "lock_in_months": None,
                "tax_benefits": None
            },
            InvestmentVehicle.SHORT_TERM_DEBT: {
                "name": "Short Term Debt Funds",
                "expected_return": 0.055,
                "risk": RiskCategory.LOW,
                "liquidity_days": 3,
                "min_investment": 1000,
                "lock_in_months": None,
                "tax_benefits": None
            },
            InvestmentVehicle.FIXED_DEPOSITS: {
                "name": "Bank Fixed Deposits",
                "expected_return": 0.065,
                "risk": RiskCategory.VERY_LOW,
                "liquidity_days": 90,
                "min_investment": 1000,
                "lock_in_months": 12,
                "tax_benefits": "80C eligible (Tax Saver FD)"
            },
            InvestmentVehicle.PPF: {
                "name": "Public Provident Fund",
                "expected_return": 0.071,
                "risk": RiskCategory.VERY_LOW,
                "liquidity_days": 1825,  # 5 years
                "min_investment": 500,
                "lock_in_months": 180,  # 15 years
                "tax_benefits": "EEE - Section 80C up to ₹1.5L"
            },
            InvestmentVehicle.ELSS: {
                "name": "Equity Linked Savings Scheme",
                "expected_return": 0.12,
                "risk": RiskCategory.HIGH,
                "liquidity_days": 1095,  # 3 years
                "min_investment": 500,
                "lock_in_months": 36,
                "tax_benefits": "Section 80C up to ₹1.5L"
            },
            InvestmentVehicle.BALANCED_FUNDS: {
                "name": "Balanced Hybrid Funds",
                "expected_return": 0.085,
                "risk": RiskCategory.MODERATE,
                "liquidity_days": 3,
                "min_investment": 1000,
                "lock_in_months": None,
                "tax_benefits": None
            },
            InvestmentVehicle.EQUITY_MUTUAL_FUNDS: {
                "name": "Equity Mutual Funds",
                "expected_return": 0.12,
                "risk": RiskCategory.HIGH,
                "liquidity_days": 3,
                "min_investment": 500,
                "lock_in_months": None,
                "tax_benefits": "LTCG >₹1L taxed at 10%"
            },
            InvestmentVehicle.INDEX_FUNDS: {
                "name": "Nifty 50 Index Funds",
                "expected_return": 0.11,
                "risk": RiskCategory.HIGH,
                "liquidity_days": 3,
                "min_investment": 100,
                "lock_in_months": None,
                "tax_benefits": "LTCG >₹1L taxed at 10%"
            },
            InvestmentVehicle.NPS: {
                "name": "National Pension System",
                "expected_return": 0.10,
                "risk": RiskCategory.MODERATE,
                "liquidity_days": 21900,  # Until retirement
                "min_investment": 500,
                "lock_in_months": 360,  # Until age 60
                "tax_benefits": "80CCD(1B) ₹50K + 80C ₹1.5L"
            },
            InvestmentVehicle.CORPORATE_BONDS: {
                "name": "Corporate Bonds/NCDs",
                "expected_return": 0.08,
                "risk": RiskCategory.LOW,
                "liquidity_days": 30,
                "min_investment": 10000,
                "lock_in_months": 12,
                "tax_benefits": None
            }
        }
    
    def recommend(self, input_data: InvestmentOptionsInput) -> InvestmentStrategy:
        """
        Generate investment recommendations for a goal.
        
        Args:
            input_data: Goal details and preferences
            
        Returns:
            Complete investment strategy with vehicle recommendations
        """
        # Classify goal by time horizon
        horizon_category = self._classify_horizon(input_data.time_horizon_months)
        
        # Get suitable vehicles based on horizon and risk tolerance
        suitable_vehicles = self._filter_vehicles(
            horizon_category,
            input_data.risk_tolerance,
            input_data.monthly_contribution
        )
        
        # Generate allocation strategy
        recommended_options = self._create_allocation(
            suitable_vehicles,
            input_data,
            horizon_category
        )
        
        # Calculate overall expected return
        overall_return = sum(
            opt.expected_return_annual * opt.allocation_percentage / 100
            for opt in recommended_options
        )
        
        # Determine rebalancing frequency
        rebalancing = self._get_rebalancing_frequency(horizon_category)
        
        # Generate risk assessment
        risk_assessment = self._assess_risk(recommended_options, input_data)
        
        # Generate strategy notes
        notes = self._generate_notes(input_data, recommended_options, horizon_category)
        
        return InvestmentStrategy(
            goal_id=input_data.goal_id,
            goal_name=input_data.goal_name,
            time_horizon_months=input_data.time_horizon_months,
            target_amount=input_data.target_amount,
            current_balance=input_data.current_balance,
            monthly_contribution=input_data.monthly_contribution,
            recommended_options=recommended_options,
            overall_expected_return=overall_return,
            rebalancing_frequency=rebalancing,
            risk_assessment=risk_assessment,
            notes=notes
        )
    
    def _classify_horizon(self, months: int) -> str:
        """Classify time horizon into categories."""
        if months <= 6:
            return "emergency"
        elif months <= 24:
            return "short_term"
        elif months <= 60:
            return "medium_term"
        else:
            return "long_term"
    
    def _filter_vehicles(
        self,
        horizon_category: str,
        risk_tolerance: str,
        monthly_contribution: float
    ) -> List[tuple[InvestmentVehicle, Dict]]:
        """Filter suitable investment vehicles."""
        suitable = []
        
        for vehicle, details in self.india_vehicles.items():
            # Filter by time horizon
            if horizon_category == "emergency":
                if details["liquidity_days"] <= 7:
                    suitable.append((vehicle, details))
            
            elif horizon_category == "short_term":
                if details["liquidity_days"] <= 180:
                    suitable.append((vehicle, details))
            
            elif horizon_category == "medium_term":
                if details["risk"] in [RiskCategory.LOW, RiskCategory.MODERATE]:
                    suitable.append((vehicle, details))
            
            elif horizon_category == "long_term":
                # All vehicles suitable for long term
                suitable.append((vehicle, details))
            
            # Filter by minimum investment
            if details["min_investment"] > monthly_contribution:
                if (vehicle, details) in suitable:
                    suitable.remove((vehicle, details))
        
        # Further filter by risk tolerance
        if risk_tolerance == "conservative":
            suitable = [
                (v, d) for v, d in suitable
                if d["risk"] in [RiskCategory.VERY_LOW, RiskCategory.LOW]
            ]
        elif risk_tolerance == "balanced":
            suitable = [
                (v, d) for v, d in suitable
                if d["risk"] in [RiskCategory.VERY_LOW, RiskCategory.LOW, RiskCategory.MODERATE]
            ]
        # aggressive includes all
        
        return suitable
    
    def _create_allocation(
        self,
        vehicles: List[tuple[InvestmentVehicle, Dict]],
        input_data: InvestmentOptionsInput,
        horizon_category: str
    ) -> List[InvestmentOption]:
        """Create allocation strategy across vehicles."""
        
        if not vehicles:
            # Fallback to high yield savings
            return [self._create_default_option()]
        
        recommendations = []
        
        if horizon_category == "emergency":
            # 100% liquid
            for vehicle, details in vehicles[:1]:
                recommendations.append(
                    InvestmentOption(
                        vehicle=vehicle,
                        name=details["name"],
                        expected_return_annual=details["expected_return"],
                        risk_category=details["risk"],
                        liquidity_days=details["liquidity_days"],
                        min_investment=details["min_investment"],
                        allocation_percentage=100.0,
                        rationale="Maximum liquidity for emergency fund",
                        lock_in_period_months=details["lock_in_months"],
                        tax_benefits=details["tax_benefits"]
                    )
                )
        
        elif horizon_category == "short_term":
            # 70% liquid, 30% short-term debt
            if len(vehicles) >= 2:
                for i, (vehicle, details) in enumerate(vehicles[:2]):
                    allocation = 70.0 if i == 0 else 30.0
                    recommendations.append(
                        InvestmentOption(
                            vehicle=vehicle,
                            name=details["name"],
                            expected_return_annual=details["expected_return"],
                            risk_category=details["risk"],
                            liquidity_days=details["liquidity_days"],
                            min_investment=details["min_investment"],
                            allocation_percentage=allocation,
                            rationale=f"{'High liquidity' if i == 0 else 'Better returns'} for short-term goal",
                            lock_in_period_months=details["lock_in_months"],
                            tax_benefits=details["tax_benefits"]
                        )
                    )
            else:
                recommendations.append(self._vehicle_to_option(vehicles[0], 100.0))
        
        elif horizon_category == "medium_term":
            # 20% liquid, 50% debt, 30% balanced
            allocations = [20.0, 50.0, 30.0]
            for i, (vehicle, details) in enumerate(vehicles[:3]):
                if i < len(allocations):
                    recommendations.append(
                        InvestmentOption(
                            vehicle=vehicle,
                            name=details["name"],
                            expected_return_annual=details["expected_return"],
                            risk_category=details["risk"],
                            liquidity_days=details["liquidity_days"],
                            min_investment=details["min_investment"],
                            allocation_percentage=allocations[i],
                            rationale=self._get_rationale(i, horizon_category),
                            lock_in_period_months=details["lock_in_months"],
                            tax_benefits=details["tax_benefits"]
                        )
                    )
        
        elif horizon_category == "long_term":
            # Risk-based allocation
            if input_data.risk_tolerance == "conservative":
                # 30% liquid, 50% debt, 20% equity
                allocations = [30.0, 50.0, 20.0]
            elif input_data.risk_tolerance == "aggressive":
                # 10% liquid, 20% debt, 70% equity
                allocations = [10.0, 20.0, 70.0]
            else:  # balanced
                # 20% liquid, 30% debt, 50% equity
                allocations = [20.0, 30.0, 50.0]
            
            for i, (vehicle, details) in enumerate(vehicles[:3]):
                if i < len(allocations):
                    recommendations.append(
                        InvestmentOption(
                            vehicle=vehicle,
                            name=details["name"],
                            expected_return_annual=details["expected_return"],
                            risk_category=details["risk"],
                            liquidity_days=details["liquidity_days"],
                            min_investment=details["min_investment"],
                            allocation_percentage=allocations[i],
                            rationale=self._get_rationale(i, horizon_category),
                            lock_in_period_months=details["lock_in_months"],
                            tax_benefits=details["tax_benefits"]
                        )
                    )
        
        return recommendations
    
    def _vehicle_to_option(
        self,
        vehicle_tuple: tuple[InvestmentVehicle, Dict],
        allocation: float
    ) -> InvestmentOption:
        """Convert vehicle tuple to InvestmentOption."""
        vehicle, details = vehicle_tuple
        return InvestmentOption(
            vehicle=vehicle,
            name=details["name"],
            expected_return_annual=details["expected_return"],
            risk_category=details["risk"],
            liquidity_days=details["liquidity_days"],
            min_investment=details["min_investment"],
            allocation_percentage=allocation,
            rationale="Suitable for goal timeline",
            lock_in_period_months=details["lock_in_months"],
            tax_benefits=details["tax_benefits"]
        )
    
    def _create_default_option(self) -> InvestmentOption:
        """Create default fallback option."""
        details = self.india_vehicles[InvestmentVehicle.HIGH_YIELD_SAVINGS]
        return InvestmentOption(
            vehicle=InvestmentVehicle.HIGH_YIELD_SAVINGS,
            name=details["name"],
            expected_return_annual=details["expected_return"],
            risk_category=details["risk"],
            liquidity_days=details["liquidity_days"],
            min_investment=details["min_investment"],
            allocation_percentage=100.0,
            rationale="Safe default option",
            lock_in_period_months=details["lock_in_months"],
            tax_benefits=details["tax_benefits"]
        )
    
    def _get_rationale(self, index: int, horizon: str) -> str:
        """Get rationale for allocation."""
        rationales = {
            "medium_term": [
                "Liquidity buffer for emergencies",
                "Stable returns with capital protection",
                "Growth potential with moderate risk"
            ],
            "long_term": [
                "Emergency liquidity reserve",
                "Stable debt component for downside protection",
                "Equity for long-term wealth creation"
            ]
        }
        return rationales.get(horizon, ["Balanced allocation"])[index]
    
    def _get_rebalancing_frequency(self, horizon_category: str) -> str:
        """Determine rebalancing frequency."""
        if horizon_category in ["emergency", "short_term"]:
            return "Not required"
        elif horizon_category == "medium_term":
            return "Annually"
        else:
            return "Semi-annually"
    
    def _assess_risk(
        self,
        options: List[InvestmentOption],
        input_data: InvestmentOptionsInput
    ) -> str:
        """Generate risk assessment."""
        weighted_risk = 0
        risk_scores = {
            RiskCategory.VERY_LOW: 1,
            RiskCategory.LOW: 2,
            RiskCategory.MODERATE: 3,
            RiskCategory.HIGH: 4,
            RiskCategory.VERY_HIGH: 5
        }
        
        for opt in options:
            weighted_risk += risk_scores[opt.risk_category] * opt.allocation_percentage / 100
        
        if weighted_risk <= 1.5:
            return "Very Low Risk - Capital protection prioritized"
        elif weighted_risk <= 2.5:
            return "Low Risk - Minimal volatility expected"
        elif weighted_risk <= 3.5:
            return "Moderate Risk - Balanced growth with manageable volatility"
        elif weighted_risk <= 4.5:
            return "High Risk - Significant growth potential with volatility"
        else:
            return "Very High Risk - Maximum growth potential, high volatility"
    
    def _generate_notes(
        self,
        input_data: InvestmentOptionsInput,
        options: List[InvestmentOption],
        horizon_category: str
    ) -> List[str]:
        """Generate strategy notes."""
        notes = []
        
        # Tax benefits note
        tax_options = [opt for opt in options if opt.tax_benefits]
        if tax_options:
            notes.append(f"✅ Tax benefits available: {', '.join([opt.name for opt in tax_options])}")
        
        # Lock-in warning
        locked = [opt for opt in options if opt.lock_in_period_months]
        if locked:
            notes.append(f"⚠️ Lock-in periods: {', '.join([f'{opt.name} ({opt.lock_in_period_months} months)' for opt in locked])}")
        
        # Minimum investment note
        total_min = sum(
            opt.min_investment * opt.allocation_percentage / 100
            for opt in options
        )
        if total_min > input_data.monthly_contribution:
            notes.append(f"💡 Consider lump sum of ₹{total_min:,.0f} to start, then SIP")
        
        # Diversification note
        if len(options) > 1:
            notes.append(f"🎯 Diversified across {len(options)} investment vehicles for risk management")
        
        # Horizon-specific notes
        if horizon_category == "emergency":
            notes.append("🚨 Emergency fund - prioritize liquidity over returns")
        elif horizon_category == "long_term":
            notes.append("📈 Long-term goal - leverage power of compounding")
        
        notes.append("⚠️ Past performance doesn't guarantee future results")
        notes.append("💼 Consider consulting a SEBI-registered financial advisor")
        
        return notes