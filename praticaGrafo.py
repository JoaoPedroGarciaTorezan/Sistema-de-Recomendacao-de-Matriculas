import networkx as nx
import matplotlib.pyplot as plt

from ModelGrafo import Disciplina



# ======================================================
# CRIAÇÃO DAS DISCIPLINAS
# ======================================================

disciplinas = {}


def criar_disciplina(codigo, nome, carga=64):

    disciplina = Disciplina(
        codigo,
        nome,
        carga
    )

    disciplinas[codigo] = disciplina

    return disciplina



# ===== 1º SEMESTRE =====

mata01 = criar_disciplina(
    "MATA01",
    "Cálculo A"
)

xmac01 = criar_disciplina(
    "XMCA01",
    "Matemática Discreta"
)

xdes01 = criar_disciplina(
    "XDES01",
    "Fundamentos de Programação"
)

crsc03 = criar_disciplina(
    "CRSC03",
    "Arquitetura de Computadores I"
)



# ===== 2º SEMESTRE =====

mata02 = criar_disciplina(
    "MATA02",
    "Cálculo B"
)

cmac04 = criar_disciplina(
    "CMAC04",
    "Modelagem Computacional"
)

ctc001 = criar_disciplina(
    "CTC001",
    "Algoritmos e Estruturas de Dados I"
)

crsc04 = criar_disciplina(
    "CRSC04",
    "Arquitetura de Computadores II"
)



# ===== 3º SEMESTRE =====

ctc002 = criar_disciplina(
    "CTC002",
    "Algoritmos e Estruturas de Dados II"
)

xdes02 = criar_disciplina(
    "XDES02",
    "Programação Orientada a Objetos"
)

crsc02 = criar_disciplina(
    "CRSC02",
    "Sistemas Operacionais"
)


ctc004 = criar_disciplina(
    "CTC004",
    "Projeto e Análise de Algoritmos"
)

xdes03 = criar_disciplina(
    "XDES03",
    "Programação Web"
)


# ===== 4º SEMESTRE =====

xahc02 = criar_disciplina(
    "XAHC02",
    "Interação Humano-Computador"
)

xcsc01 = criar_disciplina(
    "XCSC01",
    "Redes de Computadores"
)


# ===== 5º SEMESTRE =====

ctc005 = criar_disciplina(
    "CTC005",
    "Teoria da Computação"
)

ctc006 = criar_disciplina(
    "CTC006",
    "Compiladores"
)

xpad01 = criar_disciplina(
    "XPAD01",
    "Banco de Dados I"
)

xmco01 = criar_disciplina(
    "XMCO01",
    "Inteligência Artificial"
)



# ===== 6º/7º =====

xahc03 = criar_disciplina(
    "XAHC03",
    "Metodologia Científica"
)

tcc1 = criar_disciplina(
    "TCC1",
    "Trabalho de Conclusão de Curso 1",
    140
)

tcc2 = criar_disciplina(
    "TCC2",
    "Trabalho de Conclusão de Curso 2",
    210
)



# ======================================================
# DEFINIÇÃO DOS PRÉ-REQUISITOS
# ======================================================


mata02.adicionar_pre_requisito(mata01)

cmac04.adicionar_pre_requisito(mata01)


cmac03 = criar_disciplina(
    "CMAC03",
    "Algoritmos em Grafos"
)

cmac03.adicionar_pre_requisito(xmac01)


ctc001.adicionar_pre_requisito(xdes01)

crsc04.adicionar_pre_requisito(crsc03)



ctc002.adicionar_pre_requisito(ctc001)

xdes02.adicionar_pre_requisito(ctc001)

crsc02.adicionar_pre_requisito(crsc04)



ctc004.adicionar_pre_requisito(ctc002)

xdes03.adicionar_pre_requisito(xdes02)


xahc02.adicionar_pre_requisito(xdes03)


xcsc01.adicionar_pre_requisito(crsc02)



ctc005.adicionar_pre_requisito(ctc004)

ctc006.adicionar_pre_requisito(ctc005)



tcc1.adicionar_pre_requisito(ctc006)

xahc03.adicionar_pre_requisito(xahc02)


tcc2.adicionar_pre_requisito(tcc1)



# ======================================================
# CRIAÇÃO DO GRAFO NETWORKX
# ======================================================


grafo = nx.DiGraph()


for disciplina in disciplinas.values():

    grafo.add_node(
        disciplina
    )


for disciplina in disciplinas.values():

    for requisito in disciplina.pre_requisitos:

        grafo.add_edge(
            requisito,
            disciplina
        )



# ======================================================
# ENTRADA DO HISTÓRICO DO ALUNO
# ======================================================


historico = {

    "XDES01": "CONCLUIDA",

    "XMCA01": "CONCLUIDA",

    "XDES04": "CONCLUIDA",

    "CTC001": "REPROVADA"

}



# ======================================================
# ATUALIZAR ESTADO DAS DISCIPLINAS
# ======================================================


for disciplina in disciplinas.values():

    if disciplina.codigo in historico:

        disciplina.estado = historico[disciplina.codigo]



# ======================================================
# BUSCAR DISCIPLINAS DISPONÍVEIS
# ======================================================


def buscar_disponiveis():

    resultado = []


    for disciplina in disciplinas.values():


        if disciplina.estado != "NAO_CURSADA":
            continue


        pode_cursar = True


        for requisito in disciplina.pre_requisitos:

            if requisito.estado != "CONCLUIDA":

                pode_cursar = False



        if pode_cursar:

            disciplina.estado = "DISPONIVEL"

            resultado.append(disciplina)


    return resultado



disponiveis = buscar_disponiveis()



print("\nDisciplinas disponíveis:")

for disciplina in disponiveis:

    print(
        disciplina
    )



# ======================================================
# ORDENAÇÃO TOPOLÓGICA
# ======================================================


print("\nOrdem topológica:")

ordem = nx.topological_sort(grafo)


for disciplina in ordem:

    print(
        f"{disciplina.codigo} - {disciplina.nome}"
    )



# ======================================================
# VISUALIZAÇÃO DO GRAFO
# ======================================================


plt.figure(figsize=(12,8))


pos = nx.spring_layout(grafo)


labels = {

    disciplina: disciplina.nome

    for disciplina in grafo.nodes

}


nx.draw(
    grafo,
    pos,
    labels=labels,
    with_labels=True,
    node_size=2500,
    font_size=8
)


plt.show()