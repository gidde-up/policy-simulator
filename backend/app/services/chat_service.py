"""
AI Chatbot Service for Policy Interpretation
=============================================
Uses Claude API to interpret natural language policy questions
and translate them into simulation parameters.
"""

import os
import json
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from dataclasses import dataclass


@dataclass
class PolicyInterpretation:
    """Interpreted policy parameters from natural language"""
    understood: bool
    message: str
    policy_params: Optional[Dict[str, Any]]
    clarification_needed: Optional[str]
    explanation: str


SYSTEM_PROMPT = """You are an economic policy advisor assistant for a job creation simulation tool.
Your role is to help policymakers understand the employment effects of their policy choices.

The simulation tool covers South Africa (ZAF) and Tunisia (TUN), and models these policy levers:

1. **Tariff changes** by sector: agriculture, mining, manufacturing, textiles, automotive,
   food_processing, chemicals, construction, utilities, trade, transport, finance,
   public_services, other_services

2. **Subsidies** by sector (same sectors as above)

3. **SME stimulus**: A percentage of GDP devoted to small and medium enterprise support

4. **Industrial/productivity investment**: Investment in modernization and productivity
   improvements in manufacturing sectors

When users describe policies, you should:
1. Identify which policy levers are being discussed
2. Estimate reasonable percentage values if not specified (e.g., "moderate tariff increase" = 10-15%)
3. Map vague sector descriptions to our sector categories
4. Ask for clarification if the request is too ambiguous

Always respond with JSON in this format:
{
    "understood": true/false,
    "policy_params": {
        "country": "ZAF" or "TUN",
        "tariff_changes": {"sector_name": percent_change, ...},
        "subsidy_changes": {"sector_name": percent_change, ...},
        "sme_stimulus": percent_of_gdp,
        "productivity_investment": percent_increase,
        "time_horizon": 1, 3, or 5
    },
    "clarification_needed": "question if clarification needed, else null",
    "explanation": "Brief explanation of how you interpreted the request"
}

Important economic context:
- Tariff increases protect domestic industry but may raise prices and reduce efficiency
- Subsidies can boost specific sectors but have fiscal costs
- SME support is generally labor-intensive and creates jobs in services/trade
- Productivity investment may reduce jobs short-term but increase quality jobs long-term
- South Africa has high unemployment (>30%) and a large mining/manufacturing base
- Tunisia has significant textiles/tourism sectors and moderate unemployment (~15%)
"""


class ChatService:
    """Service for AI-powered policy interpretation"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = None

        self.conversation_history: List[Dict[str, str]] = []

    def is_available(self) -> bool:
        """Check if Claude API is configured"""
        return self.client is not None

    async def interpret_policy(
        self,
        user_message: str,
        country_code: str = "ZAF",
        current_params: Optional[Dict] = None
    ) -> PolicyInterpretation:
        """
        Interpret natural language policy description into simulation parameters.
        """
        if not self.is_available():
            return PolicyInterpretation(
                understood=False,
                message="AI assistant not configured. Please set ANTHROPIC_API_KEY.",
                policy_params=None,
                clarification_needed=None,
                explanation="API key missing"
            )

        # Build context message
        context = f"Current country context: {country_code}\n"
        if current_params:
            context += f"Current simulation parameters: {json.dumps(current_params)}\n"
        context += f"\nUser's policy question/request: {user_message}"

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": context}
                ]
            )

            # Parse response
            response_text = response.content[0].text

            # Try to extract JSON from response
            try:
                # Find JSON in response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    parsed = json.loads(json_str)
                else:
                    parsed = json.loads(response_text)

                return PolicyInterpretation(
                    understood=parsed.get('understood', False),
                    message="Policy interpreted successfully" if parsed.get('understood') else "Could not fully understand the request",
                    policy_params=parsed.get('policy_params'),
                    clarification_needed=parsed.get('clarification_needed'),
                    explanation=parsed.get('explanation', '')
                )
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response
                return PolicyInterpretation(
                    understood=False,
                    message=response_text,
                    policy_params=None,
                    clarification_needed="Could you rephrase your policy question?",
                    explanation="Could not parse structured response"
                )

        except Exception as e:
            return PolicyInterpretation(
                understood=False,
                message=f"Error communicating with AI: {str(e)}",
                policy_params=None,
                clarification_needed=None,
                explanation=str(e)
            )

    async def explain_results(
        self,
        simulation_results: Dict,
        user_question: Optional[str] = None
    ) -> str:
        """
        Generate natural language explanation of simulation results.
        """
        if not self.is_available():
            return self._generate_basic_explanation(simulation_results)

        prompt = f"""Based on these economic simulation results, provide a clear,
