import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="글로벌 TOP10 주식",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 글로벌 빅테크 TOP10 주식 대시보드")
st.markdown("### 최근 1년 성과를 한눈에 비교해보세요")

TOP10 = {
    "🍎 Apple": "AAPL",
    "🪟 Microsoft": "MSFT",
    "🔍 Google": "GOOGL",
    "🚗 Tesla": "TSLA",
    "📦 Amazon": "AMZN",
    "📱 Meta": "META",
    "🤖 Nvidia": "NVDA",
    "💼 Berkshire": "BRK-B",
    "☁️ Broadcom": "AVGO",
    "🧠 AMD": "AMD"
}

end = datetime.today()
start = end - timedelta(days=365)

@st.cache_data
def get_data():
    data = yf.download(
        list(TOP10.values()),
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )
    return data["Close"]

df = get_data()

rename_dict = {}
for k, v in TOP10.items():
    rename_dict[v] = k

df = df.rename(columns=rename_dict)

normalized = df / df.iloc[0] * 100

returns = ((df.iloc[-1] / df.iloc[0]) - 1) * 100
returns = returns.sort_values(ascending=False)

# -------------------------------
# KPI
# -------------------------------

st.subheader("🏆 최근 1년 수익률 TOP3")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "🥇 1위",
        returns.index[0],
        f"{returns.iloc[0]:.1f}%"
    )

with c2:
    st.metric(
        "🥈 2위",
        returns.index[1],
        f"{returns.iloc[1]:.1f}%"
    )

with c3:
    st.metric(
        "🥉 3위",
        returns.index[2],
        f"{returns.iloc[2]:.1f}%"
    )

# -------------------------------
# 인터랙티브 차트
# -------------------------------

st.subheader("📈 최근 1년 주가 흐름")

selected = st.multiselect(
    "종목 선택",
    list(normalized.columns),
    default=list(normalized.columns)[:5]
)

fig = px.line(
    normalized[selected],
    x=normalized.index,
    y=selected,
    title="시작가 = 100 기준 비교"
)

fig.update_layout(
    hovermode="x unified",
    height=700,
    legend_title="종목"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 수익률 순위
# -------------------------------

st.subheader("🚀 최근 1년 수익률 순위")

rank_df = pd.DataFrame({
    "종목": returns.index,
    "수익률(%)": returns.values
})

bar = px.bar(
    rank_df,
    x="수익률(%)",
    y="종목",
    orientation="h",
    title="TOP10 수익률 랭킹"
)

bar.update_layout(height=600)

st.plotly_chart(bar, use_container_width=True)

# -------------------------------
# 카드형 정보
# -------------------------------

st.subheader("💡 기업 한줄 설명")

col1, col2 = st.columns(2)

info = {
    "🍎 Apple": "아이폰과 생태계의 제왕",
    "🪟 Microsoft": "클라우드와 AI 강자",
    "🔍 Google": "검색과 광고 시장 지배자",
    "🚗 Tesla": "전기차 혁신 기업",
    "📦 Amazon": "전자상거래 및 AWS",
    "📱 Meta": "인스타그램·페이스북",
    "🤖 Nvidia": "AI 반도체 최강자",
    "💼 Berkshire": "워런 버핏 투자회사",
    "☁️ Broadcom": "반도체·인프라 솔루션",
    "🧠 AMD": "CPU·GPU 성장 기업"
}

items = list(info.items())

for i in range(0, len(items), 2):
    with col1:
        st.info(
            f"### {items[i][0]}\n\n{items[i][1]}"
        )

    if i + 1 < len(items):
        with col2:
            st.info(
                f"### {items[i+1][0]}\n\n{items[i+1][1]}"
            )

st.success("🎯 팁: 그래프에서 종목을 클릭하면 특정 기업만 비교할 수 있습니다.")
