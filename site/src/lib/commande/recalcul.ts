/**
 * Recalcul serveur d'un panier avant paiement (Bloc B3 — étape 0).
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * LA RÈGLE, EN UNE PHRASE
 * ─────────────────────────────────────────────────────────────────────────────
 * Le navigateur envoie ce que le client VEUT (produit, dimensions, classe, quantité) ;
 * le serveur décide ce que ça COÛTE. Aucun prix reçu n'est jamais utilisé pour calculer.
 *
 * Sans ce module, n'importe qui modifie l'affichage de son navigateur — c'est l'affaire
 * de quelques secondes — et paie un filtre 1 € au lieu de 108 €.
 *
 * Ce fichier ne réimplémente rien : il enchaîne les briques déjà validées.
 *   `verifierOffre` (offre.ts)      → la combinaison est-elle vendable en ligne ?
 *   `calculerPrix`  (pricing/)      → le moteur B1, conforme à l'Excel au centime
 *   `calculerPort`  (pricing/)      → port par département + franco
 *   `tva.ts`                        → TVA et arrondis
 *
 * Les règles de totalisation sont EXACTEMENT celles de la page `/panier` (port et franco
 * calculés sur le total produits, minimum de facturation hors port) : le serveur doit
 * conclure comme le navigateur, sinon toute commande honnête serait refusée.
 */

import { calculerPrix } from "../pricing";
import { calculerPort } from "../pricing/shipping";
import { MIN_COMMANDE_HT } from "../boutique";
import { verifierOffre } from "./offre";
import { arrondi2, montantTVA, totalTTC, TAUX_TVA } from "./tva";
import type {
  CommandeValidee,
  LigneRefusee,
  LigneValidee,
  MotifRefus,
  PanierRecu,
} from "./types";

/**
 * Écart toléré entre le total du serveur et celui affiché au client, en euros.
 *
 * Strictement un artefact d'arrondi : les deux côtés font la même somme de montants déjà
 * arrondis au centime, l'écart légitime est donc nul. Le demi-centime absorbe la
 * représentation flottante, sans laisser passer une manipulation (le moindre centime
 * volontairement retiré dépasse ce seuil).
 */
const TOLERANCE_ECART_EUR = 0.005;

const refuse = (motif: MotifRefus, message: string, lignesRefusees: LigneRefusee[] = []): CommandeValidee => ({
  statut: "refuse",
  motif,
  message,
  lignesRefusees,
});

/**
 * Valide un panier reçu et en calcule le montant à débiter.
 *
 * Ne renvoie JAMAIS de montant partiel : soit toutes les lignes passent et la commande
 * est chiffrée, soit elle est refusée avec le détail de ce qui bloque. Une commande
 * amputée en silence de sa ligne fautive serait pire qu'un refus — le client paierait
 * autre chose que ce qu'il a composé.
 */
