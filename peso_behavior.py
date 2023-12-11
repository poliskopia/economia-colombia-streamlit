import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta, datetime
import numpy as np
from plotly.subplots import make_subplots

DATE_TIME = "date/time"
FILE_NAMES = [
    "USD_COP.csv", "Fed_interest_rate.csv", "Inflation.csv", "hystorical_events.csv",
    "Oil.csv", "Fertilizantes.csv", "IPC-Colombia.csv", "Tasa-interes-Banrep.csv"
]

st.set_page_config(layout="wide")
st.cache_data.clear()

_, colc, _ = st.columns([1, 2, 1])
with colc:
    st.title("Peso Colombiano")
    st.markdown("Esta aplicación es un dashboard en Streamlit que puede ser usado "
                "para analizar el comportamiento del peso colombiano 🪙🇨🇴")
    col1, col2 = st.columns(2)
    selected_series = []
    with col1:
        d0 = st.date_input("Fecha inicial", date(2018, 1, 1))
        for series_name in ["Tasa Interés FED", "USA IPC", "WTI oil"]:
            selected = st.checkbox(series_name, value=False)
            if selected:
                selected_series.append(series_name)
    with col2:
        d1 = st.date_input("Fecha final", date(2023, 11, 30))
        for series_name in ["Urea", "IPC", "Tasa Interés Banrep"]:
            selected = st.checkbox(series_name, value=False)
            if selected:
                selected_series.append(series_name)
    st.markdown("Escoge las curvas que quieras remover o añadir a la gráfica")


def is_not_nan(x):
    if pd.isnull(x):
        a = "Forex"
    else:
        a = "Events"
    return a


def get_size(x):
    if x == "Forex":
        a = 1
    elif x == "Events":
        a = 20
    return a


@st.cache_data(persist=True)
def load_data():
    data = pd.read_csv(FILE_NAMES[0], delimiter=",")
    data["Date"] = pd.to_datetime(data["Date"], format="%d.%m.%Y")
    data["Ultimo"] = data["Ultimo"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)

    data_fed = pd.read_csv(FILE_NAMES[1], delimiter=",")
    data_fed["Date"] = pd.to_datetime(data_fed["Date"], format="%d.%m.%Y")
    data_fed["Interest"] = data_fed["Interest"].astype(float)

    data_infl = pd.read_csv(FILE_NAMES[2], delimiter=",")
    data_infl["Date"] = pd.to_datetime(data_infl["Date"], format="%d.%m.%Y")
    data_infl["Inflation"] = data_infl["Inflation"].astype(float)

    data_hist = pd.read_csv(FILE_NAMES[3], delimiter=",")
    data_hist["Date"] = pd.to_datetime(data_hist["Date"], format="%d.%m.%Y")
    data = data.merge(data_hist, on='Date', how="outer")
    data["series"] = data["Event"].apply(is_not_nan)
    data["size"] = data["series"].apply(get_size)

    data_oil = pd.read_csv(FILE_NAMES[4], delimiter=",")
    data_oil["Date"] = pd.to_datetime(data_oil["Date"])

    data_fert = pd.read_csv(FILE_NAMES[5], delimiter=";")
    data_fert["Date"] = pd.to_datetime(data_fert["Date"])
    data_fert["Urea-Bulto-40-Kg"] = data_fert["Urea-Bulto-40-Kg"]*1000
    data_fert["KCL-Bulto-50-Kg"] = data_fert["KCL-Bulto-50-Kg"]*1000
    data_fert["Fosfato-Diamonico-Bulto-50Kg"] = data_fert["Fosfato-Diamonico-Bulto-50Kg"]*1000

    data_ipc = pd.read_csv(FILE_NAMES[6], delimiter=";")
    data_ipc["Date"] = pd.to_datetime(data_ipc["Date"], format="mixed")

    data_banrep = pd.read_csv(FILE_NAMES[7], delimiter=",")
    data_banrep["Date"] = pd.to_datetime(data_banrep["Date"], format="%d/%m/%Y")
    return data, data_fed, data_infl, data_oil, data_fert, data_ipc, data_banrep


data, data_fed, data_infl, data_oil, data_fert, data_ipc, data_banrep = load_data()


