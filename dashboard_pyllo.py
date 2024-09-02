# %% [markdown]
# BIBLIOTECAS

# %%
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime as dt
import numpy as np
import unidecode
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# %% [markdown]
# EXTRAÇÃO DOS DADOS

# %%
#   Dados de acesso PostgreSQL
trt_name = 'automatiza_metricas_dev'
trt_user = 'automatiza'
trt_password = 'automatiza'
trt_host = '10.5.15.78'
trt_port = '5432'

#   Acessa o banco de dados e cria a engine
db_url = f'postgresql+psycopg2://{trt_user}:{trt_password}@{trt_host}:{trt_port}/{trt_name}'
engine = create_engine(db_url)

#   Seleciona as tabelas
query_cartoes = "SELECT * FROM cartoes"
query_checklists = "SELECT * FROM checklists"
query_listas = "SELECT * FROM listas"
query_quadros = "SELECT * FROM quadros"

#   Armazena tabelas em dataframes
df_cartoes = pd.read_sql(query_cartoes, engine)
df_checklists = pd.read_sql(query_checklists, engine)
df_listas = pd.read_sql(query_listas, engine)
df_quadros = pd.read_sql(query_quadros, engine)

#   Copia de segurança das tabelas
quadros = df_quadros.copy()
listas = df_listas.copy()
cartoes = df_cartoes.copy()
checklists = df_checklists.copy()

# %% [markdown]
# TRANSFORMAÇÃO DOS DADOS

# %%
#   Renomear coluna "nome" das tabelas
quadros.rename(columns={'nome': 'quadro'}, inplace=True)
listas.rename(columns={'nome': 'lista'}, inplace=True)
cartoes.rename(columns={'nome': 'cartao'}, inplace=True)
checklists.rename(columns={'nome': 'checklist'}, inplace=True)

#   Concatenar dataframes
consolidado = quadros.merge(listas, on='id_quadro', how='outer') \
    .merge(cartoes, on='id_lista', how='outer') \
        .merge(checklists, on='id_cartao', how='outer')

#   Tratar valores nulos
consolidado['data_inicio'] = consolidado['data_inicio'].fillna(consolidado['data_fim'])
consolidado['data_fim'] = consolidado['data_fim'].fillna(consolidado['data_inicio'])
consolidado[['data_inicio', 'data_fim']] = consolidado[['data_inicio', 'data_fim']].fillna(pd.Timestamp('01-01-1900'))
consolidado['lead_time'] = consolidado['lead_time'].replace('', np.nan).replace(0, np.nan).fillna(1)
consolidado['descricao'] = consolidado['descricao'].replace('', np.nan).fillna('sem descricao')
consolidado['id_lista'] = consolidado['id_lista'].replace('', np.nan).fillna('sem lista')
consolidado['lista'] = consolidado['lista'].replace('', np.nan).fillna('sem lista')
consolidado['id_cartao'] = consolidado['id_cartao'].replace('', np.nan).fillna('sem cartao')
consolidado['cartao'] = consolidado['cartao'].replace('', np.nan).fillna('sem cartao')
consolidado['id_checklist'] = consolidado['id_checklist'].replace('', np.nan).fillna('sem checklist')
consolidado['checklist'] = consolidado['checklist'].replace('', np.nan).fillna('sem checklist')
consolidado['quant_itens'] = consolidado['quant_itens'].replace('', np.nan).fillna(0)

#   Padronizar textos em series
def processar_texto(texto):
    texto = texto.lower() # letras minusculas
    texto = unidecode.unidecode(texto) # remove acentuação
    return texto
consolidado['lista'] = consolidado['lista'].apply(processar_texto)
consolidado['checklist'] = consolidado['checklist'].apply(processar_texto)

#   Converter tipos de dados
consolidado['data_inicio'] = pd.to_datetime(consolidado['data_inicio'], format='%d-%m-%Y')
consolidado['data_fim'] = pd.to_datetime(consolidado['data_fim'], format='%d-%m-%Y')
consolidado['lead_time'] = consolidado['lead_time'].astype(int)
consolidado['quant_itens'] = consolidado['quant_itens'].astype(int)

#   Tratar itens de checklist: bugs e testes (estebelecer um padrão)
consolidado['checklist'] = consolidado['checklist'] \
    .replace(to_replace=r'.*bug.*', value='bug', regex=True) \
        .replace(to_replace=r'.*teste.*', value='teste', regex=True)



# %% [markdown]
# ANÁLISE EXPLORATÓRIA

