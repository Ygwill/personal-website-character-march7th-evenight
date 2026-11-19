// 站点级配置：换角色时只需要改 character.js，这个文件按仓库改一次即可
export const org = {
  name: 'personal-website',
  url: 'https://git.ygwill.top/personal-website',
  site: 'https://ygwill.top',
}

// 角色名 -> 解包索引 characters.json 里的 tag（官方英文小写名，跨版本稳定）。
// 这张表是站内跳转的依据，取自上游索引，不是自己起的别名。
export const charTags = {
  大黑塔: 'theherta', 阿格莱雅: 'aglaea', 缇宝: 'tribbie', 万敌: 'mydei',
  那刻夏: 'anaxa', 赛飞儿: 'cipher', 遐蝶: 'castorice', 白厄: 'phainon',
  风堇: 'hyacine', 海瑟音: 'hysilens', 刻律德菈: 'cerydra',
  长夜月: 'evernight', '丹恒·腾荒': 'danhengpt', 昔涟: 'cyrene',
}

// tag -> 本组织内已建成的角色仓库；仓库名可能带前缀（如 evernight 的仓库叫 character-march7th-evenight），
// 所以这里手工对齐一次，跳转前会检查目标仓库是否存在。
export const characterRepos = {
  cyrene: 'character-cyrene',
  hyacine: 'character-hyacine',
  castorice: 'character-castorice',
  evernight: 'character-march7th-evenight',
}

// 「献予X之诗」是昔涟那边德谬歌的专属机制，本角色技能里没有这批条目，故留空
// tag -> 已上线的角色页子域（由 CF 自动部署）。还没上线的角色不要写，链接会自动退回 Gitea 仓库页。
// 注意仓库名与子域名可以不同：evernight 的仓库叫 character-march7th-evenight，子域是 evenight。
export const charSites = {
  cyrene: 'https://cyrene.ygwill.top',
  hyacine: 'https://hyacine.ygwill.top',
  castorice: 'https://castorice.ygwill.top',
  evernight: 'https://evenight.ygwill.top',
}

// 跨角色跳转的地址：优先角色页，其次组织内的角色仓库，都没有就返回空串（组件里 v-if 退化掉链接）
export function charLink(tag) {
  if (!tag) return ''
  if (charSites[tag]) return charSites[tag]
  const repo = characterRepos[tag]
  return repo ? org.url + '/' + repo : ''
}

export function charLinkLabel(tag) {
  return charSites[tag] ? '→ 角色页' : '→ 角色仓库'
}

// 「献诗」栏目存在时的一句话说明，没有这类机制就留空
export const poemNote = ''

export const poemOwners = {}

export const dataSources = [
  {
    label: 'Mar-7th/StarRailRes',
    note: '官方游戏数据的解包索引（分支 master，具体角色与索引指纹见下方快照）',
    url: 'https://github.com/Mar-7th/StarRailRes',
  },
  {
    label: '游戏内文本',
    note: '技能 / 行迹 / 星魂 / 档案描述由 characters、character_skills、character_skill_trees、character_ranks、descriptions 等索引直出',
  },
]

// 解包数据里没有、且没有可靠一手来源的字段，一律挂在这里而不是编造
export const unknownFields = [
  ['与三月七的关系', '档案原文写「与三月七相貌相同，互为表里」「三月七交出自己的记忆陷入沉睡」，是否同一人官方未明说，这里只引原文不下结论'],
  ['数值机制细节', '【忆质】【至暗之谜】的获取与消耗规则需逐条回游戏核对'],
  ['仓库名 / tag', '官方 tag 是 evernight，仓库名却是 character-march7th-evenight（带三月七前缀），站内跳转靠 site.js 的表对齐'],
  ['称号', '解包索引没有称号字段，wiki 上的各种写法未采信'],
  ['实装日期 / 卡池', '解包索引不含 gacha 数据，需以官方公告为准'],
  ['皮肤', '解包上游没有皮肤表（index_new/cn 与 index_min/cn 各 23 个索引里都没有 spinner/voice 一类文件）'],
]
