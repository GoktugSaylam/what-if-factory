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
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # Configure Gemini model with JSON response
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
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
            factory_context = f"""
FABRİKA PROFİLİ:
- Sektör: {factory_profile.get('sector', 'Genel Üretim')}
- Mevcut Durum: {factory_profile.get('current_status', 'Standart operasyon')}
- Çalışan Sayısı: {factory_profile.get('employee_count', {}).get('total', 200)} (Mavi Yaka: {factory_profile.get('employee_count', {}).get('blue_collar', 150)}, Beyaz Yaka: {factory_profile.get('employee_count', {}).get('white_collar', 20)})
- Başlangıç Bütçesi: {factory_profile.get('initial_budget', 5000000):,} TL
"""
        
        if USE_GEMINI:
            # Use Gemini API
            gemini_model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
            prompt = f"{prompts.CUSTOM_AGENT_SYSTEM.format(factory_profile=factory_context, context=context)}\n\n{prompts.get_custom_agent_prompt(decision, context)}\n\nRespond ONLY with valid JSON format, no markdown code blocks."
            response = gemini_model.generate_content(prompt)
            
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
        print(f"Error in simulate_decision: {e}")
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
            "production_rate_impact": 0
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
            gemini_model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
            prompt = f"{prompts.CLASSIFICATION_AGENT_SYSTEM}\n\n{prompts.get_classification_prompt(decision, result)}\n\nRespond ONLY with valid JSON format, no markdown code blocks."
            response = gemini_model.generate_content(prompt)
            
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
        if USE_GEMINI:
            # Use Gemini API
            gemini_model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
            prompt = f"{prompts.SUMMARY_AGENT_SYSTEM}\n\n{prompts.get_summary_prompt(history)}"
            response = gemini_model.generate_content(prompt)
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
