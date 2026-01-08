with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar início e fim da função processarLogsDiscador
inicio = None
fim = None
nivel_chaves = 0

for i, line in enumerate(lines):
    if '// Função para processar logs de filtrar_discador_e_salvar_no_banco' in line:
        inicio = i
        continue
    
    if inicio is not None:
        # Contar chaves abertas e fechadas
        nivel_chaves += line.count('{') - line.count('}')
        
        # Se encontramos o fechamento da função (nível volta a 0 após abrir)
        if 'function processarLogsDiscador' in lines[inicio+1] and nivel_chaves == 0 and i > inicio + 1:
            fim = i + 1
            break

print(f"Função encontrada: linhas {inicio+1} a {fim+1}")
print(f"Total de linhas a substituir: {fim - inicio}")

# Ler nova função
with open('funcao_discador_nova.js', 'r', encoding='utf-8') as f:
    nova_funcao = f.readlines()

# Substituir
novas_linhas = lines[:inicio] + nova_funcao + lines[fim:]

# Salvar
with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(novas_linhas)

print("Arquivo atualizado com sucesso!")

