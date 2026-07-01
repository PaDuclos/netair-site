#!/bin/sh
# Régénère les fiches techniques depuis les JSON produits (source unique) avant la
# construction / l'aperçu du site (appelé par les scripts npm prebuild / predev).
#
# Si python3 est absent (ex. environnement de déploiement sans Python), on saute
# proprement : les fiches déjà présentes dans public/fiches-techniques/ (committées)
# sont utilisées. Quand python3 est présent, le code de sortie du générateur est
# propagé → une vraie erreur de génération fait échouer la construction localement.
if command -v python3 >/dev/null 2>&1; then
  python3 "$(dirname "$0")/../../fiches-techniques/Generateur/generer_tous.py"
else
  echo "regen-fiches : python3 absent — fiches non régénérées (copies committées utilisées)."
fi
