#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 webcodex-flow 的抖音竖版宣传视频（1080x1920，含中文配音）。"""
import math
import os
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
FONT_PATH = '/System/Library/Fonts/Hiragino Sans GB.ttc'

BG = (11, 14, 19)
INK = (232, 237, 244)
MUTED = (140, 152, 168)
BLUE = (74, 158, 255)
GREEN = (47, 191, 113)
AMBER = (224, 163, 62)
PURPLE = (160, 140, 255)

_font_cache = {}


def F(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        idx = 1 if bold else 0
        try:
            _font_cache[key] = ImageFont.truetype(FONT_PATH, size, index=idx)
        except Exception:
            _font_cache[key] = ImageFont.truetype(FONT_PATH, size)
    return _font_cache[key]


def e_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def seg(t, start, dur):
    """把 [start, start+dur] 映射到 0..1"""
    return max(0.0, min(1.0, (t - start) / dur)) if dur > 0 else 1.0


def base_bg(glow=(60, 120, 220), glow_pos=(0.5, 0.35)):
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(H):
        f = y / H
        r = int(BG[0] + (glow[0] * 0.10) * (1 - f))
        g = int(BG[1] + (glow[1] * 0.10) * (1 - f))
        b = int(BG[2] + (glow[2] * 0.12) * (1 - f))
        d.line([(0, y), (W, y)], fill=(r, g, b))
    for x in range(0, W + 120, 120):
        d.line([(x, 0), (x, H)], fill=(23, 29, 38))
    for y in range(0, H + 120, 120):
        d.line([(0, y), (W, y)], fill=(23, 29, 38))
    return img


def soft_glow(d, cx, cy, r, color, alpha):
    for i in range(28, 0, -1):
        rr = r * i / 28
        a = int(alpha * (1 - i / 28) ** 2)
        d.ellipse([cx - rr, cy - rr * 0.62, cx + rr, cy + rr * 0.62], fill=color + (a,))


def tw(d, text, font):
    b = d.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


def put(d, text, cx, cy, font, fill, alpha=255, dy=0, anchor='mm'):
    if len(fill) == 3:
        fill = fill + (alpha,)
    d.text((cx, cy + dy), text, font=font, fill=fill, anchor=anchor)


def pill(d, cx, cy, w, h, text, font, color, alpha=255, fill_bg=None):
    x0, y0 = cx - w / 2, cy - h / 2
    r = h / 2
    if fill_bg is None:
        d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=r, outline=color + (alpha,), width=3)
    else:
        d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=r, fill=fill_bg + (alpha,))
    d.text((cx, cy), text, font=font, fill=INK + (alpha,), anchor='mm')


def card(d, cx, cy, w, h, title, sub, items, accent, alpha):
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=28,
                        fill=(24, 30, 39, alpha), outline=accent + (alpha,), width=3)
    put(d, title, cx, y0 + 62, F(50, True), INK, alpha)
    put(d, sub, cx, y0 + 120, F(30), accent, alpha)
    yy = y0 + 190
    for it in items:
        put(d, it, cx, yy, F(32), MUTED, alpha)
        yy += 54


# ───────────────────────── 各场景 ─────────────────────────

def s1(t, d, bg):
    put(d, '每个用 Codex 的人都遇到过', W / 2, 640, F(38), MUTED, int(255 * e_out(seg(t, 0.0, 0.6))))
    a = int(255 * e_out(seg(t, 0.35, 0.7)))
    put(d, '额度', W / 2, 800, F(150, True), INK, a)
    put(d, '又用完了', W / 2, 950, F(150, True), BLUE, a)
    a2 = int(255 * e_out(seg(t, 1.2, 0.7)))
    put(d, '5 小时一档，跑两个任务就没了', W / 2, 1090, F(40), MUTED, a2)
    a3 = int(255 * e_out(seg(t, 2.0, 0.7)))
    put(d, '然后你只能干等，或者换别的 AI', W / 2, 1160, F(40), AMBER, a3)


def s2(t, d, bg):
    a = int(255 * e_out(seg(t, 0.0, 0.6)))
    put(d, '但你其实还有', W / 2, 720, F(76, True), MUTED, a)
    a2 = int(255 * e_out(seg(t, 0.4, 0.7)))
    put(d, '一整份额度', W / 2, 870, F(110, True), GREEN, a2)
    a3 = int(255 * e_out(seg(t, 1.1, 0.7)))
    put(d, 'ChatGPT 网页聊天，和 Codex 分开算', W / 2, 1020, F(42), INK, a3)
    a4 = int(255 * e_out(seg(t, 1.9, 0.7)))
    put(d, '它一直在那儿，你一次都没用过', W / 2, 1100, F(38), MUTED, a4)


