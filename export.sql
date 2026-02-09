WITH t1 AS (
  SELECT
    sku_id AS skuid,
    MAX(category_name) AS categoryname,
    MAX(sub_category) AS subcategory,
    MAX(product_url) AS producturl,
    MAX(std_brand_name) AS stdbrandname,
    MAX(LOWER(sku_title)) AS skutitle,
    MAX(LOWER(product_title_cn)) AS producttitlecn,
    ROUND(SUM(discount_sales), 0) AS gmv
  FROM
    $({"dynamicType":"COLLECTION","name":"灯光类","collectionId":"8FAP7DYZFT"})
  GROUP BY 1
),

matched AS (
  SELECT
    c.producturl,
    c.skuid,
    c.skutitle,
    c.producttitlecn,
    c.stdbrandname,
    c.categoryname,
    c.subcategory,
    c.gmv,
    k.keyword,
    k.category,
    NULLIF(POSITION(k.keyword IN c.skutitle), 0) AS pos
  FROM
    t1 c
    LEFT JOIN (
      /* =========================
         关键词表（保持你现有的“高精度词”策略）
         ========================= */

      /* ===== 英文：闪光灯 ===== */
      SELECT 'speedlite'   AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'speedlight'  AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'strobe'      AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'ttl'         AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'hss'         AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'flash'       AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'ring flash'  AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'clip-on strobe' AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'clip on strobe' AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'clip-on flash'  AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'clip on flash'  AS keyword, '闪光灯' AS category UNION ALL

      /* ===== 英文：环形灯 ===== */
      SELECT 'ring light'  AS keyword, '环形灯' AS category UNION ALL
      SELECT 'luce ad anello' AS keyword, '环形灯' AS category UNION ALL

      /* ===== 英文：平板灯 ===== */
      SELECT 'panel'       AS keyword, '平板灯' AS category UNION ALL
      SELECT 'flapjack'    AS keyword, '平板灯' AS category UNION ALL
      SELECT 'softbox'     AS keyword, '平板灯' AS category UNION ALL

      /* ===== 英文：摄影手电 ===== */
      SELECT 'flashlight'  AS keyword, '摄影手电' AS category UNION ALL
      SELECT 'torch'       AS keyword, '摄影手电' AS category UNION ALL

      /* ===== 英文：棒灯 ===== */
      SELECT 'wand'        AS keyword, '棒灯' AS category UNION ALL
      SELECT 'tube light'  AS keyword, '棒灯' AS category UNION ALL

      /* ===== 英文：口袋灯 ===== */
      SELECT 'cold shoe'   AS keyword, '口袋灯' AS category UNION ALL
      SELECT ' pocket light' AS keyword, '口袋灯' AS category UNION ALL
      SELECT ' cube'       AS keyword, '口袋灯' AS category UNION ALL
      SELECT 'video light' AS keyword, '口袋灯' AS category UNION ALL
      SELECT 'mini video light' AS keyword, '口袋灯' AS category UNION ALL

      /* ===== 英文：充气灯 ===== */
      SELECT 'inflatable'  AS keyword, '充气灯' AS category UNION ALL

      /* ===== 英文：COB ===== */
      SELECT 'cob'         AS keyword, 'COB补光灯' AS category UNION ALL
      SELECT 'bowens'      AS keyword, 'COB补光灯' AS category UNION ALL
      SELECT 'bowens mount' AS keyword, 'COB补光灯' AS category UNION ALL

      /* ===== 日语：闪光灯（保留高精度词） ===== */
      SELECT 'フラッシュ'           AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'ストロボ'             AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'スピードライト'       AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'カメラフラッシュ'     AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'ワイヤレスフラッシュ' AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'スレーブ'             AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'pc同期'               AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'シンクロ'             AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'クリップオンストロボ' AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'クリップオンフラッシュ' AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'リングフラッシュ'     AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'mr-14ex2'             AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'mr-14ex'              AS keyword, '闪光灯' AS category UNION ALL
      SELECT 'yn-14ex'              AS keyword, '闪光灯' AS category UNION ALL

      /* ===== 日语：环形灯 ===== */
      SELECT 'リングライト'         AS keyword, '环形灯' AS category UNION ALL
      SELECT 'リング ライト'        AS keyword, '环形灯' AS category UNION ALL
      SELECT '女優ライト'           AS keyword, '环形灯' AS category UNION ALL
      SELECT 'ledリング'            AS keyword, '环形灯' AS category UNION ALL
      SELECT 'リング型ライト'       AS keyword, '环形灯' AS category UNION ALL
      SELECT 'リング照明'           AS keyword, '环形灯' AS category UNION ALL
      SELECT 'リングフィルライト'   AS keyword, '环形灯' AS category UNION ALL
      SELECT 'リングライブ'         AS keyword, '环形灯' AS category UNION ALL

      /* ===== 日语：平板灯/影棚灯/套装 ===== */
      SELECT 'パネルライト'       AS keyword, '平板灯' AS category UNION ALL
      SELECT 'ライトパネル'       AS keyword, '平板灯' AS category UNION ALL
      SELECT 'ledパネル'          AS keyword, '平板灯' AS category UNION ALL
      SELECT 'ソフトボックス'     AS keyword, '平板灯' AS category UNION ALL
      SELECT '照明キット'         AS keyword, '平板灯' AS category UNION ALL
      SELECT 'ライトキット'       AS keyword, '平板灯' AS category UNION ALL
      SELECT 'ライトセット'       AS keyword, '平板灯' AS category UNION ALL
      SELECT 'スタジオ照明'       AS keyword, '平板灯' AS category UNION ALL
      SELECT 'スタジオライト'     AS keyword, '平板灯' AS category UNION ALL

      /* ===== 日语：摄影手电 ===== */
      SELECT '懐中電灯'           AS keyword, '摄影手电' AS category UNION ALL
      SELECT 'フラッシュライト'   AS keyword, '摄影手电' AS category UNION ALL
      SELECT 'トーチ'             AS keyword, '摄影手电' AS category UNION ALL
      SELECT 'ハンドライト'       AS keyword, '摄影手电' AS category UNION ALL
      SELECT 'ハンディライト'     AS keyword, '摄影手电' AS category UNION ALL
      SELECT 'ペンライト'         AS keyword, '摄影手电' AS category UNION ALL

      /* ===== 日语：棒灯 ===== */
      SELECT 'チューブライト'     AS keyword, '棒灯' AS category UNION ALL
      SELECT 'ライトチューブ'     AS keyword, '棒灯' AS category UNION ALL
      SELECT 'ライト チューブ'    AS keyword, '棒灯' AS category UNION ALL
      SELECT 'ライトスティック'   AS keyword, '棒灯' AS category UNION ALL
      SELECT 'スティックライト'   AS keyword, '棒灯' AS category UNION ALL
      SELECT 'ライトワンド'       AS keyword, '棒灯' AS category UNION ALL
      SELECT '照明棒'             AS keyword, '棒灯' AS category UNION ALL
      SELECT '照明スティック'     AS keyword, '棒灯' AS category UNION ALL

      /* ===== 日语：口袋灯（小型机顶视频灯） ===== */
      SELECT 'ポケットライト'           AS keyword, '口袋灯' AS category UNION ALL
      SELECT 'ポケットビデオライト'     AS keyword, '口袋灯' AS category UNION ALL
      SELECT 'ミニビデオライト'         AS keyword, '口袋灯' AS category UNION ALL
      SELECT '小型ビデオライト'         AS keyword, '口袋灯' AS category UNION ALL
      SELECT 'コンパクトビデオライト'   AS keyword, '口袋灯' AS category UNION ALL
      SELECT 'キューブライト'           AS keyword, '口袋灯' AS category UNION ALL
      SELECT 'キューブ'                 AS keyword, '口袋灯' AS category UNION ALL
      SELECT 'コールドシュー'           AS keyword, '口袋灯' AS category UNION ALL

      /* ===== 日语：充气灯 ===== */
      SELECT 'インフレータブル' AS keyword, '充气灯' AS category UNION ALL
      SELECT 'エアライト'       AS keyword, '充气灯' AS category UNION ALL
      SELECT 'バルーン'         AS keyword, '充气灯' AS category UNION ALL

      /* ===== 日语：COB ===== */
      SELECT 'ボーエンズ'         AS keyword, 'COB补光灯' AS category UNION ALL
      SELECT 'ボーエンズマウント' AS keyword, 'COB补光灯' AS category UNION ALL
      SELECT 'bowensマウント'     AS keyword, 'COB补光灯' AS category UNION ALL
      SELECT 'コブ'               AS keyword, 'COB补光灯' AS category
    ) k
      ON c.skutitle LIKE '%' || k.keyword || '%'
),

