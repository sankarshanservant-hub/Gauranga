#!/bin/bash
# commit+push own files only: save.sh "message"
cd /home/user/Gauranga
F="chaitanya-charitamrita/vcd/new chaitanya-charitamrita/tools chaitanya-charitamrita/PLAN.md chaitanya-charitamrita/GLOSSARY-vcd.md"
git add $F
git commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KGC2T1PiSRGJe48WTtGST9" -- $F
for d in 0 2 4 8 16; do sleep $d; git pull -q --rebase --autostash origin claude/book-translation-tesseract-bengali-yaygag && git push -q -u origin claude/book-translation-tesseract-bengali-yaygag && break; done
git log --oneline | head -1
