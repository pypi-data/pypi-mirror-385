#!/usr/bin/env python3
"""
Findings Manager for QINA Security Editor
Handles saving and loading detailed findings to/from temporary files
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class DetailedFinding:
    """Data class for detailed vulnerability finding"""
    id: str
    title: str
    severity: str
    file: str
    line: int
    type: str
    language: Optional[str] = None
    rule_id: Optional[str] = None
    description: Optional[str] = None
    code_snippet: Optional[str] = None
    cwe: Optional[str] = None
    references: Optional[List[str]] = None
    timestamp: Optional[str] = None

class FindingsManager:
    """Manages detailed findings storage and retrieval"""
    
    def __init__(self, tmp_dir: Path = None):
        self.tmp_dir = tmp_dir or Path("/tmp/qina_security_scan")
        self.findings_file = self.tmp_dir / "detailed_findings.json"
        self.findings: List[DetailedFinding] = []
        
    def save_findings(self, findings_data: List[Dict[str, Any]]) -> bool:
        """
        Save detailed findings to temporary file
        
        Args:
            findings_data: List of finding dictionaries from scan results
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert findings data to DetailedFinding objects
            findings = []
            for finding_data in findings_data:
                finding = DetailedFinding(
                    id=finding_data.get('id', 'UNKNOWN'),
                    title=finding_data.get('title', 'Unknown Finding'),
                    severity=finding_data.get('severity', 'unknown'),
                    file=finding_data.get('file', 'unknown'),
                    line=finding_data.get('line', 0),
                    type=finding_data.get('type', 'unknown'),
                    language=finding_data.get('language'),
                    rule_id=finding_data.get('rule_id'),
                    description=finding_data.get('description'),
                    code_snippet=finding_data.get('code_snippet'),
                    cwe=finding_data.get('cwe'),
                    references=finding_data.get('references'),
                    timestamp=datetime.now().isoformat()
                )
                findings.append(finding)
            
            # Ensure tmp directory exists
            self.tmp_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to JSON file
            with open(self.findings_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(finding) for finding in findings], f, indent=2)
            
            self.findings = findings
            return True
            
        except Exception as e:
            print(f"Error saving findings: {e}")
            return False
    
    def load_findings(self) -> List[DetailedFinding]:
        """
        Load detailed findings from temporary file
        
        Returns:
            List[DetailedFinding]: List of loaded findings
        """
        try:
            if not self.findings_file.exists():
                return []
            
            with open(self.findings_file, 'r', encoding='utf-8') as f:
                findings_data = json.load(f)
            
            findings = []
            for finding_data in findings_data:
                finding = DetailedFinding(**finding_data)
                findings.append(finding)
            
            self.findings = findings
            return findings
            
        except Exception as e:
            print(f"Error loading findings: {e}")
            return []
    
    def get_findings_by_severity(self, severity: str) -> List[DetailedFinding]:
        """
        Get findings filtered by severity
        
        Args:
            severity: Severity level (critical, high, medium, low)
            
        Returns:
            List[DetailedFinding]: Filtered findings
        """
        if not self.findings:
            self.load_findings()
        
        return [f for f in self.findings if f.severity.lower() == severity.lower()]
    
    def get_findings_by_classification(self, classification: str) -> List[DetailedFinding]:
        """
        Get findings filtered by classification
        
        Args:
            classification: Classification type (must fix, good to fix, false positive)
            
        Returns:
            List[DetailedFinding]: Filtered findings
        """
        if not self.findings:
            self.load_findings()
        
        # Note: classification is not currently stored in DetailedFinding
        # This would need to be added if classification filtering is needed
        return []
    
    def clear_findings(self) -> bool:
        """
        Clear all findings from temporary file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.findings_file.exists():
                self.findings_file.unlink()
            self.findings = []
            return True
        except Exception as e:
            print(f"Error clearing findings: {e}")
            return False
    
    def has_findings(self) -> bool:
        """
        Check if findings exist
        
        Returns:
            bool: True if findings exist, False otherwise
        """
        if not self.findings:
            self.load_findings()
        return len(self.findings) > 0
    
    def get_findings_file_path(self) -> Path:
        """
        Get the path to the findings file
        
        Returns:
            Path: Path to findings file
        """
        return self.findings_file
    
    def get_findings_summary(self) -> Dict[str, int]:
        """
        Get summary of findings by severity
        
        Returns:
            Dict[str, int]: Count of findings by severity
        """
        if not self.findings:
            self.load_findings()
        
        summary = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'total': len(self.findings)
        }
        
        for finding in self.findings:
            severity = finding.severity.lower()
            if severity in summary:
                summary[severity] += 1
        
        return summary
