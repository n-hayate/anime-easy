import streamlit as st
import openai
import requests
from dotenv import load_dotenv
import os

# .envファイルから環境変数を読み込む
load_dotenv()

# OPENAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")


# Jikan APIのエンドポイント
JIKAN_API_BASE_URL = "https://api.jikan.moe/v4"

def search_anime(title):
    """Jikan APIでアニメを検索する関数"""
    response = requests.get(f"{JIKAN_API_BASE_URL}/anime?q={title}&limit=1")
    data = response.json()
    if data and data['data']:
        return data['data'][0]
    return None

def generate_synopsis(anime_info):
    """OPENAI APIであらすじを生成する関数（日本語対応、gpt-3.5-turbo）"""
    if not anime_info:
        return "アニメ情報が見つかりませんでした。"

    prompt = f"""以下の情報をもとに、このアニメの日本語のあらすじを生成してください。

    タイトル: {anime_info['title']}
    ジャンル: {', '.join([genre['name'] for genre in anime_info['genres']])}
    放送時期: {anime_info['aired']['string']}
    簡単な概要: {anime_info['synopsis'][:200] if anime_info['synopsis'] else 'なし'}

    あらすじ:
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"あらすじの生成に失敗しました: {e}"

def main():
    st.title("アニメあらすじ自動生成アプリ")

    anime_title = st.text_input("アニメタイトルを入力してください")
    search_button = st.button("検索")

    if search_button:
        anime_data = search_anime(anime_title)
        st.session_state.anime_data = anime_data
        st.session_state.synopsis = None
    elif "anime_data" in st.session_state and st.session_state.anime_data:
        anime_data = st.session_state.anime_data
    else:
        anime_data = None

    if anime_data:
        st.subheader(f"検索結果: {anime_data['title']}")
        st.write(f"**ジャンル:** {', '.join([genre['name'] for genre in anime_data['genres']])}")
        st.write(f"**放送時期:** {anime_data['aired']['string']}")
        if anime_data['synopsis']:
            st.write(f"**簡単な概要:** {anime_data['synopsis'][:200]}...")

        generate_button = st.button("あらすじを生成")
        if generate_button:
            with st.spinner("あらすじを生成中です..."):
                synopsis = generate_synopsis(anime_data)
                st.session_state.synopsis = synopsis
        elif "synopsis" in st.session_state:
            synopsis = st.session_state.synopsis
        else:
            synopsis = None

        if synopsis:
            st.subheader("生成されたあらすじ")
            st.write(synopsis)

if __name__ == "__main__":
    main()