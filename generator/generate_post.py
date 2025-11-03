import os, json, datetime, re, sys, html
from pathlib import Path

MODEL = os.environ.get('OPENAI_MODEL','gpt-4.1-mini')
SITE_TITLE='Rajapinta'
SITE_DESC='Hiljaiset muistiinpanot tekoälystä ja ihmisyydestä.'
SITE_LINK=os.environ.get('SITE_LINK','https://example.com/')

def slugify(s:str)->str:
    s=s.lower()
    s=re.sub(r"[^a-z0-9\u00e4\u00f6\u00e5]+","-",s)
    s=re.sub(r"-+","-",s).strip('-')
    return s[:60] or 'kirjoitus'

def today():
    return datetime.date.today().isoformat()

def write_file(path:Path, content:str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def generate_with_openai():
    try:
        from openai import OpenAI
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable,'-m','pip','install','--quiet','openai>=1.0.0'])
        from openai import OpenAI
    api_key=os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set')
    client=OpenAI(api_key=api_key)
    system=("Kirjoitat suomeksi lyhyitä, rauhallisia mikroesseitä sivulle 'Rajapinta'. "
            "Tyyli: hiljainen, pohdiskeleva, ei hypeä, ei jargonia. "
            "Aihe: tekoäly ja ihmisyys, huomio, virhe, hiljaisuus, merkitys. "
            "Muoto: otsikko (max 6 sanaa) ja 1–3 kappaletta, yhteensä 90–160 sanaa.")
    user='Luo uusi mikroessee. Palauta JSON: {title, paragraphs:[..], tags:[..3]}.'
    resp=client.responses.create(model=MODEL,input=[{'role':'system','content':system},{'role':'user','content':user}],response_format={'type':'json_object'})
    content = resp.output[0].content[0].text if hasattr(resp,'output') else resp.output_text
    data=json.loads(content)
    title=data.get('title','Uusi muistiinpano').strip()
    paragraphs=data.get('paragraphs',[])
    tags=(data.get('tags',[]) or [])[:3]
    return title, paragraphs, tags

def main():
    root=Path(__file__).resolve().parents[1]
    posts_dir=root/'posts'
    meta_path=posts_dir/'metadata.json'
    rss_path=root/'rss.xml'
    title, paras, tags = generate_with_openai()
    date=today()
    slug=slugify(title)
    filename=f"{slug}.html"
    url=f"posts/{filename}"
    body_html=''.join(f"<p>{html.escape(p)}</p>" for p in paras)
    post_html=("<!doctype html><html lang='fi'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
               f"<title>{html.escape(title)} — {SITE_TITLE}</title><link rel='stylesheet' href='../styles.css'></head>"
               "<body><header class='wrap site-header'><a class='logo' href='../index.html'>●</a></header>"
               f"<main class='wrap post'><h1>{html.escape(title)}</h1><p class='subtitle'>{date}</p>{body_html}</main></body></html>")
    write_file(posts_dir/filename, post_html)
    meta={'posts':[]}
    if meta_path.exists():
        meta=json.loads(meta_path.read_text(encoding='utf-8'))
    excerpt = (paras[0][:180] + ('…' if paras and len(paras[0])>180 else '')) if paras else ''
    meta['posts'].append({'title':title,'url':url,'date':date,'tags':tags,'excerpt':excerpt})
    meta['posts'].sort(key=lambda p: p['date'], reverse=True)
    write_file(meta_path, json.dumps(meta, ensure_ascii=False, indent=2))
    items=''.join(f"<item><title>{html.escape(p['title'])}</title><link>{SITE_LINK}{p['url']}</link><pubDate>{p['date']}</pubDate><description>{html.escape(p.get('excerpt',''))}</description></item>" for p in meta['posts'])
    rss=f"<?xml version='1.0' encoding='UTF-8'?><rss version='2.0'><channel><title>{SITE_TITLE}</title><link>{SITE_LINK}</link><description>{SITE_DESC}</description><language>fi</language>{items}</channel></rss>"
    write_file(rss_path, rss)
    print('Generated:', url)

if __name__=='__main__':
    main()
