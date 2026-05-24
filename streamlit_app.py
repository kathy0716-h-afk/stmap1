import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- ページ設定 ---
st.set_page_config(page_title="日本全国気温 3D Map", layout="wide")
st.title("日本全国（47都道府県）の現在の気温 3Dカラムマップ")

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
    'Okinawa':
