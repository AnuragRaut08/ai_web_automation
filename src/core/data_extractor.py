from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self, ai_agent):
        self.ai_agent = ai_agent
    
    def extract_users_from_table(self, html_content: str) -> List[Dict[str, str]]:
        """Extract user data from HTML table"""
        soup = BeautifulSoup(html_content, 'html.parser')
        users = []
        
        # Find potential user tables
        tables = soup.find_all('table')
        for table in tables:
            if self._is_user_table(table):
                users.extend(self._parse_user_table(table))
        
        # If no tables found, try AI extraction
        if not users:
            users = self.ai_agent.extract_user_data(html_content)
        
        return users
    
    def _is_user_table(self, table) -> bool:
        """Determine if table contains user data"""
        headers = table.find_all('th')
        header_text = ' '.join([th.get_text().lower() for th in headers])
        
        user_indicators = ['name', 'email', 'user', 'member', 'role', 'permission']
        return any(indicator in header_text for indicator in user_indicators)
    
    def _parse_user_table(self, table) -> List[Dict[str, str]]:
        """Parse user data from table"""
        users = []
        rows = table.find_all('tr')
        
        if not rows:
            return users
        
        # Get headers
        headers = [th.get_text().strip().lower() for th in rows[0].find_all(['th', 'td'])]
        
        # Process data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= len(headers):
                user_data = {}
                for i, cell in enumerate(cells[:len(headers)]):
                    if i < len(headers):
                        user_data[headers[i]] = cell.get_text().strip()
                
                # Normalize field names
                normalized_user = self._normalize_user_data(user_data)
                if normalized_user.get('email'):  # Must have email
                    users.append(normalized_user)
        
        return users
    
    def _normalize_user_data(self, user_data: Dict[str, str]) -> Dict[str, str]:
        """Normalize field names and data"""
        normalized = {}
        
        # Field mappings
        field_mappings = {
            'name': ['name', 'full_name', 'display_name', 'user_name'],
            'email': ['email', 'email_address', 'mail'],
            'role': ['role', 'permission', 'access_level', 'type'],
            'last_login': ['last_login', 'last_seen', 'last_active'],
            'status': ['status', 'state', 'active']
        }
        
        for standard_field, possible_fields in field_mappings.items():
            for field in possible_fields:
                if field in user_data:
                    normalized[standard_field] = user_data[field]
                    break
        
        return normalized
    
    def extract_pagination_info(self, html_content: str) -> Dict[str, Any]:
        """Extract pagination information"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for pagination elements
        pagination_selectors = [
            '.pagination',
            '.pager',
            '[class*="page"]',
            '[class*="next"]',
            '[class*="prev"]'
        ]
        
        pagination_info = {
            'has_next': False,
            'has_previous': False,
            'current_page': 1,
            'total_pages': 1,
            'next_selector': None,
            'prev_selector': None
        }
        
        for selector in pagination_selectors:
            elements = soup.select(selector)
            if elements:
                # Analyze pagination structure
                pagination_info.update(self._analyze_pagination(elements[0]))
                break
        
        return pagination_info
    
    def _analyze_pagination(self, pagination_element) -> Dict[str, Any]:
        """Analyze pagination element structure"""
        info = {}
        
        # Look for next/previous buttons
        next_button = pagination_element.find(['a', 'button'], text=re.compile(r'next|>', re.I))
        prev_button = pagination_element.find(['a', 'button'], text=re.compile(r'prev|<', re.I))
        
        info['has_next'] = next_button is not None and not next_button.get('disabled')
        info['has_previous'] = prev_button is not None and not prev_button.get('disabled')
        
        if next_button:
            info['next_selector'] = self._get_element_selector(next_button)
        if prev_button:
            info['prev_selector'] = self._get_element_selector(prev_button)
        
        return info
    
    def _get_element_selector(self, element) -> str:
        """Generate CSS selector for element"""
        # Simple selector generation
        if element.get('id'):
            return f"#{element['id']}"
        elif element.get('class'):
            classes = ' '.join(element['class'])
            return f".{classes.replace(' ', '.')}"
        else:
            return element.name

