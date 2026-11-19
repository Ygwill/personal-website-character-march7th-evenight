// 临时脚本：用 SSR 把每个栏目渲染一遍，检查模板里有没有 undefined / NaN / 取值错误。
// 用法：npm run check（= vite build --ssr + node，逐个栏目渲染，看有没有 undefined / NaN / 缺字段）
import fs from 'node:fs'
import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'
import character from '../src/data/character.js'
import snapshot from '../src/data/snapshot.js'
import SiteHeader from '../src/components/SiteHeader.vue'
import CharHero from '../src/components/CharHero.vue'
import InfoPanel from '../src/components/InfoPanel.vue'
import StatsPanel from '../src/components/StatsPanel.vue'
import SkillsPanel from '../src/components/SkillsPanel.vue'
import PoemsPanel from '../src/components/PoemsPanel.vue'
import TracesPanel from '../src/components/TracesPanel.vue'
import EidolonsPanel from '../src/components/EidolonsPanel.vue'
import LorePanel from '../src/components/LorePanel.vue'
import SourcesPanel from '../src/components/SourcesPanel.vue'
import SiteFooter from '../src/components/SiteFooter.vue'

const comps = { SiteHeader, CharHero, InfoPanel, StatsPanel, SkillsPanel, PoemsPanel,
  TracesPanel, EidolonsPanel, LorePanel, SourcesPanel, SiteFooter }

async function main() {
  let total = 0
  const parts = {}
  for (const [cname, C] of Object.entries(comps)) {
    const html = await renderToString(createSSRApp(C, { char: character, snapshot }))
    parts[cname] = html
    fs.writeFileSync('/tmp/ssr-' + cname + '.html', html)
    total += html.length
    const bad = /undefined|NaN|\[object Object\]/.test(html)
    console.log(`${bad ? '!!' : 'ok'} ${cname.padEnd(13)} ${String(html.length).padStart(6)} B`)
    if (bad) console.log('   ', (html.match(/.{50}(undefined|NaN|\[object Object\]).{30}/g) || []).slice(0, 3).join('\n     '))
  }
  const joined = Object.values(parts).join('\n').replace(/<[^>]+>/g, ' ')
  console.log('---- 关键内容抽查 ----')
  // 关键串全部从数据里现取，换角色不必改这个脚本
  const c = character
  const t = c.tiers[c.tiers.length - 1]
  const firstMat = (c.ascension[0] ? c.ascension[0].items : []).find((m) => m.id !== '2')
  const keys = [
    c.name, c.elementName, c.pathName, String(c.id), String(c.rarity),
    c.skills[0] && c.skills[0].name,
    c.skills[c.skills.length - 1] && c.skills[c.skills.length - 1].name,
    (c.traces.find((x) => x.kind === 'exclusive') || {}).name,
    c.eidolons[0] && c.eidolons[0].name,
    firstMat && firstMat.name,
    c.lore[0] && c.lore[0].title,
    // 属性表的算法结果也要落到字面上：末档 80 级的生命、首档暴击率
    String(Math.floor(t.hp.base + t.hp.step * 79)),
    Math.round(c.tiers[0].crit_rate.base * 100) + '%',
    'Mar-7th/StarRailRes', '尚未确认',
  ].filter(Boolean)
  const miss = keys.filter((k) => !joined.includes(k))
  miss.forEach((k) => console.log('✗ 缺失 ' + k))
  console.log('关键串 %d/%d 命中 %s，总渲染字节 %d（素材齐全时渲染里会带 <img>）',
    keys.length - miss.length, keys.length, JSON.stringify(keys), total)
}
main()
