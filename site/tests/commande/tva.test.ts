import { describe, it, expect } from "vitest";
import { arrondi2, montantTVA, totalTTC, TAUX_TVA } from "../../src/lib/commande/tva";

/**
 * Tests de l'étape 0 — tva.ts. Taux normal 20 % (France métropole + Corse, filtres
 * industriels vendus à des professionnels).
 */

describe("arrondi2", () => {
  it("arrondit au centime", () => {
    expect(arrondi2(19.004)).toBe(19);
    expect(arrondi2(19.005)).toBe(19.01);
    expect(arrondi2(19.006)).toBe(19.01);
  });

  it("neutralise les surprises du calcul flottant (0,1 + 0,2)", () => {
    expect(arrondi2(0.1 + 0.2)).toBe(0.3);
  });

  it("arrondit 1,005 vers le haut (le piège classique de Math.round)", () => {
    expect(arrondi2(1.005)).toBe(1.01);
  });
});

describe("montantTVA", () => {
  it("applique 20 % (170 € HT → 34 €)", () => {
    expect(montantTVA(170)).toBe(34);
  });

  it("arrondit au centime (19,99 € HT → 4,00 €)", () => {
    expect(montantTVA(19.99)).toBe(4);
  });

  it("le taux exporté vaut bien 0,20", () => {
    expect(TAUX_TVA).toBe(0.2);
  });
});

describe("totalTTC", () => {
  it("170 € HT → 204 € TTC", () => {
    expect(totalTTC(170)).toBe(204);
  });

  /**
   * L'invariant qui compte pour le client : les trois montants affichés doivent
   * s'additionner exactement. C'est pour ça que le TTC vaut HT + TVA arrondie,
   * et non HT × 1,2 arrondi séparément.
   */
  it("HT + TVA = TTC au centime, sur 500 montants consécutifs", () => {
    for (let centimes = 1; centimes <= 500; centimes++) {
      const ht = arrondi2(centimes / 7); // des montants « sales », pas des comptes ronds
      expect(totalTTC(ht)).toBe(arrondi2(ht + montantTVA(ht)));
    }
  });
});
