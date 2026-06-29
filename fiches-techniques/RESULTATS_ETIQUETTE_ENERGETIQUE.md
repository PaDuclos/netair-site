# Résultats — Classes énergétiques calculées (méthode Eurovent 4/21)

> **Statut : estimation INDICATIVE, non certifiée Eurovent.** Calcul du 27/06/2026.
> Méthode et seuils : voir [`SPEC_ETIQUETTE_ENERGETIQUE.md`](SPEC_ETIQUETTE_ENERGETIQUE.md).
> Recalcul automatique : `python3 Generateur/etiquette_energetique.py`
> (relit les polynômes ΔP des `produits/*.json` → toute évolution des données R&D met à jour les classes).

## Méthode appliquée (rappel)

- **Point de référence** : 3400 m³/h sur cadre 592×592 → vitesse d'air **v = 2,6948 m/s** (fixe, ne dépend pas de l'usage réel).
- **ΔP au point de référence** = polynôme R&D `a·v² + b·v + c` évalué à v = 2,6948.
- **ΔP moyenne** (estimée, faute d'essai de colmatage) = ΔP propre **× 1,10**.
- **Énergie annuelle** : `W = 11,328 × ΔP moyenne` (kWh/an).
- **Classe** : meilleure lettre dont le seuil n'est pas dépassé (table AFPRO/Camfil par groupe ISO × % d'efficacité).
- **Validation** : résultats conformes aux exemples de la spec (NETBAG F7 650 = C, F8 500 = D, M6 380 = E).

---

## Filtres AVEC étiquette énergétique

Classe de la **configuration de référence** + plage selon la profondeur / l'épaisseur.

| Filtre | Classe ISO | Config réf. | Classe énergie | Plage (selon profondeur) |
|---|---|---|:---:|---|
| **NETPAK S AZUR** | ePM1 (F7→F9) | F7 292 mm | **A+** | F7 A+ · F8 B · F9 A |
| **NETPAK S LUMEN** | ePM1 (F7→F9) | F7 292 mm | **A** | F7/F8/F9 tous A |
| **NETPAK S CILIA** | ePM10→ePM1 | F7 | **A+/A** | F7 A+ → F9 C/D |
| **NETPAK S BORA** | ePM1 50% | F7 | **B** | B |
| **NETBAG S** | ePM10→ePM1 | F7 650 mm | **C** | B (poche 550) → E (poche 380) |
| **NETPLY** | ePM10 50% (M5) | M5 | **D** | D |
| **NETPAK S DUO** | ePM1 + charbon | F7+CA | **E** | E (combiné) |
| **NETCARB BAG** | ePM1 80% + charbon | F9+CA | **E** | E (combiné) |

### Détail complet (toutes les configurations)

| Filtre | Config | ISO | ΔP @3400 (Pa) | W (kWh/an) | Classe |
|---|---|---|--:|--:|:--:|
| NETPAK S AZUR | F7 292 mm | ePM1 55% | 63 | 790 | **A+** |
| NETPAK S AZUR | F8 292 mm | ePM1 70% | 91 | 1130 | **B** |
| NETPAK S AZUR | F9 292 mm | ePM1 80% | 95 | 1189 | **A** |
| NETPAK S LUMEN | F7 292 mm | ePM1 55% | 71 | 879 | **A** |
| NETPAK S LUMEN | F8 292 mm | ePM1 70% | 84 | 1051 | **A** |
| NETPAK S LUMEN | F9 292 mm | ePM1 80% | 88 | 1094 | **A** |
| NETPAK S CILIA | F7 48 mm | ePM1 50% | 61 | 754 | **A+** |
| NETPAK S CILIA | F7 98 mm | ePM1 50% | 65 | 808 | **A** |
| NETPAK S CILIA | M5 48 mm | ePM10 50% | 77 | 962 | **D** |
| NETPAK S CILIA | M5 98 mm | ePM10 50% | 72 | 901 | **D** |
| NETPAK S CILIA | M6 48 mm | ePM2,5 50% | 96 | 1192 | **C** |
| NETPAK S CILIA | M6 98 mm | ePM2,5 50% | 77 | 958 | **C** |
| NETPAK S CILIA | F8 48 mm | ePM1 70% | 137 | 1707 | **D** |
| NETPAK S CILIA | F8 98 mm | ePM1 70% | 107 | 1336 | **C** |
| NETPAK S CILIA | F9 48 mm | ePM1 80% | 147 | 1832 | **D** |
| NETPAK S CILIA | F9 98 mm | ePM1 80% | 119 | 1483 | **C** |
| NETPAK S BORA | F7 48/98 mm | ePM1 50% | 82 | 1017 | **B** |
| NETBAG S | M5 380 mm | ePM10 50% | 82 | 1024 | **D** |
| NETBAG S | M5 550 mm | ePM10 50% | 48 | 602 | **B** |
| NETBAG S | M5 650 mm | ePM10 50% | 65 | 805 | **D** |
| NETBAG S | M6 380 mm | ePM2,5 50% | 156 | 1950 | **E** |
| NETBAG S | F7 380 mm | ePM1 55% | 175 | 2178 | **E** |
| NETBAG S | F7 550 mm | ePM1 55% | 105 | 1312 | **C** |
| NETBAG S | F7 650 mm | ePM1 55% | 101 | 1262 | **C** |
| NETBAG S | F8 380 mm | ePM1 70% | 192 | 2390 | **E** |
| NETBAG S | F8 500 mm | ePM1 70% | 128 | 1594 | **D** |
| NETBAG S | F9 500 mm | ePM1 80% | 158 | 1974 | **D** |
| NETPLY | M5 48 mm | ePM10 50% | 70 | 866 | **D** |
| NETPLY | M5 98 mm | ePM10 50% | 62 | 777 | **D** |
| NETPAK S DUO | F7+CA 48/98 mm | ePM1 50% | 190 | 2372 | **E** |
| NETCARB BAG | F9+CA 48/98 mm | ePM1 80% | 229 | 2854 | **E** |

> **Note de lecture** : plus la poche est profonde / la surface grande, plus la ΔP baisse → meilleure classe.
> Les **combinés charbon** (DUO, NETCARB BAG) sont en E : le charbon ajoute de la résistance à l'air.
> Petite non-monotonie F8/F9 (ex. AZUR F9 = A alors que F8 = B) : artefact des seuils Eurovent
> (la bande ePM1 80-85 % est plus tolérante que 70-75 %). Conforme aux tables.

---

## Filtres SANS étiquette (hors périmètre Eurovent 4/21)

Eurovent 4/21 ne classe **que** les filtres fins (ePM1/ePM2,5/ePM10) → badge « non classé » pour :

| Catégorie | Filtres |
|---|---|
| Préfiltres Coarse | NETMETAL · NETFIL · NETFIBRE · NETPLAN · (NETPLY version G4) |
| HEPA / T.H.E (MPPS) | NETCEL V AZUR · NETCEL V NIVAL · NETPAK V LAM |
| Charbon actif pur (ISO 10121) | NETCARB CILIA · NETCARB AZUR · NETCARB NIVAL |

---

## Limites

- Estimation indicative (±1 classe vs certifié) — voir §6-7 de la spec.
- Ne pas afficher le **logo Eurovent** (marque déposée, réservée aux produits certifiés).
- Pour passer en « certifié » : obtenir les courbes de colmatage ISO 16890-3 (labo ou fournisseurs).
