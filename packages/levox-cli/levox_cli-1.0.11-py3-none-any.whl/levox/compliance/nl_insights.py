"""
Natural Language Compliance Insights

Generates concise, human-readable prompts such as
"Why are you collecting this data here?" for surfaced findings.
"""

from __future__ import annotations

from typing import Any, Dict, List


def generate_nl_insights(results: Any, max_per_file: int = 3, max_total: int = 50) -> List[Dict[str, Any]]:
    """Generate NL compliance prompts from scan results.

    Args:
        results: DetectionResult-like object with file_results[].matches[]
        max_per_file: limit per file
        max_total: overall cap

    Returns:
        List of NL insights dictionaries
    """
    insights: List[Dict[str, Any]] = []
    if not hasattr(results, 'file_results'):
        return insights

    total = 0
    for file_result in results.file_results:
        per_file = 0
        file_path = getattr(file_result, 'file_path', 'unknown')
        for m in getattr(file_result, 'matches', []) or []:
            if per_file >= max_per_file or total >= max_total:
                break
            title = "Potential unwanted data collection"
            pn = getattr(m, 'pattern_name', None) or getattr(m, 'rule_id', 'personal_data')
            line = getattr(m, 'line', None) or getattr(m, 'line_number', None) or 0
            desc = f"Why are you collecting {pn.replace('_', ' ')} in '{file_path}' at line {line}?"
            sev = (getattr(m, 'severity', 'medium') or 'medium').lower()
            conf = float(getattr(m, 'confidence', 0.6) or 0.6)
            insight = {
                'id': f"{file_path}:{line}:{pn}",
                'insight_type': 'nl_compliance_question',
                'title': title,
                'description': desc,
                'confidence': min(0.95, max(0.4, conf)),
                'impact_score': 0.8 if sev in ('critical', 'high') else 0.4,
                'risk_level': sev,
                'affected_areas': ['data_collection', 'privacy'],
                'recommendations': [
                    'Remove or mask the data if unnecessary',
                    'Document legitimate interest and minimization rationale',
                    'Add input validation and redaction at source'
                ]
            }
            insights.append(insight)
            per_file += 1
            total += 1
            if total >= max_total:
                break

    return insights


