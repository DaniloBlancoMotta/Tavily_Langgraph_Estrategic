"""
Immutable Audit Log

Provides cryptographically-secured, immutable audit logs of all agent transitions:
- Timestamp precision
- Input/Output tracking
- Reasoning capture
- Hash-chain verification
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class LogEntry:
    """A single immutable log entry"""
    log_id: str
    sequence_number: int
    timestamp: str
    event_type: str  # transition, error, metric, decision
    level: str  # info, warning, error, critical
    
    # Core data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    
    # Context
    thread_id: str = ""
    node_from: str = ""
    node_to: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Integrity
    previous_hash: str = ""
    entry_hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def compute_hash(self) -> str:
        """Compute hash of this entry for integrity checking"""
        # Create deterministic string representation
        data = {
            "log_id": self.log_id,
            "sequence_number": self.sequence_number,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "level": self.level,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "reasoning": self.reasoning,
            "thread_id": self.thread_id,
            "node_from": self.node_from,
            "node_to": self.node_to,
            "previous_hash": self.previous_hash
        }
        
        # Convert to canonical JSON
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
        
        # Compute SHA-256 hash
        return hashlib.sha256(canonical.encode()).hexdigest()


class ImmutableAuditLog:
    """
    Immutable, append-only audit log with cryptographic verification.
    
    Features:
    - Hash-chain linking (blockchain-style)
    - Tamper detection
    - Full history replay
    - Export capabilities
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("data/monitoring/audit_logs")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.entries: List[LogEntry] = []
        self.sequence_counter: int = 0
        self.current_log_file: Optional[Path] = None
        
        # Initialize new log file
        self._init_log_file()
    
    def _init_log_file(self):
        """Initialize a new log file"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.current_log_file = self.storage_path / f"audit_log_{timestamp}.jsonl"
        
        # Write header
        header = {
            "type": "LOG_HEADER",
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "format": "jsonl"
        }
        
        with open(self.current_log_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(header) + "\n")
    
    def log_transition(
        self,
        thread_id: str,
        node_from: str,
        node_to: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        reasoning: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> LogEntry:
        """
        Log a state transition (the primary use case).
        
        Args:
            thread_id: Thread identifier
            node_from: Source node
            node_to: Destination node
            input_data: Input to the transition
            output_data: Output from the transition
            reasoning: Reasoning for the transition
            metadata: Optional metadata
            tags: Optional tags
            
        Returns:
            Created log entry
        """
        return self._create_entry(
            event_type="transition",
            level="info",
            thread_id=thread_id,
            node_from=node_from,
            node_to=node_to,
            input_data=input_data,
            output_data=output_data,
            reasoning=reasoning,
            metadata=metadata or {},
            tags=tags or []
        )
    
    def log_error(
        self,
        thread_id: str,
        error_message: str,
        error_type: str,
        context: Dict[str, Any],
        stack_trace: Optional[str] = None
    ) -> LogEntry:
        """Log an error"""
        return self._create_entry(
            event_type="error",
            level="error",
            thread_id=thread_id,
            reasoning=error_message,
            input_data={
                "error_type": error_type,
                "stack_trace": stack_trace
            },
            output_data=context
        )
    
    def log_metric(
        self,
        thread_id: str,
        metric_name: str,
        metric_value: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> LogEntry:
        """Log a metric measurement"""
        return self._create_entry(
            event_type="metric",
            level="info",
            thread_id=thread_id,
            input_data={"metric_name": metric_name},
            output_data={
                "value": metric_value,
                "context": context or {}
            }
        )
    
    def log_decision(
        self,
        thread_id: str,
        decision_type: str,
        reasoning: str,
        selected_action: str,
        alternatives: List[str],
        confidence: float
    ) -> LogEntry:
        """Log a decision point"""
        return self._create_entry(
            event_type="decision",
            level="info",
            thread_id=thread_id,
            reasoning=reasoning,
            input_data={
                "decision_type": decision_type,
                "alternatives": alternatives
            },
            output_data={
                "selected_action": selected_action,
                "confidence": confidence
            }
        )
    
    def _create_entry(
        self,
        event_type: str,
        level: str,
        thread_id: str = "",
        node_from: str = "",
        node_to: str = "",
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        reasoning: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> LogEntry:
        """Create a new log entry"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Generate log ID
        log_data = f"{timestamp}_{self.sequence_counter}_{event_type}_{thread_id}"
        log_id = hashlib.sha256(log_data.encode()).hexdigest()[:16]
        
        # Get previous hash
        previous_hash = ""
        if self.entries:
            previous_hash = self.entries[-1].entry_hash
        
        # Create entry
        entry = LogEntry(
            log_id=log_id,
            sequence_number=self.sequence_counter,
            timestamp=timestamp,
            event_type=event_type,
            level=level,
            input_data=self._sanitize_data(input_data or {}),
            output_data=self._sanitize_data(output_data or {}),
            reasoning=reasoning,
            thread_id=thread_id,
            node_from=node_from,
            node_to=node_to,
            metadata=metadata or {},
            tags=tags or [],
            previous_hash=previous_hash
        )
        
        # Compute and set hash
        entry.entry_hash = entry.compute_hash()
        
        # Append to log
        self.entries.append(entry)
        self.sequence_counter += 1
        
        # Persist to disk
        self._persist_entry(entry)
        
        return entry
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for logging"""
        sanitized = {}
        
        for key, value in data.items():
            # Truncate large strings
            if isinstance(value, str) and len(value) > 3000:
                sanitized[key] = value[:3000] + "...<truncated>"
            # Truncate large lists
            elif isinstance(value, list) and len(value) > 20:
                sanitized[key] = value[:20] + ["...<truncated>"]
            # Handle non-serializable objects
            else:
                try:
                    json.dumps(value)
                    sanitized[key] = value
                except (TypeError, ValueError):
                    sanitized[key] = str(value)[:500]
        
        return sanitized
    
    def _persist_entry(self, entry: LogEntry):
        """Persist entry to disk (append-only)"""
        if not self.current_log_file:
            self._init_log_file()
        
        with open(self.current_log_file, "a", encoding="utf-8") as f:
            f.write(entry.to_json(indent=None) + "\n")
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify the integrity of the log chain.
        
        Returns:
            Verification results
        """
        if not self.entries:
            return {
                "valid": True,
                "message": "No entries to verify"
            }
        
        errors = []
        
        for i, entry in enumerate(self.entries):
            # Verify hash
            computed_hash = entry.compute_hash()
            if computed_hash != entry.entry_hash:
                errors.append({
                    "sequence": i,
                    "log_id": entry.log_id,
                    "error": "Hash mismatch - entry may be tampered",
                    "expected": entry.entry_hash,
                    "computed": computed_hash
                })
            
            # Verify chain
            if i > 0:
                expected_prev_hash = self.entries[i - 1].entry_hash
                if entry.previous_hash != expected_prev_hash:
                    errors.append({
                        "sequence": i,
                        "log_id": entry.log_id,
                        "error": "Chain broken - previous hash mismatch",
                        "expected": expected_prev_hash,
                        "found": entry.previous_hash
                    })
            
            # Verify sequence
            if entry.sequence_number != i:
                errors.append({
                    "sequence": i,
                    "log_id": entry.log_id,
                    "error": "Sequence number mismatch",
                    "expected": i,
                    "found": entry.sequence_number
                })
        
        return {
            "valid": len(errors) == 0,
            "total_entries": len(self.entries),
            "errors": errors
        }
    
    def get_entries(
        self,
        thread_id: Optional[str] = None,
        event_type: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[LogEntry]:
        """
        Query log entries with filters.
        
        Args:
            thread_id: Filter by thread
            event_type: Filter by event type
            level: Filter by level
            start_time: ISO timestamp
            end_time: ISO timestamp
            tags: Filter by tags
            
        Returns:
            Filtered log entries
        """
        filtered = self.entries
        
        if thread_id:
            filtered = [e for e in filtered if e.thread_id == thread_id]
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        if level:
            filtered = [e for e in filtered if e.level == level]
        
        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]
        
        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]
        
        if tags:
            filtered = [
                e for e in filtered 
                if any(tag in e.tags for tag in tags)
            ]
        
        return filtered
    
    def replay_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Replay all transitions for a thread.
        
        Returns:
            Chronological list of transitions
        """
        entries = self.get_entries(thread_id=thread_id, event_type="transition")
        
        return [
            {
                "sequence": e.sequence_number,
                "timestamp": e.timestamp,
                "transition": f"{e.node_from} → {e.node_to}",
                "input": e.input_data,
                "output": e.output_data,
                "reasoning": e.reasoning,
                "log_id": e.log_id
            }
            for e in entries
        ]
    
    def export_to_file(
        self,
        output_path: Path,
        format: str = "json",
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export log to a file.
        
        Args:
            output_path: Output file path
            format: json or csv
            filters: Optional filters to apply
            
        Returns:
            Path to exported file
        """
        # Apply filters
        entries = self.entries
        if filters:
            entries = self.get_entries(**filters)
        
        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json_data = {
                    "metadata": {
                        "total_entries": len(entries),
                        "exported_at": datetime.now(timezone.utc).isoformat(),
                        "filters": filters or {}
                    },
                    "entries": [e.to_dict() for e in entries]
                }
                json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            import csv
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                if not entries:
                    return str(output_path)
                
                fieldnames = [
                    "sequence_number", "timestamp", "event_type", "level",
                    "thread_id", "node_from", "node_to", "reasoning",
                    "log_id", "entry_hash"
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in entries:
                    writer.writerow({
                        "sequence_number": entry.sequence_number,
                        "timestamp": entry.timestamp,
                        "event_type": entry.event_type,
                        "level": entry.level,
                        "thread_id": entry.thread_id,
                        "node_from": entry.node_from,
                        "node_to": entry.node_to,
                        "reasoning": entry.reasoning,
                        "log_id": entry.log_id,
                        "entry_hash": entry.entry_hash
                    })
        
        return str(output_path)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the log"""
        if not self.entries:
            return {"message": "No entries logged yet"}
        
        # Group by event type
        by_event_type: Dict[str, int] = {}
        by_level: Dict[str, int] = {}
        by_thread: Dict[str, int] = {}
        
        for entry in self.entries:
            by_event_type[entry.event_type] = by_event_type.get(entry.event_type, 0) + 1
            by_level[entry.level] = by_level.get(entry.level, 0) + 1
            by_thread[entry.thread_id] = by_thread.get(entry.thread_id, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "first_entry": self.entries[0].timestamp,
            "latest_entry": self.entries[-1].timestamp,
            "by_event_type": by_event_type,
            "by_level": by_level,
            "unique_threads": len(by_thread),
            "integrity_verified": self.verify_integrity()["valid"]
        }
    
    def search(self, query: str) -> List[LogEntry]:
        """
        Full-text search across all log entries.
        
        Args:
            query: Search query
            
        Returns:
            Matching entries
        """
        query_lower = query.lower()
        matches = []
        
        for entry in self.entries:
            # Search in reasoning
            if query_lower in entry.reasoning.lower():
                matches.append(entry)
                continue
            
            # Search in input/output data
            if query_lower in json.dumps(entry.input_data).lower():
                matches.append(entry)
                continue
            
            if query_lower in json.dumps(entry.output_data).lower():
                matches.append(entry)
                continue
            
            # Search in metadata
            if query_lower in json.dumps(entry.metadata).lower():
                matches.append(entry)
                continue
        
        return matches
