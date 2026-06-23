import { getCollection, type CollectionEntry } from 'astro:content';

export type Produit = CollectionEntry<'produits'>;

/**
 * Taxonomie des 7 familles (ordre d'affichage).
 * Les JSON produits ne portent pas de champ « famille » : on garde la
 * correspondance ici, côté site, sans modifier les fichiers source.
 */
export interface Famille {
  slug: string;
  titre: string;
  tag: string;
  desc: string;
}

export const FAMILLES: Famille[] = [
  {
    slug: 'prefiltres',
    titre: 'Préfiltres',
    tag: 'ISO Coarse',
    desc: "Première barrière contre les grosses poussières, en protection des étages fins. Cellules métalliques, médias synthétiques en panneau ou en rouleau, et filtres plissés.",
  },
  {
    slug: 'filtres-plans',
    titre: 'Filtres plans',
    tag: 'G3 · G4',
    desc: "Filtration générale en faible épaisseur, pour les caissons à l'encombrement limité.",
  },
  {
    slug: 'poches-souples',
    titre: 'Poches souples',
    tag: 'G4 → F9',
    desc: "Grande surface filtrante développée sur plusieurs poches, pour une longue durée de service à perte de charge maîtrisée.",
  },
  {
    slug: 'compacts',
    titre: 'Compacts / poches rigides',
    tag: 'ePM10 → ePM1',
    desc: "Filtration fine à très fine sous faible encombrement, en mini-plis ou poches rigides. Gamme NETPAK.",
  },
  {
    slug: 'hepa',
    titre: 'HEPA / T.H.E',
    tag: 'E10 → H14',
    desc: "Filtration absolue pour les environnements maîtrisés : salles propres, santé, process sensibles. Gamme NETCEL.",
  },
  {
    slug: 'charbon-actif',
    titre: 'Charbon actif',
    tag: 'Gaz · odeurs',
    desc: "Traitement des gaz et des odeurs par adsorption sur charbon actif. Cellules compactes, dièdres ou poches imprégnées. Gamme NETCARB.",
  },
  {
    slug: 'combines',
    titre: 'Combinés',
    tag: 'Particules + gaz',
    desc: "Un étage particulaire associé au charbon actif, pour traiter l'air en une seule passe lorsque la place manque.",
  },
];

/** Correspondance identifiant produit (= nom de fichier JSON) → slug de famille. */
export const SLUG_FAMILLE: Record<string, string> = {
  netmetal: 'prefiltres',
  netfil: 'prefiltres',
  netfibre: 'prefiltres',
  netply: 'prefiltres',
  netplan: 'filtres-plans',
  'netbag-s': 'poches-souples',
  'netpak-s-bora': 'compacts',
  'netpak-s-cilia': 'compacts',
  'netpak-s-azur': 'compacts',
  'netpak-s-lumen': 'compacts',
  'netpak-v-lam': 'hepa',
  'netcel-v-azur': 'hepa',
  'netcel-v-nival': 'hepa',
  'netpak-s-duo': 'combines',
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
  return all.filter((p) => SLUG_FAMILLE[p.id] === familleSlug);
}

/** Badge de classe court pour les cartes (1ère ligne de badges_p1, nettoyée). */
export function badgeClasse(p: Produit): string | undefined {
  const tag = familleBadge(p);
  return tag;
}

function familleBadge(p: Produit): string | undefined {
  const b = p.data.badges_p1?.[0];
  if (!b) return undefined;
  // « ISO 16890 : Coarse 65% / ePM10 50% » → « Coarse 65% / ePM10 50% »
  return b.replace(/^ISO\s*16890\s*:\s*/i, '').trim();
}
