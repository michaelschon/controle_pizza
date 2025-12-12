import streamlit as st
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Controle de Estoque - Pizzaria", page_icon="🍕", layout="wide")

# Arquivo para salvar os dados
DATA_FILE = Path("./estoque_pizzas.json")

# Dias da semana
DIAS_SEMANA = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira"]

# Sabores FIXOS
SABORES = ["Calabresa", "Mussarela", "Frango", "Americana"]

# Inicializar session state
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = {}  # {sabor: {dia: quantidade_pedida}}
if 'retiradas' not in st.session_state:
    st.session_state.retiradas = []  # Lista de todas as retiradas

# Função para carregar dados
def carregar_dados():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            st.session_state.pedidos = dados.get('pedidos', {})
            st.session_state.retiradas = dados.get('retiradas', [])

# Função para salvar dados
def salvar_dados():
    dados = {
        'pedidos': st.session_state.pedidos,
        'retiradas': st.session_state.retiradas
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# Função para calcular total pedido por sabor e dia
def calcular_pedido_sabor_dia(sabor, dia):
    if sabor in st.session_state.pedidos and dia in st.session_state.pedidos[sabor]:
        return st.session_state.pedidos[sabor][dia]
    return 0

# Função para calcular total entregue por sabor e dia
def calcular_entregue_sabor_dia(sabor, dia):
    total = 0
    for retirada in st.session_state.retiradas:
        if retirada['dia'] == dia and sabor in retirada['pizzas']:
            total += retirada['pizzas'][sabor]
    return total

# Função para calcular estoque restante por sabor e dia
def calcular_restante_sabor_dia(sabor, dia):
    pedido = calcular_pedido_sabor_dia(sabor, dia)
    entregue = calcular_entregue_sabor_dia(sabor, dia)
    return pedido - entregue

# Carregar dados ao iniciar
carregar_dados()

# CSS customizado para tema escuro
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🍕 Controle de Estoque - Pizzaria")

# Abas
tab1, tab2, tab3 = st.tabs(["📝 Cadastro", "📊 Relatório", "💾 Backup"])

# ABA 1: CADASTRO (Registrar Nova Retirada)
with tab1:
    st.header("Registrar Nova Retirada")
    
    # Dia da Semana
    st.markdown("**Dia da Semana**")
    dia_selecionado = st.selectbox(
        "Dia da Semana",
        DIAS_SEMANA,
        label_visibility="collapsed"
    )
    
    # Nome de quem retirou
    st.markdown("**Nome de Quem Retirou**")
    nome_retirou = st.text_input(
        "Nome de Quem Retirou",
        placeholder="Digite o nome aqui...",
        label_visibility="collapsed"
    )
    
    # Observações
    st.markdown("**Observações (opcional)**")
    observacoes = st.text_area(
        "Observações",
        placeholder="Alguma observação adicional...",
        label_visibility="collapsed",
        height=100
    )
    
    st.markdown("---")
    
    # Sabores das Pizzas
    st.markdown("### Sabores das Pizzas")
    
    # Inicializar contador de pizzas no session state
    if 'contador_pizzas' not in st.session_state:
        st.session_state.contador_pizzas = {sabor: 0 for sabor in SABORES}
    
    # Para cada sabor, mostrar botões + e -
    for sabor in SABORES:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{sabor}**")
        
        with col2:
            # Botão de diminuir
            if st.button("➖", key=f"menos_{sabor}", use_container_width=True):
                if st.session_state.contador_pizzas[sabor] > 0:
                    st.session_state.contador_pizzas[sabor] -= 1
                    st.rerun()
        
        with col3:
            # Mostrar contador atual
            st.markdown(f"<div style='text-align: center; font-size: 24px; font-weight: bold;'>{st.session_state.contador_pizzas[sabor]}</div>", unsafe_allow_html=True)
        
        with col4:
            # Botão de aumentar
            if st.button("➕", key=f"mais_{sabor}", use_container_width=True):
                st.session_state.contador_pizzas[sabor] += 1
                st.rerun()
    
    st.markdown("---")
    
    # Total de pizzas
    total_pizzas = sum(st.session_state.contador_pizzas.values())
    st.info(f"**Total de Pizzas: {total_pizzas}**")
    
    # Botões de ação
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.contador_pizzas = {sabor: 0 for sabor in SABORES}
            st.rerun()
    
    with col2:
        if st.button("💾 Salvar Retirada", type="primary", use_container_width=True):
            if not nome_retirou.strip():
                st.error("❌ Por favor, informe o nome de quem retirou!")
            elif total_pizzas == 0:
                st.error("❌ Adicione pelo menos uma pizza!")
            else:
                # Verificar se há excedentes
                excedentes = []
                for sabor, qtd in st.session_state.contador_pizzas.items():
                    if qtd > 0:
                        restante = calcular_restante_sabor_dia(sabor, dia_selecionado)
                        if qtd > restante:
                            excedentes.append({
                                'sabor': sabor,
                                'pedido': calcular_pedido_sabor_dia(sabor, dia_selecionado),
                                'excedente': qtd - restante
                            })
                
                # Criar registro da retirada
                retirada = {
                    'id': len(st.session_state.retiradas) + 1,
                    'data': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    'dia': dia_selecionado,
                    'nome': nome_retirou.strip(),
                    'observacoes': observacoes.strip(),
                    'pizzas': {sabor: qtd for sabor, qtd in st.session_state.contador_pizzas.items() if qtd > 0},
                    'total': total_pizzas,
                    'tem_excedente': len(excedentes) > 0,
                    'excedentes': excedentes
                }
                
                st.session_state.retiradas.append(retirada)
                salvar_dados()
                
                # Limpar formulário
                st.session_state.contador_pizzas = {sabor: 0 for sabor in SABORES}
                
                if len(excedentes) > 0:
                    st.warning(f"⚠️ Retirada salva, mas ATENÇÃO: Foram detectados excedentes!")
                    for exc in excedentes:
                        st.error(f"🔴 **{exc['sabor']}**: Foram pedidas apenas {exc['pedido']} pizzas para {dia_selecionado}, mas você está entregando {exc['excedente']} a mais!")
                else:
                    st.success("✅ Retirada registrada com sucesso!")
                
                st.rerun()

# ABA 2: RELATÓRIO
with tab2:
    st.header("📊 Relatório de Entregas")
    
    # Seção de configuração de pedidos
    with st.expander("⚙️ Configurar Pedidos por Dia", expanded=not bool(st.session_state.pedidos)):
        st.info("💡 Configure quantas pizzas de cada sabor foram pedidas para cada dia")
        
        for sabor in SABORES:
            st.markdown(f"**🍕 {sabor}**")
            cols = st.columns(3)
            
            for idx, dia in enumerate(DIAS_SEMANA):
                with cols[idx]:
                    valor_atual = calcular_pedido_sabor_dia(sabor, dia)
                    novo_valor = st.number_input(
                        dia,
                        min_value=0,
                        value=valor_atual,
                        step=1,
                        key=f"pedido_{sabor}_{dia}"
                    )
                    
                    if novo_valor != valor_atual:
                        if sabor not in st.session_state.pedidos:
                            st.session_state.pedidos[sabor] = {}
                        st.session_state.pedidos[sabor][dia] = novo_valor
                        salvar_dados()
            
            st.markdown("---")
        
        # Mostrar total configurado
        if st.session_state.pedidos:
            total_config = sum(sum(dias.values()) for dias in st.session_state.pedidos.values())
            st.success(f"**🍕 Total de pizzas pedidas: {total_config}**")
    
    st.markdown("---")
    
    if not st.session_state.pedidos:
        st.warning("⚠️ Configure os pedidos acima primeiro")
    else:
        # Calcular totais gerais
        total_pedido = sum(sum(dias.values()) for dias in st.session_state.pedidos.values())
        total_entregue = sum(ret['total'] for ret in st.session_state.retiradas)
        total_restante = total_pedido - total_entregue
        
        # Métricas no topo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🍕 Total Pedido", f"{total_pedido} pizzas")
        with col2:
            st.metric("✅ Total Entregue", f"{total_entregue} pizzas")
        with col3:
            st.metric("📦 Restante", f"{total_restante} pizzas", 
                     delta=f"{total_restante - total_pedido}" if total_restante != total_pedido else "0")
        
        st.markdown("---")
        
        # Verificar retiradas com excedentes
        retiradas_com_excedente = [r for r in st.session_state.retiradas if r.get('tem_excedente', False)]
        if retiradas_com_excedente:
            st.error(f"⚠️ **ALERTA:** {len(retiradas_com_excedente)} retirada(s) com excedente(s) detectada(s)!")
            
            total_excedente = sum(
                sum(exc['excedente'] for exc in ret['excedentes'])
                for ret in retiradas_com_excedente
            )
            st.warning(f"📊 Total de pizzas entregues além do pedido: **{total_excedente} pizzas**")
        
        st.markdown("---")
        
        # Estoque por Sabor e Dia
        st.subheader("📋 Estoque por Sabor e Dia")
        
        for sabor in SABORES:
            with st.expander(f"🍕 {sabor}", expanded=True):
                cols = st.columns(3)
                
                for idx, dia in enumerate(DIAS_SEMANA):
                    with cols[idx]:
                        pedido = calcular_pedido_sabor_dia(sabor, dia)
                        entregue = calcular_entregue_sabor_dia(sabor, dia)
                        restante = pedido - entregue
                        
                        st.markdown(f"**{dia}**")
                        
                        # Cores baseadas no estoque
                        if restante < 0:
                            st.markdown(f"🔴 **{restante}** / {pedido}")
                            st.caption(f"⚠️ Excedente: {abs(restante)}")
                        elif restante == 0 and pedido > 0:
                            st.markdown(f"🔴 {restante} / {pedido}")
                            st.caption("Esgotado")
                        elif restante < pedido * 0.2 and pedido > 0:
                            st.markdown(f"🟡 {restante} / {pedido}")
                            st.caption("Estoque baixo")
                        elif pedido > 0:
                            st.markdown(f"🟢 {restante} / {pedido}")
                        else:
                            st.markdown(f"⚪ Não pedido")
        
        st.markdown("---")
        
        # Lista de Retiradas
        st.subheader("📜 Histórico de Retiradas")
        
        if st.session_state.retiradas:
            st.info(f"**Total de retiradas: {len(st.session_state.retiradas)}**")
            
            for retirada in reversed(st.session_state.retiradas):
                with st.expander(
                    f"#{retirada['id']} - {retirada['nome']} ({retirada['dia']}) - {retirada['total']} pizzas - {retirada['data']}"
                    + (" 🔴 EXCEDENTE" if retirada.get('tem_excedente', False) else "")
                ):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Nome:** {retirada['nome']}")
                        st.markdown(f"**Dia:** {retirada['dia']}")
                        st.markdown(f"**Data:** {retirada['data']}")
                        if retirada.get('observacoes'):
                            st.markdown(f"**Obs:** {retirada['observacoes']}")
                    
                    with col2:
                        st.markdown(f"**Total:** {retirada['total']} pizzas")
                    
                    st.markdown("**Pizzas retiradas:**")
                    for sabor, qtd in retirada['pizzas'].items():
                        st.text(f"• {sabor}: {qtd}")
                    
                    # Mostrar excedentes se houver
                    if retirada.get('tem_excedente', False):
                        st.markdown("---")
                        st.error("⚠️ **EXCEDENTES DETECTADOS:**")
                        for exc in retirada['excedentes']:
                            st.markdown(f"🔴 **{exc['sabor']}**: {exc['excedente']} pizzas a mais (pedido: {exc['pedido']})")
                    
                    # Botão de apagar registro
                    st.markdown("---")
                    if st.button(f"🗑️ Apagar Registro #{retirada['id']}", key=f"del_ret_{retirada['id']}", type="secondary", use_container_width=True):
                        st.session_state.retiradas = [r for r in st.session_state.retiradas if r['id'] != retirada['id']]
                        salvar_dados()
                        st.success(f"✅ Registro #{retirada['id']} apagado!")
                        st.rerun()
        else:
            st.info("Nenhuma retirada registrada ainda.")

# ABA 3: BACKUP
with tab3:
    st.header("💾 Backup e Restauração")
    
    st.markdown("### 📥 Exportar Dados")
    st.info("Faça backup dos seus dados!")
    
    if st.session_state.pedidos or st.session_state.retiradas:
        dados_backup = {
            'pedidos': st.session_state.pedidos,
            'retiradas': st.session_state.retiradas,
            'data_backup': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        json_str = json.dumps(dados_backup, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="📥 Baixar Backup (JSON)",
            data=json_str,
            file_name=f"backup_pizzaria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.warning("Nenhum dado para exportar.")
    
    st.markdown("---")
    
    st.markdown("### 📤 Importar Dados")
    st.info("Restaure um backup anterior")
    
    uploaded_file = st.file_uploader("Selecione o arquivo (.json)", type=['json'])
    
    if uploaded_file:
        try:
            dados_importados = json.load(uploaded_file)
            
            if 'pedidos' in dados_importados or 'retiradas' in dados_importados:
                st.success("✅ Arquivo válido!")
                
                with st.expander("👁️ Preview"):
                    st.json(dados_importados)
                
                if st.button("✅ Confirmar Importação", type="primary", use_container_width=True):
                    st.session_state.pedidos = dados_importados.get('pedidos', {})
                    st.session_state.retiradas = dados_importados.get('retiradas', [])
                    salvar_dados()
                    st.success("✅ Dados importados!")
                    st.rerun()
            else:
                st.error("❌ Arquivo inválido!")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
    
    st.markdown("---")
    
    # Limpar tudo
    if st.button("🗑️ Limpar Todos os Dados", type="secondary", use_container_width=True):
        st.session_state.pedidos = {}
        st.session_state.retiradas = []
        if DATA_FILE.exists():
            DATA_FILE.unlink()
        st.success("✅ Todos os dados foram limpos!")
        st.rerun()

# Rodapé
st.markdown("---")
st.caption("🍕 Sistema de Controle de Pizzaria | Sabores: Calabresa, Mussarela, Frango, Americana")
