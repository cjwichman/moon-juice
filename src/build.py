#!/usr/bin/env python3
"""Inline vendor/matter.min.js into src/game.html and write index.html at the repo root.

Run from anywhere: python3 src/build.py
"""
import os
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
src = open(os.path.join(here, 'game.html')).read()
matter = open(os.path.join(root, 'vendor', 'matter.min.js')).read()
assert '/*__MATTER__*/' in src, 'placeholder missing from src/game.html'
out = src.replace('/*__MATTER__*/', matter)
open(os.path.join(root, 'index.html'), 'w').write(out)
print('wrote index.html (%d bytes)' % len(out))
