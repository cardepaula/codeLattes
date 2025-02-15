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
import shutil
import sys
import re
import Levenshtein

SEP = os.path.sep
BASE = "scriptLattes" + SEP
ABSBASE = os.path.abspath(".") + SEP


def buscarArquivo(filepath, arquivoConfiguracao=None):
    if not arquivoConfiguracao:
        arquivoConfiguracao = sys.argv[1]
    curdir = os.path.abspath(os.path.curdir)
    if not os.path.isfile(filepath) and arquivoConfiguracao:
        # vamos tentar mudar o diretorio para o atual do arquivo
        os.chdir(os.path.abspath(os.path.join(arquivoConfiguracao, os.pardir)))
    if not os.path.isfile(filepath):
        # se ainda nao existe, tentemos ver se o arquivo não está junto com o
        # config
        filepath = os.path.abspath(os.path.basename(filepath))
    else:
        # se encontramos, definimos então caminho absoluto
        filepath = os.path.abspath(filepath)
    os.chdir(curdir)
    return filepath


def copiarArquivos(dir):
    base = ABSBASE
    try:
        dst = os.path.join(dir, "css")
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(os.path.join(base, "css"), dst)
    except OSError as e:
        # provavelmente diretório já existe
        logging.warning(e)

    shutil.copy2(os.path.join(base, "imagens", "lattesPoint0.png"), dir)
    shutil.copy2(os.path.join(base, "imagens", "lattesPoint1.png"), dir)
    shutil.copy2(os.path.join(base, "imagens", "lattesPoint2.png"), dir)
    shutil.copy2(os.path.join(base, "imagens", "lattesPoint3.png"), dir)
    shutil.copy2(os.path.join(base, "imagens", "lattesPoint_shadow.png"), dir)
    shutil.copy2(os.path.join(base, "imagens", "doi.png"), dir)

    try:
        dst = os.path.join(dir, "images")
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(os.path.join(base, "images"), dst)
    except OSError as e:
        # provavelmente diretório já existe
        logging.warning(e)

    try:
        dst = os.path.join(dir, "js")
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(os.path.join(base, "js"), dst)
    except OSError as e:
        # provavelmente diretório já existe
        logging.warning(e)

    print(f"\n\nArquivos salvos em: >>{os.path.abspath(dir)}<<")


# ---------------------------------------------------------------------------- #
def similaridade_entre_cadeias(str1, str2, qualis=False):
    """
    Compara duas cadeias de caracteres e retorna a medida de similaridade entre elas,
    entre 0 e 1, onde 1 significa que as cadeias são idênticas ou uma é contida
    na outra.
    :param str1:
    :param str2:
    :param qualis:
    :return: A medida de similaridade entre as cadeias, de 0 a 1.
    """
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()

    # caso especial
    if (
        "apresentação" == str1
        or "apresentação" == str2
        or "apresentacao" == str1
        or "apresentacao" == str2
    ):
        return 0

    if len(str1) == 0 or len(str2) == 0:
        return 0

    if len(str1) >= 20 and len(str2) >= 20 and (str1 in str2 or str2 in str1):
        return 1

    if qualis:
        dist = Levenshtein.ratio(str1, str2)
        if len(str1) >= 10 and len(str2) >= 10 and dist >= 0.90:
            return dist

    else:
        if (
            len(str1) >= 10
            and len(str2) >= 10
            and Levenshtein.distance(str1, str2) <= 5
        ):
            return 1
    return 0


def criarDiretorio(dir):
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        # except OSError as exc:
        except BaseException:
            print(("\n[ERRO] Não foi possível criar ou atualizar o diretório: " + dir))
            print("[ERRO] Você conta com as permissões de escrita? \n")
            return 0
    return 1


# Combining Dictionaries Of Lists


def merge_dols(dol1, dol2):
    result = {}
    if len(dol1) > 0 and len(dol2) > 0:
        result = dol1 | dol2
        result.update((k, dol1[k] + dol2[k]) for k in set(dol1).intersection(dol2))
    elif len(dol1) > 0:
        result = dol1
    elif len(dol2) > 0:
        result = dol2
    return result


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
