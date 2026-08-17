import { describe, it, expect } from "vitest";
import { recalculerPanier } from "../../src/lib/commande/recalcul";
import type { CommandeAcceptee, LignePanierRecue, PanierRecu } from "../../src/lib/commande/types";

/**
 * Tests de l'étape 0 — recalcul.ts (le contrôle de sécurité avant paiement).
 *
 * Valeurs de référence, toutes issues des tables en service :
 *   NETPLY G4 592×592×48 = 19,00 € HT/u  ·  port dép. 35 = 75 €  ·  franco 750 €
 *   minimum de facturation = 80 € HT (produits, hors port)  ·  TVA 20 %
 */

const NETPLY_U = 19;

const netply = (quantite: number): LignePanierRecue => ({
  produitId: "netply",
  largeur_mm: 592,
  hauteur_mm: 592,
  profondeur_mm: 48,
  classe: "G4",
  quantite,
});

const panier = (o: Partial<PanierRecu> = {}): PanierRecu => ({
  departement: "35",
  lignes: [netply(5)],
  ...o,
});

/** Rétrécit le type après un `expect(...).toBe("ok")`, pour lire les montants sans transtypage. */
function accepte(r: ReturnType<typeof recalculerPanier>): CommandeAcceptee {
  if (r.statut !== "ok") throw new Error(`commande refusée (${r.motif}) : ${r.message}`);
  return r;
}

describe("commande acceptée", () => {
  it("5 × NETPLY livré en 35 : 95 € produits + 75 € port = 170 € HT, 34 € TVA, 204 € TTC", () => {
    const r = accepte(recalculerPanier(panier()));
    expect(r.totalProduitsHT).toBe(95);
    expect(r.fraisPortHT).toBe(75);
    expect(r.francoApplique).toBe(false);
    expect(r.totalHT).toBe(170);
    expect(r.montantTVA).toBe(34);
    expect(r.totalTTC).toBe(204);
  });

  it("la ligne validée porte le code-gamme résolu par le SERVEUR, pas par le navigateur", () => {
    const r = accepte(recalculerPanier(panier()));
    expect(r.lignes).toHaveLength(1);
    expect(r.lignes[0]).toMatchObject({
      produitId: "netply",
      codeGamme: "1",
      prixUnitaireHT: NETPLY_U,
      prixTotalHT: 95,
      palierQuantite: "0-5",
    });
  });

  it("au-delà du franco (50 × NETPLY = 950 €) : port offert, TTC 1 140 €", () => {
    const r = accepte(recalculerPanier(panier({ lignes: [netply(50)] })));
    expect(r.totalProduitsHT).toBe(950);
    expect(r.francoApplique).toBe(true);
    expect(r.fraisPortHT).toBe(0);
    expect(r.totalHT).toBe(950);
    expect(r.totalTTC).toBe(1140);
  });

  it("plusieurs lignes : le port est calculé UNE fois sur le total, pas par ligne", () => {
    const r = accepte(recalculerPanier(panier({ lignes: [netply(3), netply(3)] })));
    expect(r.totalProduitsHT).toBe(114); // 6 × 19
    expect(r.fraisPortHT).toBe(75); // un seul port
    expect(r.totalHT).toBe(189);
  });
});

/**
 * ── Le cœur du sujet : les tentatives de fraude ──
 * Chacune simule un panier que le navigateur ne produirait jamais, mais qu'un client
 * peut fabriquer à la main en quelques secondes.
 */
