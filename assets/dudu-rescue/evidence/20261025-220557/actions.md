# 逐步动作表

Recorder after 图可能仍是过渡帧；后继 before 图和 decisions/OCR 源图用于验收。

| 状态 | 操作/坐标 | 原因 | 执行 | 前图 | 后图 |
|---|---|---|---|---|---|
| → | session_created  |  |  | — | — |
| S0001→ | shot  |  | True | — | — |
| S0001→S0002 | tap [52, 195] | 实时图已是主鱼缸，进入精彩活动大厅定位本活动，不触碰其它任务 | True | [图](frames/screenshots--S0001_before.webp) | [图](frames/screenshots--S0001_after.webp) |
| S0002→S0003 | tap [145, 370] | 大厅首卡标题确认嘎嘎队立大功，进入本次授权活动 | True | [图](frames/screenshots--S0002_before.webp) | [图](frames/screenshots--S0002_after.webp) |
| S0003→ | shot  |  | True | — | — |
| S0003→S0004 | tap [632, 628] | MFA已由用户结束，恢复本轮未知区域核对安全路线 | True | [图](frames/screenshots--S0003_before.webp) | [图](frames/screenshots--S0003_after.webp) |
| S0004→S0005 | tap [750, 430] | 当前6/9救援点仍有金锤任务入口，中心750430；与驱散云价签相隔超过100像素，先进入核对免费玩法 | True | [图](frames/screenshots--S0004_before.webp) | [图](frames/screenshots--S0004_after.webp) |
| S0005→S0006 | swipe [640, 580, 440, 405, 700] | 剩4次免费锤子，选择最近底排第2块高亮砖，记录命中与收益 | True | [图](frames/screenshots--S0005_before.webp) | [图](frames/screenshots--S0005_after.webp) |
| S0006→S0007 | swipe [640, 580, 1015, 405, 700] | 免费锤剩3，尝试底排右侧高亮砖；上一锤8到11好感且多个砖消失，轨迹按实际图验收 | True | [图](frames/screenshots--S0006_before.webp) | [图](frames/screenshots--S0006_after.webp) |
| S0007→S0008 | swipe [640, 580, 555, 185, 700] | 剩2次免费锤子，复验首排第3块高亮目标方向，不使用一键按钮 | True | [图](frames/screenshots--S0006_after.webp) | [图](frames/screenshots--S0007_after.webp) |
| S0008→S0009 | swipe [640, 580, 785, 185, 700] | 最后1次免费锤子，朝首排第5块高亮砖，之后遇额外价签即退出 | True | [图](frames/screenshots--S0008_before.webp) | [图](frames/screenshots--S0008_after.webp) |
| S0009→S0010 | tap [630, 605] | 免费锤击已获得随机小鱼x1，弹窗为固定掉落且已入仓库，收下结果 | True | [图](frames/screenshots--S0009_before.webp) | [图](frames/screenshots--S0009_after.webp) |
| S0010→S0011 | tap [1240, 40] | 砸砖4次免费已用完，已得小鱼x1银色勋章2好感8，额外锤有价签，返回地图 | True | [图](frames/screenshots--S0009_after.webp) | [图](frames/screenshots--S0010_after.webp) |
| S0011→S0012 | tap [588, 467] | 当前点9/9完成，选择下方中央哭脸中心588467，离最近付费云边缘约60像素以上，短途飞行 | True | [图](frames/screenshots--S0011_before.webp) | [图](frames/screenshots--S0011_after.webp) |
| S0012→S0013 | tap [590, 440] | 第二救援点机械爪x1请求完全露出且库存6，先处理远离云层的右侧请求 | True | [图](frames/screenshots--S0012_before.webp) | [图](frames/screenshots--S0012_after.webp) |
| S0013→S0014 | tap [565, 445] | 第二点5/9剩手电x1，库存2；请求重排至542440，点其右侧露出部分565445避开左侧云 | True | [图](frames/screenshots--S0013_before.webp) | [图](frames/screenshots--S0013_after.webp) |
| S0014→S0015 | tap [352, 162] | 两个南部点已圆满，优先左上村庄哭脸；其整圈在云层矩形之外，不碰中央被云遮挡的目标 | True | [图](frames/screenshots--S0014_before.webp) | [图](frames/screenshots--S0014_after.webp) |
| S0015→S0016 | tap [280, 160] | 村庄手电x1请求位于左上无云区域，库存1，使用最后手电争取免费收益 | True | [图](frames/screenshots--S0015_before.webp) | [图](frames/screenshots--S0015_after.webp) |
| S0016→S0017 | tap [360, 160] | 村庄绷带x1请求，库存3，落点在云层左侧明确露出的请求圆内 | True | [图](frames/screenshots--S0016_before.webp) | [图](frames/screenshots--S0016_after.webp) |
| S0017→ | shot  |  | True | — | — |
| S0017→S0018 | tap [320, 160] | 村庄6/9剩单独活动勋章图标任务气泡，无通用资产或价签，核对活动内任务后继 | True | [图](frames/screenshots--S0017_before.webp) | [图](frames/screenshots--S0017_after.webp) |
| S0018→S0019 | tap [262, 524] | 三档救援物资赠送页左档明确免费银色勋章1，仅领免费档 | True | [图](frames/screenshots--S0018_before.webp) | [图](frames/screenshots--S0018_after.webp) |
| S0019→S0020 | tap [630, 606] | 收下免费固定银色勋章1，不购买其它两档 | True | [图](frames/screenshots--S0019_before.webp) | [图](frames/screenshots--S0019_after.webp) |
| S0020→S0021 | tap [1240, 40] | 三档任务左免费已Get，关闭该层回地图，不点另两档 | True | [图](frames/screenshots--S0020_before.webp) | [图](frames/screenshots--S0020_after.webp) |
| S0021→S0022 | tap [747, 155] | 村庄已圆满，雪山哭脸右侧747155露出在云图外；避开曾误触的710160区域，尝试安全边缘飞行 | True | [图](frames/screenshots--S0021_before.webp) | [图](frames/screenshots--S0021_after.webp) |
| S0022→S0023 | tap [745, 135] | 雪山机械爪x1，库存5；点击请求右上露出部分745135，避开下方现金云 | True | [图](frames/screenshots--S0022_before.webp) | [图](frames/screenshots--S0022_after.webp) |
| S0023→S0024 | tap [685, 125] | 雪山5/9剩绷带1，库存2；请求重排到675145，点其露出云上方的右上位置685125 | True | [图](frames/screenshots--S0023_before.webp) | [图](frames/screenshots--S0023_after.webp) |
| S0024→S0025 | tap [368, 583] | 雪山请求露出部分仍落在云层实际点击区域，立即取消驱散，停止试探该覆盖区 | True | [图](frames/screenshots--S0024_before.webp) | [图](frames/screenshots--S0024_after.webp) |
| S0025→S0026 | tap [1240, 40] | 本轮未知区32/55，剩余请求和未完成目标受付费云覆盖，用户已授权无安全推进路径时结束本轮，打开结束确认 | True | [图](frames/screenshots--S0025_before.webp) | [图](frames/screenshots--S0025_after.webp) |
| S0026→S0027 | tap [368, 583] | 用户明确要求无法安全推进时彻底结束本轮，选择左确认而非暂时离开，保留已得活动货币进入下一轮 | True | [图](frames/screenshots--S0026_before.webp) | [图](frames/screenshots--S0026_after.webp) |
| S0027→S0028 | tap [630, 627] | 旧轮已彻底结束，首页恢复出发救援且剩3体力，开启下一轮免费救援，预计剩2 | True | [图](frames/screenshots--S0027_before.webp) | [图](frames/screenshots--S0027_after.webp) |
