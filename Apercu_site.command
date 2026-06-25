#!/bin/bash
# Double-cliquez ce fichier pour lancer l'aperçu en direct du SITE WEB.
# Vous pouvez ranger ce raccourci où vous voulez DANS le dossier du projet :
# il retrouve le site tout seul en remontant les dossiers parents.
# Une fois lancé, ouvrez http://localhost:4321 dans votre navigateur.
# Pour arrêter : fermez la fenêtre noire.
d="$(cd "$(dirname "$0")" && pwd)"
while [ "$d" != "/" ] && [ ! -f "$d/site/package.json" ]; do
  d="$(dirname "$d")"
done
if [ ! -f "$d/site/package.json" ]; then
  echo "Impossible de retrouver le site."
  echo "Gardez ce raccourci dans le dossier Site_Web (ou l'un de ses sous-dossiers)."
  read -r -p "Appuyez sur Entrée pour fermer…"
  exit 1
fi
cd "$d/site" || exit 1
echo "Démarrage de l'aperçu du site web…"
echo "Le navigateur va s'ouvrir tout seul sur http://localhost:4321"
npm run dev -- --open
