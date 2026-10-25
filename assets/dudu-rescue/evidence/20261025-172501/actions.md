# 逐步动作表

Recorder after 图可能仍是过渡帧；后继 before 图和 decisions/OCR 源图用于验收。

| 状态 | 操作/坐标 | 原因 | 执行 | 前图 | 后图 |
|---|---|---|---|---|---|
| → | session_created  |  |  | — | — |
| S0001→ | shot  |  | True | — | — |
| S0001→S0002 | tap [57, 41] | 阅读活动帮助规则 | True | [图](frames/screenshots--S0001_before.webp) | [图](frames/screenshots--S0001_after.webp) |
| S0002→S0003 | tap [630, 83] | 阅读奖励合集页签 | True | [图](frames/screenshots--S0001_after.webp) | [图](frames/screenshots--S0002_after.webp) |
| S0003→S0004 | tap [895, 87] | 阅读宝石合集页签 | True | [图](frames/screenshots--S0002_after.webp) | [图](frames/screenshots--S0003_after.webp) |
| S0004→ | shot  |  | True | — | — |
| S0004→ | shot  |  | True | — | — |
| S0004→S0005 | tap [145, 395] | 从活动大厅首卡进入嘎嘎队立大功 | True | [图](frames/screenshots--S0004_before.webp) | [图](frames/screenshots--S0004_after.webp) |
| S0005→ | shot  |  | True | — | — |
| S0005→S0006 | tap [140, 530] | 查看飞行员手册的任务和免费奖励条件 | True | [图](frames/screenshots--S0005_before.webp) | [图](frames/screenshots--S0005_after.webp) |
| S0006→S0007 | tap [1240, 40] | 手册任务未达成且兑换涉及长期奖励保留用户选择，返回首页 | True | [图](frames/screenshots--S0006_before.webp) | [图](frames/screenshots--S0006_after.webp) |
| S0007→ | shot  |  | True | — | — |
| S0007→S0008 | tap [620, 630] | 首页显示4点已授权活动体力，开始第一轮救援，预计消耗1点 | True | [图](frames/screenshots--S0007_before.webp) | [图](frames/screenshots--S0007_after.webp) |
| S0008→S0009 | tap [210, 375] | 准备页明确普通背包免费3次，开启未上锁的左中背包，普通次数预计3变2 | True | [图](frames/screenshots--S0008_before.webp) | [图](frames/screenshots--S0008_after.webp) |
| S0009→ | shot  |  | True | — | — |
| S0009→S0010 | tap [210, 550] | 普通背包剩余2次，开启左下未锁背包 | True | [图](frames/screenshots--S0009_before.webp) | [图](frames/screenshots--S0009_after.webp) |
| S0010→S0011 | tap [400, 550] | 普通背包剩余1次，开启下排中间未锁背包 | True | [图](frames/screenshots--S0010_before.webp) | [图](frames/screenshots--S0010_after.webp) |
| S0011→S0012 | tap [400, 375] | 保留的免费加锁背包额度1/1，开启中排中间锁包；普通背包已转付费不再点 | True | [图](frames/screenshots--S0011_before.webp) | [图](frames/screenshots--S0011_after.webp) |
| S0012→S0013 | tap [1071, 660] | 仅在右下按钮区域识别出发救援，免费补给已收齐，进入地图 | True | [图](frames/screenshots--S0012_before.webp) | [图](frames/screenshots--S0012_after.webp) |
| S0013→ | shot  |  | True | — | — |
| S0013→S0014 | tap [640, 225] | 关闭首次进入的锦旗兑换说明浮层，只点说明文字不点任何兑换选项 | True | [图](frames/screenshots--S0013_before.webp) | [图](frames/screenshots--S0013_after.webp) |
| S0014→S0015 | tap [260, 116] | 锦旗说明文字点击无变化，点击当前页面问号切换说明显示 | True | [图](frames/screenshots--S0014_before.webp) | [图](frames/screenshots--S0014_after.webp) |
| S0015→S0016 | tap [460, 360] | 区域A提示点击扳手检修，选择机头扳手；右上一键检修另有货币价签不点 | True | [图](frames/screenshots--S0015_before.webp) | [图](frames/screenshots--S0015_after.webp) |
| S0016→S0017 | tap [565, 460] | 机头检修已使进度0变10且补给未扣，继续左下扳手检修 | True | [图](frames/screenshots--S0016_before.webp) | [图](frames/screenshots--S0016_after.webp) |
| S0017→S0018 | tap [800, 225] | 继续区域A右上尚未检修的扳手，每步留图确认 | True | [图](frames/screenshots--S0017_before.webp) | [图](frames/screenshots--S0017_after.webp) |
| S0018→S0019 | tap [680, 340] | 区域A进度30，点机身中央尚存扳手，预计增加检修进度 | True | [图](frames/screenshots--S0018_before.webp) | [图](frames/screenshots--S0018_after.webp) |
| S0019→S0020 | tap [780, 460] | 区域A进度40，点击最后一个普通机翼扳手；已出现的宝石精修不点 | True | [图](frames/screenshots--S0019_before.webp) | [图](frames/screenshots--S0019_after.webp) |
| S0020→S0021 | tap [1139, 660] | 区域A免费检修50/100已满足页面出发条件，补给保持5/8/1，进入下一阶段 | True | [图](frames/screenshots--S0020_before.webp) | [图](frames/screenshots--S0020_after.webp) |
| S0021→S0022 | tap [200, 125] | 进入区域A后先读区域玩法帮助，未点击一键救援 | True | [图](frames/screenshots--S0021_before.webp) | [图](frames/screenshots--S0021_after.webp) |
| S0022→S0023 | tap [200, 125] | 已读救援帮助，切回地图，按距离规划路线避免浪费飞机耐久 | True | [图](frames/screenshots--S0022_before.webp) | [图](frames/screenshots--S0022_after.webp) |
| S0023→S0024 | tap [615, 420] | 按帮助点击最近的石门哭脸进入救援点，当前耐久50，保存飞行消耗 | True | [图](frames/screenshots--S0021_before.webp) | [图](frames/screenshots--S0023_after.webp) |
| S0024→S0025 | tap [620, 405] | 石门救援点展开锤子玩法入口与绷带入口，先进入无价签锤子小游戏 | True | [图](frames/screenshots--S0024_before.webp) | [图](frames/screenshots--S0024_after.webp) |
| S0025→S0026 | tap [448, 599] | 锤巨石明确每击需20个账号宝石或付费，本次体力授权不包含账号宝石，零锤击退出该子玩法 | True | [图](frames/screenshots--S0024_after.webp) | [图](frames/screenshots--S0025_after.webp) |
| S0026→S0027 | tap [629, 605] | 零锤击直接结算已弹出固定免费随机奖励，收下金币章3金牌4折扣券1，无选择无额外消耗 | True | [图](frames/screenshots--S0026_before.webp) | [图](frames/screenshots--S0026_after.webp) |
| S0027→S0028 | tap [620, 405] | 该救援点下一任务是活动内夹爪x1，库存1，使用本局免费补给继续救援 | True | [图](frames/screenshots--S0027_before.webp) | [图](frames/screenshots--S0027_after.webp) |
| S0028→S0029 | tap [575, 405] | 石门任务进度6/9，当前只剩绷带x1请求且库存充足，使用活动内免费绷带 | True | [图](frames/screenshots--S0028_before.webp) | [图](frames/screenshots--S0028_after.webp) |
| S0029→S0030 | tap [430, 345] | 石门9/9已完成，飞往相邻树林哭脸救援点，记录耐久38的变化 | True | [图](frames/screenshots--S0029_before.webp) | [图](frames/screenshots--S0029_after.webp) |
| S0030→S0031 | tap [430, 325] | 树林请求绷带x1且库存4，先完成可用补给任务；夹爪库存0不点击 | True | [图](frames/screenshots--S0030_before.webp) | [图](frames/screenshots--S0030_after.webp) |
| S0031→S0032 | tap [430, 325] | 树林绷带任务已完成，新出现糖果篮小游戏入口，进入阅读规则 | True | [图](frames/screenshots--S0031_before.webp) | [图](frames/screenshots--S0031_after.webp) |
| S0032→S0033 | tap [270, 445] | 糖果篮玩法赠送7个钩爪，目标黄色糖果，先尝试最左篮观察单步交互 | True | [图](frames/screenshots--S0032_before.webp) | [图](frames/screenshots--S0032_after.webp) |
| S0033→S0034 | tap [390, 485] | 首次左篮为红色未命中黄色，钩爪剩6，探测第二个未开篮 | True | [图](frames/screenshots--S0033_before.webp) | [图](frames/screenshots--S0033_after.webp) |
| S0034→S0035 | tap [515, 445] | 钩爪剩5，继续第三个尚未开过的糖果篮，保留目标与结果帧 | True | [图](frames/screenshots--S0034_before.webp) | [图](frames/screenshots--S0034_after.webp) |
| S0035→S0036 | tap [640, 485] | 钩爪剩4，继续中间第四篮，免费次数未用尽 | True | [图](frames/screenshots--S0035_before.webp) | [图](frames/screenshots--S0035_after.webp) |
| S0036→S0037 | tap [765, 445] | 第四篮命中黄色，顶部黄色剩余2变1，钩爪3，继续第五个未开篮 | True | [图](frames/screenshots--S0036_before.webp) | [图](frames/screenshots--S0036_after.webp) |
| S0037→S0038 | tap [270, 445] | 当前目标已变红色，复用第一篮实际见过的红糖位置；钩爪剩2 | True | [图](frames/screenshots--S0037_before.webp) | [图](frames/screenshots--S0037_after.webp) |
| S0038→ | shot  |  | True | — | — |
| S0038→S0039 | tap [515, 445] | 新截图目标仍为红糖，第三篮曾实测红糖，使用最后1个免费钩爪 | True | [图](frames/screenshots--S0038_before.webp) | [图](frames/screenshots--S0038_after.webp) |
| S0039→ | shot  |  | True | — | — |
| S0039→S0040 | tap [645, 185] | 前三枚目标灯全部点亮，领取已达成的首个免费宝箱；额外下钩已转付费不点 | True | [图](frames/screenshots--S0039_before.webp) | [图](frames/screenshots--S0039_after.webp) |
| S0040→S0041 | tap [1230, 40] | 糖果篮免费钩爪已耗尽，额外一次明确付费，关闭小游戏结算本次免费进度 | True | [图](frames/screenshots--S0039_observe_02.webp) | [图](frames/screenshots--S0040_after.webp) |
| S0041→S0042 | tap [460, 175] | 树林6/9剩余夹爪库存0，先去相邻村庄哭脸，继续使用现有免费补给 | True | [图](frames/screenshots--S0041_before.webp) | [图](frames/screenshots--S0041_after.webp) |
| S0042→S0043 | tap [460, 150] | 村庄任务请求绷带1且当前库存3，完成活动内补给任务 | True | [图](frames/screenshots--S0042_before.webp) | [图](frames/screenshots--S0042_after.webp) |
| S0043→S0044 | tap [415, 150] | 村庄剩手电x1请求，库存8，使用活动内免费手电完成任务 | True | [图](frames/screenshots--S0043_before.webp) | [图](frames/screenshots--S0043_after.webp) |
| S0044→S0045 | tap [770, 185] | 区域A总进度24/25，村庄已9/9，飞往最后山地救援点以争取区域通关 | True | [图](frames/screenshots--S0044_before.webp) | [图](frames/screenshots--S0044_after.webp) |
| S0045→S0046 | tap [690, 165] | 山地有锤巨石入口，复用已验证的零锤击免费结算分支，不消耗账号宝石 | True | [图](frames/screenshots--S0045_before.webp) | [图](frames/screenshots--S0045_after.webp) |
| S0046→S0047 | tap [448, 599] | 山地巨石同样只走零锤击结算，纸飞机宝石20不消耗 | True | [图](frames/screenshots--S0045_after.webp) | [图](frames/screenshots--S0046_after.webp) |
| S0047→S0048 | tap [690, 165] | 山地新任务为绷带1且库存2，不额外飞行即可增加救援收益 | True | [图](frames/screenshots--S0047_before.webp) | [图](frames/screenshots--S0047_after.webp) |
| S0048→S0049 | tap [496, 613] | 区域A达30/25，山地和树林仅缺夹爪且库存0，转下个区域继续免费救援 | True | [图](frames/screenshots--S0048_before.webp) | [图](frames/screenshots--S0048_after.webp) |
| S0049→S0050 | tap [780, 200] | 新区域准备页普通背包免费3/3，先开右上未锁包 | True | [图](frames/screenshots--S0049_before.webp) | [图](frames/screenshots--S0049_after.webp) |
| S0050→S0051 | tap [400, 375] | 新区域准备页普通背包免费2/3，开中排未锁包 | True | [图](frames/screenshots--S0050_before.webp) | [图](frames/screenshots--S0050_after.webp) |
| S0051→S0052 | tap [400, 550] | 普通背包仅剩1次，开启下排中间未锁包 | True | [图](frames/screenshots--S0051_before.webp) | [图](frames/screenshots--S0051_after.webp) |
| S0052→S0053 | tap [210, 375] | 新区域仅剩免费加锁背包1/1，开启左中锁包，绝不额外开普通包 | True | [图](frames/screenshots--S0052_before.webp) | [图](frames/screenshots--S0052_after.webp) |
| S0053→S0054 | tap [1071, 660] | 本区域4个免费背包已用尽，补给4/3/5，进入飞机检修页 | True | [图](frames/screenshots--S0053_before.webp) | [图](frames/screenshots--S0053_after.webp) |
| S0054→S0055 | tap [460, 360] | 区域B当前机头是普通扳手，开始免费检修；动态扳手模板未命中已交回Agent | True | [图](frames/screenshots--S0054_before.webp) | [图](frames/screenshots--S0054_after.webp) |
| S0055→S0056 | tap [565, 460] | B机头检修进度5变15，点击左下普通扳手 | True | [图](frames/screenshots--S0055_before.webp) | [图](frames/screenshots--S0055_after.webp) |
| S0056→S0057 | tap [800, 225] | 区域B进度25，右上仍是无价签普通扳手 | True | [图](frames/screenshots--S0056_before.webp) | [图](frames/screenshots--S0056_after.webp) |
| S0057→S0058 | tap [675, 340] | 区域B35/100，点击中央仍存在的普通扳手 | True | [图](frames/screenshots--S0057_before.webp) | [图](frames/screenshots--S0057_after.webp) |
| S0058→S0059 | tap [780, 460] | 区域B45/100，点击最后机翼普通扳手达到免费检修55 | True | [图](frames/screenshots--S0058_before.webp) | [图](frames/screenshots--S0058_after.webp) |
| S0059→ | shot  |  | True | — | — |
| S0059→S0060 | tap [674, 383] | 第五个普通扳手打开免费指针检修小游戏，点击中央表盘验证交互，避开上方精修价签 | True | [图](frames/screenshots--S0059_before.webp) | [图](frames/screenshots--S0059_after.webp) |
| S0060→S0061 | tap [674, 383] | 免费指针检修已完成第1次，继续第2次中央表盘点击，不点精修 | True | [图](frames/screenshots--S0060_before.webp) | [图](frames/screenshots--S0060_after.webp) |
| S0061→ | tap  | 文案命中红线词「修复」，拒绝执行 | False | — | — |
| S0061→S0062 | tap [674, 383] | 当前弹窗计数2/3，完成免费中央表盘第3次，不点带价签的上方按钮 | True | [图](frames/screenshots--S0061_before.webp) | [图](frames/screenshots--S0061_after.webp) |
| S0062→ | shot  |  | True | — | — |
| S0062→S0063 | tap [1139, 660] | 区域B表盘结束且当前耐久50已达出发条件，进入地图 | True | [图](frames/screenshots--S0062_before.webp) | [图](frames/screenshots--S0062_after.webp) |
| S0063→S0064 | tap [580, 435] | 区域B有5处救援，先选最近的南部桥边哭脸，耐久50 | True | [图](frames/screenshots--S0063_before.webp) | [图](frames/screenshots--S0063_after.webp) |
| S0064→S0065 | tap [580, 415] | 桥边请求绷带1且库存4，先用免费活动补给 | True | [图](frames/screenshots--S0064_before.webp) | [图](frames/screenshots--S0064_after.webp) |
| S0065→S0066 | tap [580, 415] | 桥边新请求手电1，当前库存3，使用免费补给 | True | [图](frames/screenshots--S0065_before.webp) | [图](frames/screenshots--S0065_after.webp) |
| S0066→S0067 | tap [535, 415] | 桥边6/9剩纸飞机小游戏入口，进入取证免费玩法 | True | [图](frames/screenshots--S0066_before.webp) | [图](frames/screenshots--S0066_after.webp) |
| S0067→ | shot  |  | True | — | — |
| S0067→S0068 | tap [1240, 40] | 纸飞机页两种获取均需账号宝石20或付费12，未见免费入口，零兑换退出 | True | [图](frames/screenshots--S0067_before.webp) | [图](frames/screenshots--S0067_after.webp) |
| S0068→S0069 | tap [680, 285] | 桥边已9/9，按B地图最短路线前往右侧石门哭脸，现有补给3/2/5 | True | [图](frames/screenshots--S0068_before.webp) | [图](frames/screenshots--S0068_after.webp) |
| S0069→S0070 | tap [695, 270] | B石门请求绷带1，库存3，完成免费补给任务 | True | [图](frames/screenshots--S0069_before.webp) | [图](frames/screenshots--S0069_after.webp) |
| S0070→S0071 | tap [650, 250] | 石门4/9剩手电1且库存2，完成该救援点 | True | [图](frames/screenshots--S0070_before.webp) | [图](frames/screenshots--S0070_after.webp) |
| S0071→S0072 | tap [560, 280] | B石门9/9已完成，飞往相邻中央哭脸，继续短路径救援 | True | [图](frames/screenshots--S0071_before.webp) | [图](frames/screenshots--S0071_after.webp) |
| S0072→S0073 | tap [565, 270] | B中央请求绷带1，库存2，使用免费活动补给 | True | [图](frames/screenshots--S0072_before.webp) | [图](frames/screenshots--S0072_after.webp) |
| S0073→S0074 | tap [520, 280] | B中央4/9剩夹爪1，库存5，完成免费请求 | True | [图](frames/screenshots--S0073_before.webp) | [图](frames/screenshots--S0073_after.webp) |
| S0074→S0075 | tap [430, 190] | 区域B已27/35，三个点圆满，前往邻近村庄争取免费达到区域门槛 | True | [图](frames/screenshots--S0074_before.webp) | [图](frames/screenshots--S0074_after.webp) |
| S0075→S0076 | tap [350, 185] | B村庄请求绷带1，库存正好1，使用本区最后免费绷带 | True | [图](frames/screenshots--S0075_before.webp) | [图](frames/screenshots--S0075_after.webp) |
| S0076→S0077 | tap [437, 185] | 村庄3/9，夹爪库存4，完成夹爪1请求 | True | [图](frames/screenshots--S0076_before.webp) | [图](frames/screenshots--S0076_after.webp) |
| S0077→S0078 | tap [390, 185] | 村庄6/9仅剩手电1，库存1，完成最后补给任务以达区域通关 | True | [图](frames/screenshots--S0077_before.webp) | [图](frames/screenshots--S0077_after.webp) |
| S0078→S0079 | tap [496, 612] | 区域B36/35已通关，耐久8且零绷带零手电，不为剩余山地额外消耗，前往区域C | True | [图](frames/screenshots--S0078_before.webp) | [图](frames/screenshots--S0078_after.webp) |
| S0079→S0080 | tap [210, 375] | 复用免费背包模块：OCR额度3/1，模板确认plain包 | True | [图](frames/screenshots--S0079_before.webp) | [图](frames/screenshots--S0079_after.webp) |
| S0080→S0081 | tap [210, 550] | 复用免费背包模块：OCR额度2/1，模板确认plain包 | True | [图](frames/screenshots--S0080_before.webp) | [图](frames/screenshots--S0080_after.webp) |
| S0081→S0082 | tap [400, 550] | 复用免费背包模块：OCR额度1/1，模板确认plain包 | True | [图](frames/screenshots--S0081_before.webp) | [图](frames/screenshots--S0081_after.webp) |
| S0082→S0083 | tap [780, 200] | 复用免费背包模块：OCR额度0/1，模板确认locked包 | True | [图](frames/screenshots--S0082_before.webp) | [图](frames/screenshots--S0082_after.webp) |
| S0083→S0084 | tap [1071, 660] | C区免费背包模块4步均通过识别与次数递减验收，进入飞机检修页 | True | [图](frames/screenshots--S0083_before.webp) | [图](frames/screenshots--S0083_after.webp) |
| S0084→S0085 | tap [460, 360] | 区域C机头当前为普通扳手，免费检修；耐久基线8 | True | [图](frames/screenshots--S0084_before.webp) | [图](frames/screenshots--S0084_after.webp) |
| S0085→S0086 | tap [565, 460] | C18/100，左下是普通扳手，执行免费检修 | True | [图](frames/screenshots--S0085_before.webp) | [图](frames/screenshots--S0085_after.webp) |
| S0086→S0087 | tap [800, 225] | C28/100，右上普通扳手仍可免费检修 | True | [图](frames/screenshots--S0086_before.webp) | [图](frames/screenshots--S0086_after.webp) |
| S0087→S0088 | tap [675, 340] | C页标题大小写OCR变体导致门禁停手，现图确认仍为普通中央扳手，改用完整检修页说明门禁 | True | [图](frames/screenshots--S0087_before.webp) | [图](frames/screenshots--S0087_after.webp) |
| S0088→S0089 | tap [803, 266] | C区实际是上方扳手触发的表盘弹窗，中心803266，完成第2次免费操作；此前标题大小写归因作废 | True | [图](frames/screenshots--S0088_before.webp) | [图](frames/screenshots--S0088_after.webp) |
| S0089→S0090 | tap [803, 266] | 上方表盘当前2/3，完成第3次免费操作，记录结束后的真实进度 | True | [图](frames/screenshots--S0089_before.webp) | [图](frames/screenshots--S0089_after.webp) |
| S0090→ | shot  |  | True | — | — |
| S0090→S0091 | tap [675, 340] | 新截图确认表盘已关闭，中央仍是普通扳手，继续免费检修 | True | [图](frames/screenshots--S0090_before.webp) | [图](frames/screenshots--S0090_after.webp) |
| S0091→S0092 | tap [780, 460] | C53/100，最后机翼仍是普通扳手，取得本区剩余免费检修收益 | True | [图](frames/screenshots--S0091_before.webp) | [图](frames/screenshots--S0091_after.webp) |
| S0092→S0093 | tap [1139, 660] | 区域C免费检修63/100，无表盘弹窗，出发进入新地图 | True | [图](frames/screenshots--S0092_before.webp) | [图](frames/screenshots--S0092_after.webp) |
| S0093→S0094 | tap [570, 445] | 区域C有6处救援、目标45笑脸，先到最近南部哭脸，耐久63 | True | [图](frames/screenshots--S0093_before.webp) | [图](frames/screenshots--S0093_after.webp) |
| S0094→S0095 | tap [580, 435] | C南部请求绷带1，库存6，使用免费补给 | True | [图](frames/screenshots--S0094_before.webp) | [图](frames/screenshots--S0094_after.webp) |
| S0095→S0096 | tap [535, 435] | C南部4/9剩手电1，库存4，完成此处免费请求 | True | [图](frames/screenshots--S0095_before.webp) | [图](frames/screenshots--S0095_after.webp) |
| S0096→S0097 | tap [540, 295] | C南部9/9完成，按相邻路线到中央塔楼哭脸，耐久51 | True | [图](frames/screenshots--S0096_before.webp) | [图](frames/screenshots--S0096_after.webp) |
| S0097→S0098 | tap [545, 290] | C中央请求绷带1，当前库存5，推进免费救援 | True | [图](frames/screenshots--S0097_before.webp) | [图](frames/screenshots--S0097_after.webp) |
| S0098→S0099 | tap [500, 290] | C中央5/9剩夹爪1，库存2，完成此救援点 | True | [图](frames/screenshots--S0098_before.webp) | [图](frames/screenshots--S0098_after.webp) |
| S0099→S0100 | tap [375, 335] | C中央圆满，去相邻左侧哭脸救援点，避免跨图来回飞行 | True | [图](frames/screenshots--S0099_before.webp) | [图](frames/screenshots--S0099_after.webp) |
| S0100→S0101 | tap [295, 325] | C左侧请求夹爪1，库存1，使用最后免费夹爪 | True | [图](frames/screenshots--S0100_before.webp) | [图](frames/screenshots--S0100_after.webp) |
| S0101→S0102 | tap [380, 325] | C左侧3/9请求手电1，库存3，完成补给任务 | True | [图](frames/screenshots--S0101_before.webp) | [图](frames/screenshots--S0101_after.webp) |
| S0102→S0103 | tap [330, 325] | C左侧6/9剩红糖图标小游戏，进入识别真实玩法和免费次数 | True | [图](frames/screenshots--S0102_before.webp) | [图](frames/screenshots--S0102_after.webp) |
| S0103→ | shot  |  | True | — | — |
| S0103→S0104 | tap [256, 616] | 红糖图标实际为锦旗好感选择页：左侧固定免费锦旗6，另外两档各有宝石或付费价签，仅收下免费档 | True | [图](frames/screenshots--S0103_before.webp) | [图](frames/screenshots--S0103_after.webp) |
| S0104→S0105 | tap [630, 606] | 收下已获得的固定锦旗6奖励，费用为0 | True | [图](frames/screenshots--S0103_after.webp) | [图](frames/screenshots--S0104_after.webp) |
| S0105→S0106 | tap [390, 190] | C左侧9/9完成，总27/45，沿左侧路线飞往村庄，耐久31 | True | [图](frames/screenshots--S0105_before.webp) | [图](frames/screenshots--S0105_after.webp) |
| S0106→S0107 | tap [405, 180] | C村庄请求手电1，库存2，先完成免费补给任务 | True | [图](frames/screenshots--S0106_before.webp) | [图](frames/screenshots--S0106_after.webp) |
| S0107→S0108 | tap [405, 180] | C村庄新请求绷带1，库存4，使用免费补给 | True | [图](frames/screenshots--S0107_before.webp) | [图](frames/screenshots--S0107_after.webp) |
| S0108→S0109 | tap [405, 180] | 村庄新出现纸飞机入口，复用已验证的只读进入、零兑换退出分支 | True | [图](frames/screenshots--S0108_before.webp) | [图](frames/screenshots--S0108_after.webp) |
| S0109→S0110 | tap [1240, 40] | 纸飞机页依旧无免费获取，保持零兑换退出 | True | [图](frames/screenshots--S0109_before.webp) | [图](frames/screenshots--S0109_after.webp) |
| S0110→S0111 | tap [355, 180] | C村庄6/9剩黄色小锤入口，进入新玩法先读资源和规则 | True | [图](frames/screenshots--S0110_before.webp) | [图](frames/screenshots--S0110_after.webp) |
| S0111→S0112 | swipe [640, 580, 555, 185, 700] | 砸砖玩法有4个免费锤子，按提示把锤子甩向首行第3个金框高亮砖 | True | [图](frames/screenshots--S0111_before.webp) | [图](frames/screenshots--S0111_after.webp) |
| S0112→S0113 | swipe [640, 580, 1015, 185, 700] | 免费锤子剩3，甩向首行第7个金框高亮砖，避开一键扔锤 | True | [图](frames/screenshots--S0112_before.webp) | [图](frames/screenshots--S0112_after.webp) |
| S0113→S0114 | swipe [640, 580, 785, 295, 700] | 免费锤子剩2，甩向第二行第5个金框砖，继续优先高亮目标 | True | [图](frames/screenshots--S0112_after.webp) | [图](frames/screenshots--S0113_after.webp) |
| S0114→S0115 | swipe [640, 580, 670, 405, 700] | 上一锤先击中射线前方普通砖，仅银牌增加；最后1锤改打最近底排第4个无遮挡金框砖 | True | [图](frames/screenshots--S0113_after.webp) | [图](frames/screenshots--S0114_after.webp) |
| S0115→S0116 | tap [1240, 40] | 砸砖免费锤子4次已用尽，额外一次显示付费2，停止并回地图；后两锤落点与目标未完全一致留待复验 | True | [图](frames/screenshots--S0115_before.webp) | [图](frames/screenshots--S0115_after.webp) |
| S0116→S0117 | tap [555, 165] | C已36/45，前往最近北部塔楼哭脸，耐久21，补给3/1/0 | True | [图](frames/screenshots--S0116_before.webp) | [图](frames/screenshots--S0116_after.webp) |
| S0117→S0118 | tap [555, 150] | C北部请求绷带1，库存3，使用免费补给 | True | [图](frames/screenshots--S0117_before.webp) | [图](frames/screenshots--S0117_after.webp) |
| S0118→S0119 | tap [555, 150] | C北部3/9新请求手电1，库存1，使用本区最后手电 | True | [图](frames/screenshots--S0118_before.webp) | [图](frames/screenshots--S0118_after.webp) |
| S0119→ | tap  | 文案命中红线词「开心宝」，拒绝执行 | False | — | — |
| S0119→S0120 | tap [510, 150] | 进入C北部纸飞机任务，查看入口与免费退出 | True | [图](frames/screenshots--S0119_before.webp) | [图](frames/screenshots--S0119_after.webp) |
| S0120→S0121 | tap [1240, 40] | 纸飞机无免费次数，已领取入口救援进度，关闭返回地图 | True | [图](frames/screenshots--S0120_before.webp) | [图](frames/screenshots--S0120_after.webp) |
| S0121→S0122 | tap [715, 165] | C已达45笑脸，尚有11耐久；前往相邻雪山争取免费救援与全点奖励 | True | [图](frames/screenshots--S0121_before.webp) | [图](frames/screenshots--S0121_after.webp) |
| S0122→S0123 | tap [710, 150] | C雪山请求绷带1，库存2，使用本区免费补给 | True | [图](frames/screenshots--S0122_before.webp) | [图](frames/screenshots--S0122_after.webp) |
| S0123→S0124 | tap [494, 612] | C达到50/45，剩手电缺货，按达标按钮前往下一阶段 | True | [图](frames/screenshots--S0123_before.webp) | [图](frames/screenshots--S0123_after.webp) |
| S0124→S0125 | tap [1240, 40] | 临时返回活动主页核实体力扣除与继续入口，保留当前救援进度 | True | [图](frames/screenshots--S0124_before.webp) | [图](frames/screenshots--S0124_after.webp) |
| S0125→S0126 | tap [899, 584] | 结束确认有暂时离开，选择保留进度返回查看体力 | True | [图](frames/screenshots--S0124_after.webp) | [图](frames/screenshots--S0125_after.webp) |
| S0126→S0127 | tap [630, 628] | 恢复已消耗1点体力的同一轮D区准备 | True | [图](frames/screenshots--S0126_before.webp) | [图](frames/screenshots--S0126_after.webp) |
| S0127→S0128 | tap [400, 200] | 复用免费背包模块：OCR额度2/2，模板确认plain包 | True | [图](frames/screenshots--S0124_before.webp) | [图](frames/screenshots--S0127_after.webp) |
| S0128→S0129 | tap [210, 375] | 复用免费背包模块：OCR额度1/2，模板确认plain包 | True | [图](frames/screenshots--S0128_before.webp) | [图](frames/screenshots--S0128_after.webp) |
| S0129→S0130 | tap [210, 550] | 复用免费背包模块：OCR额度0/2，模板确认locked包 | True | [图](frames/screenshots--S0129_before.webp) | [图](frames/screenshots--S0129_after.webp) |
| S0130→S0131 | tap [400, 550] | 复用免费背包模块：OCR额度0/1，模板确认locked包 | True | [图](frames/screenshots--S0130_before.webp) | [图](frames/screenshots--S0130_after.webp) |
| S0131→S0132 | tap [1075, 660] | 当前背包免费额度均耗尽，点击已目视确认出发按钮 | True | [图](frames/screenshots--S0131_before.webp) | [图](frames/screenshots--S0131_after.webp) |
| S0132→S0133 | tap [460, 360] | D准备页左前普通扳手首次检修，残余耐久1 | True | [图](frames/screenshots--S0132_before.webp) | [图](frames/screenshots--S0132_after.webp) |
| S0133→S0134 | tap [565, 460] | D左下普通扳手首次免费检修 | True | [图](frames/screenshots--S0133_before.webp) | [图](frames/screenshots--S0133_after.webp) |
| S0134→S0135 | tap [800, 225] | D上部普通扳手首次免费检修 | True | [图](frames/screenshots--S0134_before.webp) | [图](frames/screenshots--S0134_after.webp) |
| S0135→S0136 | tap [675, 340] | D中央普通扳手首次免费检修 | True | [图](frames/screenshots--S0135_before.webp) | [图](frames/screenshots--S0135_after.webp) |
| S0136→S0137 | tap [674, 383] | D中央扳手延迟出现免费检修0/3浮层；门禁已拦住后台点击，改点指针中心 | True | [图](frames/screenshots--S0136_before.webp) | [图](frames/screenshots--S0136_after.webp) |
| S0137→S0138 | tap [674, 383] | D免费指针检修第2/3次 | True | [图](frames/screenshots--S0137_before.webp) | [图](frames/screenshots--S0137_after.webp) |
| S0138→S0139 | tap [674, 383] | D免费指针检修第3/3次 | True | [图](frames/screenshots--S0138_before.webp) | [图](frames/screenshots--S0138_after.webp) |
