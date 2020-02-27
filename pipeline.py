from Download import Downloader, lista_arquivos_descompactados

# d = Downloader('337.0')
# d.login()
# d.download_dados(['20200201'])

# lista_arquivo_prepbufr = d.descompacta_dados()

lista_arquivo_prepbufr = lista_arquivos_descompactados()

import os

from Parser import prepbufr2littler_surface, prepbufr2littler_upperair

for arquivo in lista_arquivo_prepbufr:
    nome_prepbufr = arquivo

    nome_base = os.path.basename(arquivo) \
                            .replace('.nr', '.littler') \
                            .replace('prepbufr.', '')

    nome_littler = os.path.join('./Dados_Out', nome_base)

    nome_littler_surface = nome_littler + '_surface'
    nome_littler_upperair = nome_littler + '_upperair'

    print(nome_prepbufr, nome_littler)

    #prepbufr2littler_surface(nome_prepbufr, nome_littler_surface)

    prepbufr2littler_upperair(nome_prepbufr, nome_littler_upperair)

