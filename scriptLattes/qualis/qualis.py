#!/usr/bin/python
# encoding: utf-8
#
#
# scriptLattes V8
# http://scriptlattes.sourceforge.net/
# Pacote desenvolvido por Helena Caseli
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

import logging
import re
import fileinput
from scriptLattes.util import similaridade_entre_cadeias

logger = logging.getLogger(__name__)


class Qualis:
    periodicos = {}
    congressos = {}
    qtdPB0 = {}  # Total de artigos em periodicos por Qualis
    qtdPB4 = {}  # Total de trabalhos completos em congressos por Qualis
    qtdPB5 = {}  # Total de resumos expandidos em congressos por Qualis
    qtdPB7 = {}  # Total de artigos aceitos para publicacao por Qualis

    def __init__(self, grupo):
        if grupo.obterParametro("global-identificar_publicacoes_com_qualis"):
            self.periodicos = self.carregarQualis(
                grupo.obterParametro("global-arquivo_qualis_de_periodicos")
            )
            self.congressos = self.carregarQualis(
                grupo.obterParametro("global-arquivo_qualis_de_congressos")
            )

    def calcularTotaisDosQualis(self, grupo):
        if not grupo.obterParametro("global-arquivo_qualis_de_periodicos") == "":
            self.qtdPB0 = self.calcularTotaisDosQualisPorTipo(
                self.qtdPB0, grupo.compilador.listaCompletaArtigoEmPeriodico
            )
            self.qtdPB7 = self.calcularTotaisDosQualisPorTipo(
                self.qtdPB7, grupo.compilador.listaCompletaArtigoAceito
            )
        if not grupo.obterParametro("global-arquivo_qualis_de_congressos") == "":
            self.qtdPB4 = self.calcularTotaisDosQualisPorTipo(
                self.qtdPB4, grupo.compilador.listaCompletaTrabalhoCompletoEmCongresso
            )
            self.qtdPB5 = self.calcularTotaisDosQualisPorTipo(
                self.qtdPB5, grupo.compilador.listaCompletaResumoExpandidoEmCongresso
            )

    def calcularTotaisDosQualisPorTipo(self, qtd, listaCompleta):
        self.inicializaListaQualis(qtd)
        keys = list(listaCompleta.keys())
        if len(keys) > 0:
            for ano in keys:
                elementos = listaCompleta[ano]
                for pub in elementos:
                    qtd[pub.qualis] += 1
        return qtd

    def buscaQualis(self, tipo, nome, sigla=""):
        dist = 0
        indice = 0
        # Percorrer lista de periodicos tentando casar com nome usando funcao
        # similaridade_entre_cadeias(str1, str2) de scriptLattes.py
        if tipo == "P":
            if self.periodicos.get(sigla) is not None:
                # Retorna Qualis do issn/sigla exato encontrado - Casamento
                # perfeito
                return self.periodicos.get(sigla), ""

            if self.periodicos.get(nome) is not None:
                # Retorna Qualis do nome exato encontrado - Casamento perfeito
                return self.periodicos.get(nome), ""

            chaves = list(self.periodicos.keys())
            for i, chave in enumerate(chaves):
                distI = similaridade_entre_cadeias(nome, chave, qualis=True)
                if distI > dist:  # comparamos: nome com cada nome de periodico
                    indice = i
                    dist = distI
            if indice > 0:
                # Retorna Qualis de nome similar
                return self.periodicos.get(chaves[indice]), chaves[indice]
        else:
            if self.congressos.get(nome) is not None:
                # Retorna Qualis do nome exato encontrado - Casamento perfeito
                return self.congressos.get(nome), ""

            chaves = list(self.congressos.keys())
            for i, chave in enumerate(chaves):
                distI = similaridade_entre_cadeias(nome, chave, qualis=True)
                if distI > dist:  # comparamos: nome com cada nome de evento
                    indice = i
                    dist = distI
            if indice > 0:
                # Retorna Qualis de nome similar
                return self.congressos.get(chaves[indice]), chaves[indice]
        # return 'Qualis nao identificado', ''
        return "Qualis nao identificado", nome

    def analisarPublicacoes(self, membro, grupo):
        # Percorrer lista de publicacoes buscando e contabilizando os qualis
        if not grupo.obterParametro("global-arquivo_qualis_de_periodicos") == "":
            for pub in membro.listaArtigoEmPeriodico:
                qualis, similar = self.buscaQualis("P", pub.revista, pub.issn)
                pub.qualis = qualis
                pub.qualissimilar = similar
            for pub in membro.listaArtigoAceito:
                qualis, similar = self.buscaQualis("P", pub.revista, pub.issn)
                pub.qualis = qualis
                pub.qualissimilar = similar

        if not grupo.obterParametro("global-arquivo_qualis_de_congressos") == "":
            for pub in membro.listaTrabalhoCompletoEmCongresso:
                qualis, similar = self.buscaQualis("C", pub.nomeDoEvento)
                if qualis == "Qualis nao identificado":
                    if self.congressos.get(pub.sigla) is not None:
                        # Retorna Qualis da sigla com nome do evento
                        qualis = self.congressos.get(pub.sigla)
                        similar = pub.sigla
                    else:
                        qualis = "Qualis nao identificado"
                        similar = pub.nomeDoEvento
                pub.qualis = qualis
                pub.qualissimilar = similar

            for pub in membro.listaResumoExpandidoEmCongresso:
                qualis, similar = self.buscaQualis("C", pub.nomeDoEvento)
                pub.qualis = qualis
                pub.qualissimilar = similar

    def inicializaListaQualis(self, lista):
        lista["A1"] = 0
        lista["A2"] = 0
        lista["A3"] = 0
        lista["A4"] = 0
        lista["B1"] = 0
        lista["B2"] = 0
        lista["B3"] = 0
        lista["B4"] = 0
        lista["B5"] = 0
        lista["C"] = 0
        lista["Qualis nao identificado"] = 0

    def carregarQualis(self, arquivo):
        lista = {}
        if not arquivo == "":
            for linha in fileinput.input(arquivo):
                linha = linha.replace("\r", "")
                linha = linha.replace("\n", "")

                campos = linha.split("\t")
                # ISSN de periodicos ou SIGLA de congressos
                sigla = campos[0].rstrip()
                # Nome do periodico ou evento
                nome = campos[1].rstrip()
                qualis = campos[2].rstrip()  # Estrato Qualis
                sigla = sigla.replace("-", "")

                lista[nome] = qualis
                # Armazena a sigla/issn do evento/periodico
                lista[sigla] = qualis
            print(("[QUALIS]: " + str(len(lista)) + " itens adicionados de " + arquivo))
        return lista

    def padronizarNome(self, nome):
        nome = nome.replace("\\u00A0", "")
        nome = nome.replace("\\u2010", "")
        nome = nome.replace("-", "")
        nome = re.sub("\\s+", " ", nome)
        nome = nome.strip()
        return nome
