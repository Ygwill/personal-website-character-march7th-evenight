<script setup>
import { computed } from 'vue'
import { fillParams } from '../utils/format.js'
import { iconUrl } from '../utils/assets.js'
import { charLink, charLinkLabel, charTags, poemOwners } from '../data/site.js'
const props = defineProps({ char: { type: Object, required: true } })

const poems = computed(() =>
  props.char.skills
    .filter((s) => s.name.includes('献予「'))
    .map((s) => {
      const spark = s.name.match(/献予「(.+?)」之诗/)[1]
      const owner = poemOwners[spark] || ''
      const tag = charTags[owner]
      return { ...s, spark, owner, link: charLink(tag), linkLabel: charLinkLabel(tag) }
    }),
)
</script>

<template>
  <div class="panel">
    <h2 class="panel-title">献予诸火种之诗（{{ poems.length }} 条）</h2>
    <p class="muted small" style="margin-top:0">
      每条「献予某火种」之诗对应一位黄金裔或「记忆」，受诗者标在名字后，可直接跳到她的角色页（还没上线的跳到仓库页）。
    </p>
    <div class="poems">
      <article v-for="p in poems" :key="p.id" class="poem">
        <header>
          <img v-if="iconUrl(p.icon)" class="ic" :src="iconUrl(p.icon)" alt="" />
          <div>
            <h3>{{ p.name }}</h3>
            <p class="who">
              火种<em>「{{ p.spark }}」</em>
              <span>· {{ p.owner }}</span>
              <a v-if="p.link" :href="p.link" class="small">{{ p.linkLabel }}</a>
            </p>
          </div>
        </header>
        <p class="body">{{ fillParams(p.desc, p.levels?.[0]) }}</p>
      </article>
    </div>
  </div>
</template>

<style scoped>
.poems { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px; margin-top: 6px; }
.poem { padding: 14px; border: 1px solid var(--line); border-radius: 12px; background: linear-gradient(180deg, #b79cff0d, transparent); }
header { display: flex; gap: 12px; align-items: flex-start; }
h3 { margin: 0; font-size: .98rem; color: var(--accent-2); }
.ic { width: 32px; height: 32px; border-radius: 8px; object-fit: contain; background: #ffffff0d; flex: none; }
.who { margin: 3px 0 0; font-size: .82rem; color: var(--dim); display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.who em { font-style: normal; color: var(--gold); }
.body { margin: 10px 0 0; font-size: .9rem; white-space: pre-line; }
</style>
