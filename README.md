# 像素城市封面

自行繪製、無外部圖片或字型依賴的像素台北。固定標題「PAI任務管理」及2026，含台北101、北門與台北車站意象。

- [Notion嵌入版](https://lupinart.github.io/notion-pixel-city/embed.html)：依台灣時間自動切換，開啟Notion的「嵌入」區塊並貼上此網址。建議寬高比2.5:1，例如1000×400；其餘空間透明，畫面完整顯示。
- [三種場景預覽](https://lupinart.github.io/notion-pixel-city/)。
- [Notion封面專用SVG（6:1）](https://lupinart.github.io/notion-pixel-city/cover.svg)：3600×600，左右延伸天空與樓群，保留中央標題、2026與101的安全空間。封面「變更」換成此網址，再以「調整位置」微調。依GitHub排程重新產生，不能保證Notion封面準點更新。
- [原比例SVG（2.5:1）](https://lupinart.github.io/notion-pixel-city/today.svg)：適合一般圖片區塊，較高的構圖不適合寬幅封面。
- [原始碼](https://github.com/lupinart/notion-pixel-city)。

台北版本：一般樓群下移，日期與年份下方保留至少24px空隙；右側101拉高至390px，以左右留白避開日期。加入北門與台北車站的像素意象。此為地標拼接構圖，非真實視點的城市全景。

index.html比較三種配色；embed.html為純城市嵌入頁。day.svg、dusk.svg、night.svg保持各自配色；today.svg及cover.svg依產生當下的台灣時間選場景。

## 重新產生

Python 3.9+，標準函式庫。正式來源留在 iCloud；執行與測試請依 AGENTS.md 複製至 `/private/tmp/codex-builds/`。

```sh
python3 -B city.py --at 2026-11-10T18:00:00+08:00
python3 -B test_city.py
```

不加 `--at` 使用現在時間；未帶時區的日期視為 Asia/Taipei。`--out` 指定輸出資料夾。時間分段：06–17白天、17–19黃昏、其餘夜晚；這是固定視覺時段，不是天文日出計算。窗燈按日期固定產生。

SVG 自帶動畫與減少動態效果規則，沒有 JavaScript。「PAI任務管理」及2026均使用使用者指定的[精品點陣體9×9標準體1.93](https://github.com/scott0107000/BoutiqueBitmap9x9/releases/tag/1.93)，取自正式壓縮包的BoutiqueBitmap9x9_1.93.ttf，不使用港版或粗體。以原生10px/em單色繪製、逐字檢查不是缺字方框，保留原字形，不再自行加粗。標題9列、每格放大10px；年份7列、每格5px。固定格點與原始字型SHA256在heading_bitmap.py，輸出為SVG方塊路徑，不含文字節點與字型檔，產生時不需Pillow或網路。字型來源授權全文保存在FONT-LICENSE.txt。雲與飛機全程位於標題上方，避免筆畫與雲連在一起。標題及2026固定，不隨時間變動。底色是完整天空插畫，無外圍白邊。

## 自動切換與排程

嵌入頁每15秒依裝置時間與固定Asia/Taipei時區檢查場景：06:00–17:00白天、17:00–19:00黃昏，其餘夜景。離開再回來也會重新檢查；不跟隨Notion明暗模式，因天色代表台灣時刻。關閉JavaScript時仍顯示最近部署的today.svg，但不會即時切換。圖片預載成功才換圖，下載失敗或超過12秒會保留原畫面並重試。

GitHub Actions於台灣時間06:00、17:00、19:00及00:07重新產生圖片並部署Pages，不修改原始碼分支。每日窗燈依日期產生；排程更新可能延遲，公開repo無活動60天後排程也可能停用（[GitHub官方說明](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)）。即使排程停用，網頁仍可在已發布的三份場景間依時間切換，只是窗燈不再每日更新。

單張SVG載入後不會自行改天色，Notion也可能快取圖片；需要可靠的持續切換請用embed.html嵌入頁。尚未實測Notion桌面App的封面SVG／動畫支援；不操作個人Notion畫面。

## 檢查

在隔離測試副本執行 `python3 -B test_city.py`、`node test-scene.mjs`。瀏覽器測試需既有Playwright與獨立Chromium，透過PLAYWRIGHT_MODULE、CHROMIUM_PATH設定；`test-live.mjs`驗證嵌入頁的跨時段、跨日、非台灣裝置時區、網路逾時與窄畫面，SITE_BASE_URL可指定正式網址。test-preview.mjs檢查SVG圖形、留白、減少動態、明暗及縮放。

## 來源

概念參考使用者提供的像素城市動態封面：
https://swg.notion.pet/s/bg-ef992f4f6af27c1b00408cbf10f741cb

本作品重新設計城市輪廓、構圖、配色、雲與飛機、數字點陣及動畫，不使用對方的 SVG 路徑或後端。
