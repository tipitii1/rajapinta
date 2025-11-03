# Rajapinta v3 — tumma teema + viikottainen AI-julkaisu

Tämä versio on tumma, simppeli ja anonymiteetti edellä. Mukana blogipohja sekä GitHub Actions -workflow,
joka kirjoittaa **kerran viikossa** uuden suomalaisen mikroesseen OpenAI Responses API:lla.

## Käyttöönotto
1) Vie kansion sisältö GitHub-repoon (juureen). Ota **GitHub Pages** käyttöön (tai Netlify).
2) Repo → Settings → **Secrets and variables → Actions** → New repository secret: `OPENAI_API_KEY`.
3) (Valinn.) Repo → Settings → **Variables** → New variable: `SITE_LINK` (esim. `https://rajapinta.fi/`).
4) Workflow `.github/workflows/weekly.yml` ajaa **maanantaisin klo 06:00 UTC** (~08:00 Helsinki). Voit ajaa myös käsin.

## Paikallinen testi
```bash
export OPENAI_API_KEY=sk-...
python generator/generate_post.py
```

## Uusi kirjoitus käsin
- Tee `posts/`-kansioon uusi HTML, lisää tieto `posts/metadata.json`-tiedostoon.
- RSS päivittyy automaattisesti generaattorilla; käsin muokatessa lisää uusi `<item>` myös `rss.xml`iin.

## Yksityisyys
- Ei evästeitä, ei analytiikkaa oletuksena.
- Älä commitoi API-avainta; käytä GitHub Secrets.

Onnea matkaan 🖤
