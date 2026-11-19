#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Mar-7th/StarRailRes 的官方解包索引生成 src/data/character.js 与 src/data/snapshot.js。

用法：
    bash tools/fetch-data.sh                # 先把索引抓到 tools/raw/
    python3 tools/gen.py --id 1415          # 生成昔涟
    python3 tools/gen.py --id 1413          # 换成别的角色，改一个数字即可

换角色时要动的地方只有两处：
    1. --id      角色 ID
    2. LORE_IDS  档案文案的 description id（不同角色不同，见下面注释）
其余字段全部由索引直出，前端不手抄。
"""
import argparse, datetime, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 档案/背景文案：descriptions.json 里的条目 id。
# 解包索引里没有「角色 -> 文案 id」的反向表，这些 id 是在 descriptions.json 中按角色人工筛出来的；
# 换角色时需要重新筛一遍，筛不出来就留空 —— 宁可少写，也不要张冠李戴。
# 口径：取 title 完全等于角色名的档案条目（同一角色会随剧情有多版），
# 外加标题里带【角色名】的专属条目；纯世界观条目只在确实相关时收。
LORE_IDS = {
    '1407': ['10231', '10262', '10300'],                    # 遐蝶
    '1409': ['10259', '10302'],                             # 风堇
    '1413': ['10287', '10291'],                             # 长夜月
    '1415': ['10280', '10310', '20093', '10283'],           # 昔涟
}

TYPE_LABEL = {
    'Normal': '普攻', 'BPSkill': '战技', 'Ultra': '终结技', 'Talent': '天赋',
    'Maze': '秘技', 'MazeNormal': '大地图攻击', 'MemospriteSkill': '忆灵技',
    'MemospriteTalent': '忆灵天赋',
}
# 不进入正文的技能类型（大地图上的普通挥击，与角色页要讲的东西无关）
SKIP_TYPES = {'MazeNormal'}

RAW_NAMES = ['characters', 'character_skills', 'character_skill_trees', 'character_ranks',
             'character_promotions', 'items', 'descriptions', 'nickname', 'elements',
             'paths', 'properties']

used_flags = set()


def load(raw, name):
    p = os.path.join(raw, name + '.json')
    if not os.path.exists(p):
        sys.exit('缺少索引文件 %s，请先运行 bash tools/fetch-data.sh' % p)
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def clean(text):
    if not text:
        return ''
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    t = re.sub(r'\n{2,}', '\n', t).strip()
    return t


def scan_flags(*texts):
    for t in texts:
        for m in re.finditer(r'#(\d+)\[([a-z0-9]+)\]', t or ''):
            used_flags.add(m.group(2))


def base(name):
    return (name or '').split('/')[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--id', required=True, help='角色 ID，例如 1415')
    ap.add_argument('--raw', default=os.path.join(ROOT, 'tools', 'raw'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'src', 'data', 'character.js'))
    ap.add_argument('--lore', default=None, help='逗号分隔的 descriptions id，覆盖 LORE_IDS')
    args = ap.parse_args()
    cid = args.id

    data = {n: load(args.raw, n) for n in RAW_NAMES}
    chars, sk, tr = data['characters'], data['character_skills'], data['character_skill_trees']
    rk, promotions = data['character_ranks'], data['character_promotions']
    items, desc = data['items'], data['descriptions']
    nick, elements, paths = data['nickname'], data['elements'], data['paths']
    props = data['properties']

    if cid not in chars:
        sys.exit('characters.json 中没有角色 %s' % cid)
    if cid not in promotions:
        sys.exit('character_promotions.json 中没有 %s 的晋阶数据' % cid)
    c = chars[cid]
    pr = promotions[cid]

    # 顺便记下每个图标在上游的完整路径（素材丢了不用猜前缀，
    # 前端找不到本地图时可按这张表回源，fetch-assets.py 也照它下载）。
    icon_paths = {}

    def icon(src):
        n = base(src)
        if n and src:
            icon_paths[n] = src
        return n

    def item(iid):
        v = items.get(str(iid)) or {}
        return {'id': str(iid), 'name': v.get('name') or str(iid), 'icon': icon(v.get('icon'))}

    # ---- 技能 ----
    skills = []
    for sid in c['skills']:
        v = sk.get(str(sid))
        if not v:
            sys.exit('技能缺失 ' + str(sid))
        if v['type'] in SKIP_TYPES:
            continue
        d = {
            'id': str(sid), 'name': v['name'], 'type': v['type'],
            'typeLabel': TYPE_LABEL.get(v['type'], v.get('type_text') or v['type']),
            'maxLevel': v['max_level'],
            'desc': clean(v.get('desc')), 'short': clean(v.get('simple_desc')),
            'levels': v.get('params') or [],
            'icon': icon(v.get('icon')),
        }
        scan_flags(d['desc'])
        skills.append(d)

    # ---- 行迹 ----
    traces = []
    for tid in c['skill_trees']:
        v = tr.get(str(tid))
        if not v:
            sys.exit('行迹缺失 ' + str(tid))
        bonus = []
        for L in (v.get('levels') or []):
            for p in (L.get('properties') or []):
                pv = props.get(p['type']) or {}
                bonus.append({'name': pv.get('name') or p['type'], 'value': p['value'],
                              'raw': p['type'], 'icon': icon(pv.get('icon'))})
        ups = []
        for lu in (v.get('level_up_skills') or []):
            s = sk.get(str(lu['id']))
            ups.append({'id': str(lu['id']), 'name': (s or {}).get('name') or str(lu['id']),
                        'num': lu['num']})
        scan_flags(v.get('desc'))
        t = str(tid)
        # 分类靠 id 尾号约定（解包没有 kind 字段）：
        #   尾号 101/102/103 = 专属行迹，201..210 = 属性行迹，其余 = 忆灵/强化节点
        kind = ('exclusive' if t.endswith(('101', '102', '103'))
                else 'stat' if t.endswith(('201', '202', '203', '204', '205',
                                           '206', '207', '208', '209', '210'))
                else 'boost')
        traces.append({
            'id': t, 'name': v['name'], 'anchor': v.get('anchor'),
            'desc': clean(v.get('desc')), 'params': (v.get('params') or [[]])[0],
            'maxLevel': v['max_level'], 'kind': kind, 'icon': icon(v.get('icon')),
            'bonus': bonus, 'levelUpSkills': ups,
            'minPromotion': min([L.get('promotion', 0) for L in (v.get('levels') or [])] or [0]),
        })

    # ---- 星魂 ----
    eidolons = []
    for rid in c['ranks']:
        v = rk.get(str(rid))
        if not v:
            sys.exit('星魂缺失 ' + str(rid))
        scan_flags(v.get('desc'))
        eidolons.append({
            'rank': v['rank'], 'id': str(rid), 'name': v['name'],
            'desc': clean(v.get('desc')), 'icon': icon(v.get('icon')),
            'cost': [item(m['id'])['name'] for m in (v.get('materials') or [])],
        })

    # ---- 属性档位（晋阶 0..6，解锁等级 1/20/30/40/50/60/70）----
    tier_levels = [1, 20, 30, 40, 50, 60, 70, 80]
    tiers = []
    for i, v in enumerate(pr['values']):
        tiers.append({
            'tier': i, 'level': tier_levels[i] if i < len(tier_levels) else None,
            'hp': v['hp'], 'atk': v['atk'], 'def': v['def'], 'spd': v['spd'],
            'taunt': v['taunt'], 'crit_rate': v['crit_rate'], 'crit_dmg': v['crit_dmg'],
        })

    # ---- 晋阶材料 ----
    asc = []
    for i, st in enumerate(pr['materials']):
        if not st:
            continue
        asc.append({'tier': i, 'items': [dict(item(m['id']), num=m['num']) for m in st]})

    # ---- 档案文案 ----
    lore_ids = args.lore.split(',') if args.lore else LORE_IDS.get(cid, [])
    lore = []
    for lid in lore_ids:
        v = desc.get(lid.strip())
        if v:
            lore.append({'id': lid.strip(), 'title': v['title'], 'text': clean(v['desc'])})

    out = {
        'slug': c['tag'], 'id': c['id'], 'name': c['name'],
        'nickname': nick['characters'].get(c['id']) or [c['name']],
        'rarity': c['rarity'],
        'element': c['element'], 'elementName': (elements.get(c['element']) or {}).get('name'),
        'elementIcon': icon((elements.get(c['element']) or {}).get('icon')),
        'path': c['path'], 'pathName': (paths.get(c['path']) or {}).get('name'),
        'pathIcon': icon((paths.get(c['path']) or {}).get('icon')),
        'energyMax': c['max_sp'],
        'portrait': c['portrait'], 'avatar': c['icon'], 'preview': c['preview'],
        'iconPaths': icon_paths,
        'tiers': tiers, 'ascension': asc, 'skills': skills,
        'traces': traces, 'eidolons': eidolons, 'lore': lore,
    }

    js = ('// 本文件由 tools/gen.py 从 Mar-7th/StarRailRes（分支 master）的官方解包索引生成，请勿手改。\n'
          '// 重新生成：bash tools/fetch-data.sh && python3 tools/gen.py --id %s\n'
          '// 角色：%s（%s）\n' % (cid, out['name'], out['id'])
          + 'export const character = ' + json.dumps(out, ensure_ascii=False, indent=2) + '\n\n'
          + 'export default character\n')
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(js)

    # ---- 数据指纹：记下本次用了哪些索引，页面「数据溯源」直接引用 ----
    files = []
    for n in RAW_NAMES:
        fp = os.path.join(args.raw, n + '.json')
        if not os.path.exists(fp):
            continue
        b = open(fp, 'rb').read()
        files.append({'name': n + '.json', 'bytes': len(b),
                      'sha256': hashlib.sha256(b).hexdigest()[:16]})
    fetched = datetime.datetime.fromtimestamp(
        os.path.getmtime(os.path.join(args.raw, 'characters.json')),
        datetime.timezone.utc).astimezone().isoformat(timespec='seconds')
    snap = {'upstream': 'Mar-7th/StarRailRes',
            'branch': os.environ.get('BRANCH', 'master'),
            'langDir': os.environ.get('LANG_DIR', 'cn'),
            'fetchedAt': fetched, 'charId': cid,
            'generator': 'tools/gen.py', 'files': files}
    snapjs = ('// 本文件由 tools/gen.py 生成：本次取数所用上游索引的指纹，供「数据溯源」栏目引用。\n'
              'export const snapshot = ' + json.dumps(snap, ensure_ascii=False, indent=2) + '\n\n'
              'export default snapshot\n')
    snap_path = os.path.join(os.path.dirname(args.out), 'snapshot.js')
    with open(snap_path, 'w', encoding='utf-8') as f:
        f.write(snapjs)

    print('未识别的占位符格式标记:', sorted(used_flags) or '无')
    print('skills %d traces %d eidolons %d tiers %d asc %d lore %d 图标回源路径 %d 条'
          % (len(skills), len(traces), len(eidolons), len(tiers), len(asc), len(lore),
             len(icon_paths)))
    print('-> %s (%d B)' % (args.out, len(js.encode('utf-8'))))
    print('-> %s (%d B, %d 个索引)' % (snap_path, len(snapjs.encode('utf-8')), len(files)))


if __name__ == '__main__':
    main()
