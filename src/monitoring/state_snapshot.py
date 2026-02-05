"""
State Snapshot Manager

Captures complete snapshots of agent state including:
- Symptoms (current conditions)
- Scores (performance metrics)
- Context (conversation history, active nodes, metadata)
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class PerformanceScores:
    """Performance metrics at snapshot time"""
    confidence: float = 0.0
    relevance: float = 0.0
    completeness: float = 0.0
    latency_ms: float = 0.0
    token_count: int = 0
    cost_usd: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Symptoms:
    """Current state symptoms/indicators"""
    active_node: str = "unknown"
    is_searching: bool = False
    has_resources: bool = False
    message_count: int = 0
    error_count: int = 0
    retry_count: int = 0
    stuck_cycles: int = 0
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StateContext:
    """Contextual information about the agent state"""
    thread_id: str
    session_id: str
    query: str = ""
    model: str = "unknown"
    temperature: float = 0.7
    max_tokens: int = 4096
    search_domains: List[str] = field(default_factory=list)
    resources_count: int = 0
    messages: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StateSnapshot:
    """Complete snapshot of agent state"""
    snapshot_id: str
    timestamp: str
    symptoms: Symptoms
    scores: PerformanceScores
    context: StateContext
    raw_state: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "symptoms": self.symptoms.to_dict(),
            "scores": self.scores.to_dict(),
            "context": self.context.to_dict(),
            "raw_state": self.raw_state,
            "tags": self.tags
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class StateSnapshotManager:
    """
    Manages complete state snapshots of the agent.
    
    Provides:
    - Automatic snapshot capture at key decision points
    - Snapshot storage and retrieval
    - State comparison and diff
    - Anomaly detection
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("data/monitoring/snapshots")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.snapshots: List[StateSnapshot] = []
        
    def capture_snapshot(
        self,
        state: Dict[str, Any],
        active_node: str = "unknown",
        tags: Optional[List[str]] = None
    ) -> StateSnapshot:
        """
        Capture a complete state snapshot.
        
        Args:
            state: Current agent state
            active_node: Currently executing node
            tags: Optional tags for categorization
            
        Returns:
            StateSnapshot object
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Generate unique snapshot ID
        snapshot_data = f"{timestamp}_{active_node}_{state.get('thread_id', '')}"
        snapshot_id = hashlib.sha256(snapshot_data.encode()).hexdigest()[:16]
        
        # Extract symptoms from state
        symptoms = self._extract_symptoms(state, active_node)
        
        # Calculate performance scores
        scores = self._calculate_scores(state)
        
        # Build context
        context = self._build_context(state)
        
        # Create snapshot
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            symptoms=symptoms,
            scores=scores,
            context=context,
            raw_state=self._sanitize_state(state),
            tags=tags or []
        )
        
        # Store snapshot
        self.snapshots.append(snapshot)
        self._persist_snapshot(snapshot)
        
        return snapshot
    
    def _extract_symptoms(self, state: Dict[str, Any], active_node: str) -> Symptoms:
        """Extract current symptoms from state"""
        messages = state.get("messages", [])
        resources = state.get("resources", [])
        logs = state.get("logs", [])
        
        # Count errors in logs
        error_count = sum(1 for log in logs if log.get("level") == "error")
        last_error = next(
            (log.get("message") for log in reversed(logs) if log.get("level") == "error"),
            None
        )
        
        return Symptoms(
            active_node=active_node,
            is_searching=active_node in ["search", "download"],
            has_resources=len(resources) > 0,
            message_count=len(messages),
            error_count=error_count,
            retry_count=state.get("retry_count", 0),
            stuck_cycles=state.get("stuck_cycles", 0),
            last_error=last_error
        )
    
    def _calculate_scores(self, state: Dict[str, Any]) -> PerformanceScores:
        """Calculate performance scores from state"""
        resources = state.get("resources", [])
        metrics = state.get("metrics", {})
        
        # Extract metrics
        confidence = state.get("confidence_score", 0.0)
        if isinstance(confidence, str):
            confidence_map = {"high": 0.9, "medium": 0.6, "low": 0.3}
            confidence = confidence_map.get(confidence.lower(), 0.0)
        
        return PerformanceScores(
            confidence=confidence,
            relevance=metrics.get("relevance", 0.0),
            completeness=min(len(resources) / 5.0, 1.0) if resources else 0.0,
            latency_ms=metrics.get("latency_ms", 0.0),
            token_count=metrics.get("token_count", 0),
            cost_usd=metrics.get("cost_usd", 0.0)
        )
    
    def _build_context(self, state: Dict[str, Any]) -> StateContext:
        """Build contextual information"""
        messages = state.get("messages", [])
        
        # Convert messages to dicts
        message_dicts = []
        for msg in messages:
            if hasattr(msg, "content"):
                message_dicts.append({
                    "role": getattr(msg, "type", "unknown"),
                    "content": msg.content[:200],  # Truncate for storage
                    "timestamp": getattr(msg, "timestamp", None)
                })
            elif isinstance(msg, dict):
                message_dicts.append({
                    "role": msg.get("role", "unknown"),
                    "content": str(msg.get("content", ""))[:200],
                    "timestamp": msg.get("timestamp")
                })
        
        return StateContext(
            thread_id=state.get("thread_id", "unknown"),
            session_id=state.get("session_id", "unknown"),
            query=state.get("query", ""),
            model=state.get("model", "unknown"),
            temperature=state.get("temperature", 0.7),
            max_tokens=state.get("max_tokens", 4096),
            search_domains=state.get("search_domains", []),
            resources_count=len(state.get("resources", [])),
            messages=message_dicts,
            metadata=state.get("metadata", {})
        )
    
    def _sanitize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize state for storage (remove large objects)"""
        sanitized = {}
        
        for key, value in state.items():
            # Skip very large values
            if isinstance(value, (str, bytes)) and len(value) > 10000:
                sanitized[key] = f"<truncated: {len(value)} chars>"
            elif isinstance(value, list) and len(value) > 50:
                sanitized[key] = f"<truncated: {len(value)} items>"
            else:
                try:
                    # Try to serialize
                    json.dumps(value)
                    sanitized[key] = value
                except (TypeError, ValueError):
                    sanitized[key] = str(value)
        
        return sanitized
    
    def _persist_snapshot(self, snapshot: StateSnapshot):
        """Persist snapshot to disk"""
        timestamp_str = snapshot.timestamp.replace(":", "-").split(".")[0]
        filename = f"snapshot_{snapshot.snapshot_id}_{timestamp_str}.json"
        filepath = self.storage_path / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(snapshot.to_json())
    
    def get_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """Retrieve a snapshot by ID"""
        for snapshot in self.snapshots:
            if snapshot.snapshot_id == snapshot_id:
                return snapshot
        return None
    
    def get_latest_snapshot(self) -> Optional[StateSnapshot]:
        """Get the most recent snapshot"""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_snapshots_by_tag(self, tag: str) -> List[StateSnapshot]:
        """Get all snapshots with a specific tag"""
        return [s for s in self.snapshots if tag in s.tags]
    
    def compare_snapshots(
        self,
        snapshot1_id: str,
        snapshot2_id: str
    ) -> Dict[str, Any]:
        """
        Compare two snapshots and return differences.
        
        Returns:
            Dict with comparison results
        """
        s1 = self.get_snapshot(snapshot1_id)
        s2 = self.get_snapshot(snapshot2_id)
        
        if not s1 or not s2:
            return {"error": "One or both snapshots not found"}
        
        return {
            "snapshot1": snapshot1_id,
            "snapshot2": snapshot2_id,
            "time_delta": (
                datetime.fromisoformat(s2.timestamp) - 
                datetime.fromisoformat(s1.timestamp)
            ).total_seconds(),
            "symptoms_changed": s1.symptoms.to_dict() != s2.symptoms.to_dict(),
            "score_delta": {
                "confidence": s2.scores.confidence - s1.scores.confidence,
                "relevance": s2.scores.relevance - s1.scores.relevance,
                "completeness": s2.scores.completeness - s1.scores.completeness,
            },
            "message_count_delta": s2.context.message_count - s1.context.message_count,
            "resources_count_delta": s2.context.resources_count - s1.context.resources_count,
        }
    
    def detect_anomalies(self, snapshot: StateSnapshot) -> List[str]:
        """
        Detect anomalies in a snapshot.
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for stuck cycles
        if snapshot.symptoms.stuck_cycles > 3:
            anomalies.append(f"Agent stuck in loop: {snapshot.symptoms.stuck_cycles} cycles")
        
        # Check for excessive retries
        if snapshot.symptoms.retry_count > 5:
            anomalies.append(f"High retry count: {snapshot.symptoms.retry_count}")
        
        # Check for low confidence
        if snapshot.scores.confidence < 0.3:
            anomalies.append(f"Low confidence score: {snapshot.scores.confidence:.2f}")
        
        # Check for high latency
        if snapshot.scores.latency_ms > 10000:
            anomalies.append(f"High latency: {snapshot.scores.latency_ms:.0f}ms")
        
        # Check for errors
        if snapshot.symptoms.error_count > 0:
            anomalies.append(f"Errors detected: {snapshot.symptoms.error_count}")
        
        # Check for no resources after search
        if snapshot.symptoms.active_node == "download" and not snapshot.symptoms.has_resources:
            anomalies.append("No resources found after search")
        
        return anomalies
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all snapshots"""
        if not self.snapshots:
            return {"message": "No snapshots captured yet"}
        
        return {
            "total_snapshots": len(self.snapshots),
            "first_snapshot": self.snapshots[0].timestamp,
            "latest_snapshot": self.snapshots[-1].timestamp,
            "avg_confidence": sum(s.scores.confidence for s in self.snapshots) / len(self.snapshots),
            "total_errors": sum(s.symptoms.error_count for s in self.snapshots),
            "nodes_visited": list(set(s.symptoms.active_node for s in self.snapshots)),
            "tags_used": list(set(tag for s in self.snapshots for tag in s.tags))
        }
