import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("영화 데이터 그래프 도감 1 - 시간")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    # 날짜 열을 진짜 날짜(datetime)로 변환 (예: 20230101 -> 2023-01-01)
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")
    return df


df = load_data()

# ------------------------------------------------------------
# 구역 1. 영화별 날짜에 따른 일관객 변화
# ------------------------------------------------------------
st.header("구역 1. 영화별 날짜에 따른 일관객 변화")

movie_list = sorted(df["영화명"].unique())
selected_movie = st.selectbox("영화를 선택하세요", movie_list, key="movie_select_1")

movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"'{selected_movie}' 날짜별 일관객 변화",
)
fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)
fig1.update_layout(xaxis_title="날짜", yaxis_title="일관객 수(명)")

st.plotly_chart(fig1, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** (여기에 문장을 채워 넣으세요)")

st.divider()

# ------------------------------------------------------------
# 구역 2. 일관객 합계 상위 5편의 날짜별 일관객 변화
# ------------------------------------------------------------
st.header("구역 2. 일관객 합계 상위 5편의 날짜별 일관객 변화")

top5_movies = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).head(5).index
)
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편 비교",
)
fig2.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra>%{fullData.name}</extra>"
)
fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    legend_title="영화명",
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** (여기에 문장을 채워 넣으세요)")

st.divider()

# ------------------------------------------------------------
# 구역 3. 날짜별 10위권 일관객 합계 추이
# ------------------------------------------------------------
st.header("구역 3. 날짜별 10위권 일관객 합계 추이")

daily_total = df.groupby("날짜")["일관객"].sum().reset_index()
top3_days = daily_total.sort_values("일관객", ascending=False).head(3)

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 10위권 일관객 합계",
)
fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계 일관객: %{y:,}명<extra></extra>"
)

# 합계가 가장 컸던 3일 표시
fig3.add_scatter(
    x=top3_days["날짜"],
    y=top3_days["일관객"],
    mode="markers+text",
    text=top3_days["날짜"].dt.strftime("%Y-%m-%d"),
    textposition="top center",
    marker=dict(size=10, color="red"),
    name="합계 상위 3일",
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계 일관객: %{y:,}명<extra></extra>",
)

fig3.update_layout(
    xaxis_title="날짜",
    yaxis_title="합계 일관객 수(명)",
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** (여기에 문장을 채워 넣으세요)")

st.divider()

# ------------------------------------------------------------
# 구역 4. 일관객 합계 TOP 10 영화
# ------------------------------------------------------------
st.header("구역 4. 일관객 합계 TOP 10 영화")

movie_summary = (
    df.groupby("영화명")
    .agg(총관객=("일관객", "sum"), 순위권유지일수=("날짜", "count"))
    .reset_index()
)
top10_movies = movie_summary.sort_values("총관객", ascending=False).head(10)
# 관객이 많은 영화가 위에 오도록 정렬 (가로 막대그래프는 아래부터 그려지므로 오름차순으로 전달)
top10_movies = top10_movies.sort_values("총관객", ascending=True)

fig4 = px.bar(
    top10_movies,
    x="총관객",
    y="영화명",
    orientation="h",
    custom_data=["순위권유지일수"],
    title="일관객 합계 TOP 10 영화",
)
fig4.update_traces(
    hovertemplate="영화명: %{y}<br>총관객: %{x:,}명<br>10위권 유지 일수: %{customdata[0]}일<extra></extra>"
)
fig4.update_layout(
    xaxis_title="총관객 수(명)",
    yaxis_title="영화명",
)

st.markdown("**이 그래프로 알 수 있는 것:** (여기에 문장을 채워 넣으세요)")

st.divider()

# ------------------------------------------------------------
# 구역 5. 월 x 요일별 일관객 합계 히트맵
# ------------------------------------------------------------
st.header("구역 5. 월 x 요일별 일관객 합계 히트맵")

heatmap_df = df.copy()
heatmap_df["월"] = heatmap_df["날짜"].dt.month
heatmap_df["요일"] = heatmap_df["날짜"].dt.day_name()

weekday_order_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_order_kr = ["월", "화", "수", "목", "금", "토", "일"]
weekday_map = dict(zip(weekday_order_en, weekday_order_kr))
heatmap_df["요일"] = heatmap_df["요일"].map(weekday_map)

pivot = (
    heatmap_df.groupby(["월", "요일"])["일관객"]
    .sum()
    .reset_index()
    .pivot(index="요일", columns="월", values="일관객")
    .reindex(weekday_order_kr)
)

fig5 = px.imshow(
    pivot,
    color_continuous_scale="Reds",
    labels=dict(x="월", y="요일", color="일관객 합계"),
    title="월 x 요일별 일관객 합계",
    aspect="auto",
)
fig5.update_traces(
    hovertemplate="월: %{x}월<br>요일: %{y}요일<br>일관객 합계: %{z:,}명<extra></extra>"
)
fig5.update_xaxes(dtick=1)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** (여기에 문장을 채워 넣으세요)")
