import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import ast
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import zipfile
import time

# -----------------------------------
# Variáveis
# -----------------------------------

# Datas
data_final =  datetime.now()
data_inicial = datetime.combine((data_final - timedelta(days=14)).date(), datetime.min.time())
formato_iso = "%Y-%m-%dT%H:%M:%S+00:00"
start_date = data_inicial.strftime(formato_iso)
end_date = data_final.strftime(formato_iso)
data_hoje = datetime.today()
data_15_dias = (data_hoje - timedelta(days=15))
data_12_meses = data_hoje - timedelta(days=365)

#IDs
project_id = "1998367459"
query_id = "2001971168"
monitoramentoId = "684"

# Filtros
params = {
    "queryId": query_id,
    "startDate": start_date,
    "endDate": end_date,
    "language": "pt",
    "pageType": ["news",
        "qq",
        "youtube",
        "facebook",
        "tumblr",
        "instagram_public",
        "instagram",
        "blog",
        "forum",
        "facebook_public",
        "twitter",
        "review",
        "tiktok",
        "reddit"],
    "search": 'NOT norte NOT tropas NOT forças NOT sul NOT bases NOT universidades NOT Latino NOT misseis NOT israel NOT sul-americanas NOT Hamas NOT Israel NOT Taylor NOT estadunidense NOT canção NOT estadounidense NOT DEnver NOT Freire NOT melatonina NOT sanções americanas NOT cidade americanas NOT bolsas americanas NOT naciones americanas NOT ligas americanas NOT garotas americanas NOT instituições americanas NOT ações americanas NOT digitais americanas NOT baixas americanas NOT rádios americanas NOT eleições americanas NOT bilheterias americanas NOT virgenes americanas NOT marcas americanas NOT panquecas americanas NOT bandeiras americanas NOT republicas americanas NOT clássicas americanas NOT empresas americanas NOT franquias americanas NOT aéreas americanas NOT playlists americanas NOT cidades americanas NOT de americanas NOT techs americanas NOT estaduais americanas NOT embaixadas americanas NOT ferrovias americanas NOT séries americanas NOT faculdades americanas NOT mãos americanas NOT milhas americanas NOT nativas americanas NOT autoridades americanas NOT primárias americanas NOT elites americanas NOT minhas americanas NOT sociedades americanas NOT crianças americanas NOT urnas americanas NOT eleições americanas NOT armys americanas NOT wars americanas NOT essas americanas NOT as americanas NOT intervenções americanas NOT fazendas americanas NOT 2023 americanas NOT pan-americanas NOT premiações americanas NOT produções americanas NOT leis americanas NOT meninas americanas NOT trans americanas NOT virgens americanas NOT artistas americanas NOT agências Americanas NOT munições americanas NOT academias americanas NOT expulsões americanas NOT novelas americanas NOT doenças americanas NOT bombas americanas NOT primarias americanas NOT limeira, americanas NOT professoras americanas NOT tech americanas NOT nativo-americanas NOT maçãs americanas NOT obras americanas NOT palavras americanas NOT gol NOT terras americanas NOT militares americanas NOT importações americanas NOT mulheres americanas NOT salas americanas NOT polêmicas americanas NOT artilharias americanas NOT banheiras americanas NOT equipes americanas NOT petrolíferas americanas NOT latrino-americanas NOT influenciadoras americanas NOT subcelebs americanas NOT em americanas NOT narração americanas NOT concorrentes americanas NOT libertárias americanas NOT invasões americanas NOT plataformas americanas NOT músicas americanas NOT rádios americanas NOT escolas americanas NOT aquelas americanas NOT ibero-americanas NOT gangues americanas NOT narrativas americanas NOT jornalistas americanas NOT prisões americanas NOT vidas americanas NOT "Tiny beam fund" NOT las americanas NOT tasas americanas NOT y americanas NOT us americanas NOT personalidades americanas NOT gravadoras americanas NOT acciones americanas NOT 🇺🇸 americanas NOT bolas americanas NOT cores americanas NOT aeronaves americanas NOT sanciones americanas NOT eleitorais americanas NOT startups americanas NOT insignias americanas NOT decisões americanas NOT placas americanas NOT siamesas americanas NOT sociais americanas NOT paradas americanas NOT prótesis americanas NOT bandas americanas NOT loiras americanas NOT prisones americanas NOT competições americanas NOT tierras americanas NOT ferias americanas NOT electorales americanas NOT prisiones americanas NOT armas americanas NOT putitas americanas NOT son americanas NOT estradas americanas NOT redes americanas NOT datas americanas NOT texas americanas NOT principais americanas NOT uvas americanas NOT asesoramiento americanas NOT tribos americanas NOT quadras americanas NOT coisas americanas NOT and americanas NOT pelis americanas NOT filhas americanas NOT pecuaria americanas NOT firmas americanas NOT internacionais americanas NOT european americanas NOT banderas americanas NOT tiendas americanas NOT organizações americanas NOT series americanas NOT personas americanas NOT peliculas americanas NOT afro-americanas NOT tarifas NOT "taxas americanas"'
}

filtros = [
    {"id": "648", "nome": "LEMANN - 15 DIAS"},
    {"id": "656", "nome": "SICUPIRA - 15 DIAS"},
    {"id": "663", "nome": "TELLES - 15 DIAS"},
    {"id": "708", "nome": "LEMANN - 90 DIAS"},
    {"id": "713", "nome": "SICUPIRA - 90 DIAS"},
    {"id": "710", "nome": "TELLES - 90 DIAS"},
    {"id": "1665", "nome": "FUNDAÇÃO LEMANN"},
    {"id": "1666", "nome": "BURGER KING"},
    {"id": "1668", "nome": "3G CAPITAL"},
    {"id": "1669", "nome": "AMBEV"},
    {"id": "1670", "nome": "KRAFT HEINZ"},
]

# -----------------------------------
# Funções
# -----------------------------------


