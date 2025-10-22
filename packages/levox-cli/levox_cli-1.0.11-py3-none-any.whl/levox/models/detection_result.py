"""
Data models for detection results and file analysis.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

from pydantic import BaseModel, Field
from ..core.config import RiskLevel


@dataclass
class DetectionMatch:
    """Represents a single PII detection match with enhanced context."""
    
    # Core identification
    file: str
    line: int
    engine: str  # regex/ast/ml/dataflow/context
    rule_id: str
    severity: str
    confidence: float
    snippet: str
    description: str
    
    # Enhanced context fields
    pattern_name: str = ""
    matched_text: str = ""
    column_start: int = 0
    column_end: int = 0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Context and validation
    context_before: str = ""
    context_after: str = ""
    false_positive: bool = False
    validated: bool = False
    legitimate_usage_flag: bool = False
    
    # Metadata and timing
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_info: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    scan_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-like access for compatibility with context analyzer."""
        return getattr(self, key, default)
    
    @property
    def line_number(self) -> int:
        """Backward compatibility property."""
        return self.line
    
    @property
    def pattern_regex(self) -> str:
        """Backward compatibility property."""
        return self.metadata.get('pattern_regex', '')


@dataclass
class FileResult:
    """Represents the analysis result for a single file."""
    
    file_path: Path
    file_size: int
    language: str
    total_lines: int
    scan_time: float
    matches: List[DetectionMatch] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def match_count(self) -> int:
        """Get total number of matches."""
        return len(self.matches)
    
    @property
    def high_risk_matches(self) -> List[DetectionMatch]:
        """Get high-risk matches."""
        return [m for m in self.matches if m.severity in ['HIGH', 'CRITICAL']]
    
    @property
    def false_positive_count(self) -> int:
        """Get count of false positives."""
        return len([m for m in self.matches if m.false_positive])
    
    def add_match(self, match: DetectionMatch) -> None:
        """Add a detection match to this file."""
        self.matches.append(match)
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = asdict(self)
        data['file_path'] = str(self.file_path)
        data['match_count'] = self.match_count
        data['high_risk_matches'] = len(self.high_risk_matches)
        data['false_positive_count'] = self.false_positive_count
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=2)