def s3(t, d, bg):
    a = int(255 * e_out(seg(t, 0.0, 0.6)))
    put(d, '双枪干活', W / 2, 620, F(120, True), INK, a)
    put(d, '贵的额度只花在「想清楚」上', W / 2, 730, F(40), BLUE, a)
    cw, ch, gap = 430, 480, 40
    aL = int(255 * e_out(seg(t, 0.8, 0.7)))
    card(d, W / 2 - cw / 2 - gap / 2, 1120, cw, ch, '桌面 Codex', '强模型 · 贵额度',
         ['写 PRD', '拆任务清单', '最终验收'], BLUE, aL)
    aR = int(255 * e_out(seg(t, 1.5, 0.7)))
    card(d, W / 2 + cw / 2 + gap / 2, 1120, cw, ch, '网页 ChatGPT', '另一份额度',
         ['照着文档写代码', '一次一条', '批量搬砖'], GREEN, aR)
    aB = int(255 * e_out(seg(t, 2.6, 0.7)))
    put(d, '中间靠什么接上？', W / 2, 1480, F(44), AMBER, aB)


def s4(t, d, bg):
    a = int(255 * e_out(seg(t, 0.0, 0.6)))
    put(d, '中间缺的那截', W / 2, 620, F(64, True), MUTED, a)
    put(d, '叫 WebCodex', W / 2, 750, F(110, True), PURPLE, int(255 * e_out(seg(t, 0.35, 0.7))))
    a2 = int(255 * e_out(seg(t, 1.1, 0.7)))
    put(d, '它让网页端直接读写你本机的项目目录', W / 2, 870, F(40), INK, a2)
    a3 = int(255 * e_out(seg(t, 1.8, 0.6)))
    pill(d, W / 2 - 320, 1030, 300, 96, '桌面 Codex', F(38, True), BLUE, a3)
    pill(d, W / 2 + 320, 1030, 300, 96, '网页 ChatGPT', F(38, True), GREEN, a3)
    d.line([(W / 2 - 170, 1030), (W / 2 + 170, 1030)], fill=PURPLE + (a3,), width=4)
    d.rounded_rectangle([W / 2 - 110, 1000, W / 2 + 110, 1060], radius=14, fill=(20, 26, 34, a3),
                        outline=PURPLE + (a3,), width=3)
    put(d, '项目目录', W / 2, 1030, F(34, True), INK, a3)
    a4 = int(255 * e_out(seg(t, 2.7, 0.7)))
    put(d, '两边唯一的桥，是硬盘上的文件', W / 2, 1200, F(42), AMBER, a4)


def s5(t, d, bg):
    a = int(255 * e_out(seg(t, 0.0, 0.6)))
    put(d, '一条命令装好', W / 2, 600, F(100, True), INK, a)
    cmd = 'sh install.sh --workspace "你的项目目录"'
    p = e_out(seg(t, 0.7, 1.2))
    n = int(len(cmd) * p)
    shown = cmd[:n]
    if shown:
        x0, y0, x1, y1 = 90, 760, 990, 920
        d.rounded_rectangle([x0, y0, x1, y1], radius=20, fill=(16, 21, 28, 255),
                            outline=(58, 70, 86, 255), width=2)
        d.text((x0 + 36, (y0 + y1) / 2), shown, font=F(38), fill=GREEN + (255,), anchor='lm')
        if n < len(cmd):
            cw, _ = tw(d, shown, F(38))
            d.rectangle([x0 + 36 + cw + 4, (y0 + y1) / 2 - 22, x0 + 36 + cw + 8, (y0 + y1) / 2 + 22],
                        fill=GREEN + (255,))
    steps = [('①', '建隧道', BLUE), ('②', '建专用 Key', BLUE), ('③', '网页端挂上', BLUE)]
    for i, (num, txt, col) in enumerate(steps):
        ai = int(255 * e_out(seg(t, 1.9 + i * 0.35, 0.5)))
        yy = 1030 + i * 96
        put(d, num, 200, yy, F(46, True), col, ai, anchor='lm')
        put(d, txt, 270, yy, F(42), INK, ai, anchor='lm')
    a5 = int(255 * e_out(seg(t, 3.4, 0.6)))
    put(d, '剩下的跟着做，十分钟搞定', W / 2, 1400, F(40), MUTED, a5)


def s6(t, d, bg):
    a = int(255 * e_out(seg(t, 0.0, 0.6)))
    put(d, '三条纪律', W / 2, 620, F(110, True), INK, a)
    items = [('方案必须落成文件', '对话里说的话，另一边看不到'),
             ('一次只派一条任务', '派一堆，只会得到一堆半成品'),
             ('动手前让它复述理解', '零成本，能挡掉一半返工')]
    for i, (t1, t2) in enumerate(items):
        ai = int(255 * e_out(seg(t, 0.7 + i * 0.5, 0.6)))
        yy = 830 + i * 200
        d.ellipse([150 - 26, yy - 26, 150 + 26, yy + 26], fill=AMBER + (ai,))
        put(d, str(i + 1), 150, yy, F(32, True), (11, 14, 19), ai)
        put(d, t1, 210, yy - 30, F(46, True), INK, ai, anchor='lm')
        put(d, t2, 210, yy + 32, F(32), MUTED, ai, anchor='lm')
    a5 = int(255 * e_out(seg(t, 2.6, 0.7)))
    put(d, '做不到这三条，模型再强也白搭', W / 2, 1520, F(40), AMBER, a5)


