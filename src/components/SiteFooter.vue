<script setup>
import { org } from '../data/site.js'
import snapshot from '../data/snapshot.js'
import character from '../data/character.js'

// __BUILD_AT__ 由 vite.config.js 的 define 注入（构建时刻，非运行时）
const built = typeof __BUILD_AT__ !== 'undefined' ? __BUILD_AT__ : '（开发模式，未注入构建时刻）'
</script>

<template>
  <footer class="foot">
    <div class="wrap inner">
      <p class="line">
        <b>{{ character.name }}</b> · 角色页——
        非官方站点，与米哈游 / HoYoverse 无任何关系。
      </p>
      <p class="line small muted">
        文本与数值取自 <a :href="`https://github.com/${snapshot.upstream}`">{{ snapshot.upstream }}</a>
        （{{ snapshot.branch }} / {{ snapshot.langDir }}，抓取于 {{ snapshot.fetchedAt }}）；
        推导规则与未采信来源见「数据溯源」。
        游戏美术素材版权归米哈游 / HoYoverse 所有，这里仅作资料整理与学习用途。
      </p>
      <p class="line small muted">
        源码：<a :href="`${org.url}/character-template`">personal-website/character-template</a>
        · 组织：<a :href="org.url">{{ org.name }}</a>
        · 站点：<a :href="org.site">ygwill.top</a>
        · 构建：{{ built }} UTC
      </p>
    </div>
  </footer>
</template>

<style scoped>
.foot {
  margin-top: 40px;
  padding: 22px 0 34px;
  border-top: 1px solid var(--line);
  background: linear-gradient(180deg, #070b1a00, #0b1120);
}
.inner { display: grid; gap: 6px; }
.line { margin: 0; }
</style>
