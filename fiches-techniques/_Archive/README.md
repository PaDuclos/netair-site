# _Archive — anciens systèmes (conservés, non actifs)

Contenu remplacé par le système actuel (`../Generateur/` → `../Fiches_Netair/`).
Rien n'est supprimé ici ; ces fichiers sont gardés pour référence/historique.
Rangé en sous-dossiers le 22/06/2026.

```
_Archive/
├── design_handoff/        Paquet de handoff design d'origine : README + gabarit NETPLY
│                          (version loi-puissance, réf. 3400 m³/h) + photo brute de référence.
├── generateurs_html/      Anciens générateurs / prototypes HTML autonomes :
│                          generateur_fiches.html, generateur-v2.html, calculateur-gt.html,
│                          gabarit_base.powerlaw.bak.html (ancien gabarit avant fusion polynôme).
├── pipeline_v4/           Système « v4 » : Fiche technique NETPLY v4.html (+ .bak), index.html,
│                          et scripts d'injection polynomiale (build_donnees_pdc.py, coeffs_pdc.py,
│                          injecter_pdc.py, retrofit_fiche_pdc.py, generer_index.py, verif_coherence.py).
├── backups_sources/       Sauvegardes datées des classeurs source (*.bak-AAAAMMJJ.xlsx).
└── divers/                Anciennes copies / exports : Fiche technique NETPLY.html, .zip, .pdf.
```

> Le modèle ΔP polynomial du système v4 a été **repris** dans le générateur actuel ;
> la source de vérité des coefficients reste `../DONNEES_PDC_Netair.xlsx`.
> Le **système actif** est uniquement `../Generateur/` (`generer.py` + `gabarit_base.html` +
> `produits/*.json`) ; tout ce qui est ici est obsolète.
