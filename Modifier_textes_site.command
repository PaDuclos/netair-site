#!/bin/bash
# Double-cliquez ce fichier pour OUVRIR les textes du site dans l'éditeur de texte.
# Chaque fichier s'ouvre dans sa propre fenêtre (le nom du fichier est dans le titre).
# Modifiez le texte, enregistrez (Cmd+S) : la page d'aperçu (http://localhost:4321)
# se met à jour toute seule.
# Astuce : lancez d'abord "Apercu_site.command" pour voir le résultat en direct.
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

echo "Ouverture des textes du site dans l'éditeur…"
echo "  • src/lib/familles.ts        → descriptions des GAMMES (le plus simple)"
echo "  • src/pages/index.astro      → page d'ACCUEIL"
echo "  • src/pages/a-propos.astro   → page À PROPOS"
echo "  • src/pages/contact.astro    → page CONTACT"
echo ""
echo "Rappel : on ne change QUE le texte lisible (jamais ce qui est entre < > ou après class=)."

open -t "src/lib/familles.ts"
open -t "src/pages/index.astro"
open -t "src/pages/a-propos.astro"
open -t "src/pages/contact.astro"

echo ""
echo "C'est ouvert. Vous pouvez fermer cette fenêtre."
