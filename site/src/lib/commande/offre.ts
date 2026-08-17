/**
 * Contrôle d'offre côté serveur (Bloc B3 — étape 0).
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * POURQUOI CE FICHIER EXISTE
 * ─────────────────────────────────────────────────────────────────────────────
 * Le moteur de prix (B1) sait dire ce qu'un filtre COÛTE. Il ne sait pas ce que Netair
 * accepte de VENDRE. Ces deux choses diffèrent, et l'écart est exactement là où se
 * logent nos garde-fous : plusieurs combinaisons sont tarifées dans l'Excel alors
 * qu'elles sont volontairement retirées de la boutique.
 *
 * Trois exemples réels, tous documentés dans `fiches-techniques/CHECKLIST.md` :
 *  - NETCEL V AZUR F8 490×592 : tarifé **3,50 €** au lieu de ~31,50 € (erreur Excel non
 *    corrigée à la source) → retiré via `classesIncluses` ;
 *  - NETFIBRE panneau G3 : 0,015 €/dm², soit 5,7× moins cher que le G4 → `classesExclues` ;
 *  - NETFIBRE rouleau : 4 formats sur 5 retirés, leurs prix au m² étant incohérents.
 *
 * Ces restrictions vivent dans `pricing/produits-gammes.ts` et n'étaient jusqu'ici
 * appliquées que par l'INTERFACE. Or l'interface tourne dans le navigateur du client,
 * donc elle est contournable. Si le serveur se contentait d'appeler le moteur avec un
 * code-gamme reçu, un panier fabriqué à la main achèterait un NETCEL V AZUR F8 à 12 €
 * au lieu de ~108 €.
 *
 * ➜ Ce module ré-applique les mêmes règles côté serveur, où le client n'a pas la main.
 *   Il ne duplique aucune donnée : il lit `GAMME_PRODUIT`, la même source que l'interface.
 */

import { gammeDuProduit, type GammeProduit, type VarianteProduit } from "../pricing/produits-gammes";
import { formatsDuCode, optionsDuCode } from "../pricing/options";
import type { LignePanierRecue, MotifRefus } from "./types";

/**
 * Plafond de quantité par ligne.
 *
 * ⚠️ GARDE-FOU TECHNIQUE, PAS UNE RÈGLE COMMERCIALE — à faire confirmer par Pierre-Alain.
 * Sans lui, une ligne à 1 000 000 000 d'unités produit un total de 19 milliards d'euros
 * que le serveur accepterait sans broncher (constaté en revue). Les tables tarifaires
 * montent jusqu'au palier « 500+ » : 10 000 laisse une marge très large aux commandes
 * réelles tout en écartant l'absurde.
 */
export const QUANTITE_MAX_LIGNE = 10_000;

/**
 * Épaisseur neutre pour les gammes qui n'en ont pas (rouleaux, mètre linéaire, dm²).
 *
 * Le moteur exige une profondeur strictement positive mais l'ignore ensuite pour ces
 * gammes. L'interface envoie déjà `c.ep ?? 48` (`produits/[ref].astro`) — mais le serveur
 * ne peut pas DÉPENDRE de cette valeur : un client qui enverrait 0 verrait sa commande
 * légitime refusée. On la rétablit donc ici, à partir des données (`optionsDuCode`),
 * jamais d'une valeur reçue du navigateur.
 */
const PROFONDEUR_NEUTRE = 48;

/** Offre acceptée : le code-gamme tarifaire et la profondeur à utiliser pour cette ligne. */
export interface OffreAcceptee {
  ok: true;
  /** Code-gamme résolu par le serveur — jamais celui envoyé par le navigateur. */
  codeGamme: string;
  /**
   * Profondeur à transmettre au moteur : celle du client pour les gammes à épaisseur,
   * la valeur neutre pour celles qui n'en ont pas.
   */
  profondeurRetenue: number;
}

/** Offre refusée : le motif et son explication. */
export interface OffreRefusee {
  ok: false;
  motif: MotifRefus;
  message: string;
}

export type ResultatOffre = OffreAcceptee | OffreRefusee;

const refus = (motif: MotifRefus, message: string): OffreRefusee => ({ ok: false, motif, message });

/**
 * Deux dimensions décrivent-elles le même format ?
 *
 * Comparaison NON ORDONNÉE (592×287 ≡ 287×592) : les grilles tarifaires rangent les côtés
 * en petit/grand (`pd_min`/`gd_min`), l'orientation saisie par le client est donc sans effet
 * sur le prix. Refuser sur l'ordre reviendrait à rejeter une commande parfaitement valide.
 */
function memeFormat(a: { l: number; h: number }, b: { l: number; h: number }): boolean {
  return Math.min(a.l, a.h) === Math.min(b.l, b.h) && Math.max(a.l, a.h) === Math.max(b.l, b.h);
}

/**
 * Le conditionnement choisi, quand le produit en déclare.
 *
 * Un produit à variantes DOIT en recevoir une : c'est elle qui porte le code-gamme, et
 * deux conditionnements du même produit peuvent avoir des prix sans rapport (NETFIBRE
 * panneau ≈ 8,57 €/dm² vs rouleau vendu à la pièce). Choisir un défaut à la place du
 * client ferait payer le mauvais tarif en silence.
 */
function resoudreVariante(
  gamme: GammeProduit,
  varianteId: string | undefined,
): { variante?: VarianteProduit } | OffreRefusee {
  if (!gamme.variantes?.length) return {};
  if (!varianteId) {
    return refus("variante_inconnue", "Le conditionnement du produit n'a pas été précisé.");
  }
  const variante = gamme.variantes.find((v) => v.id === varianteId);
  if (!variante) {
    return refus("variante_inconnue", `Conditionnement « ${varianteId} » inconnu pour ce produit.`);
  }
  return { variante };
}