describe("tentatives de fraude", () => {
  it("un prix envoyé par le client est purement et simplement ignoré", () => {
    // On glisse des champs de prix dans la ligne : le contrat ne les prévoit pas,
    // et le total doit rester celui du serveur.
    const truque = { ...netply(5), prixUnitaireHT: 1, prixTotalHT: 5, unit: 1 };
    const r = accepte(recalculerPanier(panier({ lignes: [truque as LignePanierRecue] })));
    expect(r.totalProduitsHT).toBe(95);
    expect(r.lignes[0].prixUnitaireHT).toBe(NETPLY_U);
  });

  it("total affiché minoré → commande refusée, jamais alignée en silence", () => {
    const r = recalculerPanier(panier({ totalAfficheHT: 5 }));
    expect(r).toMatchObject({ statut: "refuse", motif: "total_divergent" });
  });

  it("total affiché conforme → accepté (le contrôle ne gêne pas un client honnête)", () => {
    expect(recalculerPanier(panier({ totalAfficheHT: 95 })).statut).toBe("ok");
  });

  it("produit sur devis forcé à l'achat (NETMETAL) → refusé", () => {
    const r = recalculerPanier(
      panier({ lignes: [{ produitId: "netmetal", largeur_mm: 592, hauteur_mm: 592, profondeur_mm: 25, classe: "G4", quantite: 10 }] }),
    );
    expect(r).toMatchObject({ statut: "refuse", motif: "produit_sur_devis" });
  });

  it("classe retirée de la vente (NETCEL V AZUR F8 à 12 €) → refusée malgré un prix valide", () => {
    const r = recalculerPanier(
      panier({
        lignes: [{ produitId: "netcel-v-azur", varianteId: "standard", largeur_mm: 490, hauteur_mm: 592, profondeur_mm: 292, classe: "F8", quantite: 10 }],
      }),
    );
    expect(r).toMatchObject({ statut: "refuse", motif: "classe_hors_offre" });
  });

  it("format inventé sur un produit à formats standard → refusé", () => {
    const r = recalculerPanier(
      panier({
        lignes: [{ produitId: "netcel-v-lam", varianteId: "standard", largeur_mm: 123, hauteur_mm: 456, profondeur_mm: 68, classe: "H14", quantite: 5 }],
      }),
    );
    expect(r).toMatchObject({ statut: "refuse", motif: "format_hors_offre" });
  });

  it("quantité fractionnaire → refusée", () => {
    const r = recalculerPanier(panier({ lignes: [netply(2.5)] }));
    expect(r).toMatchObject({ statut: "refuse", motif: "quantite_invalide" });
  });

  it("une seule ligne fautive fait tomber TOUTE la commande (jamais de panier amputé)", () => {
    const r = recalculerPanier(panier({ lignes: [netply(5), { ...netply(5), classe: "ZZ9" }] }));
    expect(r.statut).toBe("refuse");
    if (r.statut !== "refuse") return;
    expect(r.lignesRefusees).toHaveLength(1);
    expect(r.lignesRefusees[0].index).toBe(1); // la position permet de pointer la bonne ligne au client
  });
});

describe("règles commerciales", () => {
  it("sous le minimum de facturation (1 × NETPLY = 19 €) → refusé, avec le manque chiffré", () => {
    const r = recalculerPanier(panier({ lignes: [netply(1)] }));
    expect(r).toMatchObject({ statut: "refuse", motif: "sous_minimum" });
    if (r.statut !== "refuse") return;
    expect(r.message).toContain("61");
  });

  it("le minimum se juge sur les produits SEULS — le port ne le fait pas atteindre", () => {
    // 4 × 19 = 76 € produits (< 80), + 75 € de port = 151 € : refusé quand même.
    expect(recalculerPanier(panier({ lignes: [netply(4)] }))).toMatchObject({
      statut: "refuse",
      motif: "sous_minimum",
    });
    // 5 × 19 = 95 € produits → accepté.
    expect(recalculerPanier(panier({ lignes: [netply(5)] })).statut).toBe("ok");
  });

  it("département non tarifé (971) → refus : on ne débite pas sur un total inconnu", () => {
    const r = recalculerPanier(panier({ departement: "971" }));
    expect(r).toMatchObject({ statut: "refuse", motif: "livraison_sur_devis" });
  });

  it("département absent → refus", () => {
    expect(recalculerPanier(panier({ departement: "  " }))).toMatchObject({
      statut: "refuse",
      motif: "departement_manquant",
    });
  });

  it("panier vide → refus", () => {
    expect(recalculerPanier(panier({ lignes: [] }))).toMatchObject({
      statut: "refuse",
      motif: "panier_vide",
    });
  });
});