ranked AS (
  SELECT
    producturl,
    skuid,
    skutitle,
    producttitlecn,
    stdbrandname,
    categoryname,
    subcategory,
    gmv,
    keyword,
    category,
    pos,
    ROW_NUMBER() OVER (
      PARTITION BY skuid
      ORDER BY (pos IS NULL), CAST(pos AS INT) ASC, LENGTH(keyword) DESC
    ) AS rn
  FROM matched
),

final_calc AS (
  SELECT
    skuid,
    producturl,
    stdbrandname,
    categoryname,
    subcategory,
    skutitle,
    producttitlecn,
    CAST(gmv AS INT) AS gmv,

    CASE
      /* ========= 1) 宏环闪（ring flash / macro ring）→ 闪光灯 ========= */
      WHEN
        REGEXP_LIKE(skutitle, '(mr-?14ex2?|yn-?14ex|ring flash|リングフラッシュ)')
        OR (
          REGEXP_LIKE(skutitle, '(macro ring|マクロリング)')
          AND REGEXP_LIKE(skutitle, '(ttl|hss|ストロボ|フラッシュ|speedlite|\\bex\\b|ex[0-9]|ws)')
        )
      THEN '闪光灯'

      /* ========= 2) クリップオンストロボ/フラッシュ → 闪光灯 ========= */
      WHEN REGEXP_LIKE(skutitle, '(クリップオンストロボ|クリップオンフラッシュ|clip[- ]on (strobe|flash))')
      THEN '闪光灯'

      /* ========= 3) 闪光灯系统强信号（防止 AD300Pro 被 watt/COB 抢走） ========= */
      WHEN
        REGEXP_LIKE(skutitle, '(フラッシュ|ストロボ|flash|strobe|speedlite|スピードライト|フラッシング)')
        AND REGEXP_LIKE(skutitle, '(ttl|hss|ws|2\\.4g|1/8000|リサイクル|発光)')
      THEN '闪光灯'

      /* ========= 4) 环形灯（放在 COB/watt 前，避免 55w ring light 被判 COB） ========= */
      WHEN
        REGEXP_LIKE(skutitle, '(?i)(ring light|luce ad anello)')
        OR REGEXP_LIKE(skutitle, '(リングライト|リング ライト|女優ライト|ledリング|リング型ライト|リング照明|リングフィルライト|リングライブ)')
      THEN '环形灯'

      /* ========= 5) COB 强特征（排除闪光灯/环形灯语义） ========= */
      WHEN
        (
          REGEXP_LIKE(skutitle, '(\\bcob\\b|bowens|bowensマウント|ボーエンズ|ボーエンズマウント|コブ)')
          OR REGEXP_LIKE(
               skutitle,
               '(?i)(amaran\\s*(100d|100x|200x|200xs|60x)|aputure\\s*(120d|300d|storm\\s*80c)|nanlite\\s*(fs|forza)|neewer\\s*fs[0-9]{2,3}|godox\\s*(ml[0-9]{2,3}|sl[0-9]{2,3}))'
             )
          OR (
            REGEXP_LIKE(skutitle, '([0-9]+)[ ]*(?:w|ｗ|ワット|watt)(?:[^0-9a-zA-Z]|$)')
            AND CAST(REGEXP_EXTRACT(skutitle, '([0-9]+)[ ]*(?:w|ｗ|ワット|watt)(?:[^0-9a-zA-Z]|$)', 1) AS INTEGER) >= 80
            AND REGEXP_LIKE(skutitle, '(定常|定常光|撮影|ビデオ|フィル|色温度|lux|cri|tlci|モデリング)')
          )
        )
        AND NOT REGEXP_LIKE(skutitle, '(フラッシュ|ストロボ|flash|strobe|speedlite|スピードライト|\\bad[0-9]{3}\\b|ws)')
        AND NOT REGEXP_LIKE(skutitle, '(リングライト|ring light|luce ad anello|女優ライト)')
      THEN 'COB补光灯'

      /* ========= 6) 口袋灯：视频灯 + 小型/薄型/USB/电池等 ========= */
      WHEN
        REGEXP_LIKE(skutitle, '(ビデオライト|撮影用ライト|撮影ライト|ledビデオライト|フィルライト|video light)')
        AND REGEXP_LIKE(skutitle, '(小型|ミニ|超薄型|薄型|コンパクト|軽量|手持ち|携帯|ポケット|usb|充電|充電式|[0-9]+mah|49led|ホットシュー|コールドシュー|オンカメラ|カメラトップ|on-camera|ulanzi\\s*vl|vijim\\s*vl)')
        AND NOT REGEXP_LIKE(skutitle, '(ストロボ|フラッシュ|スピードライト|\\bad[0-9]{3}\\b|ws|ボーエンズ|cob|コブ)')
      THEN '口袋灯'

      /* ========= 7) 脚架（自拍杆/自撮り棒） ========= */
      WHEN REGEXP_LIKE(skutitle, '(selfie stick|自撮り棒|セルカ棒|セルフィースティック)')
      THEN '脚架'

      /* ========= 8) 关键词命中（来自 k） ========= */
      WHEN rn = 1 AND pos IS NOT NULL THEN category

      ELSE '灯光类-其他'
    END AS stdcategory3t
  FROM ranked
  WHERE rn = 1
),

