# Instala primeiramente as dependências em python
pip3 install -r requirements.txt 

mkdir Dados_In
mkdir Dados_Out

# Instala a biblioteca BUFRLIB
cd Parser
python3 setup.py install
