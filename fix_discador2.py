with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar a função inteira - desde o comentário até o fim
inicio_comentario = content.find('// Função para processar logs de filtrar_discador_e_salvar_no_banco')
if inicio_comentario == -1:
    print("Não encontrou o comentário!")
    exit(1)

# Encontrar o final da função - procurar pela próxima função ou flag
# Vamos procurar por "// Flag para controlar primeira carga" que vem depois
fim_marker = content.find('// Flag para controlar primeira carga', inicio_comentario)
if fim_marker == -1:
    print("Não encontrou o marcador de fim!")
    exit(1)

print(f"Início: {inicio_comentario}")
print(f"Fim: {fim_marker}")

# Remover tudo entre o início e o fim
antes = content[:inicio_comentario]
depois = content[fim_marker:]

# Ler nova função
with open('funcao_discador_nova.js', 'r', encoding='utf-8') as f:
    nova_funcao = f.read()

# Juntar tudo
novo_conteudo = antes + nova_funcao + '\n\n' + depois

# Salvar
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(novo_conteudo)

print("Arquivo corrigido!")

