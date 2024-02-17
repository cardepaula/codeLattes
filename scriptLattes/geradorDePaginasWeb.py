#!/usr/bin/python
# encoding: utf-8
#
#
# scriptLattes
# http://scriptlattes.sourceforge.net/
#
# Este programa é um software livre; você pode redistribui-lo e/ou
# modifica-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 2 da
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuído na esperança que possa ser util,
# mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
from collections import defaultdict
import datetime
import os
import re
import unicodedata
import logging

import pandas
from pandas.core.indexing import IndexingError
from .charts.graficoDeInternacionalizacao import *
from .highcharts import *  # highcharts
from .membro import *

logger = logging.getLogger("scriptLattes")


class GeradorDePaginasWeb:
    grupo = None
    dir = None
    version = None
    extensaoPagina = None
    arquivoRis = None

    def __init__(self, grupo):
        self.grupo = grupo
        self.version = "V8.13"
        self.dir = self.grupo.obterParametro("global-diretorio_de_saida")

        if self.grupo.obterParametro("global-criar_paginas_jsp"):
            self.extensaoPagina = ".jsp"
            self.html1 = (
                '<%@ page language="java" contentType="text/html; charset=ISO8859-1" '
                'pageEncoding="ISO8859-1"%> '
                '<%@ taglib prefix="f" uri="http://java.sun.com/jsf/core"%> '
                "<f:verbatim>"
            )
            self.html2 = "</f:verbatim>"
        else:
            self.extensaoPagina = ".html"
            self.html1 = "<html>"
            self.html2 = "</html>"

        # geracao de arquivo RIS com as publicacoes
        if self.grupo.obterParametro("relatorio-salvar_publicacoes_em_formato_ris"):
            prefix = (
                self.grupo.obterParametro("global-prefixo") + "-"
                if not self.grupo.obterParametro("global-prefixo") == ""
                else ""
            )
            self.arquivoRis = open(
                self.dir + "/" + prefix + "publicacoes.ris", "w", encoding="utf-8"
            )

        self.gerar_pagina_de_membros()
        self.gerarPaginasDeProducoesBibliograficas()
        self.gerarPaginasDeProducoesTecnicas()
        self.gerarPaginasDeProducoesArtisticas()
        self.gerarPaginasDePatentes()

        if self.grupo.obterParametro("relatorio-mostrar_orientacoes"):
            self.gerarPaginasDeOrientacoes()

        if self.grupo.obterParametro("relatorio-incluir_projeto_pesquisa"):
            self.gerarPaginasDeProjetosDePesquisa()

        if self.grupo.obterParametro("relatorio-incluir_projeto_extensao"):
            self.gerarPaginasDeProjetosDeExtensao()

        if self.grupo.obterParametro("relatorio-incluir_projeto_desenvolvimento"):
            self.gerarPaginasDeProjetosDeDesenvolvimento()

        if self.grupo.obterParametro("relatorio-incluir_outros_projetos"):
            self.gerarPaginasDeOutrosProjetos()

        if self.grupo.obterParametro("relatorio-incluir_premio"):
            self.gerarPaginasDePremios()

        if self.grupo.obterParametro("relatorio-incluir_participacao_em_evento"):
            self.gerarPaginasDeParticipacaoEmEventos()

        if self.grupo.obterParametro("relatorio-incluir_organizacao_de_evento"):
            self.gerarPaginasDeOrganizacaoDeEventos()

        if self.grupo.obterParametro("grafo-mostrar_grafo_de_colaboracoes"):
            self.gerarPaginaDeGrafosDeColaboracoes()

        if self.grupo.obterParametro("relatorio-incluir_internacionalizacao"):
            self.gerarPaginasDeInternacionalizacao()

        # final do fim!
        self.gerarPaginaPrincipal()

        if self.grupo.obterParametro("relatorio-salvar_publicacoes_em_formato_ris"):
            self.arquivoRis.close()

    def gerarPaginaPrincipal(self):
        nomeGrupo = self.grupo.obterParametro("global-nome_do_grupo")

        s = (
            self.html1
            + " \
        <head> \
           <title>"
            + nomeGrupo
            + '</title> \
           <meta name="Generator" content="scriptLattes"> \
           <link rel="stylesheet" href="css/scriptLattes.css" type="text/css">  \
           <meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
        )
        if self.grupo.obterParametro("mapa-mostrar_mapa_de_geolocalizacao"):
            s += self.grupo.mapaDeGeolocalizacao.mapa  # .encode("utf8")

        s += (
            '</head> \n \
        <body onload="initialize()" onunload="GUnload()"> <div id="header">  \
        <center> <h2> '
            + nomeGrupo
            + "</h2>"
        )

        s += (
            "[ <a href=membros"
            + self.extensaoPagina
            + "><b>Membros</b></a> \
            | <a href=#producaoBibliografica>Produção bibliográfica</a> \
            | <a href=#producaoTecnica>Produção técnica</a> \
            | <a href=#producaoArtistica>Produção artística</a> "
        )

        if self.grupo.obterParametro("relatorio-mostrar_orientacoes"):
            s += "| <a href=#orientacoes>Orientações</a> "

        if self.grupo.obterParametro("relatorio-incluir_projeto_pesquisa"):
            s += "| <a href=#projetos>Projetos</a> "

        if self.grupo.obterParametro("relatorio-incluir_premio"):
            s += "| <a href=#premios>Prêmios</a> "

        if self.grupo.obterParametro(
            "relatorio-incluir_participacao_em_evento"
        ) or self.grupo.obterParametro("relatorio-incluir_organizacao_de_evento"):
            s += "| <a href=#eventos>Eventos</a> "

        if self.grupo.obterParametro("grafo-mostrar_grafo_de_colaboracoes"):
            s += "| <a href=#grafo>Grafo de colaborações</a> "

        if self.grupo.obterParametro("mapa-mostrar_mapa_de_geolocalizacao"):
            s += "| <a href=#mapa>Mapa de geolocalização</a> "

        if self.grupo.obterParametro("relatorio-incluir_internacionalizacao"):
            s += "| <a href=#internacionalizacao>Internacionalização</a> "

        if self.grupo.obterParametro("relatorio-incluir_producao_com_colaboradores"):
            s += (
                "| <a href=producao-com-colaboradores/index"
                + self.extensaoPagina
                + "><b>Produção com colaboradores</b></a> "
            )

        s += " ] </center><br></div>"
        s += '<h3 id="producaoBibliografica">Produção bibliográfica</h3> <ul>'

        if self.nPB0 > 0:
            s += (
                '<li> <a href="PB0-0'
                + self.extensaoPagina
                + '">Artigos completos publicados em periódicos</a> '
                + "("
                + str(self.nPB0)
                + ")"
            )
        if self.nPB1 > 0:
            s += (
                '<li> <a href="PB1-0'
                + self.extensaoPagina
                + '">Livros publicados/organizados ou edições</a> '
                + "("
                + str(self.nPB1)
                + ")"
            )
        if self.nPB2 > 0:
            s += (
                '<li> <a href="PB2-0'
                + self.extensaoPagina
                + '">Capítulos de livros publicados </a> '
                + "("
                + str(self.nPB2)
                + ")"
            )
        if self.nPB3 > 0:
            s += (
                '<li> <a href="PB3-0'
                + self.extensaoPagina
                + '">Textos em jornais de notícias/revistas </a> '
                + "("
                + str(self.nPB3)
                + ")"
            )
        if self.nPB4 > 0:
            s += (
                '<li> <a href="PB4-0'
                + self.extensaoPagina
                + '">Trabalhos completos publicados em anais de congressos </a> '
                + "("
                + str(self.nPB4)
                + ")"
            )
        if self.nPB5 > 0:
            s += (
                '<li> <a href="PB5-0'
                + self.extensaoPagina
                + '">Resumos expandidos publicados em anais de congressos </a> '
                + "("
                + str(self.nPB5)
                + ")"
            )
        if self.nPB6 > 0:
            s += (
                '<li> <a href="PB6-0'
                + self.extensaoPagina
                + '">Resumos publicados em anais de congressos </a> '
                + "("
                + str(self.nPB6)
                + ")"
            )
        if self.nPB7 > 0:
            s += (
                '<li> <a href="PB7-0'
                + self.extensaoPagina
                + '">Artigos aceitos para publicação </a> '
                + "("
                + str(self.nPB7)
                + ")"
            )
        if self.nPB8 > 0:
            s += (
                '<li> <a href="PB8-0'
                + self.extensaoPagina
                + '">Apresentações de trabalho </a> '
                + "("
                + str(self.nPB8)
                + ")"
            )
        if self.nPB9 > 0:
            s += (
                '<li> <a href="PB9-0'
                + self.extensaoPagina
                + '">Demais tipos de produção bibliográfica </a> '
                + "("
                + str(self.nPB9)
                + ")"
            )
        if self.nPB > 0:
            s += (
                '<li> <a href="PB-0'
                + self.extensaoPagina
                + '">Total de produção bibliográfica</a> '
                + "("
                + str(self.nPB)
                + ")"
            )
        else:
            s += "<i>Nenhum item achado nos currículos Lattes</i>"

        s += '</ul> <h3 id="producaoTecnica">Produção técnica</h3> <ul>'
        if self.nPT0 > 0:
            s += (
                '<li> <a href="PT0-0'
                + self.extensaoPagina
                + '">Programas de computador com registro de patente</a> '
                + "("
                + str(self.nPT0)
                + ")"
            )
        if self.nPT1 > 0:
            s += (
                '<li> <a href="PT1-0'
                + self.extensaoPagina
                + '">Programas de computador sem registro de patente</a> '
                + "("
                + str(self.nPT1)
                + ")"
            )
        if self.nPT2 > 0:
            s += (
                '<li> <a href="PT2-0'
                + self.extensaoPagina
                + '">Produtos tecnológicos</a> '
                + "("
                + str(self.nPT2)
                + ")"
            )
        if self.nPT3 > 0:
            s += (
                '<li> <a href="PT3-0'
                + self.extensaoPagina
                + '">Processos ou técnicas</a> '
                + "("
                + str(self.nPT3)
                + ")"
            )
        if self.nPT4 > 0:
            s += (
                '<li> <a href="PT4-0'
                + self.extensaoPagina
                + '">Trabalhos técnicos</a> '
                + "("
                + str(self.nPT4)
                + ")"
            )
        if self.nPT5 > 0:
            s += (
                '<li> <a href="PT5-0'
                + self.extensaoPagina
                + '">Demais tipos de produção técnica</a> '
                + "("
                + str(self.nPT5)
                + ")"
            )
        if self.nPT > 0:
            s += (
                '<li> <a href="PT-0'
                + self.extensaoPagina
                + '">Total de produção técnica</a> '
                + "("
                + str(self.nPT)
                + ")"
            )
        else:
            s += "<i>Nenhum item achado nos currículos Lattes</i>"

        s += '</ul> <h3 id="producaoArtistica">Produção artística</h3> <ul>'
        if self.nPA > 0:
            s += (
                '<li> <a href="PA-0'
                + self.extensaoPagina
                + '">Total de produção artística</a> '
                + "("
                + str(self.nPA)
                + ")"
            )
        else:
            s += "<i>Nenhum item achado nos currículos Lattes</i>"

        if self.grupo.obterParametro("relatorio-mostrar_orientacoes"):
            s += '</ul> <h3 id="orientacoes">Orientações</h3> <ul>'
            s += "<li><b>Orientações em andamento</b>"
            s += "<ul>"
            if self.nOA0 > 0:
                s += (
                    '<li> <a href="OA0-0'
                    + self.extensaoPagina
                    + '">Supervisão de pós-doutorado</a> '
                    + "("
                    + str(self.nOA0)
                    + ")"
                )
            if self.nOA1 > 0:
                s += (
                    '<li> <a href="OA1-0'
                    + self.extensaoPagina
                    + '">Tese de doutorado</a> '
                    + "("
                    + str(self.nOA1)
                    + ")"
                )
            if self.nOA2 > 0:
                s += (
                    '<li> <a href="OA2-0'
                    + self.extensaoPagina
                    + '">Dissertação de mestrado</a> '
                    + "("
                    + str(self.nOA2)
                    + ")"
                )
            if self.nOA3 > 0:
                s += (
                    f'<li> <a href="OA3-0{self.extensaoPagina}">'
                    "Monografia de conclusão de curso de aperfeiçoamento/especialização"
                    f"</a> ({str(self.nOA3)})"
                )
            if self.nOA4 > 0:
                s += (
                    '<li> <a href="OA4-0'
                    + self.extensaoPagina
                    + '">Trabalho de conclusão de curso de graduação</a> '
                    + "("
                    + str(self.nOA4)
                    + ")"
                )
            if self.nOA5 > 0:
                s += (
                    '<li> <a href="OA5-0'
                    + self.extensaoPagina
                    + '">Iniciação científica</a> '
                    + "("
                    + str(self.nOA5)
                    + ")"
                )
            if self.nOA6 > 0:
                s += (
                    '<li> <a href="OA6-0'
                    + self.extensaoPagina
                    + '">Orientações de outra natureza</a> '
                    + "("
                    + str(self.nOA6)
                    + ")"
                )
            if self.nOA > 0:
                s += (
                    '<li> <a href="OA-0'
                    + self.extensaoPagina
                    + '">Total de orientações em andamento</a> '
                    + "("
                    + str(self.nOA)
                    + ")"
                )
            else:
                s += "<i>Nenhum item achado nos currículos Lattes</i>"
            s += "</ul>"

            s += "<li><b>Supervisões e orientações concluídas</b>"
            s += "<ul>"
            if self.nOC0 > 0:
                s += (
                    '<li> <a href="OC0-0'
                    + self.extensaoPagina
                    + '">Supervisão de pós-doutorado</a> '
                    + "("
                    + str(self.nOC0)
                    + ")"
                )
            if self.nOC1 > 0:
                s += (
                    '<li> <a href="OC1-0'
                    + self.extensaoPagina
                    + '">Tese de doutorado</a> '
                    + "("
                    + str(self.nOC1)
                    + ")"
                )
            if self.nOC2 > 0:
                s += (
                    '<li> <a href="OC2-0'
                    + self.extensaoPagina
                    + '">Dissertação de mestrado</a> '
                    + "("
                    + str(self.nOC2)
                    + ")"
                )
            if self.nOC3 > 0:
                s += (
                    f'<li> <a href="OC3-0{self.extensaoPagina}">'
                    "Monografia de conclusão de curso de aperfeiçoamento/especialização"
                    f"</a> ({str(self.nOC3)}"
                )
            if self.nOC4 > 0:
                s += (
                    '<li> <a href="OC4-0'
                    + self.extensaoPagina
                    + '">Trabalho de conclusão de curso de graduação</a> '
                    + "("
                    + str(self.nOC4)
                    + ")"
                )
            if self.nOC5 > 0:
                s += (
                    '<li> <a href="OC5-0'
                    + self.extensaoPagina
                    + '">Iniciação científica</a> '
                    + "("
                    + str(self.nOC5)
                    + ")"
                )
            if self.nOC6 > 0:
                s += (
                    '<li> <a href="OC6-0'
                    + self.extensaoPagina
                    + '">Orientações de outra natureza</a> '
                    + "("
                    + str(self.nOC6)
                    + ")"
                )
            if self.nOC > 0:
                s += (
                    '<li> <a href="OC-0'
                    + self.extensaoPagina
                    + '">Total de orientações concluídas</a> '
                    + "("
                    + str(self.nOC)
                    + ")"
                )
            else:
                s += "<i>Nenhum item achado nos currículos Lattes</i>"
            s += "</ul>"

        if self.grupo.obterParametro("relatorio-incluir_projeto_pesquisa"):
            s += '</ul> <h3 id="projetos">Projetos de pesquisa</h3> <ul>'
            if self.nPj > 0:
                s += (
                    '<li> <a href="Pj-0'
                    + self.extensaoPagina
                    + '">Total de projetos de pesquisa</a> '
                    + "("
                    + str(self.nPj)
                    + ")"
                )
            else:
                s += "<i>Nenhum item achado nos currículos Lattes</i>"
            s += "</ul>"

        if self.grupo.obterParametro("relatorio-incluir_projeto_extensao"):
            s += '</ul> <h3 id="projetos">Projetos de Extensao</h3> <ul>'
            if self.nPje > 0:
                s += (
                    '<li> <a href="Pje-0'
                    + self.extensaoPagina
                    + '">Total de projetos de Extensao</a> '
                    + "("
                    + str(self.nPje)
                    + ")"
                )
            else:
                s += "<i>Nenhum item achado nos currículos Lattes</i>"
            s += "</ul>"

        if self.grupo.obterParametro("relatorio-incluir_projeto_desenvolvimento"):
            s += '</ul> <h3 id="projetos">Projetos de Desenvolvimento</h3> <ul>'
            if self.nPjd > 0:
                s += (
                    '<li> <a href="Pjd-0'
                    + self.extensaoPagina
                    + '">Total de projetos de Desenvolvimento</a> '
                    + "("
                    + str(self.nPjd)
                    + ")"
                )
            else:
                s += "<i>Nenhum item achado nos currículos Lattes</i>"
            s += "</ul>"

        if self.grupo.obterParametro("relatorio-incluir_outros_projetos"):
            s += '</ul> <h3 id="projetos">Outros Projetos</h3> <ul>'
            if self.nOpj > 0:
                s += (
                    '<li> <a href="Opj-0'
                    + self.extensaoPagina
                    + '">Total de outros projetos</a> '
                    + "("
                    + str(self.nOpj)
                    + ")"
                )
            else:
                s += "<i>Nenhum item achado nos currículos Lattes</i>"
            s += "</ul>"

        if self.grupo.obterParametro("relatorio-incluir_premio"):
            s += '</ul> <h3 id="premios">Prêmios e títulos</h3> <ul>'
            if self.nPm > 0:
                s += (
                    '<li> <a href="Pm-0'
                    + self.extensaoPagina
                    + '">Total de prêmios e títulos</a> '
                    + "("
                    + str(self.nPm)
                    + ")"
                )
            else:
                s += "<i>Nenhum item achado nos currículos Lattes</i>"
            s += "</ul>"

        if self.grupo.obterParametro("relatorio-incluir_participacao_em_evento"):
            s += '</ul> <h3 id="eventos">Participação em eventos</h3> <ul>'
            if self.nEp > 0:
                s += (
                    '<li> <a href="Ep-0'
                    + self.extensaoPagina
                    + '">Total de participação em eventos</a> '
                    + "("
                    + str(self.nEp)
                    + ")"
                )
            else:
                s += "<i>Nenhum item achado nos currículos Lattes</i>"
            s += "</ul>"

        if self.grupo.obterParametro("relatorio-incluir_organizacao_de_evento"):
            s += '</ul> <h3 id="eventos">Organização de eventos</h3> <ul>'
            if self.nEo > 0:
                s += (
                    '<li> <a href="Eo-0'
                    + self.extensaoPagina
                    + '">Total de organização de eventos</a> '
                    + "("
                    + str(self.nEo)
                    + ")"
                )
            else:
                s += "<i>Nenhum item achado nos currículos Lattes</i>"
            s += "</ul>"

        if self.grupo.obterParametro("grafo-mostrar_grafo_de_colaboracoes"):
            s += '</ul> <h3 id="grafo">Grafo de colaborações</h3> <ul>'
            s += (
                '<a href="grafoDeColaboracoes'
                + self.extensaoPagina
                + '"><img src="grafoDeColaboracoesSemPesos-t.png" border=1> </a>'
            )
        s += "</ul>"

        if self.grupo.obterParametro("mapa-mostrar_mapa_de_geolocalizacao"):
            s += (
                '<h3 id="mapa">Mapa de geolocaliza&ccedil;&atilde;o</h3> '
                '<br> <div id="map_canvas" style="width: 800px; height: 600px">'
                "</div> <br>"
            )
            s += "<b>Legenda</b><table>"
            if self.grupo.obterParametro("mapa-incluir_membros_do_grupo"):
                s += (
                    "<tr><td> <img src=lattesPoint0.png></td> "
                    "<td> Membro (orientador) </td></tr>"
                )
            if self.grupo.obterParametro("mapa-incluir_alunos_de_pos_doutorado"):
                s += (
                    "<tr><td> <img src=lattesPoint1.png></td> "
                    "<td>  Pesquisador com pós-doutorado concluído e "
                    "ID Lattes cadastrado no currículo do supervisor </td></tr>"
                )
            if self.grupo.obterParametro("mapa-incluir_alunos_de_doutorado"):
                s += (
                    "<tr><td> <img src=lattesPoint2.png></td> "
                    "<td>  Aluno com doutorado concluído e ID Lattes cadastrado "
                    "no currículo do orientador </td></tr>"
                )
            if self.grupo.obterParametro("mapa-incluir_alunos_de_mestrado"):
                s += (
                    "<tr><td> <img src=lattesPoint3.png></td> "
                    "<td>  Aluno com mestrado e ID Lattes cadastrado "
                    "no currículo do orientador </td></tr>"
                )
            s += "</table>"

        if self.grupo.obterParametro("relatorio-incluir_internacionalizacao"):
            s += '</ul> <h3 id="internacionalizacao">Internacionalização</h3> <ul>'
            if self.nIn0 > 0:
                s += (
                    '<li> <a href="In0-0'
                    + self.extensaoPagina
                    + '">Coautoria e internacionalização</a> '
                    + "("
                    + str(self.nIn0)
                    + ")"
                )
            else:
                s += "<i>Nenhuma publicação com DOI disponível para análise</i>"
            s += "</ul>"

        s += self.paginaBottom()
        self.salvarPagina("index" + self.extensaoPagina, s)

    def gerarPaginasDeProducoesBibliograficas(self):
        self.nPB0 = 0
        self.nPB1 = 0
        self.nPB2 = 0
        self.nPB3 = 0
        self.nPB4 = 0
        self.nPB5 = 0
        self.nPB6 = 0
        self.nPB7 = 0
        self.nPB8 = 0
        self.nPB9 = 0
        self.nPB = 0

        if self.grupo.obterParametro("relatorio-incluir_artigo_em_periodico"):
            self.nPB0 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaArtigoEmPeriodico,
                "Artigos completos publicados em periódicos",
                "PB0",
                ris=True,
            )
        if self.grupo.obterParametro("relatorio-incluir_livro_publicado"):
            self.nPB1 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaLivroPublicado,
                "Livros publicados/organizados ou edições",
                "PB1",
                ris=True,
            )
        if self.grupo.obterParametro("relatorio-incluir_capitulo_de_livro_publicado"):
            self.nPB2 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaCapituloDeLivroPublicado,
                "Capítulos de livros publicados",
                "PB2",
                ris=True,
            )
        if self.grupo.obterParametro("relatorio-incluir_texto_em_jornal_de_noticia"):
            self.nPB3 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaTextoEmJornalDeNoticia,
                "Textos em jornais de notícias/revistas",
                "PB3",
                ris=True,
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_trabalho_completo_em_congresso"
        ):
            self.nPB4 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaTrabalhoCompletoEmCongresso,
                "Trabalhos completos publicados em anais de congressos",
                "PB4",
                ris=True,
            )
        if self.grupo.obterParametro("relatorio-incluir_resumo_expandido_em_congresso"):
            self.nPB5 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaResumoExpandidoEmCongresso,
                "Resumos expandidos publicados em anais de congressos",
                "PB5",
                ris=True,
            )
        if self.grupo.obterParametro("relatorio-incluir_resumo_em_congresso"):
            self.nPB6 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaResumoEmCongresso,
                "Resumos publicados em anais de congressos",
                "PB6",
                ris=True,
            )
        if self.grupo.obterParametro("relatorio-incluir_artigo_aceito_para_publicacao"):
            self.nPB7 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaArtigoAceito,
                "Artigos aceitos para publicação",
                "PB7",
            )
        if self.grupo.obterParametro("relatorio-incluir_apresentacao_de_trabalho"):
            self.nPB8 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaApresentacaoDeTrabalho,
                "Apresentações de trabalho",
                "PB8",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_outro_tipo_de_producao_bibliografica"
        ):
            self.nPB9 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOutroTipoDeProducaoBibliografica,
                "Demais tipos de produção bibliográfica",
                "PB9",
            )
        # Total de produção bibliográfica
        self.nPB = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaPB,
            "Total de produção bibliográfica",
            "PB",
        )

    def gerarPaginasDeProducoesTecnicas(self):
        self.nPT0 = 0
        self.nPT1 = 0
        self.nPT2 = 0
        self.nPT3 = 0
        self.nPT4 = 0
        self.nPT5 = 0
        self.nPT = 0

        if self.grupo.obterParametro("relatorio-incluir_software_com_patente"):
            self.nPT0 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaSoftwareComPatente,
                "Softwares com registro de patente",
                "PT0",
            )
        if self.grupo.obterParametro("relatorio-incluir_software_sem_patente"):
            self.nPT1 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaSoftwareSemPatente,
                "Softwares sem registro de patente",
                "PT1",
            )
        if self.grupo.obterParametro("relatorio-incluir_produto_tecnologico"):
            self.nPT2 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaProdutoTecnologico,
                "Produtos tecnológicos",
                "PT2",
            )
        if self.grupo.obterParametro("relatorio-incluir_processo_ou_tecnica"):
            self.nPT3 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaProcessoOuTecnica,
                "Processos ou técnicas",
                "PT3",
            )
        if self.grupo.obterParametro("relatorio-incluir_trabalho_tecnico"):
            self.nPT4 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaTrabalhoTecnico,
                "Trabalhos técnicos",
                "PT4",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_outro_tipo_de_producao_tecnica"
        ):
            self.nPT5 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOutroTipoDeProducaoTecnica,
                "Demais tipos de produção técnica",
                "PT5",
            )
        # Total de produções técnicas
        self.nPT = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaPT, "Total de produção técnica", "PT"
        )

    def gerarPaginasDeProducoesArtisticas(self):
        self.nPA0 = 0
        self.nPA = 0

        if self.grupo.obterParametro("relatorio-incluir_producao_artistica"):
            self.nPA0 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaProducaoArtistica,
                "Produção artística/cultural",
                "PA0",
            )
        # Total de produções técnicas
        self.nPA = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaPA, "Total de produção artística", "PA"
        )

    def gerarPaginasDePatentes(self):
        self.nPR0 = 0
        self.nPR1 = 0
        self.nPR2 = 0
        self.nPR = 0

    def gerarPaginasDeOrientacoes(self):
        self.nOA0 = 0
        self.nOA1 = 0
        self.nOA2 = 0
        self.nOA3 = 0
        self.nOA4 = 0
        self.nOA5 = 0
        self.nOA6 = 0
        self.nOA = 0

        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_em_andamento_pos_doutorado"
        ):
            self.nOA0 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOASupervisaoDePosDoutorado,
                "Supervisão de pós-doutorado",
                "OA0",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_em_andamento_doutorado"
        ):
            self.nOA1 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOATeseDeDoutorado,
                "Tese de doutorado",
                "OA1",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_em_andamento_mestrado"
        ):
            self.nOA2 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOADissertacaoDeMestrado,
                "Dissertação de mestrado",
                "OA2",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_em_andamento_monografia_de_especializacao"
        ):
            self.nOA3 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOAMonografiaDeEspecializacao,
                "Monografia de conclusão de curso de aperfeiçoamento/especialização",
                "OA3",
            )
        if self.grupo.obterParametro("relatorio-incluir_orientacao_em_andamento_tcc"):
            self.nOA4 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOATCC,
                "Trabalho de conclusão de curso de graduação",
                "OA4",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_em_andamento_iniciacao_cientifica"
        ):
            self.nOA5 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOAIniciacaoCientifica,
                "Iniciação científica",
                "OA5",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_em_andamento_outro_tipo"
        ):
            self.nOA6 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOAOutroTipoDeOrientacao,
                "Orientações de outra natureza",
                "OA6",
            )
        # Total de orientações em andamento
        self.nOA = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaOA,
            "Total de orientações em andamento",
            "OA",
        )

        self.nOC0 = 0
        self.nOC1 = 0
        self.nOC2 = 0
        self.nOC3 = 0
        self.nOC4 = 0
        self.nOC5 = 0
        self.nOC6 = 0
        self.nOC = 0

        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_concluida_pos_doutorado"
        ):
            self.nOC0 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOCSupervisaoDePosDoutorado,
                "Supervisão de pós-doutorado",
                "OC0",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_concluida_doutorado"
        ):
            self.nOC1 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOCTeseDeDoutorado,
                "Tese de doutorado",
                "OC1",
            )
        if self.grupo.obterParametro("relatorio-incluir_orientacao_concluida_mestrado"):
            self.nOC2 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOCDissertacaoDeMestrado,
                "Dissertação de mestrado",
                "OC2",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_concluida_monografia_de_especializacao"
        ):
            self.nOC3 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOCMonografiaDeEspecializacao,
                "Monografia de conclusão de curso de aperfeiçoamento/especialização",
                "OC3",
            )
        if self.grupo.obterParametro("relatorio-incluir_orientacao_concluida_tcc"):
            self.nOC4 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOCTCC,
                "Trabalho de conclusão de curso de graduação",
                "OC4",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_concluida_iniciacao_cientifica"
        ):
            self.nOC5 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOCIniciacaoCientifica,
                "Iniciação científica",
                "OC5",
            )
        if self.grupo.obterParametro(
            "relatorio-incluir_orientacao_concluida_outro_tipo"
        ):
            self.nOC6 = self.gerar_pagina_de_producoes(
                self.grupo.compilador.listaCompletaOCOutroTipoDeOrientacao,
                "Orientações de outra natureza",
                "OC6",
            )
        # Total de orientações concluídas
        self.nOC = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaOC,
            "Total de orientações concluídas",
            "OC",
        )

    def gerarPaginasDeProjetosDePesquisa(self):
        self.nPj = 0
        self.nPj = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaProjetoDePesquisa,
            "Total de projetos de pesquisa",
            "Pj",
        )

    def gerarPaginasDeProjetosDeExtensao(self):
        self.nPje = 0
        self.nPje = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaProjetoDeExtensao,
            "Total de projetos de extensao",
            "Pje",
        )

    def gerarPaginasDeProjetosDeDesenvolvimento(self):
        self.nPjd = 0
        self.nPjd = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaProjetoDeDesenvolvimento,
            "Total de projetos de desenvolvimento",
            "Pjd",
        )

    def gerarPaginasDeOutrosProjetos(self):
        self.nOpj = 0
        self.nOpj = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaOutrosProjetos,
            "Total de outros projetos",
            "Opj",
        )

    def gerarPaginasDePremios(self):
        self.nPm = 0
        self.nPm = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaPremioOuTitulo,
            "Total de prêmios e títulos",
            "Pm",
        )

    def gerarPaginasDeParticipacaoEmEventos(self):
        self.nEp = 0
        self.nEp = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaParticipacaoEmEvento,
            "Total de participação em eventos",
            "Ep",
        )

    def gerarPaginasDeOrganizacaoDeEventos(self):
        self.nEo = 0
        self.nEo = self.gerar_pagina_de_producoes(
            self.grupo.compilador.listaCompletaOrganizacaoDeEvento,
            "Total de organização de eventos",
            "Eo",
        )

    def gerarPaginasDeInternacionalizacao(self):
        self.nIn0 = 0
        self.nIn0 = self.gerarPaginaDeInternacionalizacao(
            self.grupo.listaDePublicacoesEinternacionalizacao,
            "Coautoria e internacionalização",
            "In0",
        )

    @staticmethod
    def arranjar_publicacoes(listaCompleta):
        l = []
        for ano in sorted(list(listaCompleta.keys()), reverse=True):
            publicacoes = sorted(listaCompleta[ano], key=lambda x: x.chave.lower())
            for indice, publicacao in enumerate(publicacoes):
                l.append((ano, indice, publicacao))
        return l

    @staticmethod
    def chunks(lista, tamanho):
        """Retorna sucessivos chunks de 'tamanho' a partir da 'lista'"""
        for i in range(0, len(lista), tamanho):
            yield lista[i : i + tamanho]

    @staticmethod
    def template_pagina_de_producoes():
        st = """
                {top}
                {grafico}
                <h3>{titulo}</h3> <br>
                    <div id="container" style="min-width: 310px; max-width: 1920px; height: {height}; margin: 0"></div>
                    Número total de itens: {numero_itens}<br>
                    {totais_qualis}
                    {indice_paginas}
                    {producoes}
                    </table>
                {bottom}
              """
        return st

    @staticmethod
    def template_producao():
        s = """
            <tr valign="top"><td>{indice}. &nbsp;</td> <td>{publicacao}</td></tr>
            """
        return s

    @staticmethod
    def gerar_grafico_de_producoes(listaCompleta, titulo):
        chart = highchart(type=chart_type.column)
        chart.set_y_title("Quantidade")

        categories = []
        areas_map = {None: 0}
        estrato_area_ano_freq = defaultdict(
            lambda: defaultdict(lambda: defaultdict(int))
        )
        for ano, publicacoes in sorted(listaCompleta.items()):
            if ano != 0:
                categories.append(ano)
                for _ in range(len(publicacoes)):
                    try:
                        estrato_area_ano_freq[None][None][ano] += 1
                    except AttributeError:
                        logger.debug("publicação sem atributo qualis")
                        # producao que nao tem qualis
                        estrato_area_ano_freq[None][None][ano] += 1

        series = []
        if not list(estrato_area_ano_freq.keys()):  # produções vazias
            logger.debug("produções vazias")
        else:  # gráfico normal sem qualis
            chart.settitle(titulo)
            chart["plotOptions"]["column"]["stacking"] = None
            chart["chart"]["height"] = 300
            chart["legend"]["enabled"] = jscmd("false")
            chart["xAxis"]["type"] = "category"

            data = []
            for ano in categories:
                freq = estrato_area_ano_freq[None][None][ano]
                data.append([ano, freq])
            series.append({"name": "Total", "data": data})

        chart.set_series(series)

        return chart

    def gerar_pagina_de_producoes(
        self, lista_completa, titulo_pagina, prefixo, ris=False
    ):
        totais_qualis = ""
        if self.grupo.obterParametro("global-identificar_publicacoes_com_qualis"):
            # FIXME: nao está mais sendo usado agora que há qualis online
            if self.grupo.obterParametro("global-arquivo_qualis_de_periodicos"):
                if prefixo == "PB0":
                    totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB0)
                elif prefixo == "PB7":
                    totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB7)
            if self.grupo.obterParametro("global-arquivo_qualis_de_congressos"):
                if prefixo == "PB4":
                    totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB4)
                elif prefixo == "PB5":
                    totais_qualis = self.formatarTotaisQualis(self.grupo.qualis.qtdPB5)

        total_producoes = sum(len(v) for v in list(lista_completa.values()))

        keys = sorted(list(lista_completa.keys()), reverse=True)
        if keys:  # apenas geramos páginas web para lista com pelo menos 1 elemento
            max_elementos = int(self.grupo.obterParametro("global-itens_por_pagina"))
            # dividimos os relatórios em grupos (e.g 1000 items)
            total_paginas = int(math.ceil(total_producoes / (max_elementos * 1.0)))

            # FIXME: é o mesmo gráfico em todas as páginas
            grafico = self.gerar_grafico_de_producoes(lista_completa, titulo_pagina)

            anos_indices_publicacoes = self.arranjar_publicacoes(lista_completa)
            itens_por_pagina = self.chunks(anos_indices_publicacoes, max_elementos)
            for numero_pagina, itens in enumerate(itens_por_pagina):
                producoes_html = ""
                for indice_na_pagina, (ano, indice_no_ano, publicacao) in enumerate(
                    itens
                ):
                    # armazenamos uma copia da publicacao (formato RIS)
                    if ris and self.grupo.obterParametro(
                        "relatorio-salvar_publicacoes_em_formato_ris"
                    ):
                        self.salvarPublicacaoEmFormatoRIS(publicacao)

                    if indice_na_pagina == 0 or indice_no_ano == 0:
                        if indice_na_pagina > 0:
                            producoes_html += "</table></div>"
                        ano_text = ano if ano else "*itens sem ano"
                        producoes_html += (
                            f'<div id="dv-year-{ano_text}">'
                            f'<h3 class="year">{ano_text}</h3> <table>'
                        )

                    producao_html = self.template_producao()
                    producao_html = producao_html.format(
                        indice=indice_no_ano + 1,
                        publicacao=publicacao.html(self.grupo.listaDeMembros),
                    )
                    producoes_html += producao_html
                producoes_html += "</table></div>"

                pagina_html = self.template_pagina_de_producoes()
                pagina_html = pagina_html.format(
                    top=self.pagina_top(),
                    bottom=self.paginaBottom(),
                    grafico=grafico.html(),
                    height=grafico["chart"]["height"],
                    titulo=titulo_pagina,
                    numero_itens=str(total_producoes),
                    totais_qualis=totais_qualis,
                    indice_paginas=self.gerarIndiceDePaginas(
                        total_paginas, numero_pagina, prefixo
                    ),
                    producoes=producoes_html,
                )
                self.salvarPagina(
                    prefixo + "-" + str(numero_pagina) + self.extensaoPagina,
                    pagina_html,
                )
        return total_producoes

    def gerarIndiceDePaginas(self, numeroDePaginas, numeroDePaginaAtual, prefixo):
        if numeroDePaginas == 1:
            return ""
        else:
            s = "Página: "
            for i in range(0, numeroDePaginas):
                if i == numeroDePaginaAtual:
                    s += "<b>" + str(i + 1) + "</b> &nbsp;"
                else:
                    s += (
                        '<a href="'
                        + prefixo
                        + "-"
                        + str(i)
                        + self.extensaoPagina
                        + '">'
                        + str(i + 1)
                        + "</a> &nbsp;"
                    )
            return "<center>" + s + "</center>"

    def gerarPaginaDeInternacionalizacao(self, listaCompleta, tituloPagina, prefixo):
        numeroTotalDeProducoes = 0
        gInternacionalizacao = GraficoDeInternacionalizacao(listaCompleta)
        htmlCharts = gInternacionalizacao.criarGraficoDeBarrasDeOcorrencias()

        keys = list(listaCompleta.keys())
        keys.sort(reverse=True)
        if (
            len(keys) > 0
        ):  # apenas geramos páginas web para lista com pelo menos 1 elemento
            for ano in keys:
                numeroTotalDeProducoes += len(listaCompleta[ano])

            maxElementos = int(self.grupo.obterParametro("global-itens_por_pagina"))
            # dividimos os relatórios em grupos (e.g 1000 items)
            numeroDePaginas = int(
                math.ceil(numeroTotalDeProducoes / (maxElementos * 1.0))
            )

            numeroDeItem = 1
            numeroDePaginaAtual = 0
            s = ""

            for ano in keys:
                anoRotulo = str(ano) if not ano == 0 else "*itens sem ano"

                s += '<h3 class="year">' + anoRotulo + "</h3> <table>"

                elementos = listaCompleta[ano]
                # Ordenamos a lista em forma ascendente (hard to explain!)
                elementos.sort(key=lambda x: x.chave.lower())

                for index, pub in enumerate(elementos):
                    s += (
                        '<tr valign="top"><td>'
                        + str(index + 1)
                        + ". &nbsp;</td> <td>"
                        + pub.html()
                        + "</td></tr>"
                    )

                    if (
                        numeroDeItem % maxElementos == 0
                        or numeroDeItem == numeroTotalDeProducoes
                    ):
                        st = self.pagina_top(cabecalho=htmlCharts)
                        st += (
                            "\n<h3>"
                            + tituloPagina
                            + (
                                '</h3> <br> <center> <table> <tr> <td valign="top">'
                                '<div id="barchart_div"></div> </td> <td valign="top">'
                                '<div id="geochart_div"></div> </td> </tr> </table> '
                                "</center>"
                            )
                        )
                        st += "<table>"
                        st += (
                            "<tr><td>Número total de publicações realizadas "
                            "SEM parceria com estrangeiros:</td><td>"
                            + str(
                                gInternacionalizacao.numeroDePublicacoesRealizadasSemParceirasComEstrangeiros()
                            )
                            + "</td><td><i>(publicações realizadas só por "
                            "pesquisadores brasileiros)</i></td></tr>"
                        )
                        st += (
                            "<tr><td>Número total de publicações realizadas "
                            "COM parceria com estrangeiros:</td><td>"
                            + str(
                                gInternacionalizacao.numeroDePublicacoesRealizadasComParceirasComEstrangeiros()
                            )
                            + "</td><td></td></tr>"
                        )
                        st += (
                            "<tr><td>Número total de publicações com parcerias "
                            "NÂO identificadas:</td><td>"
                            + str(
                                gInternacionalizacao.numeroDePublicacoesComParceriasNaoIdentificadas()
                            )
                            + "</td><td></td></tr>"
                        )
                        st += (
                            "<tr><td>Número total de publicações "
                            "com DOI cadastrado:</td><td><b>"
                            + str(numeroTotalDeProducoes)
                            + "</b></td><td></td></tr>"
                        )
                        st += "</table>"
                        st += (
                            '<br> <font color="red">(*) A estimativa de "coautoria '
                            'e internacionalização" é baseada na análise automática '
                            "dos DOIs das publicações cadastradas nos CVs Lattes. "
                            "A identificação de países, para cada publicação, é "
                            "feita através de buscas simples de nomes de países."
                            "</font><br><p>"
                        )

                        st += self.gerarIndiceDePaginas(
                            numeroDePaginas, numeroDePaginaAtual, prefixo
                        )
                        st += s
                        st += "</table>"
                        st += self.paginaBottom()

                        self.salvarPagina(
                            prefixo
                            + "-"
                            + str(numeroDePaginaAtual)
                            + self.extensaoPagina,
                            st,
                        )
                        numeroDePaginaAtual += 1

                        if (index + 1) < len(elementos):
                            s = '<h3 class="year">' + anoRotulo + "</h3> <table>"
                        else:
                            s = ""
                    numeroDeItem += 1

                s += "</table>"
        return numeroTotalDeProducoes

    def gerarPaginaDeGrafosDeColaboracoes(self):
        lista = ""
        if self.grupo.obterParametro("grafo-incluir_artigo_em_periodico"):
            lista += "Artigos completos publicados em periódicos, "
        if self.grupo.obterParametro("grafo-incluir_livro_publicado"):
            lista += "Livros publicados/organizados ou edições, "
        if self.grupo.obterParametro("grafo-incluir_capitulo_de_livro_publicado"):
            lista += "Capítulos de livros publicados, "
        if self.grupo.obterParametro("grafo-incluir_texto_em_jornal_de_noticia"):
            lista += "Textos em jornais de notícias/revistas, "
        if self.grupo.obterParametro("grafo-incluir_trabalho_completo_em_congresso"):
            lista += "Trabalhos completos publicados em anais de congressos, "
        if self.grupo.obterParametro("grafo-incluir_resumo_expandido_em_congresso"):
            lista += "Resumos expandidos publicados em anais de congressos, "
        if self.grupo.obterParametro("grafo-incluir_resumo_em_congresso"):
            lista += "Resumos publicados em anais de congressos, "
        if self.grupo.obterParametro("grafo-incluir_artigo_aceito_para_publicacao"):
            lista += "Artigos aceitos para publicação, "
        if self.grupo.obterParametro("grafo-incluir_apresentacao_de_trabalho"):
            lista += "Apresentações de trabalho, "
        if self.grupo.obterParametro(
            "grafo-incluir_outro_tipo_de_producao_bibliografica"
        ):
            lista += "Demais tipos de produção bibliográfica, "

        lista = lista.strip().strip(",")

        s = self.pagina_top()
        s += (
            "\n<h3>Grafo de colabora&ccedil;&otilde;es</h3> "
            "<a href=membros"
            + self.extensaoPagina
            + ">"
            + str(self.grupo.numeroDeMembros())
            + " curriculos Lattes</a> foram considerados, "
            "gerando os seguintes grafos de colabora&ccedil;&otilde;es "
            "encontradas com base nas produ&ccedil;&otilde;es: <i>"
            + lista
            + "</i>. <br><p>"
        )

        prefix = (
            self.grupo.obterParametro("global-prefixo") + "-"
            if not self.grupo.obterParametro("global-prefixo") == ""
            else ""
        )

        s += (
            "\nClique no nome dentro do vértice para visualizar o currículo Lattes. "
            "Para cada nó: o valor entre colchetes indica o número de "
            "produ&ccedil;&otilde;es feitas em colabora&ccedil;&atilde;o apenas "
            "com os outros membros do próprio grupo. <br>"
        )

        if self.grupo.obterParametro("grafo-considerar_rotulos_dos_membros_do_grupo"):
            s += "As cores representam os seguintes rótulos: "
            for i, rot in enumerate(self.grupo.listaDeRotulos):
                cor = self.grupo.listaDeRotulosCores[i]
                if rot == "":
                    rot = "[Sem rótulo]"
                s += (
                    '<span style="background-color:'
                    + cor
                    + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>'
                    + rot
                    + " "
                )
        s += (
            "<ul> "
            "<li><b>Grafo de colabora&ccedil;&otilde;es sem pesos</b><br> "
            "    <img src=grafoDeColaboracoesSemPesos.png border=1 ISMAP "
            'USEMAP="#grafo1"> <br><p> '
            "<li><b>Grafo de colabora&ccedil;&otilde;es com pesos</b><br> "
            "    <img src=grafoDeColaboracoesComPesos.png border=1 ISMAP "
            'USEMAP="#grafo2"> <br><p> '
            "<li><b>Grafo de colabora&ccedil;&otilde;es com pesos normalizados</b><br> "
            "    <img src=grafoDeColaboracoesNormalizado.png border=1 ISMAP "
            'USEMAP="#grafo3"> '
            "</ul>"
        )

        cmapx1 = self.grupo.grafosDeColaboracoes.grafoDeCoAutoriaSemPesosCMAPX
        cmapx2 = self.grupo.grafosDeColaboracoes.grafoDeCoAutoriaComPesosCMAPX
        cmapx3 = self.grupo.grafosDeColaboracoes.grafoDeCoAutoriaNormalizadoCMAPX
        s += '<map id="grafo1" name="grafo1">' + cmapx1 + "\n</map>\n"
        s += '<map id="grafo2" name="grafo2">' + cmapx2 + "\n</map>\n"
        s += '<map id="grafo3" name="grafo3">' + cmapx3 + "\n</map>\n"

        if self.grupo.obterParametro("grafo-incluir_grau_de_colaboracao"):
            s += (
                "<br><p><h3>Grau de colaboração</h3> O grau de colaboração "
                "(<i>Collaboration Rank</i>) é um valor numérico que indica o "
                "impacto de um membro no grafo de colaborações. <br>Esta medida é "
                "similar ao <i>PageRank</i> para grafos direcionais (com pesos)."
                "<br><p>"
            )

            ranks, autores, rotulos = list(
                zip(
                    *sorted(
                        zip(
                            self.grupo.vectorRank, self.grupo.nomes, self.grupo.rotulos
                        ),
                        reverse=True,
                    )
                )
            )

            s += (
                "<table border=1><tr> <td><i><b>Collaboration Rank</b></i></td> "
                "<td><b>Membro</b></td> </tr>"
            )
            for i, rank in enumerate(ranks):
                s += (
                    "<tr><td>"
                    + str(round(rank, 2))
                    + "</td><td>"
                    + autores[i]
                    + "</td></tr>"
                )
            s += "</table> <br><p>"

            if self.grupo.obterParametro(
                "grafo-considerar_rotulos_dos_membros_do_grupo"
            ):
                for i, rotulo in enumerate(self.grupo.listaDeRotulos):
                    somaAuthorRank = 0
                    cor = self.grupo.listaDeRotulosCores[i]
                    s += (
                        '<b><span style="background-color:'
                        + cor
                        + '">&nbsp;&nbsp;&nbsp;&nbsp;</span>'
                        + rotulo
                        + "</b><br>"
                    )

                    s += (
                        "<table border=1><tr> <td><i><b>AuthorRank</b></i></td> "
                        "<td><b>Membro</b></td> </tr>"
                    )
                    for i, rank in enumerate(ranks):
                        if rotulos[i] == rotulo:
                            s += (
                                "<tr><td>"
                                + str(round(rank, 2))
                                + "</td><td>"
                                + autores[i]
                                + "</td></tr>"
                            )
                            somaAuthorRank += rank
                    s += (
                        "</table> <br> Total: "
                        + str(round(somaAuthorRank, 2))
                        + "<br><p>"
                    )

        s += self.paginaBottom()
        self.salvarPagina("grafoDeColaboracoes" + self.extensaoPagina, s)

        # grafo interativo
        s = self.pagina_top()
        s += (
            "<applet code=MyGraph.class width=1280 height=800 archive="
            '"http://www.vision.ime.usp.br/creativision/graphview/graphview.jar,'
            'http://www.vision.ime.usp.br/creativision/graphview/prefuse.jar">'
            "</applet></body></html>"
        )
        s += self.paginaBottom()
        self.salvarPagina("grafoDeColaboracoesInterativo" + self.extensaoPagina, s)

    @staticmethod
    def producao_qualis(elemento, membro):
        tabela_template = (
            '<table style="width: 100%; display: block; overflow-x: auto;"><tbody>'
            '<br><span style="font-size:14px;"><b>Totais de publicações com '
            "Qualis:</b></span><br><br>"
            '<div style="width:100%; overflow-x:scroll;">{body}</div>'
            "</tbody></table>"
        )

        first_column_template = (
            '<div style="float:left; width:200px; height: auto; '
            "border: 1px solid black; border-collapse: collapse; margin-left:0px; "
            "margin-top:0px; background:#CCC; vertical-align: middle; padding: 4px 0;"
            ' {extra_style}"><b>{header}</b></div>'
        )
        header_template = (
            '<div style="float:left; width:{width}px; height: auto; '
            "border-style: solid; border-color: black; border-width: 1 1 1 0; "
            "border-collapse: collapse; margin-left:0px; margin-top:0px;"
            " background:#CCC; text-align: center; vertical-align: middle; "
            'padding: 4px 0;"><b>{header}</b></div>'
        )
        line_template = (
            '<div style="float:left; width:{width}px; height: auto; '
            "border-style: solid; border-color: black; border-width: 1 1 1 0; "
            "border-collapse: collapse; margin-left:0px; margin-top:0px;"
            " background:#EAEAEA; text-align: center; vertical-align: middle; "
            'padding: 4px 0;">{value}</div>'
        )

        cell_size = 40
        num_estratos = len(membro.tabela_qualis["estrato"].unique())

        header_ano = first_column_template.format(
            header="Ano", extra_style="text-align: center;"
        )
        header_estrato = first_column_template.format(
            header="Área \\ Estrato", extra_style="text-align: center;"
        )

        for ano in sorted(membro.tabela_qualis["ano"].unique()):
            header_ano += header_template.format(
                header=ano, width=num_estratos * (cell_size + 1) - 1
            )
            for estrato in sorted(membro.tabela_qualis["estrato"].unique()):
                header_estrato += header_template.format(
                    header=estrato, width=cell_size
                )

        if membro.tabela_qualis and not membro.tabela_qualis.empty():
            pt = membro.tabela_qualis.pivot_table(
                columns=["area", "ano", "estrato"], values="freq"
            )
        lines = ""
        for area in sorted(membro.tabela_qualis["area"].unique()):
            lines += first_column_template.format(header=area, extra_style="")
            for ano in sorted(membro.tabela_qualis["ano"].unique()):
                for estrato in sorted(membro.tabela_qualis["estrato"].unique()):
                    try:
                        lines += line_template.format(
                            value=pt.ix[area, ano, estrato], width=cell_size
                        )
                    except IndexingError:
                        lines += line_template.format(value="&nbsp;", width=cell_size)
            lines += '<div style="clear:both"></div>'

        tabela_body = header_ano
        tabela_body += '<div style="clear:both"></div>'
        tabela_body += header_estrato
        tabela_body += '<div style="clear:both"></div>'
        tabela_body += lines

        tabela = tabela_template.format(body=tabela_body)

        return tabela

    def gerar_pagina_de_membros(self):
        s = self.pagina_top()
        s += '\n<h3>Lista de membros</h3> <table id="membros" class="sortable" ><tr>\
                <th></th>\
                <th></th>\
                <th><b><font size=-1>Rótulo/Grupo</font></b></th>\
                <th><b><font size=-1>Bolsa CNPq</font></b></th>\
                <th><b><font size=-1>Período de<br>análise individual</font></b></th>\
                <th><b><font size=-1>Data de<br>atualização do CV</font><b></th>\
                <th><b><font size=-1>Grande área</font><b></th>\
                <th><b><font size=-1>Área</font><b></th>\
                <th><b><font size=-1>Instituição</font><b></th>\
                </tr>'

        elemento = 0
        for membro in self.grupo.listaDeMembros:
            elemento += 1
            bolsa = membro.bolsaProdutividade if membro.bolsaProdutividade else ""
            rotulo = membro.rotulo if not membro.rotulo == "[Sem rotulo]" else ""
            nomeCompleto = (
                unicodedata.normalize("NFKD", membro.nomeCompleto)
                .encode("ASCII", "ignore")
                .decode()
            )

            self.gerar_pagina_individual_de_membro(membro)

            s += f'\n<tr class="testetabela"> \
                     <td valign="center">{str(elemento)}.</td> \
                     <td><a href="membro-{membro.idLattes}.html"> {nomeCompleto}</a></td> \
                     <td><font size=-2>{rotulo}</font></td> \
                     <td><font size=-2>{bolsa}</font></td> \
                     <td><font size=-2>{membro.periodo}</font></td> \
                     <td><font size=-2>{membro.atualizacaoCV}</font></td> \
                     <td><font size=-2>{membro.nomePrimeiraGrandeArea}</font></td> \
                     <td><font size=-2>{membro.nomePrimeiraArea}</font></td> \
                     <td><font size=-2>{membro.instituicao}</font></td> \
                 </tr>'

        s += "\n</table>"

        s += (
            "<script>"
            "  $(document).ready( function () {"
            "    $('#membros').DataTable();"
            "  });"
            "</script>"
        )

        s += self.paginaBottom()

        self.salvarPagina("membros" + self.extensaoPagina, s)

    def gerar_pagina_individual_de_membro(self, membro):
        bolsa = membro.bolsaProdutividade if membro.bolsaProdutividade else ""
        rotulo = membro.rotulo if not membro.rotulo == "[Sem rotulo]" else ""
        nomeCompleto = (
            unicodedata.normalize("NFKD", membro.nomeCompleto)
            .encode("ASCII", "ignore")
            .decode()
        )

        s = self.pagina_top()
        s += f'\n<h3>{nomeCompleto}</h3>\
                {membro.textoResumo}<br><p>\
                <table border=0>\
                <tr><td>\
                    <img height=130px src={membro.foto}>\
                </td><td>\
                    <ul>\
                    <li> <a href="{membro.url}">{membro.url}</a> ({membro.atualizacaoCV}) </li>\
                    <li> <b>Rótulo/Grupo:</b> {rotulo}</li>\
                    <li> <b>Bolsa CNPq:</b> {bolsa}</li>\
                    <li> <b>Período de análise:</b> {membro.periodo}</li>\
                    <li> <b>Endereço:</b> {membro.enderecoProfissional}</li>\
                    <li> <b>Grande área:</b> {membro.nomePrimeiraGrandeArea}</li>\
                    <li> <b>Área:</b> {membro.nomePrimeiraArea}</li>\
                    <li> <b>Citações:</b> <a href="http://scholar.google.com.br/citations?view_op=search_authors&mauthors={nomeCompleto}">Google Acadêmico</a> </li>\
                    </ul>\
                </td><tr>\
                </table><br>'

        (nPB0, lista_PB0, titulo_PB0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaArtigoEmPeriodico, "Artigos completos publicados em periódicos"
        )
        (nPB1, lista_PB1, titulo_PB1) = self.gerar_lista_de_producoes_de_membro(
            membro.listaLivroPublicado, "Livros publicados/organizados ou edições"
        )
        (nPB2, lista_PB2, titulo_PB2) = self.gerar_lista_de_producoes_de_membro(
            membro.listaCapituloDeLivroPublicado, "Capítulos de livros publicados"
        )
        (nPB3, lista_PB3, titulo_PB3) = self.gerar_lista_de_producoes_de_membro(
            membro.listaTextoEmJornalDeNoticia, "Textos em jornais de notícias/revistas"
        )
        (nPB4, lista_PB4, titulo_PB4) = self.gerar_lista_de_producoes_de_membro(
            membro.listaTrabalhoCompletoEmCongresso,
            "Trabalhos completos publicados em anais de congressos",
        )
        (nPB5, lista_PB5, titulo_PB5) = self.gerar_lista_de_producoes_de_membro(
            membro.listaResumoExpandidoEmCongresso,
            "Resumos expandidos publicados em anais de congressos",
        )
        (nPB6, lista_PB6, titulo_PB6) = self.gerar_lista_de_producoes_de_membro(
            membro.listaResumoEmCongresso, "Resumos publicados em anais de congressos"
        )
        (nPB7, lista_PB7, titulo_PB7) = self.gerar_lista_de_producoes_de_membro(
            membro.listaArtigoAceito, "Artigos aceitos para publicação"
        )
        (nPB8, lista_PB8, titulo_PB8) = self.gerar_lista_de_producoes_de_membro(
            membro.listaApresentacaoDeTrabalho, "Apresentações de trabalho"
        )
        (nPB9, lista_PB9, titulo_PB9) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOutroTipoDeProducaoBibliografica,
            "Demais tipos de produção bibliográfica",
        )

        (nPT0, lista_PT0, titulo_PT0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaSoftwareComPatente,
            "Programas de computador com registro de patente",
        )
        (nPT1, lista_PT1, titulo_PT1) = self.gerar_lista_de_producoes_de_membro(
            membro.listaSoftwareSemPatente,
            "Programas de computador sem registro de patente",
        )
        (nPT2, lista_PT2, titulo_PT2) = self.gerar_lista_de_producoes_de_membro(
            membro.listaProdutoTecnologico, "Produtos tecnológicos"
        )
        (nPT3, lista_PT3, titulo_PT3) = self.gerar_lista_de_producoes_de_membro(
            membro.listaProcessoOuTecnica, "Processos ou técnicas"
        )
        (nPT4, lista_PT4, titulo_PT4) = self.gerar_lista_de_producoes_de_membro(
            membro.listaTrabalhoTecnico, "Trabalhos técnicos"
        )
        (nPT5, lista_PT5, titulo_PT5) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOutroTipoDeProducaoTecnica, "Demais tipos de produção técnica"
        )

        (nPA0, lista_PA0, titulo_PA0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaProducaoArtistica, "Total de produção artística"
        )

        (nOA0, lista_OA0, titulo_OA0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOASupervisaoDePosDoutorado, "Supervisão de pós-doutorado"
        )
        (nOA1, lista_OA1, titulo_OA1) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOATeseDeDoutorado, "Tese de doutorado"
        )
        (nOA2, lista_OA2, titulo_OA2) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOADissertacaoDeMestrado, "Dissertação de mestrado"
        )
        (nOA3, lista_OA3, titulo_OA3) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOAMonografiaDeEspecializacao,
            "Monografia de conclusão de curso de aperfeiçoamento/especialização",
        )
        (nOA4, lista_OA4, titulo_OA4) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOATCC, "Trabalho de conclusão de curso de graduação"
        )
        (nOA5, lista_OA5, titulo_OA5) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOAIniciacaoCientifica, "Iniciação científica"
        )
        (nOA6, lista_OA6, titulo_OA6) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOAOutroTipoDeOrientacao, "Orientações de outra natureza"
        )

        (nOC0, lista_OC0, titulo_OC0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOCSupervisaoDePosDoutorado, "Supervisão de pós-doutorado"
        )
        (nOC1, lista_OC1, titulo_OC1) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOCTeseDeDoutorado, "Tese de doutorado"
        )
        (nOC2, lista_OC2, titulo_OC2) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOCDissertacaoDeMestrado, "Dissertação de mestrado"
        )
        (nOC3, lista_OC3, titulo_OC3) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOCMonografiaDeEspecializacao,
            "Monografia de conclusão de curso de aperfeiçoamento/especialização",
        )
        (nOC4, lista_OC4, titulo_OC4) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOCTCC, "Trabalho de conclusão de curso de graduação"
        )
        (nOC5, lista_OC5, titulo_OC5) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOCIniciacaoCientifica, "Iniciação científica"
        )
        (nOC6, lista_OC6, titulo_OC6) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOCOutroTipoDeOrientacao, "Orientações de outra natureza"
        )

        (nPj0, lista_Pj0, titulo_Pj0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaProjetoDePesquisa, "Total de projetos de pesquisa"
        )
        (nPje0, lista_Pje0, titulo_Pje0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaProjetoDeExtensao, "Total de projetos de extensao"
        )
        (nPjd0, lista_Pjd0, titulo_Pjd0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaProjetoDeDesenvolvimento, "Total de projetos de desenvolvimento"
        )
        (nOpj0, lista_Opj0, titulo_Opj0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOutrosProjetos, "Total de outros projetos"
        )
        (nPm0, lista_Pm0, titulo_Pm0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaPremioOuTitulo, "Total de prêmios e títulos"
        )
        (nEp0, lista_Ep0, titulo_Ep0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaParticipacaoEmEvento, "Total de participação em eventos"
        )
        (nEo0, lista_Eo0, titulo_Eo0) = self.gerar_lista_de_producoes_de_membro(
            membro.listaOrganizacaoDeEvento, "Total de organização de eventos"
        )

        (nCE, lista_CE, titulo_CE, lista_CE_detalhe) = self.gerar_lista_de_colaboracoes(
            membro, "Colaborações endôgenas"
        )

        s += "<h3>Produção bibliográfica</h3> <ul>"
        s += f'<li><a href="#PB0">{titulo_PB0}</a> ({nPB0}) </li>'
        s += f'<li><a href="#PB1">{titulo_PB1}</a> ({nPB1}) </li>'
        s += f'<li><a href="#PB2">{titulo_PB2}</a> ({nPB2}) </li>'
        s += f'<li><a href="#PB3">{titulo_PB3}</a> ({nPB3}) </li>'
        s += f'<li><a href="#PB4">{titulo_PB4}</a> ({nPB4}) </li>'
        s += f'<li><a href="#PB5">{titulo_PB5}</a> ({nPB5}) </li>'
        s += f'<li><a href="#PB6">{titulo_PB6}</a> ({nPB6}) </li>'
        s += f'<li><a href="#PB7">{titulo_PB7}</a> ({nPB7}) </li>'
        s += f'<li><a href="#PB8">{titulo_PB8}</a> ({nPB8}) </li>'
        s += f'<li><a href="#PB9">{titulo_PB9}</a> ({nPB9}) </li>'
        s += "</ul>"
        s += "<h3>Produção técnica</h3> <ul>"
        s += f'<li><a href="#PT0">{titulo_PT0}</a> ({nPT0}) </li>'
        s += f'<li><a href="#PT1">{titulo_PT1}</a> ({nPT1}) </li>'
        s += f'<li><a href="#PT2">{titulo_PT2}</a> ({nPT2}) </li>'
        s += f'<li><a href="#PT3">{titulo_PT3}</a> ({nPT3}) </li>'
        s += f'<li><a href="#PT4">{titulo_PT4}</a> ({nPT4}) </li>'
        s += f'<li><a href="#PT5">{titulo_PT5}</a> ({nPT5}) </li>'
        s += "</ul>"
        s += "<h3>Produção artística</h3> <ul>"
        s += f'<li><a href="#PA0">{titulo_PA0}</a> ({nPA0}) </li>'
        s += "</ul>"
        s += "<h3>Orientações em andamento</h3> <ul>"
        s += f'<li><a href="#OA0">{titulo_OA0}</a> ({nOA0}) </li>'
        s += f'<li><a href="#OA1">{titulo_OA1}</a> ({nOA1}) </li>'
        s += f'<li><a href="#OA2">{titulo_OA2}</a> ({nOA2}) </li>'
        s += f'<li><a href="#OA3">{titulo_OA3}</a> ({nOA3}) </li>'
        s += f'<li><a href="#OA4">{titulo_OA4}</a> ({nOA4}) </li>'
        s += f'<li><a href="#OA5">{titulo_OA5}</a> ({nOA5}) </li>'
        s += f'<li><a href="#OA6">{titulo_OA6}</a> ({nOA6}) </li>'
        s += "</ul>"
        s += "<h3>Supervisões e orientações concluídas</h3> <ul>"
        s += f'<li><a href="#OC0">{titulo_OC0}</a> ({nOC0}) </li>'
        s += f'<li><a href="#OC1">{titulo_OC1}</a> ({nOC1}) </li>'
        s += f'<li><a href="#OC2">{titulo_OC2}</a> ({nOC2}) </li>'
        s += f'<li><a href="#OC3">{titulo_OC3}</a> ({nOC3}) </li>'
        s += f'<li><a href="#OC4">{titulo_OC4}</a> ({nOC4}) </li>'
        s += f'<li><a href="#OC5">{titulo_OC5}</a> ({nOC5}) </li>'
        s += f'<li><a href="#OC6">{titulo_OC6}</a> ({nOC6}) </li>'
        s += "</ul>"
        s += "<h3>Projetos de pesquisa</h3> <ul>"
        s += f'<li><a href="#Pj0">{titulo_Pj0}</a> ({nPj0}) </li>'
        s += "</ul>"
        s += "<h3>Projetos de extensao</h3> <ul>"
        s += f'<li><a href="#Pje0">{titulo_Pje0}</a> ({nPje0}) </li>'
        s += "</ul>"
        s += "<h3>Projetos de desenvolvimento</h3> <ul>"
        s += f'<li><a href="#Pjd0">{titulo_Pjd0}</a> ({nPjd0}) </li>'
        s += "</ul>"
        s += "<h3>Outros Projetos</h3> <ul>"
        s += f'<li><a href="#Opj0">{titulo_Opj0}</a> ({nOpj0}) </li>'
        s += "</ul>"
        s += "<h3>Prêmios e títulos</h3> <ul>"
        s += f'<li><a href="#Pm0">{titulo_Pm0}</a> ({nPm0}) </li>'
        s += "</ul>"
        s += "<h3>Participação em eventos</h3> <ul>"
        s += f'<li><a href="#Ep0">{titulo_Ep0}</a> ({nEp0}) </li>'
        s += "</ul>"
        s += "<h3>Organização de eventos</h3> <ul>"
        s += f'<li><a href="#Eo0">{titulo_Eo0}</a> ({nEo0}) </li>'
        s += "</ul>"
        # --------
        s += "<h3>Lista de colaborações</h3> <ul>"
        s += f'<li><a href="#CE">{titulo_CE}</a> ({nCE}) </li>'
        s += f"    <ul> {lista_CE} </ul>"
        s += "</ul>"

        s += "<hr>"
        s += "<h3>Produção bibliográfica</h3> <ul>"
        s += f'<li id="PB0"> <b>{titulo_PB0}</b> ({nPB0}) <br> {lista_PB0} </li>'
        s += f'<li id="PB1"> <b>{titulo_PB1}</b> ({nPB1}) <br> {lista_PB1} </li>'
        s += f'<li id="PB2"> <b>{titulo_PB2}</b> ({nPB2}) <br> {lista_PB2} </li>'
        s += f'<li id="PB3"> <b>{titulo_PB3}</b> ({nPB3}) <br> {lista_PB3} </li>'
        s += f'<li id="PB4"> <b>{titulo_PB4}</b> ({nPB4}) <br> {lista_PB4} </li>'
        s += f'<li id="PB5"> <b>{titulo_PB5}</b> ({nPB5}) <br> {lista_PB5} </li>'
        s += f'<li id="PB6"> <b>{titulo_PB6}</b> ({nPB6}) <br> {lista_PB6} </li>'
        s += f'<li id="PB7"> <b>{titulo_PB7}</b> ({nPB7}) <br> {lista_PB7} </li>'
        s += f'<li id="PB8"> <b>{titulo_PB8}</b> ({nPB8}) <br> {lista_PB8} </li>'
        s += f'<li id="PB9"> <b>{titulo_PB9}</b> ({nPB9}) <br> {lista_PB9} </li>'
        s += "</ul>"
        s += "<h3>Produção técnica</h3> <ul>"
        s += f'<li id="PT0"> <b>{titulo_PT0}</b> ({nPT0}) <br> {lista_PT0} </li>'
        s += f'<li id="PT1"> <b>{titulo_PT1}</b> ({nPT1}) <br> {lista_PT1} </li>'
        s += f'<li id="PT2"> <b>{titulo_PT2}</b> ({nPT2}) <br> {lista_PT2} </li>'
        s += f'<li id="PT3"> <b>{titulo_PT3}</b> ({nPT3}) <br> {lista_PT3} </li>'
        s += f'<li id="PT4"> <b>{titulo_PT4}</b> ({nPT4}) <br> {lista_PT4} </li>'
        s += f'<li id="PT5"> <b>{titulo_PT5}</b> ({nPT5}) <br> {lista_PT5} </li>'
        s += "</ul>"
        s += "<h3>Produção artística</h3> <ul>"
        s += f'<li id="PA0"> <b>{titulo_PA0}</b> ({nPA0}) <br> {lista_PA0} </li>'
        s += "</ul>"
        s += "<h3>Orientações em andamento</h3> <ul>"
        s += f'<li id="OA0"> <b>{titulo_OA0}</b> ({nOA0}) <br> {lista_OA0} </li>'
        s += f'<li id="OA1"> <b>{titulo_OA1}</b> ({nOA1}) <br> {lista_OA1} </li>'
        s += f'<li id="OA2"> <b>{titulo_OA2}</b> ({nOA2}) <br> {lista_OA2} </li>'
        s += f'<li id="OA3"> <b>{titulo_OA3}</b> ({nOA3}) <br> {lista_OA3} </li>'
        s += f'<li id="OA4"> <b>{titulo_OA4}</b> ({nOA4}) <br> {lista_OA4} </li>'
        s += f'<li id="OA5"> <b>{titulo_OA5}</b> ({nOA5}) <br> {lista_OA5} </li>'
        s += f'<li id="OA6"> <b>{titulo_OA6}</b> ({nOA6}) <br> {lista_OA6} </li>'
        s += "</ul>"
        s += "<h3>Supervisões e orientações concluídas</h3> <ul>"
        s += f'<li id="OC0"> <b>{titulo_OC0}</b> ({nOC0}) <br> {lista_OC0} </li>'
        s += f'<li id="OC1"> <b>{titulo_OC1}</b> ({nOC1}) <br> {lista_OC1} </li>'
        s += f'<li id="OC2"> <b>{titulo_OC2}</b> ({nOC2}) <br> {lista_OC2} </li>'
        s += f'<li id="OC3"> <b>{titulo_OC3}</b> ({nOC3}) <br> {lista_OC3} </li>'
        s += f'<li id="OC4"> <b>{titulo_OC4}</b> ({nOC4}) <br> {lista_OC4} </li>'
        s += f'<li id="OC5"> <b>{titulo_OC5}</b> ({nOC5}) <br> {lista_OC5} </li>'
        s += f'<li id="OC6"> <b>{titulo_OC6}</b> ({nOC6}) <br> {lista_OC6} </li>'
        s += "</ul>"
        s += "<h3>Projetos de pesquisa</h3> <ul>"
        s += f'<li id="Pj0"> <b>{titulo_Pj0}</b> ({nPj0}) <br> {lista_Pj0} </li>'
        s += "</ul>"
        s += "<h3>Projetos de extensao</h3> <ul>"
        s += f'<li id="Pje0"> <b>{titulo_Pje0}</b> ({nPje0}) <br> {lista_Pje0} </li>'
        s += "</ul>"
        s += "<h3>Projetos de desenvolvimento</h3> <ul>"
        s += f'<li id="Pjd0"> <b>{titulo_Pjd0}</b> ({nPjd0}) <br> {lista_Pjd0} </li>'
        s += "<h3>Outros Projetos</h3> <ul>"
        s += f'<li id="Opj0"> <b>{titulo_Opj0}</b> ({nOpj0}) <br> {lista_Opj0} </li>'
        s += "</ul>"
        s += "<h3>Prêmios e títulos</h3> <ul>"
        s += f'<li id="Pm0"> <b>{titulo_Pm0}</b> ({nPm0}) <br> {lista_Pm0} </li>'
        s += "</ul>"
        s += "<h3>Participação em eventos</h3> <ul>"
        s += f'<li id="Ep0"> <b>{titulo_Ep0}</b> ({nEp0}) <br> {lista_Ep0} </li>'
        s += "</ul>"
        s += "<h3>Organização de eventos</h3> <ul>"
        s += f'<li id="Eo0"> <b>{titulo_Eo0}</b> ({nEo0}) <br> {lista_Eo0} </li>'
        s += "</ul>"
        s += "<h3>Lista de colaborações</h3> <ul>"
        s += f'<li id="CE"> <b>{titulo_CE}</b> ({nCE}) <br> {lista_CE_detalhe} </li>'
        s += "</ul>"

        s += self.paginaBottom()
        self.salvarPagina("membro-" + membro.idLattes + self.extensaoPagina, s)

    def gerar_lista_de_producoes_de_membro(self, lista, titulo):
        s = "<ol>"
        for publicacao in lista:
            s += "<li>" + publicacao.html(self.grupo.listaDeMembros)
        s += "</ol><br>"
        return (len(lista), s, titulo)

    def gerar_lista_de_colaboracoes(self, membro, titulo):
        s = "<ol>"
        detalhe = "<ul>"

        colaboradores = self.grupo.colaboradores_endogenos[membro.idMembro]
        for idColaborador, quantidade in sorted(
            colaboradores, key=lambda x: (-x[1], x[0])
        ):
            colaborador = self.grupo.listaDeMembros[idColaborador]
            s += (
                f'<li><a href="#{colaborador.idLattes}">'
                f"{colaborador.nomeCompleto}</a> ({quantidade})"
            )
            detalhe += (
                f'<li id="{colaborador.idLattes}"> <b>{membro.nomeCompleto} &hArr; '
                f'<a href="membro-{colaborador.idLattes}{self.extensaoPagina}">'
                f"{colaborador.nomeCompleto}</a></b> ({quantidade}) <ol>"
            )

            for publicacao in self.grupo.listaDeColaboracoes[membro.idMembro][
                idColaborador
            ]:
                detalhe += "<li>" + publicacao.html(self.grupo.listaDeMembros)

            detalhe += "</ol><br>"
        s += "</ol><br>"

        detalhe += "</ul><br>"
        return (len(colaboradores), s, titulo, detalhe)

    @staticmethod
    def producao_qualis_por_membro(lista_de_membros):
        # FIXME: ver um local melhor para este método

        producao_por_membro = pandas.DataFrame(
            columns=list(Membro.tabela_qualis.columns) + ["membro"]
        )

        for m in lista_de_membros:
            nome_membro = (
                unicodedata.normalize("NFKD", m.nomeCompleto)
                .encode("ASCII", "ignore")
                .decode()
            )
            df = pandas.DataFrame(
                {"membro": [nome_membro] * len(m.tabela_qualis)},
                index=m.tabela_qualis.index,
            )
            producao_por_membro = producao_por_membro.append(
                m.tabela_qualis.join(df), ignore_index=True
            )

        if producao_por_membro.empty:
            producao_por_membro_pivo = pandas.DataFrame()
        else:
            producao_por_membro_pivo = producao_por_membro.pivot_table(
                values="freq",
                columns=["ano", "estrato"],
                index=["area", "membro"],
                dropna=True,
                fill_value=0,
                margins=False,
                aggfunc=sum,
            )
        return producao_por_membro_pivo

    def gerar_pagina_de_producao_qualificado_por_membro(self):
        html = self.pagina_top()
        html += "<h3>Produção qualificado por área e membro</h3>"
        table_template = (
            '<table id="producao_por_membro" class="display nowrap">'
            "  <thead>{head}</thead>"
            "  <tfoot>{foot}</tfoot>"
            "  <tbody>{body}</tbody>"
            "</table>"
        )
        table_line_template = "<tr>{line}</tr>"

        first_column_template = '<td style="{extra_style}">{header}</td>'
        header_template = '<th colspan="{colspan}" {extra_pars}>{header}</th>'
        cell_template = '<td class="dt-body-center">{value}</td>'

        header_area = header_template.format(
            header="Área", colspan=1, extra_pars='rowspan="2"'
        )
        header_anos = header_template.format(header="Ano", colspan=1, extra_pars="")
        header_estratos = header_template.format(
            header="Membro \\ Estrato", colspan=1, extra_pars=""
        )

        footer = "<th>Área</th><th>Membro</th>"

        producao_por_membro = self.producao_qualis_por_membro(self.grupo.listaDeMembros)

        if producao_por_membro.empty:
            html += self.paginaBottom()
            self.salvarPagina("producao_membros" + self.extensaoPagina, html)
            return

        anos = sorted(producao_por_membro.columns.get_level_values("ano").unique())
        estratos = sorted(
            producao_por_membro.columns.get_level_values("estrato").unique()
        )

        for ano in anos:
            header_anos += header_template.format(
                header=int(ano), colspan=len(estratos), extra_pars=""
            )
            for estrato in estratos:
                header_estratos += header_template.format(
                    header=estrato, colspan=1, extra_pars=""
                )
                footer += '<th style="display: ;"></th>'

        first_row_header = table_line_template.format(line=header_area + header_anos)
        second_row_header = table_line_template.format(line=header_estratos)
        table_header = first_row_header + second_row_header

        table_footer = table_line_template.format(line=footer)

        areas = sorted(producao_por_membro.index.get_level_values("area").unique())
        membros = sorted(producao_por_membro.index.get_level_values("membro").unique())

        lines = ""
        for area in areas:
            line_area = first_column_template.format(header=area, extra_style="")
            for membro in membros:
                line = line_area
                line += cell_template.format(value=membro)
                for ano in anos:
                    for estrato in estratos:
                        try:
                            freq = producao_por_membro.ix[area, membro][ano, estrato]
                            # não mostrar zeros ou nulos
                            line += cell_template.format(
                                value=freq if freq else "&nbsp;"
                            )
                        except KeyError:
                            line += cell_template.format(value="&nbsp;")
                lines += table_line_template.format(line=line)

        table = table_template.format(head=table_header, body=lines, foot=table_footer)

        html += table

        html += """<script>
                  $(document).ready( function () {
                      var lastIdx = null;
                      var table = $("#producao_por_membro").DataTable({
                          "dom": 'C<"clear">lfrtip',
                          scrollX: true,
                          //scrollY: "400px",
                          //scrollCollapse: true,
                          paging: true,
                          stateSave: true,
                          initComplete: function () {
                              var api = this.api();
                              api.columns().indexes().flatten().each( function ( i ) {
                                  var column = api.column( i );
                                  var select = $('<select><option value=""></option></select>')
                                      .appendTo( $(column.footer()).empty() )
                                      .on( 'change', function () {
                                          var val = $.fn.dataTable.util.escapeRegex(
                                              $(this).val()
                                          );
                                          console.log(val);
                                          column
                                              .search( val ? '^'+val+'$' : '', true, false )
                                              .draw();
                                      } );
                                  column.data().unique().sort().each( function ( d, j ) {
                                      select.append( '<option value="'+d+'">'+d+'</option>' )
                                  } );
                              } );
                          },
                      });
                      $('#producao_por_membro tbody')
                              .on( 'mouseover', 'td', function () {
                                  var colIdx = table.cell(this).index().column;
                                  if ( colIdx !== lastIdx ) {
                                        $( table.cells().nodes() ).removeClass( 'highlight' );
                                        $( table.column( colIdx ).nodes() ).addClass( 'highlight' );
                                  }
                              } )
                              .on( 'mouseleave', function () {
                                  $( table.cells().nodes() ).removeClass( 'highlight' );
                              } );
                  });
                </script>"""

        # Salvar em planilha
        xls_filename = os.path.join(self.dir, "producao_membros.xls")
        producao_por_membro.to_excel(os.path.abspath(xls_filename))
        html += (
            f'<a href="{os.path.abspath(xls_filename)}">'
            f'{"Baixar planilha com os dados"}</a>'
        )

        html += self.paginaBottom()
        self.salvarPagina("producao_membros" + self.extensaoPagina, html)

    def pagina_top(self, cabecalho=""):
        nome_grupo = self.grupo.obterParametro("global-nome_do_grupo")

        s = self.html1
        template = (
            "<head>"
            '<meta http-equiv="Content-Type" content="text/html; charset=utf8">'
            '<meta name="Generator" content="scriptLattes">'
            "<title>{nome_grupo}</title>"
            '<link rel="stylesheet" href="css/scriptLattes.css" type="text/css">'
            '<link rel="stylesheet" type="text/css" href="css/jquery.dataTables.css">'
            '<link rel="stylesheet" type="text/css" '
            'href="css/dataTables.colVis.min.css">'
            '<script type="text/javascript" charset="utf8" src="js/jquery.min.js">'
            "</script>"
            '<script type="text/javascript" charset="utf8" '
            'src="js/jquery.dataTables.min.js"></script>'
            '<script type="text/javascript" charset="utf8" '
            'src="js/dataTables.colVis.min.js"></script>'
            '<script src="http://professor.ufabc.edu.br/~jesus.mena/sorttable.js">'
            "</script>"
            "{cabecalho}"
            "</head>"
            '<body><div id="header2"> <button onClick="history.go(-1)">Voltar</button>'
            "<h2>{nome_grupo}</h2></div>"
        )
        s += template.format(nome_grupo=nome_grupo, cabecalho=cabecalho)
        return s

    def paginaBottom(self):
        agora = datetime.datetime.now()
        dia = "0" + str(agora.day)
        mes = "0" + str(agora.month)
        ano = str(agora.year)
        hora = "0" + str(agora.hour)
        minuto = "0" + str(agora.minute)
        segundo = "0" + str(agora.second)

        dia = dia[-2:]
        mes = mes[-2:]
        hora = hora[-2:]
        minuto = minuto[-2:]
        segundo = segundo[-2:]
        data = dia + "/" + mes + "/" + ano + " " + hora + ":" + minuto + ":" + segundo

        s = "<br><p>"
        if (
            not self.grupo.obterParametro("global-itens_desde_o_ano") == ""
            and not self.grupo.obterParametro("global-itens_ate_o_ano") == ""
        ):
            s += (
                "<br>(*) Relatório criado com produções desde "
                + self.grupo.obterParametro("global-itens_desde_o_ano")
                + " até "
                + self.grupo.obterParametro("global-itens_ate_o_ano")
            )

        s += (
            "\n<br>Data de processamento: " + data + "<br>\n"
            '<div id="footer">\n'
            "Este arquivo foi gerado automaticamente por "
            '<a href="http://scriptlattes.sourceforge.net/">scriptLattes '
            + self.version
            + "</a>.\n"
            "Os resultados estão sujeitos a falhas devido a inconsistências "
            "no preenchimento dos currículos Lattes. "
            "Caso note alguma falha, por favor, contacte o responsável "
            "por esta página: "
            '<a href="mailto:'
            + self.grupo.obterParametro("global-email_do_admin")
            + '">'
            + self.grupo.obterParametro("global-email_do_admin")
            + "</a>\n"
            "</div> "
        )

        if self.grupo.obterParametro("global-google_analytics_key"):
            s += (
                '<script type="text/javascript">'
                'var gaJsHost = (("https:" == document.location.protocol) ? '
                '"https://ssl." : "http://www.");'
                'document.write(unescape("%3Cscript src=\'" + gaJsHost '
                "+ \"google-analytics.com/ga.js' "
                "type='text/javascript'%3E%3C/script%3E\"));"
                "</script>"
                '<script type="text/javascript">'
                "try {"
                'var pageTracker = _gat._getTracker("'
                + self.grupo.obterParametro("global-google_analytics_key")
                + '");'
                "pageTracker._trackPageview();"
                "} catch(err) {}"
                "</script>"
            )
        s += "</body>" + self.html2

        return s

    def salvarPagina(self, nome, conteudo):
        file = open(os.path.join(self.dir, nome), "w", encoding="utf-8")
        file.write(conteudo)
        file.close()

    def salvarPublicacaoEmFormatoRIS(self, pub):
        self.arquivoRis.write(pub.ris())

    def formatarTotaisQualis(self, qtd):
        st = (
            "(<b>A1</b>: "
            + str(qtd["A1"])
            + ", <b>A2</b>: "
            + str(qtd["A2"])
            + ", <b>A3</b>: "
            + str(qtd["A3"])
            + ", <b>A4</b>: "
            + str(qtd["A4"])
            + ", <b>B1</b>: "
            + str(qtd["B1"])
            + ", <b>B2</b>: "
            + str(qtd["B2"])
        )
        st += (
            ", <b>B3</b>: "
            + str(qtd["B3"])
            + ", <b>B4</b>: "
            + str(qtd["B4"])
            + ", <b>B5</b>: "
            + str(qtd["B5"])
            + ", <b>C</b>: "
            + str(qtd["C"])
        )
        st += (
            ", <b>Qualis n&atilde;o identificado</b>: "
            + str(qtd["Qualis nao identificado"])
            + ")"
        )
        st += "<br><p><b>Legenda Qualis:</b><ul>"
        st += (
            "<li> Publica&ccedil;&atilde;o para a qual o nome exato do Qualis foi "
            'identificado: <font color="#254117"><b>Qualis &lt;estrato&gt;</b></font>'
        )
        st += (
            "<li> Publica&ccedil;&atilde;o para a qual um nome similar "
            "(n&atilde;o exato) do Qualis foi identificado: "
            '<font color="#F88017"><b>Qualis &lt;estrato&gt;</b></font> (nome similar)'
        )
        st += (
            "<li> Publica&ccedil;&atilde;o para a qual nenhum nome do Qualis foi "
            'identificado: <font color="#FDD7E4"><b>Qualis n&atilde;o identificado</b>'
            "</font> (nome usado na busca)"
        )
        st += "</ul>"
        return st