def formatar_data(data, formato_data="%d/%m/%Y"):
   return data.strftime(formato_data)

def requisicao_get(url, headers=None, params=None):
    """
    Faz uma requisição GET genérica a qualquer URL, com suporte a headers e parâmetros.

    Parâmetros:
    - url (str): URL completa da requisição.
    - headers (dict, opcional): Cabeçalhos da requisição.
    - params (dict, opcional): Parâmetros de query string.

    Retorna:
    - dict com os dados em caso de sucesso.
    - None em caso de erro.
    """
    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            print("✅ Requisição realizada com sucesso!")
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def contador_regressivo(segundos, mensagem="⏳ Aguardando..."):
    contagem = st.empty()
    for i in range(segundos, 0, -1):
        contagem.markdown(f"{mensagem} **{i} segundos restantes...**")
        time.sleep(1)
    contagem.markdown("✅ Tempo de espera finalizado.")

@st.cache_data(show_spinner="🔄 Carregando dados V-tracker...")
def gerar_dash_id(filtro, filtro_id, nome, max_tentativas=5, intervalo_entre_tentativas=120):
    for tentativa in range(1, max_tentativas + 1):
        url_gerar_dash = f"http://developers.vtracker.com.br/api/rest/graficos/gerarDash?key={chave}&monitoramentoId={monitoramentoId}&filtroId={filtro_id}"
        resposta = requisicao_get(url_gerar_dash)

        if resposta["conteudo"].startswith("dash_"):
            st.success(f"Dash_id gerado com sucesso para o filtro {nome}")
            filtro["dash_id"] = resposta["conteudo"]
            return filtro
        else:
            st.warning(f"Tentativa {tentativa}/{max_tentativas} falhou para o filtro '{nome}'. Tentando novamente em {intervalo_entre_tentativas} segundos...")
            contador_regressivo(intervalo_entre_tentativas, mensagem=f"🔁 Tentativa {tentativa + 1} em breve...")
    
    st.error(f"❌ Erro: Não foi possível recuperar o dash_id para o filtro '{nome}' após {max_tentativas} tentativas.")
    return None

def carregar_arquivos(arquivo_1, arquivo_2, arquivo_3):
    try:
        df_historico_americanas = pd.read_excel(arquivo_1)
        df_historico_americanas['DATA'] = pd.to_datetime(df_historico_americanas['DATA'], dayfirst=True)
        # st.dataframe(df_historico_americanas.tail(15))

        df_historico_mencoes = pd.read_excel(arquivo_2)
        df_historico_mencoes['DATA'] = pd.to_datetime(df_historico_mencoes['DATA'], dayfirst=True)
        # st.dataframe(df_historico_mencoes.tail(15))

        df_historico_alcance = pd.read_excel(arquivo_3)
        df_historico_alcance['DATA INICIO'] = pd.to_datetime(df_historico_alcance['DATA INICIO'], dayfirst=True)
        df_historico_alcance['DATA FINAL'] = pd.to_datetime(df_historico_alcance['DATA FINAL'], dayfirst=True)
        # st.dataframe(df_historico_alcance.tail(15))

        st.success("✅ Arquivos carregados com sucesso!")

        return df_historico_americanas, df_historico_mencoes, df_historico_alcance
    except Exception as e:
        st.error(f"Erro ao ler os arquivos: {e}")

