"""
io Intelligence Agent wrappers
v1.3 - IO.net Integration fixes
"""
import json
import os
from dotenv import load_dotenv
import prompts
import re

# Load environment variables
load_dotenv()

# Check which API to use

def safe_print(text):
    """Safely print to console, handling encoding errors on Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            print(text.encode('utf-8', errors='ignore').decode('utf-8'))
        except:
            print(text.encode('ascii', errors='replace').decode('ascii'))
    except Exception:
        pass # Silent fail if printing is totally broken

# Prioritize IO.net Intelligence if key is present
# Prioritize IO.net Intelligence if key is present
# MODIFIED: Prioritize Gemini if requested
USE_GEMINI_FIRST = os.getenv("GEMINI_API_KEY") is not None
USE_IONET = os.getenv("IO_API_KEY") is not None
NO_API_KEY = False
client = None

if USE_GEMINI_FIRST:
    safe_print("USING GEMINI API (Primary)")
    USE_GEMINI = True
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # Configure Gemini model with JSON response
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }
elif USE_IONET:
    safe_print("USING IO.NET INTELLIGENCE API")
    USE_GEMINI = False
    from openai import OpenAI
    client = OpenAI(
        api_key=os.getenv("IO_API_KEY"),
        base_url=os.getenv("IO_BASE_URL")
    )
else:
    safe_print("⚠️ NO API KEY FOUND - USING MOCK MODE")
    NO_API_KEY = True


def parse_json_response(response_text: str) -> dict:
    """
    Robustly parses JSON from LLM response.
    Handles markdown code blocks, surrounding text, and unquoted keys.
    """
    cleaned = response_text.strip()
    
    # 1. Strip Markdown Code Blocks
    if "```" in cleaned:
        matches = re.findall(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
        if matches:
            cleaned = matches[0].strip()
        else:
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    # 2. Strip Comments (// and /* */)
    # Be careful with URLs (http://), but in this factory context, text usually doesn't have URLs.
    # We use a pattern that requires whitespace before // to be safer: \s//
    # Or start of line.
    cleaned = re.sub(r'(^|\s)//.*', '', cleaned)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

    # 3. Strip Trailing Commas (Common LLM error: {"a":1,})
    cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)

    # 4. Extract JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    
    if start != -1 and end != -1:
        cleaned = cleaned[start:end+1]
    elif start == -1:
         # Fallback: maybe it's a list?
         start_arr = cleaned.find("[")
         end_arr = cleaned.rfind("]")
         if start_arr != -1 and end_arr != -1:
             cleaned = cleaned[start_arr:end_arr+1]
         else:
             raise ValueError("No JSON object found (missing '{')")

    # 5. Try Parse & Repair
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            # Common Error: Unquoted keys {key: "value"}
            repaired = re.sub(r'(?<!")(\b\w+\b)(?=\s*:)', r'"\1"', cleaned)
            return json.loads(repaired)
        except:
             try:
                 # Single quotes to double quotes
                 repaired_quotes = cleaned.replace("'", '"')
                 return json.loads(repaired_quotes)
             except:
                 raise ValueError(f"JSON parse failed. Raw: {cleaned[:100]}...")

def clean_json_response(response_text: str) -> str:
    """DEPRECATED: Use parse_json_response"""
    return response_text # Dummy filler to avoid breaking imports if any, but we will update callers.



def simulate_decision(decision: str, context: str = "", factory_profile: dict = None, model: str = "gpt-4") -> dict:
    """
    Custom Agent: Simulates factory decision outcomes
    """
    try:
        if NO_API_KEY:
            safe_print("USING MOCK RESPONSE (No API Key)")
            return {
                "production_change_percent": 0,
                "cost_change_percent": 0,
                "risk_level": "Orta",
                "risk_explanation": "API Anahtarı bulunamadı (.env dosyası eksik). Lütfen .env dosyasını ayarlayın. Bu bir simülasyon yanıtıdır.",
                "side_effects": ["API Bağlantı Hatası"],
                "score_impact": 0,
                "budget_impact": 0,
                "satisfaction_impact": 0,
                "production_rate_impact": 0,
                "is_allowed": True
            }

        factory_context = ""
        if factory_profile:
            skills = factory_profile.get('employee_count', {}).get('skills', {})
            factory_context = f"""
