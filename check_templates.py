import django, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_cm.settings')
django.setup()
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist

bad = []
# Scan all template dirs
scan_dirs = ['templates']
for app in ['boutique','services','formations','dashboard','payments','billing',
            'math_cm','progress','accounts','EnglishPrepApp','GermanPrepApp',
            'italian_courses','preparation_tests','annonces_cam','auto_cameroun',
            'immobilier_cameroun','curriculum','content','core']:
    d = os.path.join(app, 'templates')
    if os.path.isdir(d):
        scan_dirs.append(d)

for scan_dir in scan_dirs:
    for root, dirs, files in os.walk(scan_dir):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]
        for f in files:
            if not f.endswith('.html'):
                continue
            full = os.path.join(root, f)
            # Get template name relative to its templates/ dir
            rel = os.path.relpath(full, scan_dir)
            try:
                get_template(rel)
            except TemplateDoesNotExist:
                pass
            except Exception as e:
                msg = str(e)
                if 'TemplateDoesNotExist' not in msg:
                    bad.append((rel, msg[:150]))

# Deduplicate
seen = set()
unique_bad = []
for t, m in bad:
    if t not in seen:
        seen.add(t)
        unique_bad.append((t, m))

if unique_bad:
    for tname, msg in unique_bad:
        print(f'FAIL: {tname}')
        print(f'      {msg}')
        print()
else:
    print('Tous les templates sont OK')
print(f'Total erreurs: {len(unique_bad)}')
