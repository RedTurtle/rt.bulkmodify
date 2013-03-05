# -*- coding: utf-8 -*-

import re

def de_html(txt):
    return txt.replace('<', '&lt;').replace('>', '&gt;')

def text_search(text, regex, flags=0):
    results = []
    pattern = re.compile(regex, flags)
    t_length = len(text)
    pos = 0
    match = pattern.search(text, pos)
    while match:
        result = {}
        start = result['start'] = match.start()
        end = result['end'] = match.end()
        pos = end
        estart = start-7 if start-10>=0 else 0
        eend = end+7 if end+10<t_length else t_length
        result['text'] = '...' + de_html(text[estart:start]) \
                    + '<span class="mark">' \
                    + de_html(text[start:end]) \
                    + '</span>' \
                    + de_html(text[end:eend]) \
                    + '...'
        results.append(result)
        match = pattern.search(text, pos)
    return results


def text_replace(text, regex, repl, flags=0):
    pattern = re.compile(regex, flags)
    replaced = pattern.sub(repl, text)
    return replaced

