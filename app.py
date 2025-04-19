import streamlit as st
import pandas as pd
import os
SAVE_FILE = "pet_journal_data.csv"
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)
from datetime import date, datetime, timedelta

# 💄 ページテーマとスタイル設定（すべてのページに影響）
st.set_page_config(page_title="ペット成長日記 / Pet Growth Diary", layout="centered")
st.markdown("""
    <style>
    /* 全体背景とフォント設定 */
    body {
        background-color: #f5f7fa;
        font-family: "Segoe UI", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif;
        font-size: 16px;
    }

    .stApp {
        background-color: #ffffff;
        color: #1f1f1f;
    }

    /* タイトル系 */
    h1, h2, h3, h4, label {
        color: #2c3e50 !important;
        font-weight: bold;
    }

    /* 入力フォームの文字色 */
    .stTextInput label,
    .stDateInput label,
    .stNumberInput label,
    .stTextArea label,
    .stSelectbox label {
        color: #34495e !important;
    }

    /* ボタンデザイン */
    .stButton>button {
        background-color: #90ee90;
        color: #1f1f1f;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 16px;
    }

    /* 画像表示を角丸＆影付きに */
    img {
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    /* データフレームや表にも余白と背景 */
    .stDataFrame, .element-container {
        background-color: #fafafa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }

    /* スマホ対応 */
    @media screen and (max-width: 768px) {
        .stApp {
            padding: 0.5rem !important;
        }
    }

    /* ✅ 追加：サイドバーの背景と文字色を明示的に設定 */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        color: #2c3e50;
    }

    section[data-testid="stSidebar"] * {
        color: #2c3e50 !important;
    }        
    /* ✅ 追加：情報ボックスの背景と文字をくっきり見やすく */
    div[data-testid="stInfo"] {
        background-color: #dff5f2 !important;
        color: #1a3c40 !important;
        border: 1px solid #1a3c40;
        border-radius: 8px;
        padding: 1rem;
        font-weight: bold;        
    }
    </style>
""", unsafe_allow_html=True)

# セッション初期化
if "pet_name" not in st.session_state:
    st.session_state.pet_name = None
if "page" not in st.session_state:
    st.session_state.page = "input_name"
if "lang" not in st.session_state:
    st.session_state.lang = "日本語"

# 言語切り替え
lang = st.sidebar.selectbox("🌐 言語 / Language", ["日本語", "English"])
st.session_state.lang = lang

# 翻訳関数
def t(ja, en):
    return ja if st.session_state.lang == "日本語" else en

# メニュー表示
def show_menu():
    st.sidebar.title(t("📚 ページ選択", "📚 Select Page"))
    return st.sidebar.radio(
        t("ページを選んでください", "Please select a page"),
        [
            t("1. 写真ページ", "1. Photo Page"),
            t("2. 基本事項", "2. Basic Info"),
            t("3. 手形の記録", "3. Handprint"),
            t("4. 初めてできたこと", "4. First Milestones"),
            t("5. 成長目安", "5. Growth Guide"),
            t("6. 誕生日メッセージ", "6. Birthday Message"),
            t("7. 成長日記", "7. Growth Diary"),
            t("8. メモ欄", "8. Notes")
        ]
    )

# 名前入力画面
if st.session_state.page == "input_name":
    st.title(t("🐾 私のペット成長日記", "🐾 My Pet Growth Diary"))
    st.subheader(t("ペットの名前を入力してください", "Please enter your pet's name"))
    name_input = st.text_input(t("名前", "Name"))
    if st.button(t("次へ", "Next")) and name_input:
        st.session_state.pet_name = name_input
        st.session_state.page = "main"
        st.rerun()
