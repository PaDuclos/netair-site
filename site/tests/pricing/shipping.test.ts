import { describe, it, expect } from "vitest";
import { calculerPort, tarifDepartement, seuilFranco } from "../../src/lib/pricing/shipping";

/**
 * Tests de T5 — shipping.ts. Valeurs issues de tables.json :
 * dép. 01 → 50 €, 35 → 75 €, 75 → 80 €, Corse 2A/2B → 150 €, 00 → 0 € ; franco 750 €.
 */

describe("tarifDepartement", () => {
  it("lit le tarif d'un département courant (35 → 75 €)", () => {
    expect(tarifDepartement("35")).toBe(75);
  });

  it("Corse 2A/2B → 150 € (port le plus cher)", () => {
    expect(tarifDepartement("2A")).toBe(150);
    expect(tarifDepartement("2B")).toBe(150);
  });

  it("normalise la casse et un chiffre seul (« 2a » → 2A ; « 1 » → 01)", () => {
    expect(tarifDepartement("2a")).toBe(150);
    expect(tarifDepartement("1")).toBe(tarifDepartement("01"));
  });

  it("département absent de la table → undefined", () => {
    expect(tarifDepartement("971")).toBeUndefined();
  });
});

describe("seuilFranco", () => {
  it("vaut 750 € pour tous aujourd'hui (lu des données)", () => {
    expect(seuilFranco("35")).toBe(750);
    expect(seuilFranco("2A")).toBe(750);
  });
});

describe("calculerPort", () => {
  it("sous le franco → tarif du département (35, total 100 € → 75 €)", () => {
    const p = calculerPort("35", 100);
    expect(p.fraisPortHT).toBe(75);
    expect(p.francoApplique).toBe(false);
    expect(p.portSurDevis).toBe(false);
  });

  it("au seuil de franco → port offert (35, total 750 € → 0 €, franco)", () => {
    const p = calculerPort("35", 750);
    expect(p.fraisPortHT).toBe(0);
    expect(p.francoApplique).toBe(true);
  });

  it("au-delà du franco → port offert (35, total 900 € → 0 €)", () => {
    expect(calculerPort("35", 900).fraisPortHT).toBe(0);
  });

  it("Corse sous le franco → 150 €", () => {
    const p = calculerPort("2A", 300);
    expect(p.fraisPortHT).toBe(150);
    expect(p.francoApplique).toBe(false);
  });

  it("département à tarif 0 (00) sous le franco → 0 € mais PAS franco", () => {
    const p = calculerPort("00", 100);
    expect(p.fraisPortHT).toBe(0);
    expect(p.francoApplique).toBe(false);
  });

  it("département inconnu → port sur devis (pas de montant), même au-dessus du franco", () => {
    const bas = calculerPort("971", 100);
    expect(bas.portSurDevis).toBe(true);
    expect(bas.fraisPortHT).toBeUndefined();
    expect(bas.message).toContain("971");

    const haut = calculerPort("971", 5000);
    expect(haut.portSurDevis).toBe(true);
    expect(haut.francoApplique).toBe(false);
  });
});
