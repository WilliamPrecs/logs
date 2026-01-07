import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configuração da página
st.set_page_config(
    page_title="MONITOR DE LOGS - SISTEMA",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS customizado para tema terminal
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #00ff00;
    }
    .terminal-box {
        background-color: #000000;
        border: 2px solid #00ff00;
        padding: 15px;
        font-family: 'Consolas', 'Courier New', monospace;
        color: #00ff00;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    .terminal-text {
        font-family: 'Consolas', 'Courier New', monospace;
        color: #00ff00;
        white-space: pre-wrap;
        font-size: 14px;
    }
    h1, h2, h3 {
        color: #00ff00;
        font-family: 'Consolas', 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# URL da API
API_URL = "https://auwb72k75qnn3ncgrchc6qpyv40kvdaa.lambda-url.sa-east-1.on.aws/"

# Função para ajustar horário -3 horas
def ajustar_horario(data_hora):
    try:
        from datetime import datetime, timedelta
        dt = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
        dt = dt - timedelta(hours=3)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return data_hora

# Função para limpar valor
def limpar_valor(valor):
    import re
    return re.sub(r'\s*:\s*[^)]*\)', '', valor).replace('(campo', '').replace(')', '').strip()

# Função para processar logs de webhooks
def processar_logs_metas_diarias(data):
    if not data or not isinstance(data, list):
        return '> Nenhum evento de negócio registrado'
    
    eventos = []
    evento_atual = None
    
    for log in data:
        msg = log.get('mensagem', '').strip()
        
        if msg == "==================================================":
            if evento_atual:
                eventos.append(evento_atual)
            evento_atual = {'data': ajustar_horario(log.get('data', '')), 'linhas': []}
            continue
        
        if evento_atual and msg and not msg.startswith(('"', '{', '}')) and 'EVENTO COMPLETO' not in msg:
            evento_atual['linhas'].append(msg)
    
    if evento_atual:
        eventos.append(evento_atual)
    
    if not eventos:
        return '> Nenhum evento de negócio registrado'
    
    ultimo_evento = eventos[-1]
    resumo = []
    
    for linha in ultimo_evento['linhas']:
        if linha.startswith("ID NEGÓCIO:"):
            valor = limpar_valor(linha.split(':')[1].strip())
            resumo.append(f"> ID NEGÓCIO: {valor}")
        elif linha.startswith("PROPRIETÁRIO:"):
            valor = limpar_valor(':'.join(linha.split(':')[1:]).strip())
            resumo.append(f"> PROPRIETÁRIO: {valor}")
        elif linha.startswith("DATA:"):
            valor = limpar_valor(':'.join(linha.split(':')[1:]).strip())
            resumo.append(f"> DATA: {valor}")
        elif linha.startswith("ID ETAPA:"):
            valor = limpar_valor(':'.join(linha.split(':')[1:]).strip())
            resumo.append(f"> ETAPA: {valor}")
        elif linha.startswith("ORÇAMENTO:"):
            valor = limpar_valor(linha.split(':')[1].strip())
            resumo.append(f"> ORÇAMENTO: {valor}")
        elif linha.startswith("ORGANIZAÇÃO:"):
            valor = limpar_valor(':'.join(linha.split(':')[1:]).strip())
            resumo.append(f"> ORGANIZAÇÃO: {valor}")
        elif linha.startswith("TRIBUNAL:"):
            valor = limpar_valor(linha.split(':')[1].strip())
            resumo.append(f"> TRIBUNAL: {valor}")
    
    return '\n'.join(resumo) if resumo else '> Nenhum dado de negócio encontrado'

# Função para processar logs de movimentacoes
def processar_logs_movimentacoes(data):
    if not data or not isinstance(data, list):
        return '> Nenhuma operação de movimentações registrada'
    
    logs_mov = [log for log in data if log.get('origem') == 'movimentacoesWilliam']
    
    if not logs_mov:
        return '> Nenhuma operação de movimentações registrada'
    
    resumo = []
    status_operacao = None
    tabela_usada = None
    total_registros = None
    municipios_banco = None
    municipios_arquivo = None
    municipios_faltando = []
    
    for log in reversed(logs_mov):
        msg = log.get('mensagem', '').replace('🔍', '').replace('📊', '').replace('📥', '').replace('🔗', '').replace('✅', '').replace('❌', '').replace('⚠️', '').strip()
        
        if 'Download concluído' in msg:
            status_operacao = 'Download concluído'
        elif 'Conectando ao SQLite' in msg:
            status_operacao = 'Conectado ao SQLite'
        elif 'Conectando ao PostgreSQL' in msg:
            status_operacao = 'Conectado ao PostgreSQL'
        elif 'Usando tabela:' in msg:
            tabela_usada = msg.split(':')[1].strip() if ':' in msg else 'N/A'
        elif 'Total de registros:' in msg:
            total_registros = msg.split(':')[1].strip() if ':' in msg else 'N/A'
        elif 'Municípios no banco de dados:' in msg:
            municipios_banco = msg.split(':')[1].strip() if ':' in msg else 'N/A'
        elif 'Municípios no arquivo:' in msg:
            municipios_arquivo = msg.split(':')[1].strip() if ':' in msg else 'N/A'
        elif 'VALIDAÇÃO FALHOU' in msg:
            status_operacao = 'Validação falhou'
        elif 'Operação cancelada' in msg:
            status_operacao = 'Operação cancelada'
        elif msg.startswith('- ') and status_operacao == 'Validação falhou':
            municipios_faltando.append(msg.replace('- ', '').strip())
    
    resumo.append('> ========================================')
    resumo.append('> RESUMO DE MOVIMENTAÇÕES')
    resumo.append('> ========================================')
    
    if status_operacao:
        resumo.append(f'> STATUS: {status_operacao}')
    if tabela_usada:
        resumo.append(f'> TABELA: {tabela_usada}')
    if total_registros:
        resumo.append(f'> TOTAL DE REGISTROS: {total_registros}')
    if municipios_banco and municipios_arquivo:
        resumo.append(f'> MUNICÍPIOS NO BANCO: {municipios_banco}')
        resumo.append(f'> MUNICÍPIOS NO ARQUIVO: {municipios_arquivo}')
        try:
            diferenca = int(municipios_banco) - int(municipios_arquivo)
            if diferenca > 0:
                resumo.append(f'> DIFERENÇA: {diferenca} município(s) a mais no banco')
        except:
            pass
    if municipios_faltando:
        resumo.append(f'> MUNICÍPIOS FALTANDO NO ARQUIVO: {len(municipios_faltando)}')
        for mun in municipios_faltando:
            resumo.append(f'>   - {mun}')
    if logs_mov:
        ultimo_log = logs_mov[-1]
        hora_ajustada = ajustar_horario(ultimo_log.get('data', ''))
        resumo.append(f'> ÚLTIMA ATUALIZAÇÃO: {hora_ajustada}')
    
    resumo.append('> ========================================')
    
    return '\n'.join(resumo)

# Função para buscar logs
@st.cache_data(ttl=10)  # Cache de 10 segundos
def buscar_logs():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# Header
st.markdown("### > SISTEMA DE MONITORAMENTO")

# Auto-refresh
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

# Buscar dados
data = buscar_logs()

# Layout em 2 colunas
col1, col2 = st.columns(2)

# Coluna 1: Metas Diárias
with col1:
    st.markdown("#### [1] METAS DIÁRIAS")
    if data:
        resumo_metas = processar_logs_metas_diarias(data)
        st.markdown(f'<div class="terminal-box"><div class="terminal-text">{resumo_metas}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="terminal-box"><div class="terminal-text">> Carregando dados...</div></div>', unsafe_allow_html=True)

# Coluna 2: Saldo em Conta
with col2:
    st.markdown("#### [2] SALDO EM CONTA")
    if data:
        resumo_mov = processar_logs_movimentacoes(data)
        st.markdown(f'<div class="terminal-box"><div class="terminal-text">{resumo_mov}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="terminal-box"><div class="terminal-text">> Carregando dados...</div></div>', unsafe_allow_html=True)

# Auto-refresh
if st.session_state.auto_refresh:
    time.sleep(10)
    st.rerun()

