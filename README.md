# news-image

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/tanglangbc/-11-19/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/tanglangbc/-11-19/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

**The World Today** — one page that sums up the world news of Thursday 19 November 2026: the first-ever Trump–Xi–Putin trilateral summit in Shenzhen, Israel's ground operation in central Gaza, three oil tankers ablaze east of the Strait of Hormuz, and Van Gogh's record $190.4M sale.

`main.py` (Python 3.13, standard library only) draws the whole front page from scratch — a hand-made 8×8 bitmap font scaled up for the masthead and headlines, plus a tiny PNG encoder — and writes it to `/output/entry.png` (1024×1024, ~15 KB). No network, no file reads, no randomness: two runs produce byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## The four stories

1. **Trump, Xi, Putin in first three-way summit** — the U.S., Chinese and Russian leaders meet in Shenzhen at the APEC summit, with nuclear arms and two wars on the table. (The Japan Times, SBS, AP)
2. **Israel launches ground operation in central Gaza** — dozens flee as troops advance; aid groups warn of a deepening crisis. (The Japan Times)
3. **Oil tankers ablaze after hitting mines** — three tankers burn east of the Strait of Hormuz, Iran reports. (NDTV)
4. **Van Gogh in $190.4M record sale** — 1890 masterpiece sets a new artist record. (Reuters, The Art Newspaper)

---

<sub>Entered on [make.fun](https://make.fun/?ref=NVRADX&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
