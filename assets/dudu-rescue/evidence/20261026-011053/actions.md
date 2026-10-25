# 逐步动作表

Recorder after 图可能仍是过渡帧；后继 before 图和 decisions/OCR 源图用于验收。

| 状态 | 操作/坐标 | 原因 | 执行 | 前图 | 后图 |
|---|---|---|---|---|---|
| → | session_created  |  |  | — | — |
| S0001→ | shot  |  | True | — | — |
| S0001→S0002 | tap [630, 627] | 首页点继续游戏，恢复本轮C区存档 | True | [图](frames/screenshots--S0001_before.webp) | [图](frames/screenshots--S0001_after.webp) |
| S0002→S0003 | tap [774, 460] | C区右下最近哭脸气泡，前往第1处救援点 | True | [图](frames/screenshots--S0002_before.webp) | [图](frames/screenshots--S0002_after.webp) |
| S0003→ | shot  |  | True | — | — |
| S0003→S0004 | tap [638, 397] | 第1处救援点交付爪x1请求，用活动内免费库存换笑脸 | True | [图](frames/screenshots--S0003_before.webp) | [图](frames/screenshots--S0003_after.webp) |
| S0004→S0005 | tap [682, 443] | 第1处救援点交付爪x1请求，用活动内免费库存换笑脸 | True | [图](frames/screenshots--S0004_before.webp) | [图](frames/screenshots--S0004_after.webp) |
| S0005→S0006 | tap [768, 443] | 第1处救援点交付绷带x1请求，用活动内免费库存换笑脸 | True | [图](frames/screenshots--S0005_before.webp) | [图](frames/screenshots--S0005_after.webp) |
| S0006→S0007 | tap [721, 440] | 剩余气泡已重新居中到721,440，交付绷带x1请求 | True | [图](frames/screenshots--S0006_before.webp) | [图](frames/screenshots--S0006_after.webp) |
| S0007→S0008 | tap [663, 331] | C区中部哭脸气泡，前往第2处救援点 | True | [图](frames/screenshots--S0007_before.webp) | [图](frames/screenshots--S0007_after.webp) |
| S0008→S0009 | tap [684, 312] | 第2处救援点交付爪x1请求 | True | [图](frames/screenshots--S0008_before.webp) | [图](frames/screenshots--S0008_after.webp) |
| S0009→S0010 | tap [684, 312] | 第2处救援点交付绷带x1请求 | True | [图](frames/screenshots--S0009_before.webp) | [图](frames/screenshots--S0009_after.webp) |
| S0010→S0011 | tap [631, 304] | 点击锤子心形气泡进入岩石小游戏，只取免费带走奖励不锤击 | True | [图](frames/screenshots--S0010_before.webp) | [图](frames/screenshots--S0010_after.webp) |
| S0011→S0012 | tap [788, 272] | C区右上哭脸气泡，前往第3处救援点 | True | [图](frames/screenshots--S0011_after.webp) | [图](frames/screenshots--S0011_after.webp) |
| S0012→ | shot  |  | True | — | — |
| S0012→S0013 | tap [690, 440] | 点岩石用1次免费锤击额度，看碎裂度变化；有价签按钮不点 | True | [图](frames/screenshots--S0011_after.webp) | [图](frames/screenshots--S0011_after.webp) |
| S0013→S0014 | tap [447, 598] | 岩石页锤击需消耗宝石或活动付费资源，按红线直接带走奖励退出 | True | [图](frames/screenshots--S0011_after.webp) | [图](frames/screenshots--S0013_after.webp) |
| S0014→S0015 | tap [629, 607] | 岩石带走奖励的固定掉落弹窗，点开心收下确认已获奖励 | True | [图](frames/screenshots--S0014_before.webp) | [图](frames/screenshots--S0014_after.webp) |
| S0015→S0016 | tap [554, 170] | C区中上哭脸气泡，前往下一处救援点 | True | [图](frames/screenshots--S0015_before.webp) | [图](frames/screenshots--S0015_after.webp) |
| S0016→S0017 | tap [471, 158] | 中上救援点交付爪x1请求 | True | [图](frames/screenshots--S0016_before.webp) | [图](frames/screenshots--S0016_after.webp) |
| S0017→S0018 | tap [510, 156] | 中上救援点交付绷带x1请求 | True | [图](frames/screenshots--S0017_before.webp) | [图](frames/screenshots--S0017_after.webp) |
| S0018→S0019 | tap [391, 199] | C区左上哭脸气泡，前往下一处救援点 | True | [图](frames/screenshots--S0018_before.webp) | [图](frames/screenshots--S0018_after.webp) |
| S0019→S0020 | tap [404, 186] | 左上救援点交付爪x1请求 | True | [图](frames/screenshots--S0019_before.webp) | [图](frames/screenshots--S0019_after.webp) |
| S0020→S0021 | tap [405, 178] | 点击糖果篮心形气泡进入锦旗好感页，只取左档免费 | True | [图](frames/screenshots--S0020_before.webp) | [图](frames/screenshots--S0020_after.webp) |
| S0021→S0022 | tap [382, 409] | 用免费钩取次数钩一个糖果篮，付费一键下钩不点 | True | [图](frames/screenshots--S0021_before.webp) | [图](frames/screenshots--S0021_after.webp) |
| S0022→S0023 | tap [270, 465] | 用免费钩取次数钩左上第一个糖果篮，付费一键下钩不点 | True | [图](frames/screenshots--S0021_after.webp) | [图](frames/screenshots--S0022_after.webp) |
| S0023→S0024 | tap [517, 470] | 用免费钩取次数钩第二个糖果篮找目标糖果 | True | [图](frames/screenshots--S0023_before.webp) | [图](frames/screenshots--S0023_after.webp) |
| S0024→S0025 | tap [367, 474] | 用免费钩取次数钩糖果篮找目标糖果 | True | [图](frames/screenshots--S0024_before.webp) | [图](frames/screenshots--S0024_after.webp) |
| S0025→S0026 | tap [640, 474] | 用免费钩取次数钩糖果篮找目标糖果 | True | [图](frames/screenshots--S0025_before.webp) | [图](frames/screenshots--S0025_after.webp) |
| S0026→S0027 | tap [759, 426] | 用免费钩取次数钩糖果篮找目标糖果 | True | [图](frames/screenshots--S0026_before.webp) | [图](frames/screenshots--S0026_after.webp) |
| S0027→S0028 | tap [889, 474] | 用免费钩取次数钩糖果篮找目标糖果 | True | [图](frames/screenshots--S0027_before.webp) | [图](frames/screenshots--S0027_after.webp) |
| S0028→S0029 | tap [1007, 420] | 用免费钩取次数钩糖果篮找目标糖果 | True | [图](frames/screenshots--S0028_before.webp) | [图](frames/screenshots--S0028_after.webp) |
| S0029→S0030 | tap [1209, 41] | 糖果篮免费钩数已用尽，点右上X退出小游戏，不点付费额外下钩 | True | [图](frames/screenshots--S0029_before.webp) | [图](frames/screenshots--S0029_after.webp) |
| S0030→S0031 | tap [404, 187] | 左上救援点交付手电x1请求 | True | [图](frames/screenshots--S0030_before.webp) | [图](frames/screenshots--S0030_after.webp) |
| S0031→S0032 | tap [357, 180] | 点击金锤心形气泡进入砸砖小游戏，只用免费次数 | True | [图](frames/screenshots--S0031_before.webp) | [图](frames/screenshots--S0031_after.webp) |
| S0032→S0033 | tap [378, 339] | C区左中哭脸气泡，前往倒数第二个救援点 | True | [图](frames/screenshots--S0032_after.webp) | [图](frames/screenshots--S0032_after.webp) |
| S0033→ | shot  |  | True | — | — |
| S0033→S0034 | swipe [634, 545, 741, 160, 700] | 按住锤子甩向金框砖头，用1次免费锤击 | True | [图](frames/screenshots--S0032_after.webp) | [图](frames/screenshots--S0033_after.webp) |
| S0034→S0035 | swipe [634, 545, 302, 263, 700] | 按住锤子甩向金框砖头，用免费锤击 | True | [图](frames/screenshots--S0034_before.webp) | [图](frames/screenshots--S0034_after.webp) |
| S0035→S0036 | swipe [634, 545, 634, 367, 700] | 按住锤子甩向金框砖头，用免费锤击 | True | [图](frames/screenshots--S0035_before.webp) | [图](frames/screenshots--S0035_after.webp) |
| S0036→S0037 | swipe [634, 545, 847, 367, 700] | 按住锤子甩向金框砖头，用免费锤击 | True | [图](frames/screenshots--S0035_after.webp) | [图](frames/screenshots--S0036_after.webp) |
| S0037→S0038 | tap [1256, 36] | 砸砖免费锤子已用尽，点右上X退出，不点付费额外扔一次 | True | [图](frames/screenshots--S0036_after.webp) | [图](frames/screenshots--S0037_after.webp) |
| S0038→S0039 | tap [378, 339] | C区左中哭脸气泡，前往救援点 | True | [图](frames/screenshots--S0038_before.webp) | [图](frames/screenshots--S0038_after.webp) |
| S0039→S0040 | tap [293, 310] | 左中救援点交付手电x1请求 | True | [图](frames/screenshots--S0039_before.webp) | [图](frames/screenshots--S0039_after.webp) |
| S0040→S0041 | tap [331, 321] | 左中救援点交付绷带x1请求 | True | [图](frames/screenshots--S0040_before.webp) | [图](frames/screenshots--S0040_after.webp) |
| S0041→S0042 | tap [494, 611] | 区域C已45/45达标，点下个区域进入下一个区域准备页（不扣体力） | True | [图](frames/screenshots--S0041_before.webp) | [图](frames/screenshots--S0041_after.webp) |
| S0042→S0043 | tap [400, 200] | 复用免费背包模块：OCR额度2/2，模板确认plain包 | True | [图](frames/screenshots--S0042_before.webp) | [图](frames/screenshots--S0042_after.webp) |
| S0043→S0044 | tap [590, 200] | 复用免费背包模块：OCR额度1/2，模板确认plain包 | True | [图](frames/screenshots--S0043_before.webp) | [图](frames/screenshots--S0043_after.webp) |
| S0044→S0045 | tap [590, 375] | 复用免费背包模块：OCR额度0/2，模板确认locked包 | True | [图](frames/screenshots--S0044_before.webp) | [图](frames/screenshots--S0044_after.webp) |
| S0045→S0046 | tap [780, 375] | 复用免费背包模块：OCR额度0/1，模板确认locked包 | True | [图](frames/screenshots--S0045_before.webp) | [图](frames/screenshots--S0045_after.webp) |
| S0046→ | shot  |  | True | — | — |
| S0046→S0047 | tap [1072, 660] | 免费背包已开完，点出发救援进入下一区域检修页 | True | [图](frames/screenshots--S0046_before.webp) | [图](frames/screenshots--S0046_after.webp) |
| S0047→S0048 | tap [767, 220] | 未知区域检修11/100：点右上无价签免费扳手 | True | [图](frames/screenshots--S0047_before.webp) | [图](frames/screenshots--S0047_after.webp) |
| S0048→S0049 | tap [785, 225] | 点击检修页无价签的勋章x10节点，取免费奖励 | True | [图](frames/screenshots--S0048_before.webp) | [图](frames/screenshots--S0048_after.webp) |
| S0049→S0050 | tap [512, 348] | 未知区域检修：点左侧无价签免费扳手 | True | [图](frames/screenshots--S0049_before.webp) | [图](frames/screenshots--S0049_after.webp) |
| S0050→S0051 | tap [452, 355] | 点击检修页无价签的x10免费节点取奖励 | True | [图](frames/screenshots--S0050_before.webp) | [图](frames/screenshots--S0050_after.webp) |
| S0051→S0052 | tap [369, 582] | 误触付费精修位的补足确认框，点取消不留任何成交 | True | [图](frames/screenshots--S0051_before.webp) | [图](frames/screenshots--S0051_after.webp) |
| S0052→S0053 | tap [668, 340] | 未知区域检修36/100：点中上无价签免费扳手 | True | [图](frames/screenshots--S0052_before.webp) | [图](frames/screenshots--S0052_after.webp) |
| S0053→S0054 | tap [668, 340] | 同一位置出现无价签x10节点，取这一次免费奖励 | True | [图](frames/screenshots--S0053_before.webp) | [图](frames/screenshots--S0053_after.webp) |
| S0054→S0055 | tap [568, 450] | 未知区域检修51/100：点左下无价签免费扳手 | True | [图](frames/screenshots--S0054_before.webp) | [图](frames/screenshots--S0054_after.webp) |
| S0055→S0056 | tap [562, 452] | 取左下位置新出现的无价签x10节点奖励 | True | [图](frames/screenshots--S0055_before.webp) | [图](frames/screenshots--S0055_after.webp) |
| S0056→S0057 | tap [369, 582] | 误触付费精修位的确认框，点取消不留成交 | True | [图](frames/screenshots--S0056_before.webp) | [图](frames/screenshots--S0056_after.webp) |
| S0057→S0058 | tap [790, 460] | 未知区域检修61/100：点右下最后一个无价签免费扳手 | True | [图](frames/screenshots--S0057_before.webp) | [图](frames/screenshots--S0057_after.webp) |
| S0058→S0059 | tap [770, 470] | 右下位置新出现的无价签x10节点，取免费奖励 | True | [图](frames/screenshots--S0058_before.webp) | [图](frames/screenshots--S0058_after.webp) |
| S0059→S0060 | tap [369, 582] | 误触付费精修位确认框，点取消不留成交 | True | [图](frames/screenshots--S0059_before.webp) | [图](frames/screenshots--S0059_after.webp) |
| S0060→ | shot  |  | True | — | — |
| S0060→S0061 | tap [1139, 661] | 耐久71已过半且免费扳手用完，出发进入未知区域地图 | True | [图](frames/screenshots--S0060_before.webp) | [图](frames/screenshots--S0060_after.webp) |
| S0061→S0062 | tap [1236, 35] | 点地图右上红X，准备用暂时离开保存本轮进度 | True | [图](frames/screenshots--S0061_before.webp) | [图](frames/screenshots--S0061_after.webp) |
| S0062→S0063 | tap [899, 584] | 选暂时离开保存本轮进度，不选确认结束整轮 | True | [图](frames/screenshots--S0062_before.webp) | [图](frames/screenshots--S0062_after.webp) |
