from st_aggrid import AgGrid
import pandas as pd
import streamlit as st
import MeCab
mecab = MeCab.Tagger()
import matplotlib.pyplot as plt
from wordcloud import WordCloud
font_path = 'ShipporiMinchoB1-ExtraBold.ttf'
import altair as alt
#import datetime
from datetime import datetime, timedelta, timezone
import numpy as np
import plotly.express as px
from PIL import Image

st.set_page_config(layout="wide")
st.title(':thinking_face: 議事録見える化@東京都中央区')
st.markdown('　**議事録見える化@東京都中央区**は、あなたが関心のあるキーワードについて「議会でどんな議論がされてるのかな？」「どの議員さんが関心持っているのかな」をざっくり可視化するサービスです。')
st.markdown('　対象は東京都中央区議会、期間は2015年5月から2022年5月まで。')
image = Image.open('jigazo.png')

#議事録キャッシュ
@st.cache_data
def load_csv(file_path, encoding="utf-8"):
    return pd.read_csv(file_path, encoding=encoding)

# データフィルタリング
@st.cache_data
def filter_logs(logs, keyword, start_year, end_year):
    return logs[
        (logs['内容'].str.contains(keyword)) &
        (logs['年度'] >= start_year) &
        (logs['年度'] <= end_year)
    ]

logs = pd.read_csv('./gijiroku2015-2022.5.csv', encoding='UTF-8')#dataframeとしてcsvを読み込み
logs["回数"] = 1
moji = logs[["年度","文字数","回数"]]
moji = moji.groupby('年度', as_index=False).sum()
st.header(':fork_and_knife: 検索条件')
logs2 = logs[["年月日","人分類","内容分類","質問","回答","会議","内容","年度","文字数","回数"]]

# 議員の名前をURLに持ってたらその人のWCを表示させ、なければランダム表示させる
query_params = st.experimental_get_query_params() # URLにあるクエリをqueary_paramsとして読み込む
if query_params: 
    option_selected_l = query_params.get('words', None)[0]
else:option_selected_l = st.text_input('あなたが調べてみたいキーワードを入力してね。初期値は「待機児童」になってます。',"待機児童")

#st.markdown(' ##### :date:「年度」での絞り込み')
with st.expander("■「年度」での絞り込み", False):
#年度選択
    start_year, end_year = st.select_slider(
    '最近の動向を知りたいとか過去はどうなってたかとか、年度で結果を絞りたい場合は使ってみてください。初期値では2019年から2021年が選択されてます。',
     options=['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022'],
     value=('2019', '2022'))
start_year = int(start_year)
end_year = int(end_year)

#文字列の抽出
selected_l = logs2[(logs2['内容'].str.contains(option_selected_l)) & (logs2['年度'] >= start_year) & (logs2['年度'] <= end_year)]
giins = logs[["人分類","年度"]]
giins = giins.drop_duplicates()
giins = giins[giins['人分類'] != "0"]
giins = giins[giins['人分類'] != "-"]
giins_year = giins[(giins['年度'] >= start_year) & (giins['年度'] <= end_year)]
giins = giins_year[["人分類"]]
giins = giins.drop_duplicates()
selected_l_moji = selected_l[["年度","年月日","人分類","内容分類","質問","回答","内容","文字数","回数"]]
selected_l_moji_g = selected_l[["年月日","人分類","内容分類","質問","回答","内容","文字数","回数"]]

st.header(':doughnut: どんな議論がされてるのかな？')
st.markdown('キーワードが含まれる発言を解析して、ざっくり1枚の画像にしてます。だいたい、どんな議論がされているのかを掴めます。')
# ワードクラウド作成
logs_contents = selected_l['内容']
f = open('temp.txt', 'w')#textに書き込み
f.writelines(logs_contents)
f.close()

text = open("temp.txt", encoding="utf8").read()

results = mecab.parse(text)
result = results.split('\n')[:-2][0]

nouns = []
for result in results.split('\n')[:-2]:
        if '名詞' in result.split('\t')[4]:
            nouns.append(result.split('\t')[0])
words = ' '.join(nouns)

