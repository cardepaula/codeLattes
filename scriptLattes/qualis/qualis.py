#!/usr/bin/python
# encoding: utf-8
# filename: qualis.py
#
# scriptLattes V8
# Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
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
from collections import defaultdict
import re
import fileinput

from scriptLattes.util import compararCadeias, buscarArquivo
from qualis_extractor import *


# def parar():
#     sys.stdin.read(1)


def padronizar_nome(nome):
    nome = nome.replace(u"\u00A0", " ")
    nome = nome.replace(u"\u2010", " ")
    nome = nome.replace(u"-", " ")

    # nome = re.sub(r"\(.*\)", " ", nome)
    # nome = re.sub(r"\(", " ", nome)
    # nome = re.sub(r"\)", " ", nome)
    nome = re.sub("\s+", ' ', nome)
    nome = nome.strip()
    return nome


def carregar_qualis_de_arquivo(arquivo):
    lista = {}
    if arquivo:
        arquivo = buscarArquivo(arquivo)

        for linha in fileinput.input(arquivo):
            linha = linha.replace("\r", "")
            linha = linha.replace("\n", "")

            campos = linha.split('\t')
            sigla = campos[0].rstrip().decode("utf8")  # ISSN de periodicos ou SIGLA de congressos
            nome = campos[1].rstrip().decode("utf8")  # Nome do periodico ou evento
            qualis = campos[2].rstrip()  # Estrato Qualis

            nome = padronizar_nome(nome)
            sigla = padronizar_nome(sigla)

            lista[nome] = qualis
            lista[sigla] = qualis  # Armazena a sigla/issn do evento/periodico

        print "[QUALIS]: " + str(len(lista)) + " itens adicionados de " + arquivo
    return lista


