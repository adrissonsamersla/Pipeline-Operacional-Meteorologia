from datetime import datetime, timedelta

import numpy as np

from Parser.Bufrlib import prepbufr_mnemonics_dict as mnemonics_dict
import Parser.Bufrlib as Bufrlib

from .MessageParserUpperair import MessageParserUpperair as MessageParser

# Janela de observação: os arquivos são feitos de 6 em 6 horas, portanto
# observações 3 horas antes e 3 horas depois cobrem essa janela.
hora_min = -3.0; hora_max = 3.0

# mnemonics to extract data from prepbufr file.
mnemonics_header            = 'SID XOB YOB DHR TYP ELV SAID T29'
mnemonics_observations      = 'POB QOB TOB ZOB UOB VOB PWO CAT PRSS TDO PMO XDR YDR HRDR SOB DDO TVO'
mnemonics_quality_control   = 'PQM QQM TQM ZQM WQM PWQ PMQ'
mnemonics_observation_error = 'POE QOE TOE ZOE WOE PWE'


# A biblioteca Bufrlib lê os arquivos com uma
# espécie de ponteiro. Assim, pode-se avançar
# com o ponteiro para ler novas informações, com 
# prepbufr.advance() ou prepbufr.load_subset(). 
# Também é possível resetar o ponteiro, usando
# prepbufr.rewind(), fazendo-o apontar para o 
# início do arquivo novamente.

# Forma como se itera sobre as mensagens:
# while prepbufr.advance() == 0:
#     prepbufr

# Forma como se itera sobre as sub-mensagens:
# while prepbufr.load_subset() == 0:
#     prepbufr


