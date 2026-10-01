from supabase_client import supabase
from typing import Dict, List, Optional


class GrupoService:
    """
    Serviço para gerenciar grupos de disciplinas do processo seletivo.
    
    Estrutura:
    - Cada grupo pertence a 1 curso e a 1 edital
    - Cada grupo tem um número explícito (1, 2, 3...) dentro do edital
    - Cada grupo pode ter 1+ disciplinas vinculadas via grupo_disciplinas
    - As avaliações de candidatos são atreladas ao grupo (avaliacoes.grupo_id)
    """

    @classmethod
    def listar_grupos(cls, edital_id: Optional[int] = None,
                      curso_id: Optional[int] = None) -> List[Dict]:
        """
        Lista grupos, opcionalmente filtrando por edital e/ou curso.
        
        Retorna cada grupo com:
        - id, numero, nome
        - curso (id, nome)
        - edital (id, numero, semestre) — se houver
        - disciplinas: lista de disciplinas vinculadas
        """
        try:
            # ── 1. Query base de grupos ─────────────────────────
            query = supabase.table('grupos')\
                .select('id, numero, nome, curso_id, edital_id, created_at')

            if edital_id:
                query = query.eq('edital_id', edital_id)
            if curso_id:
                query = query.eq('curso_id', curso_id)

            response = query.order('numero').execute()

            if not response.data:
                return []

            grupos = response.data

            # ── 2. Coletar IDs para JOINS ───────────────────────
            grupo_ids = [g['id'] for g in grupos]
            curso_ids = list({g['curso_id'] for g in grupos if g.get('curso_id')})
            edital_ids = list({g['edital_id'] for g in grupos if g.get('edital_id')})

            # ── 3. Buscar cursos ────────────────────────────────
            cursos_map = {}
            if curso_ids:
                cursos_resp = supabase.table('cursos')\
                    .select('id, nome, codigo, modalidade')\
                    .in_('id', curso_ids)\
                    .execute()
                cursos_map = {c['id']: c for c in cursos_resp.data}

            # ── 4. Buscar editais ───────────────────────────────
            editais_map = {}
            if edital_ids:
                editais_resp = supabase.table('editais')\
                    .select('id, numero, semestre, ano')\
                    .in_('id', edital_ids)\
                    .execute()
                editais_map = {e['id']: e for e in editais_resp.data}

            # ── 5. Buscar disciplinas dos grupos ────────────────
            gd_resp = supabase.table('grupo_disciplinas')\
                .select('grupo_id, disciplina_id')\
                .in_('grupo_id', grupo_ids)\
                .execute()

            disciplinas_por_grupo = {}
            disciplina_ids_set = set()

            for gd in gd_resp.data:
                gid = gd['grupo_id']
                did = gd['disciplina_id']
                disciplinas_por_grupo.setdefault(gid, []).append(did)
                disciplina_ids_set.add(did)

            # ── 6. Buscar dados das disciplinas ─────────────────
            disciplinas_map = {}
            if disciplina_ids_set:
                disc_resp = supabase.table('disciplinas')\
                    .select('id, nome, codigo, curso_id, vagas')\
                    .in_('id', list(disciplina_ids_set))\
                    .execute()
                disciplinas_map = {d['id']: d for d in disc_resp.data}

            # ── 7. Montar resposta ──────────────────────────────
            resultado = []
            for g in grupos:
                gid = g['id']
                disc_ids = disciplinas_por_grupo.get(gid, [])
                disciplinas = [disciplinas_map[did] for did in disc_ids if did in disciplinas_map]

                resultado.append({
                    'id': g['id'],
                    'numero': g.get('numero'),
                    'nome': g['nome'],
                    'curso': cursos_map.get(g.get('curso_id')),
                    'edital': editais_map.get(g.get('edital_id')),
                    'disciplinas': disciplinas,
                })

            return resultado

        except Exception as e:
            print(f"❌ Erro em listar_grupos: {e}")
            return []

    @classmethod
    def obter_grupo(cls, grupo_id: int) -> Optional[Dict]:
        """Retorna um grupo específico com todas as suas disciplinas."""
        try:
            response = supabase.table('grupos')\
                .select('id, numero, nome, curso_id, edital_id, created_at')\
                .eq('id', grupo_id)\
                .execute()

            if not response.data:
                return None

            g = response.data[0]

            # Curso
            curso = None
            if g.get('curso_id'):
                c = supabase.table('cursos')\
                    .select('id, nome, codigo, modalidade')\
                    .eq('id', g['curso_id'])\
                    .execute()
                curso = c.data[0] if c.data else None

            # Edital
            edital = None
            if g.get('edital_id'):
                e = supabase.table('editais')\
                    .select('id, numero, semestre, ano')\
                    .eq('id', g['edital_id'])\
                    .execute()
                edital = e.data[0] if e.data else None

            # Disciplinas
            gd = supabase.table('grupo_disciplinas')\
                .select('disciplina_id')\
                .eq('grupo_id', grupo_id)\
                .execute()

            disc_ids = [x['disciplina_id'] for x in gd.data]

            disciplinas = []
            if disc_ids:
                d = supabase.table('disciplinas')\
                    .select('id, nome, codigo, curso_id, vagas')\
                    .in_('id', disc_ids)\
                    .execute()
                disciplinas = d.data

            return {
                'id': g['id'],
                'numero': g.get('numero'),
                'nome': g['nome'],
                'curso': curso,
                'edital': edital,
                'disciplinas': disciplinas,
            }
        except Exception as e:
            print(f"❌ Erro em obter_grupo: {e}")
            return None