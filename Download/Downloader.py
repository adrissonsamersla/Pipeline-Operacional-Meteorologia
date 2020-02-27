import sys, os
import requests
import tarfile

from glob import glob
from getpass import getpass

def confere_status_arquivo(endereco_arquivo, tamanho_arquivo):
    """ 
        Função para conferir o andamento do download: recebe o nome e o tamanho final
        do arquivo e compara com o seu tamanho atual.
    """
    sys.stdout.write('\r')
    sys.stdout.flush()

    tamanho = int(os.stat(endereco_arquivo).st_size)

    porcentagem_completado = (tamanho/tamanho_arquivo) * 100

    sys.stdout.write('{:.3f} {:s}'.format(porcentagem_completado, '% Completado'))
    sys.stdout.flush()

def lista_arquivos_descompactados():
    return glob('Dados_In/*.nr/*')

class Downloader:
    """
        Essa classe é responsável por fazer o download dos arquivos. 
        Exemplo de funcionamento:
            downloader = Downloader('INSIRA SEU EMAIL', '337.0')
            downloader.login('INSIRA SUA SENHA')
            downloader.download_dados(['20200122','20200123'])
    """

    def __init__(self, dataset: str, email: str = None):
        """
            O parâmetro dataset deve estar no formato: DDD.D no qual D é um dígito. 
            Exemplo: 337.0 (usado como padrão).
        """
        if email is None:
            sys.stdout.write('Insira seu email: ')
            sys.stdout.flush()

            email = sys.stdin.readline()

        self.email = email
        self.dataset = dataset
        self.cookies = ''
        self.arquivos_compactados = []

    def login(self, senha: str = None):
        """
            Usa o email já fornecida com a senha passada para se cadastrar no site da NCAR: 
            https://rda.ucar.edu/
            Armazena as informações de login em forma de cookies.
            Se não for possível realizar o login, retorna uma exceção.
        """
        if senha is None:
            senha = getpass('Insira sua senha: ')

        url = 'https://rda.ucar.edu/cgi-bin/login'
        values = {
            'email' : self.email, 
            'passwd' : senha, 
            'action' : 'login'
        }

        ret = requests.post(url,data=values)
        if ret.status_code != 200:
            raise Exception(('Não foi possível se autenticar no site da NCAR.\n' + \
                'Status retornado: {}\n' + \
                'Mensagem retornada: {}').format(ret.status_code, ret.text)
            )
        self.cookies = ret.cookies

    def download_dados(self, lista_datas: list):
        """
            Realiza propriamente o download dos arquivos (separados por dia).
            O parâmetro lista_datas deve conter as datas (e os arquivos) desejados,
            no formato AAAAMMDD. Ao fim da transferência, eles estarão compactados
            na pasta Dados_In. Exemplo:
                lista_datas = ['20200122','20200123']
                    => Dados_In/prepbufr.20200122.nr.tar.gz
                    => Dados_In/prepbufr.20200122.nr.tar.gz
            Retorna uma lista com o endereço dos arquivos baixados.
        """
        if (not os.path.isdir('Dados_In/')):
            os.mkdir('Dados_In/')
        if (not os.path.isdir('Dados_Out/')):
            os.mkdir('Dados_Out/')

        # Exemplo: https://rda.ucar.edu/data/ds337.0/
        endereco_dataset = 'https://rda.ucar.edu/data/ds{}/'.format(self.dataset)

        lista_arquivos = []
        for data in lista_datas:
            # Pega o ano dentro da data
            ano = data[0:4]

            # Exemplo: tarfiles/2020/prepbufr.20200210.nr.tar.gz
            arquivo = 'tarfiles/{}/prepbufr.{}.nr.tar.gz'.format(ano, data)
            lista_arquivos.append(arquivo)

        lista_endereco_arquivo = []
        for arquivo in lista_arquivos:
            nome_arquivo = os.path.basename(arquivo)
            print('Baixando o arquivo: {}'.format(nome_arquivo))

            endereco_web_arquivo = endereco_dataset + arquivo
            endereco_destino_arquivo = 'Dados_In/{}'.format(nome_arquivo)

            lista_endereco_arquivo.append(endereco_destino_arquivo)

            req = requests.get(endereco_web_arquivo, cookies = self.cookies, allow_redirects = True, stream = True)
            tamanho_arquivo = int(req.headers['Content-length'])

            with open(endereco_destino_arquivo, 'wb') as arquivo_destino:
                # 1048576 = 2^20 = 1 MByte
                chunk_size = 1048576
                for chunk in req.iter_content(chunk_size = chunk_size):
                    arquivo_destino.write(chunk)
                    if chunk_size < tamanho_arquivo:
                        confere_status_arquivo(endereco_destino_arquivo, tamanho_arquivo)
            
                confere_status_arquivo(endereco_destino_arquivo, tamanho_arquivo)
                print()

        self.arquivos_compactados = lista_endereco_arquivo

    def descompacta_dados(self) -> list:
        for arquivo_targz in self.arquivos_compactados:
            nome_arquivo = os.path.basename(arquivo_targz)
            print('Descompactando o arquivo: {}'.format(nome_arquivo))

            compactado = tarfile.open(arquivo_targz, 'r:gz')
            compactado.extractall(path = 'Dados_In')
            compactado.close()

        self.remove_compactados()

        return lista_arquivos_descompactados()

    def remove_compactados(self):
        for arquivo_targz in self.arquivos_compactados:
            nome_arquivo = os.path.basename(arquivo_targz)
            print('Removendo o arquivo: {}'.format(nome_arquivo))
            os.remove(arquivo_targz)


