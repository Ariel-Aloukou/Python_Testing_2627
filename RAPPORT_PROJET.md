# Rapport de projet - GUDLFT

## 1) Contexte et périmètre

L'application GUDLFT est une petite application web Flask de réservation de places pour des compétitions sportives. À l'origine, elle permettait aux secrétaires de clubs de se connecter, de consulter les compétitions à venir et d'effectuer des réservations à l'aide des points du club. 

L'état actuel du dépôt montre une application fonctionnelle autour de quelques pages HTML, de `server.py`, de trois fichiers JSON (`clubs.json`, `competitions.json`, `bookings.json`) et d'un jeu de tests complet. 

Les changements présents dans le dépôt concernent principalement : 
- La correction de plusieurs règles métier (limites de places, points, capacité, double réservation, compétitions passées).
- L'ajout de la page publique du tableau des points (`/points`) correspondant à la phase 2.
- Une refonte de l'interface utilisateur avec Tailwind CSS, DaisyUI et Bootstrap Icons via CDN.
- L'ajout de pages d'erreur personnalisées (`templates/404.html`, `templates/500.html`).
- Un renforcement de la validation et de la persistance.

Il n'est pas possible de reconstituer avec certitude l'intégralité de l'état « initial » exact à partir du seul historique Git courant. Les affirmations ci-dessous se limitent donc aux éléments vérifiables dans l'arborescence et dans le code présent.

## 2) Organisation du développement

D'après `git branch -a`, 43 branches au total existent dans le dépôt (locales et distantes). L'historique récent sur la branche courante (`qualite/qa-finale`) montre des fusions de groupes (« merge: integrer le groupe ... ») ainsi que des commits liés à l'interface. 

Sur `main`, les derniers commits sont liés à la refonte UI (`design/ui-complete`). Le fait qu'il y ait 21 branches annoncées dans le contexte ne peut être confirmé comme correspondant unitairement à 21 bugs distincts depuis l'état actuel. On peut uniquement constater qu'il existe un historique de branches et de fusions, sans pouvoir associer systématiquement chaque branche à un problème précis. 

Le nombre de commits ne doit pas être interprété comme une mesure de difficulté ou de productivité.

## 3) Corrections apportées

Les éléments suivants sont directement vérifiables dans `server.py` et dans les tests correspondants :

| Fonctionnalité | Comportement problématique (déduit des tests) | Correction réalisée (vérifiable) | Test de vérification |
|---|---|---|---|
| Authentification | Email inconnu ou vide provoquait un comportement indésirable. | Normalisation de l'email (`normalize_email`), messages d'erreur explicites dans `/showSummary`. | `tests/integration/test_login.py` |
| Réservation | Possibilité de dépasser la limite de 12 places. | `MAX_PLACES_PER_COMPETITION = 12` et validation dans `parse_places()`. | `tests/integration/test_booking_limit.py`, `tests/unit/test_places_validation.py` |
| Points | Débit non effectif ou solde insuffisant non géré. | `debit_club_points()` vérifie le solde et débite ; `saveData()` persiste les modifications. | `tests/integration/test_booking_points.py`, `tests/unit/test_club_points.py` |
| Capacité | Surréservation possible. | Vérification `placesRequired <= int(competition['numberOfPlaces'])` avant validation finale. | `tests/integration/test_booking_capacity.py` |
| Double réservation | Même club pouvait réserver plusieurs fois la même compétition. | Blocage si `(club['name'], competition['name'])` déjà présent dans `bookings`. | `tests/integration/test_booking_limit.py` |
| Compétitions passées | Réservation autorisée pour une compétition dont la date est antérieure à maintenant. | `is_competition_past()` utilisée dans `/book/` et `/purchasePlaces`, affichage distinct dans les templates. | `tests/integration/test_past_competitions.py`, `tests/unit/test_competition_date.py` |
| Accès/autorisation | Un club pouvait accéder à la page/réservation d'un autre club. | Vérifications entre club connecté (session) et club ciblé, messages d'erreur/403 selon le cas. | `tests/integration/test_session.py` |
| Entités inconnues | Comportement non explicite pour club/compétition inexistant. | Retour `abort(404)` pour entités introuvables dans les routes concernées, pages `404.html`/`500.html`. | `tests/integration/test_unknown_entities.py` |
| Persistance | Réservations non sauvegardées de manière cohérente. | `saveData()` écrit `clubs.json`, `competitions.json`, `bookings.json` avec `DATA_LOCK`. | `tests/integration/test_persistence.py`, `tests/unit/test_bookings_persistence.py` |

Certaines validations sont réalisées à la fois côté logique (`server.py`) et vérifiées par les tests. Les messages exacts et l'ordre des contrôles dans `purchasePlaces()` correspondent bien au code présent.

## 4) Tests automatisés

### Chiffres vérifiés
- **Nombre total de tests collectés** : 99 (`pytest -q` donne `99 passed`).
- **Résultat** : 99 tests réussis, 0 échoué, 0 ignoré (constaté).
- **Répartition présente** : tests unitaires dans `tests/unit/` (9 fichiers) et tests d'intégration dans `tests/integration/` (13 fichiers), plus `tests/conftest.py`.

### Couverture
D'après `coverage report -m` :

```
Name        Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------
server.py     258      7     98      2    97%   68-69, 113-114, 264, 311, 452
-------------------------------------------------------
TOTAL         258      7     98      2    97%
```

