/* ============================================================
   CECIERJ - Tela de Convocações
   ============================================================ */

// Estado da aplicação
const estado = {
    grupos: [],
    grupoSelecionado: null,
    funcaoSelecionada: 'Coordenador de Disciplina',
    cr: null,
    proxima: null,
    kpis: null,
    carregando: false,
};

// ============================================================
// INICIALIZAÇÃO
// ============================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('📋 Iniciando tela de convocações...');
    await carregarGrupos();
});

// ============================================================
// CARREGAR GRUPOS
// ============================================================

async function carregarGrupos() {
    try {
        // Por enquanto, grupos mockados
        // TODO: Criar endpoint /api/grupos/
        estado.grupos = [
            { id: 1, nome: 'Sociologia da Educação', curso: '2026.2 Licenciatura em Pedagogia' },
            { id: 2, nome: 'Estágio em Gestão', curso: '2026.2 Licenciatura em Pedagogia' },
        ];
        
        preencherSelectGrupos();
        
        // Selecionar o primeiro grupo automaticamente
        if (estado.grupos.length > 0) {
            estado.grupoSelecionado = estado.grupos[0].id;
            document.getElementById('filtro-grupo').value = estado.grupoSelecionado;
            await carregarCR();
        }
    } catch (error) {
        console.error('Erro ao carregar grupos:', error);
        mostrarMensagem('erro', 'Erro ao carregar grupos');
    }
}

function preencherSelectGrupos() {
    const select = document.getElementById('filtro-grupo');
    select.innerHTML = '<option value="">Selecione um grupo...</option>';
    
    estado.grupos.forEach(grupo => {
        const option = document.createElement('option');
        option.value = grupo.id;
        option.textContent = `${grupo.nome} (${grupo.curso})`;
        select.appendChild(option);
    });
}

// ============================================================
// CARREGAR CR
// ============================================================

async function carregarCR() {
    if (!estado.grupoSelecionado) {
        mostrarMensagem('erro', 'Selecione um grupo');
        return;
    }
    
    estado.carregando = true;
    mostrarLoading();
    
    // ✅ LIMPAR MENSAGEM DE ERRO ANTES DE COMEÇAR
    document.getElementById('mensagem').className = 'mensagem';
    
    try {
        // Buscar CR
        console.log('🔍 Buscando CR...');
        const crResponse = await apiListarCR(estado.grupoSelecionado, estado.funcaoSelecionada);
        estado.cr = crResponse.data;
        console.log('✅ CR carregado:', estado.cr);
        
        // Buscar próxima convocação
        console.log('🔍 Buscando próxima convocação...');
        const proximaResponse = await apiProximaConvocacao(estado.grupoSelecionado, estado.funcaoSelecionada);
        estado.proxima = proximaResponse.data;
        console.log('✅ Próxima convocação carregada:', estado.proxima);
        
        // Buscar KPIs
        console.log('🔍 Buscando KPIs...');
        const kpisResponse = await apiKPIs();
        estado.kpis = kpisResponse.data;
        console.log('✅ KPIs carregados:', estado.kpis);
        
        // Renderizar
        renderizarKPIs();
        renderizarAvisoProxima();
        renderizarTabelaCG();
        renderizarTabelaRV();
        
        esconderLoading();
        
    } catch (error) {
        console.error('❌ Erro ao carregar CR:', error);
        mostrarMensagem('erro', `Erro: ${error.message}`);
        esconderLoading();
    } finally {
        estado.carregando = false;
    }
}

// ============================================================
// RENDERIZAR KPIs
// ============================================================

function renderizarKPIs() {
    if (!estado.kpis) return;
    
    document.getElementById('kpi-total').textContent = estado.kpis.total || 0;
    document.getElementById('kpi-convocados').textContent = estado.kpis.convocados || 0;
    document.getElementById('kpi-aguardando').textContent = estado.kpis.aguardando || 0;
    document.getElementById('kpi-expirados').textContent = estado.kpis.expirados || 0;
    document.getElementById('kpi-recusou').textContent = estado.kpis.recusou || 0;
}