def carregar_dados_americanas(df_historico_americanas):
        # ----------------------------------
    # Autenticação Brandwatch
    # ----------------------------------
    url_autenticacao = f"https://api.brandwatch.com/oauth/token?username={username}&grant_type=api-password&client_id=brandwatch-api-client"
    response = requests.post(url_autenticacao, data={'password': password})

    if response.status_code == 200:
        token_data = response.json()
        print("✅ Token obtido com sucesso!")
        print(token_data)
        access_token = json.loads(response.text)['access_token']
    else:
        print("❌ Erro ao obter o token")
        print(f"Status code: {response.status_code}")
        print(response.text)

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # ----------------------------------
    # Requisição na API para pegar os dados AMERICANAS
    # ----------------------------------
    url_brandwatch = f"https://api.brandwatch.com/projects/{project_id}/data/multiAggregate/sentiment/days?aggregate=volume,reachEstimate"
    data = requisicao_get(url_brandwatch, headers=headers, params=params)
    dados_por_data = {}

    for sentimento in data["results"]:
        tipo = sentimento["name"].upper() 
        for registro in sentimento["values"]:
            data_str = registro["name"].split(" ")[0]
            volume = registro["value"]["volume"]
            alcance = registro["value"]["reachEstimate"]

            if data_str not in dados_por_data:
                dados_por_data[data_str] = {
                    "DATA": data_str,
                    "POSITIVE": 0,
                    "NEUTRAL": 0,
                    "NEGATIVE": 0,
                    "ALCANCE": 0
                }

            dados_por_data[data_str][tipo] = volume
            dados_por_data[data_str]["ALCANCE"] += alcance
    
    # ----------------------------------
    # Criação dos Dataframes para os resultados finais
    # ----------------------------------

    df_quinzena_americanas = pd.DataFrame(dados_por_data.values())
    df_quinzena_americanas["TOTAL"] = df_quinzena_americanas["POSITIVE"] + df_quinzena_americanas["NEUTRAL"] + df_quinzena_americanas["NEGATIVE"]
    df_quinzena_americanas = df_quinzena_americanas[["DATA", "POSITIVE", "NEUTRAL", "NEGATIVE", "TOTAL", "ALCANCE"]]
    df_quinzena_americanas["DATA"] = pd.to_datetime(df_quinzena_americanas["DATA"])
    df_quinzena_americanas = df_quinzena_americanas.sort_values("DATA")

    # Junta com histórico e remove duplicados
    df_americanas_atualizado = pd.concat([df_historico_americanas, df_quinzena_americanas], ignore_index=True)
    df_americanas_atualizado = df_americanas_atualizado.drop_duplicates(subset=["DATA"])
    df_americanas_atualizado = df_americanas_atualizado.sort_values("DATA").reset_index(drop=True)

    # Filtra os últimos 15 dias do df_americanas_atualizado
    hoje = datetime.now()
    inicio_periodo = hoje - timedelta(days=14)
    filtro_15_dias = df_americanas_atualizado[df_americanas_atualizado["DATA"] >= inicio_periodo]

    # Soma total dos sentimentos e alcance 
    total_positive = filtro_15_dias["POSITIVE"].sum()
    total_neutral  = filtro_15_dias["NEUTRAL"].sum()
    total_negative = filtro_15_dias["NEGATIVE"].sum()
    total_geral    = filtro_15_dias["TOTAL"].sum()
    total_alcance  = filtro_15_dias["ALCANCE"].sum()

    # Calcula porcentagens sem arredondar
    porc_positive_raw = (total_positive / total_geral) * 100
    porc_neutral_raw  = (total_neutral  / total_geral) * 100
    porc_negative_raw = (total_negative / total_geral) * 100

    # Arredonda todos 
    porc_positive = round(porc_positive_raw)
    porc_neutral  = round(porc_neutral_raw)
    porc_negative = round(porc_negative_raw)

    #  Soma provisória 
    soma_porcentagens = porc_positive + porc_neutral + porc_negative

    #  Corrige se soma ≠ 100 
    if soma_porcentagens != 100:
        residuos = {
            "POSITIVE": porc_positive_raw - porc_positive,
            "NEUTRAL": porc_neutral_raw - porc_neutral,
            "NEGATIVE": porc_negative_raw - porc_negative
        }
        diferenca = 100 - soma_porcentagens
        ajuste_em = max(residuos, key=lambda k: abs(residuos[k]))

        if ajuste_em == "POSITIVE":
            porc_positive += diferenca
        elif ajuste_em == "NEUTRAL":
            porc_neutral += diferenca
        elif ajuste_em == "NEGATIVE":
            porc_negative += diferenca


    # Cria o DataFrame final 
    df_resumo_quinzena_americanas = pd.DataFrame([{
        "NOME": "AMERICANAS",
        "POSITIVAS": total_positive,
        "NEUTRAS": total_neutral,
        "NEGATIVAS": total_negative,
        "TOTAL": total_geral,
        "% POSITIVAS": porc_positive,
        "% NEUTRAS": porc_neutral,
        "% NEGATIVAS": porc_negative,
        "ALCANCE": total_alcance
    }])

    # Garante que a coluna DATA é datetime
    df_americanas_atualizado["DATA"] = pd.to_datetime(df_americanas_atualizado["DATA"])

    #  Filtra os últimos 12 meses 
    hoje = datetime.now()
    inicio_12_meses = hoje - timedelta(days=365)
    df_12_meses = df_americanas_atualizado[df_americanas_atualizado["DATA"] >= inicio_12_meses].copy()

    #  Cria intervalo de 15 dias por linha 
    df_12_meses["QUINZENA"] = df_12_meses["DATA"].dt.to_period("D").apply(
        lambda d: d.start_time - timedelta(days=d.day % 15)
    )

    #  Agrupa por quinzena e calcula médias 
    agg_quinzenal = df_12_meses.groupby("QUINZENA").agg({
        "TOTAL": "sum",
        "ALCANCE": "sum"
    }).reset_index()

    media_total_quinzenal   = agg_quinzenal["TOTAL"].mean()
    media_alcance_quinzenal = agg_quinzenal["ALCANCE"].mean()

    #  Filtra última quinzena 
    inicio_ult_quinzena = hoje - timedelta(days=14)
    df_ult_quinzena = df_americanas_atualizado[df_americanas_atualizado["DATA"] >= inicio_ult_quinzena]

    total_quinzena   = df_ult_quinzena["TOTAL"].sum()
    alcance_quinzena = df_ult_quinzena["ALCANCE"].sum()

    #  Calcula comparativo percentual 
    comparativo_total   = round(((total_quinzena - media_total_quinzenal) / media_total_quinzenal) * 100, 2)
    comparativo_alcance = round(((alcance_quinzena - media_alcance_quinzenal) / media_alcance_quinzenal) * 100, 2)

    #  Monta o DataFrame final 
    df_comparativo_americanas = pd.DataFrame([{
        "NOME": "AMERICANAS",
        "MENCOES QUINZENA": total_quinzena,
        "ALCANCE QUINZENA": alcance_quinzena,
        "MEDIA MENCOES": round(media_total_quinzenal),
        "MEDIA ALCANCE": round(media_alcance_quinzenal),
        "COMPARATIVO MENCOES (%)": round(comparativo_total),
        "COMPARATIVO ALCANCE (%)": round(comparativo_alcance)
    }])

    # ----------------------------------
    # Visualização dos dataframes 
    # ----------------------------------
    # st.header("📋 Resultados Americanas")
    # st.subheader("Historico atualizado")
    # st.dataframe(df_americanas_atualizado.tail(20))
    # st.subheader("Resulmo da ultima quinzena")
    # st.dataframe(df_resumo_quinzena_americanas)
    # st.subheader("Comparativo com os ultimos 12 meses")
    # st.dataframe(df_comparativo_americanas)

    return df_americanas_atualizado, df_resumo_quinzena_americanas, df_comparativo_americanas

