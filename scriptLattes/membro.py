#!/usr/bin/python
#  encoding: utf-8
#
#
#  scriptLattes
#  Copyright http://scriptlattes.sourceforge.net/
#
#  Este programa é um software livre; você pode redistribui-lo e/ou
#  modifica-lo dentro dos termos da Licença Pública Geral GNU como
#  publicada pela Fundação do Software Livre (FSF); na versão 2 da
#  Licença, ou (na sua opinião) qualquer versão.
#
#  Este programa é distribuído na esperança que possa ser util,
#  mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
#  MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
#  Licença Pública Geral GNU para maiores detalhes.
#
#  Você deve ter recebido uma cópia da Licença Pública Geral GNU
#  junto com este programa, se não, escreva para a Fundação do Software
#  Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#

import datetime
import os
import re
import pandas
from lxml import etree
from .baixaLattes import baixaCVLattes
from .parserLattes import ParserLattes
from .parserLattesXML import ParserLattesXML
from .charts.geolocalizador import Geolocalizador


class Membro:
    idLattes = None  # ID Lattes
    idMembro = None
    rotulo = ""

    nomeInicial = ""
    nomeCompleto = ""
    sexo = ""
    nomeEmCitacoesBibliograficas = ""
    periodo = ""
    listaPeriodo = []
    bolsaProdutividade = ""
    enderecoProfissional = ""
    enderecoProfissionalLat = ""
    enderecoProfissionalLon = ""

    identificador10 = ""
    url = ""
    atualizacaoCV = ""
    foto = ""
    textoResumo = ""

    itemsDesdeOAno = ""  # periodo global
    itemsAteOAno = ""  # periodo global
    # diretorio de armazento de CVs (útil para extensas listas de CVs)
    diretorioCache = ""

    listaFormacaoAcademica = []
    listaProjetoDePesquisa = []
    listaProjetoDeExtensao = []
    listaProjetoDeDesenvolvimento = []
    listaOutrosProjetos = []
    listaAreaDeAtuacao = []
    listaIdioma = []
    listaPremioOuTitulo = []

    listaIDLattesColaboradores = []
    listaIDLattesColaboradoresUnica = []

    # Produção bibliográfica
    listaArtigoEmPeriodico = []
    listaLivroPublicado = []
    listaCapituloDeLivroPublicado = []
    listaTextoEmJornalDeNoticia = []
    listaTrabalhoCompletoEmCongresso = []
    listaResumoExpandidoEmCongresso = []
    listaResumoEmCongresso = []
    listaArtigoAceito = []
    listaApresentacaoDeTrabalho = []
    listaOutroTipoDeProducaoBibliografica = []

    # Produção técnica
    listaSoftwareComPatente = []
    listaSoftwareSemPatente = []
    listaProdutoTecnologico = []
    listaProcessoOuTecnica = []
    listaTrabalhoTecnico = []
    listaOutroTipoDeProducaoTecnica = []

    # Patentes e registros
    listaPatente = []
    listaProgramaComputador = []
    listaDesenhoIndustrial = []

    # Produção artística/cultural
    listaProducaoArtistica = []

    # Orientações em andamento
    listaOASupervisaoDePosDoutorado = []
    listaOATeseDeDoutorado = []
    listaOADissertacaoDeMestrado = []
    listaOAMonografiaDeEspecializacao = []
    listaOATCC = []
    listaOAIniciacaoCientifica = []
    listaOAOutroTipoDeOrientacao = []

    # Orientações concluídas
    listaOCSupervisaoDePosDoutorado = []
    listaOCTeseDeDoutorado = []
    listaOCDissertacaoDeMestrado = []
    listaOCMonografiaDeEspecializacao = []
    listaOCTCC = []
    listaOCIniciacaoCientifica = []
    listaOCOutroTipoDeOrientacao = []

    # Eventos
    listaParticipacaoEmEvento = []
    listaOrganizacaoDeEvento = []

    rotuloCorFG = ""
    rotuloCorBG = ""

    tabela_qualis = pandas.DataFrame(columns=["ano", "area", "estrato", "freq"])

    nomePrimeiraGrandeArea = ""
    nomePrimeiraArea = ""
    instituicao = ""

    dicionarioDeGeolocalizacao = None

    def __init__(
        self,
        idMembro,
        identificador,
        nome,
        periodo,
        rotulo,
        itemsDesdeOAno,
        itemsAteOAno,
        diretorioCache,
        dicionarioDeGeolocalizacao=None,
    ):
        self.idMembro = idMembro
        self.idLattes = identificador
        self.nomeInicial = nome
        self.nomeCompleto = nome.split(";")[0].strip()
        self.periodo = periodo
        self.rotulo = rotulo
        self.rotuloCorFG = "#000000"
        self.rotuloCorBG = "#FFFFFF"
        self.dicionarioDeGeolocalizacao = dicionarioDeGeolocalizacao

        p = re.compile("[a-zA-Z]+")

        if p.match(identificador):
            self.url = (
                "http://buscatextual.cnpq.br/buscatextual/visualizacv.do?id="
                + identificador
            )
        else:
            self.url = "http://lattes.cnpq.br/" + identificador

        self.itemsDesdeOAno = itemsDesdeOAno
        self.itemsAteOAno = itemsAteOAno
        self.criarListaDePeriodos(self.periodo)
        self.diretorioCache = diretorioCache

    def criarListaDePeriodos(self, periodoDoMembro):
        self.listaPeriodo = []
        periodoDoMembro = re.sub("\\s+", "", periodoDoMembro)

        if not periodoDoMembro:
            # se nao especificado o periodo, entao aceitamos todos os items do CV Lattes
            self.listaPeriodo = [[0, 10000]]
        else:
            lista = periodoDoMembro.split("&")
            for periodo in lista:
                ano1, _, ano2 = periodo.partition("-")

                if ano1.lower() == "hoje":
                    ano1 = str(datetime.datetime.now().year)
                if ano2.lower() == "hoje" or ano2 == "":
                    ano2 = str(datetime.datetime.now().year)

                if ano1.isdigit() and ano2.isdigit():
                    self.listaPeriodo.append([int(ano1), int(ano2)])
                else:
                    print(
                        "\n[AVISO IMPORTANTE] Periodo nao válido: "
                        f"{periodo}. (periodo desconsiderado na lista)"
                    )
                    print(
                        "[AVISO IMPORTANTE] CV Lattes: "
                        f"{self.idLattes}. Membro: {self.nomeInicial}\n"
                    )

    def carregarDadosCVLattes(self):
        cvPath = self.diretorioCache + "/" + self.idLattes

        if "xml" in cvPath:
            arquivoX = open(cvPath, encoding="utf-8")
            cvLattesXML = arquivoX.read()
            arquivoX.close()

            extended_chars = "".join(
                chr(c) for c in range(127, 65536, 1)
            )  # srange(r"[\0x80-\0x7FF]")
            special_chars = " -" ""
            # TODO Verificar se ocorrerá o ero "surrogates not allowed"
            # soluçao na linha 238
            cvLattesXML = (
                cvLattesXML.decode("iso-8859-1", "replace")
                + extended_chars
                + special_chars
            )
            parser = ParserLattesXML(self.idMembro, cvLattesXML)

            self.idLattes = parser.idLattes
            self.url = parser.url
            print(("(*) Utilizando CV armazenado no cache: " + cvPath))

        elif "0000000000000000" == self.idLattes:
            # se o codigo for '0000000000000000' então serao considerados dados de
            # pessoa estrangeira - sem Lattes.
            # sera procurada a coautoria endogena com os outros membro.
            # para isso é necessario indicar o nome abreviado no arquivo .list
            return

        else:
            if os.path.exists(cvPath):
                arquivoH = open(cvPath, encoding="utf-8")
                cvLattesHTML = arquivoH.read()

                if self.idMembro != "":
                    print(("(*) Utilizando CV armazenado no cache: " + cvPath))
            else:
                cvLattesHTML = baixaCVLattes(self.idLattes)
                if not self.diretorioCache == "":
                    file = open(cvPath, "w", encoding="utf-8")
                    file.write(cvLattesHTML)
                    file.close()
                    print(" (*) O CV está sendo armazenado no Cache")
            if cvLattesHTML == "   ":
                ##########################################
                # TODO verificar se o cache está vazio #
                ##########################################
                raise Exception("CV Lattes vazio")

            extended_chars = "".join(
                chr(c) for c in range(127, 65536, 1)
            )  # srange(r"[\0x80-\0x7FF]")
            special_chars = " -" ""
            extended_chars = extended_chars.encode("utf-8", "surrogatepass").decode(
                "utf-8", "replace"
            )
            cvLattesHTML = cvLattesHTML + extended_chars + special_chars
            # reference:
            # https://stackoverflow.com/questions/38147259/how-can-i-convert-surrogate-pairs-to-normal-string-in-python
            # https://bugs.python.org/issue26260
            # b'C\xc3N'.decode('utf8','replace')
            parser = ParserLattes(self.idMembro, cvLattesHTML)

            p = re.compile("[a-zA-Z]+")
            if p.match(self.idLattes):
                self.identificador10 = self.idLattes
                self.idLattes = parser.identificador16
                self.url = "http://lattes.cnpq.br/" + self.idLattes

        # Obtemos todos os dados do CV Lattes
        self.nomeCompleto = parser.nomeCompleto
        self.bolsaProdutividade = parser.bolsaProdutividade
        self.enderecoProfissional = parser.enderecoProfissional
        self.sexo = parser.sexo
        self.nomeEmCitacoesBibliograficas = parser.nomeEmCitacoesBibliograficas
        self.atualizacaoCV = parser.atualizacaoCV
        self.textoResumo = parser.textoResumo
        self.foto = parser.foto

        self.listaIDLattesColaboradores = parser.listaIDLattesColaboradores
        self.listaFormacaoAcademica = parser.listaFormacaoAcademica
        self.listaProjetoDePesquisa = parser.listaProjetoDePesquisa
        self.listaProjetoDeExtensao = parser.listaProjetoDeExtensao
        self.listaProjetoDeDesenvolvimento = parser.listaProjetoDeDesenvolvimento
        self.listaOutrosProjetos = parser.listaOutrosProjetos
        self.listaAreaDeAtuacao = parser.listaAreaDeAtuacao
        self.listaIdioma = parser.listaIdioma
        self.listaPremioOuTitulo = parser.listaPremioOuTitulo
        self.listaIDLattesColaboradoresUnica = set(self.listaIDLattesColaboradores)

        # Produção bibliográfica
        self.listaArtigoEmPeriodico = parser.listaArtigoEmPeriodico
        self.listaLivroPublicado = parser.listaLivroPublicado
        self.listaCapituloDeLivroPublicado = parser.listaCapituloDeLivroPublicado
        self.listaTextoEmJornalDeNoticia = parser.listaTextoEmJornalDeNoticia
        self.listaTrabalhoCompletoEmCongresso = parser.listaTrabalhoCompletoEmCongresso
        self.listaResumoExpandidoEmCongresso = parser.listaResumoExpandidoEmCongresso
        self.listaResumoEmCongresso = parser.listaResumoEmCongresso
        self.listaArtigoAceito = parser.listaArtigoAceito
        self.listaApresentacaoDeTrabalho = parser.listaApresentacaoDeTrabalho
        self.listaOutroTipoDeProducaoBibliografica = (
            parser.listaOutroTipoDeProducaoBibliografica
        )

        # Produção técnica
        self.listaSoftwareComPatente = parser.listaSoftwareComPatente
        self.listaSoftwareSemPatente = parser.listaSoftwareSemPatente
        self.listaProdutoTecnologico = parser.listaProdutoTecnologico
        self.listaProcessoOuTecnica = parser.listaProcessoOuTecnica
        self.listaTrabalhoTecnico = parser.listaTrabalhoTecnico
        self.listaOutroTipoDeProducaoTecnica = parser.listaOutroTipoDeProducaoTecnica

        # Patentes e registros
        self.listaPatente = parser.listaPatente
        self.listaProgramaComputador = parser.listaProgramaComputador
        self.listaDesenhoIndustrial = parser.listaDesenhoIndustrial

        # Produção artística
        self.listaProducaoArtistica = parser.listaProducaoArtistica

        # Orientações em andamento
        self.listaOASupervisaoDePosDoutorado = parser.listaOASupervisaoDePosDoutorado
        self.listaOATeseDeDoutorado = parser.listaOATeseDeDoutorado
        self.listaOADissertacaoDeMestrado = parser.listaOADissertacaoDeMestrado
        self.listaOAMonografiaDeEspecializacao = (
            parser.listaOAMonografiaDeEspecializacao
        )
        self.listaOATCC = parser.listaOATCC
        self.listaOAIniciacaoCientifica = parser.listaOAIniciacaoCientifica
        self.listaOAOutroTipoDeOrientacao = parser.listaOAOutroTipoDeOrientacao

        # Orientações concluídas
        self.listaOCSupervisaoDePosDoutorado = parser.listaOCSupervisaoDePosDoutorado
        self.listaOCTeseDeDoutorado = parser.listaOCTeseDeDoutorado
        self.listaOCDissertacaoDeMestrado = parser.listaOCDissertacaoDeMestrado
        self.listaOCMonografiaDeEspecializacao = (
            parser.listaOCMonografiaDeEspecializacao
        )
        self.listaOCTCC = parser.listaOCTCC
        self.listaOCIniciacaoCientifica = parser.listaOCIniciacaoCientifica
        self.listaOCOutroTipoDeOrientacao = parser.listaOCOutroTipoDeOrientacao

        # Eventos
        self.listaParticipacaoEmEvento = parser.listaParticipacaoEmEvento
        self.listaOrganizacaoDeEvento = parser.listaOrganizacaoDeEvento

        nomePrimeiraGrandeArea = ""
        nomePrimeiraArea = ""

        if len(self.listaAreaDeAtuacao) > 0:
            descricao = self.listaAreaDeAtuacao[0].descricao
            partes = descricao.split("/")
            nomePrimeiraGrandeArea = partes[0]
            nomePrimeiraGrandeArea = nomePrimeiraGrandeArea.replace(
                "Grande área:", ""
            ).strip()

            if len(partes) > 1:
                partes = partes[1].split(":")
                partes = partes[1].strip()
                nomePrimeiraArea = partes
                nomePrimeiraArea = nomePrimeiraArea.strip(".")
                nomePrimeiraArea = nomePrimeiraArea.replace("Especialidade", "")
        else:
            nomePrimeiraGrandeArea = "[sem-grandeArea]"
            nomePrimeiraArea = "[sem-area]"

        self.nomePrimeiraGrandeArea = nomePrimeiraGrandeArea
        self.nomePrimeiraArea = nomePrimeiraArea

        if len(self.enderecoProfissional) > 0:
            instituicao = self.enderecoProfissional.split(".")[0]
            self.instituicao = instituicao.replace("'", "")

    def filtrarItemsPorPeriodo(self):
        self.listaArtigoEmPeriodico = self.filtrarItems(self.listaArtigoEmPeriodico)
        self.listaLivroPublicado = self.filtrarItems(self.listaLivroPublicado)
        self.listaCapituloDeLivroPublicado = self.filtrarItems(
            self.listaCapituloDeLivroPublicado
        )
        self.listaTextoEmJornalDeNoticia = self.filtrarItems(
            self.listaTextoEmJornalDeNoticia
        )
        self.listaTrabalhoCompletoEmCongresso = self.filtrarItems(
            self.listaTrabalhoCompletoEmCongresso
        )
        self.listaResumoExpandidoEmCongresso = self.filtrarItems(
            self.listaResumoExpandidoEmCongresso
        )
        self.listaResumoEmCongresso = self.filtrarItems(self.listaResumoEmCongresso)
        self.listaArtigoAceito = self.filtrarItems(self.listaArtigoAceito)
        self.listaApresentacaoDeTrabalho = self.filtrarItems(
            self.listaApresentacaoDeTrabalho
        )
        self.listaOutroTipoDeProducaoBibliografica = self.filtrarItems(
            self.listaOutroTipoDeProducaoBibliografica
        )

        self.listaSoftwareComPatente = self.filtrarItems(self.listaSoftwareComPatente)
        self.listaSoftwareSemPatente = self.filtrarItems(self.listaSoftwareSemPatente)
        self.listaProdutoTecnologico = self.filtrarItems(self.listaProdutoTecnologico)
        self.listaProcessoOuTecnica = self.filtrarItems(self.listaProcessoOuTecnica)
        self.listaTrabalhoTecnico = self.filtrarItems(self.listaTrabalhoTecnico)
        self.listaOutroTipoDeProducaoTecnica = self.filtrarItems(
            self.listaOutroTipoDeProducaoTecnica
        )

        self.listaPatente = self.filtrarItems(self.listaPatente)
        self.listaProgramaComputador = self.filtrarItems(self.listaProgramaComputador)
        self.listaDesenhoIndustrial = self.filtrarItems(self.listaDesenhoIndustrial)

        self.listaProducaoArtistica = self.filtrarItems(self.listaProducaoArtistica)

        self.listaOASupervisaoDePosDoutorado = self.filtrarItems(
            self.listaOASupervisaoDePosDoutorado
        )
        self.listaOATeseDeDoutorado = self.filtrarItems(self.listaOATeseDeDoutorado)
        self.listaOADissertacaoDeMestrado = self.filtrarItems(
            self.listaOADissertacaoDeMestrado
        )
        self.listaOAMonografiaDeEspecializacao = self.filtrarItems(
            self.listaOAMonografiaDeEspecializacao
        )
        self.listaOATCC = self.filtrarItems(self.listaOATCC)
        self.listaOAIniciacaoCientifica = self.filtrarItems(
            self.listaOAIniciacaoCientifica
        )
        self.listaOAOutroTipoDeOrientacao = self.filtrarItems(
            self.listaOAOutroTipoDeOrientacao
        )

        self.listaOCSupervisaoDePosDoutorado = self.filtrarItems(
            self.listaOCSupervisaoDePosDoutorado
        )
        self.listaOCTeseDeDoutorado = self.filtrarItems(self.listaOCTeseDeDoutorado)
        self.listaOCDissertacaoDeMestrado = self.filtrarItems(
            self.listaOCDissertacaoDeMestrado
        )
        self.listaOCMonografiaDeEspecializacao = self.filtrarItems(
            self.listaOCMonografiaDeEspecializacao
        )
        self.listaOCTCC = self.filtrarItems(self.listaOCTCC)
        self.listaOCIniciacaoCientifica = self.filtrarItems(
            self.listaOCIniciacaoCientifica
        )
        self.listaOCOutroTipoDeOrientacao = self.filtrarItems(
            self.listaOCOutroTipoDeOrientacao
        )

        self.listaPremioOuTitulo = self.filtrarItems(self.listaPremioOuTitulo)
        self.listaProjetoDePesquisa = self.filtrarItems(self.listaProjetoDePesquisa)
        self.listaProjetoDeExtensao = self.filtrarItems(self.listaProjetoDeExtensao)
        self.listaProjetoDeDesenvolvimento = self.filtrarItems(
            self.listaProjetoDeDesenvolvimento
        )
        self.listaOutrosProjetos = self.filtrarItems(self.listaOutrosProjetos)

        self.listaParticipacaoEmEvento = self.filtrarItems(
            self.listaParticipacaoEmEvento
        )
        self.listaOrganizacaoDeEvento = self.filtrarItems(self.listaOrganizacaoDeEvento)

    def filtrarItems(self, lista):
        return list(filter(self.estaDentroDoPeriodo, lista))

    def estaDentroDoPeriodo(self, objeto):
        if objeto.__module__ == "orientacaoEmAndamento":
            objeto.ano = int(objeto.ano) if objeto.ano else 0
            return 1 if objeto.ano <= self.itemsAteOAno else 0

        if objeto.__module__ in [
            "projetoDePesquisa",
            "projetoDeExtensao",
            "projetoDeDesenvolvimento",
            "outrosProjetos",
        ]:
            if objeto.anoConclusao.lower() == "atual":
                objeto.anoConclusao = str(datetime.datetime.now().year)

            if not objeto.anoInicio:
                objeto.anoInicio = "0"
            if not objeto.anoConclusao:
                objeto.anoConclusao = "0"

            objeto.anoInicio = int(objeto.anoInicio)
            objeto.anoConclusao = int(objeto.anoConclusao)
            objeto.ano = objeto.anoInicio

            if (
                objeto.anoInicio > self.itemsAteOAno
                and objeto.anoConclusao > self.itemsAteOAno
                or objeto.anoInicio < self.itemsDesdeOAno
                and objeto.anoConclusao < self.itemsDesdeOAno
            ):
                return 0

            for periodo in self.listaPeriodo:
                if (
                    objeto.anoInicio > periodo[1]
                    and objeto.anoConclusao > periodo[1]
                    or objeto.anoInicio < periodo[0]
                    and objeto.anoConclusao < periodo[0]
                ):
                    continue
                return 1
            return 0

        if not objeto.ano or not objeto.ano.isdigit():
            objeto.ano = 0
            return 1

        objeto.ano = int(objeto.ano)
        if self.itemsDesdeOAno > objeto.ano or objeto.ano > self.itemsAteOAno:
            return 0

        return any(
            periodo[0] <= objeto.ano <= periodo[1] for periodo in self.listaPeriodo
        )

    def obterCoordenadasDeGeolocalizacao(self):
        geo = Geolocalizador(self.enderecoProfissional, self.dicionarioDeGeolocalizacao)
        self.enderecoProfissionalLat = geo.lat
        self.enderecoProfissionalLon = geo.lon

    def ris(self):
        s = ""
        s += "\nTY  - MEMBRO"
        s += "\nNOME  - " + self.nomeCompleto
        s += "\nCITA  - " + self.nomeEmCitacoesBibliograficas
        s += "\nBOLS  - " + self.bolsaProdutividade
        s += "\nENDE  - " + self.enderecoProfissional
        s += "\nURLC  - " + self.url
        s += "\nDATA  - " + self.atualizacaoCV
        s += "\nRESU  - " + self.textoResumo

        for i, formacao in enumerate(self.listaFormacaoAcademica):
            s += "\nFO" + str(i + 1) + "a  - " + formacao.anoInicio
            s += "\nFO" + str(i + 1) + "b  - " + formacao.anoConclusao
            s += "\nFO" + str(i + 1) + "c  - " + formacao.tipo
            s += "\nFO" + str(i + 1) + "d  - " + formacao.nomeInstituicao
            s += "\nFO" + str(i + 1) + "e  - " + formacao.descricao

        for i, area in enumerate(self.listaAreaDeAtuacao):
            s += "\nARE" + str(i + 1) + "  - " + area.descricao

        for i, idioma in enumerate(self.listaIdioma):
            s += "\nID" + str(i + 1) + "a  - " + idioma.nome
            s += "\nID" + str(i + 1) + "b  - " + idioma.proficiencia

        return s

    def __str__(self):
        verbose = 0

        s = "+ ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+ ROTULO      : " + self.rotulo + "\n"
        s += "+ NOME REAL   : " + self.nomeCompleto + "\n"

        if verbose:
            s += "\n[COLABORADORES]"
            for idColaborador in self.listaIDLattesColaboradoresUnica:
                s += "\n+ " + idColaborador

        else:
            s += "\n- Numero de colaboradores (identificado)      : " + str(
                len(self.listaIDLattesColaboradoresUnica)
            )
            s += "\n- Artigos completos publicados em periódicos  : " + str(
                len(self.listaArtigoEmPeriodico)
            )
            s += "\n- Livros publicados/organizados ou edições    : " + str(
                len(self.listaLivroPublicado)
            )
            s += "\n- Capítulos de livros publicados              : " + str(
                len(self.listaCapituloDeLivroPublicado)
            )
            s += "\n- Textos em jornais de notícias/revistas      : " + str(
                len(self.listaTextoEmJornalDeNoticia)
            )
            s += "\n- Trabalhos completos publicados em congressos: " + str(
                len(self.listaTrabalhoCompletoEmCongresso)
            )
            s += "\n- Resumos expandidos publicados em congressos : " + str(
                len(self.listaResumoExpandidoEmCongresso)
            )
            s += "\n- Resumos publicados em anais de congressos   : " + str(
                len(self.listaResumoEmCongresso)
            )
            s += "\n- Artigos aceitos para publicação             : " + str(
                len(self.listaArtigoAceito)
            )
            s += "\n- Apresentações de Trabalho                   : " + str(
                len(self.listaApresentacaoDeTrabalho)
            )
            s += "\n- Demais tipos de produção bibliográfica      : " + str(
                len(self.listaOutroTipoDeProducaoBibliografica)
            )
            s += "\n- Softwares com registro de patente           : " + str(
                len(self.listaSoftwareComPatente)
            )
            s += "\n- Softwares sem registro de patente           : " + str(
                len(self.listaSoftwareSemPatente)
            )
            s += "\n- Produtos tecnológicos                       : " + str(
                len(self.listaProdutoTecnologico)
            )
            s += "\n- Processos ou técnicas                       : " + str(
                len(self.listaProcessoOuTecnica)
            )
            s += "\n- Trabalhos técnicos                          : " + str(
                len(self.listaTrabalhoTecnico)
            )
            s += "\n- Demais tipos de produção técnica            : " + str(
                len(self.listaOutroTipoDeProducaoTecnica)
            )
            s += "\n- Patente                                     : " + str(
                len(self.listaPatente)
            )
            s += "\n- Programa de computador                      : " + str(
                len(self.listaProgramaComputador)
            )
            s += "\n- Desenho industrial                          : " + str(
                len(self.listaDesenhoIndustrial)
            )
            s += "\n- Produção artística/cultural                 : " + str(
                len(self.listaProducaoArtistica)
            )
            s += "\n- Orientações em andamento"
            s += "\n  . Supervições de pos doutorado              : " + str(
                len(self.listaOASupervisaoDePosDoutorado)
            )
            s += "\n  . Tese de doutorado                         : " + str(
                len(self.listaOATeseDeDoutorado)
            )
            s += "\n  . Dissertações de mestrado                  : " + str(
                len(self.listaOADissertacaoDeMestrado)
            )
            s += "\n  . Monografías de especialização             : " + str(
                len(self.listaOAMonografiaDeEspecializacao)
            )
            s += "\n  . TCC                                       : " + str(
                len(self.listaOATCC)
            )
            s += "\n  . Iniciação científica                      : " + str(
                len(self.listaOAIniciacaoCientifica)
            )
            s += "\n  . Orientações de outra natureza             : " + str(
                len(self.listaOAOutroTipoDeOrientacao)
            )
            s += "\n- Orientações concluídas"
            s += "\n  . Supervições de pos doutorado              : " + str(
                len(self.listaOCSupervisaoDePosDoutorado)
            )
            s += "\n  . Tese de doutorado                         : " + str(
                len(self.listaOCTeseDeDoutorado)
            )
            s += "\n  . Dissertações de mestrado                  : " + str(
                len(self.listaOCDissertacaoDeMestrado)
            )
            s += "\n  . Monografías de especialização             : " + str(
                len(self.listaOCMonografiaDeEspecializacao)
            )
            s += "\n  . TCC                                       : " + str(
                len(self.listaOCTCC)
            )
            s += "\n  . Iniciação científica                      : " + str(
                len(self.listaOCIniciacaoCientifica)
            )
            s += "\n  . Orientações de outra natureza             : " + str(
                len(self.listaOCOutroTipoDeOrientacao)
            )
            s += "\n- Projetos de pesquisa                        : " + str(
                len(self.listaProjetoDePesquisa)
            )
            s += "\n- Projetos de extensão                        : " + str(
                len(self.listaProjetoDeExtensao)
            )
            s += "\n- Projetos de desenvolvimento                 : " + str(
                len(self.listaProjetoDeDesenvolvimento)
            )
            s += "\n- Outros Projetos                             : " + str(
                len(self.listaOutrosProjetos)
            )
            s += "\n- Prêmios e títulos                           : " + str(
                len(self.listaPremioOuTitulo)
            )
            s += "\n- Participação em eventos                     : " + str(
                len(self.listaParticipacaoEmEvento)
            )
            s += "\n- Organização de eventos                      : " + str(
                len(self.listaOrganizacaoDeEvento)
            )
            s += "\n\n"
        return s
