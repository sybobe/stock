import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="최근 1년 주가 변동 분석",
    page_icon="📈",
    layout="wide"
)

st.title("📈 최근 1년 주가 변동 분석 웹앱")
st.write("삼성전자, SK하이닉스, 구글, 마이크로소프트, 애플의 최근 1년 주가 흐름을 비교합니다.")

stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "구글": "GOOGL",
    "마이크로소프트": "MSFT",
    "애플": "AAPL"
}

selected_names = st.multiselect(
    "분석할 종목을 선택하세요",
    list(stocks.keys()),
    default=list(stocks.keys())
)

end_date = datetime.today()
start_date = end_date - timedelta(days=365)

@st.cache_data
def load_stock_data(tickers, start, end):
    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )
    return data

if selected_names:
    selected_tickers = [stocks[name] for name in selected_names]

    with st.spinner("주가 데이터를 불러오는 중입니다..."):
        raw_data = load_stock_data(selected_tickers, start_date, end_date)

    if len(selected_tickers) == 1:
        close_data = raw_data[["Close"]]
        close_data.columns = selected_names
    else:
        close_data = raw_data["Close"]
        close_data = close_data.rename(
            columns={stocks[name]: name for name in selected_names}
        )

    close_data = close_data.dropna(how="all")

    st.subheader("📌 최근 종가 데이터")
    st.dataframe(close_data.tail(10), use_container_width=True)

    normalized_data = close_data / close_data.iloc[0] * 100

    st.subheader("📊 주가 변동률 비교")
    st.write("시작일 주가를 100으로 두고, 이후 주가가 얼마나 변했는지 비교합니다.")

    fig = px.line(
        normalized_data,
        x=normalized_data.index,
        y=normalized_data.columns,
        title="최근 1년 주가 변동률 비교",
        labels={
            "value": "기준가 대비 변동률",
            "Date": "날짜",
            "variable": "종목"
        }
    )

    fig.update_layout(
        hovermode="x unified",
        height=600,
        legend_title_text="종목",
        xaxis_title="날짜",
        yaxis_title="시작일 = 100"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏆 수익률 요약")

    summary = pd.DataFrame({
        "시작가": close_data.iloc[0],
        "최근가": close_data.iloc[-1],
        "변동률(%)": ((close_data.iloc[-1] / close_data.iloc[0]) - 1) * 100,
        "최고가": close_data.max(),
        "최저가": close_data.min()
    })

    summary = summary.round(2)
    summary = summary.sort_values("변동률(%)", ascending=False)

    st.dataframe(summary, use_container_width=True)

    best_stock = summary.index[0]
    worst_stock = summary.index[-1]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🥇 가장 많이 오른 종목",
            best_stock,
            f"{summary.loc[best_stock, '변동률(%)']}%"
        )

    with col2:
        st.metric(
            "📉 가장 부진한 종목",
            worst_stock,
            f"{summary.loc[worst_stock, '변동률(%)']}%"
        )

    with col3:
        avg_return = summary["변동률(%)"].mean()
        st.metric(
            "📊 평균 변동률",
            f"{avg_return:.2f}%"
        )

    st.subheader("💡 간단 분석")

    for stock in summary.index:
        rate = summary.loc[stock, "변동률(%)"]

        if rate > 20:
            comment = "강한 상승 흐름을 보였습니다. 🚀"
        elif rate > 0:
            comment = "완만한 상승 흐름을 보였습니다. 🙂"
        elif rate > -10:
            comment = "큰 하락은 아니지만 약세 흐름을 보였습니다. ⚠️"
        else:
            comment = "상대적으로 뚜렷한 하락 흐름을 보였습니다. 📉"

        st.write(f"**{stock}**: 최근 1년 변동률은 **{rate:.2f}%**로, {comment}")

    st.caption("※ 본 자료는 yfinance 데이터를 활용한 참고용 분석이며, 투자 권유가 아닙니다.")

else:
    st.warning("하나 이상의 종목을 선택해주세요.")
