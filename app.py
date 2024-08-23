import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
from bs4 import BeautifulSoup
import requests
from datetime import datetime

df_dxy = pd.read_csv('dxy_daily_2023_marketwatch.csv')
df_xau = pd.read_csv('xauusd_daily_2023_metaquotesdemo.csv')
df_eur = pd.read_csv('eurusd_daily_2023_metaquotesdemo.csv')
df_gbp = pd.read_csv('gbpusd_daily_2023_metaquotesdemo.csv')
df_aud = pd.read_csv('audusd_daily_2023_metaquotesdemo.csv')

artigos = pd.read_csv('artigos_coletados.csv')

# armazenar 'data e fechamento diário' num dataframe independente
df_dxy_close = df_dxy[['date', 'close']].copy()
df_xau_close = df_xau[['date', 'close']].copy()
df_eur_close = df_eur[['date', 'close']].copy()
df_gbp_close = df_gbp[['date', 'close']].copy()
df_aud_close = df_aud[['date', 'close']].copy()

# converter valores na coluna data em tipo datetime de ambos dataframes
df_xau_close['date'] = pd.to_datetime(df_xau_close['date'])
df_dxy_close['date'] = pd.to_datetime(df_dxy_close['date'])
df_eur_close['date'] = pd.to_datetime(df_eur_close['date'])
df_gbp_close['date'] = pd.to_datetime(df_gbp_close['date'])
df_aud_close['date'] = pd.to_datetime(df_aud_close['date'])
artigos['date'] = pd.to_datetime(artigos['date'])
# ordenar valores no dataframe do índice do dólar
df_dxy_close = df_dxy_close.sort_values(by='date')

# DEFININDO ALTA VOLATILIDADE -----------------------------------------------------------------
df_xau_close['diferenca'] = df_xau_close['close'].diff()
df_xau_close = df_xau_close.dropna()
media_df_xau = df_xau_close['diferenca'].mean()
desvio_padrao_xau = df_xau_close['diferenca'].std()
limite_volatilidade = media_df_xau + desvio_padrao_xau
alta_volatilidade_xau = df_xau_close[df_xau_close['diferenca'] > limite_volatilidade]

fig_xau = go.Figure()
fig_xau.add_trace(go.Scatter(x=df_dxy_close['date'], y=df_dxy_close['close'], mode='lines', name='Índice do Dólar', yaxis='y1'))
fig_xau.add_trace(go.Scatter(x=df_xau_close['date'], y=df_xau_close['close'], mode='lines', name='Histórico XAUUSD', yaxis='y2'))
fig_xau.update_layout(
    title='DXY vs XAUUSD',
    xaxis_title='DATA',
    yaxis=dict(
        title='ÍNDICE DO DÓLAR',
        titlefont=dict(color='#1f77b4'),
        tickfont=dict(color='#1f77b4'),
        showgrid=True,
        gridwidth=1,
        gridcolor='#E2E2E2'
    ),
    yaxis2=dict(
        title='HISTÓRICO XAUUSD',
        titlefont=dict(color='#ff7f0e'),
        tickfont=dict(color='#ff7f0e'),
        overlaying='y',
        side='right',
        showgrid=False
    ),
    legend=dict(x=0.01, y=0.99),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='#f8f9fa'
)

fig_eur = go.Figure()
fig_eur.add_trace(go.Scatter(x=df_dxy_close['date'], y=df_dxy_close['close'], mode='lines', name='Índice do Dólar', yaxis='y1'))
fig_eur.add_trace(go.Scatter(x=df_eur_close['date'], y=df_eur_close['close'], mode='lines', name='Histórico EURUSD', yaxis='y2'))
fig_eur.update_layout(
    title='DXY vs EURUSD',
    xaxis_title='DATA',
    yaxis=dict(
        title='ÍNDICE DO DÓLAR',
        titlefont=dict(color='#1f77b4'),
        tickfont=dict(color='#1f77b4'),
        showgrid=True,
        gridwidth=1,
        gridcolor='#E2E2E2'
    ),
    yaxis2=dict(
        title='HISTÓRICO EURUSD',
        titlefont=dict(color='#ff7f0e'),
        tickfont=dict(color='#ff7f0e'),
        overlaying='y',
        side='right',
        showgrid=False
    ),
    legend=dict(x=0.01, y=0.99),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='#f8f9fa'
)

fig_gbp = go.Figure()
fig_gbp.add_trace(go.Scatter(x=df_dxy_close['date'], y=df_dxy_close['close'], mode='lines', name='Índice do Dólar', yaxis='y1'))
fig_gbp.add_trace(go.Scatter(x=df_gbp_close['date'], y=df_gbp_close['close'], mode='lines', name='Histórico GBPUSD', yaxis='y2'))
fig_gbp.update_layout(
    title='DXY vs GBPUSD',
    xaxis_title='DATA',
    yaxis=dict(
        title='ÍNDICE DO DÓLAR',
        titlefont=dict(color='#1f77b4'),
        tickfont=dict(color='#1f77b4'),
        showgrid=True,
        gridwidth=1,
        gridcolor='#E2E2E2'
    ),
    yaxis2=dict(
        title='HISTÓRICO GBPUSD',
        titlefont=dict(color='#ff7f0e'),
        tickfont=dict(color='#ff7f0e'),
        overlaying='y',
        side='right',
        showgrid=False
    ),
    legend=dict(x=0.01, y=0.99),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='#f8f9fa'
)

