"""
io Intelligence Agent wrappers
"""
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import prompts

# Load environment variables
load_dotenv()

# Initialize OpenAI client (compatible with io.net)
client = OpenAI(
    api_key=os.getenv("IO_API_KEY") or os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("IO_BASE_URL") or "https://api.openai.com/v1"
)

def simulate_decision(decision: str, context: str = "", model: str = "gpt-4") -> dict:
    """
    Custom Agent: Simulates factory decision outcomes
    
    Args:
        decision: The decision made by user
        context: Optional factory context from uploaded files
        model: Model to use (default gpt-4)
    
    Returns:
        dict: Simulation results
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompts.CUSTOM_AGENT_SYSTEM.format(context=context)},
                {"role": "user", "content": prompts.get_custom_agent_prompt(decision, context)}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"Error in simulate_decision: {e}")
        # Fallback response
        return {
            "production_change_percent": 0,
            "cost_change_percent": 0,
            "cost_change_daily_tl": 0,
            "risk_level": "Orta",
            "risk_explanation": "Simülasyon hatası oluştu.",
            "side_effects": ["API hatası"],
            "score_impact": 0
        }

def classify_risk(decision: str, result: dict, model: str = "gpt-4") -> dict:
    """
    Classification Agent: Classifies decision risk
    
    Args:
        decision: The decision made
        result: Simulation result from Custom Agent
        model: Model to use
    
    Returns:
        dict: Classification result
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompts.CLASSIFICATION_AGENT_SYSTEM},
                {"role": "user", "content": prompts.get_classification_prompt(decision, result)}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        classification = json.loads(response.choices[0].message.content)
        return classification
    except Exception as e:
        print(f"Error in classify_risk: {e}")
        return {
            "category": "Güvenli",
            "explanation": "Sınıflandırma hatası.",
            "recommendation": ""
        }

def generate_summary(history: list, model: str = "gpt-4") -> str:
    """
    Summary Agent: Generates period summary report
    
    Args:
        history: List of decision history
        model: Model to use
    
    Returns:
        str: Markdown formatted summary report
    """
    if not history:
        return "## Henüz karar alınmadı\n\nKarar aldıkça burada özet göreceksiniz."
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompts.SUMMARY_AGENT_SYSTEM},
                {"role": "user", "content": prompts.get_summary_prompt(history)}
            ],
            temperature=0.6
        )
        
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Error in generate_summary: {e}")
        return f"## Özet Hatası\n\nRapor oluşturulurken hata oluştu: {str(e)}"
