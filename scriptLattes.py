#!/usr/bin/env python
# encoding: utf-8
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

import logging
import os
import sys
from scriptLattes.grupo import Grupo
from scriptLattes.util import criarDiretorio, copiarArquivos

if "win" in sys.platform.lower():
    os.environ["PATH"] += ";" + os.path.abspath(os.curdir + "\\Graphviz2.36\\bin")


def executar_scriptLattes(arquivoConfiguracao):
    novoGrupo = Grupo(arquivoConfiguracao)
    novoGrupo.imprimirListaDeRotulos()
    novoGrupo.carregar_dados_temporarios_de_geolocalizacao()

    if criarDiretorio(novoGrupo.obterParametro("global-diretorio_de_saida")):
        novoGrupo.carregarDadosCVLattes()  # obrigatorio
        novoGrupo.compilarListasDeItems()  # obrigatorio
        novoGrupo.identificarQualisEmPublicacoes()  # obrigatorio
        novoGrupo.calcularInternacionalizacao()  # obrigatorio

        novoGrupo.gerarGrafosDeColaboracoes()  # obrigatorio
        novoGrupo.gerarMapaDeGeolocalizacao()  # obrigatorio
        novoGrupo.gerarPaginasWeb()  # obrigatorio
        novoGrupo.gerarArquivosTemporarios()  # obrigatorio

        novoGrupo.salvar_dados_temporarios_de_geolocalizacao()

        copiarArquivos(novoGrupo.obterParametro("global-diretorio_de_saida"))

        print("\n\n[PARA REFERENCIAR/CITAR ESTE SOFTWARE USE]")
        print("    Jesus P. Mena-Chalco & Roberto M. Cesar-Jr.")
        print(
            "    scriptLattes: An open-source knowledge extraction system from the"
            " Lattes Platform."
        )
        print(
            "    Journal of the Brazilian Computer Society, vol.15, n.4, páginas"
            " 31-39, 2009."
        )
        print("    http://dx.doi.org/10.1007/BF03194511")
        print("\n\nscriptLattes executado!")

        # para incluir a producao com colaboradores é necessário um novo
        # chamado ao scriptLattes
        if novoGrupo.obterParametro("relatorio-incluir_producao_com_colaboradores"):
            executar_scriptLattes(
                novoGrupo.obterParametro("global-diretorio_de_saida")
                + "/producao-com-colaboradores.config"
            )


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(format="%(asctime)s - %(levelname)s (%(name)s) - %(message)s")
    logging.root.setLevel(level=logging.DEBUG)
    logger.info("Executando '%s'", " ".join(sys.argv))

    executar_scriptLattes(sys.argv[1])
