# Site du restaurant Schnock

Site statique de [schnock-restaurant.fr](https://www.schnock-restaurant.fr/), repris à l'identique de l'ancien site Zenchef, avec une page Privatisation en plus.

- Les pages publiées sont à la racine (`index.html`, `menus-carte/`, `photos/`, `privatisation/`, `informations-contact/`, pages légales).
- `_source/` contient le script de génération (`build.py`) et les contenus ajoutés (`src/` : page privatisation, menus de groupe, FAQ, styles et scripts). Ce dossier n'est pas publié.
- Réservations : module Zenchef (restaurant 376115). Formulaires de contact et de devis : FormSubmit vers schnock.resto@gmail.com.

## Langues

Le français reste la langue principale, à la racine. Les versions anglaise, espagnole, italienne, chinoise et japonaise sont dans `en/`, `es/`, `it/`, `zh/` et `ja/`, générées à partir des pages françaises par `_source/i18n.py` :

- `python3 _source/i18n.py build` écrit les pages traduites, le sélecteur de langue, les balises hreflang et le `sitemap.xml`. À relancer après chaque modification d'une page française (après `build.py`).
- Les traductions sont dans `_source/i18n/t-*.json` : une ligne par texte français, `[fr, en, es, it, zh, ja]`. Si un texte français change ou s'ajoute, le build s'arrête et liste les textes manquants ; `python3 _source/i18n.py extract` les écrit dans `_source/i18n/strings.fr.json`.
- `_source/i18n/keep.json` liste les textes identiques dans toutes les langues (noms propres, adresse).
- Les pages légales restent en français. Les formulaires envoient toujours les choix en français, avec un champ `langue` pour répondre au client dans sa langue.