def menuHTMLdeBuscaPB(titulo):
    titulo = re.sub("\\s+", "+", titulo)

    s = (
        '<br>\
         <font size=-1> \
         [ <a href="http://scholar.google.com/scholar?hl=en&lr=&q='
        + titulo
        + '&btnG=Search">cita&ccedil;&otilde;es Google Scholar</a> | \
           <a href="http://academic.research.microsoft.com/Search?query='
        + titulo
        + '">cita&ccedil;&otilde;es Microsoft Acad&ecirc;mico</a> | \
           <a href="http://www.google.com/search?btnG=Google+Search&q='
        + titulo
        + '">busca Google</a> ] \
         </font><br>'
    )
    return s


def menuHTMLdeBuscaPT(titulo):
    titulo = re.sub("\\s+", "+", titulo)

    s = (
        '<br>\
         <font size=-1> \
         [ <a href="http://www.google.com/search?btnG=Google+Search&q='
        + titulo
        + '">busca Google</a> | \
           <a href="http://www.bing.com/search?q='
        + titulo
        + '">busca Bing</a> ] \
         </font><br>'
    )
    return s


def menuHTMLdeBuscaPA(titulo):
    titulo = re.sub("\\s+", "+", titulo)

    s = (
        '<br>\
         <font size=-1> \
         [ <a href="http://www.google.com/search?btnG=Google+Search&q='
        + titulo
        + '">busca Google</a> | \
           <a href="http://www.bing.com/search?q='
        + titulo
        + '">busca Bing</a> ] \
         </font><br>'
    )
    return s


def formata_qualis(qualis, qualissimilar):
    s = ""
    if qualis is not None:
        if qualis == "":
            qualis = "Qualis nao identificado"

        if qualis == "Qualis nao identificado":
            # Qualis nao identificado - imprime em vermelho
            s += (
                '<font color="#FDD7E4"><b>Qualis: N&atilde;o identificado</b></font> ('
                + qualissimilar
                + ")"
            )
        else:
            if qualissimilar == "":
                # Casamento perfeito - imprime em verde
                s += '<font color="#254117"><b>Qualis: ' + qualis + "</b></font>"
            else:
                # Similar - imprime em laranja
                s += (
                    '<font color="#F88017"><b>Qualis: '
                    + qualis
                    + "</b></font> ("
                    + qualissimilar
                    + ")"
                )
    return s
