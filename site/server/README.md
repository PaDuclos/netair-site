# `server/` — code serveur prêt à activer (hors build)

Ce dossier contient du code serveur **volontairement placé hors de `src/pages/`** : Astro
ne le construit donc pas tant que le site est statique. Il sert à **poser la structure**
d'une fonctionnalité qui ne pourra tourner qu'une fois le site hébergé avec un adaptateur
serveur (après immatriculation / choix d'hébergement).

| Fichier | Rôle | Activation |
|---|---|---|
| `contact-endpoint.ts` | Réception + envoi par email du formulaire de la page `/contact` | Voir l'en-tête du fichier (adaptateur Astro + service d'email + variables d'environnement), puis déplacer vers `src/pages/api/contact.ts`. |

⚠️ **Depuis le 12/10/2026, ce n'est plus ce fichier qui envoie les formulaires.** Sur
l'hébergement OVH, les trois formulaires (devis, contact, rendez-vous) passent par
`public/api/envoi.php` (fonction mail() d'OVH, sans mot de passe stocké) ; plus aucun
repli mailto. `contact-endpoint.ts` n'est conservé que pour un éventuel passage vers un
hébergeur à fonctions serveur (boutique en ligne).
