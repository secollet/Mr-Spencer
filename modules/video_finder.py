import streamlit as st
import subprocess
import json
import time
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
from io import BytesIO
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def initialize_session_state():
    """Initialize session state for dynamic lists."""
    if 'aliases' not in st.session_state:
        st.session_state.aliases = ['']
    if 'handles' not in st.session_state:
        st.session_state.handles = ['']
    if 'excluded_accounts' not in st.session_state:
        st.session_state.excluded_accounts = ['']


def add_list_item(list_key):
    """Add another item to a dynamic list."""
    st.session_state[list_key].append('')


def render_dynamic_list(label, session_key, placeholder=""):
    """Render a dynamic list input with 'Add Another' button."""
    st.write(f"**{label}**")

    items = []
    cols = st.columns([1, 0.15])

    with cols[0]:
        for i, item in enumerate(st.session_state[session_key]):
            st.session_state[session_key][i] = st.text_input(
                f"{label} {i+1}",
                value=item,
                placeholder=placeholder,
                label_visibility="collapsed",
                key=f"{session_key}_{i}"
            )

    with cols[1]:
        if st.button("Add", key=f"btn_{session_key}", use_container_width=True):
            add_list_item(session_key)
            st.rerun()

    return [item.strip() for item in st.session_state[session_key] if item.strip()]


