import openai
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def analyze_page_structure(self, html_content: str, task: str) -> Dict[str, Any]:
        """Analyze page structure and return element selectors"""
        prompt = f"""
        Analyze this HTML content and identify elements for the task: {task}
        
        HTML Content (truncated):
        {html_content[:5000]}...
        
        Return a JSON object with:
        - selectors: CSS selectors for relevant elements
        - actions: Recommended actions to take
        - confidence: Confidence score (0-1)
        
        Focus on finding:
        - User management tables/lists
        - Login forms
        - Navigation elements
        - Action buttons (Add User, Remove User, etc.)
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert web scraping AI that analyzes HTML structure."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"selectors": {}, "actions": [], "confidence": 0.0}
    
    def extract_user_data(self, html_content: str) -> List[Dict[str, str]]:
        """Extract user data from HTML"""
        prompt = f"""
        Extract user information from this HTML content:
        
        {html_content[:8000]}...
        
        Return a JSON array of user objects with fields:
        - name: User's full name
        - email: Email address
        - role: User role/permission level
        - last_login: Last login date (if available)
        - status: Account status (active/inactive)
        
        Only return valid, complete user records.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data extraction specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"User data extraction failed: {e}")
            return []
    
    def generate_automation_steps(self, task: str, page_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate step-by-step automation instructions"""
        prompt = f"""
        Generate automation steps for task: {task}
        
        Based on page analysis:
        {json.dumps(page_analysis, indent=2)}
        
        Return a JSON array of steps with:
        - action: Type of action (click, type, wait, etc.)
        - selector: CSS selector for element
        - value: Value to input (if applicable)
        - description: Human-readable description
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an automation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Step generation failed: {e}")
            return []

