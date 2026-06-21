# Générateur de fiches techniques Netair

Produit les fiches techniques **à l'identique** du gabarit NETPLY validé, en ne
changeant que les données propres à chaque produit.

## Comment ça marche

- `gabarit_base.html` — le gabarit NETPLY validé (**ne jamais modifier à la main**).
- `generer.py` — repart du gabarit et remplace uniquement les zones variables.
- `produits/*.json` — un fichier de données par produit.
- `assets/` — les photos produits détourées (fond blanc pur).

## Générer une fiche

```bash
cd Generateur
python3 generer.py produits/netply.json
```

→ produit `Fiche technique NETPLY.html` (dans ce dossier, à côté de `assets/`).
Pour imprimer : ouvrir dans un navigateur → `Cmd/Ctrl + P` → A4, marges **aucune**,
cocher « graphiques d'arrière-plan ».

Option : `--out "mon-nom.html"` pour choisir le nom du fichier de sortie.

## Garantie de fidélité (test d'identité)

Régénérer `netply.json` reproduit `gabarit_base.html` **à l'octet près** :

```bash
python3 generer.py produits/netply.json --out _t.html && diff gabarit_base.html _t.html && rm _t.html
```

Un `diff` vide prouve que tout le « fixe » (style, calculateur, courbe) est intact.

## Ajouter un produit

1. Copier `produits/netply.json` → `produits/netxxx.json`.
2. Remplir les zones variables (cf. ci-dessous). Garder la structure JSON.
3. Déposer la photo détourée dans `assets/` (nom = champ `"photo"`).
4. `python3 generer.py produits/netxxx.json`.

### Champs du JSON

| Champ | Rôle |
|---|---|
| `slug` | identifiant interne minuscule (ex. `netbag`) — sert aux id HTML internes |
| `nom` | nom produit (en-têtes, titre, références) |
| `soustitre` | sous-titre sous le nom (page 1) |
| `fiche` | `num`, `version`, `date` (pied de page) |
| `photo`, `photo_alt` | fichier dans `assets/` + texte alternatif |
| `description` | paragraphe de présentation (page 1) |
| `points_cles` | liste (4 recommandés, grille 2×2) |
| `specs` | tableau `[clé, valeur]` (9 lignes type) |
| `badges_p1` / `badges_p2` | 3 badges normes (P2 = transition « → ») |
| `classes.low` / `classes.high` | les **2 classes** du produit (voir plus bas) |
| `dimensions` | liste `{L, H, P, debit}` — surface, ΔP et référence calculées |

### Bloc `classes` (le cœur du calculateur)

Le gabarit est bâti pour un produit à **2 classes** (une « basse » + une « haute »)
et 2 épaisseurs (48 / 98 mm). Pour chaque classe :

| Clé | Sens |
|---|---|
| `label` | code EN 779, ex. `G4` |
| `iso` | classe ISO 16890, ex. `Coarse 65%` |
| `scale48` / `scale98` | ΔP initiale (Pa) à 3400 m³/h sur 592×592, par épaisseur |
| `exp` | exposant de la loi ΔP ∝ vitesseᵉˣᵖ |
| `add` | Pa ajoutés en fin de vie (EN 13053) |
| `rule` | libellé court (ex. `classe Coarse`) |
| `dp` | ΔP fixe affichée dans le tableau dimensions |

### Calculs automatiques (tableau dimensions)

- **Surface filtrante** = `2 × (L × H)` (m², arrondi au centième).
- **Débit** = valeur **curatée** fournie par dimension (champ `debit`), car les
  débits du gabarit sont des arrondis métier (ex. 287×592 → 1700).
- **ΔP** = `dp` de la classe (fixe). **Ordre** : toutes les lignes classe basse,
  puis classe haute. **Référence** = `NOM-iso-label-LxHxP`.

## Limite connue

Les familles à structure différente (HEPA mono-classe, poches F7/F8/F9,
charbon actif) ne rentrent pas dans le modèle « 2 classes / 2 épaisseurs » de la
page 2 telle quelle → elles demanderont une petite variante de structure
(à traiter au cas par cas, le gabarit ne changera pas pour autant).
