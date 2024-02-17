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

# import re
# import os
# import http.cookiejar
# import mechanize
# import requests
# import webbrowser
# from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

HEADERS = [
    ("Accept-Language", "en-us,en;q=0.5"),
    ("Accept-Encoding", "deflate"),
    ("Keep-Alive", "115"),
    ("Connection", "keep-alive"),
    ("Cache-Control", "max-age=0"),
    ("Host", "buscatextual.cnpq.br"),
    ("Origin", "http,//buscatextual.cnpq.br"),
    (
        "User-Agent",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    ),
]


def __get_data(id_lattes):
    url = f"http://lattes.cnpq.br/{id_lattes}"
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    recaptcha_element = driver.find_element(By.ID, "divCaptcha")
    if recaptcha_element:
        input(
            "\n\n[AVISO] reCAPTCHA detectado. Pressione Enter aqui quando o reCAPTCHA "
            "for resolvido"
        )

    html = driver.page_source

    driver.quit()

    return html


def baixaCVLattes(id_lattes, debug=True):
    tries = 50
    while tries > 0:
        try:
            data = __get_data(id_lattes)
            # time.sleep(random.random()+0.5) #0.5 a 1.5 segs de espera, nao
            # altere esse tempo para não ser barrado do servidor do lattes
            if "infpessoa" not in data:
                tries -= 1
            else:
                return data
        except Exception as e:
            if debug:
                print(e)
            tries -= 1
    # depois de 5 tentativas, verifiquemos se existe uma nova versao do baixaLattes
    # __self_update()
    if debug:
        print(("[AVISO] Nao é possível obter o CV Lattes: ", id_lattes))
        print("[AVISO] Certifique-se que o CV existe.")

    print("Nao foi possivel baixar o CV Lattes em varias tentativas")
    return "   "
    # raise Exception("Nao foi possivel baixar o CV Lattes em 5 tentativas")