def gerar_dados_mencoes(df_historico_mencoes):
    #-------------------------------------
    # Geração de dados de MENÇÕES
    #-------------------------------------
    # Gera o gráfico somente para os filtros dos ultimos 90 dias
    tipo = "OCORRENCIASPORDIA"
    dados = {}

    for filtro in filtros:
        if "90 DIAS" in filtro['nome']:
            # Gerando o Conteudo
            url_grafico_dados = f"http://developers.vtracker.com.br/api/rest/graficos/dados?key={chave}&codigo={filtro['dash_id']}&tipo={tipo}"
            resposta = requisicao_get(url_grafico_dados)

            conteudo = resposta['conteudo']

            # Convertendo o conteudo para uma lista
            lista_dados = ast.literal_eval(f"[{conteudo.strip(',')}]")
            lista_dados = lista_dados[1:]

            # Armazenando em um dicionario
            dados_filtro = {dia: total for dia, total in lista_dados}
            dados[filtro['nome'].replace(" - 90 DIAS", "")] = dados_filtro

    df_mencoes = pd.DataFrame(dados)
    df_mencoes.fillna(0, inplace=True)
    df_mencoes.index.name = "DATA"
    df_mencoes.reset_index(inplace=True)
    df_mencoes['DATA'] = pd.to_datetime(df_mencoes['DATA'], dayfirst=True)

    # ========= Atualiza o histórico de menções ===========

    # Garantir que ambos tenham as mesas colunas
    colunas = ["DATA", "LEMANN", "SICUPIRA", "TELLES"]
    df_historico_mencoes = df_historico_mencoes[colunas]
    df_mencoes = df_mencoes[colunas]
    # Junta os dois DataFrames
    df_mencoes_atualizado = pd.concat([df_historico_mencoes, df_mencoes], ignore_index=True)
    # Remove as possiveis DATAS duplicadas
    df_mencoes_atualizado = df_mencoes_atualizado.sort_values("DATA").drop_duplicates(subset="DATA", keep="last")
    # Recalcula o total de menções por dia
    df_mencoes_atualizado["TOTAL DIA"] = df_mencoes_atualizado[["LEMANN", "SICUPIRA", "TELLES"]].sum(axis=1)
    # Ordena por DATA e reseta o índice
    df_mencoes_atualizado = df_mencoes_atualizado.sort_values("DATA").reset_index(drop=True)
    # Garantir que os valores ausentes sejam 0
    df_mencoes_atualizado.fillna(0, inplace=True)

    # ========= Gera o comparativo de mençoes dos sócios ===========

    colunas = ["LEMANN","SICUPIRA","TELLES"]
    resultado = []

    for coluna in colunas:
        # Total da quinzena
        total_quinzena = df_mencoes_atualizado.loc[df_mencoes_atualizado["DATA"] >= data_15_dias, coluna].sum()
        # Subset dos últimos 12 meses
        df_ultimos_12_meses = df_mencoes_atualizado[df_mencoes_atualizado["DATA"] >= data_12_meses]
        # Divide os 12 meses em blocos de 15 dias
        datas_ordenadas = df_ultimos_12_meses["DATA"].sort_values().unique()
        medias_quinzenas = []

        for i in range(0, len(datas_ordenadas), 15):
            bloco = df_ultimos_12_meses[df_ultimos_12_meses["DATA"].isin(datas_ordenadas[i:i+15])]
            soma_bloco = bloco[coluna].sum()
            medias_quinzenas.append(soma_bloco)

        # Calcula média das quinzenas
        media_12_meses = sum(medias_quinzenas) / len(medias_quinzenas) if medias_quinzenas else 0
        # Comparativo percentual
        if media_12_meses != 0:
            comparativo = ((total_quinzena - media_12_meses) / media_12_meses) * 100
        else:
            comparativo = 0

        # Adiciona ao resultado
        resultado.append({
            "NOME": coluna,
            "MENCOES QUINZENA": round(total_quinzena),
            "MEDIA MENCOES": round(media_12_meses),
            "COMPARATIVO MENCOES (%)": round(comparativo)
        })

    # Cria DataFrame final
    df_comparativo_mencoes_socios = pd.DataFrame(resultado)

    # st.subheader("Historio de menções atualizado")
    # st.dataframe(df_mencoes_atualizado)
    # st.subheader("Comparativo de menções dos socios nos ultimos 12 meses")
    # st.dataframe(df_comparativo_mencoes_socios)


    return df_mencoes_atualizado, df_comparativo_mencoes_socios

def gerar_dados_sentimentos():
    # -------------------------------
    # Gerar dados de SENTIMENTOS
    # -------------------------------

    # Valores necessários para atualizar o df_historico_alcance
    nova_linha = {'DATA INICIO': data_15_dias,'DATA FINAL': data_hoje}
    colunas = ["LEMANN - 15 DIAS","SICUPIRA - 15 DIAS","TELLES - 15 DIAS"]
    dados_sentimentos = []
    for item in filtros:
        # Gerando o Conteudo
        tipo = "OCORRENCIASPORQUALIFICACAO"
        url_grafico_dados = f"http://developers.vtracker.com.br/api/rest/graficos/dados?key={chave}&codigo={item['dash_id']}&tipo={tipo}"
        resposta = requisicao_get(url_grafico_dados)
        conteudo = ast.literal_eval("[" + resposta['conteudo'] + "]")

        # Salvando os dados de sentimentos
        positivas = conteudo[1][1]
        negativas = conteudo[2][1]
        neutras = conteudo[3][1]
        total = positivas +neutras + negativas

        # Calculando as porcentagens:
        pct_positivas = round((positivas / total * 100) if total else 0)
        pct_negativas = round((negativas/ total * 100) if total else 0)
        pct_neutras = round((neutras / total * 100) if total else 0)

        tipo = "TOTALPESSOASEIMPRESSAO"
        url_grafico_dados = f"http://developers.vtracker.com.br/api/rest/graficos/dados?key={chave}&codigo={item['dash_id']}&tipo={tipo}"
        resposta = requisicao_get(url_grafico_dados)
        conteudo = ast.literal_eval("[" + resposta['conteudo'] + "]")
        alcance = conteudo[1][2]
        # Salva o valor do alcance para atualizar o df_historico_alcance
        if item['nome'] in colunas:
            nome_coluna = item['nome'].replace(" - 15 DIAS", "")
            nova_linha[nome_coluna] = alcance

        resultado = {'NOME' : item['nome'],
                    'POSITIVAS' : positivas,
                    'NEUTRAS': neutras,
                    'NEGATIVAS' : negativas,
                    'TOTAL' : total,
                    '% POSITIVAS' : pct_positivas,
                    '% NEUTRAS' : pct_neutras,
                    '% NEGATIVAS' : pct_negativas,
                    'ALCANCE': alcance}

        dados_sentimentos.append(resultado)

    # Gerando o dataframe
    df_sentimentos = pd.DataFrame(dados_sentimentos)

    # st.subheader('Dados de sentimentos')
    # st.dataframe(df_sentimentos)

    return nova_linha, df_sentimentos