class DetectionResult(BaseModel):
    """Main result container for a complete scan - single source of truth."""
    
    scan_id: str = Field(..., description="Unique identifier for this scan")
    scan_timestamp: datetime = Field(default_factory=datetime.utcnow)
    scan_duration: float = Field(..., description="Total scan duration in seconds")
    
    # Configuration
    config_version: str = Field(default="1.0.0")
    license_tier: str = Field(..., description="License tier used for scanning")
    scan_path: str = Field(..., description="Path that was scanned")
    
    # Results
    files_scanned: int = Field(..., description="Total number of files scanned")
    files_with_matches: int = Field(..., description="Number of files with PII matches")
    total_matches: int = Field(..., description="Total number of PII matches found")
    
    # Performance metrics
    total_scan_time: float = Field(..., description="Total time spent scanning")
    average_file_time: float = Field(..., description="Average time per file")
    memory_peak_mb: float = Field(..., description="Peak memory usage in MB")
    
    # Quality metrics
    false_positive_rate: float = Field(..., description="Estimated false positive rate")
    confidence_average: float = Field(..., description="Average confidence score")
    
    # File results
    file_results: List[FileResult] = Field(default_factory=list)
    
    # Summary
    risk_summary: Dict[str, int] = Field(default_factory=dict)
    pattern_summary: Dict[str, int] = Field(default_factory=dict)
    engine_summary: Dict[str, int] = Field(default_factory=dict)  # New: per-engine counts
    
    # Optional scan metadata for external tools/tests
    scan_metadata: Dict[str, Any] | None = None
    
    # Compliance analysis data
    compliance_data: Optional[Dict[str, Any]] = None
    
    # Errors and warnings
    scan_errors: List[str] = Field(default_factory=list)
    scan_warnings: List[str] = Field(default_factory=list)
    
    model_config = {
        "json_encoders": {
            Path: str,
            datetime: lambda v: v.isoformat(),
        }
    }
    
    def add_file_result(self, file_result: FileResult) -> None:
        """Add a file result to the scan results."""
        self.file_results.append(file_result)
        self.files_scanned += 1
        
        if file_result.match_count > 0:
            self.files_with_matches += 1
        
        self.total_matches += file_result.match_count
        
        # Update risk summary
        for match in file_result.matches:
            risk_key = match.severity
            self.risk_summary[risk_key] = self.risk_summary.get(risk_key, 0) + 1
            
            pattern_key = match.pattern_name
            self.pattern_summary[pattern_key] = self.pattern_summary.get(pattern_key, 0) + 1
            
            # Update engine summary
            engine_key = match.engine
            self.engine_summary[engine_key] = self.engine_summary.get(engine_key, 0) + 1
    
    def calculate_metrics(self) -> None:
        """Calculate derived metrics."""
        if self.files_scanned > 0:
            self.average_file_time = self.total_scan_time / self.files_scanned
        
        # Calculate confidence average
        total_confidence = 0.0
        confidence_count = 0
        for fr in self.file_results:
            if hasattr(fr, 'matches'):
                for match in fr.matches:
                    if hasattr(match, 'confidence') and match.confidence is not None:
                        total_confidence += match.confidence
                        confidence_count += 1
        
        if confidence_count > 0:
            self.confidence_average = total_confidence / confidence_count
        
        # Calculate false positive rate estimate
        total_false_positives = 0
        for fr in self.file_results:
            if hasattr(fr, 'false_positive_count'):
                total_false_positives += fr.false_positive_count
        if self.total_matches > 0:
            self.false_positive_rate = total_false_positives / self.total_matches
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'scan_id': self.scan_id,
            'scan_path': self.scan_path,
            'files_scanned': self.files_scanned,
            'files_with_matches': self.files_with_matches,
            'total_matches': self.total_matches,
            'scan_duration': self.scan_duration,
            'license_tier': self.license_tier,
            'risk_summary': self.risk_summary,
            'pattern_summary': self.pattern_summary,
            'engine_summary': self.engine_summary
        }
    
    def get_engine_timing_summary(self) -> Dict[str, float]:
        """Get engine timing summary."""
        timing_summary = {}
        for fr in self.file_results:
            if hasattr(fr, 'metadata') and 'stage_times' in fr.metadata:
                for stage, time_val in fr.metadata['stage_times'].items():
                    if stage not in timing_summary:
                        timing_summary[stage] = 0.0
                    timing_summary[stage] += time_val
        return timing_summary
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.model_dump(), indent=indent, default=str)
    
    def save_to_file(self, file_path: str) -> None:
        """Save DetectionResult to a file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @staticmethod
    def _safe_risk_level(risk_level_value: Any) -> RiskLevel:
        """Safely convert risk level value to RiskLevel enum."""
        if risk_level_value is None:
            return RiskLevel.MEDIUM
        
        # If it's already a RiskLevel enum, return it
        if isinstance(risk_level_value, RiskLevel):
            return risk_level_value
        
        # If it has a 'value' attribute (like an enum), get the value
        if hasattr(risk_level_value, 'value'):
            try:
                return RiskLevel(risk_level_value.value)
            except (ValueError, TypeError):
                pass
        
        # Try to convert string/int to RiskLevel
        try:
            return RiskLevel(str(risk_level_value).lower())
        except (ValueError, TypeError):
            return RiskLevel.MEDIUM

    @classmethod
    def from_file(cls, file_path: str) -> 'DetectionResult':
        """Load DetectionResult from a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert file_results back to FileResult objects
        if 'file_results' in data:
            file_results = []
            for fr_data in data['file_results']:
                # Convert matches back to DetectionMatch objects
                matches = []
                for match_data in fr_data.get('matches', []):
                    match = DetectionMatch(
                        file=match_data.get('file', ''),
                        line=match_data.get('line', 0),
                        engine=match_data.get('engine', 'regex'),
                        rule_id=match_data.get('rule_id', ''),
                        severity=match_data.get('severity', 'MEDIUM'),
                        confidence=match_data.get('confidence', 0.0),
                        snippet=match_data.get('snippet', ''),
                        description=match_data.get('description', ''),
                        pattern_name=match_data.get('pattern_name', ''),
                        matched_text=match_data.get('matched_text', ''),
                        column_start=match_data.get('column_start', 0),
                        column_end=match_data.get('column_end', 0),
                        risk_level=self._safe_risk_level(match_data.get('risk_level', 'MEDIUM')),
                        context_before=match_data.get('context_before', ''),
                        context_after=match_data.get('context_after', ''),
                        false_positive=match_data.get('false_positive', False),
                        validated=match_data.get('validated', False),
                        legitimate_usage_flag=match_data.get('legitimate_usage_flag', False),
                        metadata=match_data.get('metadata', {}),
                        context_info=match_data.get('context_info', {}),
                        confidence_score=match_data.get('confidence_score', 0.0),
                        scan_timestamp=datetime.fromisoformat(match_data.get('scan_timestamp', datetime.utcnow().isoformat()))
                    )
                    matches.append(match)
                
                # Create FileResult
                fr = FileResult(
                    file_path=Path(fr_data.get('file_path', '')),
                    file_size=fr_data.get('file_size', 0),
                    language=fr_data.get('language', ''),
                    total_lines=fr_data.get('total_lines', 0),
                    scan_time=fr_data.get('scan_time', 0.0),
                    matches=matches,
                    errors=fr_data.get('errors', []),
                    warnings=fr_data.get('warnings', []),
                    metadata=fr_data.get('metadata', {})
                )
                file_results.append(fr)
            
            data['file_results'] = file_results
        
        return cls(**data)
