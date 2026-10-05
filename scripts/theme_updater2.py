import os
import re

directories = ['d:/AIWF PROJECTS/PLACEMENT-PROJECT/frontend/src/pages', 'd:/AIWF PROJECTS/PLACEMENT-PROJECT/frontend/src/components']

replacements = {
    r'(?<!dark:)divide-slate-800/50': 'divide-slate-200 dark:divide-slate-800/50',
    r'(?<!dark:)divide-slate-800': 'divide-slate-200 dark:divide-slate-800',
    r'(?<!dark:)border-slate-300 dark:border-slate-700': 'border-slate-200 dark:border-slate-700',
}

for d in directories:
    for root, _, files in os.walk(d):
        for file in files:
            if file.endswith('.tsx'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original = content
                for pattern, repl in replacements.items():
                    content = re.sub(pattern, repl, content)
                
                if content != original:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {file}")
