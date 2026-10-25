# 逐步动作表

Recorder after 图可能仍是过渡帧；后继 before 图和 decisions/OCR 源图用于验收。

| 状态 | 操作/坐标 | 原因 | 执行 | 前图 | 后图 |
|---|---|---|---|---|---|
| → | session_created  |  |  | — | — |
| S0001→S0002 | tap [210, 200] | 复用免费背包模块：OCR额度3/1，模板确认plain包 | True | [图](frames/screenshots--S0001_before.webp) | [图](frames/screenshots--S0001_after.webp) |
| S0002→S0003 | tap [400, 375] | 复用免费背包模块：OCR额度2/1，模板确认plain包 | True | [图](frames/screenshots--S0002_before.webp) | [图](frames/screenshots--S0002_after.webp) |
| S0003→S0004 | tap [210, 550] | 复用免费背包模块：OCR额度1/1，模板确认plain包 | True | [图](frames/screenshots--S0003_before.webp) | [图](frames/screenshots--S0003_after.webp) |
| S0004→S0005 | tap [210, 375] | 复用免费背包模块：OCR额度0/1，模板确认locked包 | True | [图](frames/screenshots--S0004_before.webp) | [图](frames/screenshots--S0004_after.webp) |
| S0005→S0006 | tap [1072, 660] | 点右下出发救援按钮进入检修页 | True | [图](frames/screenshots--S0005_before.webp) | [图](frames/screenshots--S0005_after.webp) |
| S0006→S0007 | tap [451, 342] | 区域A检修 0/100：点左侧免费扳手(无价签) | True | [图](frames/screenshots--S0006_before.webp) | [图](frames/screenshots--S0006_after.webp) |
| S0007→S0008 | tap [672, 339] | 区域A检修 10/100：点中央免费扳手 | True | [图](frames/screenshots--S0007_before.webp) | [图](frames/screenshots--S0007_after.webp) |
| S0008→ | shot  |  | True | — | — |
| S0008→S0009 | tap [797, 224] | 区域A检修 20/100：点右上免费扳手 | True | [图](frames/screenshots--S0008_before.webp) | [图](frames/screenshots--S0008_after.webp) |
| S0009→S0010 | tap [560, 444] | 区域A检修 30/100：点左下免费扳手 | True | [图](frames/screenshots--S0009_before.webp) | [图](frames/screenshots--S0009_after.webp) |
| S0010→S0011 | tap [772, 463] | 区域A检修 40/100：点右下免费扳手 | True | [图](frames/screenshots--S0010_before.webp) | [图](frames/screenshots--S0010_after.webp) |
| S0011→ | shot  |  | True | — | — |
| S0011→ | shot  |  | True | — | — |
| S0011→ | shot  |  | True | — | — |
| S0011→S0012 | tap [1139, 661] | 检修进度65/100已过半，出发救援进入区域A地图 | True | [图](frames/screenshots--S0011_before.webp) | [图](frames/screenshots--S0011_after.webp) |
| S0012→S0013 | tap [712, 286] | 点击最近的哭脸气泡前往救援点，区域A剩余4处救援点 | True | [图](frames/screenshots--S0012_before.webp) | [图](frames/screenshots--S0012_after.webp) |
| S0013→S0014 | tap [779, 330] | 点击右下哭脸气泡(连通域实测中心779,334)前往该救援点 | True | [图](frames/screenshots--S0013_before.webp) | [图](frames/screenshots--S0013_after.webp) |
| S0014→ | tap  | 无法识别的 safety='inventory' | False | — | — |
| S0014→ | tap  | 无法识别的 safety='inventory' | False | — | — |
| S0014→S0015 | tap [680, 305] | 点击爪x1请求气泡，用活动内免费库存交付换笑脸 | True | [图](frames/screenshots--S0014_before.webp) | [图](frames/screenshots--S0014_after.webp) |
| S0015→S0016 | tap [726, 315] | 点击手电x1请求气泡，用活动内免费库存交付换笑脸 | True | [图](frames/screenshots--S0015_before.webp) | [图](frames/screenshots--S0015_after.webp) |
| S0016→S0017 | tap [769, 183] | 点击最近的左上哭脸气泡前往第二个救援点 | True | [图](frames/screenshots--S0016_before.webp) | [图](frames/screenshots--S0016_after.webp) |
| S0017→S0018 | tap [686, 155] | 第二个救援点：点击爪x1请求气泡交付 | True | [图](frames/screenshots--S0017_before.webp) | [图](frames/screenshots--S0017_after.webp) |
| S0018→S0019 | tap [711, 140] | 第二个救援点：点击手电x1请求气泡交付 | True | [图](frames/screenshots--S0018_before.webp) | [图](frames/screenshots--S0018_after.webp) |
| S0019→S0020 | tap [547, 289] | 点击左侧哭脸气泡前往第三个救援点，区域还差7个笑脸 | True | [图](frames/screenshots--S0019_before.webp) | [图](frames/screenshots--S0019_after.webp) |
| S0020→S0021 | tap [550, 267] | 第三个救援点：点击爪x1请求气泡交付 | True | [图](frames/screenshots--S0020_before.webp) | [图](frames/screenshots--S0020_after.webp) |
| S0021→S0022 | tap [556, 272] | 第三个救援点：点击绷带x1请求气泡交付 | True | [图](frames/screenshots--S0021_before.webp) | [图](frames/screenshots--S0021_after.webp) |
| S0022→ | shot  |  | True | — | — |
| S0022→S0023 | tap [598, 195] | 区域24/25还差1个笑脸，前往第4个哭脸气泡接着交付 | True | [图](frames/screenshots--S0022_before.webp) | [图](frames/screenshots--S0022_after.webp) |
| S0023→ | shot  |  | True | — | — |
| S0023→S0024 | tap [528, 150] | 第4个救援点：点击手电x1请求气泡交付，区域还差1个笑脸 | True | [图](frames/screenshots--S0023_before.webp) | [图](frames/screenshots--S0023_after.webp) |
| S0024→ | shot  |  | True | — | — |
| S0024→S0025 | tap [561, 148] | 第4个救援点：点击爪x1请求气泡交付，把本处推到完美救援 | True | [图](frames/screenshots--S0024_before.webp) | [图](frames/screenshots--S0024_after.webp) |
| S0025→S0026 | tap [495, 611] | 区域A已达29/25且完成3处救援，点下个区域进入下一准备页 | True | [图](frames/screenshots--S0025_before.webp) | [图](frames/screenshots--S0025_after.webp) |
| S0026→S0027 | tap [590, 200] | 复用免费背包模块：OCR额度3/1，模板确认plain包 | True | [图](frames/screenshots--S0026_before.webp) | [图](frames/screenshots--S0026_after.webp) |
| S0027→S0028 | tap [210, 375] | 复用免费背包模块：OCR额度2/1，模板确认plain包 | True | [图](frames/screenshots--S0027_before.webp) | [图](frames/screenshots--S0027_after.webp) |
| S0028→S0029 | tap [400, 375] | 复用免费背包模块：OCR额度1/1，模板确认plain包 | True | [图](frames/screenshots--S0028_before.webp) | [图](frames/screenshots--S0028_after.webp) |
| S0029→S0030 | tap [590, 375] | 复用免费背包模块：OCR额度0/1，模板确认locked包 | True | [图](frames/screenshots--S0029_before.webp) | [图](frames/screenshots--S0029_after.webp) |
| S0030→S0031 | tap [1114, 673] | 免费背包已开完，点出发救援进入新区域检修页 | True | [图](frames/screenshots--S0030_before.webp) | [图](frames/screenshots--S0030_after.webp) |
| S0031→S0032 | tap [674, 345] | 点击区域B中部免费扳手检修飞机，每处首次免费 | True | [图](frames/screenshots--S0031_before.webp) | [图](frames/screenshots--S0031_after.webp) |
| S0032→S0033 | tap [452, 348] | 点击区域B左侧免费扳手检修飞机 | True | [图](frames/screenshots--S0032_before.webp) | [图](frames/screenshots--S0032_after.webp) |
| S0033→S0034 | tap [556, 447] | 点击区域B下方免费扳手检修飞机 | True | [图](frames/screenshots--S0033_before.webp) | [图](frames/screenshots--S0033_after.webp) |
| S0034→S0035 | tap [758, 450] | 点击区域B右下免费扳手检修飞机 | True | [图](frames/screenshots--S0034_before.webp) | [图](frames/screenshots--S0034_after.webp) |
| S0035→S0036 | tap [795, 214] | 点击区域B右上免费扳手检修飞机 | True | [图](frames/screenshots--S0035_before.webp) | [图](frames/screenshots--S0035_after.webp) |
| S0036→ | shot  |  | True | — | — |
| S0036→S0037 | tap [1139, 661] | 区域B耐久73/100已过半且5处免费扳手用完，出发救援进入区域B地图 | True | [图](frames/screenshots--S0036_before.webp) | [图](frames/screenshots--S0036_after.webp) |
| S0037→S0038 | tap [790, 309] | 区域B：点击最近哭脸气泡前往第1个救援点 | True | [图](frames/screenshots--S0037_before.webp) | [图](frames/screenshots--S0037_after.webp) |
| S0038→ | shot  |  | True | — | — |
| S0038→S0039 | tap [795, 303] | 区域B第1个救援点：点击爪x1请求气泡交付 | True | [图](frames/screenshots--S0038_before.webp) | [图](frames/screenshots--S0038_after.webp) |
| S0039→S0040 | tap [795, 303] | 区域B第1个救援点：点击绷带x1请求气泡交付 | True | [图](frames/screenshots--S0039_before.webp) | [图](frames/screenshots--S0039_after.webp) |
| S0040→S0041 | tap [680, 279] | 区域B第1点已6/9且无新请求，前往最近的第2个哭脸气泡 | True | [图](frames/screenshots--S0040_before.webp) | [图](frames/screenshots--S0040_after.webp) |
| S0041→ | shot  |  | True | — | — |
| S0041→S0042 | tap [676, 245] | 进入纸飞机心形气泡小游戏，只看免费部分不兑换 | True | [图](frames/screenshots--S0041_before.webp) | [图](frames/screenshots--S0041_after.webp) |
| S0042→S0043 | tap [1030, 152] | 关闭纸飞机小游戏浮层，不兑换任何价位 | True | [图](frames/screenshots--S0042_after.webp) | [图](frames/screenshots--S0042_after.webp) |
| S0043→S0044 | tap [1240, 38] | 关闭纸飞机小游戏全屏页，未兑换任何价位 | True | [图](frames/screenshots--S0042_after.webp) | [图](frames/screenshots--S0043_after.webp) |
| S0044→ | shot  |  | True | — | — |
| S0044→S0045 | tap [700, 245] | 区域B第2个救援点：点击绷带x1请求气泡交付 | True | [图](frames/screenshots--S0044_before.webp) | [图](frames/screenshots--S0044_after.webp) |
| S0045→S0046 | tap [700, 240] | 区域B第2个救援点：点击爪x1请求气泡交付 | True | [图](frames/screenshots--S0045_before.webp) | [图](frames/screenshots--S0045_after.webp) |
| S0046→S0047 | tap [594, 240] | 进入锤子心形气泡小游戏，看是否也给笑脸 | True | [图](frames/screenshots--S0046_before.webp) | [图](frames/screenshots--S0046_after.webp) |
| S0047→S0048 | tap [628, 248] | 点击锤子心形气泡中心，看是否打开小游戏 | True | [图](frames/screenshots--S0047_before.webp) | [图](frames/screenshots--S0047_after.webp) |
| S0048→S0049 | tap [561, 279] | 区域B第2点已圆满，前往最近的第3个哭脸气泡 | True | [图](frames/screenshots--S0048_after.webp) | [图](frames/screenshots--S0048_after.webp) |
| S0049→S0050 | tap [457, 598] | 岩石小游戏：不锤击直接带走奖励退出，免费拿救援点笑脸 | True | [图](frames/screenshots--S0048_after.webp) | [图](frames/screenshots--S0049_after.webp) |
| S0050→S0051 | tap [633, 611] | 岩石零锤击固定奖励弹窗，点开心收下（已获得的固定掉落） | True | [图](frames/screenshots--S0049_after.webp) | [图](frames/screenshots--S0050_after.webp) |
| S0051→S0052 | tap [578, 431] | 区域B：前往下一处哭脸气泡救援点 | True | [图](frames/screenshots--S0051_before.webp) | [图](frames/screenshots--S0051_after.webp) |
| S0052→S0053 | tap [574, 394] | 区域B第3个救援点：点击绷带x1请求气泡交付 | True | [图](frames/screenshots--S0052_before.webp) | [图](frames/screenshots--S0052_after.webp) |
| S0053→S0054 | tap [500, 396] | 点击糖果心形气泡收取节点奖励，免费加笑脸 | True | [图](frames/screenshots--S0053_before.webp) | [图](frames/screenshots--S0053_after.webp) |
| S0054→ | shot  |  | True | — | — |
| S0054→S0055 | tap [256, 615] | 锦旗好感三档：只点左档免费收下，中间宝石20与右侧钞票12不点 | True | [图](frames/screenshots--S0054_before.webp) | [图](frames/screenshots--S0054_after.webp) |
| S0055→S0056 | tap [633, 610] | 锦旗免费档已获得固定掉落，点开心收下确认 | True | [图](frames/screenshots--S0054_after.webp) | [图](frames/screenshots--S0055_after.webp) |
| S0056→ | shot  |  | True | — | — |
| S0056→S0057 | tap [497, 405] | 区域B第3个救援点：点击手电x1请求气泡交付 | True | [图](frames/screenshots--S0056_before.webp) | [图](frames/screenshots--S0056_after.webp) |
| S0057→S0058 | tap [430, 189] | 区域B：库存已无匹配请求，前往最后一处哭脸气泡继续换笑脸 | True | [图](frames/screenshots--S0057_before.webp) | [图](frames/screenshots--S0057_after.webp) |
| S0058→ | shot  |  | True | — | — |
| S0058→S0059 | tap [435, 175] | 区域B第5个救援点：点击手电x1请求气泡交付 | True | [图](frames/screenshots--S0058_before.webp) | [图](frames/screenshots--S0058_after.webp) |
| S0059→S0060 | tap [437, 178] | 区域B第5个救援点：点击爪x1请求气泡交付 | True | [图](frames/screenshots--S0059_before.webp) | [图](frames/screenshots--S0059_after.webp) |
| S0060→S0061 | tap [437, 178] | 点击锤子心形气泡收节点奖励，免费加笑脸 | True | [图](frames/screenshots--S0060_before.webp) | [图](frames/screenshots--S0060_after.webp) |
| S0061→ | shot  |  | True | — | — |
| S0061→S0062 | tap [447, 598] | 岩石小游戏：零锤击直接带走奖励退出，给当前救援点加笑脸 | True | [图](frames/screenshots--S0061_before.webp) | [图](frames/screenshots--S0061_after.webp) |
| S0062→S0063 | tap [341, 152] | 点击糖果心形气泡，进入免费三档锦旗好感页 | True | [图](frames/screenshots--S0062_before.webp) | [图](frames/screenshots--S0062_after.webp) |
| S0063→S0064 | tap [390, 186] | 点击糖果心形气泡进入免费三档锦旗好感页 | True | [图](frames/screenshots--S0063_before.webp) | [图](frames/screenshots--S0063_after.webp) |
| S0064→ | shot  |  | True | — | — |
| S0064→S0065 | tap [256, 615] | 锦旗好感三档：只点左档免费收下 | True | [图](frames/screenshots--S0064_before.webp) | [图](frames/screenshots--S0064_after.webp) |
| S0065→S0066 | tap [633, 610] | 免费档固定掉落确认，点开心收下 | True | [图](frames/screenshots--S0064_after.webp) | [图](frames/screenshots--S0065_after.webp) |
| S0066→S0067 | tap [593, 259] | 区域B还差4个笑脸，前往下一处哭脸气泡 | True | [图](frames/screenshots--S0066_before.webp) | [图](frames/screenshots--S0066_after.webp) |
| S0067→S0068 | tap [552, 262] | 区域B第4个救援点：点击手电x1请求气泡交付 | True | [图](frames/screenshots--S0067_before.webp) | [图](frames/screenshots--S0067_after.webp) |
| S0068→S0069 | tap [562, 284] | 区域B第4个救援点：点击爪x1请求气泡交付，再+3即达35 | True | [图](frames/screenshots--S0068_before.webp) | [图](frames/screenshots--S0068_after.webp) |
| S0069→S0070 | tap [495, 611] | 区域B已37/35达标，点下个区域进入下一区域 | True | [图](frames/screenshots--S0069_before.webp) | [图](frames/screenshots--S0069_after.webp) |
| S0070→S0071 | tap [210, 375] | 复用免费背包模块：OCR额度3/1，模板确认plain包 | True | [图](frames/screenshots--S0070_before.webp) | [图](frames/screenshots--S0070_after.webp) |
| S0071→S0072 | tap [400, 375] | 复用免费背包模块：OCR额度2/1，模板确认plain包 | True | [图](frames/screenshots--S0071_before.webp) | [图](frames/screenshots--S0071_after.webp) |
| S0072→S0073 | tap [210, 550] | 复用免费背包模块：OCR额度1/1，模板确认plain包 | True | [图](frames/screenshots--S0072_before.webp) | [图](frames/screenshots--S0072_after.webp) |
| S0073→S0074 | tap [400, 200] | 复用免费背包模块：OCR额度0/1，模板确认locked包 | True | [图](frames/screenshots--S0073_before.webp) | [图](frames/screenshots--S0073_after.webp) |
| S0074→S0075 | tap [1114, 673] | 区域C免费背包已开完，点出发救援进入检修页 | True | [图](frames/screenshots--S0074_before.webp) | [图](frames/screenshots--S0074_after.webp) |
| S0075→S0076 | tap [671, 336] | 区域C：点击中部免费扳手检修 | True | [图](frames/screenshots--S0075_before.webp) | [图](frames/screenshots--S0075_after.webp) |
| S0076→S0077 | tap [452, 357] | 区域C：点击左侧免费扳手检修 | True | [图](frames/screenshots--S0076_before.webp) | [图](frames/screenshots--S0076_after.webp) |
| S0077→S0078 | tap [575, 455] | 区域C：点击左下免费扳手检修 | True | [图](frames/screenshots--S0077_before.webp) | [图](frames/screenshots--S0077_after.webp) |
| S0078→ | shot  |  | True | — | — |
| S0078→ | shot  |  | True | — | — |
| S0078→ | shot  |  | True | — | — |
| S0078→ | shot  |  | True | — | — |
| S0078→S0079 | tap [1139, 661] | 区域C耐久61/100已过半、免费扳手用完，出发救援进入区域C地图 | True | [图](frames/screenshots--S0078_before.webp) | [图](frames/screenshots--S0078_after.webp) |
| S0079→S0080 | tap [1236, 35] | 点地图右上红X，准备用暂时离开保存本轮进度 | True | [图](frames/screenshots--S0079_before.webp) | [图](frames/screenshots--S0079_after.webp) |
| S0080→S0081 | tap [897, 582] | 选右「暂时离开」保存本轮进度回首页，不选左「确认」结束游戏 | True | [图](frames/screenshots--S0080_before.webp) | [图](frames/screenshots--S0080_after.webp) |