/**
 * ── Robustesse : la frontière de sécurité ne doit JAMAIS lever d'exception ──
 * Quatre de ces cas faisaient planter le module avant la revue du 17/08/2026. Sur un
 * point d'entrée HTTP, une exception = une panne offerte au premier venu.
 */
describe("charges utiles malformées", () => {
  const malformes: [string, unknown][] = [
    ["panier null", null],
    ["panier undefined", undefined],
    ["panier sans lignes", {}],
    ["lignes pas un tableau", { departement: "35", lignes: "x" }],
    ["lignes = null", { departement: "35", lignes: null }],
  ];

  it.each(malformes)("%s → refus propre, pas d'exception", (_nom, charge) => {
    const r = recalculerPanier(charge as PanierRecu);
    expect(r.statut).toBe("refuse");
    if (r.statut !== "refuse") return;
    expect(r.motif).toBe("panier_invalide");
  });

  it.each([null, undefined, 42, "netply"])("ligne inexploitable (%s) → refus propre", (l) => {
    const r = recalculerPanier(panier({ lignes: [l as unknown as LignePanierRecue] }));
    expect(r).toMatchObject({ statut: "refuse", motif: "ligne_invalide" });
  });

  it.each([
    ["texte", "592"],
    ["NaN", Number.NaN],
    ["infini", Number.POSITIVE_INFINITY],
    ["négatif", -592],
  ])("dimension %s → refus explicite (dimensions_invalides)", (_nom, largeur) => {
    const r = recalculerPanier(
      panier({ lignes: [{ ...netply(5), largeur_mm: largeur as number }] }),
    );
    expect(r).toMatchObject({ statut: "refuse", motif: "dimensions_invalides" });
  });

  it("quantité démesurée (1 milliard) → refusée au lieu de chiffrer 19 milliards d'euros", () => {
    const r = recalculerPanier(panier({ lignes: [netply(1_000_000_000)] }));
    expect(r).toMatchObject({ statut: "refuse", motif: "quantite_excessive" });
  });

  it("le plafond laisse passer une grosse commande réelle (500 pièces)", () => {
    expect(recalculerPanier(panier({ lignes: [netply(500)] })).statut).toBe("ok");
  });
});

/**
 * L'interface envoie une épaisseur neutre de 48 pour les gammes qui n'en ont pas
 * (`produits/[ref].astro` : `c.ep ?? 48`). Le serveur ne doit pas DÉPENDRE de cette
 * valeur : il la rétablit lui-même, sinon un client envoyant 0 verrait sa commande
 * légitime refusée (défaut relevé en revue le 17/08/2026).
 */
describe("gammes sans épaisseur (rouleau NETFIBRE)", () => {
  const rouleau = (profondeur_mm: number): LignePanierRecue => ({
    produitId: "netfibre",
    varianteId: "rouleau",
    largeur_mm: 2,
    hauteur_mm: 20,
    profondeur_mm,
    classe: "G4",
    quantite: 1,
  });

  it("commande acceptée quelle que soit l'épaisseur envoyée (0, 48 ou 999)", () => {
    const totaux = [0, 48, 999].map((ep) => accepte(recalculerPanier(panier({ lignes: [rouleau(ep)] }))).totalProduitsHT);
    expect(totaux[0]).toBeGreaterThan(0);
    expect(new Set(totaux).size).toBe(1); // le prix ne dépend pas de la valeur envoyée
  });

  it("la ligne validée porte la profondeur retenue par le SERVEUR", () => {
    const r = accepte(recalculerPanier(panier({ lignes: [rouleau(0)] })));
    expect(r.lignes[0].profondeur_mm).toBe(48);
    expect(r.lignes[0].codeGamme).toBe("5");
  });
});

describe("cohérence des montants rendus", () => {
  it("totalHT = produits + port, et HT + TVA = TTC, au centime", () => {
    for (const q of [5, 7, 13, 41, 50]) {
      const r = accepte(recalculerPanier(panier({ lignes: [netply(q)] })));
      expect(r.totalHT).toBe(Math.round((r.totalProduitsHT + r.fraisPortHT) * 100) / 100);
      expect(r.totalTTC).toBe(Math.round((r.totalHT + r.montantTVA) * 100) / 100);
    }
  });
});
