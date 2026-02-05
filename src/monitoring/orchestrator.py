"""
Agent Observability Orchestrator

Integrates all monitoring components:
- State snapshots
- Decision replay
- Immutable audit logs

Provides unified interface for comprehensive agent monitoring.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .state_snapshot import StateSnapshotManager, StateSnapshot
from .decision_replay import DecisionReplayManager, DecisionRecord
from .audit_log import ImmutableAuditLog, LogEntry


class AgentMonitor:
    """
    Comprehensive agent monitoring orchestrator.
    
    Automatically captures:
    - State snapshots at decision points
    - Decision replay records
    - Immutable audit trail
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the monitor.
        
        Args:
            base_path: Base path for all monitoring data
        """
        base_path = base_path or Path("data/monitoring")
        
        self.snapshot_manager = StateSnapshotManager(base_path / "snapshots")
        self.decision_manager = DecisionReplayManager(base_path / "decisions")
        self.audit_log = ImmutableAuditLog(base_path / "audit_logs")
        
        self.active_decisions: Dict[str, str] = {}  # node_id -> decision_id
    
    def start_node_execution(
        self,
        node_name: str,
        thread_id: str,
        state: Dict[str, Any],
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Start monitoring a node execution.
        
        Returns:
            decision_id for tracking
        """
        # Capture state snapshot
        snapshot = self.snapshot_manager.capture_snapshot(
            state=state,
            active_node=node_name,
            tags=tags
        )
        
        # Start decision recording
        decision_id = self.decision_manager.start_decision(
            node_name=node_name,
            thread_id=thread_id,
            state=state,
            tags=tags
        )
        
        # Log to audit trail
        self.audit_log.log_transition(
            thread_id=thread_id,
            node_from=state.get("previous_node", "START"),
            node_to=node_name,
            input_data={"state_keys": list(state.keys())},
            output_data={},
            reasoning=f"Starting execution of node: {node_name}",
            metadata={"snapshot_id": snapshot.snapshot_id}
        )
        
        self.active_decisions[node_name] = decision_id
        
        return decision_id
    
    def record_prompt(
        self,
        decision_id: str,
        prompt_template: str,
        variables: Dict[str, Any],
        final_prompt: str,
        model: str = "unknown",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """Record the prompt used in a decision"""
        self.decision_manager.record_prompt(
            decision_id=decision_id,
            prompt_template=prompt_template,
            variables=variables,
            final_prompt=final_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def record_output(
        self,
        decision_id: str,
        raw_output: str,
        parsed_output: Optional[Dict[str, Any]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        resources_found: Optional[List[str]] = None,
        confidence: str = "unknown",
        token_count: int = 0
    ):
        """Record the output of a decision"""
        self.decision_manager.record_output(
            decision_id=decision_id,
            raw_output=raw_output,
            parsed_output=parsed_output,
            tool_calls=tool_calls,
            resources_found=resources_found,
            confidence=confidence,
            token_count=token_count
        )
    
    def record_reasoning(
        self,
        decision_id: str,
        decision_type: str,
        rationale: str,
        selected_action: str,
        alternatives: Optional[List[str]] = None,
        confidence: float = 0.0
    ):
        """Record reasoning for a decision"""
        self.decision_manager.record_reasoning(
            decision_id=decision_id,
            decision_type=decision_type,
            rationale=rationale,
            selected_action=selected_action,
            alternatives=alternatives,
            confidence=confidence
        )
    
    def end_node_execution(
        self,
        decision_id: str,
        thread_id: str,
        state: Dict[str, Any],
        node_name: str,
        status: str = "success",
        error: Optional[str] = None
    ):
        """
        Complete monitoring of a node execution.
        
        Args:
            decision_id: Decision ID from start_node_execution
            thread_id: Thread ID
            state: Final state
            node_name: Node that was executed
            status: success or error
            error: Error message if any
        """
        # Capture final snapshot
        snapshot = self.snapshot_manager.capture_snapshot(
            state=state,
            active_node=node_name,
            tags=["completed", status]
        )
        
        # End decision recording
        self.decision_manager.end_decision(
            decision_id=decision_id,
            state=state,
            status=status,
            error=error
        )
        
        # Log completion to audit
        if error:
            self.audit_log.log_error(
                thread_id=thread_id,
                error_message=error,
                error_type="node_execution_error",
                context={"node": node_name, "snapshot_id": snapshot.snapshot_id}
            )
        else:
            self.audit_log.log_transition(
                thread_id=thread_id,
                node_from=node_name,
                node_to=state.get("next_node", "END"),
                input_data={},
                output_data={"state_keys": list(state.keys())},
                reasoning=f"Completed execution of node: {node_name}",
                metadata={"snapshot_id": snapshot.snapshot_id}
            )
        
        # Remove from active
        if node_name in self.active_decisions:
            del self.active_decisions[node_name]
    
    def log_metric(
        self,
        thread_id: str,
        metric_name: str,
        metric_value: Any,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log a metric"""
        self.audit_log.log_metric(
            thread_id=thread_id,
            metric_name=metric_name,
            metric_value=metric_value,
            context=context
        )
    
    def get_complete_report(self, thread_id: str) -> Dict[str, Any]:
        """
        Generate a complete monitoring report for a thread.
        
        Returns:
            Comprehensive report with all monitoring data
        """
        # Get snapshots
        snapshots = [
            s for s in self.snapshot_manager.snapshots 
            if s.context.thread_id == thread_id
        ]
        
        # Get decision chain
        decision_chain = self.decision_manager.get_decision_chain(thread_id)
        
        # Get audit trail
        audit_trail = self.audit_log.replay_thread(thread_id)
        
        # Performance analysis
        performance = self.decision_manager.analyze_performance(thread_id)
        
        # Anomaly detection
        anomalies = []
        for snapshot in snapshots:
            detected = self.snapshot_manager.detect_anomalies(snapshot)
            if detected:
                anomalies.extend(detected)
        
        # Integrity check
        integrity = self.audit_log.verify_integrity()
        
        return {
            "thread_id": thread_id,
            "generated_at": datetime.now().isoformat(),
            
            "summary": {
                "total_snapshots": len(snapshots),
                "total_decisions": len(decision_chain),
                "total_transitions": len(audit_trail),
                "anomalies_detected": len(anomalies),
                "integrity_valid": integrity["valid"]
            },
            
            "snapshots": [
                {
                    "id": s.snapshot_id,
                    "timestamp": s.timestamp,
                    "node": s.symptoms.active_node,
                    "confidence": s.scores.confidence,
                    "latency_ms": s.scores.latency_ms
                }
                for s in snapshots
            ],
            
            "decision_chain": decision_chain,
            
            "audit_trail": audit_trail,
            
            "performance": performance,
            
            "anomalies": anomalies,
            
            "integrity": integrity
        }
    
    def export_report(
        self,
        thread_id: str,
        output_path: Optional[Path] = None,
        format: str = "json"
    ) -> str:
        """
        Export complete report to file.
        
        Returns:
            Path to exported file
        """
        import json
        
        report = self.get_complete_report(thread_id)
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"data/monitoring/reports/report_{thread_id}_{timestamp}.json")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def visualize_execution(self, thread_id: str) -> str:
        """
        Create a text visualization of the complete execution.
        
        Returns:
            Formatted text visualization
        """
        report = self.get_complete_report(thread_id)
        
        lines = [
            "=" * 100,
            f"AGENT EXECUTION REPORT - Thread: {thread_id}",
            "=" * 100,
            "",
            "📊 SUMMARY",
            "-" * 100,
            f"  Total Snapshots:    {report['summary']['total_snapshots']}",
            f"  Total Decisions:    {report['summary']['total_decisions']}",
            f"  Total Transitions:  {report['summary']['total_transitions']}",
            f"  Anomalies Detected: {report['summary']['anomalies_detected']}",
            f"  Integrity Valid:    {'✅ Yes' if report['summary']['integrity_valid'] else '❌ No'}",
            "",
            "🔄 DECISION CHAIN",
            "-" * 100
        ]
        
        for i, decision in enumerate(report['decision_chain'], 1):
            status = "✅" if decision['status'] == "success" else "❌"
            lines.append(f"\n  {i}. {status} {decision['node']} ({decision['duration_ms']:.0f}ms)")
            lines.append(f"     Type: {decision['decision_type']}")
            lines.append(f"     Action: {decision['action']}")
        
        if report['anomalies']:
            lines.append("\n")
            lines.append("⚠️  ANOMALIES DETECTED")
            lines.append("-" * 100)
            for anomaly in report['anomalies']:
                lines.append(f"  • {anomaly}")
        
        lines.append("\n")
        lines.append("📈 PERFORMANCE")
        lines.append("-" * 100)
        perf = report['performance']
        lines.append(f"  Success Rate:     {perf.get('success_rate', 0):.1%}")
        lines.append(f"  Avg Duration:     {perf.get('avg_duration_ms', 0):.0f}ms")
        lines.append(f"  Total Duration:   {perf.get('total_duration_ms', 0):.0f}ms")
        
        lines.append("\n" + "=" * 100)
        
        return "\n".join(lines)
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status of the monitoring system.
        
        Returns:
            Health status information
        """
        snapshot_summary = self.snapshot_manager.get_summary()
        audit_stats = self.audit_log.get_statistics()
        
        return {
            "status": "healthy",
            "snapshots": snapshot_summary,
            "audit_log": audit_stats,
            "active_decisions": len(self.active_decisions)
        }


# Global monitor instance
_global_monitor: Optional[AgentMonitor] = None


def get_monitor() -> AgentMonitor:
    """Get or create the global monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = AgentMonitor()
    return _global_monitor
