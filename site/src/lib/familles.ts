import { getCollection, type CollectionEntry } from 'astro:content';

export type Produit = CollectionEntry<'produits'>;

/**
 * Taxonomie des 6 familles (ordre d'affichage).
 * Les JSON produits ne portent pas de champ « famille » : on garde la
 * correspondance ici, côté site, sans modifier les fichiers source.
 */
export interface Famille {
  slug: string;
  titre: string;
  /** Badge — 1re ligne : classe ISO 16890 (norme primaire). */
  tag: string;
  /** Badge — 2e ligne : classe EN 779 (ancienne norme), si applicable. */
  tagEn?: string;
  desc: string;
  /** Photo détourée (PNG transparent) représentative de la famille. */
  photo?: string;
}

export const FAMILLES: Famille[] = [
  {
    slug: 'prefiltres',
    titre: 'Préfiltres',
    tag: 'Coarse → ePM10',
    tagEn: 'G3 → M5',
    photo: '/produits/detour/netply-v6-photo.png',
    desc: "Première barrière contre les grosses poussières, en protection des étages fins. Filtres plissés et plans, cellules métalliques, médias synthétiques en panneau ou en rouleau.",
  },
  {
    slug: 'compacts-miniplis',
    titre: 'Filtres miniplis',
    tag: 'ePM10 50% → ePM1 80%',
    tagEn: 'M5 → F9',
    photo: '/produits/detour/netpak-s-cilia-photo.png',
    desc: "Filtration fine à très fine sous faible encombrement : média finement plissé en cadre rigide, grande surface filtrante pour une longue durée de service.",
  },
  {
    slug: 'poches-souples-rigides',
    titre: 'Filtres à poches souples et rigides',
    tag: 'ePM10 → ePM1',
    tagEn: 'G4 → F9',
    photo: '/produits/detour/netbag-s-photo.png',
    desc: "Grande surface filtrante développée sur plusieurs poches — souples ou rigides (polydièdres) — pour une longue durée de service à perte de charge maîtrisée.",
  },
  {
    slug: 'hepa',
    titre: 'Filtres absolus (HEPA / T.H.E)',
    tag: 'E10 → H14',
    photo: '/produits/detour/netcel-v-nival-photo.png',
    desc: "Filtration absolue pour les environnements maîtrisés : salles propres, santé, process sensibles. Gamme NETCEL et caisson laminaire.",
  },
  {
    slug: 'charbon-actif',
    titre: 'Charbons actifs',
    tag: 'Gaz · odeurs',
    desc: "Traitement des gaz et des odeurs par adsorption sur charbon actif. Cellules compactes, dièdres ou poches imprégnées. Gamme NETCARB.",
  },
  {
    slug: 'combines',
    titre: 'Combinés',
    tag: 'Particules + gaz',
    photo: '/produits/detour/netpak-s-duo-photo.png',
    desc: "Un étage particulaire associé au charbon actif, pour traiter l'air en une seule passe lorsque la place manque.",
  },
];

/**
 * Correspondance identifiant produit (= nom de fichier JSON) → familles.
 * Un produit peut appartenir à PLUSIEURS familles (doublons volontaires : un client
 * doit retrouver son filtre partout où il pourrait le chercher). La 1re famille de la
 * liste est la famille « principale » (utilisée pour le fil d'Ariane des fiches).
 */
export const SLUG_FAMILLE: Record<string, string[]> = {
  netmetal: ['prefiltres'],
  netfil: ['prefiltres'],
  netfibre: ['prefiltres'],
  netply: ['prefiltres'],
  netplan: ['prefiltres'],
  'netpak-s-cilia': ['compacts-miniplis'],
  'netpak-s-bora': ['compacts-miniplis', 'poches-souples-rigides'],
  'netpak-s-azur': ['compacts-miniplis', 'poches-souples-rigides'],
  'netpak-s-lumen': ['compacts-miniplis', 'poches-souples-rigides'],
  'netbag-s': ['poches-souples-rigides'],
  'netcel-v-azur': ['hepa'],
  'netcel-v-nival': ['hepa'],
  'netcel-v-lam': ['hepa'],
  'netcarb-cilia': ['charbon-actif'],
  'netcarb-azur': ['charbon-actif'],
  'netcarb-nival': ['charbon-actif'],
  'netcarb-bag': ['charbon-actif'],
  'netpak-s-duo': ['combines', 'charbon-actif', 'compacts-miniplis'],
};

/** Famille principale d'un produit (1re de la liste), pour le fil d'Ariane. */
export function famillePrincipale(id: string): string | undefined {
  return SLUG_FAMILLE[id]?.[0];
}

/**
 * Ordre d'affichage explicite des produits dans leur famille.
 * Plus le nombre est petit, plus le produit apparaît tôt (en haut à gauche).
 * Les produits absents de cette table passent après, triés par nom.
 */
export const ORDRE_PRODUITS: Record<string, number> = {
  // Préfiltres : NETPLY d'abord, puis NETPLAN, puis la suite.
  netply: 1,
  netplan: 2,
  netmetal: 3,
  netfil: 4,
  netfibre: 5,
};

export function familleBySlug(slug: string): Famille | undefined {
  return FAMILLES.find((f) => f.slug === slug);
}

/** Tous les produits, triés par nom. */
export async function getProduits(): Promise<Produit[]> {
  const all = await getCollection('produits');
  return all.sort((a, b) => a.data.nom.localeCompare(b.data.nom, 'fr'));
}

/** Produits d'une famille donnée. */
export async function getProduitsByFamille(familleSlug: string): Promise<Produit[]> {
  const all = await getProduits();
  return all
    .filter((p) => (SLUG_FAMILLE[p.id] ?? []).includes(familleSlug))
    .sort((a, b) => {
      const oa = ORDRE_PRODUITS[a.id] ?? 999;
      const ob = ORDRE_PRODUITS[b.id] ?? 999;
      if (oa !== ob) return oa - ob;
      return a.data.nom.localeCompare(b.data.nom, 'fr');
    });
}

/**
 * Classes du produit pour le badge des cartes :
 * - `iso` (1re ligne) = classe ISO 16890 (norme primaire) ou EN 1822 pour les HEPA.
 * - `en`  (2e ligne)  = classe EN 779 (ancienne norme), si applicable.
 * Source : badges_p1 du JSON, ex. ["ISO 16890 : Coarse 65% / ePM10 50%", "EN 779 : G4 / M5", …].
 */
export function classesProduit(p: Produit): { iso?: string; en?: string } {
  const arr: string[] = p.data.badges_p1 ?? [];
  const clean = (s: string) => s.replace(/^(ISO\s*16890|EN\s*779|EN\s*1822)\s*:\s*/i, '').trim();
  const iso = arr[0] ? clean(arr[0]) : undefined;
  const enLine = arr.find((b) => /^EN\s*779/i.test(b));
  const en = enLine ? clean(enLine) : undefined;
  return { iso, en };
}
