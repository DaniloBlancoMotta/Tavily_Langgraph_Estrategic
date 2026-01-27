"""
Script to index strategic consulting knowledge into RAG.
Run this once to populate the vector store with demo documents.
"""
from langchain_core.documents import Document
from rag_store import get_rag


# Sample strategic consulting documents for demo
DEMO_DOCUMENTS = [
    Document(
        page_content="""
        Digital Transformation Strategy Framework
        
        A comprehensive digital transformation requires alignment across four key dimensions:
        1. Technology Infrastructure: Cloud migration, API architecture, data platforms
        2. Operating Model: Agile teams, DevOps practices, product-centric organization
        3. Customer Experience: Omnichannel engagement, personalization, self-service
        4. Data & Analytics: Real-time insights, predictive models, decision automation
        
        Success factors include executive sponsorship, change management, and iterative delivery.
        McKinsey research shows 70% of transformations fail due to organizational resistance.
        """,
        metadata={"title": "Digital Transformation Framework", "source": "internal_kb", "type": "framework"}
    ),
    
    Document(
        page_content="""
        ESG Governance Best Practices
        
        Environmental, Social, and Governance (ESG) integration requires:
        - Board-level oversight with dedicated ESG committee
        - Material ESG metrics tied to executive compensation
        - Stakeholder engagement and transparent reporting (GRI, SASB standards)
        - Climate risk assessment and scenario planning
        - Supply chain due diligence and human rights policies
        
        Leading companies embed ESG into strategy, not just compliance.
        """,
        metadata={"title": "ESG Governance Framework", "source": "internal_kb", "type": "governance"}
    ),
    
    Document(
        page_content="""
        Change Management Methodology
        
        Effective organizational change follows the ADKAR model:
        - Awareness: Communicate the need for change
        - Desire: Build motivation and engagement
        - Knowledge: Provide training and resources
        - Ability: Enable new behaviors and processes
        - Reinforcement: Sustain change through incentives
        
        Critical success factors: leadership alignment, two-way communication, 
        quick wins, and addressing resistance proactively.
        """,
        metadata={"title": "Change Management Best Practices", "source": "internal_kb", "type": "methodology"}
    ),
    
    Document(
        page_content="""
        Financial Services Digital Strategy
        
        Banks and insurers must prioritize:
        1. Core Banking Modernization: Replace legacy systems with cloud-native platforms
        2. Open Banking APIs: Enable third-party integrations and ecosystems
        3. AI-Powered Services: Chatbots, fraud detection, personalized advice
        4. Regulatory Compliance: GDPR, PSD2, Basel III automation
        5. Cybersecurity: Zero-trust architecture, threat intelligence
        
        Digital leaders achieve 20-30% cost reduction and 2x revenue growth.
        """,
        metadata={"title": "Financial Services Digital Roadmap", "source": "internal_kb", "type": "industry"}
    ),
    
    Document(
        page_content="""
        Strategic Planning Process
        
        Annual strategic planning cycle:
        Q1: Environmental scan (PESTEL, Porter's Five Forces)
        Q2: Strategic options development (scenarios, war gaming)
        Q3: Portfolio prioritization (growth-share matrix, resource allocation)
        Q4: Execution planning (OKRs, KPIs, governance)
        
        Best practice: Quarterly strategy reviews with dynamic resource reallocation.
        Avoid "set and forget" - strategy must be adaptive.
        """,
        metadata={"title": "Strategic Planning Framework", "source": "internal_kb", "type": "process"}
    ),
    
    Document(
        page_content="""
        M&A Integration Playbook
        
        Post-merger integration critical path:
        Day 1: Legal close, communications, IT access
        Day 30: Quick wins, cultural assessment, talent retention
        Day 100: Operating model design, synergy capture, brand strategy
        Day 365: Full integration, performance tracking, lessons learned
        
        Key risks: culture clash, talent attrition, customer churn.
        PMO governance essential for tracking 200+ integration tasks.
        """,
        metadata={"title": "M&A Integration Best Practices", "source": "internal_kb", "type": "playbook"}
    ),
    
    Document(
        page_content="""
        Agile at Scale Framework
        
        Scaling agile beyond single teams requires:
        - SAFe, LeSS, or Spotify model selection based on context
        - Product management layer (roadmaps, backlogs, prioritization)
        - Architecture runway for technical enablers
        - Communities of practice for knowledge sharing
        - Metrics: velocity, cycle time, customer satisfaction
        
        Anti-patterns: agile theater, lack of empowerment, waterfall disguised as agile.
        """,
        metadata={"title": "Agile Transformation Guide", "source": "internal_kb", "type": "methodology"}
    ),
    
    Document(
        page_content="""
        Customer Experience Excellence
        
        CX transformation pillars:
        1. Journey Mapping: Identify pain points and moments of truth
        2. Voice of Customer: NPS, CSAT, sentiment analysis
        3. Personalization: Segment-of-one marketing and service
        4. Omnichannel: Seamless experience across touchpoints
        5. Employee Experience: Engaged employees create great CX
        
        ROI: 1-point NPS improvement = 3-7% revenue growth.
        """,
        metadata={"title": "Customer Experience Strategy", "source": "internal_kb", "type": "framework"}
    ),
    
    Document(
        page_content="""
        Data Strategy and Governance
        
        Enterprise data strategy components:
        - Data Architecture: Lakes, warehouses, mesh, fabric
        - Data Quality: Profiling, cleansing, master data management
        - Data Governance: Policies, stewardship, lineage, catalog
        - Data Monetization: Products, insights-as-a-service
        - Data Ethics: Privacy, bias mitigation, responsible AI
        
        Gartner: By 2025, 80% of organizations will have a Chief Data Officer.
        """,
        metadata={"title": "Enterprise Data Strategy", "source": "internal_kb", "type": "framework"}
    ),
    
    Document(
        page_content="""
        Innovation Portfolio Management
        
        Balanced innovation portfolio (McKinsey Three Horizons):
        - Horizon 1 (70%): Core business optimization
        - Horizon 2 (20%): Adjacent growth opportunities
        - Horizon 3 (10%): Transformational bets
        
        Governance: Stage-gate process, venture board, innovation metrics.
        Avoid: Innovation theater, lack of funding, risk aversion.
        """,
        metadata={"title": "Innovation Strategy Framework", "source": "internal_kb", "type": "framework"}
    ),
]


def index_demo_documents():
    """Index demo documents into RAG store."""
    print("🚀 Indexing strategic consulting knowledge...")
    print(f"📄 Documents to index: {len(DEMO_DOCUMENTS)}")
    
    rag = get_rag()
    rag.index_documents(DEMO_DOCUMENTS)
    
    print("✅ Indexing complete!")
    print(f"📊 Vector store location: {rag.persist_directory}")
    
    # Test search
    print("\n🔍 Testing semantic search...")
    test_query = "How to manage organizational change?"
    results = rag.search(test_query, k=3)
    
    print(f"\nQuery: '{test_query}'")
    print(f"Results found: {len(results)}\n")
    
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc.metadata['title']}")
        print(f"   {doc.page_content[:100]}...\n")


if __name__ == "__main__":
    index_demo_documents()
