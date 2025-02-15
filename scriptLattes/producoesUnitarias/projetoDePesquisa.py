#!/usr/bin/python
# encoding: utf-8
# filename: projetoDePesquisa.py
#
#  scriptLattes V8
#  Copyright 2005-2013: Jesús P. Mena-Chalco e Roberto M. Cesar-Jr.
#  http://scriptlattes.sourceforge.net/
#
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


import datetime

from scriptLattes.util import similaridade_entre_cadeias


class ProjetoDePesquisa:
    idMembro = None
    anoInicio = None
    anoConclusao = None
    nome = ""
    descricao = ""
    chave = None
    ano = None

    def __init__(self, idMembro, partesDoItem):
        # partesDoItem[0]: Periodo do projeto de pesquisa
        # partesDoItem[1]: cargo e titulo do projeto
        # partesDoItem[2]: Descricao (resto)

        self.idMembro = list([])
        self.idMembro.append(idMembro)

        anos = partesDoItem[0].partition("-")
        self.anoInicio = anos[0].strip()
        self.anoConclusao = anos[2].strip()
        self.nome = partesDoItem[1]

        self.descricao = list([])
        self.descricao.append(partesDoItem[2])

        self.chave = self.nome  # chave de comparação entre os objetos

        self.ano = self.anoInicio  # para comparação entre objetos

    def html(self, listaDeMembros):
        if self.anoConclusao == datetime.datetime.now().year:
            self.anoConclusao = "Atual"
        if self.anoInicio == 0 and self.anoConclusao == 0:
            s = '<span class="projects"> (*) </span> '
        else:
            s = (
                '<span class="projects">'
                + str(self.anoInicio)
                + "-"
                + str(self.anoConclusao)
                + "</span>. "
            )
        s += "<b>" + self.nome + "</b>"

        for i, id in enumerate(self.idMembro):
            s += "<br><i><font size=-1>" + self.descricao[i] + "</font></i>"
            m = listaDeMembros[id]
            s += (
                '<br><i><font size=-1>Membro: <a href="'
                + m.url
                + '">'
                + m.nomeCompleto
                + "</a>.</font>"
            )

        return s

    def compararCom(self, objeto):
        if set(self.idMembro).isdisjoint(
            set(objeto.idMembro)
        ) and similaridade_entre_cadeias(self.nome, objeto.nome):
            # Os IDs dos membros são agrupados.
            # Essa parte é importante para a geracao do relorio de projetos
            self.idMembro.extend(objeto.idMembro)

            # Apenas juntamos as descrições
            self.descricao.extend(objeto.descricao)

            return self
        return None  # nao similares

    # ------------------------------------------------------------------------ #

    def __str__(self):
        s = "\n[PROJETO DE PESQUISA] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+ANO INICIO  : " + str(self.anoInicio) + "\n"
        s += "+ANO CONCLUS.: " + str(self.anoConclusao) + "\n"
        s += "+NOME        : " + self.nome + "\n"
        s += "+DESCRICAO   : " + str(self.descricao) + "\n"
        return s
