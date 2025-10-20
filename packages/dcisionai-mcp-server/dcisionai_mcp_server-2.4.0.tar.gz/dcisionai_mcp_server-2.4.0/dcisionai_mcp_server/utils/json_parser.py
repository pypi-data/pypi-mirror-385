#!/usr/bin/env python3
"""
Enhanced JSON parsing with comprehensive error handling and recovery
"""

import json
import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


def parse_json(text: str) -> Dict[str, Any]:
    """Enhanced JSON parsing with comprehensive error handling and recovery"""
    if not text:
        return {"raw_response": ""}
    
    # Enhanced text cleaning
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = re.sub(r',(\s*[}\]])', r'\1', text)  # Remove trailing commas
    text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)  # Quote unquoted keys
    text = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*([,}])', r': "\1"\2', text)  # Quote unquoted string values
    text = text.strip()
    
    # Try direct parsing first
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError as e:
        logger.debug(f"Direct JSON parsing failed: {e}")
    
    # Try to find JSON object in the text - look for the first complete JSON object
    try:
        # Find the first opening brace
        start_pos = text.find('{')
        if start_pos == -1:
            raise ValueError("No opening brace found")
        
        # Count braces to find the matching closing brace
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_pos, len(text)):
            char = text[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found matching closing brace
                        json_text = text[start_pos:i+1]
                        
                        # Enhanced cleaning
                        json_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_text)  # Control characters
                        json_text = re.sub(r'\\n', ' ', json_text)  # Newlines in strings
                        json_text = re.sub(r'\\t', ' ', json_text)  # Tabs in strings
                        json_text = re.sub(r'\\r', ' ', json_text)  # Carriage returns
                        
                        result = json.loads(json_text)
                        if isinstance(result, dict):
                            return result
                        break
        
        # If we get here, no matching closing brace was found
        raise ValueError("No matching closing brace found")
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.debug(f"Brace counting JSON parsing failed: {e}")
    
    # Try regex fallback with improved patterns
    try:
        # Try multiple regex patterns for different JSON structures
        patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Original pattern
            r'\{[^{}]*"[^"]*"[^{}]*\}',  # Pattern for quoted strings
            r'\{[^{}]*:[^{}]*\}',  # Pattern for key-value pairs
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    json_text = match.group(0)
                    # Enhanced cleaning
                    json_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_text)
                    json_text = re.sub(r'\\n', ' ', json_text)
                    json_text = re.sub(r'\\t', ' ', json_text)
                    json_text = re.sub(r'\\r', ' ', json_text)
                    
                    result = json.loads(json_text)
                    if isinstance(result, dict):
                        return result
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logger.debug(f"Regex JSON parsing failed: {e}")
    
    # Try to extract partial JSON and fix common issues
    try:
        # Find the largest potential JSON object
        start_pos = text.find('{')
        if start_pos != -1:
            # Try to find a reasonable end point
            end_pos = text.rfind('}')
            if end_pos > start_pos:
                json_text = text[start_pos:end_pos+1]
                
                # Try to fix common JSON issues
                json_text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_text)
                json_text = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*([,}])', r': "\1"\2', json_text)
                json_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_text)
                
                result = json.loads(json_text)
                if isinstance(result, dict):
                    return result
    except Exception as e:
        logger.debug(f"Partial JSON parsing failed: {e}")
    
    # If all else fails, return raw response with debug info
    logger.warning(f"JSON parsing failed for text: {text[:200]}...")
    return {"raw_response": text}
