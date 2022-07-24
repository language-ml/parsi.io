import re


def t2s(text, tags):
    s = []
    e = []
    gap = 0
    stack = dict((i, []) for i in tags)
    res = dict((i, []) for i in tags)
    final_text = text

    for i in tags:
        for j in re.finditer(f"<{i}>", text):
            s.append(j)
        for j in re.finditer(f"</{i}>", text):
            e.append(j)
        final_text = final_text.replace(f"<{i}>","")
        final_text = final_text.replace(f"</{i}>","")

    all_tags = s+e
    all_tags = sorted(all_tags, key=lambda x: x.span()[0])
    for i in all_tags:
        if i.group(0)[1]!='/':
            stack[i.group(0)[1:-1]].append((i, gap))
        else:
            start = stack[i.group(0)[2:-1]][-1][0].span()[0] - stack[i.group(0)[2:-1]][-1][1]
            end = i.span()[0] - gap
            res[i.group(0)[2:-1]].append((start, end))
            stack[i.group(0)[2:-1]].pop()

        gap += i.span()[1] - i.span()[0]
    return res, final_text

def s2t(text, tags):
    res = list(text)
    for i in tags.keys():
        for start, end in tags[i]:
            res[start], res[end] = f"<{i}>" + res[start], f"</{i}>" + res[end]
    return "".join(res)
