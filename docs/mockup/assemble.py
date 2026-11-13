import base64, re
SP='/tmp/claude-0/-home-user-Betulin/94669c08-8575-53a3-8e4f-1a2c1ecb33e4/scratchpad/'
F='/home/user/Betulin/site/static/fonts/'
b=lambda p: base64.b64encode(open(p,'rb').read()).decode()
t=open(SP+'mock/mock.tpl.html',encoding='utf8').read()
tick='<svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><circle cx="11" cy="11" r="11" fill="#115060"/><path d="M6.5 11.5l3 3 6-6.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def ic(path): return f'<svg width="36" height="36" viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="8" fill="#ade2e1"/><path d="{path}" fill="none" stroke="#115060" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
rep={'__GOLOS_CYR__':b(F+'golos-text-cyrillic.woff2'),'__GOLOS_LAT__':b(F+'golos-text-latin.woff2'),'__MANROPE_CYR__':b(F+'manrope-cyrillic.woff2'),'__MANROPE_LAT__':b(F+'manrope-latin.woff2'),
 '__FRONT__':b(SP+'label/front.webp'),'__LEAF__':b(SP+'label/leaf.webp'),'__TICK__':tick,
 '__I_DOC__':ic('M8 5h6l3 3v11H8z M14 5v3h3 M10 12h5 M10 15h5'),
 '__I_FACTORY__':ic('M5 19V11l4 2V11l4 2V8l6 3v8z M5 19h14'),
 '__I_BOOK__':ic('M6 6h5a2 2 0 0 1 2 2v10a2 2 0 0 0-2-2H6z M18 6h-5 M18 6v10h-5'),
 '__I_TRUCK__':ic('M4 8h9v8H4z M13 11h4l3 3v2h-7z M7 18a1.5 1.5 0 1 0 0-.01 M17 18a1.5 1.5 0 1 0 0-.01')}
for k,v in rep.items(): t=t.replace(k,v)
open(SP+'mock/index.html','w',encoding='utf8').write(t)
print('left:', re.findall(r'__[A-Z_]+__',t), len(t)//1024,'KB')
