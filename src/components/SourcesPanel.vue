<script setup>
import { computed } from 'vue'
import snapshot from '../data/snapshot.js'
import { org } from '../data/site.js'
const props = defineProps({ char: { type: Object, required: true } })

// 页面字段 -> 索引文件与字段名。这张表是「人话版」的字段映射，
// 真正的取数逻辑在 tools/gen.py，改数据请改那里。
const fieldMap = [
  ['名称 / 稀有度 / ID / 别名', 'characters.json + nickname.json', 'name、rarity、id、tag'],
  ['战斗属性 / 命途 / 能量上限', 'characters.json + elements.json + paths.json', 'element、path、max_sp（含图标）'],
  ['技能名称、文本、每级数值', 'character_skills.json', 'name、desc、simple_desc、params、max_level'],
  ['行迹（专属 / 属性 / 强化）', 'character_skill_trees.json + properties.json', 'desc、params、levels[].properties、level_up_skills'],
  ['星魂', 'character_ranks.json + items.json', 'name、desc、materials'],
  ['属性档位与晋阶材料', 'character_promotions.json + items.json', 'values[]（base/step）、materials[]'],
  ['档案文案', 'descriptions.json', 'title、desc（id 由 tools/gen.py 的 LORE_IDS 人工筛选）'],
]

// 这些不是索引里的现成字段，而是本页推导/约定的规则，全部写明以便复核
const derived = [
  ['等级属性算法', 'stat = floor(base + step × (等级 − 1))，晋阶档解锁等级 [1,20,30,40,50,60,70]',
   '已用另一位角色的公开属性表逐格核对（Lv20 前后 350/421、Lv80 1319/543/582 一致）'],
  ['文本占位符还原', '#N[i] 取整数、#N[f1] 一位小数、#N[f2] 两位小数；占位符后紧跟 % 时先把原值 ×100',
   '规则从 params 与文本的对应关系反推，生成时会列出未识别的格式标记（当前只有 i / f1 / f2）'],
  ['行迹分类', '解包没有 kind 字段，按行迹 id 尾号判定：101/102/103 = 专属，201–210 = 属性，其余 = 忆灵强化节点',
   '对本角色 20 条行迹逐条核对过；换角色时应抽查，不要盲信'],
  ['技能类型中文名', 'Normal/BPSkill/Ultra/Talent/Maze/MemospriteSkill… → 普攻/战技/终结技/天赋/秘技/忆灵技',
   '映射表在 tools/gen.py 的 TYPE_LABEL，兜底用索引自带的 type_text'],
  ['剔除了什么', 'type = MazeNormal（大地图普通挥击）不入正文，避免技能列表被无意义的条目淹没',
   '如需还原，删掉 gen.py 里的 SKIP_TYPES 即可'],
]

const notTrusted = [
  ['wiki.biligame.com（萌娘百科 SR 站）', '只当作页面结构的参考（栏目划分、表格形态）。内容可被任意编辑，且本角色页面返回的是 WAF 反爬壳（HTTP 567，正文只有一串校验字符），没有采信其中任何数值。'],
  ['百度百科 / 其他二手汇总', '同理，未作为数据来源；出现分歧时以游戏内文本与解包索引为准。'],
]

const kb = (n) => (n / 1024).toFixed(0) + ' KB'
const totalBytes = computed(() => snapshot.files.reduce((s, f) => s + f.bytes, 0))
</script>

