from Download import Downloader

d = Downloader('337.0')
d.login()
d.download_dados(['20200201'])

lista_arquivo_prepbufr = d.descompacta_dados()

import os

from Parser import prepbufr2littler

for arquivo in lista_arquivo_prepbufr:
    nome_prepbufr = arquivo

    nome_base = os.path.basename(arquivo) \
                            .replace('.nr', '.littler') \
                            .replace('prepbufr.', '')
    nome_littler = os.path.join('./Dados_Out', nome_base)

    print(nome_prepbufr, nome_littler)

    prepbufr2littler(nome_prepbufr, nome_littler)

