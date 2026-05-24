import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- ページ設定 ---
st.set_page_config(page_title="東北気温 3D Map", layout="wide")
st.title("東北主要都市の現在の気温 3Dカラムマップ")

# 東北6県のデータ（県庁所在地の緯度・経度）
tohoku_capitals = {
    'Aomori':    {'lat': 40.8246, 'lon': 140.7406},
    'Morioka':   {'lat': 39.7020, 'lon': 141.1545},
    'Sendai':    {'lat': 38.2682, 'lon': 140.8694},
    'Akita':     {'lat': 39.7200, 'lon': 140.1026},
    'Yamagata':  {'lat': 38.2404, 'lon': 140.3636},
    'Fukushima': {'lat': 37.7608, 'lon': 140.4748}
}

# --- データ取得関数 ---
@st.cache_data(ttl=600)
def fetch_weather_data():
    weather_info = []
    BASE_URL = 'https://api.open-meteo.com/v1/forecast'
    
    for city, coords in tohoku_capitals.items():
        params = {
            'latitude':  coords['lat'],
            'longitude': coords['lon'],
            'current': 'temperature_2m'
        }
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            weather_info.append({
                'City': city,
                'lat': coords['lat'],
                'lon': coords['lon'],
                'Temperature': data['current']['temperature_2m']
            })
        except Exception as e:
            st.error(f"Error fetching {city}: {e}")
            
    return pd.DataFrame(weather_info)

# データの取得
with st.spinner('最新の気温データを取得中...'):
    df = fetch_weather_data()

# 気温を高さ（メートル）に変換（例：1度 = 3000m）
df['elevation'] = df['Temperature'] * 3000

# --- メインレイアウト ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("取得したデータ")
    st.dataframe(df[['City', 'Temperature']], use_container_width=True)
    
    if st.button('データを更新'):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.subheader("3D カラムマップ")

    # Pydeck の設定（東北地方の中心にカメラを合わせる）
    view_state = pdk.ViewState(
        latitude=39.5,   # 東北の中心付近（岩手・秋田あたり）
        longitude=140.5,
        zoom=6.0,        # 九州より少し広めに映るように微調整
        pitch=45,
        bearing=0
    )

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        radius=12000,        # 柱の太さ
        get_fill_color='[255, 100, 0, 180]', # 柱の色（オレンジ系）
        pickable=True,       # ホバーを有効に
        auto_highlight=True,
    )

    # 描画
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{City}</b><br>気温: {Temperature}°C",
            "style": {"color": "white"}
        }
    ))