# %%
#consolidado.to_csv('consolidado.csv', index=False)
#consolidado.to_excel('consolidado.xlsx', index=False)
#display(consolidado.info())
#display(consolidado.head(3))
#display(consolidado[consolidado['data_inicio'] == '01-01-1900'])
#display(consolidado['lista'].value_counts())
#display(consolidado[consolidado['quadro'] == 'Testes Pyllo'].head(12))
#display(consolidado[consolidado['checklist'].str.contains('teste', case=False)])
#display(consolidado['quadro'][consolidado['checklist'].str.contains('teste', case=False)])
#display(consolidado['lead_time'].describe())
#display(consolidado['checklist'].value_counts())
#display(consolidado[['quadro', 'cartao', 'lead_time']].head(5))


# %% [markdown]
# CONFIGURAÇÕES DAS FIGURAS

# %%
#   Dados a serem inseridos nas figuras
tarefas_quadro = consolidado.groupby('quadro').size().reset_index(name = 'total_cartoes')
leadtime_tarefas = consolidado[['quadro', 'cartao','data_inicio', 'data_fim', 'lead_time', 'checklist']]
"""
checklist_interessada = consolidado[consolidado['checklist'].isin(['bug', 'teste'])]
bugs_encontrados = checklist_interessada['checklist'].str.contains('bug').sum()
testes_encontrados = checklist_interessada['checklist'].str.contains('teste').sum()
"""
#   FIGURAS ESTÁTICAS
#   Total de tarefas por quadro
fig_tarefasconcluidas = go.Figure(go.Bar(
    x = tarefas_quadro['total_cartoes'],
    y = tarefas_quadro['quadro'],
    orientation = 'h',
    text = tarefas_quadro['total_cartoes'],
    textposition = 'auto',
    textangle = 0
    ))
fig_tarefasconcluidas.update_layout(
    title = {
        'text': "TOTAL DE CARTÕES POR QUADRO",
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
        },
    xaxis_title =  "TAREFAS CONCLUÍDAS",
    yaxis = dict(categoryorder = 'total ascending'),
    uniformtext_minsize = 8,
    uniformtext_mode = 'hide'
)
"""
#   Tempo de tarefas concluídas
fig_leadtime = go.Figure(go.Scatter(
    y = leadtime_tarefas['lead_time'],
    mode = 'markers',
    customdata = list(zip(leadtime_tarefas['quadro'], leadtime_tarefas['lead_time'])),
    hovertemplate = '%{customdata[0]}<br>' +
                  '%{customdata[1]} dias<br>' +
                  '<extra></extra>'
    ))
fig_leadtime.update_layout(
    title = {
        'text': "LEAD TIME",
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
        },
    yaxis_title = "TEMPO DE TAREFA (DIAS)",
    xaxis_title = "TAREFAS CONCLUÍDAS"
)

#   Bugs e testes encontrados em checklists
fig_bugteste = go.Figure(go.Bar(
    x = checklist_interessada['checklist'],
    y = [bugs_encontrados, testes_encontrados],
    text = [bugs_encontrados, testes_encontrados]
    ))
fig_bugteste.update_layout(
    title = {
        'text': "BUGS E TESTES",
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
        },
    xaxis_title= "CHECKLIST",
    yaxis_title="REGISTRADOS"
)

#   Quadro Lead Time
quadro_leadtime = [
    html.H5(f"Todos os Quadros", style={'text-align':'center'}),
    dbc.ListGroupItem(f"Lead time médio: {leadtime_tarefas['lead_time'].count().astype(int)} dias"),
    dbc.ListGroupItem(f"Lead time médio: {leadtime_tarefas['lead_time'].mean().astype(int)} dias"),
    dbc.ListGroupItem(f"Mínimo: {leadtime_tarefas['lead_time'].min().astype(int)} dias"),
    dbc.ListGroupItem(f"Máximo: {leadtime_tarefas['lead_time'].max().astype(int)} dias")
    ]

leadtime_filtrado = leadtime_tarefas[
    (leadtime_tarefas['quadro'] == 'Testes Pyllo') &
    (leadtime_tarefas['data_inicio'] >= '2024-08-01') &
    (leadtime_tarefas['data_fim'] <= '2024-08-30')
    ]
"""

# %% [markdown]
# LAYOUT DA DASHBOARD

# %%
BS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
app = Dash(__name__, external_stylesheets=[BS])

