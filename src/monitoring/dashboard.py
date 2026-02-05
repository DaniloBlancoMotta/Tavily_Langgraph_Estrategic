"""
Monitoring Dashboard - Streamlit App

Real-time visualization of agent monitoring metrics:
- State snapshots
- Decision replay
- Audit logs
- Performance metrics
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import json
from datetime import datetime
from src.monitoring.orchestrator import AgentMonitor

# Page config
st.set_page_config(
    page_title="Agent Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize monitor
@st.cache_resource
def get_monitor():
    return AgentMonitor()

monitor = get_monitor()

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">📊 Agent Monitoring Dashboard</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Real-time observability of AI Agent execution</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Controls")
    
    # Health status
    st.markdown("#### System Health")
    health = monitor.get_health_status()
    
    if health["status"] == "healthy":
        st.success("✅ System Healthy")
    else:
        st.error("❌ System Unhealthy")
    
    st.metric("Active Decisions", health["active_decisions"])
    
    st.markdown("---")
    
    # Thread selection
    st.markdown("#### Thread Selection")
    
    # Get available threads from snapshots
    all_threads = list(set(
        s.context.thread_id 
        for s in monitor.snapshot_manager.snapshots
    ))
    
    if all_threads:
        selected_thread = st.selectbox(
            "Select Thread",
            options=all_threads,
            index=0
        )
    else:
        selected_thread = None
        st.info("No threads available yet. Execute the agent to see monitoring data.")
    
    st.markdown("---")
    
    # Export options
    st.markdown("#### Export")
    
    if selected_thread:
        if st.button("📥 Export Report", use_container_width=True):
            try:
                path = monitor.export_report(selected_thread)
                st.success(f"Report exported to:\n`{path}`")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")

# Main content
if selected_thread:
    # Get complete report
    report = monitor.get_complete_report(selected_thread)
    
    # Summary metrics
    st.markdown("### 📈 Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Snapshots",
            report["summary"]["total_snapshots"],
            help="Total state snapshots captured"
        )
    
    with col2:
        st.metric(
            "Decisions",
            report["summary"]["total_decisions"],
            help="Total decisions made"
        )
    
    with col3:
        st.metric(
            "Transitions",
            report["summary"]["total_transitions"],
            help="Total state transitions"
        )
    
    with col4:
        anomaly_count = report["summary"]["anomalies_detected"]
        st.metric(
            "Anomalies",
            anomaly_count,
            delta=None if anomaly_count == 0 else "⚠️",
            help="Detected anomalies"
        )
    
    with col5:
        integrity = report["summary"]["integrity_valid"]
        st.metric(
            "Integrity",
            "✅" if integrity else "❌",
            help="Audit log integrity status"
        )
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔄 Execution Flow",
        "📸 State Snapshots",
        "🎯 Decision Replay",
        "📝 Audit Trail",
        "📊 Performance"
    ])
    
    with tab1:
        st.markdown("### Execution Flow Visualization")
        
        # Show decision tree
        tree = monitor.decision_manager.visualize_decision_tree(selected_thread)
        st.code(tree, language="text")
        
        # Anomalies
        if report["anomalies"]:
            st.markdown("### ⚠️ Anomalies Detected")
            for anomaly in report["anomalies"]:
                st.markdown(f"""
                <div class="warning-box">
                    ⚠️ {anomaly}
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### State Snapshots")
        
        for snapshot_data in report["snapshots"]:
            with st.expander(
                f"📸 {snapshot_data['node']} - {snapshot_data['timestamp'][:19]}",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Metrics**")
                    st.metric("Confidence", f"{snapshot_data['confidence']:.2f}")
                    st.metric("Latency", f"{snapshot_data['latency_ms']:.0f}ms")
                
                with col2:
                    st.markdown("**Details**")
                    st.json({
                        "snapshot_id": snapshot_data["id"],
                        "node": snapshot_data["node"],
                        "timestamp": snapshot_data["timestamp"]
                    })
    
    with tab3:
        st.markdown("### Decision Replay")
        
        for i, decision in enumerate(report["decision_chain"], 1):
            status_icon = "✅" if decision["status"] == "success" else "❌"
            
            with st.expander(
                f"{i}. {status_icon} {decision['node']} ({decision['duration_ms']:.0f}ms)",
                expanded=False
            ):
                # Get full replay
                replay = monitor.decision_manager.replay_decision(decision["decision_id"])
                
                if replay:
                    st.markdown("**Execution**")
                    st.json({
                        "node": replay["execution"]["node"],
                        "duration_ms": replay["execution"]["duration_ms"],
                        "status": replay["execution"]["status"]
                    })
                    
                    st.markdown("**Prompt Used**")
                    st.code(replay["prompt"]["final_prompt"][:500] + "...", language="text")
                    
                    st.markdown("**Output Generated**")
                    st.text_area(
                        "Output",
                        value=replay["output"]["text"][:500] + "...",
                        height=150,
                        key=f"output_{decision['decision_id']}"
                    )
                    
                    st.markdown("**Reasoning**")
                    st.info(f"""
                    **Type:** {replay["reasoning"]["type"]}
                    
                    **Rationale:** {replay["reasoning"]["rationale"]}
                    
                    **Selected Action:** {replay["reasoning"]["selected"]}
                    """)
    
    with tab4:
        st.markdown("### Audit Trail")
        
        for i, entry in enumerate(report["audit_trail"], 1):
            transition = entry["transition"]
            timestamp = entry["timestamp"][:19]
            
            with st.expander(
                f"{i}. {transition} - {timestamp}",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Input**")
                    st.json(entry["input"])
                
                with col2:
                    st.markdown("**Output**")
                    st.json(entry["output"])
                
                if entry["reasoning"]:
                    st.markdown("**Reasoning**")
                    st.info(entry["reasoning"])
    
    with tab5:
        st.markdown("### Performance Analysis")
        
        perf = report["performance"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Overall Metrics")
            st.metric("Total Decisions", perf["total_decisions"])
            st.metric("Success Rate", f"{perf.get('success_rate', 0):.1%}")
            st.metric("Average Duration", f"{perf.get('avg_duration_ms', 0):.0f}ms")
            st.metric("Total Duration", f"{perf.get('total_duration_ms', 0):.0f}ms")
        
        with col2:
            st.markdown("#### Node Statistics")
            
            if "node_stats" in perf:
                for node, stats in perf["node_stats"].items():
                    with st.expander(f"**{node}**", expanded=True):
                        st.metric("Count", stats["count"])
                        st.metric("Avg Duration", f"{stats['avg_duration_ms']:.0f}ms")
                        st.metric("Min Duration", f"{stats['min_duration_ms']:.0f}ms")
                        st.metric("Max Duration", f"{stats['max_duration_ms']:.0f}ms")
    
    # Visualization
    st.markdown("---")
    st.markdown("### 📋 Complete Report (Raw)")
    
    with st.expander("View Raw JSON", expanded=False):
        st.json(report)

else:
    # No thread selected
    st.info("""
    ### 👋 Welcome to the Agent Monitoring Dashboard
    
    This dashboard provides comprehensive observability for your AI agent executions.
    
    **Features:**
    - 📸 **State Snapshots**: Complete state capture at every decision point
    - 🎯 **Decision Replay**: Full replay of decisions with prompts and outputs
    - 📝 **Audit Trail**: Immutable, cryptographically-secured logs
    - 📊 **Performance Metrics**: Real-time performance analysis
    
    **To get started:**
    1. Run your agent with monitoring enabled
    2. Select a thread from the sidebar
    3. Explore the metrics and visualizations
    
    The monitoring system automatically captures all agent activity with zero configuration required.
    """)
    
    # Show system stats
    st.markdown("### 📊 System Statistics")
    
    snapshot_summary = monitor.snapshot_manager.get_summary()
    audit_stats = monitor.audit_log.get_statistics()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Snapshot Manager")
        st.json(snapshot_summary)
    
    with col2:
        st.markdown("#### Audit Log")
        st.json(audit_stats)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>Agent Monitoring Dashboard v1.0.0 | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
