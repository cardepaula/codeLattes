#!/usr/bin/python
# encoding: utf-8
# filename: analisadorDePublicacoes.py
#
# scriptLattes V8
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


import http.cookiejar
import time
import urllib.request
import urllib.error
import urllib.parse
import xml.dom.minidom
import os.path
import re
import unicodedata

from html import unescape
from .genericParser import genericParser
from .parser101007 import parser101007
from .parser101590 import parser101590
from .publicacaoEinternacionalizacao import PublicacaoEinternacionalizacao


class AnalisadorDePublicacoes:

    def __init__(self, grupo):
        self.grupo = grupo
        self.listaDePublicacoesEinternacionalizacao = {}
        self.listaDoiValido = []
        self.parserFile = xml.dom.minidom.parse(
            "./scriptLattes/internacionalizacao/parserFileConfig.xml"
        )  # read the file just the fist time
        self.paises = {
            "Abkhazia": ["Apsny", "Abkhaziya"],
            "Afghanistan": ["Afghanestan"],
            "Albania": ["Shqipëria"],
            "Algeria": ["Al-Jazā'ir"],
            "American Samoa": ["Amerika Sāmoa"],
            "Andorra": [],
            "Angola": [],
            "Anguilla": [],
            "Antigua and Barbuda": [],
            "Argentina": [],
            "Armenia": ["Hayastán"],
            "Aruba": [],
            "Australia": [],
            "Austria": ["Österreich"],
            "Azerbaijan": ["Azərbaycan"],
            "The Bahamas": ["Bahamas"],
            "Bahrain": ["Al-Baḥrayn"],
            "Bangladesh": [],
            "Barbados": [],
            "Belarus": ["Belorussiya", "Belorussiâ"],
            "Belgium": ["België", "Belgique", "Belgien"],
            "Belize": [],
            "Benin": ["Bénin"],
            "Bermuda": [],
            "Bhutan": ["Druk Yul"],
            "Bolivia": ["Volívia"],
            "Bosnia and Herzegovina": ["Bosna i Hercegovina"],
            "Botswana": [],
            "Brazil": ["Brasil"],
            "Brunei": [],
            "Bulgaria": ["Bulgariya", "Bălgarija"],
            "Burkina Faso": [],
            "Burma": ["Myanmar"],
            "Burundi": [],
            "Cambodia": ["Kampuchea"],
            "Cameroon": ["Cameroun"],
            "Canada": [],
            "Cape Verde": ["Cabo Verde"],
            "Cayman Islands": [],
            "Central African Republic": ["République Centrafricaine"],
            "Chad": ["Tchad"],
            "Chile": [],
            "China": ["PR China"],
            "Christmas Island": [],
            "Cocos Islands": [],
            "Colombia": [],
            "Comoros": ["Komori", "Comores"],
            "Congo": [],
            "Cook Islands": [],
            "Costa Rica": [],
            "Cote dIvoire": ["Côte d'Ivoire", "Cote d'Ivoire"],
            "Croatia": ["Hrvatska"],
            "Cuba": [],
            "Cyprus": ["Kypros"],
            "Czech Republic": ["Česká republika", "Česko"],
            "Denmark": ["Danmark"],
            "Djibouti": ["Jībūtī"],
            "Dominica": [],
            "Dominican Republic": ["República Dominicana", "Republica Dominicana"],
            "East Timor": ["Timor Lorosa'e", "Timor-Leste"],
            "Ecuador": [],
            "Egypt": [],
            "El Salvador": [],
            "Equatorial Guinea": ["Guinea Ecuatorial"],
            "Eritrea": ["Iritriya"],
            "Estonia": ["Eesti"],
            "Ethiopia": ["Ityop'ia", "Ityopia"],
            "Faroe Islands": [],
            "Fiji": ["Viti"],
            "Finland": ["Suomi"],
            "France": [],
            "French Guiana": ["Guyane"],
            "French Polynesia": ["Polynésie française"],
            "Gabon": [],
            "The Gambia": [],
            "Georgia": ["Sak'art'velo"],
            "Germany": ["Deutschland"],
            "Ghana": [],
            "Gibraltar": [],
            "Greece": ["Hellas", "Ellada"],
            "Greenland": ["Kalaallit Nunaat"],
            "Grenada": [],
            "Guadeloupe": [],
            "Guam": [],
            "Guatemala": [],
            "Guernsey": [],
            "Guinea": ["Guinée"],
            "Guinea-Bissau": ["Guiné-Bissau"],
            "Guyana": [],
            "Haiti": ["Haïti", "Ayiti"],
            "Honduras": [],
            "Hungary": ["Magyarország"],
            "Iceland": ["Ísland"],
            "India": ["Bhārat"],
            "Indonesia": [],
            "Iran": ["Īrān"],
            "Iraq": ["Al-'Iraq"],
            "Ireland": ["Éire"],
            "Isle of Man": ["Ellan Vannin"],
            "Israel": ["Yisrael"],
            "Italy": ["Italia"],
            "Jamaica": [],
            "Japan": ["Nippon", "Nihon"],
            "Jersey": ["Jèrri"],
            "Jordan": ["Al-’Urdun"],
            "Kazakhstan": ["Qazaqstan", "Kazakhstán"],
            "Kenya": [],
            "Kiribati": [],
            "South Korea": [],
            "North Korea": [],
            "Kosovo": ["Kosova", "Косово"],
            "Kuwait": ["Al-Kuwayt"],
            "Kyrgyzstan": ["Kirgizija"],
            "Laos": ["Lao"],
            "Latvia": ["Latvija"],
            "Lebanon": ["Lubnān"],
            "Lesotho": [],
            "Liberia": [],
            "Libya": ["Lībiyā"],
            "Liechtenstein": [],
            "Lithuania": ["Lietuva"],
            "Luxembourg": ["Lëtzebuerg", "Luxembourg"],
            "Macedonia": ["Makedonija"],
            "Madagascar": ["Madagasikara"],
            "Malawi": [],
            "Malaysia": [],
            "Maldives": ["Dhivehi Raajje"],
            "Mali": [],
            "Malta": [],
            "Marshall Islands": [],
            "Martinique": [],
            "Mauritania": ["Mauritanie"],
            "Mauritius": [],
            "Mayotte": [],
            "Mexico": ["México"],
            "Federated States of Micronesia": [],
            "Moldova": [],
            "Monaco": [],
            "Mongolia": [],
            "Montenegro": ["Crna Gora"],
            "Montserrat": [],
            "Morocco": ["Al-Maghrib"],
            "Mozambique": ["Moçambique"],
            "Namibia": [],
            "Nauru": ["Naoero", "Nauruo"],
            "Nepal": ["Nepāla"],
            "Netherlands": ["Nederland"],
            "New Caledonia": ["Nouvelle-Calédonie"],
            "New Zealand": ["Aotearoa"],
            "Nicaragua": [],
            "Niger": [],
            "Nigeria": [],
            "Niue": [],
            "Norfolk Island": [],
            "Northern Ireland": [],
            "Northern Mariana Islands": [],
            "Norway": ["Norge", "Noreg"],
            "Oman": [],
            "Pakistan": [],
            "Palau": ["Belau"],
            "Palestinian National Authority": ["Filastīn"],
            "Panama": ["Panamá"],
            "Papua New Guinea": ["Papua Niugini"],
            "Paraguay": ["Paraguái"],
            "Peru": ["Perú"],
            "Philippines": ["Pilipinas", "Filipinas"],
            "Pitcairn Islands": [],
            "Poland": ["Polska"],
            "Portugal": [],
            "Puerto Rico": [],
            "Qatar": [],
            "Reunion": ["Réunion"],
            "Romania": ["România"],
            "Russia": ["Rossiya", "Rossiâ"],
            "Rwanda": [],
            "Saint-Pierre and Miquelon": ["Saint-Pierre et Miquelon"],
            "Saint Helena": [],
            "Saint Kitts and Nevis": [],
            "Saint Lucia": [],
            "Saint Vincent and the Grenadines": [],
            "Samoa": [],
            "San Marino": [],
            "Sao Tome and Principe": ["São Tomé and Príncipe", "São Tomé e Príncipe"],
            "Saudi Arabia": [],
            "Senegal": ["Sénégal"],
            "Serbia": ["Srbija", "Serbia and Montenegro"],
            "Seychelles": ["Sesel"],
            "Sierra Leone": [],
            "Singapore": ["Singapura", "Singapur"],
            "Slovakia": ["Slovensko"],
            "Slovenia": ["Slovenija"],
            "Solomon Islands": [],
            "Somalia": ["Soomaaliya"],
            "South Africa": ["Suid-Afrika"],
            "South Sudan": [],
            "South Ossetia": ["Khussar Iryston"],
            "Spain": ["España", "Espanya", "Espainia", "Espanha"],
            "Sri Lanka": ["Sri Lankā"],
            "Sudan": ["As-Sudan"],
            "Suriname": [],
            "Svalbard": [],
            "Swaziland": [],
            "Sweden": ["Sverige"],
            "Switzerland": ["Schweiz", "Suisse", "Svizzera", "Svizra"],
            "Syria": ["Suriyah"],
            "Taiwan": [],
            "Tajikistan": ["Tojikistan"],
            "Tanzania": [],
            "Thailand": ["Mueang Thai"],
            "Togo": [],
            "Tokelau": [],
            "Tonga": [],
            "Trinidad and Tobago": [],
            "Tunisia": ["Tunis"],
            "Turkey": ["Türkiye"],
            "Turkish Republic of Northern Cyprus": [],
            "Turkmenistan": ["Türkmenistan"],
            "Turks and Caicos Islands": [],
            "Tuvalu": [],
            "Uganda": [],
            "Ukraine": ["Ukraїna"],
            "United Arab Emirates": ["UAE", "The Emirates"],
            "United Kingdom": ["UK", "Britain", "U.K."],
            "United States": [
                "USA",
                "America",
                "US",
                "U.S.",
                "USA",
                "Estados Unidos",
                "América",
            ],
            "Uruguay": ["República Oriental del Uruguay"],
            "Uzbekistan": ["O'zbekiston", "Ozbekiston"],
            "Vanuatu": [],
            "Vatican City": ["Civitas Vaticana", "Vatican", "vaticano"],
            "Venezuela": [],
            "Vietnam": [],
            "Virgin Islands": [],
            "Vojvodina": ["Vojvodyna"],
            "Wallis and Futuna": ["Wallis-et-Futuna", "Wallis et Futuna"],
            "Yemen": ["Al-Yaman"],
            "Zambia": [],
            "Zimbabwe": [],
        }

    def analisarInternacionalizacaoNaCoautoria(self):
        listaCompletaPB = self.grupo.compilador.listaCompletaArtigoEmPeriodico
        keys = list(listaCompletaPB.keys())
        for ano in keys:
            elementos = listaCompletaPB[ano]
            for pub in elementos:
                if hasattr(pub, "doi"):
                    if not pub.doi == "":
                        listaDePaisesIdentificados = self.identificarPaisesEmPublicacao(
                            pub.doi, ano
                        )
                        publicacaoEinternacionalizacao = PublicacaoEinternacionalizacao(
                            pub
                        )
                        publicacaoEinternacionalizacao.atribuirListaDeIndicesDePaises(
                            listaDePaisesIdentificados
                        )

                        if (
                            self.listaDePublicacoesEinternacionalizacao.get(pub.ano)
                            is None
                        ):
                            self.listaDePublicacoesEinternacionalizacao[pub.ano] = []
                        self.listaDePublicacoesEinternacionalizacao[pub.ano].append(
                            publicacaoEinternacionalizacao
                        )

        # devolve uma lista com as publicacoes e paises
        return self.listaDePublicacoesEinternacionalizacao

    def identificarPaisesEmPublicacao(self, urlDOI, ano):
        listaDePaisesIdentificados = None
        dataDoi = self.obterDadosAtravesDeDOI(urlDOI)

        if dataDoi:
            listaDePaisesIdentificados = []

            for key in list(self.paises.keys()):
                nomeDePais = key
                # Procuramos o nome em ingles (nome original)
                if self.procurarPais(dataDoi, nomeDePais, urlDOI):
                    listaDePaisesIdentificados.append(nomeDePais)
                else:
                    if len(self.paises[nomeDePais]) > 0:
                        # Procuramos os nomes alternativos dos países
                        for nomeAlternativoDePais in self.paises[nomeDePais]:
                            if self.procurarPais(
                                dataDoi, nomeAlternativoDePais, urlDOI
                            ):
                                listaDePaisesIdentificados.append(nomeDePais)
                                break

        print(("- Paises identificados : " + str(listaDePaisesIdentificados)))

        # na lista de paises identificados
        if listaDePaisesIdentificados is not None:
            if len(listaDePaisesIdentificados) > 0:
                if (
                    "Brazil" not in listaDePaisesIdentificados
                    and "Brasil" not in listaDePaisesIdentificados
                ):
                    listaDePaisesIdentificados.append("Brazil")
            cadeia = (
                str(ano)
                + " , "
                + urlDOI
                + " , "
                + str(len(listaDePaisesIdentificados))
                + ", "
            )
            for nomPais in listaDePaisesIdentificados:
                cadeia = cadeia + nomPais + "; "
            self.listaDoiValido.append(cadeia)

        return listaDePaisesIdentificados

    def procurarPais(self, dataDoi, nomeDePais, urlDOI):
        # TODO rever a forma de procurar país. Muitos não estão sendo identificados
        nomeDePais = nomeDePais.lower()
        nomeDePais = unescape(nomeDePais)
        nomeDePais = (
            unicodedata.normalize("NFKD", str(nomeDePais))
            .encode("ASCII", "ignore")
            .decode()
        )
        if len(nomeDePais) <= 0:
            return False
        if len(dataDoi) == 2:
            doihtml = dataDoi[0]
            doihtml = doihtml.lower()
            doihtml = doihtml.replace("\\r\\n", "")
            doihtml = doihtml.replace("\\t", "")
            doihtml = doihtml.replace("\\n", "")
            prefixo = dataDoi[1][4]
            posfixo = dataDoi[1][5]
            if re.search(
                (prefixo, "")[prefixo is None]
                + re.escape(nomeDePais)
                + (posfixo, "")[posfixo is None],
                doihtml,
            ):
                return True

            return False
        if len(dataDoi) == 1:
            doihtml = dataDoi[0]
            doihtml = doihtml.lower()
            prefixo = ",.*,\\s*"
            if re.search(prefixo + re.escape(nomeDePais) + r"\s*\n", doihtml):
                return True
            if re.search(prefixo + re.escape(nomeDePais) + r"\W*\n", doihtml):
                return True
            return False

        return False

    def obterDadosAtravesDeDOI(self, urlDOI):
        print(("\nProcessando DOI: " + urlDOI))
        txdata = None
        txheaders = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:2.0) "
            + "Gecko/20100101 Firefox/4.0",
            "Accept-Language": "en-us,en;q=0.5",
            "Accept-Encoding": "deflate",
            "Keep-Alive": "115",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }

        doiNumber = urlDOI
        doiNumber = doiNumber.replace("http://dx.doi.org/", "")
        doiNumber = doiNumber.replace("/", "-")
        doiPath = self.grupo.diretorioDoi + "/" + doiNumber

        if os.path.isfile(doiPath):
            arquivoX = open(doiPath, encoding="utf-8")
            rawDOIhtml = arquivoX.read()
            arquivoX.close()
            print(("- Utilizando DOI armazenado no cache: " + doiPath))

        # -----------------------------------------------------------------
        # tentamos 3 vezes baixar a página web associado ao DOI
        else:
            tentativa = 1
            while tentativa <= 1:
                try:
                    req = urllib.request.Request(urlDOI, txdata, txheaders)

                    cj = http.cookiejar.CookieJar()
                    opener = urllib.request.build_opener(
                        urllib.request.HTTPCookieProcessor(cj)
                    )
                    response = opener.open(req)
                    rawDOIhtml = response.read()
                    print(("- Baixando publicacao com DOI: " + urlDOI))

                    rawDOIhtml = unescape(rawDOIhtml.decode("utf8", "ignore"))
                    rawDOIhtml = (
                        unicodedata.normalize("NFKD", str(rawDOIhtml))
                        .encode("ASCII", "ignore")
                        .decode()
                    )

                    if not self.grupo.diretorioDoi == "":
                        print(("- Armazenando DOI armazenado no cache: " + doiPath))
                        filename = doiPath
                        f = open(filename, "w", encoding="utf-8")
                        f.write(rawDOIhtml)
                        f.close()
                    break
                except BaseException:
                    print(
                        (
                            "[AVISO] Tentativa "
                            + str(tentativa)
                            + ": DOI não está disponível na internet: ",
                            urlDOI,
                        )
                    )
                    time.sleep(10)
                    rawDOIhtml = None
                    tentativa += 1
                    continue
        dataDoi = []
        if rawDOIhtml is not None:
            parserData = self.procurarParser(urlDOI)
            if parserData is not None:
                if len(parserData) == 6:
                    print(("**caso -- " + parserData[0]))
                    caso = genericParser(parserData)
                    try:
                        caso.feed(rawDOIhtml)
                    except BaseException:
                        caso.data = ""
                    doihtml = str(caso.data)
                    dataDoi.append(doihtml)
                    dataDoi.append(parserData)

            elif urlDOI.find("10.1134") > -1:
                print("**caso - 10.1134")
                casoUrl = parser101007()
                try:
                    casoUrl.feed(rawDOIhtml)
                except BaseException:
                    casoUrl.data = ""
                doihtml = str(casoUrl.data)
                parserData = [
                    "10.1134",
                    "",
                    "",
                    "",
                    "authoraddress=.*\\+",
                    ".*&contentid",
                ]
                dataDoi.append(doihtml)
                dataDoi.append(parserData)

            elif urlDOI.find("10.1590") > -1:
                print("**caso -- 10.1590")
                caso = parser101590()
                try:
                    caso.feed(rawDOIhtml)
                except BaseException:
                    caso.data = ""
                doihtml = str(caso.data)
                parserData = [
                    "10.1590",
                    "",
                    "",
                    "",
                    ",.*,\\s*",
                    "[\\s*|,|;|-|\\.|'|\"]",
                ]
                dataDoi.append(doihtml)
                dataDoi.append(parserData)
            else:
                print("**caso DEFAULT não esta no xml")
                doihtml = self.html2texto(rawDOIhtml)
                dataDoi.append(doihtml)

        else:
            dataDoi = []
        return dataDoi

    def html2texto(self, rawDOIhtml):
        # First we remove inline JavaScript/CSS:
        cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", rawDOIhtml.strip())
        # Then we remove html comments. This has to be done before removing regular
        # tags since comments can contain '>' characters.
        cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)

        cleaned = re.sub(r"<br>", "\n", cleaned)
        cleaned = re.sub(r"(?s)<p.*?>", "\n", cleaned)
        cleaned = re.sub(r"(?s)<li.*?>", "\n", cleaned)
        cleaned = re.sub(r"(?s)<div.*?>", "\n", cleaned)
        cleaned = re.sub(r"\r", "\n", cleaned)
        cleaned = re.sub(r"\t+", " ", cleaned)

        # Next we can remove the remaining tags:
        cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)

        cleaned = re.sub(r"\s+\n", "\n", cleaned)
        return cleaned.strip()

    def procurarParser(self, urlDOI):
        idDoi = urlDOI[18:25]
        x = self.parserFile
        nos = x.documentElement
        fields = []
        filhos1 = [no for no in nos.childNodes if no.nodeType == x.ELEMENT_NODE]
        for pai in filhos1:
            if pai.hasAttribute("idDoi"):
                atr = pai.getAttributeNode("idDoi")
                if atr.value == idDoi:
                    fields.append(atr.value)
                    filhos2 = [
                        no for no in pai.childNodes if no.nodeType == x.ELEMENT_NODE
                    ]
                    for filho in filhos2:
                        fields.append(self.node2Text(filho))
                    return fields
        return None

    def node2Text(self, node):
        text = ""
        for child in node.childNodes:
            if child.nodeType is child.TEXT_NODE:
                text += child.data
        return text