def search_last_value(row):
    if row["Date"].weekday() == 5:
        value = row["Date"] - timedelta(days=1)
        return value
    elif row["Date"].weekday() == 6:
        value = row["Date"] - timedelta(days=2)
        return value
    else:
        return row["Date"]


def put_space(row):
    event = row["Event"]
    date_event = row["Date"]
    if pd.isnull(event):
        a = ""
    else:
        a = event + f" - {date_event.strftime('%B')} {date_event.day}, {date_event.year}"
    return a


def put_value_on_weekend(row):
    value_to_be_put = search_last_value(row)
    if np.isnan(row["Ultimo"]):
        return data[data["Date"] == value_to_be_put].iloc[0]["Ultimo"]
    else:
        return row["Ultimo"]


data["Ultimo"] = data.apply(put_value_on_weekend, axis=1)
data["Event"] = data.apply(put_space, axis=1)


queried_data = data.query("Date>=@d0 and Date<=@d1").sort_values(by=['Date'], ascending=True)
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig1 = px.line(
    queried_data,
    x='Date',
    y='Ultimo',
    hover_name="Ultimo",
    hover_data={"Date": False, "Ultimo": False, "series": False, "size": False}
    )
fig1.update_traces(
    line_color='#3440eb',
    line_width=1,
    name="Dolar a COP",
    showlegend=True,
    yaxis="y1",
    hoverlabel=dict(font_size=16)
    )
fig.add_trace(list(fig1.select_traces())[0])

fig2 = px.scatter(
    queried_data[queried_data["Event"] != ""].dropna(how="any"),
    x='Date',
    y='Ultimo',
    hover_name="Event",
    hover_data={"Date": False, "Ultimo": False, "series": False, "size": False}
    )
fig2.update_traces(marker=dict(size=9, color="#3440eb", line=dict(width=1, color='DarkSlateGrey')),
                   selector=dict(mode='markers'),
                   name="Eventos históricos", showlegend=True, yaxis="y1", hoverlabel=dict(font_size=16))
fig.add_trace(list(fig2.select_traces())[0])

queried_data_fed = data_fed.query("Date>=@d0 and Date<=@d1").sort_values(by=['Date'], ascending=True)
fig3 = px.line(queried_data_fed,
               x='Date',
               y='Interest',
               hover_name="Interest",
               hover_data={"Date": False, "Interest": False})
fig3.update_traces(
    line_color='#34eb5b',
    line_width=1,
    line=dict(dash="dot", width=1),
    name="Tasa Interés FED",
    showlegend=True,
    yaxis="y2",
    hoverlabel=dict(font_size=16)
    )
if "Tasa Interés FED" in selected_series:
    fig.add_trace(list(fig3.select_traces())[0])


queried_data_infl = data_infl.query("Date>=@d0 and Date<=@d1").sort_values(by=['Date'], ascending=True)
fig4 = px.line(queried_data_infl,
               x='Date',
               y='Inflation',
               hover_name="Inflation",
               hover_data={"Date": False, "Inflation": False})
fig4.update_traces(
    line_color='#34eb5b',
    line_width=1,
    name="USA IPC",
    showlegend=True,
    yaxis="y2",
    hoverlabel=dict(font_size=16)
    )
if "USA IPC" in selected_series:
    fig.add_trace(list(fig4.select_traces())[0])


queried_data_oil = data_oil.query("Date>=@d0 and Date<=@d1").sort_values(by=['Date'], ascending=True)
fig5 = px.line(queried_data_oil,
               x='Date',
               y='WTI',
               hover_name="WTI",
               hover_data={"Date": False, "WTI": False})
fig5.update_traces(
    line_color='#fcba03',
    line_width=1,
    name="WTI oil",
    yaxis="y3",
    showlegend=True,
    hoverlabel=dict(font_size=16)
    )
if "WTI oil" in selected_series:
    fig.add_trace(list(fig5.select_traces())[0])

queried_data_fert = data_fert.query("Date>=@d0 and Date<=@d1").sort_values(by=['Date'], ascending=True)
fig6 = px.line(
    queried_data_fert,
    x='Date',
    y='Urea-Bulto-40-Kg',
    hover_name="Urea-Bulto-40-Kg",
    hover_data={"Date": False, "Urea-Bulto-40-Kg": False}
    )
