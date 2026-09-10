import os
import sys
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from supabase_client import supabase

def limpar_cpf(cpf):
    if not cpf:
        return None
    return str(cpf).replace('.', '').replace('-', '').strip()

def converter_data(data_str):
    if not data_str or pd.isna(data_str):
        return None
    try:
        data = datetime.strptime(str(data_str).strip(), '%d/%m/%Y')
        return data.strftime('%Y-%m-%d')
    except:
        return None

def gerar_codigo(prefixo, texto):
    hash_obj = hashlib.md5(texto.encode())
    return f"{prefixo}_{hash_obj.hexdigest()[:10].upper()}"

print("=" * 60)
print("📥 IMPORTAÇÃO - EDITAL 2026.2")
print("=" * 60)

# 1. Verificar conexão
print("\n🔍 Testando conexão com Supabase...")
try:
    response = supabase.table('editais').select('*').execute()
    print(f"✅ Conexão OK. Editais encontrados: {len(response.data)}")
    if response.data:
        edital = response.data[0]
        print(f"✅ Edital: {edital['numero']} (ID: {edital['id']})")
    else:
        print("❌ Nenhum edital encontrado!")
        exit()
except Exception as e:
    print(f"❌ Erro na conexão: {e}")
    exit()

# 2. Verificar contagem atual
print("\n📊 Contagem atual no Supabase:")
resp = supabase.table('candidatos').select('*', count='exact').execute()
print(f"   Candidatos: {resp.count}")
resp = supabase.table('cursos').select('*', count='exact').execute()
print(f"   Cursos: {resp.count}")
resp = supabase.table('disciplinas').select('*', count='exact').execute()
print(f"   Disciplinas: {resp.count}")
resp = supabase.table('inscricoes').select('*', count='exact').execute()
print(f"   Inscrições: {resp.count}")

# 3. Ler CSV
print("\n📂 Lendo arquivo CSV...")
df = pd.read_csv('inscricoes_2026-2_CD.csv', encoding='latin1', delimiter=',')
print(f"📊 Total de registros no CSV: {len(df)}")

# 4. Processar
print("\n" + "=" * 60)
print("📝 Processando registros...")
print("=" * 60)

candidatos_criados = 0
cursos_criados = 0
disciplinas_criadas = 0
inscricoes_criadas = 0
erros = 0

for index, row in df.iterrows():
    try:
        if index % 50 == 0:
            print(f"🔄 {index+1}/{len(df)}...")
        
        # ✅ VERIFICAÇÃO DE LINHA INVÁLIDA (adicionada aqui)
        if pd.isna(row.get('Nome Civil')) or pd.isna(row.get('CPF')):
            continue
        
        # Candidato
        cpf = limpar_cpf(row.get('CPF'))
        if not cpf:
            continue
        
        resp = supabase.table('candidatos').select('*').eq('cpf', cpf).execute()
        if resp.data:
            candidato = resp.data[0]
        else:
            dados = {
                'nome_completo': row.get('Nome Civil', '').strip(),
                'cpf': cpf,
                'email': row.get('E-mail', '').strip(),
                'telefone': row.get('Telefone 1', '').strip(),
                'data_nascimento': converter_data(row.get('Data de Nascimento'))
            }
            resp = supabase.table('candidatos').insert(dados).execute()
            candidato = resp.data[0]
            candidatos_criados += 1
        
        # Curso
        curso_nome = row.get('Curso', '').strip()
        resp = supabase.table('cursos').select('*').eq('nome', curso_nome).execute()
        if resp.data:
            curso = resp.data[0]
        else:
            dados = {
                'nome': curso_nome,
                'codigo': gerar_codigo('CUR', curso_nome),
                'universidade': row.get('Universidade', '').strip()
            }
            resp = supabase.table('cursos').insert(dados).execute()
            curso = resp.data[0]
            cursos_criados += 1
        
        # Disciplina
        disciplina_nome = row.get('Disciplina', '').strip()
        resp = supabase.table('disciplinas').select('*').eq('nome', disciplina_nome).eq('curso_id', curso['id']).execute()
        if resp.data:
            disciplina = resp.data[0]
        else:
            dados = {
                'nome': disciplina_nome,
                'codigo': gerar_codigo('DISC', f"{curso['id']}_{disciplina_nome}"),
                'curso_id': curso['id']
            }
            resp = supabase.table('disciplinas').insert(dados).execute()
            disciplina = resp.data[0]
            disciplinas_criadas += 1
        
        # Inscrição
        opta_cotas = row.get('Cota', '').strip() != 'Nenhuma/Ampla Concorrência'
        resp = supabase.table('inscricoes')\
            .select('*')\
            .eq('candidato_id', candidato['id'])\
            .eq('edital_id', edital['id'])\
            .eq('disciplina_id', disciplina['id'])\
            .execute()
        
        if not resp.data:
            dados = {
                'candidato_id': candidato['id'],
                'edital_id': edital['id'],
                'disciplina_id': disciplina['id'],
                'status': 'pendente',
                'opta_cotas': opta_cotas
            }
            supabase.table('inscricoes').insert(dados).execute()
            inscricoes_criadas += 1
        
    except Exception as e:
        erros += 1
        if erros <= 5:
            print(f"  ❌ Erro {index}: {e}")

# 5. Resumo
print("\n" + "=" * 60)
print("📊 RESUMO FINAL")
print("=" * 60)
print(f"  👤 Candidatos criados: {candidatos_criados}")
print(f"  📚 Cursos criados: {cursos_criados}")
print(f"  📖 Disciplinas criadas: {disciplinas_criadas}")
print(f"  📝 Inscrições criadas: {inscricoes_criadas}")
print(f"  ❌ Erros: {erros}")
print("=" * 60)

# 6. Verificação final
print("\n📊 Verificação final no Supabase:")
resp = supabase.table('candidatos').select('*', count='exact').execute()
print(f"   Candidatos: {resp.count}")
resp = supabase.table('cursos').select('*', count='exact').execute()
print(f"   Cursos: {resp.count}")
resp = supabase.table('disciplinas').select('*', count='exact').execute()
print(f"   Disciplinas: {resp.count}")
resp = supabase.table('inscricoes').select('*', count='exact').execute()
print(f"   Inscrições: {resp.count}")