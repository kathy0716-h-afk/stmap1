import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- ページ設定 ---
st.set_page_config(page_title="📍日本全国気温 3D Map", layout="wide")
st.title("🗺️日本全国（47都道府県）の現在の気温 3Dカラムマップ")

# 47都道府県のデータ（県庁所在地の緯度・経度）
japan_capitals = {
    'Hokkaido': {'lat': 43.0642, 'lon': 141.3469},
    'Aomori': {'lat': 40.8246, 'lon': 140.7406},
    'Iwate': {'lat': 39.7020, 'lon': 141.1545},
    'Miyagi': {'lat': 38.2682, 'lon': 140.8694},
    'Akita': {'lat': 39.7200, 'lon': 140.1026},
    'Yamagata': {'lat': 38.2404, 'lon': 140.3636},
    'Fukushima': {'lat': 37.7608, 'lon': 140.4748},
    'Ibaraki': {'lat': 36.3418, 'lon': 140.4468},
    'Tochigi': {'lat': 36.5657, 'lon': 139.8836},
    'Gunma': {'lat': 36.3911, 'lon': 139.0608},
    'Saitama': {'lat': 35.8572, 'lon': 139.6490},
    'Chiba': {'lat': 35.6051, 'lon': 140.1233},
    'Tokyo': {'lat': 35.6895, 'lon': 139.6917},
    'Kanagawa': {'lat': 35.4478, 'lon': 139.6425},
    'Niigata': {'lat': 37.9024, 'lon': 139.0232},
    'Toyama': {'lat': 36.6953, 'lon': 137.2113},
    'Ishikawa': {'lat': 36.5947, 'lon': 136.6256},
    'Fukui': {'lat': 36.0641, 'lon': 136.2219},
    'Yamanashi': {'lat': 35.6639, 'lon': 138.5683},
    'Nagano': {'lat': 36.6513, 'lon': 138.1812},
    'Gifu': {'lat': 35.4233, 'lon': 136.7607},
    'Shizuoka': {'lat': 34.9756, 'lon': 138.3828},
    'Aichi': {'lat': 35.1815, 'lon': 136.9066},
    'Mie': {'lat': 34.7303, 'lon': 136.5086},
    'Shiga': {'lat': 35.0142, 'lon': 135.8589},
    'Kyoto': {'lat': 35.0116, 'lon': 135.7681},
    'Osaka': {'lat': 34.6937, 'lon': 135.5023},
    'Hyogo': {'lat': 34.6913, 'lon': 135.1830},
    'Nara': {'lat': 34.6851, 'lon': 135.8048},
    'Wakayama': {'lat': 34.2260, 'lon': 135.1675},
    'Tottori': {'lat': 35.5011, 'lon': 134.2351},
    'Shimane': {'lat': 35.4723, 'lon': 133.0505},
    'Okayama': {'lat': 34.6618, 'lon': 133.9344},
    'Hiroshima': {'lat': 34.3853, 'lon': 132.4553},
    'Yamaguchi': {'lat': 34.1861, 'lon': 131.4705},
    'Tokushima': {'lat': 34.0704, 'lon': 134.5594},
    'Kagawa': {'lat': 34.3401, 'lon': 134.0434},
    'Ehime': {'lat': 33.8392, 'lon': 132.7653},
    'Kochi': {'lat': 33.5597, 'lon': 133.5311},
    'Fukuoka': {'lat': 33.5904, 'lon': 130.4017},
    'Saga': {'lat': 33.2494, 'lon': 130.2974},
    'Nagasaki': {'lat': 32.7450, 'lon': 129.8739},
    'Kumamoto': {'lat': 32.7900, 'lon': 130.7420},
    'Oita': {'lat': 33.2381, 'lon': 131.6119},
    'Miyazaki': {'lat': 31.9110, 'lon': 131.4240},
    'Kagoshima': {'lat': 31.5600, 'lon': 130.5580},
    'Okinawa': {'lat': 26.2124, 'lon': 127.6809}
}

# --- データ取得関数 ---
@st.cache_data(ttl=600)
def fetch_weather_data():
    weather_info = []
    BASE_URL = 'https://api.open-meteo.com/v1/forecast'
    
    for city, coords in japan_capitals.items():
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
with st.spinner('全国47都道府県の最新気温データを取得中...'):
    df = fetch_weather_data()

# 気温を高さ（メートル）に変換
# 氷点下の場合は高さがマイナス（下向き）になるのを防ぎたい場合は max(0.1, x) などにする手もありますが、
# 今回はそのままのスケールを使用します。
df['elevation'] = df['Temperature'] * 3000

# --- 色の計算ロジック（気温に基づくグラデーション） ---
def get_color(temperature):
    # 気温の範囲（北海道の冬〜沖縄の夏を想定: -10度〜35度）
    min_temp = -10
    max_temp = 35
    
    # 範囲内に収める
    temp = max(min(temperature, max_temp), min_temp)
    
    # 正規化 (0.0 〜 1.0)
    ratio = (temp - min_temp) / (max_temp - min_temp)
    
    # グラデーション計算（青 -> 緑 -> 黄 -> 赤）
    if ratio < 0.33: # 青 -> 緑
        r = 0
        g = int(255 * (ratio / 0.33))
        b = 255
    elif ratio < 0.66: # 緑 -> 黄
        r = int(255 * ((ratio - 0.33) / 0.33))
        g = 255
        b = int(255 * (1 - (ratio - 0.33) / 0.33))
    else: # 黄 -> 赤
        r = 255
        g = int(255 * (1 - (ratio - 0.66) / 0.34))
        b = 0
    
    return [r, g, b, 200]

# データフレームに色の列を追加
df['color'] = df['Temperature'].apply(get_color)

# --- メインレイアウト ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("取得したデータ")
    # 高さが足りない場合は高さ指定を追加 (例: height=600)
    st.dataframe(df[['City', 'Temperature']], height=500, use_container_width=True)
    
    if st.button('データを更新'):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.subheader("3D カラムマップ")

    # Pydeck の設定（日本全体が見えるようにズームと中心座標を調整）
    view_state = pdk.ViewState(
        latitude=37.0,   # 日本のほぼ中央（新潟・長野あたり）
        longitude=137.5,
        zoom=4.5,        # 全国が入るようにズームアウト
        pitch=45,
        bearing=0
    )

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        radius=15000,        # ズームアウトに合わせて柱を少し太く（15km）
        get_fill_color='color', 
        pickable=True,
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
