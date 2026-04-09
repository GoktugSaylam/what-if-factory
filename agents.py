"""
io Intelligence Agent wrappers
"""
import json
import os
from dotenv import load_dotenv
import prompts

# Load environment variables
load_dotenv()

# Check which API to use
USE_GEMINI = os.getenv("GEMINI_API_KEY") is not None

if USE_GEMINI:
    from google import genai
    from google.genai import types
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    # Configure Gemini model with JSON response
    generation_config = types.GenerateContentConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
    )
else:
    from openai import OpenAI
    # Initialize OpenAI client (compatible with io.net)
    client = OpenAI(
        api_key=os.getenv("IO_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("IO_BASE_URL") or "https://api.openai.com/v1"
    )

def simulate_decision(decision: str, context: str = "", factory_profile: dict = None, model: str = "gpt-4") -> dict:
    """
    Custom Agent: Simulates factory decision outcomes
    
    Args:
        decision: The decision made by user
        context: Optional factory context from uploaded files
        factory_profile: Factory profile dict
        model: Model to use (default gpt-4)
    
    Returns:
        dict: Simulation results
    """
    try:
        factory_context = ""
        if factory_profile:
            skills = factory_profile.get('employee_count', {}).get('skills', {})
            factory_context = f"""
FABRİKA PROFİLİ:
- Sektör: {factory_profile.get('sector', 'Genel Üretim')}
- Mevcut Durum: {factory_profile.get('current_status', 'Standart operasyon')}
- Çalışan Sayısı: {factory_profile.get('employee_count', {}).get('total', 200)} (Mavi Yaka: {factory_profile.get('employee_count', {}).get('blue_collar', 150)}, Beyaz Yaka: {factory_profile.get('employee_count', {}).get('white_collar', 20)})
- Çalışan Becerileri:
  * Operatörler: {skills.get('operators', 0)} kişi
  * Teknisyenler: {skills.get('technicians', 0)} kişi
  * Bakım Ekibi: {skills.get('maintenance_crew', 0)} kişi
  * Mühendisler: {skills.get('engineers', 0)} kişi
  * Kalite Kontrol: {skills.get('quality_control', 0)} kişi
  * Yönetim: {skills.get('management', 0)} kişi
- Başlangıç Bütçesi: {factory_profile.get('initial_budget', 5000000):,} TL
"""
        
        if USE_GEMINI:
            # Use Gemini API
            prompt = f"{prompts.CUSTOM_AGENT_SYSTEM.format(factory_profile=factory_context, context=context)}\n\n{prompts.get_custom_agent_prompt(decision, context)}\n\nRespond ONLY with valid JSON format, no markdown code blocks."
            response = gemini_client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=generation_config)
            
            # Extract JSON from response (handle markdown code blocks)
            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
        else:
            # Use OpenAI/io.net API
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompts.CUSTOM_AGENT_SYSTEM.format(factory_profile=factory_context, context=context)},
                    {"role": "user", "content": prompts.get_custom_agent_prompt(decision, context)}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
        
        return result
    except Exception as e:
        print(f"====== ERROR in simulate_decision ======")
        print(f"Error: {e}")
        print(f"Decision: {decision}")
        if 'response_text' in locals():
            print(f"Response text: {response_text[:500]}")
        import traceback
        traceback.print_exc()
        print(f"====== END ERROR ======")
        # Fallback response
        return {
            "production_change_percent": 0,
            "cost_change_percent": 0,
            "cost_change_daily_tl": 0,
            "risk_level": "Orta",
            "risk_explanation": "Simülasyon hatası oluştu.",
            "side_effects": ["API hatası"],
            "score_impact": 0,
            "budget_impact": 0,
            "satisfaction_impact": 0,
            "production_rate_impact": 0,
            "is_investment": False,
            "investment_delay_weeks": 0,
            "investment_description": "",
            "delayed_production_impact": 0,
            "delayed_budget_impact": 0,
            "delayed_satisfaction_impact": 0
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
        if USE_GEMINI:
            # Use Gemini API
            prompt = f"{prompts.CLASSIFICATION_AGENT_SYSTEM}\n\n{prompts.get_classification_prompt(decision, result)}\n\nRespond ONLY with valid JSON format, no markdown code blocks."
            response = gemini_client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=generation_config)
            
            # Extract JSON from response (handle markdown code blocks)
            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            classification = json.loads(response_text)
        else:
            # Use OpenAI/io.net API
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
        print(f"Response text (if available): {response_text if 'response_text' in locals() else 'N/A'}")
        import traceback
        traceback.print_exc()
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
        return "## Henüz karar alınmadı\n\nKarar aldık ça burada özet göreceksiniz."
    
    try:
        if USE_GEMINI:
            # Use Gemini API
            prompt = f"{prompts.SUMMARY_AGENT_SYSTEM}\n\n{prompts.get_summary_prompt(history)}"
            response = gemini_client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=generation_config)
            summary = response.text
        else:
            # Use OpenAI/io.net API
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

def generate_random_event(factory_profile: dict, risk_level: float, week_number: int, model: str = "gpt-4") -> dict:
    """
    Event Generator Agent: Generates contextual random events
    
    Args:
        factory_profile: Factory profile dict
        risk_level: Current risk level (0-100)
        week_number: Current week number
        model: Model to use
    
    Returns:
        dict: Event data or None if no event
    """
    try:
        if USE_GEMINI:
            # Use Gemini API
            prompt = f"{prompts.get_event_generator_prompt(factory_profile, risk_level, week_number)}\n\nRespond ONLY with valid JSON format, no markdown code blocks."
            response = gemini_client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=generation_config)
            
            # Extract JSON from response (handle markdown code blocks)
            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            event = json.loads(response_text)
        else:
            # Use OpenAI/io.net API
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an event generator for a factory simulation game."},
                    {"role": "user", "content": prompts.get_event_generator_prompt(factory_profile, risk_level, week_number)}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            event = json.loads(response.choices[0].message.content)
        
        # Return None if no event
        if not event.get('has_event', False):
            return None
            
        return event
    except Exception as e:
        print(f"Error in generate_random_event: {e}")
        # Return None on error (no event)
        return None
