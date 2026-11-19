# 长夜月 · 角色页（崩坏：星穹铁道）

解包 ID **1413**，官方 tag `evernight`。骨架与取数流水线来自 `personal-website/character-template`；
数据全部由官方解包索引生成，不在前端手抄文本、不采信百科类站点的内容。
与模板最大的区别：**图片素材随本仓库提交（Git LFS）**。

当前取数规模：技能 11 条、行迹 20 个节点、星魂 6 条、档案文案 2 条。

## 快速开始

```bash
git lfs install
git clone https://git.ygwill.top/personal-website/character-march7th-evenight.git
cd character-march7th-evenight
npm install
npm run dev              # http://127.0.0.1:5177
```

## 数据流

```
bash tools/fetch-data.sh                 抓 Mar-7th/StarRailRes 的 index_new/cn/ 共 11 个 JSON -> tools/raw/
python3 tools/gen.py --id 1413           生成 src/data/character.js + src/data/snapshot.js（索引指纹）
python3 tools/fetch-assets.py --id 1413  按索引 icon 字段拉图 -> src/assets/（立绘缩到 1024 边长并转 WebP）
```

`src/data/character.js` 和 `src/assets/` 下的图都由脚本生成，**不要手改**，改逻辑改 `tools/gen.py`。
页面里每个数字都能回溯到某个索引的某个键，见站内「数据溯源」栏目。
`tools/raw/`、`dist/`、`node_modules/` 不入库。

## 取材口径（写死在这儿，免得日后没人记得）

- 属性算法：`floor(base + step ×(等级-1))`；晋阶档解锁等级 1/20/30/40/50/60/70（自推后逐格核对过）
- 行迹分类靠 id 尾号约定：`101/102/103` 专属、`201..210` 属性、其余是技能强化节点（索引里没有 kind 字段）
- 占位符：`#N[i]` 取整、`[f1]`/`[f2]` 保留 1/2 位小数，紧跟 `%` 时先 ×100
- 技能剔除 `MazeNormal`（大地图挥击，与角色页无关）
- 档案文案只收 `title` 等于角色名的条目，以及标题带【角色名】的专属条目
- 与三月七的关系只引档案原文（「相貌相同，互为表里」），是否同一人官方未明说，不下结论

## 自检 / 构建

```bash
npm run check    # SSR 逐个栏目渲染，undefined / NaN / 关键串缺失会直接列出
npm run build    # base 为相对路径，dist/ 可丢进任意子路径托管
npx vite preview
```

## 还没做的

- 语音文本：上游 `index_new/cn`、`index_min/cn` 各 23 个索引里**都没有语音表**，要做得另找一手来源
- 皮肤：上游没有皮肤表
- 培养材料汇总：数据取得全（成本 = 晋阶 + 行迹，技能等级提升靠行迹节点），暂未做进页面
- 称号 / 实装日期 / 卡池：解包不含，需官方公告，先挂在页内「尚未确认」里

## 声明

非官方站点，仅作资料整理。游戏文本与美术素材版权归米哈游 / HoYoverse 所有。