def prepbufr2littler_upperair(arquivo_prepbufr: str, arquivo_littler: str):
    if arquivo_prepbufr == arquivo_littler:
        raise IOError('A sobrescrita de arquivo não é permitida: PREPBUFR e LITTLER devem ter nomes diferentes.')

    # Abre o arquivo prepbufr usando a biblioteca Bufrlib
    # e conta o número de mensagens lá dentro. Ao fim, retorna
    # o ponteiro leitor para o início do arquivo.
    prepbufr = Bufrlib.open(arquivo_prepbufr)
    
    numero_mensagens = 0
    while prepbufr.advance() == 0:
        # Somente mensagens válidas, segundo o MessageParser (Surface)
        if not MessageParser.valid_type(prepbufr.msg_type): 
            continue
        numero_mensagens += 1

    # Repare que percorremos, com o ponteiro, todo o arquivo. Portanto, para relermos,
    # devemos resetar o ponteiro, apontá-lo para o início do arquivo novamente. Bufrlib
    # nos fornece o método: prepbufr.rewind(). Na primeira execução, tudo ocorre como 
    # esperado, contudo nos próximos arquivos, Bufrlib gera um erro em execução da biblioteca 
    # em fortran77 por baixo. Portanto optou-se por fechar o arquivo e abrí-lo novamente.
    prepbufr.close(); 
    prepbufr = Bufrlib.open(arquivo_prepbufr)

    # Abre o arquivo de saída (LITTLER) para escrita
    littler = open(arquivo_littler, mode = 'wb')

    # Itera sobre todas as mensagens, extraindo delas
    # as informações necessárias para o LITTLER.
    conjunto_identificadores_observacoes = set()
    index_mensagem = 0
    while prepbufr.advance() == 0:
        # Somente mensagens válidas, segundo o MessageParser (Surface)
        if (not MessageParser.valid_type(prepbufr.msg_type)): 
            continue

        index_mensagem += 1
        # Às vezes, a última mensagem do arquivo gera erro enquanto roda,
        # devido a bufrlib (erro em tempo de execução do fortran77). Portanto,
        # decidi pular a última mensagem.
        # TODO: como aproveitar a última mensagem? O que gera o erro?
        # if index_mensagem == numero_mensagens:
        #     continue

        numero_observacoes_mensagem = 0
        while prepbufr.load_subset() == 0: # loop over subsets in message.

            # Usa os mnemonicos definidos no início do arquivo para extrair
            # as informações do subset. Um subset contém vários levels, por 
            # isso observations é um vetor de duas dimensões. Para saber o que
            # cada mnemônico significa, consulte Bufrlib/bufr_mnemonics.py.
            headers         = prepbufr.read_subset(mnemonics_header).squeeze()
            observations    = prepbufr.read_subset(mnemonics_observations)
            quality_control = prepbufr.read_subset(mnemonics_quality_control)
            errors          = prepbufr.read_subset(mnemonics_observation_error)

            parser = MessageParser(prepbufr.msg_type, headers[4])
            longitude = headers[1]
            latitude  = headers[2]
            hora      = headers[3]
            altitude  = headers[5]

            parser.set_latitude(latitude)
            parser.set_longitude(longitude)
            parser.set_id(headers[0].tostring())
            parser.set_name()
            parser.set_platform()
            parser.set_source()
            parser.set_elevation(altitude)
            parser.set_valid_fields()
            parser.set_errors()
            parser.set_warnings()
            parser.set_sequence_number()
            parser.set_duplicates()
            parser.set_is_sounding()
            parser.set_bogus()
            parser.set_discard()
            parser.set_unix_time()
            parser.set_julian_day()

            date = datetime.strptime(str(prepbufr.msg_date), "%Y%m%d%H")
            date_correct = date + timedelta(hours = headers[3])
            date_string = date_correct.strftime("%Y%m%d%H%M%S")
            parser.set_date_string(date_string)

            parser.set_sea_level()
            parser.set_reference_pressure()
            parser.set_ground_temperature()
            parser.set_sst()
            parser.set_psfc()
            parser.set_precipitation()
            parser.set_max_temp()
            parser.set_min_temp()
            parser.set_min_night_temp()
            parser.set_h3_pressure()
            parser.set_h24_pressure()
            parser.set_cloud_cover()
            parser.set_ceiling()

            index_level = 0
            for level in range(observations.shape[-1]):
                # Para os tipos desejados ('ADPSFC' e 'SFCSHP'), há 1 level (observação) 
                # por subset. Mas para 'ADPUPA', por exemplo, pode haver vários. 

                # Algumas variáveis importantes são extraídas
                pressao   = observations[0,level]

                # Faz algumas validações e processamentos nessas variáveis.
                # Dependendo do tipo da mensagem, o valor a ser usado pode variar.
                # Para os tipos interessados ('ADPSFC', 'SFCSHP'), elas não parecem importar.
                # TODO: compreender melhor essas transformações. Os comentários são originais.

                # use balloon drift lat/lon/time for sondes, pibals
                # in obid string.
                if headers[4] in [120,220,221]:
                    longitude = observations[11,level]; latitude = observations[12,level]
                    # only use drift corrected time if it is within
                    # assimilation window.
                    if observations[13,level] >= hora_min and observations[13,level] < hora_max:
                        hora = observations[13,level]
                elif headers[4] >= 223 and headers[4] <= 228:
                    altitude = observations[3,level] # use zob, not station elev



                # Mais uma validação: verifica se a observação não é repetida.
                # Usa um identificador composto por: 
                #     Id da estacao: headers[0].tostring()
                #     Subtipo:       headers[4]

                identificador_observacao = "%s %3i %6.2f %6.2f %9.5f %5i %6.1f" % \
                    (headers[0].tostring(), headers[4], longitude, latitude, hora, int(altitude), pressao)
                
                # Se o identificador estiver no conjunto de identificadores, ele já 
                # apareceu alguma vez portanto é repetido. Set é uma estrutura de dados
                # que não aceita repetição.
                if identificador_observacao not in conjunto_identificadores_observacoes:
                    conjunto_identificadores_observacoes.add(identificador_observacao)
                else:
                    print('Ignorando observacao: {}'.format(identificador_observacao))
                    continue

                if (type(observations[0,level]) == np.ma.core.MaskedConstant):
                    parser.set_obs_pressure(index_level)
                else:
                    parser.set_obs_pressure(index_level, observations[0,level])

                if (type(observations[3,level]) == np.ma.core.MaskedConstant):
                    parser.set_obs_height(index_level)
                else:
                    parser.set_obs_height(index_level, observations[3,level])
                
                # Arquivos prepbufr possuem algo chamado Virtual Temperature.
                # Alguns documentos dizem para usá-lo em vez da temperatura 
                # observada (mnemônico: 'TOB'), porém, quando testei, ambos 
                # eram exatamente iguais.
                # TODO: validar a diferença e aplicação do Virtual Temperature.
                if (type(observations[2,level]) == np.ma.core.MaskedConstant):
                    parser.set_obs_temperature(index_level)
                else:
                    parser.set_obs_temperature(index_level, observations[2,level])

                if (type(observations[9,level]) == np.ma.core.MaskedConstant):
                    parser.set_obs_dew_point(index_level)
                else:
                    parser.set_obs_dew_point(index_level, observations[9,level])

                if (type(observations[14,level]) == np.ma.core.MaskedConstant):
                    parser.set_obs_wind_speed(index_level)
                else:
                    parser.set_obs_wind_speed(index_level, observations[14,level])

                if (type(observations[15,level]) == np.ma.core.MaskedConstant):
                    parser.set_obs_wind_direction(index_level)
                else:
                    parser.set_obs_wind_direction(index_level, observations[15,level])

                parser.set_obs_wind_ew(index_level)
                parser.set_obs_wind_ns(index_level)
                parser.set_obs_relative_humidity(index_level)
                parser.set_obs_thickness(index_level)

                # Método mais importante: ele escreve a mensagem setada
                # no arquivo de destino, em littler.
                parser.dump_littler(littler)

                # A partir daqui, esse level/observação é válido! 
                index_level += 1

            # Acumula o número de observações desse subset para a mensagem
            numero_observacoes_mensagem += index_level

        print('Escrevendo mensagem {:d} de {:d}, com {:d} observacoes e cujo tipo eh {:s}'.format(
            index_mensagem, numero_mensagens, numero_observacoes_mensagem, prepbufr.msg_type
        ))

    # Fecha todos os arquivos usados
    prepbufr.close(); littler.close()
