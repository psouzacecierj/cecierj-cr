/* ============================================================
   CECIERJ - Chamadas à API
   ============================================================ */

const API_BASE = '/api';

/**
 * Função genérica para chamadas à API
 */
async function chamarAPI(endpoint, opcoes = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    const config = {
        headers: {
            'Content-Type': 'application/json',
        },
        ...opcoes,
    };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `Erro ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error(`Erro em ${endpoint}:`, error);
        throw error;
    }
}

// ============================================================
// CONVOCAÇÕES
// ============================================================

/**
 * Lista o CR de um grupo/função
 */
async function apiListarCR(grupoId, funcao) {
    const params = new URLSearchParams({ funcao });
    return chamarAPI(`/convocacoes/cr/grupo/${grupoId}/?${params}`);
}

/**
 * Retorna a próxima convocação
 */
async function apiProximaConvocacao(grupoId, funcao) {
    const params = new URLSearchParams({ funcao });
    return chamarAPI(`/convocacoes/cr/grupo/${grupoId}/proxima/?${params}`);
}

/**
 * Convoca um candidato
 */
async function apiConvocar(avaliacaoId, dataConvocacao, observacoes = '') {
    return chamarAPI(`/convocacoes/cr/convocar/${avaliacaoId}/`, {
        method: 'POST',
        body: JSON.stringify({
            data_convocacao: dataConvocacao,
            observacoes: observacoes,
        }),
    });
}

/**
 * Registra recusa
 */
async function apiRegistrarRecusa(avaliacaoId, motivo = '') {
    return chamarAPI(`/convocacoes/cr/recusar/${avaliacaoId}/`, {
        method: 'POST',
        body: JSON.stringify({ motivo }),
    });
}

/**
 * Atualiza status
 */
async function apiAtualizarStatus(avaliacaoId, dados) {
    return chamarAPI(`/convocacoes/cr/atualizar/${avaliacaoId}/`, {
        method: 'PATCH',
        body: JSON.stringify(dados),
    });
}

/**
 * KPIs do CR
 */
async function apiKPIs(editalId = null) {
    const params = editalId ? `?edital_id=${editalId}` : '';
    return chamarAPI(`/convocacoes/cr/kpis/${params}`);
}

// ============================================================
// RESULTADOS
// ============================================================

/**
 * Resultado de um grupo
 */
async function apiResultadoGrupo(grupoId, funcao) {
    const params = new URLSearchParams({ funcao });
    return chamarAPI(`/avaliacoes/resultado/grupo/${grupoId}/?${params}`);
}

/**
 * Resultado geral
 */
async function apiResultadoGeral() {
    return chamarAPI('/avaliacoes/resultado/geral/');
}

/**
 * Recálcula classificação
 */
async function apiRecalcularClassificacao(grupoId, funcao) {
    return chamarAPI(`/avaliacoes/recalcular-classificacao/${grupoId}/`, {
        method: 'POST',
        body: JSON.stringify({ funcao }),
    });
}

// ============================================================
// GRUPOS
// ============================================================

/**
 * Lista grupos de um curso
 * (Endpoint ainda precisa ser criado)
 */
async function apiListarGrupos(cursoId = null) {
    const params = cursoId ? `?curso_id=${cursoId}` : '';
    return chamarAPI(`/grupos/${params}`);
}