def check_yt_dlp_installed():
    """Check if yt-dlp is installed."""
    try:
        subprocess.run(['yt-dlp', '--version'],
                      capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
YÙX\ÚÞ[Ý]XJ\Ù]Û[YK[X\Ù\Ë[\Ë^ÛYYÝ\ËÙÜ\Ü×ÜXÙZÛ\NÙX\Ú[ÝUXH\Ú[È]Y\Ý[ÈH×BÙX\ÚÜ]Y\Y\ÈHÝ\Ù]Û[YWH
È[X\Ù\È
È[\ÂÙX\ÚÜ]Y\Y\ÈHÜKÝ\

HÜH[ÙX\ÚÜ]Y\Y\ÈYKÝ\

WBÝ[Ü]Y\Y\ÈH[ÙX\ÚÜ]Y\Y\ÊBÜY]Y\H[[[Y\]JÙX\ÚÜ]Y\Y\ÊNÙÜ\Ü×ÜXÙZÛ\ÙÜ\ÜÊ
YÈÝ[Ü]Y\Y\ÊH
LÈ
BÝÜ]JÙX\Ú[È[ÝUXHÜÜ]Y\_HBNÛYHÂ	Þ]Y	ËÞ]ÙX\ÚLÜ]Y\_IË	ËKY[\ZÛÛË	ËKY]\^[\Ý	Ë	ËK[ËYÝÛØY	Ë	ËK\ÛØÚÙ]][Y[Ý]	Ë	ÌL	ÂB\Ý[HÝXØÙ\ÜË[ÛYØ\\WÛÝ]]UYK^UYK[Y[Ý]LÌ
BY\Ý[]\ÛÙHOHÛÛ[YBÜ[H[\Ý[ÝÝ]Ý\

KÜ]
	×ÊNYÝ[KÝ\

NÛÛ[YBN[HHÛÛØYÊ[JBÈ^XÝY[È[ÜX][ÛY[×Ý\H[KÙ]
	ÝÙXYÙWÝ\	ÊHÜ[KÙ]
	Ý\	ÊBYÝY[×Ý\ÛÛ[YBÈÚXÚÈYÚ[[TÚÝ[H^ÛYYÚ[[Ý\H[KÙ]
	ØÚ[[Ý\	Ë	ÉÊBYÚ[[Ý\[[J^ÛYY[Ú[[Ý\Ü^ÛYY[^ÛYYÝ\ÊNÛÛ[YB\Ý[Ë\[
Â	Ó[ÉÎY[×Ý\	ÔÛÝ\ÙH]ÜIÎ	Ö[ÝUXIË	Ñ]HX\ÚY	Î[KÙ]
	Ý\ØYÙ]IË	Õ[ÛÝÛÊK	ÕY[È]IÎ[KÙ]
	Ý]IË	Õ[ÛÝÛÊK	Ñ\ØÜ\[ÛÎ[KÙ]
	Ù\ØÜ\[ÛË	ÉÊK	Õ\ØY\ÐÚ[[[YIÎ[KÙ]
	ØÚ[[	Ë	Õ[ÛÝÛÊK	ÐÚ[[T	ÎÚ[[Ý\	ÕYÙÙY[\ÈÝ[	Î]Y\HY]Y\H[[\È[ÙH	ÉÂJB^Ù\ÛÛÓÓXÛÙQ\ÜÛÛ[YB[YKÛY\
JB^Ù\ÝXØÙ\ÜË[Y[Ý]^\YÝØ\[Ê[ÝUXHÙX\Ú[YYÝ]Ü]Y\NÜ]Y\_HB^Ù\^Ù\[Û\ÈNÝØ\[Ê\ÜÙX\Ú[È[ÝUXHÜ	ÞÜ]Y\_IÎÜÝJ_HB]\\Ý[ÂYÙX\ÚÙÛÛÙÛWÝY[ÜÊ\Ù]Û[YK[X\Ù\Ë[\Ë]Ü\ËÙÜ\Ü×ÜXÙZÛ\Ý\[ÜÙÜ\ÜÊNÙX\ÚÛÛÙÛHÜY[ÜÈÛÜXÚYYY]Ü\Ë\Ý[ÈH×BÙ\ÜÚ[ÛH\]Y\ÝËÙ\ÜÚ[Û
BÙ\ÜÚ[ÛXY\Ë\]JÂ	Õ\Ù\PYÙ[	Î	Ó[Þ[KÍK
Ú[ÝÜÈLÈÚ[È

H\UÙXÚ]ÍLÍËÍÂJBÈZ[ÙX\Ú]Y\Y\ÈÜXXÚ]ÜBÙX\ÚÝ\ÚÜÈH×BÜ]ÜH[]Ü\ÎY]ÜH[ÉÖ[ÝUXIË	Õ[Y[ÉË	Ô[XIË	ÑZ[[[Ý[ÛË	Ð\Ú]KÜÉ×NÚ]WÙÛXZ[HÂ	Ö[ÝUXIÎ	Þ[Ý]XKÛÛIË	Õ[Y[ÉÎ	Ý[Y[ËÛÛIË	Ô[XIÎ	Ü[XKÛÛIË	ÑZ[[[Ý[ÛÎ	ÙZ[[[Ý[ÛÛÛIË	Ð\Ú]KÜÉÎ	Ø\Ú]KÜÉÂKÙ]
]ÜK	ÉÊBYÝÚ]WÙÛXZ[ÛÛ[YBÈÜ[Y[ËÙX\ÚH[YH[[\ÂÙX\ÚÜ]Y\Y\ÈHÝ\Ù]Û[YWH
È[X\Ù\ÂY]ÜHOH	Õ[Y[ÉÎÙX\ÚÜ]Y\Y\Ë^[
[\ÊBÜ]Y\H[ÙX\ÚÜ]Y\Y\ÎY]Y\KÝ\

NÙX\ÚÝ\ÚÜË\[

]ÜKÚ]WÙÛXZ[]Y\KÝ\

K	Û[YIÊJBÈ[ÛÈÙX\ÚÚ][\ÂÜ[H[[\ÎY[KÝ\

NÙX\ÚÝ\ÚÜË\[

]ÜKÚ]WÙÛXZ[[KÝ\

K	Ú[IÊJBÝ[Ý\ÚÜÈH[ÙX\ÚÝ\ÚÜÊBÜ\Ú×ÚY
]ÜKÚ]WÙÛXZ[]Y\K]Y\WÝ\JH[[[Y\]JÙX\ÚÝ\ÚÜÊNÙÜ\Ü×Ü\Ù[HÝ\[ÜÙÜ\ÜÈ
È
\Ú×ÚYÈÝ[Ý\ÚÜÊH

LÈ
ÙÜ\Ü×ÜXÙZÛ\ÙÜ\ÜÊZ[ÙÜ\Ü×Ü\Ù[ÈLMJJBNÈZ[ÙX\Ú]Y\BY]Y\WÝ\HOH	Ú[IÈ[]Y\KÝ\ÝÚ]
	Ð	ÊNÛÛÙÛWÜ]Y\HHÈÜ]Y\_HÚ]NÜÚ]WÙÛXZ[HY[ÉÂ[Y]Y\WÝ\HOH	Ú[IÎÛÛÙÛWÜ]Y\HHÈÜ]Y\_HÚ]NÜÚ]WÙÛXZ[HY[ÉÂ[ÙNÛÛÙÛWÜ]Y\HHÈÜ]Y\_HÚ]NÜÚ]WÙÛXZ[HY[ÉÂÙX\ÚÝ\HÚÎËÝÝÝËÛÛÙÛKÛÛKÜÙX\ÚÜO^Ü][ÝWÜ\ÊÛÛÙÛWÜ]Y\J_IÂ\ÜÛÙHHÙ\ÜÚ[ÛÙ]
ÙX\ÚÝ\[Y[Ý]LL
B\ÜÛÙKZ\ÙWÙÜÜÝ]\Ê
BÛÝ\HX]]Y[ÛÝ\
\ÜÛÙKÛÛ[	Ú[\Ù\ÊBÈ^XÝY[ÈTÈÛHÙX\Ú\Ý[ÂÜ[È[ÛÝ\[Ø[
	ØIËYUYJNYH[ÖÉÚY×BÈ[\ÜY[È[ÜÂYÚ]WÙÛXZ[[Y[
	ÝØ]Ú	È[YÜ	ÝY[ÉÈ[YÜ	ÝIÈ[YNÈ^XÝÛX[TY	ËÝ\ÜOIÈ[YÛX[Ý\HYÜ]
	ËÝ\ÜOIÊVÌWKÜ]
	ÉÊVÌB[ÙNÛX[Ý\HYÈÚÚ\ÛÛÙÛHY\XÝÂY	ÙÛÛÙÛKÛÛIÈ[ÛX[Ý\ÛÛ[YB]HH[ËÙ]Ý^

HÜ	Õ[ÛÝÛÂ\Ý[Ë\[
Â	Ó[ÉÎÛX[Ý\	ÔÛÝ\ÙH]ÜIÎ]ÜK	Ñ]HX\ÚY	Î	Õ[ÛÝÛË	ÕY[È]IÎ]K	Ñ\ØÜ\[ÛÎ	ÉË	Õ\ØY\ÐÚ[[[YIÎ	ÉË	ÐÚ[[T	Î	ÉË	ÕYÙÙY[\ÈÝ[	Î]Y\HY]Y\WÝ\HOH	Ú[IÈ[ÙH	ÉÂJB[YKÛY\
HÈ]H[Z][Â^Ù\\]Y\ÝË\]Y\Ý^Ù\[Û\ÈNÝØ\[Ê\ÜÙX\Ú[ÈÜ]Ü_HÜ	ÞÜ]Y\_IÎÜÝJ_HB^Ù\^Ù\[Û\ÈNÝØ\[Ê[^XÝY\ÜÙX\Ú[ÈÜ]Ü_NÜÝJ_HB]\\Ý[À(()ÍÉ¡}Í½¥±}Ñ}½¹Ñ¹Ð¡ÑÉÑ}¹µ°¡¹±Ì°ÁÉ½ÉÍÍ}Á±¡½±È°ÕÉÉ¹Ñ}ÁÉ½ÉÍÌ¤è(MÉ ½ÈÑ½¹Ñ¹Ð½¸Í½¥°µ¥Á±Ñ½ÉµÌ¸(ÉÍÕ±ÑÌômt(ÍÍÍ¥½¸ôÉÅÕÍÑÌ¹MÍÍ¥½¸ ¤(ÍÍÍ¥½¸¹¡ÉÌ¹ÕÁÑ¡ì(UÍÈµ¹Ðè5½é¥±±¼Ô¸À¡]¥¹½ÝÌ9PÄÀ¸Àì]¥¸ØÐìàØÐ¤ÁÁ±]-¥Ð¼ÔÌÜ¸ÌØ(ô¤((Á±Ñ½ÉµÌôì(QÝ¥ÑÑÈ½`èÑÝ¥ÑÑÈ¹½´°(%¹ÍÑÉ´è¥¹ÍÑÉ´¹½´°(Q¥­Q½¬èÑ¥­Ñ½¬¹½´°(½½¬è½½¬¹½´(ô((ÍÉ¡}ÑÍ­Ìômt((	Õ¥±ÍÉ ÑÍ­Ì(½ÈÁ±Ñ½Éµ}¹µ°Í¥Ñ}½µ¥¸¥¸Á±Ñ½ÉµÌ¹¥ÑµÌ ¤è(MÉ ä¹µ(ÍÉ¡}ÑÍ­Ì¹ÁÁ¹ ¡Á±Ñ½Éµ}¹µ°Í¥Ñ}½µ¥¸°ÑÉÑ}¹µ°¹µ¤¤((MÉ ä ¡¹±(½È¡¹±¥¸¡¹±Ìè(¥¡¹±¹ÍÑÉ¥À ¤è(ÍÉ¡}ÑÍ­Ì¹ÁÁ¹ ¡Á±Ñ½Éµ}¹µ°Í¥Ñ}½µ¥¸°¡¹±¹ÍÑÉ¥À ¤°¡¹±¤¤((Ñ½Ñ±}ÑÍ­Ìô±¸¡ÍÉ¡}ÑÍ­Ì¤((½ÈÑÍ­}¥à°¡Á±Ñ½É´°Í¥Ñ}½µ¥¸°ÅÕÉä°ÅÕÉå}ÑåÁ¤¥¸¹ÕµÉÑ¡ÍÉ¡}ÑÍ­Ì¤è(ÁÉ½ÉÍÍ}ÁÉ¹ÐôÕÉÉ¹Ñ}ÁÉ½ÉÍÌ¬¡ÑÍ­}¥à¼Ñ½Ñ±}ÑÍ­Ì¤¨ÈÔ¼Ð(ÁÉ½ÉÍÍ}Á±¡½±È¹ÁÉ½ÉÍÌ¡µ¥¸¡ÁÉ½ÉÍÍ}ÁÉ¹Ð¼ÄÀÀ°À¸äÔ¤¤((ÑÉäè(	Õ¥±ÍÉ ÅÕÉä(¥ÅÕÉå}ÑåÁôô¡¹±¹ÅÕÉä¹ÍÑÉÑÍÝ¥Ñ   ¤è(½½±}ÅÕÉäôíÅÕÉåôÍ¥ÑéíÍ¥Ñ}½µ¥¹ôÙ¥¼(±¥ÅÕÉå}ÑåÁôô¡¹±è(½½±}ÅÕÉäôíÅÕÉåôÍ¥ÑéíÍ¥Ñ}½µ¥¹ôÙ¥¼(±Íè(½½±}ÅÕÉäôíÅÕÉåôÍ¥ÑéíÍ¥Ñ}½µ¥¹ôÙ¥¼((ÍÉ¡}ÕÉ°ô¡ÑÑÁÌè¼½ÝÝÜ¹½½±¹½´½ÍÉ ýÄõíÅÕ½Ñ}Á±ÕÌ¡½½±}ÅÕÉä¥ô((ÉÍÁ½¹ÍôÍÍÍ¥½¸¹Ð¡ÍÉ¡}ÕÉ°°Ñ¥µ½ÕÐôÄÀ¤(ÉÍÁ½¹Í¹É¥Í}½É}ÍÑÑÕÌ ¤((Í½ÕÀô	ÕÑ¥Õ±M½ÕÀ¡ÉÍÁ½¹Í¹½¹Ñ¹Ð°¡Ñµ°¹ÁÉÍÈ¤((áÑÉÐÙ¥¼UI1Ì(½È±¥¹¬¥¸Í½ÕÀ¹¥¹}±° °¡ÉõQÉÕ¤è(¡Éô±¥¹­l¡Ét((¥Í¥Ñ}½µ¥¸¥¸¡Éè(¥½ÕÉ°ýÄô¥¸¡Éè(±¹}ÕÉ°ô¡É¹ÍÁ±¥Ð ½ÕÉ°ýÄô¥lÅt¹ÍÁ±¥Ð ¥lÁt(±Íè(±¹}ÕÉ°ô¡É((¥½½±¹½´¥¸±¹}ÕÉ°è(½¹Ñ¥¹Õ((Ñ¥Ñ±ô±¥¹¬¹Ñ}ÑáÐ ¤½ÈU¹­¹½Ý¸((ÉÍÕ±ÑÌ¹ÁÁ¹¡ì(1¥¹¬è±¹}ÕÉ°°(M½ÕÉA±Ñ½É´èÁ±Ñ½É´°(ÑAÕ±¥Í¡èU¹­¹½Ý¸°(Y¥¼Q¥Ñ±èÑ¥Ñ±°(ÍÉ¥ÁÑ¥½¸è°(UÁ±½È½
¡¹¹°9µè°(
¡¹¹°UI0è°(Q!¹±Ì½Õ¹èÅÕÉä¥ÅÕÉå}ÑåÁôô¡¹±±Í(ô¤((Ñ¥µ¹Í±À È¤IÑ±¥µ¥Ñ¥¹((áÁÐÉÅÕÍÑÌ¹IÅÕÍÑáÁÑ¥½¸Ìè(ÍÐ¹ÝÉ¹¥¹¡ÉÉ½ÈÍÉ¡¥¹íÁ±Ñ½Éµô½ÈíÅÕÉåôèíÍÑÈ¡¥ô¤(áÁÐáÁÑ¥½¸Ìè(ÍÐ¹ÝÉ¹¥¹¡U¹áÁÑÉÉ½ÈÍÉ¡¥¹íÁ±Ñ½ÉµôèíÍÑÈ¡¥ô¤((ÉÑÕÉ¸ÉÍÕ±ÑÌ(()¹É¥¡}µÑÑ}Ý¥Ñ¡}åÑ±À¡Ù¥½}ÕÉ°¤è(¹É¥ Ù¥¼µÑÑÕÍ¥¹åÐµ±À¸(ÑÉäè(µôl(åÐµ±À°(´µÕµÀµ©Í½¸°(´µ¹¼µ½Ý¹±½°(´µÍ½­ÐµÑ¥µ½ÕÐ°ÄÀ°(Ù¥½}ÕÉ°(t((ÉÍÕ±ÐôÍÕÁÉ½ÍÌ¹ÉÕ¸¡µ°ÁÑÕÉ}½ÕÑÁÕÐõQÉÕ°ÑáÐõQÉÕ°Ñ¥µ½ÕÐôÄÔ¤((¥ÉÍÕ±Ð¹ÉÑÕÉ¹½ôôÀè(ÑÉäè(Ñô©Í½¸¹±½Ì¡ÉÍÕ±Ð¹ÍÑ½ÕÐ¤(ÉÑÕÉ¸ì(ÕÁ±½}ÑèÑ¹Ð ÕÁ±½}Ñ°¤°(ÍÉ¥ÁÑ¥½¸èÑ¹Ð ÍÉ¥ÁÑ¥½¸°¤°(ÕÁ±½ÈèÑ¹Ð ÕÁ±½È°¤(ô(áÁÐ©Í½¸¹)M=9½ÉÉ½Èè(ÉÑÕÉ¸íô((ÉÑÕÉ¸íô((áÁÐáÁÑ¥½¸è(ÉÑÕÉ¸íô(()ÕÁ±¥Ñ}ÉÍÕ±ÑÌ¡ÉÍÕ±ÑÌ¤è(Iµ½ÙÕÁ±¥ÑUI1ÌÉ½´ÉÍÕ±ÑÌ¸(Í¹}ÕÉ±ÌôÍÐ ¤(ÕÁ±¥Ñômt((½ÈÉÍÕ±Ð¥¸ÉÍÕ±ÑÌè(ÕÉ°ôÉÍÕ±Ð¹Ð 1¥¹¬°¤(¥ÕÉ°¹½Ð¥¸Í¹}ÕÉ±Ìè(Í¹}ÕÉ±Ì¹¡ÕÉ°¤(ÕÁ±¥Ñ¹ÁÁ¹¡ÉÍÕ±Ð¤((ÉÑÕÉ¸ÕÁ±¥Ñ(()ÁÁ±å}á±Õ}¥±ÑÈ¡ÉÍÕ±ÑÌ°á±Õ}ÕÉ±Ì¤è(¥±ÑÈ½ÕÐÉÍÕ±ÑÌµÑ¡¥¹á±Õ½Õ¹ÐUI1Ì¸(¥±ÑÉômt((½ÈÉÍÕ±Ð¥¸ÉÍÕ±ÑÌè(±¥¹¬ôÉÍÕ±Ð¹Ð 1¥¹¬°¤(Í¡½Õ±}á±Õô±Í((½Èá±Õ¥¸á±Õ}ÕÉ±Ìè(¥á±Õ¹ÍÑÉ¥À ¤¹á±Õ¹ÍÑÉ¥À ¤¥¸±¥¹¬è(Í¡½Õ±}á±ÕôQÉÕ(É¬((¥¹½ÐÍ¡½Õ±}á±Õè(¥±ÑÉ¹ÁÁ¹¡ÉÍÕ±Ð¤((ÉÑÕÉ¸¥±ÑÉ*
def export_to_excel(df):
    """Export dataframe to Excel bytes."""
    output = BytesIO()

    # Use pandas to write to Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Video Finder Results')

        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Video Finder Results']

        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass

            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)
    return output


def run_video_finder():
    """Main video finder function."""
    st.header("Video Finder - OSINT Investigation")
    st.write("Search for videos featuring a target individual across multiple platforms.")

    # Initialize session state
    initialize_session_state()

    # UI Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        target_name = st.text_input(
            "Target Name",
            placeholder="Enter the target individual's name",
            key="target_name_input"
        )

    st.divider()

    # Aliases section
    aliases = render_dynamic_list("Aliases", "aliases", placeholder="Alternative names/spellings")

    st.divider()

    # Social Media Handles
    handles = render_dynamic_list(
        "Social Media Handles",
        "handles",
        placeholder="@username format"
    )

    st.divider()

    # Excluded Accounts
    excluded_accounts = render_dynamic_list(
        "Target's Own Accounts to Exclude",
        "excluded_accounts",
        placeholder="Channel/profile URL to filter OUT"
    )

    st.divider()

    # Optional Keywords
    keywords = st.text_input(
        "Optional Keywords",
        placeholder="e.g., conference, interview, speech (optional)"
    )

    st.divider()

    # Platform selection
    st.write("**Select Platforms to Search**")
    platform_cols = st.columns(3)

    platforms_options = [
        'YouTube', 'Vimeo', 'Rumble', 'Dailymotion', 'Archive.org',
        'Twitter/X', 'Instagram', 'TikTok', 'Facebook'
    ]

    selected_platforms = []
    for idx, platform in enumerate(platforms_options):
        col_idx = idx % 3
        with platform_cols[col_idx]:
            if st.checkbox(platform, value=True, key=f"platform_{platform}"):
                selected_platforms.append(platform)

    st.divider()

    # Search button
    search_button = st.button("ð Search Videos", type="primary", use_container_width=True)

    if search_button:
        # Validation
        if not target_name.strip():
            st.error("Please enter a target name.")
            return

        # Check yt-dlp installation
        if not check_yt_dlp_installed():
            st.error(
                "yt-dlp is not installed. Please install it with: `pip install yt-dlp`"
            )
            return

        # Create progress bar and status areas
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        results_placeholder = st.empty()

        all_results = []

        try:
            # Phase 1: YouTube search
            status_placeholder.info("Phase 1/4: Searching YouTube...")
            youtube_results = search_youtube(
                target_name,
                aliases,
                handles,
                excluded_accounts,
                progress_bar
            )
            all_results.extend(youtube_results)
            st.write(f"Found {len(youtube_results)} YouTube videos")

            # Phase 2: Google scraping for video platforms
            status_placeholder.info("Phase 2/4: Searching video platforms (Vimeo, Rumble, etc.)...")
            video_platform_results = search_google_videos(
                target_name,
                aliases,
                handles,
                selected_platforms,
                progress_bar,
                25
            )
            all_results.extend(video_platform_results)
            st.write(f"Found {len(video_platform_results)} videos on other platforms")

            # Phase 3: Social media tagged content
            status_placeholder.info("Phase 3/4: Searching social media tagged content...")
            social_results = search_social_tagged_content(
                target_name,
                handles,
                progress_bar,
                50
            )
            all_results.extend(social_results)
            st.write(f"Found {len(social_results)} social media videos")

            # Phase 4: Deduplication and filtering
            status_placeholder.info("Phase 4/4: Processing and deduplicating results...")
            progress_bar.progress(90)

            all_results = deduplicate_results(all_results)
            st.write(f"After deduplication: {len(all_results)} unique videos")

            all_results = apply_exclude_filter(all_results, excluded_accounts)
            st.write(f"After filtering excluded accounts: {len(all_results)} videos")

            progress_bar.progress(100)
            status_placeholder.success(f"Search complete! Found {len(all_results)} videos.")

            # Display results
            if all_results:
                df = pd.DataFrame(all_results)

                # Remove Channel URL column from display (internal use only)
                display_df = df[['Link', 'Source Platform', 'Date Published',
                                 'Video Title', 'Description', 'Uploader/Channel Name',
                                 'Tagged Handles Found']]

                st.subheader("Search Results")
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # Export button
                excel_bytes = export_to_excel(display_df)
                st.download_button(
                    label="ð¥ Download as Excel (.xlsx)",
                    data=excel_bytes,
                    file_name="video_finder_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Statistics
                st.subheader("Search Statistics")
                stats_col1, stats_col2, stats_col3 = st.columns(3)

                with stats_col1:
                    st.metric("Total Videos Found", len(all_results))

                with stats_col2:
                    platform_counts = display_df['Source Platform'].value_counts()
                    st.metric("Platforms with Results", len(platform_counts))

                with stats_col3:
                    st.metric("With Known Upload Dates",
                             len(display_df[display_df['Date Published'] != 'Unknown']))

            else:
                st.warning("No videos found matching your search criteria.")

        except Exception as e:
            status_placeholder.error(f"An error occurred during search: {str(e)}")
            st.exception(e)


render = run_video_finder

if __name__ == "__main__":
    run_video_finder()