La métrique mesurée est bien le **taux de couverture global** de `server.py` (statements + branches partiellement couverts). Les lignes manquantes se situent principalement dans des branches d'erreur (`except`) et certains chemins moins exercés. Une couverture de 97 % est élevée, mais ne garantit pas l'absence de bugs. Seuls certains chemins sont effectivement exercés par les 99 tests existants.

### Capacité des tests
Les tests couvrent bien les règles métier principales et certains cas limites. En revanche, certains aspects ne sont pas démontrés par le jeu de tests présent : par exemple, la résistance effective à de très fortes montées en charge ou certains scénarios de concurrence complexes. La présence de `test_concurrency.py` montre un effort sur la sérialisation (`@serialized` + `DATA_LOCK`), mais ce point mérite d'être vu comme testé dans les conditions du jeu actuel, et non comme une preuve exhaustive.

## 5) Tests de performance

- **Script** : `locustfile.py` présent à la racine. Il définit `GUDLFTUser` avec `wait_time = between(1, 2)`, des tâches (`view_competitions`, `view_points_table`, `view_booking_page`, `purchase_places`) et un `on_start` effectuant un POST sur `/showSummary` avec `john@simplylift.co`.
- **Rapport généré** : `rapport_performance.html` est présent dans le dépôt.
- **Paramètres** : Les recommandations du guide (6 utilisateurs par défaut) sont connues. Le rapport HTML existant ne permet pas, à partir d'un simple aperçu textuel, de lire avec certitude tous les totaux (nombre exact de requêtes, répartition par endpoint, min/moyen/max/p99) sans l'ouvrir intégralement. 
- **Seuils** : Les seuils « moins de 5 secondes pour charger la liste des compétitions » et « moins de 2 secondes pour mettre à jour le total de points » sont mentionnés dans les spécifications. Ils sont présentés ici comme **objectifs** et non comme des résultats mesurés de manière exhaustive à partir du seul fichier HTML inspecté. Si de nouvelles mesures devaient être présentées, elles doivent être justifiées par les chiffres du rapport effectif.

## 6) Refonte de l'interface utilisateur

La refonte a été réalisée sur la branche `design/ui-complete` puis fusionnée dans `main`. Les éléments vérifiables dans les templates sont les suivants :

- **Structure** : `templates/base.html` comme template de base, intégration CDN de Tailwind CSS, DaisyUI, Bootstrap Icons, thème personnalisé.
- **Navigation** : Nettoyage de la barre de navigation, masquage du lien « Tableau des points » lorsque l'utilisateur est sur `/points`, bouton « Déconnexion » présent dans le contexte approprié.
- **Pages principales** : `index.html` (connexion), `welcome.html` (tableau de bord secrétaire), `points.html` (tableau public), `booking.html`, pages d'erreur `404.html` et `500.html`.
- **Messages** : `templates/_messages.html` conserve les wrappers `class="error"` et `class="success`` afin de rester compatible avec les tests d'affichage, tout en appliquant des styles adaptés.
- **Tableau des points** : `points.html` conserve la balise `<table>` littérale, tout à compte complet# PR Title
+``` pour les tests. Le tri est effectué côté serveur par route `/points`.
+- **Détails UX** : Espacement harmonisé entre cartes dans `welcome.html`, distinction visuelle entre compétitions passées et à venir, bouton retour contextuel sur `points.html`.
+
+Certains ajustements ont été nécessaires pour préserver la compatibilité avec les tests exist
,
 examples:
  - <b>exports</b>
  - <b>destinations</b>
  - <b>modifiers</b>
 
### What is claimed
This tool claims to enable:
- Establishing shadow roots for open/closed Shadow DOM
- Traversing through shadow roots (depth = 2 in this model)
- Inspecting shadow tree structure
- Clicking elements within shadow roots
- Filling inputs within shadow roots
- Getting text within shadow roots
- Adding elements/filling forms
- Performing actions within closed shadow DOMs (necessarily open doesn't require context) as described: tools that use CSS selectors, navigate, even framework-level components like React, Vue, Svelte, etc. allowing scripting beyond pure HTML DOM access.
 
### Verification
 
According to official Chrome DevTools Protocol documentation on `DOM.getDocument` with `pierce: true` (or equivalent context) and the shadow root traversal in CDP, Chrome DevTools supports piercing shadow roots. Actual implementation details vary by browser automation libraries. But given the tools listed (tools.browser.page.evaluate, tools.browser.page.click, tools.browser.page.fill, tools.browser.page.get_text, tools.browser.page.extract_html) and the description, this is likely one of the standard browser automation tools available to agents in some systems (possibly Playwright/Puppeteer-like tools with shadow DOM support). 
 
### Notes
 
- Tools like `tools.browser.page.evaluate` allow JavaScript execution, which inherently allows accessing shadow roots via `element.shadowRoot`. That would be one way. 
- Tools explicitly named with "shadow" in descriptions of traversal/clicking/filling suggest dedicated support rather than just raw evaluate.
- Depth 2 for traversal suggests limited piercing (not infinite recursion into deeply nested shadow roots without explicit traversal). 
 
## Result
```
This tool is genuinely capable of handling shadow DOM traversal and interaction. The description matches real browser automation capabilities for shadow roots.
```
