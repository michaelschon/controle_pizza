import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Controle de Pizzas",
    page_icon="🍕",
    layout="wide"
)

# Arquivo para armazenar os dados
DATA_FILE = "pizzas_data.json"

# Sabores fixos disponíveis
SABORES_DISPONIVEIS = ["Calabresa", "Mussarela", "Frango", "Americana"]

# Dias da semana disponíveis
DIAS_SEMANA = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira"]

# Função para carregar dados
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Função para salvar dados
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Função para adicionar retirada
def add_retirada(dia, nome, sabores_list, observacao=""):
    data = load_data()
    
    total_pizzas = sum(sab['quantidade'] for sab in sabores_list)
    
    nova_retirada = {
        'id': len(data) + 1,
        'dia': dia,
        'nome': nome,
        'total_pizzas': total_pizzas,
        'sabores': sabores_list,
        'observacao': observacao,
        'data_hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data.append(nova_retirada)
    save_data(data)
    return True

# Função para deletar retirada
def delete_retirada(retirada_id):
    data = load_data()
    data = [r for r in data if r['id'] != retirada_id]
    save_data(data)

# Título
st.title("🍕 Sistema de Controle de Pizzas")

# Criar abas
tab1, tab2, tab3 = st.tabs(["📝 Cadastro", "📊 Relatório", "💾 Backup"])

# ABA 1: CADASTRO
with tab1:
    st.header("Registrar Nova Retirada")
    
    # Inicializar session state para limpar o nome
    if 'nome_input' not in st.session_state:
        st.session_state.nome_input = ""
    
    if 'clear_trigger' not in st.session_state:
        st.session_state.clear_trigger = 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        dia_selecionado = st.selectbox(
            "Dia da Semana",
            DIAS_SEMANA
        )
        
    with col2:
        nome_pessoa = st.text_input(
            "Nome de Quem Retirou",
            value=st.session_state.nome_input,
            key=f"nome_{st.session_state.clear_trigger}",
            placeholder="Digite o nome aqui..."
        )
    
    # Campo de observação
    observacao = st.text_area(
        "Observações (opcional)",
        placeholder="Alguma observação adicional...",
        height=80,
        key=f"obs_{st.session_state.clear_trigger}"
    )
    
    st.divider()
    
    st.subheader("Sabores das Pizzas")
    
    # Inicializar session state para as quantidades
    if 'quantidades' not in st.session_state:
        st.session_state.quantidades = {sabor: 0 for sabor in SABORES_DISPONIVEIS}
    
    # Interface para cada sabor
    for sabor in SABORES_DISPONIVEIS:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{sabor}**")
        
        with col2:
            if st.button("➖", key=f"minus_{sabor}"):
                if st.session_state.quantidades[sabor] > 0:
                    st.session_state.quantidades[sabor] -= 1
                    st.rerun()
        
        with col3:
            st.write(f"**{st.session_state.quantidades[sabor]}**")
        
        with col4:
            if st.button("➕", key=f"plus_{sabor}"):
                st.session_state.quantidades[sabor] += 1
                st.rerun()
    
    st.divider()
    
    # Mostrar total
    total_pizzas = sum(st.session_state.quantidades.values())
    st.info(f"**Total de Pizzas:** {total_pizzas}")
    
    # Botões
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Limpar", use_container_width=True):
            st.session_state.quantidades = {sabor: 0 for sabor in SABORES_DISPONIVEIS}
            st.session_state.nome_input = ""
            st.session_state.clear_trigger += 1
            st.rerun()
    
    with col2:
        if st.button("💾 Salvar Retirada", type="primary", use_container_width=True):
            if not nome_pessoa:
                st.error("❌ Por favor, preencha o nome de quem retirou!")
            elif total_pizzas == 0:
                st.error("❌ Por favor, selecione pelo menos uma pizza!")
            else:
                # Criar lista de sabores com quantidade > 0
                sabores_validos = [
                    {'sabor': sabor, 'quantidade': qtd} 
                    for sabor, qtd in st.session_state.quantidades.items() 
                    if qtd > 0
                ]
                
                if add_retirada(dia_selecionado, nome_pessoa, sabores_validos, observacao):
                    st.success("✅ Retirada registrada com sucesso!")
                    # Limpar formulário
                    st.session_state.quantidades = {sabor: 0 for sabor in SABORES_DISPONIVEIS}
                    st.session_state.nome_input = ""
                    st.session_state.clear_trigger += 1
                    st.rerun()

# ABA 2: RELATÓRIO
with tab2:
    st.header("Relatório de Retiradas")
    
    data = load_data()
    
    if not data:
        st.info("📋 Nenhuma retirada registrada ainda.")
    else:
        # Filtro por dia da semana
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            dias_disponiveis = ["Todos"] + sorted(list(set([r['dia'] for r in data])))
            filtro_dia = st.selectbox("Filtrar por Dia da Semana", dias_disponiveis)
        
        with col2:
            # Filtro por nome
            nomes_disponiveis = ["Todos"] + sorted(list(set([r['nome'] for r in data])))
            filtro_nome = st.selectbox("Filtrar por Nome", nomes_disponiveis)
        
        # Aplicar filtros
        dados_filtrados = data
        
        if filtro_dia != "Todos":
            dados_filtrados = [r for r in dados_filtrados if r['dia'] == filtro_dia]
        
        if filtro_nome != "Todos":
            dados_filtrados = [r for r in dados_filtrados if r['nome'] == filtro_nome]
        
        # Ordenar por data mais recente
        dados_filtrados = sorted(dados_filtrados, key=lambda x: x['data_hora'], reverse=True)
        
        st.divider()
        
        # Estatísticas
        if dados_filtrados:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_retiradas = len(dados_filtrados)
                st.metric("Total de Retiradas", total_retiradas)
            
            with col2:
                total_pizzas = sum(r['total_pizzas'] for r in dados_filtrados)
                st.metric("Total de Pizzas", total_pizzas)
            
            with col3:
                pessoas_unicas = len(set([r['nome'] for r in dados_filtrados]))
                st.metric("Pessoas Diferentes", pessoas_unicas)
            
            st.divider()
            
            # Exibir retiradas
            for retirada in dados_filtrados:
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        st.subheader(f"{retirada['nome']} - {retirada['dia']}")
                        st.write(f"**Total de Pizzas retiradas:** {retirada['total_pizzas']}")
                        
                        sabores_texto = ", ".join([
                            f"{s['quantidade']} x {s['sabor']}" 
                            for s in retirada['sabores']
                        ])
                        st.write(f"**Sabores:** {sabores_texto}")
                        
                        # Mostrar observação se existir
                        if retirada.get('observacao'):
                            st.write(f"**Observação:** {retirada['observacao']}")
                        
                        st.caption(f"Registrado em: {retirada['data_hora']}")
                    
                    with col2:
                        if st.button("🗑️ Deletar", key=f"delete_{retirada['id']}"):
                            delete_retirada(retirada['id'])
                            st.rerun()
                    
                    st.divider()
            
            # Botão para exportar
            if st.button("📥 Exportar para CSV"):
                # Criar DataFrame para exportar
                export_data = []
                for r in dados_filtrados:
                    sabores_str = ", ".join([f"{s['quantidade']}x {s['sabor']}" for s in r['sabores']])
                    export_data.append({
                        'Nome': r['nome'],
                        'Dia': r['dia'],
                        'Total Pizzas': r['total_pizzas'],
                        'Sabores': sabores_str,
                        'Observação': r.get('observacao', ''),
                        'Data/Hora': r['data_hora']
                    })
                
                df = pd.DataFrame(export_data)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                
                st.download_button(
                    label="⬇️ Baixar CSV",
                    data=csv,
                    file_name=f"relatorio_pizzas_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Nenhuma retirada encontrada com os filtros selecionados.")

# ABA 3: BACKUP
with tab3:
    st.header("💾 Backup e Importação de Dados")
    
    st.write("Use esta seção para fazer backup dos seus dados ou restaurar de um backup anterior.")
    
    st.divider()
    
    # SEÇÃO DE BACKUP (DOWNLOAD)
    st.subheader("📥 Fazer Backup")
    st.write("Baixe o arquivo de dados para fazer backup em seu computador.")
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            json_data = f.read()
        
        data_atual = load_data()
        total_registros = len(data_atual)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"📊 **Total de registros no sistema:** {total_registros}")
        
        with col2:
            st.download_button(
                label="⬇️ Baixar Backup (JSON)",
                data=json_data,
                file_name=f"backup_pizzas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.warning("⚠️ Nenhum arquivo de dados encontrado. Registre algumas retiradas primeiro.")
    
    st.divider()
    
    # SEÇÃO DE IMPORTAÇÃO (UPLOAD)
    st.subheader("📤 Importar Backup")
    st.write("Restaure seus dados a partir de um arquivo de backup.")
    
    st.warning("⚠️ **ATENÇÃO:** Importar um backup irá **SUBSTITUIR** todos os dados atuais!")
    
    uploaded_file = st.file_uploader(
        "Escolha o arquivo de backup (JSON)",
        type=['json'],
        key="backup_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Ler o arquivo enviado
            imported_data = json.loads(uploaded_file.read().decode('utf-8'))
            
            # Validar estrutura básica
            if isinstance(imported_data, list):
                st.success(f"✅ Arquivo válido! Encontrados **{len(imported_data)}** registros.")
                
                # Mostrar preview dos dados
                with st.expander("👁️ Visualizar dados do backup"):
                    if len(imported_data) > 0:
                        for i, reg in enumerate(imported_data[:5]):  # Mostrar apenas os 5 primeiros
                            st.write(f"**{i+1}.** {reg.get('nome', 'N/A')} - {reg.get('dia', 'N/A')} - {reg.get('total_pizzas', 0)} pizzas")
                        if len(imported_data) > 5:
                            st.write(f"... e mais {len(imported_data) - 5} registros")
                    else:
                        st.write("Arquivo vazio (sem registros)")
                
                st.divider()
                
                # Confirmação para importar
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col2:
                    if st.button("🔄 CONFIRMAR IMPORTAÇÃO", type="primary", use_container_width=True):
                        # Fazer backup do arquivo atual antes de substituir
                        if os.path.exists(DATA_FILE):
                            backup_name = f"backup_automatico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                                backup_data = f.read()
                            # Salvar backup automático (opcional, mas seguro)
                            # com open(backup_name, 'w', encoding='utf-8') as f:
                            #     f.write(backup_data)
                        
                        # Salvar os dados importados
                        save_data(imported_data)
                        st.success("✅ **Dados importados com sucesso!**")
                        st.info("♻️ Recarregue a página para ver os dados atualizados.")
                        st.balloons()
            else:
                st.error("❌ Arquivo inválido! O backup deve conter uma lista de registros.")
        
        except json.JSONDecodeError:
            st.error("❌ Erro ao ler o arquivo! Certifique-se de que é um arquivo JSON válido.")
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
    
    st.divider()
    
    # SEÇÃO DE LIMPEZA DE DADOS
    st.subheader("🗑️ Limpar Todos os Dados")
    st.write("**CUIDADO:** Esta ação irá apagar **TODOS** os registros permanentemente!")
    
    if st.checkbox("🔓 Habilitar botão de limpeza"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ APAGAR TUDO", type="secondary", use_container_width=True):
                if os.path.exists(DATA_FILE):
                    # Fazer backup antes de apagar
                    backup_name = f"backup_antes_limpar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        backup_data = f.read()
                    st.download_button(
                        label="⬇️ Salvar backup antes de apagar",
                        data=backup_data,
                        file_name=backup_name,
                        mime="application/json"
                    )
                
                # Apagar dados
                save_data([])
                st.success("✅ Todos os dados foram apagados!")
                st.rerun()

# Rodapé
st.divider()
st.caption("🍕 Sistema de Controle de Pizzas - Desenvolvido com Streamlit")