#   LAYOUT
app.layout = dbc.Container(
    [
        #    Primeira linha
        dbc.Row(
            html.H4('DASHBOARD PYLLO', style={'text-align':'center','margin-top':'20px'})
        ),
        #    Segunda linha
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="quadro_escolhido",
                        placeholder="Selecione o quadro",
                        options=leadtime_tarefas['quadro'].unique()
                        ),
                    width={"size":3, 'offset':1}
                ),
                dbc.Col(
                    dbc.Input(id="data_inicio", type="date", value=dt.today().date().replace(day=1)),
                    width={"size": 2}
                ),
                dbc.Col(
                    dbc.Input(id="data_fim", type="date", value=dt.today().date()),
                    width={"size":2}
                )
            ], className="mt-5", justify='center'
        ),
        #    Terceira linha
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(figure=fig_tarefasconcluidas), width={"size":3}
                ),
                dbc.Col(
                    dcc.Graph(id='figura_leadtime'), width={"size":5}
                ),
                dbc.Col(
                    dbc.ListGroup(id='quadro_leadtime'), width={"size":2}, style={'margin-top':'3%'}
                ),
                dbc.Col(
                    dcc.Graph(id='figura_bugteste'), width={"size": 2}
                )
            ], className="mt-5", justify='center'
        )
    ], fluid=True, className="dbc"
)


# %% [markdown]
# CALLBACKS

# %%
#   Filtrar dashboard por quadro e período
@app.callback(
    Output('figura_leadtime','figure'),
    Output('quadro_leadtime', 'children'),
    Output('figura_bugteste', 'figure'),
    Input('quadro_escolhido', 'value'),
    Input('data_inicio', 'value'),
    Input('data_fim', 'value')
)
def filtrar_leadtime(quadro_escolhido, data_inicio, data_fim):
    if data_inicio and data_fim:
        leadtime_filtrado = leadtime_tarefas[
            (leadtime_tarefas['data_inicio'] >= data_inicio) &
            (leadtime_tarefas['data_fim'] <= data_fim)
            ]
        if quadro_escolhido is None:
            quadro_escolhido = "Todos os Quadros"
        else:
            leadtime_filtrado = leadtime_filtrado[leadtime_filtrado['quadro'] == quadro_escolhido]
    #   Figura leadtime
    fig_leadtime_att = go.Figure(go.Scatter(
    y = leadtime_filtrado['lead_time'],
    mode = 'markers',
    customdata = list(zip(leadtime_filtrado['quadro'], leadtime_filtrado['lead_time'])),
    hovertemplate = '%{customdata[0]}<br>' + '%{customdata[1]} dias<br>' + '<extra></extra>'
    ))
    fig_leadtime_att.update_layout(
        title = {
            'text': "LEAD TIME",
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
            },
        yaxis_title = "TEMPO DE TAREFA (DIAS)",
        xaxis_title = "TAREFAS CONCLUÍDAS",
    )
    #   Quadro estatístico
    lead_mean = leadtime_filtrado['lead_time'].mean()
    lead_max = leadtime_filtrado['lead_time'].max()
    lead_min = leadtime_filtrado['lead_time'].min()
    lead_count = leadtime_filtrado['lead_time'].count()
    if pd.isna(lead_mean) and pd.isna(lead_max) and pd.isna(lead_min):
        lead_mean_str = "0"
        lead_max_str = "0"
        lead_min_str = "0"
        lead_count_str = "0"
    else:
        lead_mean_str = f"{int(lead_mean)} dias"
        lead_max_str = f"{int(lead_max)} dias"
        lead_min_str = f"{int(lead_min)} dias"
        lead_count_str = f"{int(lead_count)}"
    quadro_leadtime_att = [
        html.H5(f"{quadro_escolhido}", style={'text-align':'center'}),
        dbc.ListGroupItem(f"Tarefas concluídas: {lead_count_str}"),
        dbc.ListGroupItem(f"Lead time médio: {lead_mean_str}"),
        dbc.ListGroupItem(f"Lead time mínimo: {lead_min_str}"),
        dbc.ListGroupItem(f"Lead time máximo: {lead_max_str}")
        ]
    #   Figura bugs e testes encontrados
    bugs = leadtime_filtrado['checklist'].str.contains('bug').sum()
    testes = leadtime_filtrado['checklist'].str.contains('teste').sum()
    fig_bugteste_att = go.Figure(go.Bar(
        x=['bug', 'teste'],
        y = [bugs, testes],
        text = [bugs, testes]
        ))
    fig_bugteste_att.update_layout(
        title = {
            'text': "BUGS E TESTES",
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
            },
        xaxis_title= "CHECKLIST",
        yaxis_title="REGISTRADOS"
    )
    return fig_leadtime_att, quadro_leadtime_att, fig_bugteste_att

# %%
#    Rodar APP
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)


