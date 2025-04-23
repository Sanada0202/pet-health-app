import streamlit as st
import pandas as pd
import os
from datetime import date, datetime, timedelta
import traceback
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定数の設定
SAVE_FILE = "pet_journal_data.csv"
GROWTH_LOG_FILE = "growth_log.csv"
MEMO_LOG_FILE = "memo_log.csv"
IMAGE_DIR = "images"

# ディレクトリの作成（存在しない場合）
os.makedirs(IMAGE_DIR, exist_ok=True)

# 💄 ページテーマとスタイル設定（すべてのページに影響）
st.set_page_config(
    page_title="ペット成長日記 / Pet Growth Diary", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# シンプルなスタイル設定
st.markdown("""
    <style>
    /* ボタンデザイン - よりコントラストを強化 */
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold;
        font-size: 16px;
    }
    
    /* メッセージの可読性向上 */
    .stSuccess, .stError, .stInfo, .stWarning {
        color: black !important;
        font-weight: bold !important;
        border: 2px solid;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# データフレームの安全な初期化（空データの準備）
def get_empty_dataframe(datatype):
    """用途に応じた空のデータフレームを返す"""
    if datatype == "main":
        return pd.DataFrame(columns=["名前", "ページ"])
    elif datatype == "growth":
        return pd.DataFrame(columns=["名前", "日付時間", "生後日数", "食事内容", "グラム", "おしっこ・うんち", "散歩", "睡眠", "MEMO"])
    elif datatype == "memo":
        return pd.DataFrame(columns=["名前", "ページ", "日付", "メモ"])
    else:
        return pd.DataFrame()

# エラーハンドリング用の共通関数
def safe_load_dataframe(file_path, datatype="main"):
    """安全にデータフレームを読み込む関数"""
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # 必要なカラムが存在するか確認し、なければ追加
            empty_df = get_empty_dataframe(datatype)
            for col in empty_df.columns:
                if col not in df.columns:
                    df[col] = ""
            return df
        else:
            return get_empty_dataframe(datatype)
    except Exception as e:
        st.error("データの読み込み中にエラーが発生しました: " + str(e))
        logging.error(f"データ読み込みエラー: {str(e)}\n{traceback.format_exc()}")
        return get_empty_dataframe(datatype)

def safe_save_dataframe(df, file_path):
    """安全にデータフレームを保存する関数"""
    try:
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        st.error("データの保存中にエラーが発生しました: " + str(e))
        logging.error(f"データ保存エラー: {str(e)}\n{traceback.format_exc()}")
        return False

def safe_save_image(uploaded_file, path):
    """安全に画像を保存する関数"""
    try:
        if uploaded_file is not None:
            with open(path, "wb") as f:
                f.write(uploaded_file.read())
            return True
        return False
    except Exception as e:
        st.error("画像の保存中にエラーが発生しました: " + str(e))
        logging.error(f"画像保存エラー: {str(e)}\n{traceback.format_exc()}")
        return False

# データフレームから安全に値を取得
def safe_get_value(df, row_idx, col_name, default=""):
    """データフレームから安全に値を取得する"""
    try:
        if df.empty or row_idx >= len(df) or col_name not in df.columns:
            return default
        value = df.iloc[row_idx][col_name]
        return default if pd.isna(value) else value
    except Exception as e:
        logging.error(f"値の取得エラー: {str(e)}")
        return default

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

# データ編集共通関数
def editable_data(df_page, key_prefix, page_label):
    st.subheader(t("📝 編集可能なデータ", "📝 Editable Data"))
    
    # データが空の場合のハンドリング
    if df_page.empty:
        st.info(t("📭 まだデータがありません。上記のフォームで情報を入力してください。", 
                 "📭 No data yet. Please enter information in the form above."))
        return
    
    try:
        # 安全に不要なカラムを削除
        columns_to_drop = []
        if "名前" in df_page.columns:
            columns_to_drop.append("名前")
        if "ページ" in df_page.columns:
            columns_to_drop.append("ページ")
            
        if columns_to_drop:
            editable_df = df_page.drop(columns=columns_to_drop)
        else:
            editable_df = df_page.copy()
            
        edited = st.data_editor(editable_df, key=f"edit_table_{key_prefix}", use_container_width=True)
        
        if st.button(t("変更を保存", "Save Changes"), key=f"save_edit_{key_prefix}"):
            df_all = safe_load_dataframe(SAVE_FILE)
            
            new_df = df_page.copy()
            for col in edited.columns:
                new_df[col] = edited[col]
                
            # 安全にフィルタリング
            try:
                not_this_page = df_all[df_all["ページ"] != page_label]
            except Exception as e:
                logging.error(f"フィルタリングエラー: {str(e)}")
                not_this_page = get_empty_dataframe("main")
                
            updated = pd.concat([not_this_page, new_df], ignore_index=True)
            
            if safe_save_dataframe(updated, SAVE_FILE):
                st.success(t("✅ 変更を保存しました！", "✅ Changes saved!"))
    except Exception as e:
        st.error(t(f"エラーが発生しました: {str(e)}", f"An error occurred: {str(e)}"))
        logging.error(f"データ編集エラー: {str(e)}\n{traceback.format_exc()}")

# 名前入力画面
if st.session_state.page == "input_name":
    st.title(t("🐾 私のペット成長日記", "🐾 My Pet Growth Diary"))
    st.subheader(t("ペットの名前を入力してください", "Please enter your pet's name"))
    
    name_input = st.text_input(t("名前", "Name"))
    
    next_button = st.button(t("次へ", "Next"), key="next_from_name")
    
    if next_button and name_input:
        st.session_state.pet_name = name_input
        st.session_state.page = "main"
        st.rerun()
    elif next_button and not name_input:
        st.warning(t("⚠️ 名前を入力してください", "⚠️ Please enter a name"))

elif st.session_state.page == "main":
    selected = show_menu()
    st.markdown(f"## 🐶 {st.session_state.pet_name} のページ / {st.session_state.pet_name}'s Page")

    # メインのデータフレームを読み込み
    df_save = safe_load_dataframe(SAVE_FILE, "main")

    # ページ 1: 写真ページ
    if selected == t("1. 写真ページ", "1. Photo Page"):
        st.header(t("📸 生まれたときの写真", "📸 Photos from Birth"))
        
        col1, col2 = st.columns(2)
        with col1:
            photo1 = st.file_uploader(t("1枚目の写真を選択", "Select the first photo"), 
                                      type=["jpg", "jpeg", "png"], key="photo1")
            if photo1 is not None:
                path1 = os.path.join(IMAGE_DIR, f"{st.session_state.pet_name}_photo1.jpg")
                if safe_save_image(photo1, path1):
                    st.image(path1, caption=t("📷 1枚目", "📷 Photo 1"), use_container_width=True)
        
        with col2:
            photo2 = st.file_uploader(t("2枚目の写真を選択", "Select the second photo"), 
                                      type=["jpg", "jpeg", "png"], key="photo2")
            if photo2 is not None:
                path2 = os.path.join(IMAGE_DIR, f"{st.session_state.pet_name}_photo2.jpg")
                if safe_save_image(photo2, path2):
                    st.image(path2, caption=t("📷 2枚目", "📷 Photo 2"), use_container_width=True)

    # ページ 2: 基本事項
    elif selected == t("2. 基本事項", "2. Basic Info"):
        st.header(t("📘 基本情報の記録", "📘 Basic Info"))

        # 既存のデータを安全に取得
        try:
            existing_data = df_save[(df_save["名前"] == st.session_state.pet_name) & 
                                  (df_save["ページ"] == "基本事項")]
        except Exception as e:
            logging.error(f"基本情報フィルタリングエラー: {str(e)}")
            existing_data = pd.DataFrame()
        
        default_birth_date = datetime.now().date()
        default_birth_time = datetime.now().time()
        default_birth_place = ""
        default_weather = ""
        default_birth_weight = ""
        default_birth_height = ""
        default_message = ""
        
        if not existing_data.empty:
            try:
                default_birth_date = pd.to_datetime(safe_get_value(existing_data, 0, "生まれた日", default_birth_date)).date()
                default_birth_time = pd.to_datetime(safe_get_value(existing_data, 0, "生まれた時間", default_birth_time)).time()
                default_birth_place = safe_get_value(existing_data, 0, "場所", "")
                default_weather = safe_get_value(existing_data, 0, "天気", "")
                default_birth_weight = safe_get_value(existing_data, 0, "体重", "")
                default_birth_height = safe_get_value(existing_data, 0, "身長", "")
                default_message = safe_get_value(existing_data, 0, "メッセージ", "")
            except Exception as e:
                logging.error(f"既存データの読み込みエラー: {str(e)}")
        
        col1, col2 = st.columns(2)
        with col1:
            birth_date = st.date_input(t("生まれた日", "Date of Birth"), value=default_birth_date)
            birth_time = st.time_input(t("生まれた時間", "Time of Birth"), value=default_birth_time)
            birth_place = st.text_input(t("生まれた場所", "Place of Birth"), value=default_birth_place)
            weather = st.text_input(t("その日の天気", "Weather on the day"), value=default_weather)
        with col2:
            birth_weight = st.text_input(t("出生時の体重", "Birth Weight"), value=default_birth_weight)
            birth_height = st.text_input(t("出生時の身長", "Birth Height"), value=default_birth_height)

        message = st.text_area(t("🐾 ペットへのメッセージ", "🐾 Message to your pet"), value=default_message)

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
            
            # 既存の行を削除し、新しいデータを追加
            try:
                df_filtered = df_save[(df_save["名前"] != st.session_state.pet_name) | 
                                    (df_save["ページ"] != "基本事項")]
            except Exception as e:
                logging.error(f"フィルタリングエラー: {str(e)}")
                df_filtered = get_empty_dataframe("main")
                
            df_all = pd.concat([df_filtered, df_new], ignore_index=True)
            
            if safe_save_dataframe(df_all, SAVE_FILE):
                st.success(t("✅ 保存しました！", "✅ Saved!"))
        
        # 編集可能データの表示
        try:
            editable_df = df_save[(df_save["名前"] == st.session_state.pet_name) & 
                                (df_save["ページ"] == "基本事項")]
        except Exception as e:
            logging.error(f"フィルタリングエラー: {str(e)}")
            editable_df = pd.DataFrame()
            
        editable_data(editable_df, "basic", "基本事項")

    # ページ 3: 手形の記録
    elif selected == t("3. 手形の記録", "3. Handprint"):
        st.header(t("✋ 手形の記録", "✋ Handprint"))

        # 既存データを安全に取得
        try:
            existing_hand = df_save[(df_save["名前"] == st.session_state.pet_name) & 
                                  (df_save["ページ"] == "手形")]
        except Exception as e:
            logging.error(f"手形データフィルタリングエラー: {str(e)}")
            existing_hand = pd.DataFrame()
        
        default_hand_date = datetime.now().date()
        default_hand_comment = ""
        
        if not existing_hand.empty:
            try:
                default_hand_date = pd.to_datetime(safe_get_value(existing_hand, 0, "日付", default_hand_date)).date()
                default_hand_comment = safe_get_value(existing_hand, 0, "コメント", "")
            except Exception as e:
                logging.error(f"手形データの読み込みエラー: {str(e)}")

        hand_photo = st.file_uploader(
            t("📸 手形の写真をアップロード", "📸 Upload handprint photo"), 
            type=["jpg", "jpeg", "png"], 
            key="hand"
        )
        
        hand_date = st.date_input(t("撮影日", "Date of Photo"), value=default_hand_date)
        hand_comment = st.text_area(t("コメント", "Comment"), value=default_hand_comment)

        # 既存の画像があれば表示
        hand_path = os.path.join(IMAGE_DIR, f"{st.session_state.pet_name}_hand.jpg")
        if hand_photo:
            if safe_save_image(hand_photo, hand_path):
                st.image(hand_path, caption=t("✋ 手形写真", "✋ Handprint Photo"), use_container_width=True)
        elif os.path.exists(hand_path):
            st.image(hand_path, caption=t("✋ 保存済みの手形写真", "✋ Saved Handprint Photo"), use_container_width=True)

        if st.button(t("保存する", "Save"), key="save_hand"):
            df_new = pd.DataFrame([{
                "名前": st.session_state.pet_name,
                "ページ": "手形",
                "日付": hand_date,
                "コメント": hand_comment
            }])
            
            # 既存の行を削除し、新しいデータを追加
            try:
                df_filtered = df_save[(df_save["名前"] != st.session_state.pet_name) | 
                                    (df_save["ページ"] != "手形")]
            except Exception as e:
                logging.error(f"フィルタリングエラー: {str(e)}")
                df_filtered = get_empty_dataframe("main")
                
            df_all = pd.concat([df_filtered, df_new], ignore_index=True)
            
            if safe_save_dataframe(df_all, SAVE_FILE):
                st.success(t("✅ 手形情報を保存しました！", "✅ Handprint saved!"))

        # 編集可能データの表示
        try:
            editable_df = df_save[(df_save["名前"] == st.session_state.pet_name) & 
                                (df_save["ページ"] == "手形")]
        except Exception as e:
            logging.error(f"フィルタリングエラー: {str(e)}")
            editable_df = pd.DataFrame()
            
        editable_data(editable_df, "hand", "手形")

    # ページ 4: 初めてできたこと
    elif selected == t("4. 初めてできたこと", "4. First Milestones"):
        st.header(t("🎉 初めてできた記念", "🎉 First Milestones"))

        # 既存データを安全に取得
        try:
            existing_firsts = df_save[(df_save["名前"] == st.session_state.pet_name) & 
                                    (df_save["ページ"] == "初めてできたこと")]
        except Exception as e:
            logging.error(f"初めてできたことデータフィルタリングエラー: {str(e)}")
            existing_firsts = pd.DataFrame()
        
        records = []
        with st.form(key="milestone_form"):
            for i in range(5):  # 入力フォームを5つに減らし、フォームで囲む
                col1, col2 = st.columns([1, 3])
                with col1:
                    date_input = st.date_input(
                        t(f"日付{i+1}", f"Date {i+1}"), 
                        key=f"date{i}",
                        value=datetime.now().date()
                    )
                    weekday = date_input.strftime("%A")
                
                with col2:
                    # 既存データがあれば、それを初期値として表示
                    default_what = ""
                    if not existing_firsts.empty and i < len(existing_firsts):
                        try:
                            default_what = safe_get_value(existing_firsts, i, "できたこと", "")
                        except Exception as e:
                            logging.error(f"既存データ取得エラー: {str(e)}")
                    
                    what = st.text_input(
                        t(f"できたこと{i+1}", f"What they did {i+1}"), 
                        key=f"what{i}",
                        value=default_what
                    )
                
                if what:  # 空でない場合のみ記録
                    records.append({
                        "名前": st.session_state.pet_name,
                        "ページ": "初めてできたこと",
                        "日付": date_input,
                        "曜日": weekday,
                        "できたこと": what
                    })
            
            submit_button = st.form_submit_button(t("保存する", "Save"))
            
            if submit_button and records:
                df_new = pd.DataFrame(records)
                
                # 既存の行を削除し、新しいデータを追加
                try:
                    df_filtered = df_save[(df_save["名前"] != st.session_state.pet_name) | 
                                        (df_save["ページ"] != "初めてできたこと")]
                except Exception as e:
                    logging.error(f"フィルタリングエラー: {str(e)}")
                    df_filtered = get_empty_dataframe("main")
                    
                df_all = pd.concat([df_filtered, df_new], ignore_index=True)
                
                if safe_save_dataframe(df_all, SAVE_FILE):
                    st.success(t("✅ 初めてできたことを保存しました！", "✅ First milestones saved!"))
        
        # 追加の項目が必要な場合はこちらから入力
        with st.expander(t("🔍 さらに記録を追加", "🔍 Add more records")):
            editable_data(existing_firsts, "firsts", "初めてできたこと")

    # ページ 5: 成長目安
    elif selected == t("5. 成長目安", "5. Growth Guide"):
        st.header(t("📈 ペットの成長目安", "📈 Growth Guide"))
        st.info(t(
            "このページは現在準備中です。今後、年齢や行動に応じた成長チェックを実装予定です。",
            "This page is under preparation. Growth checks based on age and behavior will be implemented."
        ))

    # ページ 6: 誕生日メッセージ
    elif selected == t("6. 誕生日メッセージ", "6. Birthday Message"):
        st.header(t("🎂 1歳の誕生日", "🎂 1st Birthday"))

        # 既存データを安全に取得
        try:
            existing_bday = df_save[(df_save["名前"] == st.session_state.pet_name) & 
                                   (df_save["ページ"] == "誕生日メッセージ")]
        except Exception as e:
            logging.error(f"誕生日メッセージデータフィルタリングエラー: {str(e)}")
            existing_bday = pd.DataFrame()
        
        default_bday_msg = ""
        if not existing_bday.empty:
            try:
                # NaNを空文字列に変換して対応
                msg = safe_get_value(existing_bday, 0, "メッセージ", "")
                default_bday_msg = "" if pd.isna(msg) else msg
            except Exception as e:
                logging.error(f"誕生日メッセージの読み込みエラー: {str(e)}")

        birthday_photo = st.file_uploader(
            t("🎉 写真をアップロード", "🎉 Upload a birthday photo"),
            type=["jpg", "jpeg", "png"],
            key="bday"
        )
        
        birthday_msg = st.text_area(
            t("🎁 ペットへのメッセージ", "🎁 Message to your pet"), 
            value=default_bday_msg
        )

        # 既存の画像があれば表示、新しくアップロードされた場合は保存して表示
        bday_path = os.path.join(IMAGE_DIR, f"{st.session_state.pet_name}_bday.jpg")
        
        if birthday_photo:
            if safe_save_image(birthday_photo, bday_path):
                st.subheader("🎉 " + t("誕生日写真", "Birthday Photo"))
                st.image(bday_path, use_container_width=True)
        elif os.path.exists(bday_path):
            st.subheader("🎉 " + t("保存済みの誕生日写真", "Saved Birthday Photo"))
            st.image(bday_path, use_container_width=True)

        if st.button(t("保存する", "Save"), key="save_birthday"):
            df_new = pd.DataFrame([{
                "名前": st.session_state.pet_name,
                "ページ": "誕生日メッセージ",
                "メッセージ": birthday_msg if birthday_msg else ""  # 明示的に空文字列を設定
            }])
            
            # 既存の行を削除し、新しいデータを追加
            try:
                df_filtered = df_save[(df_save["名前"] != st.session_state.pet_name) | 
                                    (df_save["ページ"] != "誕生日メッセージ")]
            except Exception as e:
                logging.error(f"フィルタリングエラー: {str(e)}")
                df_filtered = get_empty_dataframe("main")
                
            df_all = pd.concat([df_filtered, df_new], ignore_index=True)
            
            if safe_save_dataframe(df_all, SAVE_FILE):
                st.success(t("✅ 誕生日の記録を保存しました！", "✅ Birthday message saved!"))

        # 編集可能データの表示
        try:
            editable_df = df_save[(df_save["名前"] == st.session_state.pet_name) & 
                                (df_save["ページ"] == "誕生日メッセージ")]
        except Exception as e:
            logging.error(f"フィルタリングエラー: {str(e)}")
            editable_df = pd.DataFrame()
            
        editable_data(editable_df, "bday", "誕生日メッセージ")

    # ページ 7: 成長日記
    elif selected == t("7. 成長日記", "7. Growth Diary"):
        st.header(t("🗓 成長日記", "🗓 Growth Diary"))

        # 生まれた日を安全に取得
        birth_date = None
        try:
            birth_row = df_save[(df_save["名前"] == st.session_state.pet_name) & (df_save["ページ"] == "基本事項")]
            
            if not birth_row.empty:
                try:
                    birth_date_str = safe_get_value(birth_row, 0, "生まれた日", None)
                    if birth_date_str:
                        birth_date = pd.to_datetime(birth_date_str)
                except Exception as e:
                    st.warning(t("⚠️ 基本情報に生まれた日が正しく保存されていません。正しい形式で再入力してください。", 
                                "⚠️ Birth date is not correctly saved in basic info. Please re-enter in correct format."))
                    logging.error(f"生まれた日の読み込みエラー: {str(e)}")
            else:
                st.warning(t("⚠️ 基本情報に生まれた日が保存されていません。基本情報ページで設定してください。", 
                            "⚠️ Birth date not found in basic info. Please set it in Basic Info page."))
        except Exception as e:
            logging.error(f"基本情報の取得エラー: {str(e)}")
            st.warning(t("⚠️ 基本情報の取得中にエラーが発生しました。", 
                        "⚠️ An error occurred while retrieving basic info."))
        
        # 成長日記入力フォーム
        with st.form(key="growth_diary_form"):
            selected_date = st.date_input(t("📅 日付を選択", "📅 Select Date"), value=date.today())
            selected_time = st.time_input(t("🕒 時間を選択", "🕒 Select Time"), value=datetime.now().time())
            dt = datetime.combine(selected_date, selected_time)
            
            days_old = None
            if birth_date:
                try:
                    days_old = (dt.date() - birth_date.date()).days
                    st.markdown(t(f"**🐣 生後 {days_old} 日目の記録**", f"**🐣 Day {days_old} since birth**"))
                except Exception as e:
                    logging.error(f"日数計算エラー: {str(e)}")
            
            col1, col2 = st.columns(2)
            with col1:
                meal = st.text_input(t("🍽 食事の内容", "🍽 Meal Details"))
                meal_grams = st.number_input(t("グラム数 (g)", "Amount (g)"), 0, 500, step=5)
                potty = st.text_input(t("🚽 おしっこ・うんち", "🚽 Potty"))
            with col2:
                walk = st.text_input(t("🐕 散歩", "🐕 Walk"))
                sleep = st.text_input(t("😴 睡眠（例：22:00〜6:00）", "😴 Sleep (e.g. 10pm–6am)"))
                
            memo = st.text_area(t("📝 MEMO", "📝 Memo"))
            
            submit_button = st.form_submit_button(t("記録を保存する", "Save Record"))
            
            if submit_button:
                # 日記の保存処理
                try:
                    new_log = pd.DataFrame([{
                        "名前": st.session_state.pet_name,
                        "日付時間": dt,
                        "生後日数": days_old if days_old is not None else "",
                        "食事内容": meal if meal else "",
                        "グラム": meal_grams,
                        "おしっこ・うんち": potty if potty else "",
                        "散歩": walk if walk else "",
                        "睡眠": sleep if sleep else "",
                        "MEMO": memo if memo else ""
                    }])
                    
                    # 既存のログファイルがあれば読み込む
                    if os.path.exists(GROWTH_LOG_FILE):
                        old_log = safe_load_dataframe(GROWTH_LOG_FILE, "growth")
                        full_log = pd.concat([old_log, new_log], ignore_index=True)
                    else:
                        full_log = new_log
                    
                    if safe_save_dataframe(full_log, GROWTH_LOG_FILE):
                        st.success(t("✅ 記録を保存しました！", "✅ Record saved!"))
                except Exception as e:
                    st.error(t(f"エラーが発生しました: {str(e)}", f"An error occurred: {str(e)}"))
                    logging.error(f"成長記録保存エラー: {str(e)}\n{traceback.format_exc()}")
            
        # 🔍 成長記録の表示・編集
        st.divider()
        st.subheader(t("🔍 保存された成長記録", "🔍 Saved Growth Records"))
        
        if os.path.exists(GROWTH_LOG_FILE):
            try:
                df_growth = safe_load_dataframe(GROWTH_LOG_FILE, "growth")
                if df_growth.empty:
                    st.info(t("📭 まだ記録がありません", "📭 No records yet"))
                else:
                    # データの前処理
                    try:
                        df_growth["日付時間"] = pd.to_datetime(df_growth["日付時間"], errors='coerce')
                        filtered_growth = df_growth[df_growth["名前"] == st.session_state.pet_name]
                    except Exception as e:
                        logging.error(f"データ前処理エラー: {str(e)}")
                        filtered_growth = pd.DataFrame()
                    
                    if filtered_growth.empty:
                        st.info(t("📭 このペットの記録はまだありません", "📭 No records for this pet yet"))
                    else:
                        # タブでフィルタと編集を分ける
                        tab1, tab2 = st.tabs([
                            t("🔍 記録を検索・表示", "🔍 Search & View Records"),
                            t("✏️ 記録を編集", "✏️ Edit Records")
                        ])
                        
                        with tab1:
                            # 検索フィルタ
                            col1, col2 = st.columns(2)
                            with col1:
                                date_filter = st.date_input(
                                    t("📅 表示したい日付", "📅 Filter by date"),
                                    value=[],
                                    key="date_filter"
                                )
                            with col2:
                                keyword = st.text_input(
                                    t("🔍 キーワード検索", "🔍 Keyword search"),
                                    key="keyword_filter"
                                )
                            
                            filtered_df = filtered_growth.copy()
                            
                            # 日付フィルタの適用
                            if date_filter:
                                try:
                                    filtered_df = filtered_df[filtered_df["日付時間"].dt.date.isin(date_filter)]
                                except Exception as e:
                                    logging.error(f"日付フィルタエラー: {str(e)}")
                            
                            # キーワードフィルタの適用
                            if keyword:
                                try:
                                    filtered_df = filtered_df[filtered_df.astype(str).apply(
                                        lambda row: keyword.lower() in ' '.join(row.values.astype(str)).lower(), axis=1
                                    )]
                                except Exception as e:
                                    logging.error(f"キーワードフィルタエラー: {str(e)}")
                            
                            # 結果の表示
                            if not filtered_df.empty:
                                st.dataframe(filtered_df, use_container_width=True)
                            else:
                                st.info(t("🔍 条件に一致する記録が見つかりませんでした", 
                                          "🔍 No records found matching your criteria"))
                        
                        with tab2:
                            try:
                                edited = st.data_editor(
                                    filtered_growth, 
                                    num_rows="dynamic", 
                                    use_container_width=True,
                                    key="growth_editor"
                                )
                                
                                if st.button(t("変更を保存する", "Save Changes"), key="save_growth_edit"):
                                    # 全体のログから該当ペットの記録を削除し、編集された記録を追加
                                    try:
                                        full_log = safe_load_dataframe(GROWTH_LOG_FILE, "growth")
                                        others = full_log[full_log["名前"] != st.session_state.pet_name]
                                        combined = pd.concat([others, edited], ignore_index=True)
                                        
                                        if safe_save_dataframe(combined, GROWTH_LOG_FILE):
                                            st.success(t("✅ 編集内容を保存しました！", "✅ Changes saved!"))
                                    except Exception as e:
                                        st.error(t(f"エラーが発生しました: {str(e)}", f"An error occurred: {str(e)}"))
                                        logging.error(f"成長記録編集エラー: {str(e)}\n{traceback.format_exc()}")
                            except Exception as e:
                                st.error(t(f"データエディタの表示中にエラーが発生しました: {str(e)}", 
                                           f"An error occurred while displaying data editor: {str(e)}"))
                                logging.error(f"データエディタエラー: {str(e)}")
                                    
            except Exception as e:
                st.error(t(f"データの読み込み中にエラーが発生しました: {str(e)}", 
                           f"An error occurred while loading data: {str(e)}"))
                logging.error(f"成長記録読み込みエラー: {str(e)}\n{traceback.format_exc()}")
        else:
            st.info(t("📝 まだ記録がありません。上のフォームから記録を追加してください。", 
                       "📝 No records yet. Add records using the form above."))

    # ページ 8: メモ欄
    elif selected == t("8. メモ欄", "8. Notes"):
        st.header(t("📝 自由メモ欄", "📝 Free Notes"))

        # 既存のメモを取得
        existing_memo = ""
        
        if os.path.exists(MEMO_LOG_FILE):
            try:
                memo_df = safe_load_dataframe(MEMO_LOG_FILE, "memo")
                memo_entries = memo_df[memo_df["名前"] == st.session_state.pet_name]
                
                if not memo_entries.empty:
                    try:
                        # 最新のメモを表示
                        memo_entries["日付"] = pd.to_datetime(memo_entries["日付"], errors='coerce')
                        memo_entries = memo_entries.sort_values("日付", ascending=False)
                        if len(memo_entries) > 0:
                            existing_memo = safe_get_value(memo_entries, 0, "メモ", "")
                    except Exception as e:
                        logging.error(f"メモデータの読み込みエラー: {str(e)}")
            except Exception as e:
                logging.error(f"メモファイル読み込みエラー: {str(e)}")

        with st.form(key="memo_form"):
            memo_input = st.text_area(
                t("気づいたこと、生活のことなどを自由に記入できます", 
                  "You can freely write your observations, lifestyle notes, etc."),
                value=existing_memo,
                height=200
            )
            
            submit_button = st.form_submit_button(t("保存する", "Save"))
            
            if submit_button:
                try:
                    memo_df = pd.DataFrame([{
                        "名前": st.session_state.pet_name,
                        "ページ": "メモ欄",
                        "日付": date.today(),
                        "メモ": memo_input if memo_input else ""  # 明示的に空文字列を設定
                    }])
                    
                    if os.path.exists(MEMO_LOG_FILE):
                        existing = safe_load_dataframe(MEMO_LOG_FILE, "memo")
                        memo_df = pd.concat([existing, memo_df], ignore_index=True)
                    
                    if safe_save_dataframe(memo_df, MEMO_LOG_FILE):
                        st.success(t("✅ メモを保存しました！", "✅ Memo saved!"))
                except Exception as e:
                    st.error(t(f"エラーが発生しました: {str(e)}", f"An error occurred: {str(e)}"))
                    logging.error(f"メモ保存エラー: {str(e)}\n{traceback.format_exc()}")

        # メモの履歴表示
        if os.path.exists(MEMO_LOG_FILE):
            try:
                df_memo = safe_load_dataframe(MEMO_LOG_FILE, "memo")
                df_memo = df_memo[df_memo["名前"] == st.session_state.pet_name]
                
                if not df_memo.empty:
                    st.divider()
                    st.subheader(t("📚 メモ履歴", "📚 Memo History"))
                    
                    try:
                        # 日付でソート
                        df_memo["日付"] = pd.to_datetime(df_memo["日付"], errors='coerce')
                        df_memo = df_memo.sort_values("日付", ascending=False)
                    except Exception as e:
                        logging.error(f"メモソートエラー: {str(e)}")
                    
                    editable_data(df_memo, "memo", "メモ欄")
                    
            except Exception as e:
                st.error(t(f"メモ履歴の表示中にエラーが発生しました: {str(e)}", 
                          f"An error occurred while displaying memo history: {str(e)}"))
                logging.error(f"メモ履歴表示エラー: {str(e)}\n{traceback.format_exc()}")

# フッター
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 10px; border-top: 1px solid #ddd;">
    <p style="color: #555; font-size: 14px;">
        🐾 ペット成長日記 / Pet Growth Diary © 2025
    </p>
</div>
""", unsafe_allow_html=True)
