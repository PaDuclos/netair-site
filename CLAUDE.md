# CLAUDE.md — netair-site

## Modèles à utiliser

| Rôle | Modèle |
|---|---|
| Spécification / conception / décisions d'architecture | **claude-sonnet-4-6** |
| Écriture du code | **claude-haiku-4-5** |
| Revue de code | **claude-sonnet-4-6** |

## Workflow obligatoire

1. **Spec** (Sonnet) — comprendre le besoin, poser les choix techniques, valider avec l'utilisateur
2. **Code** (Haiku) — implémenter uniquement ce qui a été spécifié
3. **Review** (Sonnet) — vérifier la correction, la sécurité, la cohérence avec la charte Netair
4. **Commit + push** — toujours en fin de tâche, sans exception

## Branches

- `main` — stable, chaque merge représente une version cohérente
- Une branche `feature/<sujet>` par fonctionnalité, créée depuis `main`
- PR vers `main` en fin de feature — toujours, même sans version en prod : ça garde un historique lisible

```
git checkout -b feature/<sujet>   # début de tâche
# ... travail ...
git push --set-upstream origin feature/<sujet>
gh pr create ...                  # fin de tâche
```

## Commit & push

À la fin de chaque tâche, sans attendre que l'utilisateur le demande :

```
git add <fichiers modifiés>
git commit -m "<message>"
git push
```

Le message de commit doit être en français, concis, et décrire le pourquoi.

## Stack

- HTML5 / CSS3 / JavaScript vanilla — pas de framework, pas de dépendance externe
- Fichiers autoportants (tout inline : styles + scripts)
- Compatible impression / PDF

## Charte graphique Netair — Precision Blanche

```
--navy:   #0F3261   (texte principal, fond logo)
--teal:   #0897A5   (accent, CTA secondaires)
--blue:   #0070C8   (CTA principal, liens)
--bg:     #F8FAFC   (fond page)
--muted:  #ECF1F4   (fonds de carte, sections)
--border: #E2E8F0   (séparateurs)
--sub:    #4A5E7A   (texte secondaire)
```

- Police : Helvetica Neue / Arial (système)
- Pas de gradients, pas de décorations superflues
- Accent teal : lame verticale gauche de 4px sur les headers
- Labels en uppercase, letter-spacing .08–.12em, font-weight 600–700

## Conventions de code

- Pas de commentaires sauf pour un invariant non-évident
- Pas de framework CSS (Tailwind, Bootstrap, etc.)
- Pas de dépendances npm
- Variables CSS dans `:root` pour toutes les couleurs
- IDs pour les éléments manipulés par JS, classes pour le style
