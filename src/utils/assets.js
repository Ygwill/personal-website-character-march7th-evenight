// 资源解析：本仓库的素材在 src/assets/ 下随仓库提交（Git LFS）。
//   1) 本地图优先：角色仓库跑过 python3 tools/fetch-assets.py 并把图提交进 src/assets/ 时，
//      这里的 import.meta.glob 就能命中，站点完全自托管，不依赖外部图床；
//   2) 本地缺图时，只有构建时显式设了 VITE_ICON_CDN 才回源到上游解包仓库的 raw 直链
//      （实测这台服务器到 cdn.jsdelivr.net 被 connection reset，raw.githubusercontent 可用但要 8s，
//       国内浏览器端更不可靠，所以这个开关只给本地预览用）；
//   3) 两者都没有才返回空串，各组件的 v-if 退化成文字占位。
import character from '../data/character.js'

const RAW = import.meta.env.VITE_ICON_CDN
  ? String(import.meta.env.VITE_ICON_CDN).replace(/\/+$/, '') + '/'
  : ''

const icons = import.meta.glob('../assets/icons/*', { eager: true, import: 'default' })
const charImgs = import.meta.glob('../assets/char/*', { eager: true, import: 'default' })
const items = import.meta.glob('../assets/items/*', { eager: true, import: 'default' })

function pick(map, name) {
  if (!name) return ''
  const hit = Object.keys(map).find((p) => p.endsWith('/' + name))
  return hit ? map[hit] : ''
}

// 图标：basename 由 gen.py 从索引直出，同名材料/属性图标也一起找
export function iconUrl(name) {
  const local = pick(icons, name) || pick(items, name)
  if (local) return local
  const src = RAW && character.iconPaths ? character.iconPaths[name] : ''
  return src ? RAW + src : ''
}

// 头像 / 立绘：本地是压缩过的 <slug>-portrait.webp，上游是 image/character_portrait/<id>.png，
// 回源时按后缀对回 characters.json 里的原始路径（立绘原图 3.5MB，只适合临时看一眼效果）
export function charUrl(name) {
  const local = pick(charImgs, name)
  if (local) return local
  if (!RAW) return ''
  const c = character
  if (/-portrait\./.test(name)) return RAW + c.portrait
  if (/-preview\./.test(name)) return RAW + c.preview
  if (/-avatar\./.test(name)) return RAW + c.avatar
  return ''
}
