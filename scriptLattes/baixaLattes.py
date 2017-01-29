#!/usr/bin/python
# encoding: utf-8
# filename: baixaLattes.py
#
#
# scriptLattes 
# http://scriptlattes.sourceforge.net/
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

import sys, time, random, re, os
import urllib, cStringIO
from PIL import Image

try:
    import mechanize
except:
    print "Erro, voce precisa do Mechanize instalado no sistema, instale no Ubuntu com 'sudo apt-get install python-mechanize"


import cookielib

VERSION       = '2017-05-09'
REMOTE_SCRIPT = 'https://api.bitbucket.org/2.0/snippets/scriptlattes/g5Bx'
HEADERS       = [('Accept-Language', 'en-us,en;q=0.5'),
    ('Accept-Encoding', 'deflate'),
    ('Keep-Alive', '115'),
    ('Connection', 'keep-alive'),
    ('Cache-Control', 'max-age=0'),
    ('Host', 'buscatextual.cnpq.br'),
    ('Origin', 'http,//buscatextual.cnpq.br'),
    ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'),
]


def __self_update():
    import inspect
    try:
        import simplejson
    except:
        print "Erro, voce precisa do Simplejson instalado no sistema, instale no Ubuntu com 'sudo apt-get install python-simplejson'"
        sys.exit(1)
    br = mechanize.Browser()
    r = br.open(REMOTE_SCRIPT)
    d = simplejson.loads(r.read())
    if d['updated_on'][:13] != VERSION:
        print "BaixaLattes desatualizado, atualizando..."
        r = br.open(d['files']['baixaLattes.py']['links']['self']['href'])
        content = r.read()
        fpath = os.path.abspath(inspect.getfile(inspect.currentframe()))
        try:
            handler = file(fpath, 'w')
        except:
            print "Erro na escrita do novo arquivo, verifique se o arquivo '%s' tem permissao de escrita" % fpath
            sys.exit(1)
        handler.write(content)
        handler.close()
        print "BaixaLattes atualizado, reinicie o programa para utilizar a nova versão, encerrando o ScriptLattes"
        sys.exit(0)


def __get_data(id_lattes):
    p = re.compile('[a-zA-Z]+')
    if p.match(id_lattes):
        url = 'http://buscatextual.cnpq.br/buscatextual/visualizacv.do?id='+id_lattes
    else:
        url = 'http://lattes.cnpq.br/'+id_lattes
    br = mechanize.Browser()
    br.set_cookiejar(cookielib.LWPCookieJar())

    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.addheaders = HEADERS

    #Parte em que buscava o CVs (Obrigado Jorge Gustavo dos Santos Pinho!)
    #r = br.open(url)

    # Nova implementação
    url_get_captcha = "http://buscatextual.cnpq.br/buscatextual/servlet/captcha?metodo=getImagemCaptcha&noCache="+str(int(time.time()))
    resp = br.open(url)

    print (url_get_captcha)

    m    = re.search('(&id=).*', resp.geturl())
    id   = m.group(0)
    id   = id.replace('&id=', '')

    resp = br.open(url_get_captcha)
    file = cStringIO.StringIO(resp.read())
    img  = Image.open(file)
    img.show(title='CAPTCHA');

    captcha     = str(raw_input('\nINSIRA AS LETRAS DO CAPTCHA: '));
    url_captha  = "http://buscatextual.cnpq.br/buscatextual/servlet/captcha?informado="+captcha+"&id="+id+"&metodo=validaCaptcha"
    resp        = br.open(url_captha)
    resp        = br.open(url)
    # Fim da implementação

    response = resp.read()
    if 'infpessoa' in response:
        return response

    br.select_form(nr=0)
    br.form.set_all_readonly(False)
    br.form['metodo'] = 'visualizarCV'
    r = br.submit()
    return r.read()


def baixaCVLattes(id_lattes, debug=True):
	tries = 50
	while tries > 0:
		try:
			data = __get_data(id_lattes)
			#time.sleep(random.random()+0.5) #0.5 a 1.5 segs de espera, nao altere esse tempo para não ser barrado do servidor do lattes
			if 'infpessoa' not in data:
				tries -= 1
			else:
				return data
		except Exception, e:
			if debug:
				print e
			tries -= 1
	# depois de 5 tentativas, verifiquemos se existe uma nova versao do baixaLattes
	#__self_update()
	if debug:
		print '[AVISO] Nao é possível obter o CV Lattes: ', id_lattes
		print '[AVISO] Certifique-se que o CV existe.'
	
	print "Nao foi possivel baixar o CV Lattes em varias tentativas"
	return "   "
	#raise Exception("Nao foi possivel baixar o CV Lattes em 5 tentativas")
