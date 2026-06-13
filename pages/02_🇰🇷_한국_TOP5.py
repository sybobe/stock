import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="한국 대표 주식 TOP5",
    page_icon="🇰🇷",
    layout="wide"
)

st.title("🇰🇷 한국 대표 주식 TOP5 대시보드")
st.markdown("### 최근 1년 주가 흐름과 수익률을 한눈에 비교합니다 📈")

KOREA_TOP5 = {
    "💾 삼성전자": "005930.KS",
    "⚡ SK하이닉스": "000660.KS",
    "🚗 현대차": "005380.KS",
    "🔋 LG에너지솔루션": "373220.KS",
    "🧪 삼성바이오로직스": "207940.KS"
}

company_info = {
    "💾 삼성전자": "반도체, 스마트폰, 가전 중심의 한국 대표 기업",
    "⚡ SK하이닉스": "AI 반도체와 HBM 수요의 핵심 수혜 기업",
    "🚗 현대차": "전기차, 수소차, 글로벌 완성차 경쟁력 보유",
    "🔋 LG에너지솔루션": "전기차 배터리 시장의 대표 기업",
    "🧪 삼성바이오로직스": "바이오 의약품 위탁생산 CDMO 강자"
}

end_date = datetime.today()
start_date = end_date - timedelta(days=365)

@st.cache_data
def load_data(tickers, start, end):
    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )
    return data

tickers = list(KOREA_TOP5.values())

with st.spinner("한국 대표 기업 주가 데이터를 불러오는 중입니다..."):
    raw_data = load_data(tickers, start_date, end_date)

close_data = raw_data["Close"]
close_data = close_data.rename(
    columns={v: k for k, v in KOREA_TOP5.items()}
)

close_data = close_data.dropna(how="all")

st.divider()

st.subheader("🏆 최근 1년 수익률 요약")

returns = ((close_data.iloc[-1] / close_data.iloc[0]) - 1) * 100
returns = returns.sort_values(ascending=False)

best_stock = returns.index[0]
worst_stock = returns.index[-1]
avg_return = returns.mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🥇 가장 많이 오른 종목",
        best_stock,
        f"{returns.loc[best_stock]:.2f}%"
    )

with col2:
    st.metric(
        "📉 가장 부진한 종목",
        worst_stock,
        f"{returns.loc[worst_stock]:.2f}%"
    )

with col3:
    st.metric(
        "📊 평균 수익률",
        f"{avg_return:.2f}%"
    )

st.divider()

st.subheader("📈 최근 1년 주가 흐름 비교")

normalized_data = close_data / close_data.iloc[0] * 100

selected_stocks = st.multiselect(
    "비교할 종목을 선택하세요",
    list(normalized_data.columns),
    default=list(normalized_data.columns)
)

if selected_stocks:
    fig = px.line(
        normalized_data[selected_stocks],
        x=normalized_data.index,
        y=selected_stocks,
        title="최근 1년 주가 변동률 비교",
        labels={
            "value": "시작일 대비 지수",
            "Date": "날짜",
            "variable": "종목"
        }
    )

    fig.update_layout(
        height=650,
        hovermode="x unified",
        legend_title_text="종목",
        xaxis_title="날짜",
        yaxis_title="시작일 = 100"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("하나 이상의 종목을 선택해주세요.")

st.divider()

st.subheader("🚀 수익률 순위")

rank_df = pd.DataFrame({
    "종목": returns.index,
    "수익률(%)": returns.values
})

bar_fig = px.bar(
    rank_df,
    x="수익률(%)",
    y="종목",
    orientation="h",
    title="한국 대표 주식 TOP5 최근 1년 수익률 순위",
    text="수익률(%)"
)

bar_fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

bar_fig.update_layout(
    height=500,
    yaxis=dict(categoryorder="total ascending"),
    xaxis_title="수익률(%)",
    yaxis_title="종목"
)

st.plotly_chart(bar_fig, use_container_width=True)

st.divider()

st.subheader("📋 상세 데이터 요약")

summary = pd.DataFrame({
    "시작가": close_data.iloc[0],
    "최근가": close_data.iloc[-1],
    "변동률(%)": returns,
    "1년 최고가": close_data.max(),
    "1년 최저가": close_data.min()
})

summary = summary.round(2)
summary = summary.sort_values("변동률(%)", ascending=False)

st.dataframe(summary, use_container_width=True)

st.divider()

st.subheader("💡 기업별 발전 가능성 간단 분석")

for company, desc in company_info.items():
    rate = returns.loc[company]

    if rate >= 30:
        opinion = "강한 상승 흐름을 보였고, 시장 기대감이 매우 높은 편입니다. 🚀"
    elif rate >= 10:
        opinion = "양호한 상승 흐름을 보였고, 성장 기대가 유지되고 있습니다. 📈"
    elif rate >= 0:
        opinion = "완만한 상승 흐름입니다. 안정성과 추가 성장성을 함께 봐야 합니다. 🙂"
    elif rate >= -10:
        opinion = "최근 1년 기준 약세 흐름이지만, 업황 회복 여부에 따라 반등 가능성이 있습니다. ⚠️"
    else:
        opinion = "하락폭이 있는 편이라 실적 개선과 산업 전망 확인이 중요합니다. 📉"

    with st.expander(f"{company}"):
        st.write(f"**기업 설명:** {desc}")
        st.write(f"**최근 1년 수익률:** {rate:.2f}%")
        st.write(f"**해석:** {opinion}")

st.success("🇰🇷 한국 대표 주식 TOP5 분석 페이지가 완성되었습니다.")

st.caption("※ 본 자료는 yfinance 데이터를 활용한 참고용 분석이며, 투자 권유가 아닙니다.")