export function recalculerPanier(panier: PanierRecu): CommandeValidee {
  // Frontière de sécurité : la charge utile vient du réseau, elle est hostile par
  // hypothèse. Aucune exception ne doit sortir d'ici — un point d'entrée HTTP qui
  // plante sur une entrée malformée est une panne offerte au premier venu.
  if (!panier || typeof panier !== "object" || !Array.isArray(panier.lignes)) {
    return refuse("panier_invalide", "Commande inexploitable.");
  }
  if (!panier.lignes.length) {
    return refuse("panier_vide", "Votre panier est vide.");
  }

  const departement = panier.departement?.trim();
  if (!departement) {
    return refuse("departement_manquant", "Le département de livraison est nécessaire pour valider la commande.");
  }

  const lignes: LigneValidee[] = [];
  const refusees: LigneRefusee[] = [];

  panier.lignes.forEach((ligne, index) => {
    const offre = verifierOffre(ligne);
    if (!offre.ok) {
      // `ligne` peut être null/undefined ici : on ne la déréférence pas directement.
      refusees.push({
        index,
        produitId: typeof ligne?.produitId === "string" ? ligne.produitId : "(inconnu)",
        motif: offre.motif,
        message: offre.message,
      });
      return;
    }

    // Le port n'est PAS demandé au moteur ici : il se calcule une seule fois, sur le
    // total du panier (franco global). Passer un département ligne à ligne appliquerait
    // un franco par produit — le défaut que le panier a précisément corrigé.
    const prix = calculerPrix({
      codeGamme: offre.codeGamme,
      largeur_mm: ligne.largeur_mm,
      hauteur_mm: ligne.hauteur_mm,
      // Profondeur décidée par le serveur (neutre pour les gammes sans épaisseur).
      profondeur_mm: offre.profondeurRetenue,
      classe: ligne.classe,
      quantite: ligne.quantite,
    });

    if (prix.statut !== "ok" || prix.prixUnitaireHT === undefined || prix.prixTotalHT === undefined) {
      refusees.push({
        index,
        produitId: ligne.produitId,
        motif: "prix_indisponible",
        message: prix.message ?? "Cette configuration n'est pas disponible à la vente en ligne.",
        statutMoteur: prix.statut,
      });
      return;
    }

    lignes.push({
      index,
      produitId: ligne.produitId,
      varianteId: ligne.varianteId,
      codeGamme: offre.codeGamme,
      classe: ligne.classe,
      largeur_mm: ligne.largeur_mm,
      hauteur_mm: ligne.hauteur_mm,
      profondeur_mm: offre.profondeurRetenue,
      quantite: ligne.quantite,
      prixUnitaireHT: prix.prixUnitaireHT,
      prixTotalHT: prix.prixTotalHT,
      palierQuantite: prix.palierQuantite,
    });
  });

  if (refusees.length) {
    return refuse(
      refusees[0].motif,
      "Certains articles de votre panier ne peuvent pas être commandés en ligne.",
      refusees,
    );
  }

  const totalProduitsHT = arrondi2(lignes.reduce((somme, l) => somme + l.prixTotalHT, 0));

  // Contrôle de cohérence avec l'affichage. Le total reçu ne sert QU'ICI : il n'entre
  // dans aucun calcul. En cas d'écart, on refuse — jamais d'alignement silencieux.
  if (
    typeof panier.totalAfficheHT === "number" &&
    Math.abs(panier.totalAfficheHT - totalProduitsHT) > TOLERANCE_ECART_EUR
  ) {
    return refuse(
      "total_divergent",
      "Nos tarifs ont changé depuis la composition de votre panier. Merci de le vérifier avant de valider.",
    );
  }

  if (totalProduitsHT < MIN_COMMANDE_HT) {
    const manque = arrondi2(MIN_COMMANDE_HT - totalProduitsHT);
    return refuse(
      "sous_minimum",
      `Montant minimum de commande : ${MIN_COMMANDE_HT} € HT (il manque ${manque} €).`,
    );
  }

  const port = calculerPort(departement, totalProduitsHT);
  if (port.portSurDevis || port.fraisPortHT === undefined) {
    // La page /panier laisse passer ce cas (elle n'encaisse rien) ; le serveur, lui,
    // s'apprête à débiter une carte. On ne prélève pas sur un total inconnu.
    return refuse(
      "livraison_sur_devis",
      port.message ?? "Les frais de livraison de ce département doivent être établis par devis.",
    );
  }

  const fraisPortHT = port.fraisPortHT;
  const totalHT = arrondi2(totalProduitsHT + fraisPortHT);

  return {
    statut: "ok",
    lignes,
    totalProduitsHT,
    fraisPortHT,
    francoApplique: port.francoApplique,
    totalHT,
    montantTVA: montantTVA(totalHT),
    tauxTVA: TAUX_TVA,
    totalTTC: totalTTC(totalHT),
  };
}
