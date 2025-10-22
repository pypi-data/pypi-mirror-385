"""
Query validator for SQL injection protection and read-only enforcement.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from mcp_core.app_config import get_readonly_db

logger = logging.getLogger(__name__)

class QueryValidatorBase:
    """Base class for SQL query validation (read-only and injection protection). Subclass for each engine."""
    DANGEROUS_KEYWORDS: List[str] = []
    DANGEROUS_STARTS: List[str] = []
    SAFE_KEYWORDS: List[str] = []
    SUSPICIOUS_PATTERNS: List[str] = []

    def __init__(self):
        self.readonly_mode = get_readonly_db()

    def validate_query(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "is_readonly": True
        }
        normalized_query = self._normalize_query(query)
        injection_check = self._check_sql_injection(normalized_query, params)
        if not injection_check["is_safe"]:
            result["is_valid"] = False
            result["errors"].extend(injection_check["errors"])
        result["warnings"].extend(injection_check.get("warnings", []))
        dangerous_check = self._check_dangerous_operations(normalized_query)
        if dangerous_check["has_dangerous_operations"]:
            result["is_readonly"] = False
            if self.readonly_mode:
                result["is_valid"] = False
                result["errors"].append(f"Read-only mode is enabled. Data modification operations are not allowed. Trigger: {dangerous_check['triggered']}")
            else:
                result["warnings"].extend(dangerous_check["warnings"])
        structure_check = self._check_query_structure(normalized_query)
        if not structure_check["is_valid"]:
            result["is_valid"] = False
            result["errors"].extend(structure_check["errors"])
        return result

    def _normalize_query(self, query: str) -> str:
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        query = re.sub(r'\s+', ' ', query.strip())
        return query.upper()

    def _check_sql_injection(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        result = {
            "is_safe": True,
            "errors": [],
            "warnings": []
        }
        for pattern in self.SUSPICIOUS_PATTERNS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                result["warnings"].append(f"Potential SQL injection pattern detected: {pattern} at {match.start()}")
        if query.count(';') > 1:
            result["is_safe"] = False
            result["errors"].append("Multiple SQL statements are not allowed")
        if params:
            placeholder_count = query.count('?') + query.count('%s')
            param_count = len(params)
            if placeholder_count != param_count:
                result["warnings"].append("Parameter count mismatch detected")
        return result

    def _check_dangerous_operations(self, query: str) -> Dict[str, Any]:
        result = {
            "has_dangerous_operations": False,
            "warnings": [],
            "triggered": None
        }
        tokens = re.findall(r'\b\w+\b', query)
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in tokens:
                result["has_dangerous_operations"] = True
                result["warnings"].append(f"Dangerous operation detected: {keyword}")
                result["triggered"] = keyword
        for start in self.DANGEROUS_STARTS:
            if query.startswith(start):
                result["has_dangerous_operations"] = True
                result["warnings"].append(f"Dangerous statement detected: {start}")
                result["triggered"] = start
        return result

    def _check_query_structure(self, query: str) -> Dict[str, Any]:
        result = {
            "is_valid": True,
            "errors": []
        }
        if not query or query.isspace():
            result["is_valid"] = False
            result["errors"].append("Query cannot be empty")
            return result
        if query.count('(') != query.count(')'):
            result["is_valid"] = False
            result["errors"].append("Unbalanced parentheses in query")
        if query.startswith('SELECT') and 'FROM' not in query:
            result["warnings"].append("SELECT query missing FROM clause")
        return result

    def is_readonly_query(self, query: str) -> bool:
        normalized_query = self._normalize_query(query)
        dangerous_check = self._check_dangerous_operations(normalized_query)
        return not dangerous_check["has_dangerous_operations"]

    def sanitize_query(self, query: str) -> str:
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        if query.count(';') > 1:
            query = query.split(';')[0] + ';'
        return query.strip()

    def get_query_type(self, query: str) -> str:
        normalized_query = self._normalize_query(query)
        for keyword in self.DANGEROUS_KEYWORDS:
            if normalized_query.startswith(keyword):
                return keyword
        for keyword in self.SAFE_KEYWORDS:
            if normalized_query.startswith(keyword):
                return keyword
        return "UNKNOWN" 