#!/bin/bash
# Double-cliquez ce fichier pour mettre à jour les fiches d'après DONNEES_PDC_Netair.xlsx.
# (Recalcule les polynômes ΔP, met à jour JSON + versions, régénère les fiches, synchronise le site.)
cd "$(dirname "$0")/Generateur" || exit 1
echo "════════════════════════════════════════════════════════"
echo "  Mise à jour des fiches Netair d'après DONNEES_PDC"
echo "════════════════════════════════════════════════════════"
echo ""
echo "→ Aperçu des changements :"
python3 maj_fiches.py
echo ""
read -r -p "Appliquer ces changements ? (o/N) " rep
if [ "$rep" = "o" ] || [ "$rep" = "O" ]; then
  echo ""
  python3 maj_fiches.py --apply
else
  echo "Annulé — rien n'a été modifié."
fi
echo ""
read -n 1 -s -r -p "Terminé. Appuyez sur une touche pour fermer cette fenêtre."
echo ""