fig_aud = go.Figure()
fig_aud.add_trace(go.Scatter(x=df_dxy_close['date'], y=df_dxy_close['close'], mode='lines', name='Índice do Dólar', yaxis='y1'))
fig_aud.add_trace(go.Scatter(x=df_aud_close['date'], y=df_aud_close['close'], mode='lines', name='Histórico AUDUSD', yaxis='y2'))
fig_aud.update_layout(
    title='DXY vs AUDUSD',
    xaxis_title='DATA',
    yaxis=dict(
        title='ÍNDICE DO DÓLAR',
        titlefont=dict(color='#1f77b4'),
        tickfont=dict(color='#1f77b4'),
        showgrid=True,
        gridwidth=1,
        gridcolor='#E2E2E2'
    ),
    yaxis2=dict(
        title='HISTÓRICO AUDUSD',
        titlefont=dict(color='#ff7f0e'),
        tickfont=dict(color='#ff7f0e'),
        overlaying='y',
        side='right',
        showgrid=False
    ),
    legend=dict(x=0.01, y=0.99),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='#f8f9fa'
)

# figura ALTA VOLATILIDADE XAUUSD
fig_alta_volat = go.Figure()
fig_alta_volat.add_trace(go.Scatter(x=df_xau_close['date'], y=df_xau_close['close'], mode='lines', name='Histórico de Preços', yaxis='y1'))
fig_alta_volat.add_trace(go.Scatter(x=alta_volatilidade_xau['date'], y=alta_volatilidade_xau['close'], mode='markers', name='Alta Volatilidade', yaxis='y2'))
fig_alta_volat.update_layout(
    title='Alta Volatilidade no XAUUSD',
    xaxis_title='DATA',
    yaxis=dict(
        title='HISTÓRICO DE PREÇOS',
        titlefont=dict(color='#1f77b4'),
        tickfont=dict(color='#1f77b4'),
        showgrid=True,
        gridwidth=1,
        gridcolor='#E2E2E2'
    ),
    yaxis2=dict(
        title='DIAS COM ALTA VOLATILIDADE',
        titlefont=dict(color='#ff7f0e'),
        tickfont=dict(color='#ff7f0e'),
        overlaying='y',
        side='right',
        showgrid=False
    ),
    legend=dict(x=0.01, y=0.99),
    plot_bgcolor='#f8f9fa',
    paper_bgcolor='#f8f9fa'
)

app = Dash(__name__)

# layout da aplicação
app.layout = html.Div([
    html.Div([
        # seleção da relação inversa
        html.Div(style={'marginTop': 50}),
        html.H3(children='a relação inversa que o índice do dólar tem com os ativos', style={'textAlign': 'center'}),
        dcc.Dropdown(['XAU', 'EUR', 'GBP', 'AUD'], value='XAU', id='relacao_dxy',
                     style={'width': '30%', 'margin': '0 auto', 'display': 'block', 'textAlign': 'center'}),
        dcc.Graph(id='inferencia', figure=fig_xau, style={'width': '100%','height': 700})
        ]),
    
    html.Div([
        html.Div(style={'marginTop': 20}),
        html.H3(children='dias de alta volatilidade no gold', style={'textAlign': 'center'}),
        dcc.Graph(id='alta volatilidade', figure=fig_alta_volat, style={'width': '100%','height': 700})
        ]),

    html.Div([
        html.Div(style={'marginTop': 20}),
        html.H3(children='notícias relevantes por investing.com', style={'textAlign': 'center'}),
        dcc.Dropdown(id='data_volatilidade', options=[{'label': date.strftime('%d/%m/%Y'), 'value': date.strftime('%Y-%m-%d')} for date in alta_volatilidade_xau['date'].unique()],
                     style={'width': '30%', 'margin': '0 auto', 'display': 'block', 'textAlign': 'center'}),
        html.Div(id='noticias', style={'marginTop': 20, 'itemAlign': 'center'}),
        html.Div(style={'marginTop': 100})
        ]),
        
])

# callbacks da aplicação
@app.callback(
    Output('inferencia', 'figure'),
    Input('relacao_dxy', 'value')
)
def update_output(value): #função que retorna relação do dxy com outro ativos
    if value == 'XAU':
        # figura do xau
        return fig_xau
    elif value == 'EUR':
        # figura do eur
        return fig_eur
    elif value == 'GBP':
        # figura do GBP
        return fig_gbp
    elif value == 'AUD':
        # figura do AUD
        return fig_aud
    
@app.callback(
    Output('noticias', 'children'),
    Input('data_volatilidade', 'value')
)
def update_noticias(data_selecionada): #função que retorna cards dos artigos coletados
    data_filtrada = artigos[artigos['date'] == data_selecionada]
    cards = [
        html.Div([
            html.H5(row['titulo'], className='card-title'),
            html.P(row['resumo'], className='card-text'),
            html.A('Leia mais', href=row['link'], className='btn btn-primary', target='_blank')
        ],
        className='card', style={'width': '18rem', 'margin': '10px'})
        for _, row in data_filtrada.iterrows()
    ]
    return html.Div(cards, className='d-flex flex-wrap justify-content-center')

# run app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