/* ========= 只优化 rescue layer：final_fix ========= */
final_fix AS (
  SELECT
    skuid,
    producturl,
    stdbrandname,
    categoryname,
    subcategory,
    skutitle,
    producttitlecn,
    gmv,

    CASE
      /* ------------------------------------------------------------
         0) 指定“灯光附件/光学配件”保持在 其他（避免被 W/品牌误拉到 COB）
         ------------------------------------------------------------ */
      WHEN stdcategory3t = '灯光类-其他'
       AND REGEXP_LIKE(
             skutitle,
             '(?i)(ソフトボックス|softbox|ディフューザー|diffuser|リフレクター|reflector|グリッド|grid|ハニカム|honeycomb|バーンドア|barndoor|ゴボ|gobo|フレネル|fresnel|スポットライト|spotlight)'
           )
      THEN '灯光类-其他'

      /* ------------------------------------------------------------
         1) 闪光灯强覆盖：修复 “AD300Pro/ストロボ + 300w” 被误判 COB
         ------------------------------------------------------------ */
      WHEN REGEXP_LIKE(skutitle, '(?i)(ストロボ|フラッシュ|スピードライト|speedlite|speedlight)')
       AND REGEXP_LIKE(skutitle, '(?i)(ttl|hss|ws|1/8000|2\\.4g|sync|シンクロ|pc同期|リサイクル|発光)')
      THEN '闪光灯'

      WHEN REGEXP_LIKE(
             skutitle,
             '(?i)\\b(ad[0-9]{3}pro?|tt[0-9]{3,4}|v[0-9]{3,4}|v1pro|v1\\b|xpro|x2t|x1t|x3)\\b'
           )
       AND REGEXP_LIKE(skutitle, '(?i)(ストロボ|フラッシュ|ttl|hss|ws|1/8000|2\\.4g|sync|シンクロ|pc同期)')
      THEN '闪光灯'

      WHEN REGEXP_LIKE(skutitle, '(?i)(クリップオンストロボ|クリップオンフラッシュ|clip[- ]on (strobe|flash))')
      THEN '闪光灯'

      WHEN REGEXP_LIKE(skutitle, '(?i)(mr-?14ex2?|yn-?14ex|ring flash|リングフラッシュ)')
      THEN '闪光灯'

      /* ------------------------------------------------------------
         2) 手机便携补光灯（磁吸/粘着等强形态信号：允许覆盖“自撮りリングライト”这类命名）
         ------------------------------------------------------------ */
      WHEN REGEXP_LIKE(skutitle, '(?i)(magsafe|マグセーフ|磁気|マグネット|粘着|ミラー付き|折りたたみ)')
       AND REGEXP_LIKE(skutitle, '(?i)(ライト|led|フィルライト|補助光|補光)')
       AND NOT REGEXP_LIKE(skutitle, '(?i)(クリップオンストロボ|クリップオンフラッシュ)')
      THEN '手机便携补光灯'

      /* ------------------------------------------------------------
         3) 环形灯覆盖：修复 “リングライト + 55w” 被 COB 抢走
            - 注意：ring flash / マクロリング + ttl/hss 等已在上方归闪光灯
         ------------------------------------------------------------ */
      WHEN REGEXP_LIKE(skutitle, '(?i)(ring light|luce ad anello)')
      THEN '环形灯'

      WHEN REGEXP_LIKE(
             skutitle,
             '(リングライト|女優ライト|サークルライト|リング照明|リングフィルライト|リングライブ|円形ライト|丸型ライト|ラウンドライト)'
           )
       AND NOT REGEXP_LIKE(skutitle, '(?i)(ring flash|リングフラッシュ|ストロボ|フラッシュ)')
      THEN '环形灯'

      /* ------------------------------------------------------------
         4) 充气灯
         ------------------------------------------------------------ */
      WHEN REGEXP_LIKE(skutitle, '(?i)(インフレータブル|エアライト|バルーン|inflatable)')
      THEN '充气灯'

      /* ------------------------------------------------------------
         5) 摄影手电（含水中/ダイビング）
         ------------------------------------------------------------ */
      WHEN REGEXP_LIKE(skutitle, '(?i)(懐中電灯|フラッシュライト|flashlight|torch|トーチ)')
      THEN '摄影手电'

      WHEN REGEXP_LIKE(skutitle, '(?i)(水中|ダイビング|防水|sealife|sea dragon|inon|weefine|bigblue|kraken|underwater|dive)')
       AND REGEXP_LIKE(skutitle, '(?i)(ライト|led|lm|ルーメン|lumen|照明)')
      THEN '摄影手电'

      /* ------------------------------------------------------------
         6) 棒灯（PavoTube / LC500 等）
         ------------------------------------------------------------ */
      WHEN stdcategory3t = '灯光类-其他'
       AND REGEXP_LIKE(
             skutitle,
             '(?i)(pavotube|チューブライト|ライトチューブ|tube light|ライトスティック|スティックライト|lc500r?|tc[- ]?[0-9]{2,3})'
           )
       AND NOT REGEXP_LIKE(skutitle, '(?i)(ストロボ|フラッシュ)')
      THEN '棒灯'

      /* ------------------------------------------------------------
         7) 口袋灯（小型视频灯）：视频/补光语义 + 小型形态信号
         ------------------------------------------------------------ */
      WHEN stdcategory3t = '灯光类-其他'
       AND REGEXP_LIKE(skutitle, '(?i)(ビデオライト|撮影用ライト|撮影ライト|フィルライト|ledビデオライト|video light|fill light)')
       AND REGEXP_LIKE(
             skutitle,
             '(?i)(小型|ミニ|超薄型|薄型|コンパクト|軽量|手持ち|携帯|ポケット|usb|充電|充電式|[0-9]+mah|49led|ulanzi|vijim|vl[- ]?[0-9]{2,3}|amaran\\s*ace\\s*25|aputure\\s*mc\\b|\\bmc\\b)'
           )
       AND NOT REGEXP_LIKE(skutitle, '(?i)(ストロボ|フラッシュ|ttl|hss|ws|ad[0-9]{3}|speedlite|speedlight)')
       AND NOT REGEXP_LIKE(skutitle, '(?i)(アダプター|コンバータ|変換|ネジ|ねじ|雲台|ボールヘッド|プレート)')
      THEN '口袋灯'

      /* ------------------------------------------------------------
         8) 手机便携补光灯（夹子类小补光灯）：仅在“非环形灯”场景触发，避免误伤 ring light 套装
         ------------------------------------------------------------ */
      WHEN stdcategory3t = '灯光类-其他'
       AND REGEXP_LIKE(skutitle, '(?i)(スマホ|iphone|携帯|phone)')
       AND REGEXP_LIKE(skutitle, '(?i)(クリップライト|クリップ式)')
       AND REGEXP_LIKE(skutitle, '(?i)(ライト|led|フィルライト|補助光|補光)')
       AND NOT REGEXP_LIKE(skutitle, '(?i)(リングライト|ring light|女優ライト|サークルライト)')
       AND NOT REGEXP_LIKE(skutitle, '(?i)(クリップオンストロボ|クリップオンフラッシュ)')
      THEN '手机便携补光灯'

      /* ------------------------------------------------------------
         9) 平板灯（含 monitor/desk/webcam/key light/一般视频灯兜底）
         ------------------------------------------------------------ */
      WHEN stdcategory3t = '灯光类-其他'
       AND REGEXP_LIKE(
             skutitle,
             '(?i)(パネルライト|ライトパネル|ledパネル|\\bpanel\\b|エッジライト|edge light|キーライト|key light|モニターライト|スクリーンバー|screenbar|ライトバー|デスクライト|卓上ライト|webカメラライト|ウェブカメラライト)'
           )
       AND NOT REGEXP_LIKE(skutitle, '(?i)(ストロボ|フラッシュ)')
      THEN '平板灯'

      WHEN stdcategory3t = '灯光类-其他'
       AND REGEXP_LIKE(skutitle, '(web会議|zoom|ビデオ会議|オンライン|配信|ストリーミング|テレワーク|リモートワーク)')
       AND REGEXP_LIKE(skutitle, '(?i)(ライト|led|照明)')
       AND NOT REGEXP_LIKE(skutitle, '(?i)(ストロボ|フラッシュ)')
      THEN '平板灯'

      /* 一般 “撮影用ライト/ビデオライト/フィルライト” 且非闪光灯 → 平板灯 兜底 */
      WHEN stdcategory3t = '灯光类-其他'
       AND REGEXP_LIKE(skutitle, '(?i)(ビデオライト|撮影用ライト|撮影ライト|フィルライト|ledビデオライト|video light|fill light)')
       AND NOT REGEXP_LIKE(skutitle, '(?i)(ストロボ|フラッシュ|ttl|hss|ws)')
      THEN '平板灯'

      /* ------------------------------------------------------------
         10) COB补光灯：更严格（排除闪光灯词 + 排除指定附件词 + 排除 panel/ring）
         ------------------------------------------------------------ */
      WHEN (
            REGEXP_LIKE(skutitle, '(?i)(\\bcob\\b|コブ|bowens|ボーエンズ|ボーエンズマウント|bowensマウント)')
            OR (
              REGEXP_LIKE(skutitle, '([0-9]+)[ ]*(?:w|ｗ|ワット|watt)(?:[^0-9a-zA-Z]|$)')
              AND CAST(REGEXP_EXTRACT(skutitle, '([0-9]+)[ ]*(?:w|ｗ|ワット|watt)(?:[^0-9a-zA-Z]|$)', 1) AS INTEGER) >= 50
              AND CAST(REGEXP_EXTRACT(skutitle, '([0-9]+)[ ]*(?:w|ｗ|ワット|watt)(?:[^0-9a-zA-Z]|$)', 1) AS INTEGER) <= 2000
              AND REGEXP_LIKE(
                    skutitle,
                    '(?i)(定常|定常光|色温度|cri|tlci|lux|モデリング|照明効果|バイカラー|rgb|アプリ|dmx|ビデオライト|撮影ライト)'
                  )
            )
            OR REGEXP_LIKE(
                 skutitle,
                 '(?i)(amaran\\s*(100d|200x|200xs|200x[- ]?s)|aputure\\s*(60x|120d|300d|600d)|nanlite\\s*(fs|forza|fc)\\s*-?\\s*[0-9]{2,3}|godox\\s*(sl|ml|ms|knowled)\\s*-?\\s*[0-9]{2,3}|neewer\\s*fs[0-9]{2,3})'
               )
           )
       AND NOT REGEXP_LIKE(skutitle, '(?i)(ストロボ|フラッシュ|ttl|hss|ws|ad[0-9]{3}|speedlite|speedlight)')
       AND NOT REGEXP_LIKE(skutitle, '(?i)(リングライト|ring light|サークルライト|女優ライト)')
       AND NOT REGEXP_LIKE(skutitle, '(?i)(パネルライト|ライトパネル|ledパネル|\\bpanel\\b|エッジライト|edge light)')
       AND NOT REGEXP_LIKE(
             skutitle,
             '(?i)(ソフトボックス|softbox|ディフューザー|diffuser|リフレクター|reflector|グリッド|grid|ハニカム|honeycomb|バーンドア|barndoor|ゴボ|gobo|フレネル|fresnel|スポットライト|spotlight)'
           )
      THEN 'COB补光灯'

      /* ------------------------------------------------------------
         11) 脚架（灯架/三脚/支架类：且无明显“光源”指标）
         ------------------------------------------------------------ */
      WHEN stdcategory3t = '灯光类-其他'
       AND REGEXP_LIKE(skutitle, '(ライトスタンド|三脚|トライポッド|tripod|cスタンド|ブーム|スタンド)')
       AND NOT REGEXP_LIKE(skutitle, '(?i)(led|色温度|cri|tlci|lux|ビデオライト|撮影ライト|フィルライト|cob|ボーエンズ|リングライト|パネルライト|ストロボ|フラッシュ)')
      THEN '脚架'

      ELSE stdcategory3t
    END AS stdcategory3t

  FROM final_calc
)

SELECT
  skuid,
  producturl,
  stdbrandname,
  categoryname,
  subcategory,
  skutitle,
  producttitlecn,
  gmv,
  stdcategory3t,
  ROW_NUMBER() OVER (PARTITION BY stdcategory3t ORDER BY gmv DESC) AS rnk
FROM final_fix;