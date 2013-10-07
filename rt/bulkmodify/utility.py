# -*- coding: utf-8 -*-

import re


def de_html(txt):
    return txt.replace('<', '&lt;').replace('>', '&gt;')


def text_search(text, regex, flags=0, preview=False):
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
        if preview:
            result['text'] = '...' + de_html(text[estart:start]) \
                        + '<span class="mark">' \
                        + de_html(text[start:end]) \
                        + '</span>' \
                        + de_html(text[end:eend]) \
                        + '...'
        else:
            result['text'] = text[start:end]
            result['pre_text'] = '...' + de_html(text[estart:start])
            result['post_text'] = de_html(text[end:eend]) + '...'
        results.append(result)
        match = pattern.search(text, pos)
    return results


def text_replace(text, regex, repl, flags=0):
    found = text_search(text, regex, flags=flags)
    pattern = re.compile(regex, flags)
    results = []
    for f in found:
        old = f['text']
        replaced = pattern.sub(repl, old)
        if old!=replaced:
            result = {'old': old, 'new': replaced}
            result['start'] = f['start']
            result['end'] = f['end']
            result['pre_text'] = f['pre_text']
            result['post_text'] = f['post_text']
            results.append(result)
    return results