def gerar_dados_alcane(nova_linha, df_historico_alcance):
    # ------------------------------
    # Gerando dados de ALCANCE
    # ------------------------------
    # Adicionando os dados da ultima quinzena no Historico de alcante
    df_historico_alcance_atualizado = pd.concat([df_historico_alcance, pd.DataFrame([nova_linha])], ignore_index=True)
    # 1. Converter a coluna de data
    df_historico_alcance_atualizado['DATA FINAL'] = pd.to_datetime(df_historico_alcance_atualizado['DATA FINAL'], format="%Y-%m-%d")
    # 2. Filtrar os dados dos últimos 12 meses
    df_12_meses = df_historico_alcance_atualizado[df_historico_alcance_atualizado['DATA FINAL'] >= data_12_meses]
    # 3. Calcular a média quinzenal para cada sócio
    medias_quinzenais = df_12_meses[["LEMANN", 'SICUPIRA','TELLES']].mean()
    # 4. Pegar os valores da quinzena mais recente (DATA FINAL mais próxima de data_hoje)
    df_ordenado = df_historico_alcance_atualizado.sort_values('DATA FINAL', ascending=False)
    quinzena_atual = df_ordenado.iloc[0][["LEMANN", 'SICUPIRA','TELLES']]
    # 5. Calcular a variação percentual da quinzena atual em relação à média
    variacao_percentual = ((quinzena_atual - medias_quinzenais) / medias_quinzenais) * 100
    # 6. Criar um DataFrame com os resultados
    df_comparativo_alcance_socios = pd.DataFrame({
        'ALCANCE QUINZENA': quinzena_atual.astype(int),
        'MEDIA ALCANCE': medias_quinzenais.round().astype(int),
        'COMPARATIVO ALCANCE (%)': pd.to_numeric(variacao_percentual, errors='coerce').round().astype('Int64')
    })

    df_comparativo_alcance_socios = df_comparativo_alcance_socios.reset_index()
    df_comparativo_alcance_socios.rename(columns={"index": "NOME"}, inplace=True)

    # st.subheader('Historico de alcance atualizado:')
    # st.dataframe(df_historico_alcance_atualizado)
    # st.subheader('Comparativo de alcance dos socios nos ultimos 12 meses:')
    # st.dataframe(df_comparativo_alcance_socios)

    return df_historico_alcance_atualizado, df_comparativo_alcance_socios

