"""
gerar_grafo.py
==============
Etapa de visualização do pipeline de recomendação de matrícula.

Gera um PNG do grafo de pré-requisitos do currículo, em camadas por período,
colorindo cada disciplina conforme o estado do aluno:

    CONCLUIDA   → já aprovada (situação 'APR' ou 'CUMP' no histórico)
    REPROVADA   → reprovada e ainda não aprovada em nenhuma tentativa posterior
    DISPONIVEL  → liberada para matrícula no semestre informado (saída do
                  filtro_disciplinas)
    NAO_CURSADA → ainda bloqueada por pré-requisito não satisfeito

As disciplinas selecionadas pelo MWIS (resultado final da recomendação)
recebem um contorno dourado para se destacarem das demais disponíveis.

Uso como módulo:
    from gerar_grafo import gerar_grafo_curriculo
    gerar_grafo_curriculo(
        dag=dag,
        aluno=aluno,
        df_historico=df_historico,
        candidatas=candidatas,
        resultado=resultado,
        nome_curso=nome_curso,
        semestre=semestre,
        caminho_saida="grafo_CCO_2025.1.png",
    )
"""

from __future__ import annotations

from collections import defaultdict
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # backend não interativo — necessário em scripts/pipelines
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import networkx as nx
import pandas as pd

from dag_cco import DAG
from read_historico import HistoricoAluno
from filtro_disciplinas import DisciplinaDisponivel


# ---------------------------------------------------------------------------
# Cores por estado
# ---------------------------------------------------------------------------

_COR_ESTADO = {
    "CONCLUIDA":   "#4CAF50",
    "REPROVADA":   "#F44336",
    "DISPONIVEL":  "#2196F3",
    "NAO_CURSADA": "#B0BEC5",
}

_COR_CONTORNO_PADRAO    = "#37474F"
_COR_CONTORNO_SELECIONADA = "#FFC107"


# ---------------------------------------------------------------------------
# Classificação de estado
# ---------------------------------------------------------------------------

def _classificar_estados(
    dag: DAG,
    aluno: HistoricoAluno,
    df_historico: Optional[pd.DataFrame],
    candidatas: list[DisciplinaDisponivel],
) -> dict[str, str]:
    """
    Retorna { codigo → estado } para todos os vértices do DAG.
    """
    aprovadas = aluno.aprovadas
    codigos_disponiveis = {d.codigo for d in candidatas}

    # Reprovadas: aparecem no histórico com situação iniciada por 'REP' e
    # que NÃO constam entre as aprovadas (cobre o caso de reprovar e depois
    # passar em uma segunda tentativa, que não deve marcar REPROVADA).
    reprovadas: set[str] = set()
    if df_historico is not None and not df_historico.empty and "situacao" in df_historico.columns:
        mask_rep = df_historico["situacao"].astype(str).str.startswith("REP")
        reprovadas = set(
            df_historico.loc[mask_rep, "codigo"].astype(str).str.strip()
        ) - aprovadas

    estados: dict[str, str] = {}
    for codigo in dag.vertices:
        if codigo in aprovadas:
            estados[codigo] = "CONCLUIDA"
        elif codigo in codigos_disponiveis:
            estados[codigo] = "DISPONIVEL"
        elif codigo in reprovadas:
            estados[codigo] = "REPROVADA"
        else:
            estados[codigo] = "NAO_CURSADA"

    return estados


# ---------------------------------------------------------------------------
# Layout em camadas por período da grade
# ---------------------------------------------------------------------------