educational explanation for policymakers. Focus on:
1. The main employment effects (jobs created/lost)
2. Which demographic groups are most affected
3. The transmission mechanism (how the policy leads to these effects)
4. Key caveats and uncertainties

Simulation Results:
{json.dumps(simulation_results, indent=2, default=str)}

{"User's specific question: " + user_question if user_question else ""}

Provide a clear, concise explanation (2-3 paragraphs) suitable for a non-economist policymaker."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return self._generate_basic_explanation(simulation_results)

    def _generate_basic_explanation(self, results: Dict) -> str:
        """Generate basic explanation without AI"""
        if not results or 'aggregate' not in results:
            return "Unable to generate explanation for these results."

        agg = results['aggregate']

        total_jobs = agg.get('total_jobs', 0) if isinstance(agg, dict) else getattr(agg, 'total_jobs', 0)
        female_share = agg.get('female_share', 0) if isinstance(agg, dict) else getattr(agg, 'female_share', 0)
        youth_share = agg.get('youth_share', 0) if isinstance(agg, dict) else getattr(agg, 'youth_share', 0)

        direction = "create" if total_jobs > 0 else "reduce"

        explanation = f"""
**Summary of Employment Effects**

This policy scenario is estimated to {direction} approximately {abs(total_jobs):,.0f} jobs
over the {results.get('time_horizon', 'selected')} year time horizon.

**Demographic Impact:**
- Women would receive {female_share*100:.1f}% of the job effects
- Youth (ages 15-24) would receive {youth_share*100:.1f}% of the job effects

**Important Caveats:**
These projections are based on input-output analysis and historical employment elasticities.
Actual outcomes depend on many factors including global economic conditions, implementation
effectiveness, and behavioral responses not fully captured in the model.
"""
        return explanation

    async def suggest_policies(
        self,
        country_code: str,
        goal: str
    ) -> str:
        """
        Suggest policy combinations to achieve a specific goal.
        """
        if not self.is_available():
            return self._get_default_suggestions(country_code, goal)

        prompt = f"""For {country_code} ({'South Africa' if country_code == 'ZAF' else 'Tunisia'}),
suggest policy combinations to achieve this goal: {goal}

Consider the available policy levers:
- Tariff changes by sector
- Subsidies by sector
- SME stimulus
- Industrial/productivity investment

Provide 2-3 specific policy suggestions with expected effects on employment,
considering the country's economic structure. Be concrete about sector targets
and approximate percentages."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception:
            return self._get_default_suggestions(country_code, goal)

    def _get_default_suggestions(self, country_code: str, goal: str) -> str:
        """Default policy suggestions without AI"""
        if country_code == "ZAF":
            return """
**Policy Suggestions for South Africa:**

1. **Manufacturing Support**: 10-15% tariff protection combined with
   productivity investment could boost formal sector employment.

2. **SME Development**: 1-2% GDP stimulus to SMEs, particularly in
   trade and services sectors, tends to be highly labor-intensive.

3. **Youth Employment**: Targeted subsidies to labor-intensive sectors
   (textiles, construction, services) with youth hiring incentives.
"""
        else:
            return """
**Policy Suggestions for Tunisia:**

1. **Textile Sector Support**: Moderate tariff protection (10%) with
   quality upgrading investments to maintain competitiveness.

2. **Agro-processing Development**: Subsidies to food processing to
   add value to agricultural output and create rural jobs.

3. **Services Expansion**: SME stimulus (1-2% GDP) focused on tourism-
   related services and IT/business services.
"""


# Singleton instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get chat service singleton"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
