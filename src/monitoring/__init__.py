"""
Monitoring and Observability Package

Provides comprehensive agent monitoring:
- State snapshots
- Decision replay
- Immutable audit logs
- Unified orchestrator

Usage:
    from src.monitoring import get_monitor
    
    monitor = get_monitor()
    
    # Start monitoring a node
    decision_id = monitor.start_node_execution("chat", thread_id, state)
    
    # Record prompt
    monitor.record_prompt(decision_id, template, vars, final_prompt)
    
    # Record output
    monitor.record_output(decision_id, output)
    
    # End monitoring
    monitor.end_node_execution(decision_id, thread_id, state, "chat")
    
    # Get complete report
    report = monitor.get_complete_report(thread_id)
"""

from .state_snapshot import StateSnapshotManager, StateSnapshot
from .decision_replay import DecisionReplayManager, DecisionRecord
from .audit_log import ImmutableAuditLog, LogEntry
from .orchestrator import AgentMonitor, get_monitor

__all__ = [
    "StateSnapshotManager",
    "StateSnapshot",
    "DecisionReplayManager",
    "DecisionRecord",
    "ImmutableAuditLog",
    "LogEntry",
    "AgentMonitor",
    "get_monitor"
]
