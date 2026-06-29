import { describe, it, expect } from "vitest";
import { calculerPrixHT } from "../../src/lib/pricing/engine";
import type { DemandePrix } from "../../src/lib/pricing/types";

/**
 * Tests du moteur (T4 étape B).
 * - Méthode A : ancres VALIDÉES par la référence cost_calculator.py (NETPLY,
 *   prix Netair = Titanair repris à date) → coût et prix exacts.
 * - Méthodes B/C/D/E/F : cohérence avec les données Netair (l'assemblage est juste) ;
 *   l'épreuve « Excel = moteur » au centime se fait en T8 (vecteurs dorés).
 * - Tous les statuts.
 */

function demande(p: Partial<DemandePrix>): DemandePrix {
  return {
    codeGamme: "1",
    largeur_mm: 287,
    hauteur_mm: 592,
    profondeur_mm: 48,
    classe: "G4",
    quantite: 10,
    ...p,
  };
}

describe("Méthode A — NETPLY (ancres validées par la référence)", () => {
  it("287×592×48 G4 ×10 → coût 3,78 € (1,1×3,44) · prix 12,60 €", () => {
    const r = calculerPrixHT(demande({}));
    expect(r.statut).toBe("ok");
    expect(r.detail?.methode).toBe("A");
    expect(r.detail?.coutHT).toBe(3.78);
    expect(r.prixUnitaireHT).toBe(12.6);
    expect(r.prixTotalHT).toBe(126);
    expect(r.palierQuantite).toBe("6-19");
    expect(r.dureeValiditeJours).toBe(30);
  });

  it("592×592×48 G4 ×46 → coût 5,70 € · prix 19,00 € · palier 20-499", () => {
    const r = calculerPrixHT(demande({ largeur_mm: 592, quantite: 46 }));
    expect(r.statut).toBe("ok");
    expect(r.detail?.coutHT).toBe(5.7);
    expect(r.prixUnitaireHT).toBe(19);
    expect(r.palierQuantite).toBe("20-499");
  });
});

describe("Méthodes B/C/D/E/F — cohérence sur données Netair", () => {
  it("B — NETFIL (code 2) 287×592 G3 ×10 → périmètre × mL → coût 2,05 € · prix 5,86 €", () => {
    const r = calculerPrixHT(demande({ codeGamme: "2", classe: "G3" }));
    expect(r.statut).toBe("ok");
    expect(r.detail?.methode).toBe("B");
    expect(r.detail?.coutHT).toBe(2.05);
    expect(r.prixUnitaireHT).toBe(5.86);
    expect(r.detail?.perimetre_m).toBeCloseTo(1.758, 3);
  });

  it("C — NETFIBRE (code 4) 287×592 G4 ×10 → dm² × surface → coût 1,45 € · prix 4,14 €", () => {
    const r = calculerPrixHT(demande({ codeGamme: "4", classe: "G4" }));
    expect(r.statut).toBe("ok");
    expect(r.detail?.methode).toBe("C");
    expect(r.detail?.coutHT).toBe(1.45);
    expect(r.prixUnitaireHT).toBe(4.14);
  });

  it("D — CILIA (code 7) F7 425×472×98 ×1 → cadre+média+pièce → coût 24,67 € · prix 70,49 €", () => {
    const r = calculerPrixHT(
      demande({ codeGamme: "7", classe: "F7", largeur_mm: 425, hauteur_mm: 472, profondeur_mm: 98, quantite: 1 }),
    );
    expect(r.statut).toBe("ok");
    expect(r.detail?.methode).toBe("D");
    expect(r.detail?.coutHT).toBe(24.67);
    expect(r.prixUnitaireHT).toBe(70.49);
    expect(r.detail?.composantsCout).toHaveLength(3);
  });

  it("E — NETFIBRE ROULEAU (code 5) G4 rouleau 1×10 m ×1 → prix pièce → coût 36,29 € · prix 103,69 €", () => {
    const r = calculerPrixHT(
      demande({ codeGamme: "5", classe: "G4", largeur_mm: 1000, hauteur_mm: 10000, quantite: 1 }),
    );
    expect(r.statut).toBe("ok");
    expect(r.detail?.methode).toBe("E");
    expect(r.detail?.coutHT).toBe(36.29);
    expect(r.prixUnitaireHT).toBe(103.69);
  });

  it("F — NETBAG (code 11) F7 287×592×292 ×1 → lecture L×l → coût 24,93 € · prix 71,23 €", () => {
    const r = calculerPrixHT(
      demande({ codeGamme: "11", classe: "F7", profondeur_mm: 292, quantite: 1 }),
    );
    expect(r.statut).toBe("ok");
    expect(r.detail?.methode).toBe("F");
    expect(r.detail?.coutHT).toBe(24.93);
    expect(r.prixUnitaireHT).toBe(71.23);
  });
});

describe("Statuts (règle d'or : jamais de prix inventé)", () => {
  it("sur_devis — gamme hors calculateur (NETMETAL, code 29)", () => {
    const r = calculerPrixHT(demande({ codeGamme: "29", classe: "G4", profondeur_mm: 48 }));
    expect(r.statut).toBe("sur_devis");
    expect(r.prixUnitaireHT).toBeUndefined();
  });

  it("gamme_inconnue — code absent des données", () => {
    expect(calculerPrixHT(demande({ codeGamme: "999" })).statut).toBe("gamme_inconnue");
  });

  it("classe_indisponible — NETPLY ne fabrique pas la F7 dans ce format", () => {
    const r = calculerPrixHT(demande({ classe: "F7" }));
    expect(r.statut).toBe("classe_indisponible");
    expect(r.prixUnitaireHT).toBeUndefined();
  });

  it("hors_fabrication — dimensions hors de toute case", () => {
    const r = calculerPrixHT(demande({ largeur_mm: 5000, hauteur_mm: 5000 }));
    expect(r.statut).toBe("hors_fabrication");
  });

  it("hors_fabrication — quantité invalide (0)", () => {
    expect(calculerPrixHT(demande({ quantite: 0 })).statut).toBe("hors_fabrication");
  });
});