def _layout_por_periodo(dag: DAG) -> tuple[dict[str, tuple[float, float]], dict[int, list[str]]]:
    """
    Posiciona cada disciplina em (x, y), onde x = período sugerido na grade
    (campo `periodo` de Disciplina) e y distribui as disciplinas do mesmo
    período verticalmente, centradas em torno de 0.

    Retorna (pos, por_periodo) — por_periodo é usado depois para desenhar os
    rótulos "1º Período", "2º Período", etc.
    """
    por_periodo: dict[int, list[str]] = defaultdict(list)
    for codigo, disc in dag.vertices.items():
        por_periodo[disc.periodo].append(codigo)

    pos: dict[str, tuple[float, float]] = {}
    for periodo, codigos in por_periodo.items():
        codigos_ordenados = sorted(codigos)
        n = len(codigos_ordenados)
        for i, codigo in enumerate(codigos_ordenados):
            x = periodo - 1
            y = (n - 1) / 2 - i
            pos[codigo] = (float(x), float(y))

    return pos, dict(sorted(por_periodo.items()))


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def gerar_grafo_curriculo(
    dag: DAG,
    aluno: HistoricoAluno,
    df_historico: Optional[pd.DataFrame],
    candidatas: list[DisciplinaDisponivel],
    resultado,  # ResultadoMWIS — não importado diretamente para evitar import circular com mwis.py
    nome_curso: str,
    semestre: str,
    caminho_saida: str,
) -> str:
    """
    Gera e salva o PNG do grafo de pré-requisitos com o estado do aluno.

    Parâmetros
    ----------
    dag            : DAG construído por dag_cco.construir_dag
    aluno          : HistoricoAluno (read_historico.processar_historico)
    df_historico   : DataFrame bruto do histórico (parse_historico), usado
                     apenas para identificar disciplinas reprovadas. Pode
                     ser None — nesse caso REPROVADA nunca é atribuída.
    candidatas     : lista de DisciplinaDisponivel (filtro_disciplinas)
    resultado      : ResultadoMWIS (mwis.resolver_mwis) — usado para destacar
                     com contorno dourado as disciplinas selecionadas
    nome_curso     : nome completo do curso, usado no título
    semestre       : semestre consultado (ex: '2025.1'), usado no título
    caminho_saida  : caminho do arquivo .png a ser salvo

    Retorno
    -------
    O próprio `caminho_saida`, para facilitar o encadeamento no pipeline.
    """

    # ── 1. Monta o grafo networkx a partir do DAG já construído ──────────────
    G = nx.DiGraph()
    G.add_nodes_from(dag.vertices.keys())
    for origem, destinos in dag.adj.items():
        for destino in destinos:
            G.add_edge(origem, destino)

    # ── 2. Estado de cada disciplina + destaque de seleção ───────────────────
    estados = _classificar_estados(dag, aluno, df_historico, candidatas)
    codigos_selecionados = (
        {d.codigo for d in resultado.selecionadas} if resultado is not None else set()
    )

    node_colors:     list[str] = []
    node_edgecolors: list[str] = []
    node_linewidths: list[float] = []
    for codigo in G.nodes:
        node_colors.append(_COR_ESTADO[estados.get(codigo, "NAO_CURSADA")])
        if codigo in codigos_selecionados:
            node_edgecolors.append(_COR_CONTORNO_SELECIONADA)
            node_linewidths.append(3.5)
        else:
            node_edgecolors.append(_COR_CONTORNO_PADRAO)
            node_linewidths.append(1.0)

    # ── 3. Layout em camadas ──────────────────────────────────────────────────
    pos, por_periodo = _layout_por_periodo(dag)

    # ── 4. Plot ────────────────────────────────────────────────────────────────
    largura = max(20, 2.6 * len(por_periodo))
    plt.figure(figsize=(largura, 11))

    labels = {c: f"{c}\n{dag.vertices[c].nome}" for c in G.nodes}

    nx.draw(
        G, pos,
        labels=labels,
        with_labels=True,
        node_size=3600,
        node_color=node_colors,
        edgecolors=node_edgecolors,
        linewidths=node_linewidths,
        font_size=6.5,
        font_weight="bold",
        arrows=True,
        arrowsize=14,
        edge_color="#90A4AE",
        width=1.2,
    )

    ax = plt.gca()
    max_n = max((len(v) for v in por_periodo.values()), default=1)
    for periodo in por_periodo:
        ax.text(
            periodo - 1, max_n / 2 + 0.8,
            f"{periodo}º Período",
            ha="center", va="bottom", fontsize=13, fontweight="bold", color="#37474F",
        )

    legenda = [Patch(facecolor=c, label=s) for s, c in _COR_ESTADO.items()]
    legenda.append(
        Patch(
            facecolor="white", edgecolor=_COR_CONTORNO_SELECIONADA, linewidth=3,
            label="SELECIONADA (MWIS)",
        )
    )
    plt.legend(handles=legenda, loc="lower right", fontsize=11)

    plt.title(
        f"Grade Curricular — {nome_curso} ({semestre})",
        fontsize=15, fontweight="bold",
    )
    plt.axis("off")
    plt.savefig(caminho_saida, dpi=150, bbox_inches="tight")
    plt.close()

    return caminho_saida
