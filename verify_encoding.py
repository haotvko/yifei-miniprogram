import os, subprocess

skip_dirs = {'pipeline', 'docs', 'node_modules', '.git', 'cloudfunctions'}
exts = ('.js', '.wxml', '.wxss', '.json')
bad = {}
for root, dirs, fnames in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for f in fnames:
        if f.endswith(exts):
            p = os.path.join(root, f)
            txt = open(p, 'rb').read().decode('utf-8', errors='replace')
            nb = set()
            for ch in txt:
                try:
                    ch.encode('gbk')
                except Exception:
                    nb.add(ch)
            if nb:
                bad[p] = ''.join(sorted(nb))

if bad:
    for f in sorted(bad):
        print(f, '=> NON-GBK:', repr(bad[f]))
else:
    print('ALL BUNDLE FILES GBK-SAFE')

NODE = 'C:/Users/admin/.workbuddy/binaries/node/versions/22.22.2/node.exe'
for f in ['pages/mastery/index/index.js', 'pages/mastery/report/report.js',
          'reports.js', 'questionbank.js', 'pages/tasks/tasks.js',
          'pages/mastery/detail/detail.js']:
    r = subprocess.run([NODE, '--check', f], capture_output=True, text=True)
    print(('OK ' if r.returncode == 0 else 'FAIL ') + f)
