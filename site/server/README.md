# `server/` — code serveur prêt à activer (hors build)

Ce dossier contient du code serveur **volontairement placé hors de `src/pages/`** : Astro
ne le construit donc pas tant que le site est statique. Il sert à **poser la structure**
d'une fonctionnalité qui ne pourra tourner qu'une fois le site hébergé avec un adaptateur
serveur (après immatriculation / choix d'hébergement).

| Fichier | Rôle | Activation |
|---|---|---|
| `contact-endpoint.ts` | Réception + envoi par email du formulaire de la page `/contact` | Voir l'en-tête du fichier (adaptateur Astro + service d'email + variables d'environnement), puis déplacer vers `src/pages/api/contact.ts`. |

Tant que ce code n'est pas activé, la page `/contact` **retombe automatiquement** sur
l'ouverture de la messagerie du visiteur (mailto) — rien n'est cassé.
