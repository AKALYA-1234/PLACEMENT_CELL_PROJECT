import os
import re

directories = ['d:/AIWF PROJECTS/PLACEMENT-PROJECT/frontend/src/pages', 'd:/AIWF PROJECTS/PLACEMENT-PROJECT/frontend/src/components']

replacements = {
    r'(?<!dark:)bg-slate-950': 'bg-slate-50 dark:bg-slate-950',
    r'(?<!dark:)bg-slate-900/80': 'bg-white dark:bg-slate-900/80',
    r'(?<!dark:)bg-slate-900/70': 'bg-white dark:bg-slate-900/70',
    r'(?<!dark:)bg-slate-900/60': 'bg-white/60 dark:bg-slate-900/60',
    r'(?<!dark:)bg-slate-800/80': 'bg-slate-50 dark:bg-slate-800/80',
    r'(?<!dark:)bg-slate-800/60': 'bg-white dark:bg-slate-800/60',
    r'(?<!dark:)bg-slate-800/50': 'bg-slate-100 dark:bg-slate-800/50',
    r'(?<!dark:)bg-slate-800/30': 'bg-slate-100 dark:bg-slate-800/30',
    r'(?<!dark:)bg-slate-800': 'bg-slate-100 dark:bg-slate-800',
    
    r'(?<!dark:)border-slate-800/60': 'border-slate-200 dark:border-slate-800/60',
    r'(?<!dark:)border-slate-800': 'border-slate-200 dark:border-slate-800',
    r'(?<!dark:)border-slate-700/60': 'border-slate-200 dark:border-slate-700/60',
    r'(?<!dark:)border-slate-700/50': 'border-slate-200 dark:border-slate-700/50',
    r'(?<!dark:)border-slate-700/40': 'border-slate-200 dark:border-slate-700/40',
    r'(?<!dark:)border-slate-700': 'border-slate-300 dark:border-slate-700',
    
    r'(?<!dark:)text-white': 'text-slate-900 dark:text-white',
    r'(?<!dark:)text-slate-200': 'text-slate-800 dark:text-slate-200',
    r'(?<!dark:)text-slate-300': 'text-slate-700 dark:text-slate-300',
    r'(?<!dark:)text-slate-400': 'text-slate-500 dark:text-slate-400',
    r'(?<!dark:)text-slate-500': 'text-slate-400 dark:text-slate-500',
    
    r'(?<!dark:)hover:bg-slate-800/30': 'hover:bg-slate-200 dark:hover:bg-slate-800/30',
    r'(?<!dark:)hover:bg-slate-800': 'hover:bg-slate-200 dark:hover:bg-slate-800',
    r'(?<!dark:)hover:bg-slate-700': 'hover:bg-slate-200 dark:hover:bg-slate-700',
    r'(?<!dark:)hover:text-white': 'hover:text-slate-900 dark:hover:text-white',
    r'(?<!dark:)hover:text-slate-300': 'hover:text-slate-700 dark:hover:text-slate-300',
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