#st.markdown('　#### :face_with_monocle: 文字解析の結果')
JST = timezone(timedelta(hours=+9), 'JST')
#dt_now = datetime.datetime.now()
dt_now = datetime.now(JST)

st.write('**[検索キーワード]**',option_selected_l, '**[対象年度]**',start_year,'-',end_year,'**[作成日時]**',dt_now)

stpwds = ["面","令和","様","辺","なし","分","款","皆","さん","議会","文","場所","現在","ら","方々","こちら","性","化","場合","対象","一方","皆様","考え","それぞれ","意味","とも","内容","とおり","目","事業","つ","見解","検討","本当","議論","民","地域","万","確認","実際","先ほど","前","後","利用","説明","次","あたり","部分","状況","わけ","話","答弁","資料","半ば","とき","支援","形","今回","中","対応","必要","今後","質問","取り組み","終了","暫時","午前","たち","九十","八十","七十","六十","五十","四十","三十","問題","提出","進行","付託","議案","動議","以上","程度","異議","開会","午後","者","賛成","投票","再開","休憩","質疑","ただいま","議事","号","二十","平成","等","会","日","月","年","年度","委員","中央","点","区","委員会","賛成者","今","中央区","もの","こと","ふう","ところ","ほう","これ","私","わたし","僕","あなた","みんな","ただ","ほか","それ", "もの", "これ", "ところ","ため","うち","ここ","そう","どこ", "つもり", "いつ","あと","もん","はず","こと","そこ","あれ","なに","傍点","まま","事","人","方","何","時","一","二","三","四","五","六","七","八","九","十"]

wc = WordCloud(stopwords=stpwds, width=900, height=900, background_color='white', colormap='Dark2', font_path = font_path)
wc.generate(words)
wc.to_file('wc.png')
st.image('wc.png')
st.markdown('補足：更新するたびに表示位置などはビミョーに変わります。対象は名詞だけで、「それぞれ」や「問題」など、頻繁に使われるけど中身のないキーワードは除外してます。')

st.header(':cookie: トレンドはどうなってる？')
st.markdown('キーワードが出てきた回数の推移を年度単位で見てみたもの。なんとなくそのキーワードのトレンドが分かります。')

#st.markdown('カテゴリとしては以下の3つに分かれています「質問」「回答」キーワードが含まれる発言内容の文字列をカウントして、ランキング化したものです。')
logs_contents_temp_moji1 = selected_l_moji.groupby(['人分類','内容分類','年度'], as_index=False).sum()# 年度ごとの文字数
logs_contents_temp_moji2 = selected_l_moji_g.groupby(['人分類','内容分類'], as_index=False).sum()# 年度ごとの文字数
logs_contents_temp_moji1 = logs_contents_temp_moji1[logs_contents_temp_moji1['内容分類'] !='議長/委員長']
logs_chart = pd.merge(giins_year, logs_contents_temp_moji1, how="left", on =['人分類', '年度'])
logs_chart = logs_chart.groupby('年度', as_index=False).sum()
logs_chart = logs_chart[["年度","文字数","回数"]]
logs_chart = pd.merge(logs_chart, moji, how="left", on =['年度'])
logs_chart["スコア"] = round(logs_chart["回数_x"]/logs_chart["回数_y"]*1000,2)
#st.area_chart(logs_chart)
#st.line_chart(logs_chart)
#st.plotly_chart(logs_chart, use_container_width=True)
#logs_chart = logs_chart.fillna({'内容分類': '回答', '文字数': 0})
#logs_chart
#st.bar_chart(logs_chart, x="年度", y="文字数", use_container_width=True)
fig2 = px.line(logs_chart, x='年度', y='スコア',height=900, width=900, text='スコア')
fig2.update_yaxes(automargin=True)
fig2.update_xaxes(automargin=True,
                tickvals=[2014,2015,2016,2017,2018,2019,2020,2021,2022],
                )

fig2.update_layout(
    xaxis_title="",
    #yaxis_title="",
    font=dict(
        size=14
    )
)

