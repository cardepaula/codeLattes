#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import codecs

import urllib2
import requests
from lxml import etree
import pickle
from HTMLParser import HTMLParser
import datetime


# converts a string to a integer if the string is a integer, else returns None
def str2int(string):
    if string == None:  return None
    try:
        return int(string)
    except ValueError:
        return None


def getvalue(attrs):
    for attr in attrs:
        if attr[0] == 'value':
            return attr[1]
    return None


class qualis_extractor(object):
    # Constructor
    def __init__(self, online):
        self.online = online  #extrair online ou offline ?
        self.publicacao = {}  #{'nome pub',[ ('Nome area','A1') ]}
        self.issn = {}  #{'issn','nome pub'}
        self.areas = []
        self.areas_to_extract = []
        self.areas_last_update = {}
        self.dtnow = datetime.datetime.now()
        self.update_time = 15
        self.init_session()


    def parseContent(self, document, issn={}, titulos={}):
        """
        Process a html page containing qualis data
        Input parameters:
            document: the document to be parsed
        Output parameters:
            issn: a dictionary containing the parsed ISSNs and Qualis
            titulos: a dictionary containing the parsed journal names and Qualis
        Return:
            1 if more pages exist
            0 otherwise
        """

        tree = etree.HTML(document.read())

        tableLines = tree.xpath("//table[@id='consultaPublicaClassificacaoForm:listaVeiculosIssn']/tbody/tr")

        for tr in tableLines:

            line = []
            for td in tr:
                line.append(HTMLParser().unescape(td.text.strip()))

            issn_q, titulo_q, estrato_q, area_q, classif_q = line

            if not issn_q or not titulo_q:
                continue

            if issn_q not in issn:
                issn[issn_q] = {}
            issn[issn_q][area_q] = estrato_q

            if titulo_q not in titulos:
                titulos[titulo_q] = {}
            titulos[titulo_q][area_q] = estrato_q

        #/html/body/div[3]/div[4]/form/table/tbody/tr[2]/td/table/tbody/tr/td/div[2]/div/div/table/tbody/tr/td[11]
        last_bts = tree.xpath("//table[@id='consultaPublicaClassificacaoForm:datascroller1_table']/tbody/tr/td")
        #print etree.tostring(last_bts)

        # se encontrar um botao com onclick='page:last', entao ainda tem paginas
        if len(last_bts) > 0:
            onclick = last_bts[-1].get("onclick")
            if onclick != None and onclick.find('{\'page\': \'last\'}') != -1:
                return 1

        return 0

    def get_areas(self, document):
        tree = etree.HTML(document)
        self.areas = []
        select = tree.xpath("//select[@id='consultaDocumentosAreaForm:somAreaAvaliacao']/option")
        for option in select:
            self.areas.append(str2int(option.get("value")), option.text.strip())

    def init_session(self):
        """
        Sao necessarias tres requisicoes iniciais para que se chegue a pagina
        que exibe a avaliacao dos artigos.
        """
        urlBase = "http://qualis.capes.gov.br/webqualis/"
        acessoInicial = requests.get(urlBase + 'principal.seam')
        jid = acessoInicial.cookies['JSESSIONID']
        print 'Iniciando sessão qualis...\n ID da Sessão: ', jid
        url1 = urlBase + "publico/pesquisaPublicaClassificacao.seam;jsessionid=" + jid + "?conversationPropagation=begin"
        req1 = urllib2.Request(url1)
        arq1 = urllib2.urlopen(req1)

        self.url2 = urlBase + "publico/pesquisaPublicaClassificacao.seam;jsessionid=" + jid

        # "http://qualis.capes.gov.br/webqualis/publico/pesquisaPublicaClassificacao.seam"
        if not self.online:
            req2 = urllib2.Request(self.url2,
                                   # 'AJAXREQUEST=_viewRoot&consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3Aissn=&javax.faces.ViewState=j_id2&consultaPublicaClassificacaoForm%3Aj_id192=consultaPublicaClassificacaoForm%3Aj_id192')
                                   'AJAXREQUEST=_viewRoot&consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3Aissn=&javax.faces.ViewState=j_id2')
            # 'AJAXREQUEST=_viewRoot&consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3Aissn=&javax.faces.ViewState=j_id4&consultaPublicaClassificacaoForm%3Aj_id195=consultaPublicaClassificacaoForm%3Aj_id195')
            # "AJAXREQUEST=_viewRoot&consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm"%"3Aissn=&javax.faces.ViewState=j_id6&consultaPublicaClassificacaoForm"%"3Aj_id195=consultaPublicaClassificacaoForm"%"3Aj_id195&"
            arq2 = urllib2.urlopen(req2)
            # get all qualis areas
            document = arq2.read()
            self.get_areas(document)
            req3 = urllib2.Request(self.url2,
                                   'consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3AsomAreaAvaliacao=0&consultaPublicaClassificacaoForm%3AsomEstrato=org.jboss.seam.ui.NoSelectionConverter.noSelectionValue&consultaPublicaClassificacaoForm%3AbtnPesquisarTituloPorArea=Pesquisar&javax.faces.ViewState=j_id2')
            # 'consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3AsomAreaAvaliacao=23&consultaPublicaClassificacaoForm%3AsomEstrato=org.jboss.seam.ui.NoSelectionConverter.noSelectionValue&consultaPublicaClassificacaoForm%3AbtnPesquisarTituloPorArea=Pesquisar&javax.faces.ViewState=j_id4')
            arq3 = urllib2.urlopen(req3)
            a3 = arq3.read()

    '''
    Formato do arquivo:
    Nome da area
    Nome da area 2
    ...
    '''

    def parse_areas_file(self, afile):
        if not afile:
            return False
        f = codecs.open(afile, 'r', 'utf-8')
        lines = f.read()
        f.close()
        lines = lines.split('\n')
        areas = []
        for line in lines:
            val = line.partition('#')[0]
            val = val.strip()
            if val:
                self.areas_to_extract.append(val.upper())
        return True

    def should_update_area(self, area):
        lupdt = self.areas_last_update.get(area)
        if lupdt == None: return True
        dtbtween = self.dtnow - lupdt
        if dtbtween.days > self.update_time: return True
        return False

    def extract_qualis(self):
        # FIXME: método só é chamado para extração offline, mas então não deveria ficar acessando a internet. Rever.
        #extract all the areas
        for area in self.areas_to_extract:
            if not self.should_update_area(area):
                print 'Qualis da area %s atualizado!' % (self.areas[area][1])
                continue

            self.areas_last_update[area] = self.dtnow
            scroller = 1
            more = 1
            # FIXME: armazenar mapeamento do nome da área para seu código, e utilizar o código nas URLs abaixo.
            reqn = urllib2.Request(self.url2,
                                   'consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3AsomAreaAvaliacao=' + str(
                                       area) + '&consultaPublicaClassificacaoForm%3AsomEstrato=org.jboss.seam.ui.NoSelectionConverter.noSelectionValue&consultaPublicaClassificacaoForm%3AbtnPesquisarTituloPorArea=Pesquisar&javax.faces.ViewState=j_id2')

            arqn = urllib2.urlopen(reqn)
            data = []
            print 'Qualis da area %s desatualizado!' % (area)
            print 'Extraindo qualis da area: %d - %s' % area
            while more == 1:
                reqn = urllib2.Request(self.url2,
                                       'AJAXREQUEST=_viewRoot&consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3AsomAreaAvaliacao=' + str(
                                           area) + '&consultaPublicaClassificacaoForm%3AsomEstrato=org.jboss.seam.ui.NoSelectionConverter.noSelectionValue&javax.faces.ViewState=j_id3&ajaxSingle=consultaPublicaClassificacaoForm%3AscrollerArea&consultaPublicaClassificacaoForm%3AscrollerArea=' + str(
                                           scroller) + '&AJAX%3AEVENTS_COUNT=1&')

                #arqn = urllib2.urlopen (reqn)
                ntries = 10
                for i in range(0, ntries):
                    try:
                        arqn = urllib2.urlopen(reqn)
                        break  # success
                    except urllib2.URLError as err:
                        print "Error occurried. Trying again."
                        continue
                        #if not isinstance(err.reason, socket.timeout):
                        #    raise "Non timeout error occurried while loading page." # propagate non-timeout errors
                        #else: # all ntries failed 
                        #    raise err # re-raise the last timeout error
                    if i == 10:
                        print "ja tentou 10 vezes!"
                        break

                more = self.parseContent(arqn)  # FIXME: funcionamento de parseContent mudou
                scroller += 1

    def load_data(self, filename='data'):
        try:
            f = open(filename, 'r')
            data = pickle.load(f)
            self.issn = data[0]
            self.publicacao = data[1]
            self.areas = data[2]
            self.areas_last_update = data[3]
            f.close()
            return True
        except:
            return False

    def save_data(self, filename='data'):
        f = open(filename, 'w')
        data = (self.issn, self.publicacao, self.areas, self.areas_last_update)
        pickle.dump(data, f)
        f.close()

    def get_area_by_name(self, name):
        for i in self.areas:
            if i[1].upper() == name.upper():
                return i
        return None

    def get_area_by_cod(self, cod):
        for i in self.areas:
            if i[0] == cod:
                return i

    '''
    Retorna Qualis do respectivo ISSN. Restringe as areas se elas tiverem sido especificadas (ver parse_areas_file).
    '''

    def get_qualis_by_issn(self, issn):
        # ISSN must be formatted like: XXXX-YYYY
        # if '-' not in issn:
        #     issn = issn[:4] + '-' + issn[4:]

        print('Extraindo qualis a partir do issn {}...'.format(issn))

        if not self.issn.has_key(issn):
            req = urllib2.Request(self.url2,
                                  'consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3Aissn=' + issn + '&consultaPublicaClassificacaoForm%3AbtnPesquisarISSN=Pesquisar&javax.faces.ViewState=j_id2')
            arqn = None
            for i in range(0, 10):
                try:
                    arqn = urllib2.urlopen(req)
                    break  # success
                except urllib2.URLError as err:
                    print "Error occurried. Trying again."
                    continue

            issn_qualis = {}
            titulo_qualis = {}
            more = self.parseContent(arqn, issn_qualis, titulo_qualis)
            scroller = 1
            while more == 1:
                req = urllib2.Request(self.url2,
                                      'AJAXREQUEST=_viewRoot&consultaPublicaClassificacaoForm=consultaPublicaClassificacaoForm&consultaPublicaClassificacaoForm%3Aissn=' + str(
                                          issn) + '&javax.faces.ViewState=j_id3&ajaxSingle=consultaPublicaClassificacaoForm%3Adatascroller1&consultaPublicaClassificacaoForm%3Adatascroller1=' + str(
                                          scroller) + '&AJAX%3AEVENTS_COUNT=1&')
                ntries = 10
                for i in range(0, ntries):
                    try:
                        arqn = urllib2.urlopen(req)
                        break  # success
                    except urllib2.URLError as err:
                        print "Error occurried. Trying again."
                        continue
                        #if not isinstance(err.reason, socket.timeout):
                        #    raise "Non timeout error occurried while loading page." # propagate non-timeout errors
                        #else: # all ntries failed
                        #    raise err # re-raise the last timeout error
                more = self.parseContent(arqn, issn_qualis, titulo_qualis)
                scroller += 1

            if issn_qualis:
                self.issn.update(issn_qualis)
                self.publicacao.update(titulo_qualis)
            else:
                # adiciona o issn informando que não há Qualis associado; poupará requisições futuras
                self.issn[issn] = {}

        qualis = {}

        if self.areas_to_extract:
            for area in self.areas_to_extract:
                if area in self.issn[issn].keys():
                    qualis[area] = self.issn[issn][area]
        else:  # get all areas
            for area, estrato in self.issn[issn].items():
                qualis[area] = estrato

        return qualis

    #get a qualis by the name
    def get_qualis_by_name(self, name):
        qualis = self.publicacoes.get(name)

        '''if qualis != None: return qualis,1
        else:
            iqualis = -1
            r = 0
            pkeys = self.publicacoes.keys()
            for i in xrange(0,pkeys):
                nr = compararCadeias( name, pkeys[i], qualis=True)
                if nr > r:
                    r = nr
                    iqualis = i
            if r > 0:
                return self.publicacoes.get(pkeys[iqualis]),0
        '''
        return None


"""extractor = qualis_extractor(0)
extractor.init_session()
extractor.load_data()
extractor.parse_areas_file()
extractor.extract_qualis()
#for i,j in extractor.get_qualis_by_issn('1993-8233'):
#    print i,'=',j
extractor.save_data()"""
