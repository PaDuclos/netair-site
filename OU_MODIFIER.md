# OÙ MODIFIER LE CONTENU — mémo simple

Ce mémo explique **comment changer les textes** des fiches techniques et du site,
en voyant le résultat se mettre à jour tout seul à l'écran. Aucune commande à retenir.

---

## 🟩 1. Modifier une FICHE TECHNIQUE

### Étape A — lancer l'aperçu
Double-cliquez **`Apercu_fiches.command`**.
→ Une fenêtre noire s'ouvre (laissez-la ouverte) et le navigateur affiche la liste des fiches.
→ Cliquez la fiche à modifier.

### Étape B — changer le texte

> 💡 **À comprendre :** la page du navigateur, c'est le **résultat fini** (comme une
> lettre imprimée). On ne tape pas dessus. On tape le texte dans un **formulaire séparé**,
> et la page se réimprime toute seule.

**Le plus simple :** sur la fiche ouverte, cliquez le bouton bleu **« ✏️ Modifier le texte »**
en bas à droite. → Le bon formulaire s'ouvre tout seul dans l'éditeur de texte du Mac.

(À la main si besoin : le formulaire est `fiches-techniques/Generateur/produits/<produit>.json`,
ex. `netbag-s.json`, `netplan.json`…)

Dans ce formulaire, vous reconnaissez le texte entre guillemets. Les champs modifiables :

| Champ dans le fichier | Ce que c'est |
|---|---|
| `"nom"` | Le nom du produit (ex. `NETPLAN`) |
| `"soustitre"` | La petite ligne sous le nom |
| `"description"` | Le paragraphe de présentation |
| `"points_cles"` | La liste des points forts (les puces) |
| `"specs"` | Le tableau des caractéristiques (paires `["Libellé", "Valeur"]`) |

**Vous changez le texte entre les guillemets, vous gardez les guillemets.**
Exemple — pour changer la description :
```
"description": "Votre nouveau texte ici, entre les guillemets.",
```

### Étape C — voir le résultat
Enregistrez le fichier (**Cmd + S**).
→ La fiche se met à jour **toute seule** dans le navigateur, en 1 à 2 secondes. ✅

### ⚠️ À NE PAS toucher dans le fichier
Les **chiffres techniques** (coefficients `a`/`b`/`c`, débits, pertes de charge `dp`,
courbes) viennent du fichier de calcul `DONNEES_PDC_Netair.xlsx`. Ne les changez pas
à la main ici : pour une donnée technique, demandez — le bon circuit, c'est le tableur
puis `maj_fiches.py`. Ici, **on ne touche qu'au TEXTE** (nom, descriptif, points clés, libellés).

---

## 🟦 2. Modifier le SITE WEB

### Étape A — lancer l'aperçu
Double-cliquez **`Apercu_site.command`**.
→ Une fenêtre noire s'ouvre, prépare le site quelques secondes, puis le navigateur
s'ouvre tout seul sur **http://localhost:4321**.
(Pas de bouton « Modifier le texte » ici, contrairement aux fiches : sur le site, on
édite directement les fichiers ci-dessous.)

### Étape B — changer le texte
Les textes des pages sont dans `site/src/pages/` :

| Fichier | Page |
|---|---|
| `index.astro` | Page d'accueil |
| `a-propos.astro` | À propos |
| `contact.astro` | Contact |
| `mentions-legales.astro` | Mentions légales |
| `confidentialite.astro` | Confidentialité |
| `gammes/` et `produits/` | Pages des gammes et produits |

Ouvrez le fichier, repérez le texte (il est écrit entre des balises, par ex.
`<h1>Mon titre</h1>` → vous changez `Mon titre`). Gardez les balises `< >`, changez ce qu'il y a entre.

### Étape C — voir le résultat
Enregistrez (**Cmd + S**).
→ La page se rafraîchit **toute seule**. ✅

---

## Arrêter un aperçu
Fermez simplement la fenêtre noire correspondante.

## En cas de doute
Si un texte n'apparaît pas où vous croyez, ou si vous voulez modifier autre chose
que du texte simple (image, mise en page, chiffres) : demandez plutôt que de modifier
au hasard. Mieux vaut une question qu'un fichier cassé.