// ============================================================
// RENDERIZAR AVISO DE PRÓXIMA CONVOCAÇÃO
// ============================================================

function renderizarAvisoProxima() {
    const container = document.getElementById('aviso-proxima');
    
    if (!container) return;
    
    if (!estado.proxima) {
        container.style.display = 'none';
        return;
    }
    
    const { tipo_proxima, proximo_candidato, aviso, posicao_no_ciclo, total_convocacoes } = estado.proxima;
    
    if (!tipo_proxima) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'flex';
    container.className = `aviso-proxima ${tipo_proxima.toLowerCase()}`;
    
    const icone = tipo_proxima === 'RV' ? '⚠️' : '✅';
    const titulo = tipo_proxima === 'RV' 
        ? 'Próxima convocação: COTA (RV)' 
        : 'Próxima convocação: AMPLA CONCORRÊNCIA (CG)';
    
    const subtitulo = proximo_candidato 
        ? `${proximo_candidato.nome_completo} - Nota: ${proximo_candidato.nota_final}`
        : 'Nenhum candidato disponível';
    
    container.innerHTML = `
        <span class="icone">${icone}</span>
        <div class="texto">
            <div class="titulo">${titulo}</div>
            <div class="subtitulo">${subtitulo}</div>
        </div>
        <div style="text-align: right; font-size: 12px;">
            <div>Ciclo: ${posicao_no_ciclo}/4</div>
            <div>Total: ${total_convocacoes} convocações</div>
        </div>
    `;
}

// ============================================================
// RENDERIZAR TABELA CG
// ============================================================

function renderizarTabelaCG() {
    const tbody = document.getElementById('tbody-cg');
    
    if (!tbody) return;
    
    if (!estado.cr || !estado.cr.cg || estado.cr.cg.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center" style="padding: 40px; color: #6B7280;">
                    Nenhum candidato de ampla concorrência
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = estado.cr.cg.map((candidato, index) => {
        const posicao = candidato.posicao_cg || index + 1;
        const badgeStatus = getBadgeStatus(candidato.status_cr);
        const badgeTipo = '<span class="badge badge-cg">CG</span>';
        
        return `
            <tr>
                <td><span class="posicao">${posicao}º</span></td>
                <td><span class="candidato">${candidato.nome_completo}</span></td>
                <td>${candidato.cpf}</td>
                <td><span class="nota">${candidato.nota_final}</span></td>
                <td>${badgeTipo}</td>
                <td>${badgeStatus}</td>
                <td>
                    ${candidato.status_cr === 'aguardando' 
                        ? `<button class="btn btn-primario" onclick="abrirModalConvocar(${candidato.avaliacao_id}, '${candidato.nome_completo.replace(/'/g, "\\'")}')">
                            🎯 Convocar
                           </button>`
                        : `<span style="color: #9CA3AF; font-size: 12px;">${candidato.data_convocacao || 'Convocado'}</span>`
                    }
                </td>
            </tr>
        `;
    }).join('');
}

// ============================================================
// RENDERIZAR TABELA RV
// ============================================================

function renderizarTabelaRV() {
    const tbody = document.getElementById('tbody-rv');
    
    if (!tbody) return;
    
    if (!estado.cr || !estado.cr.rv || estado.cr.rv.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center" style="padding: 40px; color: #6B7280;">
                    Nenhum candidato de reserva de vaga
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = estado.cr.rv.map((candidato, index) => {
        const posicao = candidato.posicao_rv || index + 1;
        const badgeStatus = getBadgeStatus(candidato.status_cr);
        const badgeTipo = '<span class="badge badge-rv">RV</span>';
        
        return `
            <tr>
                <td><span class="posicao">${posicao}º</span></td>
                <td><span class="candidato">${candidato.nome_completo}</span></td>
                <td>${candidato.cpf}</td>
                <td><span class="nota">${candidato.nota_final}</span></td>
                <td>${badgeTipo}</td>
                <td>${badgeStatus}</td>
                <td>
                    ${candidato.status_cr === 'aguardando' 
                        ? `<button class="btn btn-primario" onclick="abrirModalConvocar(${candidato.avaliacao_id}, '${candidato.nome_completo.replace(/'/g, "\\'")}')">
                            🎯 Convocar
                           </button>`
                        : `<span style="color: #9CA3AF; font-size: 12px;">${candidato.data_convocacao || 'Convocado'}</span>`
                    }
                </td>
            </tr>
        `;
    }).join('');
}

