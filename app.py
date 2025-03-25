import streamlit as st
import pandas as pd
import os
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import calendar

# ページ全体の明るい印象を与える設定
st.set_page_config(page_title="ペット体調管理", layout="centered")
st.markdown("""
    <style>
        body {
            background-color: #fdfdfd;
        }
        .stApp {
            background-color: #fefefe;
            color: #333;
        }
        h1, h2, h3, h4 {
            color: #2c3e50;
        }
        .css-1cpxqw2, .css-ffhzg2 {
            background-color: #ffffff;
        }
        button[kind="primary"] {
            background-color: #90ee90 !important;
            color: black !important;
        }
        .stButton>button {
            background-color: #90ee90;
            color: black;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
        }
        .stDataFrame, .element-container {
            background-color: #fafafa;
        }
        .css-1d391kg, .css-1v0mbdj, .css-12w0qpk, .css-1r6slb0 {
            color: #2c3e50 !important;
        }
        label, .stTextInput, .stNumberInput, .stDateInput, .stMarkdown, .stSubheader {
            color: #2c3e50 !important;
        }
    </style>
""", unsafe_allow_html=True)

csv_file = "health_log.csv"

if "pet_name" not in st.session_state:
    st.session_state.pet_name = None
if "calendar_year" not in st.session_state:
    st.session_state.calendar_year = date.today().year
if "calendar_month" not in st.session_state:
    st.session_state.calendar_month = date.today().month
if "selected_day" not in st.session_state:
    st.session_state.selected_day = None

if not st.session_state.pet_name:
    st.title("🐾 ペット選択")
    name_input = st.text_input("ペットの名前を入力してください")
    if st.button("次へ") and name_input:
        st.session_state.pet_name = name_input
        st.rerun()
else:
    st.title(f"🐶 {st.session_state.pet_name} の体調管理")

    st.header("📋 今日の健康記録")
    weight = st.number_input("体重 (kg)", min_value=0.0, step=0.1)
    temperature = st.number_input("体温 (℃)", min_value=30.0, max_value=45.0, step=0.1, format="%.1f")
    walks = st.number_input("散歩回数", min_value=0, step=1)
    record_date = st.date_input("記録日", value=date.today())

    if st.button("記録する"):
        if weight > 0:
            new_data = pd.DataFrame({
                "名前": [st.session_state.pet_name],
                "日付": [record_date],
                "体重(kg)": [weight],
                "体温(℃)": [temperature],
                "散歩回数": [walks]
            })
            if os.path.exists(csv_file):
                new_data.to_csv(csv_file, mode='a', index=False, header=False)
            else:
                new_data.to_csv(csv_file, index=False)
            st.success("✅ 記録を保存しました！")
            st.write(new_data)
        else:
            st.warning("⚠️ 体重を入力してください。")

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df["日付"] = pd.to_datetime(df["日付"])
        df_pet = df[df["名前"] == st.session_state.pet_name]
        df_pet["日付"] = pd.to_datetime(df_pet["日付"])

        st.header("📅 カレンダー形式の記録表示")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← 前月"):
                if st.session_state.calendar_month == 1:
                    st.session_state.calendar_month = 12
                    st.session_state.calendar_year -= 1
                else:
                    st.session_state.calendar_month -= 1
        with col3:
            if st.button("次月 →"):
                if st.session_state.calendar_month == 12:
                    st.session_state.calendar_month = 1
                    st.session_state.calendar_year += 1
                else:
                    st.session_state.calendar_month += 1

        selected_year = st.session_state.calendar_year
        selected_month = st.session_state.calendar_month

        st.subheader(f"📆 {selected_year}年 {selected_month}月")

        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdatescalendar(selected_year, selected_month)

        df_month = df_pet[
            (df_pet["日付"].dt.year == selected_year) &
            (df_pet["日付"].dt.month == selected_month)
        ]

        for week in month_days:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day.month != selected_month:
                    cols[i].markdown("#### ")
                else:
                    if cols[i].button(f"{day.day}", key=f"day-{day}"):
                        st.session_state.selected_day = day

        if st.session_state.selected_day:
            st.markdown(f"### 📌 {st.session_state.selected_day.strftime('%Y-%m-%d')} の記録")
            selected_data = df_pet[df_pet["日付"].dt.date == st.session_state.selected_day]
            if not selected_data.empty:
                st.write(selected_data.drop(columns=["名前"]).fillna("未記入"))
            else:
                st.info("この日の記録はありません。")

        st.header("📈 体重の推移グラフ")
        if not df_pet.empty:
            df_pet = df_pet.sort_values("日付")
            fig, ax = plt.subplots()
            ax.plot(df_pet["日付"], df_pet["体重(kg)"], marker='o', linestyle='-', color='#2ecc71')
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
            min_w = df_pet["体重(kg)"].min()
            max_w = df_pet["体重(kg)"].max()
            margin = 0.5
            ax.set_ylim(min_w - margin, max_w + margin)
            ax.set_xlabel("日付")
            ax.set_ylabel("体重(kg)")
            ax.set_title("体重の推移")
            ax.grid(True, linestyle='--', alpha=0.5)
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("まだ記録がありません。")

        st.header("📖 過去の健康記録")
        df_display = df_pet.fillna("未記入")
        st.dataframe(df_display)

    if st.button("🔄 ペットを変更する"):
        st.session_state.pet_name = None
        st.rerun()
