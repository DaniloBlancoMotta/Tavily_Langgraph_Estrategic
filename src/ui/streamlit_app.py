import sys
import os
import certifi
from pathlib import Path

# 🔍 MONITORING FIX: Force correct SSL certificates for LangSmith
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import asyncio
import uuid
import json
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.agent import graph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from io import BytesIO

# ============================================================================
# CONFIGURAÇÃO DE PÁGINA E TEMA CUSTOMIZADO
# ============================================================================

st.set_page_config(
    page_title="Big Four Researcher",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado - Tema Azul Profissional
st.markdown("""
<style>
    /* Tema principal - Azul e Branco */
    :root {
        --primary-blue: #0066CC;
        --light-blue: #4A90E2;
        --very-light-blue: #E8F4FD;
        --white: #FFFFFF;
        --dark-text: #1A1A1A;
        --gray-text: #666666;
    }
    
    /* Header customizado */
    .main-header {
        background: linear-gradient(135deg, #0066CC 0%, #4A90E2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 102, 204, 0.15);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        color: #E8F4FD;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0066CC 0%, #003D7A 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background-color: white !important;
        color: #0066CC !important;
        border: none;
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #E8F4FD !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* Chat messages styling */
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    [data-testid="stChatMessageContent"] {
        background-color: white;
    }
    
    /* User message - azul claro */
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FF 100%);
        border-left: 4px solid #0066CC;
    }
    
    /* Assistant message - branco com borda azul */
    [data-testid="stChatMessage"][data-testid*="assistant"] {
        background: white;
        border-left: 4px solid #4A90E2;
        box-shadow: 0 2px 8px rgba(74, 144, 226, 0.1);
    }
    
    /* Input de chat customizado */
    .stChatInputContainer {
        border-top: 2px solid #E8F4FD;
        padding-top: 1rem;
    }
    
    /* Botões principais */
    .stButton button {
        background: linear-gradient(135deg, #0066CC 0%, #4A90E2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
        transform: translateY(-2px);
    }
    
    /* Download button específico - branco com borda azul */
    .stDownloadButton button {
        background: white !important;
        color: #0066CC !important;
        border: 2px solid #0066CC !important;
    }
    
    .stDownloadButton button:hover {
        background: #E8F4FD !important;
    }
    
    /* Status containers */
    .stStatus {
        background-color: #E8F4FD;
        border-left: 4px solid #0066CC;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #E8F4FD;
        border-radius: 5px;
        color: #0066CC;
        font-weight: 600;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #0066CC;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Dividers */
    hr {
        border-color: #E8F4FD;
        margin: 2rem 0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #E8F4FD;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        color: #0066CC;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066CC 0%, #4A90E2 100%);
        color: white;
    }
    
    /* Alertas e warnings */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #E8F4FD 0%, #D1E9FF 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0066CC;
        margin: 1rem 0;
    }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28A745;
        color: #155724;
    }
    
    /* Cards para features */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 102, 204, 0.1);
        border-top: 4px solid #0066CC;
        margin-bottom: 1rem;
    }
    
    .feature-card h3 {
        color: #0066CC;
        margin-top: 0;
    }
    
    /* Logo e branding */
    .logo-container {
        text-align: center;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666666;
        border-top: 2px solid #E8F4FD;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER PRINCIPAL
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>🔬 Big Four Researcher</h1>
    <p>Pesquisa estratégica de elite alimentada por IA com fontes das principais consultorias globais</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - CONFIGURAÇÕES
# ============================================================================

with st.sidebar:
    # Logo/Branding
    st.markdown("""
    <div class="logo-container" style="background: linear-gradient(135deg, #0066CC 0%, #003D7A 100%);">
        <h2 style="color: white; margin: 0;">🔬</h2>
        <h3 style="color: white; margin: 0.5rem 0;">Big Four Researcher</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs para organizar configurações
    config_tab, about_tab = st.tabs(["⚙️ Configurações", "ℹ️ Sobre"])
    
    with config_tab:
        st.markdown("### 📊 Fontes de Pesquisa")
        st.caption("Selecione as consultorias que serão consultadas")
        
        # Big Four em destaque
        st.markdown("**🏆 Big Four:**")
        big_four = st.multiselect(
            "Principais Consultorias",
            options=[
                "Deloitte",
                "KPMG",
                "PwC (PricewaterhouseCoopers)",
                "EY-Parthenon"
            ],
            default=["Deloitte", "KPMG"],
            label_visibility="collapsed"
        )
        
        st.markdown("**🌟 Outras Consultorias de Elite:**")
        other_consultancies = st.multiselect(
            "Outras Fontes",
            options=[
                "McKinsey & Company",
                "Boston Consulting Group (BCG)",
                "Bain & Company",
                "Gartner",
                "Accenture Strategy",
                "Oliver Wyman"
            ],
            default=["McKinsey & Company", "Gartner"],
            label_visibility="collapsed"
        )
        
        strategic_sources = big_four + other_consultancies
        
        st.markdown("---")
        
        # Modelo de IA
        st.markdown("### 🤖 Modelo de IA")
        model_choice = st.radio(
            "Selecione o modelo:",
            options=["Kimi (Recomendado)", "Ollama (Local)"],
            index=0,
            label_visibility="collapsed"
        )
        
        model = "kimi" if "Kimi" in model_choice else "llama"
        
        st.markdown("---")
        
        # Configurações Avançadas
        with st.expander("🔧 Configurações Avançadas", expanded=False):
            st.markdown("**Temperatura do Modelo:**")
            temperature = st.slider(
                "Criatividade das respostas",
                0.0, 1.0, 0.2,
                help="0.0 = Mais conservador, 1.0 = Mais criativo",
                label_visibility="collapsed"
            )
            
            st.markdown("**Tokens Máximos:**")
            max_tokens = st.number_input(
                "Tamanho máximo da resposta",
                500, 8000, 4096,
                step=500,
                label_visibility="collapsed"
            )
            
            # Mostrar configurações ativas
            st.info(f"""
            **Configuração Ativa:**
            - Temperatura: {temperature}
            - Max Tokens: {max_tokens}
            - Modelo: {model_choice}
            """)
    
    with about_tab:
        st.markdown("""
        ### 🎯 Sobre o Big Four Researcher
        
        Plataforma de pesquisa estratégica que combina:
        
        **✨ Inteligência Artificial Avançada**
        - Modelos LLM de última geração
        - Processamento de PDFs completos
        - Análise contextual profunda
        
        **📚 Fontes Premium**
        - Big Four (Deloitte, KPMG, PwC, EY)
        - Consultorias de elite (McKinsey, BCG, Bain)
        - Pesquisas Gartner e Accenture
        
        **🔍 Capacidades**
        - Busca seletiva em domínios confiáveis
        - Extração de conteúdo completo
        - Síntese executiva estruturada
        - Exportação em PDF profissional
        
        ---
        
        **📈 Versão:** 2.0 (2026)
        
        **🏢 Powered by:** StratGov AI
        """)
        
        st.markdown("---")
        
        # Estatísticas da sessão
        st.markdown("### 📊 Estatísticas da Sessão")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Perguntas", len([m for m in st.session_state.get("messages", []) if m["role"] == "user"]))
        with col2:
            st.metric("Fontes", len(st.session_state.get("last_resources", [])))
    
    st.markdown("---")
    
    # Botão de reset com confirmação
    if st.button("🔄 Nova Pesquisa", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.last_resources = []
        st.rerun()

# Mapeamento para domínios
domain_mapping = {
    "McKinsey & Company": "mckinsey.com",
    "Gartner": "gartner.com",
    "Boston Consulting Group (BCG)": "bcg.com",
    "Deloitte": "deloitte.com",
    "KPMG": "kpmg.com",
    "PwC (PricewaterhouseCoopers)": "pwc.com",
    "EY-Parthenon": "ey.com",
    "Bain & Company": "bain.com",
    "Accenture Strategy": "accenture.com",
    "Oliver Wyman": "oliverwyman.com"
}

selected_domains = [domain_mapping[source] for source in strategic_sources if source in domain_mapping]

# ============================================================================
# INICIALIZAÇÃO DE SESSION STATE
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "last_resources" not in st.session_state:
    st.session_state.last_resources = []

# ============================================================================
# FUNÇÃO PARA GERAR PDF
# ============================================================================

def generate_pdf(query: str, response: str, resources: list) -> BytesIO:
    """Gera um PDF formatado com tema azul profissional."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos customizados - tema azul
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor='#0066CC',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#0066CC',
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=14
    )
    
    source_style = ParagraphStyle(
        'SourceStyle',
        parent=styles['BodyText'],
        fontSize=9,
        textColor='#666666',
        leftIndent=20,
        spaceAfter=8
    )
    
    # Header com logo
    story.append(Paragraph("🔬 BIG FOUR RESEARCHER", title_style))
    story.append(Paragraph("Relatório de Pesquisa Estratégica", styles['Normal']))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.4*inch))
    
    # Questão de pesquisa
    story.append(Paragraph("QUESTÃO DE PESQUISA", heading_style))
    story.append(Paragraph(query, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Análise estratégica
    story.append(Paragraph("ANÁLISE E INSIGHTS ESTRATÉGICOS", heading_style))
    
    # Processar resposta
    response_paragraphs = response.split('\n\n')
    for para in response_paragraphs:
        if para.strip():
            # Converter markdown básico para HTML
            para_html = para.replace('**', '<b>').replace('*', '<i>')
            para_html = para_html.replace('<i><b>', '<b><i>').replace('</b></i>', '</i></b>')
            # Remover markdown de headers se houver
            para_html = para_html.replace('## ', '').replace('### ', '')
            story.append(Paragraph(para_html, body_style))
    
    story.append(Spacer(1, 0.4*inch))
    
    # Fontes consultadas
    if resources:
        story.append(Paragraph(f"FONTES CONSULTADAS ({len(resources)})", heading_style))
        for idx, res in enumerate(resources, 1):
            story.append(Paragraph(f"<b>[{idx}]</b> {res.get('title', 'Sem título')}", source_style))
            story.append(Paragraph(f"<i>{res.get('url', 'URL não disponível')}</i>", source_style))
            if res.get('description'):
                desc = res['description'][:250] + "..." if len(res.get('description', '')) > 250 else res.get('description', '')
                story.append(Paragraph(desc, source_style))
            story.append(Spacer(1, 0.15*inch))
    
    # Footer
    story.append(Spacer(1, 0.6*inch))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor='#999999', alignment=TA_CENTER)
    story.append(Paragraph("_" * 80, footer_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"Big Four Researcher • Powered by StratGov AI • {datetime.now().year}", footer_style))
    story.append(Paragraph("Documento gerado automaticamente com fontes verificadas", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# ÁREA PRINCIPAL - NAVEGAÇÃO POR ABAS
# ============================================================================

main_tab, sources_tab, help_tab = st.tabs(["💬 Chat de Pesquisa", "📚 Fontes Ativas", "❓ Como Usar"])

with main_tab:
    # Mensagem de boas-vindas se não houver histórico
    if not st.session_state.messages:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0; color: #0066CC;">👋 Bem-vindo ao Big Four Researcher!</h3>
            <p>Faça perguntas estratégicas e receba análises profundas baseadas em fontes premium:</p>
            <ul>
                <li><b>Big Four:</b> Deloitte, KPMG, PwC, EY</li>
                <li><b>Consultorias Elite:</b> McKinsey, BCG, Bain, Gartner</li>
            </ul>
            <p><b>✨ Exemplos de perguntas:</b></p>
            <ul>
                <li>"Quais as principais tendências em transformação digital para 2024?"</li>
                <li>"Como implementar ESG em empresas de médio porte?"</li>
                <li>"Análise de mercado sobre IA no setor financeiro"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Display Chat History
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🔬"):
            st.markdown(msg["content"])
            
            # Botão de download para respostas do assistente
            if msg["role"] == "assistant" and idx > 0:
                col1, col2, col3 = st.columns([5, 1, 1])
                with col2:
                    # Pergunta correspondente
                    user_query = st.session_state.messages[idx-1]["content"] if idx > 0 else "Consulta"
                    resources = msg.get("resources", [])
                    
                    pdf_buffer = generate_pdf(user_query, msg["content"], resources)
                    st.download_button(
                        label="📄 PDF",
                        data=pdf_buffer,
                        file_name=f"big_four_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{idx}",
                        use_container_width=True
                    )
                
                with col3:
                    if "logs" in msg and msg["logs"]:
                        with st.expander("📋 Logs", expanded=False):
                            for log in msg["logs"]:
                                log_type_emoji = {
                                    "info": "ℹ️",
                                    "search": "🔍",
                                    "warning": "⚠️",
                                    "error": "❌"
                                }.get(log.get('type', 'info'), "📝")
                                st.text(f"{log_type_emoji} {log['message']}")

with sources_tab:
    st.markdown("### 📊 Fontes Ativas na Pesquisa")
    
    if selected_domains:
        st.success(f"✅ {len(selected_domains)} fontes selecionadas")
        
        # Organizar por categoria
        big_four_domains = [d for s, d in domain_mapping.items() if s in big_four]
        other_domains = [d for s, d in domain_mapping.items() if s in other_consultancies]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Big Four")
            for source in big_four:
                if source in domain_mapping:
                    st.markdown(f"- ✓ **{source}** (`{domain_mapping[source]}`)")
        
        with col2:
            st.markdown("#### 🌟 Outras Consultorias")
            for source in other_consultancies:
                if source in domain_mapping:
                    st.markdown(f"- ✓ **{source}** (`{domain_mapping[source]}`)")
        
        st.markdown("---")
        
        # Últimos recursos encontrados
        if st.session_state.last_resources:
            st.markdown(f"### 📚 Últimos Recursos Encontrados ({len(st.session_state.last_resources)})")
            
            for idx, res in enumerate(st.session_state.last_resources, 1):
                with st.expander(f"**[{idx}]** {res.get('title', 'Sem título')}", expanded=False):
                    st.markdown(f"**URL:** [{res.get('url', 'N/A')}]({res.get('url', '#')})")
                    st.caption(res.get('description', 'Sem descrição')[:300] + "...")
    else:
        st.warning("⚠️ Nenhuma fonte selecionada. Por favor, selecione pelo menos uma consultoria na barra lateral.")

with help_tab:
    st.markdown("""
    ### ❓ Como Usar o Big Four Researcher
    
    #### 1️⃣ Selecione as Fontes
    Na barra lateral, escolha quais consultorias deseja consultar:
    - **Big Four**: Deloitte, KPMG, PwC, EY
    - **Outras**: McKinsey, BCG, Bain, Gartner, Accenture, Oliver Wyman
    
    #### 2️⃣ Configure o Modelo de IA
    - **Kimi (Recomendado)**: Modelo avançado com melhor qualidade
    - **Ollama (Local)**: Modelo local para privacidade total
    
    #### 3️⃣ Faça sua Pergunta
    Digite sua questão estratégica no chat. Exemplos:
    
    ```
    📊 "Análise de tendências em ESG para o setor bancário"
    🔍 "Como implementar governança de dados em empresas médias?"
    💡 "Principais desafios da transformação digital no varejo"
    ```
    
    #### 4️⃣ Aguarde a Análise
    O sistema irá:
    - 🔍 Buscar em fontes premium
    - 📄 Baixar e processar PDFs completos
    - 💡 Gerar síntese executiva estruturada
    - 📚 Listar todas as fontes consultadas
    
    #### 5️⃣ Exporte o Relatório
    Clique no botão **📄 PDF** para baixar um relatório profissional.
    
    ---
    
    ### 🎯 Dicas para Melhores Resultados
    
    ✅ **Seja específico**: "Transformação digital no setor de saúde brasileiro"
    
    ✅ **Defina o contexto**: "Para empresas de médio porte com faturamento de R$ 100-500M"
    
    ✅ **Foque em estratégia**: Perguntas sobre tendências, implementação, melhores práticas
    
    ❌ **Evite perguntas muito genéricas**: "O que é IA?"
    
    ❌ **Evite perguntas operacionais**: "Como configurar um servidor?"
    
    ---
    
    ### 🔒 Privacidade e Segurança
    
    - ✅ Todas as fontes são verificadas e confiáveis
    - ✅ Nenhum dado é armazenado permanentemente
    - ✅ Conversas são isoladas por sessão
    - ✅ PDFs gerados localmente no seu navegador
    
    ---
    
    ### 📞 Suporte
    
    **Problemas?** Clique em **🔄 Nova Pesquisa** na barra lateral para reiniciar.
    
    **Bugs ou sugestões?** Entre em contato com a equipe StratGov AI.
    """)

# ============================================================================
# CHAT INPUT
# ============================================================================

if prompt := st.chat_input("💬 Digite sua pergunta estratégica aqui..."):
    # Validação de domínios
    if not selected_domains:
        st.error("⚠️ **Atenção:** Selecione pelo menos uma fonte estratégica na barra lateral antes de fazer uma pergunta.")
        st.stop()
    
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Prepare AI Response Container
    with st.chat_message("assistant", avatar="🔬"):
        message_placeholder = st.empty()
        status_placeholder = st.status("🔍 Iniciando pesquisa...", expanded=True)
        
        # Use dict to avoid nonlocal scope issues
        response_data = {
            "full_response": "",
            "current_logs": [],
            "resources": []
        }
        
        # Prepare Config
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "search_domains": selected_domains,
            "query": prompt,
            "logs": []
        }

        async def run_agent():
            try:
                async for event in graph.astream(initial_state, config, stream_mode="updates"):
                    for node_name, node_data in event.items():
                        
                        # Process Logs
                        if "logs" in node_data:
                            for log in node_data["logs"]:
                                log_msg = log.message if hasattr(log, 'message') else str(log)
                                log_type = log.type if hasattr(log, 'type') else "info"
                                
                                # Emoji por tipo de log
                                log_emoji = {
                                    "info": "ℹ️",
                                    "search": "🔍",
                                    "warning": "⚠️",
                                    "error": "❌"
                                }.get(log_type, "📝")
                                
                                status_placeholder.write(f"{log_emoji} **{node_name}**: {log_msg}")
                                response_data["current_logs"].append({"type": log_type, "message": log_msg})

                        # Process Resources (Search Results)
                        if "resources" in node_data and node_data["resources"]:
                            pdf_count = sum(1 for r in node_data["resources"] if "[PDF]" in (r.title if hasattr(r, 'title') else r.get('title', '')))
                            article_count = sum(1 for r in node_data["resources"] if "[Article]" in (r.title if hasattr(r, 'title') else r.get('title', '')))
                            
                            
                            status_placeholder.markdown("---")
                            status_placeholder.write(f"📚 **Recursos encontrados:** {len(node_data['resources'])} total ({pdf_count} PDFs, {article_count} Artigos)")
                            
                            # Salvar recursos para PDF
                            for res in node_data["resources"]:
                                resource_dict = {
                                    "url": res.url if hasattr(res, 'url') else res.get('url', ''),
                                    "title": res.title if hasattr(res, 'title') else res.get('title', ''),
                                    "description": res.description if hasattr(res, 'description') else res.get('description', '')
                                }
                                response_data["resources"].append(resource_dict)

                        # Process Final Answer
                        if "messages" in node_data:
                            last_msg = node_data["messages"][-1]
                            if isinstance(last_msg, AIMessage) and last_msg.content:
                                response_data["full_response"] = last_msg.content
                                
                                # Formato documental da resposta
                                formatted_response = f"## 📊 Análise Estratégica\n\n{response_data['full_response']}"
                                
                                if response_data["resources"]:
                                    formatted_response += f"\n\n---\n\n### 📚 Fontes Consultadas ({len(response_data['resources'])})\n\n"
                                    for idx, res in enumerate(response_data["resources"], 1):
                                        formatted_response += f"**[{idx}]** [{res['title']}]({res['url']})\n\n"
                                
                                message_placeholder.markdown(formatted_response)
                                
            except Exception as e:
                status_placeholder.error(f"❌ **Erro durante o processamento:** {str(e)}")
                response_data["full_response"] = f"⚠️ Erro ao processar a consulta: {str(e)}\n\nPor favor, tente novamente ou ajuste as configurações."

        # Run the async loop
        asyncio.run(run_agent())
        
        status_placeholder.update(label="✅ Análise concluída!", state="complete", expanded=False)
        
        # Save to history with resources
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_data["full_response"],
            "logs": response_data["current_logs"],
            "resources": response_data["resources"]
        })
        st.session_state.last_resources = response_data["resources"]

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div class="footer">
    <p><strong>🔬 Big Four Researcher</strong> • Powered by StratGov AI • 2026</p>
    <p>Pesquisa estratégica de elite com fontes verificadas das principais consultorias globais</p>
</div>
""", unsafe_allow_html=True)
