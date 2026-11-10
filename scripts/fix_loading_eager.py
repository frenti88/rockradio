with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = '<img src="${imgUrl}" alt="${escapeHtmlStr(track.name)}" loading="lazy">'
replace1 = '<img src="${imgUrl}" alt="${escapeHtmlStr(track.name)}" loading="eager">'

target2 = '<img src="${imgUrl}" alt="${escapeHtmlStr(playlist.name)}" loading="lazy">'
replace2 = '<img src="${imgUrl}" alt="${escapeHtmlStr(playlist.name)}" loading="eager">'

text = text.replace(target1, replace1)
text = text.replace(target2, replace2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated loading to eager!')
