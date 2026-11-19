<script setup>
import { computed } from 'vue'
import { poemNote, unknownFields } from '../data/site.js'
const props = defineProps({ char: { type: Object, required: true } })

const rows = computed(() => [
  ['角色 ID', props.char.id],
  ['名称', props.char.name],
  ['稀有度', '★'.repeat(props.char.rarity)],
  ['命途', props.char.pathName + '（' + props.char.path + '）'],
  ['战斗属性', props.char.elementName + '（' + props.char.element + '）'],
  ['能量上限', props.char.energyMax == null ? '索引里 max_sp 为 null，未采信任何猜测值' : props.char.energyMax],
  ['昵称 / 本名', (props.char.nickname || []).join('、')],
  ['档案条数', props.char.lore.length + ' 条（见「档案」）'],
])

// 「献予X之诗」是德谬歌赋诗那批忆灵技的命名特征，只有昔涟有；栏目与说明都按数据里是否真有这些条目决定
const poems = computed(() => props.char.skills.filter((s) => s.name.includes('献予「')))

// 忆灵：技能类型以 Memosprite 开头的条目（各角色通用）
const memosprite = computed(() => props.char.skills.filter((s) => s.type.startsWith('Memosprite')))
const types = computed(() => {
  const m = new Map()
  for (const s of props.char.skills) m.set(s.typeLabel, (m.get(s.typeLabel) || 0) + 1)
  return [...m.entries()]
})
</script>

<template>
  <div class="grid">
    <div class="panel">
      <h2 class="panel-title">基本信息</h2>
      <table>
        <tbody>
          <tr v-for="r in rows" :key="r[0]">
            <th style="width: 11em">{{ r[0] }}</th>
            <td>{{ r[1] }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="panel">
      <h2 class="panel-title">技能构成</h2>
      <p class="muted small" style="margin-top:0">
        共 {{ props.char.skills.length }} 条技能条目，其中忆灵相关 {{ memosprite.length }} 条。
      </p>
      <ul class="types">
        <li v-for="t in types" :key="t[0]">
          <span>{{ t[0] }}</span><b>{{ t[1] }}</b>
        </li>
      </ul>
      <p v-if="poems.length" class="small muted">
        「献诗」栏目单独列出 {{ poems.length }} 条<em class="tag-poem">「 ◌ 献予某火种 」</em>的忆灵技{{ poemNote ? ' —— ' + poemNote + '。' : '，逐条见「献诗」栏目。' }}
      </p>
    </div>

    <div class="panel warn">
      <h2 class="panel-title">尚未确认（不编造）</h2>
      <dl class="todo">
        <template v-for="u in unknownFields" :key="u[0]">
          <dt>{{ u[0] }}</dt>
          <dd>{{ u[1] }}</dd>
        </template>
      </dl>
    </div>
  </div>
</template>

<style scoped>
.types { list-style: none; margin: 0 0 12px; padding: 0; display: flex; flex-wrap: wrap; gap: 8px; }
.types li { display: flex; gap: 8px; align-items: baseline; padding: 6px 12px; border: 1px solid var(--line); border-radius: 999px; background: #ffffff08; font-size: .86rem; }
.types b { color: var(--accent); }
em { font-style: normal; }
.warn { border-color: #f0c96a33; background: linear-gradient(180deg, #f0c96a0e, var(--panel)); }
.todo { margin: 0; }
.todo dt { color: var(--gold); font-weight: 600; margin-top: 10px; }
.todo dd { margin: 2px 0 0 0; color: var(--dim); font-size: .88rem; }
.todo dt:first-child { margin-top: 0; }
</style>
