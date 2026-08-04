# Temporary script: replace all non-GBK emoji/special chars with GBK-safe equivalents.
import os

repl = {
 'pages/mastery/index/index.js': [
    ("const EMOJI = { english: '\U0001F4D8', math: '\U0001F4D0', chinese: '\U0001F4D6' };",
     "const EMOJI = { english: '英', math: '数', chinese: '语' };"),
    ("emoji: EMOJI[s.key] || '\U0001F4DA'",
     "emoji: EMOJI[s.key] || '·'"),
 ],
 'pages/mastery/index/index.wxml': [
    ("伊菲的学习看板 \U0001F44B", "伊菲的学习看板"),
    ('<view class="subj-arrow">\u203A</view>', '<view class="subj-arrow">></view>'),
 ],
 'pages/mastery/detail/detail.wxml': [
    ('<view class="section-title">\U0001F4CB 现阶段掌握内容</view>',
     '<view class="section-title">现阶段掌握内容</view>'),
    ('<view class="section-title">\U0001F6A8 当前最该攻的一项</view>',
     '<view class="section-title">当前最该攻的一项</view>'),
 ],
 'pages/mastery/report/report.wxml': [
    ('<view class="section-title">\U0001F4DD 详细汇报</view>',
     '<view class="section-title">详细汇报</view>'),
    ('<view class="section-title">\U0001F4CA 评分由来</view>',
     '<view class="section-title">评分由来</view>'),
    ('<view class="section-title">\U0001F50D 具体扣分项（核心失分模式）</view>',
     '<view class="section-title">具体扣分项（核心失分模式）</view>'),
    ('<view class="bd-from">\U0001F4CC {{item.from}}</view>',
     '<view class="bd-from">注：{{item.from}}</view>'),
    ('<view class="section-title">\u2705 已稳定掌握</view>',
     '<view class="section-title">已稳定掌握</view>'),
    ('<text class="chk">\u2713</text>', '<text class="chk">•</text>'),
    ('<view class="section-title">\U0001F3AF 提分建议</view>',
     '<view class="section-title">提分建议</view>'),
 ],
 'pages/tasks/tasks.wxml': [
    ('<view class="intro-title">\U0001F3AF 智能提分练习</view>',
     '<view class="intro-title">智能提分练习</view>'),
    ("{{c.picked ? '\u2713' : ''}}", "{{c.picked ? '\u25CF' : ''}}"),
    ('<view class="step-btn" bindtap="dec">\u2212</view>',
     '<view class="step-btn" bindtap="dec">-</view>'),
    ('<text class="picker-arrow">\u25BE</text>', '<text class="picker-arrow"></text>'),
    ('<view class="empty-emoji">\U0001F4DA</view>', '<view class="empty-emoji"></view>'),
 ],
 'pages/upload/upload.wxml': [
    ('<view class="up-icon">\U0001F4F7</view>', '<view class="up-icon"></view>'),
    ('\U0001F4F7 拍照 / 选图上传', '拍照 / 选图上传'),
    ('<view class="section-title">\U0001F4CB 提交记录</view>',
     '<view class="section-title">提交记录</view>'),
    ('<view class="empty-emoji">\U0001F5BC\uFE0F</view>', '<view class="empty-emoji"></view>'),
 ],
}

for f, pairs in repl.items():
    t = open(f, encoding='utf-8').read()
    orig = t
    for a, b in pairs:
        if a not in t:
            print("  [WARN] not found in %s: %r" % (f, a[:30]))
        t = t.replace(a, b)
    if t != orig:
        open(f, 'w', encoding='utf-8').write(t)
        print("updated", f)
    else:
        print("no change", f)

# Strip any stray U+FE0F variation selectors across the whole bundle
for root, dirs, fnames in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in {'pipeline', 'docs', 'node_modules', '.git', 'cloudfunctions'}]
    for fn in fnames:
        if fn.endswith(('.js', '.wxml', '.wxss', '.json')):
            p = os.path.join(root, fn)
            t = open(p, encoding='utf-8').read()
            if '\uFE0F' in t:
                open(p, 'w', encoding='utf-8').write(t.replace('\uFE0F', ''))
                print("stripped U+FE0F in", p)
print("DONE")
