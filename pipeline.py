import os

from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

from Download import Downloader, lista_arquivos_descompactados
from Parser import prepbufr2littler



# d = Downloader('337.0')
# d.login()
# d.download_dados(['20200201'])
# lista_arquivo_prepbufr = d.descompacta_dados()

lista_arquivo_prepbufr = lista_arquivos_descompactados()



def execucao_parser(arquivo):
    nome_prepbufr = arquivo

    nome_base = os.path.basename(arquivo) \
                            .replace('.nr', '.littler') \
                            .replace('prepbufr.', '')
    nome_littler = os.path.join('./Dados_Out', nome_base)

    print(nome_prepbufr, nome_littler)

    prepbufr2littler(nome_prepbufr, nome_littler)

with ThreadPoolExecutor(mp.cpu_count()) as executor:
    executor.map(execucao_parser, lista_arquivo_prepbufr)
