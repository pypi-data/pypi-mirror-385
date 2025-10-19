import Gempyre
import inspect
import urllib.request
import re

DOX_FUNC="https://mmertama.github.io/Gempyre/functions_func.html"


def list_items(module, context):
    content = {'function':[], 'class':[], 'method':[], 'data':[]}
    for name, obj in inspect.getmembers(module):
        if name.startswith('__') and name.endswith('__'):
            continue
        if inspect.isclass(obj):
            content['class'].append(f"{context}::{name}")
            for k, v in list_items(obj, f"{context}::{name}").items():
                if len(v) > 0:
                    content[k].extend(v)
        elif inspect.isfunction(obj):
            content['function'].append(f"{context}::{name}")
        elif inspect.ismethod(obj):
            content['method'].append(f"{context}::{name}")
        elif inspect.isroutine(obj):
            content['method'].append(f"{context}::{name}")    
        elif inspect.isdatadescriptor(obj): # Properties, etc.
            content['data'].append(f"{context}::{name}")                  
    return content

def main():
    items = list_items(Gempyre, 'Gempyre')
    with urllib.request.urlopen(DOX_FUNC) as fp:
        bytes = fp.read()
        html = bytes.decode("utf8")
    
    functions = []    
    for line in html.split('\n'): 
        m = re.match(r'\s*<li>([a-zA-Z_][a-zA-Z0-9_]*)\(\).*\>([a-zA-Z_:][a-zA-Z0-9_:]*)</a></li>', line)
        if m:
            els = m[2].split('::')
            els.append(m[1]) 
            functions.append(els)
            
    exceptions = set()
    exceptions_map = {}
    with open('exceptions.txt') as f:
        for line in f.readlines():
            m = re.match(r'\s*([a-zA-Z_][^# ]+)', line)
            if m:
                exceptions.add(m[1])
            m = re.match(r'\s*([a-zA-Z_]\s*->\s*([a-zA-Z_])[^# ]+)', line)
            if m:
                exceptions_map[m[1]] = m[2]                    
    
    for func in functions:
        name = '::'.join(func)
        if name not in items['method'] and name not in exceptions and (
            name not in exceptions_map or exceptions_map[name] not in items['method']) and func[-1] != func[-2]: # skip constructors
            print(f"'{name}'")
        

if __name__ == "__main__":
    main()