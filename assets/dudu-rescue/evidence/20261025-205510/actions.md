# 逐步动作表

Recorder after 图可能仍是过渡帧；后继 before 图和 decisions/OCR 源图用于验收。

| 状态 | 操作/坐标 | 原因 | 执行 | 前图 | 后图 |
|---|---|---|---|---|---|
| → | session_created  |  |  | — | — |
| S0001→ | shot  |  | True | — | — |
| S0001→S0002 | tap [632, 626] | 接手交接：点继续游戏恢复已有一轮，不新开不扣体力 | True | [图](frames/screenshots--S0001_before.webp) | [图](frames/screenshots--S0001_after.webp) |
| S0002→S0003 | tap [675, 383] | 指针检修浮层：明确指向表盘中心，观察指针是否开始转动 | True | [图](frames/screenshots--S0002_before.webp) | [图](frames/screenshots--S0002_after.webp) |
| S0003→S0004 | tap [675, 383] | 指针检修已 3/3 用尽，点表盘确认收尾/关闭浮层 | True | [图](frames/screenshots--S0003_before.webp) | [图](frames/screenshots--S0003_after.webp) |
| S0004→S0005 | tap [770, 460] | 未知区域检修页：点圆圈内免费扳手（无价签），继续提升检修进度 | True | [图](frames/screenshots--S0004_before.webp) | [图](frames/screenshots--S0004_after.webp) |
| S0005→S0006 | tap [770, 460] | 复验：同一免费扳手位是否还能继续修（上次 51→61） | True | [图](frames/screenshots--S0005_before.webp) | [图](frames/screenshots--S0005_after.webp) |
| S0006→S0007 | tap [1139, 661] | 检修 61/100 已过半，按右下“出发救援”进入未知区域地图 | True | [图](frames/screenshots--S0006_before.webp) | [图](frames/screenshots--S0006_after.webp) |
| S0007→S0008 | tap [165, 105] | 点地图左上“?”查看本区域规则（只读） | True | [图](frames/screenshots--S0007_before.webp) | [图](frames/screenshots--S0007_after.webp) |
| S0008→S0009 | tap [711, 379] | 试验：点地图上一朵云，看是否免费驱散（非付费控件区域） | True | [图](frames/screenshots--S0008_before.webp) | [图](frames/screenshots--S0008_after.webp) |
| S0009→S0010 | tap [782, 438] | 地图哭脸=救援目标，点最近的哭脸飞过去（飞行只耗耐久，不耗体力） | True | [图](frames/screenshots--S0009_before.webp) | [图](frames/screenshots--S0009_after.webp) |
| S0010→S0011 | tap [677, 417] | 当前点上方请求图标=手电x1，用活动库存手电(3)交付，换笑脸 | True | [图](frames/screenshots--S0010_before.webp) | [图](frames/screenshots--S0010_after.webp) |
| S0011→S0012 | tap [699, 400] | 按放大图实测气泡中心(699,400)交付手电x1请求 | True | [图](frames/screenshots--S0011_before.webp) | [图](frames/screenshots--S0011_after.webp) |
| S0012→S0013 | tap [677, 397] | 同一心形气泡现显示金锤（无价签），点开看是免费道具还是奖励 | True | [图](frames/screenshots--S0012_before.webp) | [图](frames/screenshots--S0012_after.webp) |
| S0013→S0014 | tap [695, 412] | 请求变为爪x1，用库存爪(7)交付，继续本处 3/9 进度 | True | [图](frames/screenshots--S0013_before.webp) | [图](frames/screenshots--S0013_after.webp) |
| S0014→S0015 | tap [193, 122] | 点左上“?”读本区域规则（只读，帮助） | True | [图](frames/screenshots--S0014_before.webp) | [图](frames/screenshots--S0014_after.webp) |
| S0015→S0016 | tap [300, 300] | 关闭规则提示横幅（点云朵背景，无控件） | True | [图](frames/screenshots--S0015_before.webp) | [图](frames/screenshots--S0015_after.webp) |
| S0016→S0017 | tap [1000, 300] | 关掉规则横幅（点在横幅空白处，避开云与价位气泡） | True | [图](frames/screenshots--S0016_before.webp) | [图](frames/screenshots--S0016_after.webp) |
| S0017→S0018 | tap [668, 378] | 当前节点上方的金锤气泡，点开看是免费小游戏/奖励还是付费档（无价签） | True | [图](frames/screenshots--S0017_before.webp) | [图](frames/screenshots--S0017_after.webp) |
| S0018→S0019 | tap [510, 318] | 本处已 6/9 过半，点中部另一个哭脸气泡前往下一个救援点 | True | [图](frames/screenshots--S0018_before.webp) | [图](frames/screenshots--S0018_after.webp) |
| S0019→ | tap  | 文案命中红线词「开心宝」，拒绝执行 | False | — | — |
| S0019→S0020 | tap [370, 582] | 余额不足补足弹窗属于付费分支，点左侧取消退出，不购买 | True | [图](frames/screenshots--S0019_before.webp) | [图](frames/screenshots--S0019_after.webp) |
| S0020→S0021 | tap [710, 160] | 雪山上另一处哭脸气泡（未压云、无价位标记），前往该救援点 | True | [图](frames/screenshots--S0020_before.webp) | [图](frames/screenshots--S0020_after.webp) |
| S0021→S0022 | tap [370, 582] | “确定消耗2驱散这片云雾吗”是付费确认，点左侧取消，不驱散 | True | [图](frames/screenshots--S0021_before.webp) | [图](frames/screenshots--S0021_after.webp) |
| S0022→S0023 | tap [1236, 35] | 地图右上红X：先看弹出的是结束本轮对话框再决定 | True | [图](frames/screenshots--S0022_before.webp) | [图](frames/screenshots--S0022_after.webp) |
| S0023→S0024 | tap [899, 584] | 选右侧“暂时离开”保存本轮入口（左侧确认=结束整轮，会丢剩余耐久） | True | [图](frames/screenshots--S0023_before.webp) | [图](frames/screenshots--S0023_after.webp) |
