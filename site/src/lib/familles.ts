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
  /** Badge — encadré primaire : classe de la norme primaire (valeur, ex. « Coarse → ePM10 »). */
  tag: string;
  /** Nom de la norme primaire pour l'étiquette de l'encadré (ex. « ISO 16890 », « EN 1822 »).
   *  Absent = tag descriptif (« Gaz · odeurs ») → encadré sans étiquette de norme. */
  norme?: string;
  /** Badge — 2e encadré : classe EN 779 (ancienne norme), si applicable. */
  tagEn?: string;
  desc: string;
  /** Texte détaillé (2-3 phrases) affiché sur la page famille /gammes/<slug>.
   *  Absent = on retombe sur `desc` (phrase courte de la bulle). */
  descLong?: string;
  /** Photo détourée (PNG transparent) représentative de la famille. */
  photo?: string;
}

export const FAMILLES: Famille[] = [
  {
    slug: 'prefiltres',
    titre: 'Préfiltres',
    tag: 'Coarse 65%',
    norme: 'ISO 16890',
    tagEn: 'G3 → M5',
    photo: '/produits/detour/netply-v6-photo.png',
    desc: "Premier niveau de filtration, les préfiltres captent les particules grossières pour protéger les installations et prolonger la durée de vie des étages suivants.",
    descLong: "Les préfiltres assurent le premier niveau de filtration en captant les particules grossières. Disponibles dans différentes technologies et classes d'efficacité, ils répondent aux besoins de chaque installation, en préfiltration ou en filtration principale.",
  },
  {
    slug: 'compacts-miniplis',
    titre: 'Filtres miniplis',
    tag: 'ePM10 50% → ePM1 80%',
    norme: 'ISO 16890',
    tagEn: 'M5 → F9',
    photo: '/produits/detour/netpak-s-cilia-photo.png',
    desc: "Conçus pour offrir une faible perte de charge, les filtres miniplis associent haute efficacité et performance énergétique.",
    descLong: "Grâce à leur faible perte de charge, les filtres miniplis associent haute efficacité et économies d'énergie. Selon les applications, leur conception permet de s'affranchir d'un étage de préfiltration et de réduire le coût global d'exploitation.",
  },
  {
    slug: 'poches-souples-rigides',
    titre: 'Filtres à poches souples et rigides',
    tag: 'Coarse 65% → ePM1 80%',
    norme: 'ISO 16890',
    tagEn: 'G4 → F9',
    photo: '/produits/detour/netbag-s-photo.png',
    desc: "Grâce à leur grande capacité de rétention des poussières, les filtres à poches offrent une longue durée de vie et des performances constantes.",
    descLong: "Déclinés en versions souples et rigides, les filtres à poches équipent les installations de ventilation et de traitement d'air. Netair propose un large choix de technologies et de classes d'efficacité pour chaque application.",
  },
  {
    slug: 'hepa',
    titre: 'Filtres absolus (HEPA / T.H.E)',
    tag: 'E10 → H14',
    norme: 'EN 1822',
    photo: '/produits/detour/netcel-v-nival-photo.png',
    desc: "Les filtres absolus HEPA assurent une très haute efficacité de filtration pour répondre aux exigences des salles propres, hôpitaux et industries sensibles.",
    descLong: "Les filtres absolus sont conçus pour les applications exigeant une très haute qualité d'air. Ils répondent aux besoins des environnements les plus sensibles, où la maîtrise de la qualité de l'air est essentielle.",
  },
  {
    slug: 'charbon-actif',
    titre: 'Charbons actifs',
    tag: 'Gaz · odeurs',
    desc: "Les filtres à charbon actif sont spécialement conçus pour capter les odeurs, les gaz et les composés organiques volatils (COV).",
    descLong: "Les filtres à charbon actif sont conçus pour le traitement des odeurs et de certains composés gazeux. Leur diversité de conception répond aux besoins de chaque application.",
  },
  {
    slug: 'combines',
    titre: 'Combinés',
    tag: 'Particules + gaz',
    photo: '/produits/detour/netpak-s-duo-photo.png',
    desc: "Les filtres combinés associent deux efficacités de filtration dans un seul filtre.",
    descLong: "Les filtres combinés associent plusieurs niveaux ou technologies de filtration au sein d'un même filtre. Ils répondent aux exigences de chaque application.",
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