def gerar_comparacao_quinzenal(df_americanas_atualizado, df_historico_mencoes):
    # --- Prepara os dataframes básicos ---
    df_americanas = df_americanas_atualizado[['DATA', 'TOTAL']].rename(columns={'TOTAL': 'TOTAL AMERICANAS'})
    df_socios = df_historico_mencoes[['DATA', 'TOTAL DIA']].rename(columns={'TOTAL DIA': 'TOTAL SOCIOS'})

    # Merge dos dataframes pela coluna DATA
    df_total_mencoes = pd.merge(df_americanas, df_socios, on='DATA')

    # Garante que DATA está como datetime
    df_total_mencoes['DATA'] = pd.to_datetime(df_total_mencoes['DATA'])

    # Ordena pela data
    df_total_mencoes = df_total_mencoes.sort_values('DATA')

    # --- Define datas de corte ---
    data_final = df_total_mencoes['DATA'].max()
    data_inicio_quinzena = data_final - pd.Timedelta(days=14)
    data_inicio_12m = data_final - pd.DateOffset(months=12)

    # --- Filtra últimos 15 dias ---
    df_quinzena = df_total_mencoes[df_total_mencoes['DATA'] > data_inicio_quinzena]
    volume_quinzena_socios = df_quinzena['TOTAL SOCIOS'].sum()
    volume_quinzena_todos = df_quinzena['TOTAL AMERICANAS'].sum() + volume_quinzena_socios

    # --- Filtra últimos 12 meses ---
    df_12m = df_total_mencoes[df_total_mencoes['DATA'] >= data_inicio_12m].copy()

    # Cria coluna de período quinzenal
    df_12m['QUINZENA'] = ((df_12m['DATA'] - df_12m['DATA'].min()).dt.days // 15)

    # Soma de cada quinzena
    df_quinzenas = df_12m.groupby('QUINZENA').agg({
        'TOTAL SOCIOS': 'sum',
        'TOTAL AMERICANAS': 'sum'
    }).reset_index()

    df_quinzenas['TOTAL TODOS'] = df_quinzenas['TOTAL SOCIOS'] + df_quinzenas['TOTAL AMERICANAS']

    # Média das 24 quinzenas
    media_quinzena_socios = df_quinzenas['TOTAL SOCIOS'].mean()
    media_quinzena_todos = df_quinzenas['TOTAL TODOS'].mean()

    # --- Calcula comparação percentual ---
    comparacao_socios = ((volume_quinzena_socios - media_quinzena_socios) / media_quinzena_socios) * 100
    comparacao_todos = ((volume_quinzena_todos - media_quinzena_todos) / media_quinzena_todos) * 100

    # --- Monta dataframe final ---
    df_total_comparacao_mencoes = pd.DataFrame({
        'VOLUME DA QUINZENA SOCIOS': [volume_quinzena_socios],
        'VOLUME DA QUINZENA TODOS': [volume_quinzena_todos],
        'MEDIA 12 MESES SOCIOS': [media_quinzena_socios],
        'MEDIA 12 MESES TODOS': [media_quinzena_todos],
        '% COMPARACAO SOCIOS': [comparacao_socios],
        '% COMPARACAO TODOS': [comparacao_todos]
    })

    return df_total_comparacao_mencoes

def gerar_graficos(df_mencoes_atualizado, df_resumo_todos, df_americanas_atualizado):
    # Criar um dicionário para armazenar os arquivos de imagem dos gráficos
    imagens = {}

    # Garante datas como datetime
    df_mencoes_atualizado['DATA'] = pd.to_datetime(df_mencoes_atualizado['DATA'])
    df_americanas_atualizado['DATA'] = pd.to_datetime(df_americanas_atualizado['DATA'])

    # === GRÁFICO 1: Últimos 15 dias (TOTAL DIA)
    df_15_dias = df_mencoes_atualizado.sort_values('DATA').tail(15)
    fig1 = plt.figure(figsize=(17.26, 2.846))
    plt.fill_between(df_15_dias['DATA'], df_15_dias['TOTAL DIA'], color='#95B3D7')
    plt.plot(df_15_dias['DATA'], df_15_dias['TOTAL DIA'], color='#95B3D7', linewidth=2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()
    buf1 = io.BytesIO()
    fig1.savefig("grafico_1.png", dpi=300, bbox_inches='tight')
    st.text('Volume de menções dos sócios nos ultimos 15 dias')
    st.pyplot(fig1)
    imagens['grafico_1.png'] = buf1.getvalue()
    plt.close(fig1)

    # === GRÁFICO 2: Últimos 3 meses (TOTAL DIA)
    data_final = df_mencoes_atualizado['DATA'].max()
    data_inicial = data_final - pd.DateOffset(months=3)
    df_3_meses = df_mencoes_atualizado[
        (df_mencoes_atualizado['DATA'] >= data_inicial) & (df_mencoes_atualizado['DATA'] <= data_final)
    ]
    fig2 = plt.figure(figsize=(17.26, 2.846))
    plt.fill_between(df_3_meses['DATA'], df_3_meses['TOTAL DIA'], color='#95B3D7')
    plt.plot(df_3_meses['DATA'], df_3_meses['TOTAL DIA'], color='#95B3D7', linewidth=2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.xticks(df_3_meses['DATA'][::2], rotation=45)
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()
    buf2 = io.BytesIO()
    fig2.savefig("grafico_2.png", dpi=300, bbox_inches='tight')
    st.text('Volume de menções dos sócios nos ultimos 3 meses')
    st.pyplot(fig2)
    imagens['grafico_2.png'] = buf2.getvalue()
    plt.close(fig2)

    # === GRÁFICO 3: Pizza - Sócios
    filtro = ['LEMANN - 90 DIAS', 'SICUPIRA - 90 DIAS', 'TELLES - 90 DIAS']
    df_filtrado = df_resumo_todos[df_resumo_todos['NOME'].isin(filtro)]
    valores = df_filtrado['TOTAL'].values
    percentuais = ((valores / valores.sum()) * 100).round(0)
    labels = ['Jorge Paulo Lemann', 'Carlos Alberto Sicupira', 'Marcel Telles']
    colors = ['#0056A6', '#4CA64C', '#56B4E9']
    fig3, ax = plt.subplots(figsize=(7.08, 7.28))
    wedges, texts, autotexts = ax.pie(
        percentuais,
        colors=colors,
        startangle=90,
        wedgeprops={'width': 0.4, 'edgecolor': 'white'},
        autopct='%1.1f%%'
    )
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig3.gca().add_artist(centre_circle)
    for text in autotexts:
        text.set_color('black')
        text.set_fontsize(12)
        text.set_weight('bold')
    ax.set_title('Volume de Menções')
    ax.axis('equal')
    plt.legend(wedges, labels, loc="lower center", bbox_to_anchor=(1, 0))
    plt.tight_layout()
    buf3 = io.BytesIO()
    fig3.savefig("grafico_3.png", dpi=300, bbox_inches='tight')
    st.text('Distribuição do volume de menções dos sócios (%)')
    st.pyplot(fig3)
    imagens['grafico_3.png'] = buf3.getvalue()
    plt.close(fig3)

    # === GRÁFICO 4: Pizza - Empresas
    empresas = ['BURGER KING', 'KRAFT HEINZ', '3G CAPITAL', 'AMBEV', 'FUNDAÇÃO LEMANN', 'AMERICANAS']
    df_filtrado_empresas = df_resumo_todos[df_resumo_todos['NOME'].isin(empresas)].copy()
    df_filtrado_empresas['PERCENTUAL'] = (df_filtrado_empresas['TOTAL'] / df_filtrado_empresas['TOTAL'].sum()) * 100
    fig4, ax = plt.subplots(figsize=(8, 6))
    wedges, texts = ax.pie(
        df_filtrado_empresas['PERCENTUAL'],
        colors=['#1f77b4', '#d62728', '#2ca02c', '#9467bd', '#17becf', '#ff7f0e'],
        startangle=90,
        counterclock=False,
        wedgeprops={'width': 0.3}
    )
    labels_legenda = [
        f"{nome}: {pct:.1f}%" for nome, pct in zip(df_filtrado_empresas['NOME'], df_filtrado_empresas['PERCENTUAL'])
    ]
    ax.legend(labels_legenda, title="Empresas", loc="center left", bbox_to_anchor=(1, 0.5))
    plt.title('Volume de Menções')
    plt.tight_layout()
    buf4 = io.BytesIO()
    fig4.savefig("grafico_4.png", dpi=300, bbox_inches='tight')
    st.text('Distribuição do volume de menções das empresas (%)')
    st.pyplot(fig4)
    imagens['grafico_4.png'] = buf4.getvalue()
    plt.close(fig4)

    # === GRÁFICOS 5, 6, 7: Linhas por sócio
    inicio_periodo = pd.Timestamp('2024-06-30')
    df_filtrado_socio = df_mencoes_atualizado[df_mencoes_atualizado['DATA'] >= inicio_periodo]
    socios = ['LEMANN', 'SICUPIRA', 'TELLES']
    for socio in socios:
        fig_socio = plt.figure(figsize=(16.71, 8.7))
        plt.fill_between(df_filtrado_socio['DATA'], df_filtrado_socio[socio], color='#95B3D7')
        plt.plot(df_filtrado_socio['DATA'], df_filtrado_socio[socio], color='#95B3D7', linewidth=2)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf5 = io.BytesIO()
        # fig_socio.savefig(f"grafico_mencoes_{socio}.png", dpi=300, bbox_inches='tight')
        st.text(f'Volume de menções desde de 30 de Junho ({socio})')
        st.pyplot(fig_socio)
        imagens[f"grafico_mencoes_{socio}.png"] = buf5.getvalue()
        plt.close(fig_socio)

    # === GRÁFICO 8: Linhas Americanas
    df_filtrado_am = df_americanas_atualizado[df_americanas_atualizado['DATA'] >= inicio_periodo]
    fig8 = plt.figure(figsize=(16.71, 8.70))
    plt.fill_between(df_filtrado_am['DATA'], df_filtrado_am['TOTAL'], color='#95B3D7')
    plt.plot(df_filtrado_am['DATA'], df_filtrado_am['TOTAL'], color='#95B3D7', linewidth=2)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf8 = io.BytesIO()
    fig8.savefig("grafico_mencoes_americanas.png", dpi=300, bbox_inches='tight')
    st.text(f'Volume de menções desde de 30 de Junho (Americanas)')
    st.pyplot(fig8)
    imagens['grafico_8.png'] = buf8.getvalue()
    plt.close(fig8)

    # Criar um arquivo ZIP na memória
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for nome_arquivo, conteudo in imagens.items():
            zip_file.writestr(nome_arquivo, conteudo)

    zip_buffer.seek(0)

    return zip_buffer

def gerar_excel_multiplas_abas(df_resumo_todos, df_comparativo_alcance_todos, df_comparativo_mencoes_todos, df_comparacao):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_resumo_todos.to_excel(writer, sheet_name='Sentimentos', index=False)
        df_comparativo_alcance_todos.to_excel(writer, sheet_name='Comparativo Alcance', index=False)
        df_comparativo_mencoes_todos.to_excel(writer, sheet_name='Comparativo Mencoes', index=False)
        df_comparacao.to_excel(writer, sheet_name='Comparacao Final', index=False)
    buffer.seek(0)
    return buffer

def gerar_excel_individual(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer

# def criar_zip_para_download():
    arquivos_zip = {}

    # Excel com múltiplas abas
    excel_completo = gerar_excel_multiplas_abas(
        df_resumo_todos, df_comparativo_alcance_todos, df_comparativo_mencoes_todos, df_comparacao
    )
    arquivos_zip["Relatorio_Quinzena.xlsx"] = excel_completo.getvalue()

    # Excels individuais
    df_americanas_atualizado['DATA'] = pd.to_datetime(df_americanas_atualizado['DATA']).dt.strftime('%d/%m/%Y')
    arquivos_zip[f"hitorico_americanas_{formatar_data(data_hoje, '%d.%m.%Y')}.xlsx"] = gerar_excel_individual(df_americanas_atualizado).getvalue()

    df_mencoes_atualizado['DATA'] = pd.to_datetime(df_mencoes_atualizado['DATA']).dt.strftime('%d/%m/%Y')
    arquivos_zip[f"hitorico_mencoes_{formatar_data(data_hoje, '%d.%m.%Y')}.xlsx"] = gerar_excel_individual(df_mencoes_atualizado).getvalue()

    df_historico_alcance_atualizado['DATA INICIO'] = pd.to_datetime(df_historico_alcance_atualizado['DATA INICIO']).dt.strftime('%d/%m/%Y')
    df_historico_alcance_atualizado['DATA FINAL'] = pd.to_datetime(df_historico_alcance_atualizado['DATA FINAL']).dt.strftime('%d/%m/%Y')
    arquivos_zip[f"hitorico_alcance_{formatar_data(data_hoje, '%d.%m.%Y')}.xlsx"] = gerar_excel_individual(df_historico_alcance_atualizado).getvalue()

    # Criar o ZIP na memória
    zip_excel = io.BytesIO()
    with zipfile.ZipFile(zip_excel, "w") as zip_file:
        for nome_arquivo, conteudo in arquivos_zip.items():
            zip_file.writestr(nome_arquivo, conteudo)
    zip_excel.seek(0)

    return zip_excel

def criar_zip_para_download():
    arquivos_zip = {}

    # Excel com múltiplas abas
    excel_completo = gerar_excel_multiplas_abas(
        st.session_state.df_resumo_todos,
        st.session_state.df_comparativo_alcance_socios,
        st.session_state.df_comparativo_mencoes_socios,
        st.session_state.df_comparacao
    )
    arquivos_zip["Relatorio_Quinzena.xlsx"] = excel_completo.getvalue()

    # Excel individual: Americanas
    df_americanas = st.session_state.df_americanas_atualizado.copy()
    df_americanas['DATA'] = pd.to_datetime(df_americanas['DATA']).dt.strftime('%d/%m/%Y')
    arquivos_zip[f"historico_americanas_{formatar_data(data_hoje, '%d.%m.%Y')}.xlsx"] = gerar_excel_individual(df_americanas).getvalue()

    # Excel individual: Menções
    df_mencoes = st.session_state.df_mencoes_atualizado.copy()
    df_mencoes['DATA'] = pd.to_datetime(df_mencoes['DATA']).dt.strftime('%d/%m/%Y')
    arquivos_zip[f"historico_mencoes_{formatar_data(data_hoje, '%d.%m.%Y')}.xlsx"] = gerar_excel_individual(df_mencoes).getvalue()

    # Excel individual: Alcance
    df_alcance = st.session_state.df_historico_alcance_atualizado.copy()
    df_alcance['DATA INICIO'] = pd.to_datetime(df_alcance['DATA INICIO']).dt.strftime('%d/%m/%Y')
    df_alcance['DATA FINAL'] = pd.to_datetime(df_alcance['DATA FINAL']).dt.strftime('%d/%m/%Y')
    arquivos_zip[f"historico_alcance_{formatar_data(data_hoje, '%d.%m.%Y')}.xlsx"] = gerar_excel_individual(df_alcance).getvalue()

    # Criar o ZIP na memória
    zip_excel = io.BytesIO()
    with zipfile.ZipFile(zip_excel, "w") as zip_file:
        for nome_arquivo, conteudo in arquivos_zip.items():
            zip_file.writestr(nome_arquivo, conteudo)
    zip_excel.seek(0)

    return zip_excel


# ============================
# Aplicativo Sreamlit
# ============================

st.title("📊 Automação de Relatório")

# ============ Autenticação ============
st.sidebar.header("🔐 Autenticação")
chave = st.sidebar.text_input("Chave da API V-Tracker", type="password")
username = st.sidebar.text_input("Login Brandwatch")
password = st.sidebar.text_input("Senha Brandwatch", type="password")

# ============ Inicialização da Session State ============
if 'dados_gerados' not in st.session_state:
    st.session_state.dados_gerados = False
if 'filtros_com_dash_id' not in st.session_state:
    st.session_state.filtros_com_dash_id = None

# ============ Main ============
if chave and username and password:
    st.header("📂 Upload de Arquivos Excel")
    arquivo_1 = st.file_uploader("📄 Envie o arquivo de histórico AMERICANAS", type=["xls", "xlsx"])
    arquivo_2 = st.file_uploader("📄 Envie o arquivo de histórico de MENÇÕES", type=["xls", "xlsx"])
    arquivo_3 = st.file_uploader("📄 Envie o arquivo de histórico de ALCANCE", type=["xls", "xlsx"])

    if arquivo_1 and arquivo_2 and arquivo_3:
        # Carregar arquivos
        st.session_state.df_historico_americanas, st.session_state.df_historico_mencoes, st.session_state.df_historico_alcance = carregar_arquivos(
            arquivo_1, arquivo_2, arquivo_3
        )

        # ============ Botão Gerar Dados ============
        if st.button("🗃️ Gerar dados"):

            st.session_state.dados_gerados = True

            # Brandwatch
            st.session_state.df_americanas_atualizado, st.session_state.df_resumo_quinzena_americanas, st.session_state.df_comparativo_americanas = carregar_dados_americanas(
                st.session_state.df_historico_americanas
            )

            # V-Tracker
            if st.session_state.filtros_com_dash_id is None:
                st.session_state.filtros_com_dash_id = []
                for filtro in filtros:
                    resultado = gerar_dash_id(filtro, filtro['id'], filtro['nome'], 5, 90)
                    if resultado:
                        st.session_state.filtros_com_dash_id.append(resultado)
            else:
                st.info("✅ Dash IDs já foram gerados nesta sessão. Pulando requisição à API.")

            filtros = st.session_state.filtros_com_dash_id

            # Menções
            st.session_state.df_mencoes_atualizado, st.session_state.df_comparativo_mencoes_socios = gerar_dados_mencoes(
                st.session_state.df_historico_mencoes
            )

            # Sentimentos
            st.session_state.nova_linha, st.session_state.df_sentimentos = gerar_dados_sentimentos()

            st.session_state.df_resumo_todos = pd.concat(
                [st.session_state.df_sentimentos, st.session_state.df_resumo_quinzena_americanas],
                ignore_index=True
            )

            # Alcance
            st.session_state.df_historico_alcance_atualizado, st.session_state.df_comparativo_alcance_socios = gerar_dados_alcane(
                st.session_state.nova_linha, st.session_state.df_historico_alcance
            )

            # Comparação final
            st.session_state.df_comparacao = gerar_comparacao_quinzenal(
                st.session_state.df_americanas_atualizado, st.session_state.df_mencoes_atualizado
            )

        # ============ Exibição e Downloads ============
        if st.session_state.dados_gerados:
            st.header('📋 Resultados gerais da quinzena')

            st.subheader("Sentimentos")
            st.dataframe(st.session_state.df_resumo_todos)

            st.subheader("Alcance")
            df_comparativo_alcance_todos = pd.concat([
                st.session_state.df_comparativo_alcance_socios,
                st.session_state.df_comparativo_americanas[['NOME', 'ALCANCE QUINZENA', 'MEDIA ALCANCE', 'COMPARATIVO ALCANCE (%)']]
            ], ignore_index=True)
            st.dataframe(df_comparativo_alcance_todos)

            st.subheader("Menções")
            df_comparativo_mencoes_todos = pd.concat([
                st.session_state.df_comparativo_mencoes_socios,
                st.session_state.df_comparativo_americanas[['NOME', 'MENCOES QUINZENA', 'MEDIA MENCOES', 'COMPARATIVO MENCOES (%)']]
            ], ignore_index=True)
            st.dataframe(df_comparativo_mencoes_todos)

            st.subheader("Comparação geral de menções")
            st.dataframe(st.session_state.df_comparacao)

            # Gráficos
            st.header('📈 Gráficos')
            zip_buffer = gerar_graficos(
                st.session_state.df_mencoes_atualizado,
                st.session_state.df_resumo_todos,
                st.session_state.df_americanas_atualizado
            )


            # Downloads
            st.download_button(
                label="📊 Baixar todos os gráficos (.zip)",
                data=zip_buffer,
                file_name="graficos.zip",
                mime="application/zip"
            )

            zip_excel = criar_zip_para_download()

            st.download_button(
                label="📁 Baixar todos os arquivos Excel (.zip)",
                data=zip_excel,
                file_name="relatorios_completos.zip",
                mime="application/zip"
            )

else:
    st.warning("🔐 Por favor, insira chave, login e senha para continuar.")

