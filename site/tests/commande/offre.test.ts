import { describe, it, expect } from "vitest";
import { verifierOffre } from "../../src/lib/commande/offre";
import { calculerPrix } from "../../src/lib/pricing";
import type { LignePanierRecue } from "../../src/lib/commande/types";

/**
 * Tests de l'étape 0 — offre.ts.
 *
 * Ce module est le garde-fou qui distingue « ce que le moteur sait chiffrer » de
 * « ce que Netair accepte de vendre ». Les cas les plus importants sont ceux où le
 * moteur rend un prix parfaitement valide sur une combinaison retirée de la vente :
 * sans ce contrôle, un panier fabriqué à la main l'achèterait à ce prix.
 */

const ligne = (o: Partial<LignePanierRecue>): LignePanierRecue => ({
  produitId: "netply",
  largeur_mm: 592,
  hauteur_mm: 592,
  profondeur_mm: 48,
  classe: "G4",
  quantite: 1,
  ...o,
});

describe("cas nominal", () => {
  it("NETPLY G4 592×592×48 → accepté, code-gamme 1, épaisseur du client conservée", () => {
    const r = verifierOffre(ligne({}));
    expect(r).toEqual({ ok: true, codeGamme: "1", profondeurRetenue: 48 });
  });

  it("le code-gamme vient de la VARIANTE quand il y en a une (rouleau NETFIBRE → code 5)", () => {
    const r = verifierOffre(
      ligne({ produitId: "netfibre", varianteId: "rouleau", largeur_mm: 2, hauteur_mm: 20, profondeur_mm: 0 }),
    );
    // Gamme sans épaisseur : le serveur substitue sa valeur neutre à celle du client.
    expect(r).toEqual({ ok: true, codeGamme: "5", profondeurRetenue: 48 });
  });

  it("gamme À épaisseur : la valeur du client est conservée telle quelle (NETPLY 98 mm)", () => {
    expect(verifierOffre(ligne({ profondeur_mm: 98 }))).toMatchObject({ profondeurRetenue: 98 });
  });
});

/**
 * ── Les deux erreurs de tarif connues (CHECKLIST.md) ──
 * Elles sont neutralisées côté interface depuis juillet/août. On vérifie ici qu'elles
 * le sont AUSSI côté serveur — c'est-à-dire là où le client n'a pas la main.
 */
describe("erreurs de tarif connues — le moteur chiffre, l'offre refuse", () => {
  it("NETCEL V AZUR F8 490×592 : le moteur rend 12 €, l'offre refuse", () => {
    // Preuve que le prix existe bel et bien dans les tables (~108 € attendus métier).
    const prix = calculerPrix({
      codeGamme: "13",
      largeur_mm: 490,
      hauteur_mm: 592,
      profondeur_mm: 292,
      classe: "F8",
      quantite: 1,
    });
    expect(prix.statut).toBe("ok");
    expect(prix.prixUnitaireHT).toBe(12);

    const r = verifierOffre(
      ligne({ produitId: "netcel-v-azur", varianteId: "standard", largeur_mm: 490, hauteur_mm: 592, profondeur_mm: 292, classe: "F8" }),
    );
    expect(r.ok).toBe(false);
    expect(r).toMatchObject({ motif: "classe_hors_offre" });
  });

  it("NETFIBRE panneau G3 : le moteur rend 1,51 €, l'offre refuse", () => {
    const prix = calculerPrix({
      codeGamme: "4",
      largeur_mm: 592,
      hauteur_mm: 592,
      profondeur_mm: 48,
      classe: "G3",
      quantite: 1,
    });
    expect(prix.statut).toBe("ok");
    expect(prix.prixUnitaireHT).toBe(1.51);

    const r = verifierOffre(ligne({ produitId: "netfibre", varianteId: "panneau", classe: "G3" }));
    expect(r).toMatchObject({ ok: false, motif: "classe_hors_offre" });
  });

  it("NETFIBRE rouleau 10 m × 1 m : format retiré de la vente (tarifs au m² incohérents)", () => {
    const r = verifierOffre(
      ligne({ produitId: "netfibre", varianteId: "rouleau", largeur_mm: 1, hauteur_mm: 10, profondeur_mm: 0 }),
    );
    expect(r).toMatchObject({ ok: false, motif: "format_hors_offre" });
  });
});

describe("restrictions d'offre", () => {
  it("produit inconnu → refus", () => {
    expect(verifierOffre(ligne({ produitId: "netinvente" }))).toMatchObject({
      ok: false,
      motif: "produit_inconnu",
    });
  });

  it("produit vendu sur devis (NETMETAL) → refus, même avec un code en tarif", () => {
    expect(verifierOffre(ligne({ produitId: "netmetal", profondeur_mm: 25 }))).toMatchObject({
      ok: false,
      motif: "produit_sur_devis",
    });
  });

  it("produit à conditionnements sans conditionnement précisé → refus", () => {
    expect(verifierOffre(ligne({ produitId: "netfibre" }))).toMatchObject({
      ok: false,
      motif: "variante_inconnue",
    });
  });

  it("conditionnement inexistant → refus", () => {
    expect(verifierOffre(ligne({ produitId: "netfibre", varianteId: "carton" }))).toMatchObject({
      ok: false,
      motif: "variante_inconnue",
    });
  });

  it("classe annoncée par la fiche mais non tarifée (NETBAG S G4) → devis, pas achat", () => {
    const r = verifierOffre(
      ligne({ produitId: "netbag-s", varianteId: "standard", profondeur_mm: 380, classe: "G4" }),
    );
    expect(r).toMatchObject({ ok: false, motif: "classe_sur_devis" });
  });

  it("épaisseur hors du conditionnement (NETBAG S standard n'a que 380 et 550)", () => {
    const r = verifierOffre(
      ligne({ produitId: "netbag-s", varianteId: "standard", profondeur_mm: 500, classe: "F7" }),
    );
    expect(r).toMatchObject({ ok: false, motif: "epaisseur_hors_offre" });
  });

  it("format inventé sur un produit vendu en formats standard (laminaire)", () => {
    const r = verifierOffre(
      ligne({ produitId: "netcel-v-lam", varianteId: "standard", largeur_mm: 123, hauteur_mm: 456, profondeur_mm: 68, classe: "H14" }),
    );
    expect(r).toMatchObject({ ok: false, motif: "format_hors_offre" });
  });

  it("les formats sont acceptés quelle que soit l'orientation (287×592 ≡ 592×287)", () => {
    const a = verifierOffre(
      ligne({ produitId: "netbag-s", varianteId: "standard", largeur_mm: 287, hauteur_mm: 592, profondeur_mm: 380, classe: "F7" }),
    );
    const b = verifierOffre(
      ligne({ produitId: "netbag-s", varianteId: "standard", largeur_mm: 592, hauteur_mm: 287, profondeur_mm: 380, classe: "F7" }),
    );
    expect(a).toMatchObject({ ok: true, codeGamme: "17" });
    expect(b).toMatchObject({ ok: true, codeGamme: "17" });
  });
});

describe("quantité", () => {
  it.each([0, -3, 1.5, Number.NaN])("refuse une quantité invalide (%s)", (q) => {
    expect(verifierOffre(ligne({ quantite: q }))).toMatchObject({
      ok: false,
      motif: "quantite_invalide",
    });
  });
});