FABRİKA PROFİLİ:
- Sektör: {factory_profile.get('sector', 'Genel Üretim')}
- Mevcut Durum: {factory_profile.get('current_status', 'Standart operasyon')}
- Çalışan Sayısı: {factory_profile.get('employee_count', {}).get('total', 200)} (Mavi Yaka: {factory_profile.get('employee_count', {}).get('blue_collar', 150)}, Beyaz Yaka: {factory_profile.get('employee_count', {}).get('white_collar', 20)})
- Aktif Sorunlar: {[i['title'] for i in factory_profile.get('active_issues', []) if isinstance(i, dict)]}
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
            gemini_model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
            prompt = f"{prompts.CUSTOM_AGENT_SYSTEM.format(factory_profile=factory_context, context=context)}\n\n{prompts.get_custom_agent_prompt(decision, context)}\n\nRespond ONLY with valid JSON format, no markdown code blocks."
            response = gemini_model.generate_content(prompt)
            response_text = response.text
        else:
            # Use OpenAI/io.net API
            response = client.chat.completions.create(
                model=os.getenv("IO_MODEL") or model,
                messages=[
                    {"role": "system", "content": prompts.CUSTOM_AGENT_SYSTEM.format(factory_profile=factory_context, context=context)},
                    {"role": "user", "content": prompts.get_custom_agent_prompt(decision, context)}
                ],
                temperature=0.3,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.3,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            response_text = response.choices[0].message.content or "{}"
            
        safe_print(f"DEBUG: Raw response: {repr(response_text)}")
            
        # Clean and parsing
        result = parse_json_response(response_text)
        
        return result

    except Exception as e:
        safe_print(f"====== ERROR in simulate_decision ======")
        safe_print(f"Decision: {decision}")
        try:
            import traceback
            traceback.print_exc()
        except Exception as trace_err:
            safe_print(f"Could not print traceback: {trace_err}")
            safe_print(f"Original Error: {e}")
        safe_print(f"====== END ERROR ======")
        
        # Fallback response with ACTUAL error message for debugging
        err_msg = str(e)
        return {
            "production_change_percent": 0,
            "cost_change_percent": 0,
            "cost_change_daily_tl": 0,
            "risk_level": "Orta",
            "risk_explanation": f"API Hatası: {err_msg[:150]}... (Loglara bakınız)",
            "side_effects": ["API Bağlantı Sorunu", err_msg[:50]],
            "score_impact": 0,
            "budget_impact": 0,
            "satisfaction_impact": 0,
            "production_rate_impact": 0,
            "is_investment": False,
            "investment_delay_weeks": 0,
            "investment_description": "",
            "delayed_production_impact": 0,
            "delayed_budget_impact": 0,
            "delayed_satisfaction_impact": 0,
            "research_analysis": None 
        }

def classify_risk(decision: str, result: dict, model: str = "gpt-4") -> dict:
    """
    Classification Agent: Classifies decision risk
    """
    try:
        if NO_API_KEY:
             return {
                "category": "Bilinmiyor",
                "explanation": "API Anahtarı eksik, risk analizi yapılamadı.",
                "recommendation": "Lütfen .env dosyasını kontrol edin."
            }

        if USE_GEMINI:
            # Use Gemini API
            gemini_model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
            prompt = f"{prompts.CLASSIFICATION_AGENT_SYSTEM}\n\n{prompts.get_classification_prompt(decision, result)}\n\nRespond ONLY with valid JSON format, no markdown code blocks."
            response = gemini_model.generate_content(prompt)
            response_text = response.text
        else:
            # Use OpenAI/io.net API
            response = client.chat.completions.create(
                model=os.getenv("IO_MODEL") or model,
                messages=[
                    {"role": "system", "content": prompts.CLASSIFICATION_AGENT_SYSTEM},
                    {"role": "user", "content": prompts.get_classification_prompt(decision, result)}
                ],
                temperature=0.3,
                top_p=0.9,
                frequency_penalty=0.3,
                response_format={"type": "json_object"}
            )
            response_text = response.choices[0].message.content or "{}"

        # Clean and parse
        classification = parse_json_response(response_text)
        
        return classification
    except Exception as e:
        safe_print(f"Error in classify_risk: {e}")
        return {
            "category": "Güvenli",
            "explanation": f"Sınıflandırma hatası: {str(e)}",
            "recommendation": ""
        }

def generate_summary(history: list, model: str = "gpt-4") -> str:
    """
    Summary Agent: Generates period summary report
    """
    if not history:
        return "## Henüz karar alınmadı\n\nKarar aldıkça burada özet göreceksiniz."
    
    try:
        if NO_API_KEY:
            return "## API Anahtarı Eksik\n\nÖzet oluşturmak için lütfen geçerli bir API anahtarı girin."

        if USE_GEMINI:
            # Use Gemini API
            gemini_model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
            prompt = f"{prompts.SUMMARY_AGENT_SYSTEM}\n\n{prompts.get_summary_prompt(history)}"
            response = gemini_model.generate_content(prompt)
            summary = response.text
        else:
            # Use OpenAI/io.net API
            response = client.chat.completions.create(
                model=os.getenv("IO_MODEL") or model,
                messages=[
                    {"role": "system", "content": prompts.SUMMARY_AGENT_SYSTEM},
                    {"role": "user", "content": prompts.get_summary_prompt(history)}
                ],
                temperature=0.6
            )
            summary = response.choices[0].message.content or "Özet oluşturulamadı (API Boş Yanıt)."
        
        return summary
    except Exception as e:
        safe_print(f"Error in generate_summary: {e}")
        return f"## Özet Hatası\n\nRapor oluşturulurken hata oluştu: {str(e)}"

def generate_random_event(factory_profile: dict, risk_level: float, month_number: int, model: str = "gpt-4", sentiment: str = "Neutral", event_type: str = None) -> dict:
    """
    Event Generator Agent: Generates contextual random events
    """
    try:
        if NO_API_KEY:
            return None

        if USE_GEMINI:
            # Use Gemini API
            gemini_model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
            prompt = f"{prompts.get_event_generator_prompt(factory_profile, risk_level, month_number, sentiment, event_type)}\n\nRespond ONLY with valid JSON format, no markdown code blocks."
            response = gemini_model.generate_content(prompt)
            response_text = response.text
        else:
            # Use OpenAI/io.net API
            response = client.chat.completions.create(
                model=os.getenv("IO_MODEL") or model,
                messages=[
                    {"role": "system", "content": "You are an event generator. Respond in JSON."},
                    {"role": "user", "content": prompts.get_event_generator_prompt(factory_profile, risk_level, month_number, sentiment, event_type)}
                ],
                temperature=0.4,
                top_p=0.95,
                frequency_penalty=0.5,
                response_format={"type": "json_object"}
            )
            response_text = response.choices[0].message.content or "{}"

        # Clean and parse
        event = parse_json_response(response_text)
        
        # Return None if no event
        if not event.get('has_event', False):
            return None
            
        return event
    except Exception as e:
        safe_print(f"Error in generate_random_event: {e}")
        return None
