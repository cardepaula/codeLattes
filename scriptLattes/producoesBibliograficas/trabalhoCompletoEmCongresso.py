#!/usr/bin/python
# encoding: utf-8
#
#
# scriptLattes
# http://scriptlattes.sourceforge.net/
#
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

import re
import logging
from scriptLattes.util import (
    similaridade_entre_cadeias,
    menuHTMLdeBuscaPB,
    formata_qualis,
)

logger = logging.getLogger("scriptLattes")


class TrabalhoCompletoEmCongresso:
    item = None  # dado bruto
    idMembro = None
    qualis = None
    qualissimilar = None

    doi = None
    relevante = None
    autores = None
    titulo = None
    nomeDoEvento = None
    ano = None
    volume = None
    paginas = None
    chave = None

    sigla = None  # Qualis

    def __init__(self, idMembro, partesDoItem="", doi="", relevante=""):
        self.idMembro = set([])
        self.idMembro.add(idMembro)

        if partesDoItem != "":
            # partesDoItem[0]: Numero (NAO USADO)
            # partesDoItem[1]: Descricao do livro (DADO BRUTO)

            self.item = partesDoItem[1]
            self.doi = doi
            self.relevante = relevante

            # Dividir o item na suas partes constituintes (autores e o resto)
            if " . " in self.item:
                partes = self.item.partition(" . ")
            elif ".. " in self.item:
                partes = self.item.partition(".. ")
            else:
                partes = self.item.partition(". ")

            # Verificar quando há um numero de autores > que 25
            # muitos autores (mais de 25) e o lattes insere etal. termina lista
            # com ;
            if partes[1] == "":
                partes = self.item.partition(" ; ")
                a = partes[0].partition(", et al.")  # remocao do et al.
                # estes autores nao estao bem separados pois falta ';'
                a = a[0] + a[2]
                b = a.replace(", ", "*")
                c = b.replace(" ", " ; ")
                self.autores = c.replace("*", ", ")
            else:
                self.autores = partes[0].strip()

            # Processando o resto (tudo menos autores)
            partes = partes[2]

            partes = partes.rpartition(" p. ")
            if partes[1] == "":  # se nao existem paginas
                self.paginas = ""
                partes = partes[2]
            else:
                self.paginas = partes[2].rstrip(".").rstrip(",")
                partes = partes[0]

            partes = partes.rpartition(" v. ")
            if partes[1] == "":  # se nao existem informacao de volume
                self.volume = ""
                partes = partes[2]
            else:
                self.volume = partes[2].rstrip(".").rstrip(",")
                partes = partes[0]

            aux = re.findall(", ((?:19|20)\\d\\d)\\b", partes)

            if len(aux) > 0:
                partes = partes.rpartition(",")
                self.ano = aux[-1].strip().rstrip(".").rstrip(",")
                partes = partes[0]
            else:
                self.ano = ""

            partes = partes.rpartition(" In: ")
            if partes[1] == "":  # se nao existe nome do evento
                self.nomeDoEvento = ""
                partes = partes[2]
            else:
                # Qualis - Eh preciso separa o titulo da conferencia em partes[2] do
                # restante
                partesV = partes[2].split(", ")
                self.nomeDoEvento = ""
                self.sigla = ""
                i = 0
                self.nomeDoEvento += partesV[i].rstrip()
                partesV = self.nomeDoEvento.split("(")
                if len(partesV) == 2:
                    partesV = partesV[1].split(")")
                    self.sigla = partesV[0].strip("'-0123456789 ")
                # Qualis - Verificar se todas as informacoes estao sendo
                # armazenadas!
                partes = partes[0]

            self.titulo = partes.strip().rstrip(".")
            self.chave = self.autores  # chave de comparação entre os objetos

        else:
            self.doi = ""
            self.relevante = ""
            self.autores = ""
            self.titulo = ""
            self.nomeDoEvento = ""
            self.ano = ""
            self.volume = ""
            self.paginas = ""

    def compararCom(self, objeto):
        if self.idMembro.isdisjoint(objeto.idMembro) and similaridade_entre_cadeias(
            self.titulo, objeto.titulo
        ):
            # Os IDs dos membros são agrupados.
            # Essa parte é importante para a criação do GRAFO de colaborações
            self.idMembro.update(objeto.idMembro)

            if len(self.doi) < len(objeto.doi):
                self.doi = objeto.doi

            if len(self.autores) < len(objeto.autores):
                self.autores = objeto.autores

            if len(self.titulo) < len(objeto.titulo):
                self.titulo = objeto.titulo

            if len(self.nomeDoEvento) < len(objeto.nomeDoEvento):
                self.nomeDoEvento = objeto.nomeDoEvento

            if len(self.volume) < len(objeto.volume):
                self.volume = objeto.volume

            if len(self.paginas) < len(objeto.paginas):
                self.paginas = objeto.paginas

            return self
        return None  # nao similares

    def html(self, listaDeMembros):
        s = self.autores + ". <b>" + self.titulo + "</b>. "

        s += (
            "Em: <font color=#330066>" + self.nomeDoEvento + "</font>, "
            if not self.nomeDoEvento == ""
            else ""
        )
        s += "v. " + self.volume + ", " if not self.volume == "" else ""
        s += "p. " + self.paginas + ", " if not self.paginas == "" else ""
        s += str(self.ano) + "." if str(self.ano).isdigit() else "."

        if not self.doi == "":
            s += (
                f' <a href="{self.doi}" target="_blank" style="PADDING-RIGHT:4px;">'
                '<img border=0 src="doi.png"></a>'
            )

        s += menuHTMLdeBuscaPB(self.titulo)
        # TODO: a lógica para qualis de conferencias é outra (provavelmente
        # precisará recair na lógica antiga do scriptLattes, ou seja, exigir um
        # CSV)

        s += formata_qualis(self.qualis, self.qualissimilar)
        return s

    def ris(self):
        paginas = self.paginas.split("-")
        if len(paginas) < 2:
            p1 = self.paginas
            p2 = ""
        else:
            p1 = paginas[0]
            p2 = paginas[1]
        s = "\n"
        s += "\nTY  - CONF"
        s += "\nAU  - " + self.autores
        s += "\nT1  - " + self.titulo
        s += "\nTI  - " + self.nomeDoEvento
        s += "\nVL  - " + self.volume
        s += "\nSP  - " + p1
        s += "\nEP  - " + p2
        s += "\nPY  - " + str(self.ano)
        s += "\nL2  - " + self.doi
        s += "\nER  - "
        return s

    def csv(self, nomeCompleto=""):
        if self.qualis is None:
            self.qualis = ""
        if self.qualissimilar is None:
            self.qualissimilar = ""
        s = "trabalhoCompletoEmCongresso\t"
        if nomeCompleto == "":  # tratamento grupal
            s += (
                str(self.ano)
                + "\t"
                + self.doi
                + "\t"
                + self.titulo
                + "\t"
                + self.nomeDoEvento
                + "\t"
                + self.autores
                + "\t"
                + self.qualis
                + "\t"
                + self.qualissimilar
            )
        else:  # tratamento individual
            try:
                s += (
                    f"{nomeCompleto}\t{self.ano}\t{self.doi}\t{self.titulo}"
                    f"\t{self.nomeDoEvento}\t{self.autores}\t{self.qualis}"
                    f"\t{self.qualissimilar}"
                )
            except UnicodeDecodeError as err:
                print(nomeCompleto)
                print((str(self.ano)))
                print((self.doi))
                print((self.titulo))
                print((self.nomeDoEvento))
                print((self.autores))
                print((self.qualis))
                print((self.qualissimilar))
                logger.warning(err)
        return s

    def __str__(self):
        s = "\n[TRABALHO COMPLETO PUBLICADO EM CONGRESSO] \n"
        s += "+ID-MEMBRO   : " + str(self.idMembro) + "\n"
        s += "+RELEVANTE   : " + str(self.relevante) + "\n"
        s += "+DOI         : " + self.doi + "\n"
        s += "+AUTORES     : " + self.autores + "\n"
        s += "+TITULO      : " + self.titulo + "\n"
        s += "+NOME EVENTO : " + self.nomeDoEvento + "\n"
        s += "+ANO         : " + str(self.ano) + "\n"
        s += "+VOLUME      : " + self.volume + "\n"
        s += "+PAGINAS     : " + self.paginas + "\n"
        s += "+item        : " + self.item + "\n"
        return s