elif st.session_state.page == "main":
    selected = show_menu()
    st.markdown(f"## 🐶 {st.session_state.pet_name} のページ / {st.session_state.pet_name}'s Page")

    if os.path.exists(SAVE_FILE):
        df_save = pd.read_csv(SAVE_FILE)
    else:
        df_save = pd.DataFrame()

    def editable_data(df_page, key_prefix, page_label):
        st.subheader(t("📝 編集可能なデータ", "📝 Editable Data"))
        editable_df = df_page.drop(columns=["名前", "ページ"], errors="ignore")
        edited = st.data_editor(editable_df, key=f"edit_table_{key_prefix}", use_container_width=True)
        if st.button(t("変更を保存", "Save Changes"), key=f"save_edit_{key_prefix}"):
            new_df = df_page.copy()
            for col in edited.columns:
                new_df[col] = edited[col]
            not_this_page = df_save[df_save["ページ"] != page_label]
            updated = pd.concat([not_this_page, new_df], ignore_index=True)
            updated.to_csv(SAVE_FILE, index=False)
            st.success(t("✅ 変更を保存しました！", "✅ Changes saved!"))

    # ページ 1: 写真ページ
    if selected == t("1. 写真ページ", "1. Photo Page"):
        st.markdown("<h3 style='color:#2c3e50;'>📸 生まれたときの写真 / Photos from Birth</h3>", unsafe_allow_html=True)
        photo1 = st.file_uploader(t("1枚目の写真を選択", "Select the first photo"), type=["jpg", "jpeg", "png"], key="photo1")
        photo2 = st.file_uploader(t("2枚目の写真を選択", "Select the second photo"), type=["jpg", "jpeg", "png"], key="photo2")

        if photo1 is not None:
            path1 = os.path.join(IMAGE_DIR, f"{st.session_state.pet_name}_photo1.jpg")
            with open(path1, "wb") as f:
                f.write(photo1.read())
            st.image(path1, caption=t("📷 1枚目", "📷 Photo 1"), use_container_width=True)

        if photo2 is not None:
            path2 = os.path.join(IMAGE_DIR, f"{st.session_state.pet_name}_photo2.jpg")
            with open(path2, "wb") as f:
                f.write(photo2.read())
            st.image(path2, caption=t("📷 2枚目", "📷 Photo 2"), use_container_width=True)

    # ページ 2: 基本事項
    elif selected == t("2. 基本事項", "2. Basic Info"):
        st.markdown("<h3 style='color:#2c3e50;'>📘 基本情報の記録 / Basic Info</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            birth_date = st.date_input(t("生まれた日", "Date of Birth"))
            birth_time = st.time_input(t("生まれた時間", "Time of Birth"))
            birth_place = st.text_input(t("生まれた場所", "Place of Birth"))
            weather = st.text_input(t("その日の天気", "Weather on the day"))
        with col2:
            birth_weight = st.text_input(t("出生時の体重", "Birth Weight"))
            birth_height = st.text_input(t("出生時の身長", "Birth Height"))

        message = st.text_area(t("🐾 ペットへのメッセージ", "🐾 Message to your pet"))

        if st.button(t("保存する", "Save"), key="save_basic"):
            df_new = pd.DataFrame([{
                "名前": st.session_state.pet_name,
                "ページ": "基本事項",
                "生まれた日": birth_date,
                "生まれた時間": birth_time,
                "場所": birth_place,
                "天気": weather,
                "体重": birth_weight,
                "身長": birth_height,
                "メッセージ": message
            }])
            df_all = pd.concat([df_save, df_new], ignore_index=True)
            df_all.to_csv(SAVE_FILE, index=False)
            st.success(t("✅ 保存しました！", "✅ Saved!"))

        editable_data(df_save[df_save["ページ"] == "基本事項"], "basic", "基本事項")
    # ページ 3: 手形の記録
    elif selected == t("3. 手形の記録", "3. Handprint"):
        st.markdown("<h3 style='color:#2c3e50;'>✋ 手形の記録 / Handprint</h3>", unsafe_allow_html=True)

        hand_photo = st.file_uploader(t("📸 手形の写真をアップロード", "📸 Upload handprint photo"), type=["jpg", "jpeg", "png"], key="hand")
        hand_date = st.date_input(t("撮影日", "Date of Photo"))
        hand_comment = st.text_area(t("コメント", "Comment"))

        if hand_photo:
            hand_path = os.path.join(IMAGE_DIR, f"{st.session_state.pet_name}_hand.jpg")
            with open(hand_path, "wb") as f:
                f.write(hand_photo.read())
            st.image(hand_path, caption=t("✋ 手形写真", "✋ Handprint Photo"), use_container_width=True)

        if st.button(t("保存する", "Save"), key="save_hand"):
            df_new = pd.DataFrame([{
                "名前": st.session_state.pet_name,
                "ページ": "手形",
                "日付": hand_date,
                "コメント": hand_comment
            }])
            df_all = pd.concat([df_save, df_new], ignore_index=True)
            df_all.to_csv(SAVE_FILE, index=False)
            st.success(t("✅ 手形情報を保存しました！", "✅ Handprint saved!"))

        editable_data(df_save[df_save["ページ"] == "手形"], "hand", "手形")

    # ページ 4: 初めてできたこと
    elif selected == t("4. 初めてできたこと", "4. First Milestones"):
        st.markdown("<h3 style='color:#2c3e50;'>🎉 初めてできた記念 / First Milestones</h3>", unsafe_allow_html=True)

        records = []
        for i in range(10):
            with st.expander(t(f"記録 {i+1}", f"Record {i+1}")):
                date_input = st.date_input(t(f"日付{i+1}", f"Date {i+1}"), key=f"date{i}")
                weekday = date_input.strftime("%A")
                what = st.text_input(t(f"できたこと{i+1}", f"What they did {i+1}"), key=f"what{i}")
                if what:
                    records.append({
                        "名前": st.session_state.pet_name,
                        "ページ": "初めてできたこと",
                        "日付": date_input,
                        "曜日": weekday,
                        "できたこと": what
                    })

        if st.button(t("保存する", "Save"), key="save_firsts"):
            df_new = pd.DataFrame(records)
            df_all = pd.concat([df_save, df_new], ignore_index=True)
            df_all.to_csv(SAVE_FILE, index=False)
            st.success(t("✅ 初めてできたことを保存しました！", "✅ First milestones saved!"))

        editable_data(df_save[df_save["ページ"] == "初めてできたこと"], "firsts", "初めてできたこと")
    # ページ 5: 成長目安
    elif selected == t("5. 成長目安", "5. Growth Guide"):
        st.markdown("<h3 style='color:#2c3e50;'>📈 ペットの成長目安 / Growth Guide</h3>", unsafe_allow_html=True)
        st.info(t(
            "このページは現在準備中です。今後、年齢や行動に応じた成長チェックを実装予定です。",
            "This page is under preparation. Growth checks based on age and behavior will be implemented."
        ))

    # ページ 6: 誕生日メッセージ
    elif selected == t("6. 誕生日メッセージ", "6. Birthday Message"):
        st.markdown("<h3 style='color:#2c3e50;'>🎂 1歳の誕生日 / 1st Birthday</h3>", unsafe_allow_html=True)

        birthday_photo = st.file_uploader(
            t("🎉 写真をアップロード", "🎉 Upload a birthday photo"),
            type=["jpg", "jpeg", "png"],
            key="bday"
        )
        birthday_msg = st.text_area(t("🎁 ペットへのメッセージ", "🎁 Message to your pet"))

        if birthday_photo:
         path = os.path.join(IMAGE_DIR, f"{st.session_state.pet_name}_bday.jpg")
         with open(path, "wb") as f:
          f.write(birthday_photo.read())
    
         st.markdown("##### 🎉 誕生日写真 / Birthday Photo")
         st.image(path, use_container_width=True)
         st.markdown("<br>", unsafe_allow_html=True)


        if st.button(t("保存する", "Save"), key="save_birthday"):
            df_new = pd.DataFrame([{
                "名前": st.session_state.pet_name,
                "ページ": "誕生日メッセージ",
                "メッセージ": birthday_msg
            }])
            df_all = pd.concat([df_save, df_new], ignore_index=True)
            df_all.to_csv(SAVE_FILE, index=False)
            st.success(t("✅ 誕生日の記録を保存しました！", "✅ Birthday message saved!"))

        editable_data(df_save[df_save["ページ"] == "誕生日メッセージ"], "bday", "誕生日メッセージ")
    # ページ 7: 成長日記
    elif selected == t("7. 成長日記", "7. Growth Diary"):
        st.markdown("<h3 style='color:#2c3e50;'>🗓 成長日記 / Growth Diary</h3>", unsafe_allow_html=True)

        # 生まれた日を取得
        if os.path.exists(SAVE_FILE):
            df_info = pd.read_csv(SAVE_FILE)
            birth_row = df_info[(df_info["名前"] == st.session_state.pet_name) & (df_info["ページ"] == "基本事項")]
            if not birth_row.empty:
                birth_date = pd.to_datetime(birth_row.iloc[0]["生まれた日"])
            else:
                st.error(t("⚠️ 基本情報に生まれた日が保存されていません。", "⚠️ Birth date not found in basic info."))
                birth_date = None
        else:
            st.error(t("⚠️ 基本情報ファイルが存在しません。", "⚠️ Basic info file not found."))
            birth_date = None

        selected_date = st.date_input(t("📅 日付を選択", "📅 Select Date"), value=date.today())
        selected_time = st.time_input(t("🕒 時間を選択", "🕒 Select Time"), value=datetime.now().time())
        dt = datetime.combine(selected_date, selected_time)

        if birth_date:
            days_old = (dt.date() - birth_date.date()).days
            st.markdown(t(f"**🐣 生後 {days_old} 日目の記録**", f"**🐣 Day {days_old} since birth**"))

        col1, col2 = st.columns(2)
        with col1:
            meal = st.text_input(t("🍽 食事の内容", "🍽 Meal Details"))
            meal_grams = st.number_input(t("グラム数 (g)", "Amount (g)"), 0, 500, step=5)
            potty = st.text_input(t("🚽 おしっこ・うんち", "🚽 Potty"))
        with col2:
            walk = st.text_input(t("🐕 散歩", "🐕 Walk"))
            sleep = st.text_input(t("😴 睡眠（例：22:00〜6:00）", "😴 Sleep (e.g. 10pm–6am)"))
            memo = st.text_area(t("📝 MEMO", "📝 Memo"))

        if st.button(t("記録を保存する", "Save Record"), key="save_growth_record"):
            new_log = pd.DataFrame([{
                "名前": st.session_state.pet_name,
                "日付時間": dt,
                "生後日数": days_old,
                "食事内容": meal,
                "グラム": meal_grams,
                "おしっこ・うんち": potty,
                "散歩": walk,
                "睡眠": sleep,
                "MEMO": memo
            }])
            if os.path.exists("growth_log.csv"):
                old_log = pd.read_csv("growth_log.csv")
                full_log = pd.concat([old_log, new_log], ignore_index=True)
            else:
                full_log = new_log
            full_log.to_csv("growth_log.csv", index=False)
            st.success(t("✅ 記録を保存しました！", "✅ Record saved!"))
        # 🔍 成長記録の表示・編集
        if os.path.exists("growth_log.csv"):
            st.divider()
            st.subheader(t("🔍 保存された成長記録", "🔍 Saved Growth Records"))

            df_growth = pd.read_csv("growth_log.csv")
            df_growth["日付時間"] = pd.to_datetime(df_growth["日付時間"])
            df_growth = df_growth[df_growth["名前"] == st.session_state.pet_name]

            date_filter = st.date_input(t("📅 表示したい日付を選択（複数選択可）", "📅 Select dates to filter (multiple allowed)"), [])
            if date_filter:
                df_growth = df_growth[df_growth["日付時間"].dt.date.isin(date_filter)]

            keyword = st.text_input(t("🔍 キーワード検索（食事、メモなど）", "🔍 Keyword search (meal, memo, etc.)"))
            if keyword:
                df_growth = df_growth[df_growth.apply(lambda row: keyword.lower() in str(row).lower(), axis=1)]

            edited = st.data_editor(df_growth, num_rows="dynamic", use_container_width=True)

            if st.button(t("変更を保存する", "Save Changes"), key="save_growth_edit"):
                full_log = pd.read_csv("growth_log.csv")
                others = full_log[full_log["名前"] != st.session_state.pet_name]
                combined = pd.concat([others, edited], ignore_index=True)
                combined.to_csv("growth_log.csv", index=False)
                st.success(t("✅ 編集内容を保存しました！", "✅ Changes saved!"))

    # ページ 8: メモ欄
    elif selected == t("8. メモ欄", "8. Notes"):
        st.markdown("<h3 style='color:#2c3e50;'>📝 自由メモ欄 / Free Notes</h3>", unsafe_allow_html=True)

        memo_input = st.text_area(t("気づいたこと、生活のことなどを自由に記入できます", "You can freely write your observations, lifestyle notes, etc."))

        if st.button(t("保存する", "Save"), key="save_memo"):
            memo_df = pd.DataFrame([{
                "名前": st.session_state.pet_name,
                "ページ": "メモ欄",
                "日付": date.today(),
                "メモ": memo_input
            }])
            if os.path.exists("memo_log.csv"):
                existing = pd.read_csv("memo_log.csv")
                memo_df = pd.concat([existing, memo_df], ignore_index=True)
            memo_df.to_csv("memo_log.csv", index=False)
            st.success(t("✅ メモを保存しました！", "✅ Memo saved!"))

        if os.path.exists("memo_log.csv"):
            df_memo = pd.read_csv("memo_log.csv")
            df_memo = df_memo[df_memo["名前"] == st.session_state.pet_name]
            editable_data(df_memo, "memo", "メモ欄")
