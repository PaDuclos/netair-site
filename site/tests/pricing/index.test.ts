import { describe, it, expect } from "vitest";
import { calculerPrix } from "../../src/lib/pricing/index";
import type { DemandePrix } from "../../src/lib/pricing/types";

/** Tests de T7 — index.ts : assemblage prix (engine) + port (shipping). */

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

describe("calculerPrix — assemblage prix + port", () => {
  it("ok + département 35 → prix + port 75 € (total 126 € < 750 → pas de franco)", () => {
    const r = calculerPrix(demande({ departement: "35" }));
    expect(r.statut).toBe("ok");
    expect(r.prixTotalHT).toBe(126);
    expect(r.fraisPortHT).toBe(75);
    expect(r.francoApplique).toBe(false);
  });

  it("ok + total ≥ 750 € → franco (port 0 €)", () => {
    const r = calculerPrix(demande({ departement: "35", quantite: 100 }));
    expect(r.statut).toBe("ok");
    expect(r.prixTotalHT).toBe(1260);
    expect(r.fraisPortHT).toBe(0);
    expect(r.francoApplique).toBe(true);
  });

  it("ok + département inconnu (971) → prix conservé, port sur devis (message, pas de montant)", () => {
    const r = calculerPrix(demande({ departement: "971" }));
    expect(r.statut).toBe("ok");
    expect(r.prixUnitaireHT).toBe(12.6);
    expect(r.fraisPortHT).toBeUndefined();
    expect(r.francoApplique).toBeUndefined();
    expect(r.message).toContain("971");
  });

  it("ok sans département → prix nu (aucun port)", () => {
    const r = calculerPrix(demande({}));
    expect(r.statut).toBe("ok");
    expect(r.prixUnitaireHT).toBe(12.6);
    expect(r.fraisPortHT).toBeUndefined();
    expect(r.francoApplique).toBeUndefined();
  });

  it("poidsTotalKg jamais rempli (T6 abandonné)", () => {
    expect(calculerPrix(demande({ departement: "35" })).poidsTotalKg).toBeUndefined();
  });
});

describe("calculerPrix — statuts non-ok : pas de port, passage tel quel", () => {
  it("sur_devis (NETMETAL code 29) même avec département → aucun port", () => {
    const r = calculerPrix(demande({ codeGamme: "29", departement: "35" }));
    expect(r.statut).toBe("sur_devis");
    expect(r.fraisPortHT).toBeUndefined();
  });

  it("gamme_inconnue → passage tel quel", () => {
    expect(calculerPrix(demande({ codeGamme: "999", departement: "35" })).statut).toBe(
      "gamme_inconnue",
    );
  });

  it("classe_indisponible (NETPLY F7) → aucun port", () => {
    const r = calculerPrix(demande({ classe: "F7", departement: "35" }));
    expect(r.statut).toBe("classe_indisponible");
    expect(r.fraisPortHT).toBeUndefined();
  });
});
