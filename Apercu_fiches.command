#!/bin/bash
# Double-cliquez ce fichier pour lancer l'aperçu en direct des FICHES TECHNIQUES.
# Vous pouvez ranger ce raccourci où vous voulez DANS le dossier du projet :
# il retrouve le programme tout seul en remontant les dossiers parents.
# Pour arrêter : fermez la fenêtre noire.
d="$(cd "$(dirname "$0")" && pwd)"
while [ "$d" != "/" ] && [ ! -f "$d/fiches-techniques/Generateur/apercu.py" ]; do
  d="$(dirname "$d")"
done
if [ ! -f "$d/fiches-techniques/Generateur/apercu.py" ]; then
  echo "Impossible de retrouver le projet."
  echo "Gardez ce raccourci dans le dossier Site_Web (ou l'un de ses sous-dossiers)."
  read -r -p "Appuyez sur Entrée pour fermer…"
  exit 1
fi
cd "$d/fiches-techniques/Generateur" || exit 1
echo "Démarrage de l'aperçu des fiches techniques…"
python3 apercu.py