fig6.update_traces(
    line_color='#fc0384',
    line_width=1,
    name="Urea-Bulto-40-Kg",
    yaxis="y4",
    showlegend=True,
    hoverlabel=dict(font_size=16)
    )
if "Urea" in selected_series:
    fig.add_trace(list(fig6.select_traces())[0])

queried_data_ipc = data_ipc.query("Date>=@d0 and Date<=@d1").sort_values(by=['Date'], ascending=True)
fig7 = px.line(
    queried_data_ipc,
    x='Date',
    y='Variacion-ano-corrido',
    hover_name="Variacion-ano-corrido",
    hover_data={"Date": False, "Variacion-ano-corrido": False}
    )
fig7.update_traces(
    line_color='#07fab9',
    line_width=1,
    name="IPC Colombia",
    yaxis="y2",
    showlegend=True,
    hoverlabel=dict(font_size=16)
    )
if "IPC" in selected_series:
    fig.add_trace(list(fig7.select_traces())[0])


queried_data_banrep = data_banrep.query("Date>=@d0 and Date<=@d1").sort_values(by=['Date'], ascending=True)
fig8 = px.line(
    queried_data_banrep,
    x='Date',
    y='Tasa',
    hover_name="Tasa",
    hover_data={"Date": False, "Tasa": False}
    )
fig8.update_traces(
    line_color='#f22c8f',
    line_width=1,
    name="Tasa Banrep",
    yaxis="y2",
    showlegend=True,
    hoverlabel=dict(font_size=16)
    )
if "Tasa Interés Banrep" in selected_series:
    fig.add_trace(list(fig8.select_traces())[0])

month_formatter = [datetime(y, m, 1) for m in range(1, 13) for y in range(2018, 2024)]
fig.update_layout(
    yaxis=dict(title="USD a COP", titlefont=dict(color="#3440eb"), tickfont=dict(color="#3440eb")),
    yaxis2=dict(
        title="Interés (%)",
        titlefont=dict(color="#34eb5b"),
        tickfont=dict(color="#34eb5b"),
        overlaying="y",
        side="right",
        position=0.15
        ),
    legend=dict(x=1.1, y=0.5),
    yaxis3=dict(
        title="Precio Petróleo WTI (USD)",
        titlefont=dict(color="#fcba03"),
        tickfont=dict(color="#fcba03"),
        overlaying="y",
        side="left",
        anchor="free",
        autoshift=True
        ),
    yaxis4=dict(
        title="Precio Urea (COP)",
        titlefont=dict(color="#fc0384"),
        tickfont=dict(color="#fc0384"),
        overlaying="y",
        side="left",
        anchor="free",
        autoshift=True
        ),
    xaxis=dict(
        domain=[0, 1],
        tickmode="array",
        tickvals=month_formatter,
        ticktext=[dt.strftime("%b,  %Y") for dt in month_formatter],
        tickangle=90
        )
    )

for tickval in month_formatter:
    cond_1 = tickval.strftime("%Y-%m-%d") >= d0.strftime("%Y-%m-%d")
    cond_2 = tickval.strftime("%Y-%m-%d") <= d1.strftime("%Y-%m-%d")
    if cond_1 and cond_2:
        fig.add_shape(
            type="line",
            x0=tickval,
            x1=tickval,
            y0=queried_data['Ultimo'].min(),
            y1=queried_data['Ultimo'].max(),
            line=dict(color="gray", width=1, dash="dash"),
        )
st.plotly_chart(fig, use_container_width=True)

_, colc, _ = st.columns([1, 2, 1])
with colc:
    st.markdown("# Fuentes")
    st.markdown("[Precio Petróleo Crudo](https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm)")
    st.markdown("[Dólar a COP](https://es.investing.com/currencies/usd-cop-historical-data)")
    st.markdown("[Fertilizantes](https://www.fedegan.org.co/estadisticas/precios)")
    st.markdown("[Inflación Colombia](https://www.banrep.gov.co/es/estadisticas/precios-e-inflacion)")
    st.markdown("[Tasa interés BANREP](https://www.banrep.gov.co/es/estadisticas/tasas-interes-politica-monetaria)")