class Qualis:
    periodicos = {}
    congressos = {}
    qtdPB0 = {}  # Total de artigos em periodicos por Qualis
    qtdPB4 = {}  # Total de trabalhos completos em congressos por Qualis
    qtdPB5 = {}  # Total de resumos expandidos em congressos por Qualis

    '''
    arquivo_qualis_de_congressos: arquivo CSV de qualis de congressos # FIXME: só funciona para uma área
    data_file_path: arquivo cache de qualis extraídos anteriormente; é atualizado ao final da execução
    '''

    def __init__(self, search_online=True, data_file_path=None, arquivo_qualis_de_congressos=None,
                 arquivo_areas_qualis=None):

        # self.periodicos = self.carregar_qualis_de_arquivo(grupo.obterParametro('global-arquivo_qualis_de_periodicos'))
        # qualis extractor -> extrai qualis diretamente da busca online do qualis
        # self.extrair_qualis_online = grupo.obterParametro('global-extrair_qualis_online')
        # self.extrair_qualis_online = grupo.diretorioCache is not ''

        self.qextractor = qualis_extractor(search_online)

        self.qextractor.parse_areas_file(arquivo_areas_qualis)

        print "\n**************************************************\n"
        self.qextractor.load_data(data_file_path)
        # self.qextractor.extract_qualis()
        self.periodicos = self.qextractor.publicacao
        # self.qextractor.save_data(data_file_path)

        self.congressos = carregar_qualis_de_arquivo(arquivo_qualis_de_congressos)

    def analisar_publicacoes(self, membro):
        # Percorrer lista de publicacoes buscando e contabilizando os qualis
        for publicacao in membro.listaArtigoEmPeriodico:
            # qualis, similar = self.buscaQualis('P', pub.revista)
            # pub.qualis = qualis
            if publicacao.issn:
                publicacao.qualis = self.qextractor.get_qualis_by_issn(publicacao.issn)

            # FIXME: utilizaria o comportamento antigo (ler qualis de um CSV), mas nao funciona se a configuracao global-arquivo_qualis_de_periodicos nao for definida
            # elif not self.extrair_qualis_online:
            #     qualis, similar = self.buscaQualis('P', pub.revista)
            #     pub.qualis = qualis
            #     pub.qualissimilar = similar
            else:
                publicacao.qualis = None
                publicacao.qualissimilar = None

        membro.tabelaQualisDosAnos, membro.tabelaQualisDosTipos = self.qualis_por_ano(membro.listaArtigoEmPeriodico)

        if self.congressos:
            for pub in membro.listaTrabalhoCompletoEmCongresso:
                qualis, similar = self.busca_qualis_congressos(pub.nomeDoEvento)
                if not qualis:
                    if self.congressos.get(pub.sigla):
                        qualis = self.congressos.get(pub.sigla)  # Retorna Qualis da sigla com nome do evento
                        similar = pub.sigla
                    else:
                        qualis = 'Qualis não identificado'
                        similar = pub.nomeDoEvento
                pub.qualis = qualis
                pub.qualissimilar = similar

            for pub in membro.listaResumoExpandidoEmCongresso:
                qualis, similar = self.busca_qualis_congressos(pub.nomeDoEvento)
                pub.qualis = qualis if qualis else 'Qualis não identificado'
                pub.qualissimilar = similar

    def calcular_totais_dos_qualis(self, artigo_em_periodico, trabalho_completo_em_congresso,
                                resumo_expandido_em_congresso):
        # FIXME: publicacao.qualis tem tipo diferente (dict) do que antes (lista)
        # self.qtdPB0 = self.totais_dos_qualis_por_tipo(artigo_em_periodico)
        self.qtdPB4 = self.totais_dos_qualis_por_tipo(trabalho_completo_em_congresso)
        self.qtdPB5 = self.totais_dos_qualis_por_tipo(resumo_expandido_em_congresso)

    # FIXME: não usado; antigo método buscaQualis(tipo, nome)
    def busca_qualis_periodicos(self, nome):
        dist = 0
        indice = 0
        # Percorrer lista de periodicos tentando casar com nome usando funcao compararCadeias(str1, str2) de scriptLattes.py
        if self.periodicos.get(nome):
            return self.periodicos.get(nome), ''  # Retorna Qualis do nome exato encontrado - Casamento perfeito
        else:
            chaves = self.periodicos.keys()
            for i in range(0, len(chaves)):
                distI = compararCadeias(nome, chaves[i], qualis=True)
                if distI > dist:  # comparamos: nome com cada nome de periodico
                    indice = i
                    dist = distI
            if indice > 0:
                return self.periodicos.get(chaves[indice]), chaves[indice]  # Retorna Qualis de nome similar
        return None, None

    def busca_qualis_congressos(self, nome):
        # Percorrer lista de periodicos tentando casar com nome usando funcao compararCadeias(str1, str2) de scriptLattes.py
        if self.congressos.get(nome):
            return self.congressos.get(nome), ''  # Retorna Qualis do nome exato encontrado - Casamento perfeito
        else:
            similaridade, nome_congresso, qualis = max(
                (compararCadeias(nome, key, qualis=True), key, value) for key, value in self.congressos.items())
            if similaridade > 0:
                return qualis, nome_congresso
            return None, nome
            # Not very pythonic
            # chaves = self.congressos.keys()
            # dist = 0
            # indice = 0
            # for i in range(0, len(chaves)):
            #     distI = compararCadeias(nome, chaves[i], qualis=True)
            #     if distI > dist:  # comparamos: nome com cada nome de evento
            #         indice = i
            #         dist = distI
            # if indice > 0:
            #     return self.congressos.get(chaves[indice]), chaves[indice]  # Retorna Qualis de nome similar
            # return 'Qualis nao identificado', ''

    def totais_dos_qualis_por_tipo(self, lista_completa):
        qtd = defaultdict(int)
        for ano, publicacoes in lista_completa.items():
            for publicacao in publicacoes:
                qtd[publicacao.qualis] += 1
        return qtd

    # FIXME: não jogar a área fora; precisa para o gerador de páginas
    def qualis_por_ano(self, publicacoes):
        tabela_ano_tipo = defaultdict(lambda: defaultdict(int))  # dict[ano][tipo] = 0
        tabela_tipo = defaultdict(int)  # dict[tipo] = 0

        for publicacao in publicacoes:
            if publicacao.qualis:
                for tipo in publicacao.qualis.values():
                    tabela_ano_tipo[publicacao.ano][tipo] += 1
                    # valorAtual = self.getTiposPeloAno(publicacao.ano, tabelaDosAnos)[tipo]
                    # self.setValorPeloAnoTipo(publicacao.ano, tipo, valorAtual + 1, tabelaDosAnos)
                    tabela_tipo[tipo] += 1

        return (tabela_ano_tipo, tabela_tipo)


