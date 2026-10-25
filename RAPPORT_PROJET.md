# Rapport de Projet - GUDLFT

## Contexte
Ce projet vise à développer une version allégée de la plateforme de réservation de places pour les compétitions régionales. Les secrétaires de clubs peuvent s'y connecter pour réserver des places à l'aide des points accumulés par leur club. L'objectif était de corriger l'ensemble des bugs de la phase 1, d'implémenter la phase 2 et d'effectuer une refonte complète de l'interface utilisateur.

## Bugs corrigés - Phase 1
- **Authentification** : Normalisation des emails (espaces, casse), messages d'erreur clairs en cas d'email inconnu ou manquant.
- **Réservations** : Limitation stricte à 12 places maximum par club et par compétition, validation des valeurs saisies.
- **Points** : Débit correct des points lors de l'achat, refus si solde insuffisant et mise à jour persistante.
- **Capacité** : Vérification des places restantes avant validation, refus en cas de surréservation.
- **Double réservation** : Empêchement des réservations multiples du même club sur une même compétition.
- **Compétitions passées** : Désactivation de la réservation et masquage du bouton pour les compétitions terminées.
- **Sessions** : Authentification sécurisée, restriction d'accès aux pages protégées et déconnexion fonctionnelle.
- **Entités inconnues** : Gestion des clubs/compétitions inexistants avec retour vers des pages 404 personnalisées.
- **Persistance** : Sauvegarde et rechargement corrects des réservations dans `bookings.json`.

## Fonctionnalités ajoutées - Phase 2
- **Tableau public des points** : Accessible sans connexion, trié par nombre de points décroissants pour plus de transparence.
- **Navigation améliorée** : Ajout de liens de retour contextuels entre les différentes pages de l'application.

## Refonte de l'interface utilisateur
- **Technologies** : Utilisation exclusive de Tailwind CSS, DaisyUI et Bootstrap Icons via CDN.
- **Design moderne** : Interface épurée, responsive et cohérente sur l'ensemble du site.
- **Internationalisation** : Unification complète en français sur toutes les pages.
- **UX** : Suppression des doublons, clarification des actions, espacement harmonisé entre les cartes.
- **Alertes** : Messages flash et erreurs affichés clairement en rouge tout en restant compatibles avec les tests.
- **Tableau des points** : Mise en forme optimisée avec balise `<table>` conservée pour la compatibilité des tests.

## Tests et couverture
- **Tests automatisés** : 99 tests au total, répartis entre tests unitaires, d'intégration et fonctionnels.
- **Résultat** : 100 % des tests passent avec succès.
- **Couverture de code** : 97 % sur `server.py`, largement au-dessus de l'objectif minimum de 60 %.
- **Qualité** : Code vérifié et validé avec Flake8 sur `server.py` et le dossier `tests/`.

## Tests de performance
- **Outil** : Locust utilisé avec 6 utilisateurs simultanés, conformément aux recommandations.
- **Chargement de la liste des compétitions** : Inférieur à 5 secondes.
- **Mise à jour du total de points** : Inférieure à 2 secondes.
- **Rapports** : `rapport_tests.html`, `rapport_performance.html` et rapport de couverture HTML générés.

## Conclusion
Tous les bugs identifiés ont été corrigés, la phase 2 est entièrement fonctionnelle et l'interface a fait l'objet d'une refonte complète. L'application est stable, performante, bien testée et conforme aux spécifications fonctionnelles. Elle est prête pour la revue sur la branche QA.
