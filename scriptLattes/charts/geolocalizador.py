#!/usr/bin/python
# encoding: utf-8
# filename: geolocalizador.py
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

import urllib.request
import urllib.error
import urllib.parse
import re
import unicodedata


class Geolocalizador:
    endereco = None
    lat = "0"
    lon = "0"
    dicionarioDeGeolocalizacao = dict([])

    def __init__(self, endereco, dicionarioDeGeolocalizacao=None):
        self.endereco = endereco
        if dicionarioDeGeolocalizacao is not None:
            self.dicionarioDeGeolocalizacao = dicionarioDeGeolocalizacao

        aux = re.findall(r"(.*) URL.*", self.endereco)
        if len(aux) > 0:
            self.endereco = aux[0]
        aux = re.findall(r"(.*) Telefone.*", self.endereco)
        if len(aux) > 0:
            self.endereco = aux[0]
        self.obterCoordenadas()

    def obterCoordenadas(self):
        cidade = ""
        uf = ""
        cep = ""
        pais = ""

        # - Fortaleza, CE - Brasil
        aux = re.findall(r" - ([^-]*), (\w+) - Brasil", self.endereco)
        if len(aux) > 0:
            (cidade, uf) = aux[0]

            aux = re.findall(
                r"(\d\d\d\d\d\d\d\d)", re.sub("\\s*-\\s*", "", self.endereco)
            )
            if len(aux) > 0:
                cep = aux[0]

            if cep == "":
                cep = self.obterNomeCapital(uf)
            if not uf == "":
                uf = self.obterNomeUF(uf)

            pais = "brasil"
        else:
            # - La Garde CEDEX, - França
            aux = re.findall(r" - ([^-]*), - (.*)", self.endereco)
            if len(aux) > 0:
                (cidade, pais) = aux[0]

        cep = self.corrigirCEP(cep)
        chave = f"{pais} {uf} {cidade} {cep}"
        chave = re.sub("\\s+", "+", chave)
        chave = unicodedata.normalize("NFKD", chave).encode("ASCII", "ignore").decode()

        if chave in self.dicionarioDeGeolocalizacao:
            (self.lat, self.lon) = self.dicionarioDeGeolocalizacao[chave]
        else:
            query = (
                "http://maps.googleapis.com/maps/api/geocode/xml?address="
                + chave
                + "&sensor=false"
            )
            req = urllib.request.Request(query)
            res = urllib.request.urlopen(req).read().decode()
            res = res.replace("\r", "")
            res = res.replace("\n", "")
            res = re.findall(r"<location>(.+?)</location>", res)

            if len(res) > 0:
                lat = re.findall(r"<lat>(.*)</lat>", res[0])
                lon = re.findall(r"<lng>(.*)</lng>", res[0])
                self.lat = lat[0]
                self.lon = lon[0]

                self.dicionarioDeGeolocalizacao[chave] = (self.lat, self.lon)

    def obterNomeUF(self, uf):
        uf = uf.lower().strip()

        nome = ""
        if uf == "ac":
            nome = "acre"
        if uf == "al":
            nome = "alagoas"
        if uf == "ap":
            nome = "amapa"
        if uf == "am":
            nome = "amazonas"
        if uf == "ba":
            nome = "bahia"
        if uf == "ce":
            nome = "ceara"
        if uf == "df":
            nome = "brasilia"
        if uf == "es":
            nome = "espirito santo"
        if uf == "go":
            nome = "goias"
        if uf == "ma":
            nome = "maranhao"
        if uf == "mt":
            nome = "mato grosso"
        if uf == "ms":
            nome = "mato grosso do sul"
        if uf == "mg":
            nome = "minas gerais"
        if uf == "pa":
            nome = "para"
        if uf == "pb":
            nome = "paraiba"
        if uf == "pr":
            nome = "parana"
        if uf == "pe":
            nome = "pernambuco"
        if uf == "pi":
            nome = "piaui"
        if uf == "rj":
            nome = "rio de janeiro"
        if uf == "rn":
            nome = "rio grande do norte"
        if uf == "rs":
            nome = "rio grande do sul"
        if uf == "ro":
            nome = "rondonia"
        if uf == "rr":
            nome = "roraima"
        if uf == "sc":
            nome = "santa catarina"
        if uf == "sp":
            nome = "sao paulo"
        if uf == "se":
            nome = "sergipe"
        if uf == "to":
            nome = "tocantins"

        return nome

    def obterNomeCapital(self, uf):
        uf = uf.lower().strip()

        nome = ""
        if uf == "ac":
            nome = "rio branco"
        if uf == "al":
            nome = "maceio"
        if uf == "ap":
            nome = "macapa"
        if uf == "am":
            nome = "manaus"
        if uf == "ba":
            nome = "salvador"
        if uf == "ce":
            nome = "fortaleza"
        if uf == "df":
            nome = "brasilia"
        if uf == "es":
            nome = "vitoria"
        if uf == "go":
            nome = "goiania"
        if uf == "ma":
            nome = "sao luis"
        if uf == "mt":
            nome = "cuiaba"
        if uf == "ms":
            nome = "campo grande"
        if uf == "mg":
            nome = "belo horizonte"
        if uf == "pa":
            nome = "belem"
        if uf == "pb":
            nome = "joao pessoa"
        if uf == "pr":
            nome = "curitiba"
        if uf == "pe":
            nome = "recibe"
        if uf == "pi":
            nome = "teresina"
        if uf == "rj":
            nome = "rio de janeiro"
        if uf == "rn":
            nome = "natal"
        if uf == "rs":
            nome = "porto alegre"
        if uf == "ro":
            nome = "porto velho"
        if uf == "rr":
            nome = "boa vista"
        if uf == "sc":
            nome = "florianopolis"
        if uf == "sp":
            nome = "sao paulo"
        if uf == "se":
            nome = "aracaju"
        if uf == "to":
            nome = "palmas"

        return nome

    # Este procedimento permite trocar um CEP por outro, a fim de
    # refinar a localização geográfica usando o Google Maps.
    #
    # Em casos específicos a agência de Correios define CEPs especiais
    # que o Google Map não os interpreta corretamente:
    # http://www.correios.com.br/servicos/cep/default.cfm

    def corrigirCEP(self, cep):
        if cep == "05508900":
            return "05508090"  # IME-USP
        if cep == "01246904":
            return "01246000"  # Av. Dr. Arnaldo 715
        if cep == "01246906":
            return "01246000"  # Av. Dr. Arnaldo 715
        if cep == "70770901":
            return "70770200"  # Brasília
        if cep == "13565905":
            return "DEMa Departamento de Engenharia de Materiais"  # Dema

        return cep
