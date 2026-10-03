#!/usr/bin/env python3
"""Headless level checks for Moon Juice.

Drives the built index.html in headless Chromium through the window.MJ test hooks.
Requires: python3, playwright (with Chromium installed). Run src/build.py first.

  python3 tools/check.py all            verify every hand-built level: no-stroke run must lose,
                                        reference stroke in tools/solutions.json must win on 3 seeds
  python3 tools/check.py gen 16 40      same checks for generated levels 16..40 (reference stroke
                                        comes from MJ.genSolution)
  python3 tools/check.py nodraw         no-stroke outcome for every hand-built level
  python3 tools/check.py try N '[[x,y],[x,y]]'   run one stroke on level N (3 seeds)
  python3 tools/check.py search N 80    random-stroke search on level N
  python3 tools/check.py shot N out.png screenshot of level N at the drawing phase
  python3 tools/check.py play N '[[x,y],[x,y]]' MS out.png   run a stroke for MS ms and screenshot
  python3 tools/check.py js 'expr'      evaluate a JS expression in the page
"""
import os, sys, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'file://' + os.path.join(ROOT, 'index.html')
SOL = os.path.join(ROOT, 'tools', 'solutions.json')
NODRAW = [[14, 90], [26, 90]]   # a 12-unit stub in the top-left corner, far from everything


def open_page(p, w=390, h=780):
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': w, 'height': h})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL)
    pg.wait_for_timeout(400)
    return b, pg, errs


def sim(pg, n, stroke, seed):
    return pg.evaluate('MJ.simStroke(%d, %s, %d)' % (n, json.dumps(stroke), seed))


def fmt(o):
    if o is None or o['st'] == 'invalid':
        return 'INVALID %s' % (o and json.dumps(o['why']))
    return '%s %d/%d ink=%.2f' % (o['st'], o['fill'][0], o['fill'][1], o['ink'])


def check_level(pg, n, stroke, seeds=(1, 2, 3)):
    nd = sim(pg, n, NODRAW, 1)
    res = [sim(pg, n, stroke, s) for s in seeds]
    ok = nd['st'] == 'fail' and all(o['st'] == 'win' for o in res)
    print('%-8s %s  nodraw: %s | stroke: %s' % ('L%d' % n, 'PASS' if ok else 'FAIL', fmt(nd), ' ; '.join(fmt(o) for o in res)), flush=True)
    return ok


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    with sync_playwright() as p:
        b, pg, errs = open_page(p)
        if mode == 'all':
            sols = json.load(open(SOL))
            n_hand = pg.evaluate('MJ.HAND.length')
            bad = []
            for n in range(1, n_hand + 1):
                sk = sols.get(str(n))
                if not sk:
                    print('L%d      no reference stroke' % n); bad.append(n); continue
                if not check_level(pg, n, sk):
                    bad.append(n)
            print('failing:', bad or 'none')
        elif mode == 'gen':
            a, z = int(sys.argv[2]), int(sys.argv[3])
            bad = []
            for n in range(a, z + 1):
                sk = pg.evaluate('MJ.genSolution(%d)' % n)
                if not check_level(pg, n, sk):
                    bad.append(n)
            print('failing:', bad or 'none')
        elif mode == 'nodraw':
            n_hand = pg.evaluate('MJ.HAND.length')
            for n in range(1, n_hand + 1):
                print(n, fmt(sim(pg, n, NODRAW, 1)))
        elif mode == 'try':
            n, sk = int(sys.argv[2]), json.loads(sys.argv[3])
            check_level(pg, n, sk)
        elif mode == 'search':
            n, N = int(sys.argv[2]), int(sys.argv[3])
            print(json.dumps(pg.evaluate('MJ.searchLevel(%d, %d)' % (n, N))))
        elif mode == 'shot':
            n, out = int(sys.argv[2]), sys.argv[3]
            pg.evaluate('MJ.startLevel(%d)' % n)
            pg.wait_for_timeout(300)
            pg.screenshot(path=out)
            print('saved', out)
        elif mode == 'play':
            n, sk, ms, out = int(sys.argv[2]), json.loads(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
            if len(sys.argv) > 6:   # optional JSON of level-field overrides, applied before the run
                pg.evaluate('Object.assign(MJ.HAND[%d], %s)' % (n - 1, sys.argv[6]))
            print(json.dumps(pg.evaluate('MJ.simStroke(%d, %s, 1, %d)' % (n, json.dumps(sk), ms))))
            pg.screenshot(path=out)
        elif mode == 'js':
            print(json.dumps(pg.evaluate(sys.argv[2])))
        if errs:
            print('PAGE ERRORS:', errs[:3])
        b.close()


if __name__ == '__main__':
    main()
