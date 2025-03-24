import streamlit as st
import pandas as pd
import os
from datetime import date

st.title("🐾 ペット体調管理アプリ")
st.header("📋 今日の健康記録")

# 入力フォーム
name = st.text_input("ペットの名前")
weight = st.number_input("体重 (kg)", min_value=0.0, step=0.1)
record_date = st.date_input("記録日", value=date.today())

# ファイル名
csv_file = "health_log.csv"

# ボタンで保存処理
if st.button("記録する"):
    if name and weight > 0:
        new_data = pd.DataFrame({
            "名前": [name],
            "日付": [record_date],
            "体重(kg)": [weight]
        })

        # CSVがすでに存在していれば追記、なければ新規作成
        if os.path.exists(csv_file):
            new_data.to_csv(csv_file, mode='a', index=False, header=False)
        else:
            new_data.to_csv(csv_file, index=False)

        st.success("✅ 記録を保存しました！")
        st.write(new_data)
    else:
        st.warning("⚠️ ペットの名前と体重を入力してください。")
st.header("📖 過去の健康記録")

# CSVファイルがあれば読み込んで表示
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    st.dataframe(df)
else:
    st.info("まだ記録がありません。")
st.header("📈 体重の推移グラフ")

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)

    if not df.empty:
        # 日付で並び替え
        df["日付"] = pd.to_datetime(df["日付"])
        df = df.sort_values("日付")

        import matplotlib.pyplot as plt

        # グラフ描画
        fig, ax = plt.subplots()
        ax.plot(df["日付"], df["体重(kg)"], marker='o', linestyle='-', color='skyblue')

        # 日付の表示形式を「年月日」のみに設定
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))

        # 体重の上下に少し余白を設ける
        min_w = df["体重(kg)"].min()
        max_w = df["体重(kg)"].max()
        margin = 0.5
        ax.set_ylim(min_w - margin, max_w + margin)

        # ラベル・タイトル・見た目調整
        ax.set_xlabel("日付", fontsize=12)
        ax.set_ylabel("体重(kg)", fontsize=12)
        ax.set_title("ペットの体重推移", fontsize=14)
        ax.grid(True)
        plt.xticks(rotation=45)

        # Streamlitに表示
        st.pyplot(fig)

    else:
        st.info("グラフ表示には記録が必要です。")