def s7(t, d, bg):
    a = int(255 * e_out(seg(t, 0.0, 0.6)))
    put(d, '已经开源了', W / 2, 620, F(110, True), INK, a)
    a2 = int(255 * e_out(seg(t, 0.5, 0.6)))
    pill(d, W / 2, 760, 320, 80, 'MIT · 免费', F(38, True), GREEN, a2)
    a3 = int(255 * e_out(seg(t, 1.1, 0.7)))
    put(d, 'github.com', W / 2, 940, F(44), MUTED, a3)
    put(d, 'xu600cheng / webcodex-flow', W / 2, 1020, F(52, True), BLUE, a3)
    a4 = int(255 * e_out(seg(t, 2.0, 0.7)))
    put(d, '一条命令，装上就能用', W / 2, 1180, F(56, True), INK, a4)
    a5 = int(255 * e_out(seg(t, 2.6, 0.6)))
    put(d, 'webcodex-flow · 双枪干活套件', W / 2, 1300, F(34), MUTED, a5)


SCENES = [
    (3.5, s1, (60, 120, 220), (0.5, 0.35), 'Codex 的额度，又用完了吧？'),
    (3.5, s2, (47, 191, 113), (0.55, 0.4), '其实你还有一整份额度，一次都没动过。'),
    (4.5, s3, (74, 158, 255), (0.5, 0.3), '桌面 Codex 写方案，网页 ChatGPT 写代码。'),
    (4.0, s4, (160, 140, 255), (0.5, 0.45), '中间的通道叫 WebCodex，让网页端直接读写你本机的项目。'),
    (4.5, s5, (47, 191, 113), (0.5, 0.35), '一条命令装好，剩下的三步，跟着做就行。'),
    (4.5, s6, (224, 163, 62), (0.5, 0.4), '记住三条：方案落成文件，一次只派一条，动手前先复述。'),
    (4.5, s7, (74, 158, 255), (0.5, 0.35), '开源免费，仓库地址就在屏幕上，装上就能用。'),
]


def main():
    out = os.path.expanduser('~/Desktop/webcodex-flow-宣传片.mp4')
    tmp = '/tmp/wcpromo'
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)

    # 1) 配音
    print('生成配音...')
    voice_parts = []
    for i, (dur, _, _, _, line) in enumerate(SCENES):
        aiff = f'{tmp}/v{i}.aiff'
        wav = f'{tmp}/v{i}.wav'
        subprocess.run(['say', '-v', 'Tingting', '-o', aiff, line], check=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', aiff, '-af',
                        f'apad,atrim=0:{dur},asetpts=N/SR/TB', '-ar', '44100', '-ac', '2', wav],
                       check=True)
        voice_parts.append(wav)
    lst = f'{tmp}/list.txt'
    with open(lst, 'w') as f:
        for p in voice_parts:
            f.write(f"file '{p}'\n")
    audio = f'{tmp}/voice.wav'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                    '-i', lst, '-c', 'copy', audio], check=True)

    # 2) 画面
    print('渲染画面...')
    total = sum(s[0] for s in SCENES)
    proc = subprocess.Popen(
        ['ffmpeg', '-y', '-loglevel', 'error',
         '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
         '-i', audio,
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '192k', '-shortest',
         '-movflags', '+faststart', out],
        stdin=subprocess.PIPE)

    clock = 0.0
    for idx, (dur, fn, glow, gpos, _) in enumerate(SCENES):
        bg = base_bg(glow, gpos)
        frames = int(round(dur * FPS))
        for f in range(frames):
            t = f / FPS
            frame = bg.copy().convert('RGBA')
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            drift = math.sin((clock + t) * 0.6) * 40
            soft_glow(d, W * gpos[0] + drift, H * gpos[1], 620, glow, 46)
            fn(t, d, bg)
            prog = (clock + t) / total
            d.rectangle([90, H - 60, W - 90, H - 54], fill=(255, 255, 255, 26))
            d.rectangle([90, H - 60, 90 + (W - 180) * prog, H - 54], fill=glow + (230,))
            put(d, 'webcodex-flow', W - 100, 110, F(28), (255, 255, 255), 90, anchor='rm')
            frame = Image.alpha_composite(frame, ov)
            proc.stdin.write(frame.convert('RGB').tobytes())
        clock += dur
        print(f'  场景 {idx + 1}/{len(SCENES)} 完成')

    proc.stdin.close()
    proc.wait()
    print('输出：', out, f'（约 {total:.1f} 秒）')


if __name__ == '__main__':
    main()