<template>
  <div class="grid">
    <div class="panel">
      <h2 class="panel-title">取数快照</h2>
      <ul class="kv">
        <li><span>上游仓库</span><b>{{ snapshot.upstream }}</b><em>官方游戏数据的解包索引</em></li>
        <li><span>分支 / 语言</span><b>{{ snapshot.branch }} · {{ snapshot.langDir }}</b><em>角色 ID {{ snapshot.charId }}（{{ props.char.name }}）</em></li>
        <li><span>抓取时刻</span><b>{{ snapshot.fetchedAt }}</b><em>由 tools/raw/ 的文件时间得出</em></li>
        <li><span>索引体量</span><b>{{ kb(totalBytes) }}</b><em>{{ snapshot.files.length }} 个文件 · 生成器 {{ snapshot.generator }}</em></li>
      </ul>
      <div class="scroll-x">
        <table>
          <thead>
            <tr><th>索引文件</th><th>大小</th><th>SHA-256（前 16 位）</th></tr>
          </thead>
          <tbody>
            <tr v-for="f in snapshot.files" :key="f.name">
              <td><code>{{ f.name }}</code></td>
              <td class="num">{{ kb(f.bytes) }}</td>
              <td><code>{{ f.sha256 }}</code></td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="small muted">
        对上一个版本的数字有疑问时，先比指纹：<code>sha256sum tools/raw/*.json</code>。
        索引会随游戏版本更新，本页所有文本与数值都来自上表这一份快照。
      </p>
    </div>

    <div class="panel scroll-x">
      <h2 class="panel-title">字段来源</h2>
      <table>
        <thead>
          <tr><th>页面字段</th><th>索引文件</th><th>用到的键</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in fieldMap" :key="r[0]">
            <td>{{ r[0] }}</td>
            <td><code>{{ r[1] }}</code></td>
            <td class="small muted">{{ r[2] }}</td>
          </tr>
        </tbody>
      </table>
      <p class="small muted">
        文本一律是索引里的原文，只做换行归一与占位符还原，没有改写措辞。
      </p>
    </div>

    <div class="panel">
      <h2 class="panel-title">本页自行推导的规则 <span class="chip is-warn">非索引直出</span></h2>
      <dl class="derived">
        <template v-for="d in derived" :key="d[0]">
          <dt>{{ d[0] }}</dt>
          <dd>{{ d[1] }}</dd>
          <dd class="how">核对方式：{{ d[2] }}</dd>
        </template>
      </dl>
    </div>

    <div class="panel">
      <h2 class="panel-title">看过但没有采信的来源</h2>
      <ul class="nolist">
        <li v-for="n in notTrusted" :key="n[0]">
          <b>{{ n[0] }}</b>
          <p class="small muted">{{ n[1] }}</p>
        </li>
      </ul>
      <p class="small muted">
        解包索引里没有现成字段、又缺一手出处的条目（称号、实装日期、派系、皮肤等），
        集中在「信息」栏末尾的<b>尚未确认</b>区块列出，不会写成正文结论。
      </p>
    </div>

    <div class="panel">
      <h2 class="panel-title">复现这份数据</h2>
      <pre class="code">bash tools/fetch-data.sh          # 抓 index_new/cn 的 11 个索引到 tools/raw/
python3 tools/gen.py --id {{ props.char.id }}      # 生成 src/data/character.js + snapshot.js
python3 tools/fetch-assets.py --id {{ props.char.id }}  # 拉技能/行迹/星魂/材料图标与立绘</pre>
      <p class="small muted">
        换角色只改 <code>--id</code>，另外在 <code>tools/gen.py</code> 的 <code>LORE_IDS</code> 里重筛档案文案 id。
        素材文件名沿用上游 basename，前端按 basename 匹配（<code>src/utils/assets.js</code>），缺图时该位置自动留空、不会报错。
        仓库地址：<a :href="`${org.url}/${char.slug}`" rel="noreferrer">{{ org.url }}/{{ char.slug }}</a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.kv { list-style: none; margin: 0 0 14px; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; }
.kv li { padding: 10px 12px; border: 1px solid var(--line); border-radius: 12px; background: #ffffff06; }
.kv span { display: block; color: var(--dim); font-size: .78rem; }
.kv b { font-size: 1rem; color: var(--accent); }
.kv em { display: block; font-style: normal; color: var(--dim); font-size: .78rem; }
code { font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; font-size: .84em; color: #cfe6ff; }
.derived { margin: 0; }
.derived dt { color: var(--accent-2); font-weight: 600; margin-top: 12px; }
.derived dd { margin: 2px 0 0; color: var(--text); }
.derived .how { color: var(--dim); font-size: .82rem; }
.nolist { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
.nolist p { margin: 2px 0 0; }
.code {
  margin: 0; padding: 12px 14px; overflow-x: auto;
  background: #05080f; border: 1px solid var(--line); border-radius: 10px;
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  font-size: .82rem; line-height: 1.9; color: #cfe6ff;
}
</style>