/** Les restrictions de classe déclarées par le produit (liste blanche, exclusions, devis). */
function verifierClasse(gamme: GammeProduit, classe: string): OffreRefusee | null {
  if (gamme.classesIncluses?.length && !gamme.classesIncluses.includes(classe)) {
    return refus("classe_hors_offre", `L'efficacité ${classe} n'est pas proposée à la vente pour ce produit.`);
  }
  if (gamme.classesExclues?.includes(classe)) {
    return refus("classe_hors_offre", `L'efficacité ${classe} n'est pas proposée à la vente pour ce produit.`);
  }
  if (gamme.classesSurDevis?.includes(classe)) {
    return refus("classe_sur_devis", `L'efficacité ${classe} est disponible sur devis, pas à l'achat en ligne.`);
  }
  return null;
}

/**
 * Les dimensions et l'épaisseur, quand le conditionnement les contraint.
 *
 * `saisie: "formats"` = le produit ne se vend qu'en dimensions standard. Les formats
 * proposés viennent soit de la variante (`formats`), soit — quand elle n'en déclare pas —
 * de la grille tarifaire elle-même (`formatsDuCode`), exactement comme l'interface.
 */
function verifierDimensions(
  variante: VarianteProduit | undefined,
  code: string,
  ligne: LignePanierRecue,
): OffreRefusee | null {
  if (!variante) return null;

  if (variante.epaisseurs?.length && !variante.epaisseurs.includes(ligne.profondeur_mm)) {
    return refus(
      "epaisseur_hors_offre",
      `L'épaisseur ${ligne.profondeur_mm} mm n'est pas proposée pour ce conditionnement.`,
    );
  }

  if (variante.saisie !== "formats") return null;

  const demande = { l: ligne.largeur_mm, h: ligne.hauteur_mm };
  const proposes = variante.formats?.length
    ? variante.formats.map((f) => ({ l: f.largeur, h: f.hauteur }))
    : formatsDuCode(code).map((f) => ({ l: f.largeur, h: f.hauteur }));

  if (!proposes.some((f) => memeFormat(f, demande))) {
    return refus(
      "format_hors_offre",
      `Le format ${ligne.largeur_mm} × ${ligne.hauteur_mm} n'est pas proposé à la vente pour ce produit.`,
    );
  }
  return null;
}

/**
 * Cette ligne est-elle vendable en ligne, et sous quel code-gamme ?
 *
 * Ne calcule AUCUN prix : elle décide seulement si la combinaison demandée fait
 * partie de l'offre, puis rend le code-gamme que le moteur devra utiliser.
 */
export function verifierOffre(ligne: LignePanierRecue): ResultatOffre {
  // Le module est la frontière de sécurité d'un futur point d'entrée HTTP : il reçoit
  // donc des données hostiles par hypothèse et ne doit JAMAIS lever d'exception.
  if (!ligne || typeof ligne !== "object") {
    return refus("ligne_invalide", "Ligne de panier inexploitable.");
  }

  if (!Number.isInteger(ligne.quantite) || ligne.quantite < 1) {
    return refus("quantite_invalide", "La quantité doit être un nombre entier d'au moins 1.");
  }
  if (ligne.quantite > QUANTITE_MAX_LIGNE) {
    return refus(
      "quantite_excessive",
      `Au-delà de ${QUANTITE_MAX_LIGNE} pièces, merci de passer par une demande de devis.`,
    );
  }

  // Dimensions contrôlées ICI plutôt que laissées au moteur : le refus est explicite
  // et le message reste celui de la boutique, pas celui du calculateur.
  for (const valeur of [ligne.largeur_mm, ligne.hauteur_mm, ligne.profondeur_mm]) {
    if (typeof valeur !== "number" || !Number.isFinite(valeur) || valeur < 0) {
      return refus("dimensions_invalides", "Les dimensions saisies ne sont pas valides.");
    }
  }

  const gamme = gammeDuProduit(ligne.produitId);
  if (!gamme) {
    return refus("produit_inconnu", `Produit « ${ligne.produitId} » inconnu au catalogue.`);
  }
  if (gamme.mode !== "calcul") {
    return refus("produit_sur_devis", "Ce produit se commande sur devis, pas en ligne.");
  }

  const resolution = resoudreVariante(gamme, ligne.varianteId);
  if ("ok" in resolution) return resolution;
  const { variante } = resolution;

  const classeRefusee = verifierClasse(gamme, ligne.classe);
  if (classeRefusee) return classeRefusee;

  // Le code de la variante prime : c'est lui qui porte le tarif du conditionnement.
  const codeGamme = variante?.code ?? gamme.code;

  const dimensionsRefusees = verifierDimensions(variante, codeGamme, ligne);
  if (dimensionsRefusees) return dimensionsRefusees;

  // Gamme sans épaisseur tarifée (rouleau, mètre linéaire, dm²) → profondeur neutre,
  // décidée par le serveur d'après les données, pas reçue du navigateur.
  const gammeSansEpaisseur = optionsDuCode(codeGamme).epaisseurs.length === 0;
  const profondeurRetenue = gammeSansEpaisseur ? PROFONDEUR_NEUTRE : ligne.profondeur_mm;
  if (profondeurRetenue <= 0) {
    return refus("dimensions_invalides", "Les dimensions saisies ne sont pas valides.");
  }

  return { ok: true, codeGamme, profondeurRetenue };
}