// ============================================================
// HELPERS
// ============================================================

function getBadgeStatus(status) {
    const badges = {
        'convocado': '<span class="badge badge-convocado">✅ Convocado</span>',
        'aguardando': '<span class="badge badge-aguardando">⏳ Aguardando</span>',
        'recusou': '<span class="badge badge-recusou">❌ Recusou</span>',
        'expirado': '<span class="badge badge-expirado">⚠️ Expirado</span>',
    };
    return badges[status] || status;
}

function mostrarLoading() {
    const loading = document.getElementById('loading');
    const conteudo = document.getElementById('conteudo');
    if (loading) loading.style.display = 'block';
    if (conteudo) conteudo.style.display = 'none';
}

function esconderLoading() {
    const loading = document.getElementById('loading');
    const conteudo = document.getElementById('conteudo');
    if (loading) loading.style.display = 'none';
    if (conteudo) conteudo.style.display = 'block';
}

function mostrarMensagem(tipo, texto) {
    const container = document.getElementById('mensagem');
    if (!container) return;
    
    container.className = `mensagem ${tipo}`;
    container.textContent = texto;
    
    setTimeout(() => {
        container.className = 'mensagem';
    }, 5000);
}

// ============================================================
// MODAL DE CONVOCAÇÃO
// ============================================================

let avaliacaoIdAtual = null;

function abrirModalConvocar(avaliacaoId, nomeCandidato) {
    avaliacaoIdAtual = avaliacaoId;
    
    const modal = document.getElementById('modal-convocar');
    if (!modal) return;
    
    document.getElementById('modal-candidato-nome').textContent = nomeCandidato;
    document.getElementById('modal-data-convocacao').value = '';
    document.getElementById('modal-observacoes').value = '';
    
    modal.style.display = 'flex';
}

function fecharModalConvocar() {
    const modal = document.getElementById('modal-convocar');
    if (modal) modal.style.display = 'none';
    avaliacaoIdAtual = null;
}

async function confirmarConvocacao() {
    const dataConvocacao = document.getElementById('modal-data-convocacao').value;
    const observacoes = document.getElementById('modal-observacoes').value;
    
    if (!dataConvocacao) {
        alert('Por favor, informe a data de convocação');
        return;
    }
    
    try {
        await apiConvocar(avaliacaoIdAtual, dataConvocacao, observacoes);
        mostrarMensagem('sucesso', 'Candidato convocado com sucesso!');
        fecharModalConvocar();
        await carregarCR();
    } catch (error) {
        console.error('Erro ao convocar:', error);
        mostrarMensagem('erro', 'Erro ao convocar candidato');
    }
}

// ============================================================
// RECALCULAR CLASSIFICAÇÃO
// ============================================================

async function recalcularClassificacao() {
    if (!confirm('Deseja recalcular a classificação deste grupo?')) {
        return;
    }
    
    try {
        await apiRecalcularClassificacao(estado.grupoSelecionado, estado.funcaoSelecionada);
        mostrarMensagem('sucesso', 'Classificação recalculada com sucesso!');
        await carregarCR();
    } catch (error) {
        console.error('Erro ao recalcular:', error);
        mostrarMensagem('erro', 'Erro ao recalcular classificação');
    }
}

// ============================================================
// HANDLERS DE FILTROS
// ============================================================

function onGrupoChange() {
    const select = document.getElementById('filtro-grupo');
    estado.grupoSelecionado = parseInt(select.value) || null;
    
    if (estado.grupoSelecionado) {
        carregarCR();
    }
}

function onFuncaoChange() {
    const select = document.getElementById('filtro-funcao');
    estado.funcaoSelecionada = select.value;
    
    if (estado.grupoSelecionado) {
        carregarCR();
    }
}