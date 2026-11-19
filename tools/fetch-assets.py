#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 tools/raw/ 索引里引用到的图片素材拉到 src/assets/ 下。

    python3 tools/fetch-assets.py --id 1415 [--force]

前端按 basename 找图（src/utils/assets.js），所以本地文件名 = 上游文件名。
立绘是 2048² 的大 PNG，这里统一缩成 1024² 的 WebP 再入库（LFS 之外也别塞几十 MB）。
"""
import argparse, json, os, re, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'tools', 'raw')
BRANCH = os.environ.get('BRANCH', 'master')
BASE = 'https://raw.githubusercontent.com/Mar-7th/StarRailRes/%s/' % BRANCH

MAX_SIDE = int(os.environ.get('PORTRAIT_MAX', '1024'))


def load(name):
    p = os.path.join(RAW, name)
    if not os.path.exists(p):
        sys.exit('缺少 %s，请先运行 bash tools/fetch-data.sh' % p)
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def fetch(url, dest):
    if os.path.exists(dest):
        return 'skip'
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + '.part'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=180) as r, open(tmp, 'wb') as f:
            f.write(r.read())
    except Exception as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        print('  !! %s <- %s' % (e, url))
        return 'fail'
    os.replace(tmp, dest)
    return 'ok'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--id', required=True, help='角色 ID，例如 1415')
    ap.add_argument('--force', action='store_true', help='已存在的文件也重新下载')
    args = ap.parse_args()
    cid = args.id

    chars = load('characters.json')
    if cid not in chars:
        sys.exit('characters.json 中没有角色 %s' % cid)
    c = chars[cid]
    slug = c['tag']
    skills, trees, ranks = load('character_skills.json'), load('character_skill_trees.json'), load('character_ranks.json')
    promotions, items = load('character_promotions.json'), load('items.json')
    elements, paths = load('elements.json'), load('paths.json')

    jobs = []  # (上游路径, 本地路径)
    A = os.path.join(ROOT, 'src', 'assets')

    def skill_icon(sid, key):
        v = (skills.get(str(sid)) or trees.get(str(sid)) or ranks.get(str(sid)) or {})
        ic = v.get('icon')
        if ic:
            jobs.append((ic, os.path.join(A, 'icons', os.path.basename(ic))))

    for sid in c.get('skills', []):
        skill_icon(sid, 'skill')
    for tid in c.get('skill_trees', []):
        skill_icon(tid, 'tree')
    for rid in c.get('ranks', []):
        skill_icon(rid, 'rank')

    for d in (elements.get(c['element']), paths.get(c['path'])):
        ic = (d or {}).get('icon')
        if ic:
            jobs.append((ic, os.path.join(A, 'icons', os.path.basename(ic))))

    # 行迹强化节点的属性图标（icon/property/IconXxx.png）
    props_idx = load('properties.json')
    for tid in c.get('skill_trees', []):
        v = trees.get(str(tid)) or {}
        for L in (v.get('levels') or []):
            for bp in (L.get('properties') or []):
                ic = (props_idx.get(bp['type']) or {}).get('icon')
                if ic:
                    jobs.append((ic, os.path.join(A, 'icons', os.path.basename(ic))))

    for st in (promotions.get(cid, {}).get('materials') or []):
        for m in (st or []):
            v = items.get(str(m['id'])) or {}
            ic = v.get('icon')
            if ic:
                jobs.append((ic, os.path.join(A, 'items', os.path.basename(ic))))

    # 头像 / 立绘
    if c.get('icon'):
        jobs.append((c['icon'], os.path.join(A, 'char', '%s-avatar.png' % slug)))
    portrait = os.path.join(A, 'char', '%s-portrait.webp' % slug)
    big = os.path.join(A, 'char', '_%s-portrait-full.png' % slug)
    jobs.append(('image/character_portrait/%s.png' % cid, big))

    # 兜底：gen.py 已经把「本页会引用的全部素材」整理进 src/data/character.js 的 iconPaths，
    # 按它补齐最稳（早先只靠逐个索引推导，会漏掉星魂图标 rank*.png 与星魂材料图标 icon/item/*）
    cj = os.path.join(ROOT, 'src', 'data', 'character.js')
    if os.path.exists(cj):
        txt = open(cj, encoding='utf-8').read()
        mm = re.search(r'"iconPaths": (\{.*?\n  \})', txt, re.S)
        if mm:
            for name, up in json.loads(mm.group(1)).items():
                sub = 'items' if up.startswith('icon/item/') else 'icons'
                jobs.append((up, os.path.join(A, sub, name)))
        else:
            print('  !! character.js 里没找到 iconPaths，只用索引推导的结果')

    if args.force:
        import glob
        for f in glob.glob(os.path.join(A, '**', '*'), recursive=True):
            if os.path.isfile(f) and '/char/_' not in f:
                os.remove(f)

    seen, stats = set(), {'ok': 0, 'skip': 0, 'fail': 0}
    for src, dest in jobs:
        if (src, dest) in seen:
            continue
        seen.add((src, dest))
        stats[fetch(BASE + src, dest)] += 1

    # 立绘缩放 + 转 WebP
    if os.path.exists(portrait):
        # 已经有压缩版，原图只是下载中间产物，直接丢掉，别把 3.5MB 塞进仓库
        if os.path.exists(big):
            os.remove(big)
            print('  立绘已存在，丢弃原图 %s' % os.path.basename(big))
    if os.path.exists(big) and not os.path.exists(portrait):
        conv = subprocess.run(
            ['convert', big, '-resize', '%dx%d>' % (MAX_SIDE, MAX_SIDE),
             '-quality', '82', portrait],
            capture_output=True, text=True)
        if conv.returncode == 0:
            os.remove(big)
            print('  立绘 %s -> %s (%d B, 最长边 %d)' % (
                os.path.basename(big), os.path.basename(portrait),
                os.path.getsize(portrait), MAX_SIDE))
        else:
            print('  !! 立绘转码失败（保留原 PNG，请手动压缩）：%s' % conv.stderr.strip()[:200])

    print('%s：%d 张待取，新下载 %d，已存在 %d，失败 %d'
          % (slug, len(seen), stats['ok'], stats['skip'], stats['fail']))
    if stats['fail']:
        sys.exit(1)


if __name__ == '__main__':
    main()