fig2.update_traces(
#    width=0.8,
#    marker_line_width=0,
    textfont_size=20,
    textposition="top right",
    line = dict(
        width = 4,
        color = '#00b894'
    ),
    marker = dict(
        size = 14
    )
#    textangle=45, 
#    cliponaxis=False
    )
fig2
st.markdown('※ 年度内でのすべての議事録での発言のうち、そのキーワードが含まれた発言の割合をスコア化したものです（単純に数だけ拾うとブレるので）。')

st.header(':coffee: どの議員さんが関心持ってるのかな？')
st.markdown('キーワードが含まれる発言文字数をカウントして、ランキング化したもの。どの議員がそのキーワードに熱心なのかを測るのに使えます。')

logs_graph = pd.merge(giins, logs_contents_temp_moji2, how="left", on = "人分類")
logs_graph = logs_graph.fillna({'内容分類': '回答', '文字数': 0})

fig = px.bar(logs_graph, x='文字数', y='人分類', color='内容分類', color_discrete_map={'回答': '#ff7979', '質問': '#74b9ff'}, text='文字数',height=900, width=900, orientation='h')
#fig.update_layout(barmode='stack', xaxis={'文字数':'category ascending'})
fig.update_yaxes(automargin=True)
fig.update_xaxes(automargin=True)
fig.update_layout(
    barmode='stack', 
    yaxis={'categoryorder':'total ascending'},
    #legend=dict(xanchor='right',
    #                    yanchor='bottom',
    #                    x=0.95,
    #                    y=0.05,
    #                    bgcolor="white",
    #                    bordercolor="white",
    #                    borderwidth=2),
    font=dict(
        #family="Courier New, monospace",
        size=14,
    )
    )

fig.update_layout(
    #xaxis_title="",
    yaxis_title="",
    font=dict(
        size=14
    )
)


fig.update_traces(
    width=1,
    marker_line_width=0,
    textfont_size=20, 
    textangle=0, 
    #textposition="outside", 
    cliponaxis=False
    )
fig
st.markdown('※ 「質問」：議員による質問内容、「回答」：議員の質問に対する区長などの回答')

st.header(':cake: 結果の詳細')
st.markdown('解析の対象になった発言の詳細を見たいときはこちらをご覧ください。')
grid_options = {
    "columnDefs":[
    {
        "headerName":"年月日",
        "field":"年月日",
        "suppressSizeToFit":True,
        "autoHeight":True,

    },
    {
        "headerName":"会議名",
        "field":"会議",
        "suppressSizeToFit":True,
        "wrapText":True,
        "autoHeight":True,
        "maxWidth":150,
    },
    {
        "headerName":"内容分類",
        "field":"内容分類",
        "suppressSizeToFit":True,
        "autoHeight":True,

    },
    {
        "headerName":"質問者",
        "field":"質問",
        "suppressSizeToFit":True,
        "wrapText":True,
        "maxWidth":100,
        "autoHeight":True,

    },
    {
        "headerName":"回答者",
        "field":"回答",
        "suppressSizeToFit":True,
        "wrapText":True,
        "maxWidth":100,
        "autoHeight":True,

    },
    {
        "headerName":"発言内容",
        "field":"内容",
        "wrapText":True,
        "autoHeight":True,
        "suppressSizeToFit":True,
        "maxWidth":500,
    },
    {
        "headerName":"人分類",
        "field":"人分類",
        "suppressSizeToFit":True,
        "wrapText":True,
        "autoHeight":True,
    },
    ],
}

AgGrid(selected_l, grid_options)


st.image(image,width=100)
st.markdown('**作った人：[ほづみゆうき](https://twitter.com/ninofku)**')

st.header(':paperclip: 情報参照元')
st.markdown('分析の元になっているデータは、[中央区議会 Webサイト](https://www.kugikai.city.chuo.lg.jp/index.html)の「会議録検索」からHTMLファイルをごっそりダウンロードして、その上であれこれ苦心して加工して作成しました。注意して作業はしたつもりですが、一部のデータが欠損等している可能性もありますのでご承知おきください。もし不備等ありましたら[ほづみゆうき](https://twitter.com/ninofku)まで声掛けいただけるとありがたいです。')
