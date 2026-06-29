import { describe, it, expect } from "vitest";
import { calculerPrix } from "../../src/lib/pricing/index";
import { calculerPrixHT } from "../../src/lib/pricing/engine";
import type { DemandePrix } from "../../src/lib/pricing/types";

/** Cas limites du moteur (T9). Complète golden.test.ts (conformité) par les bords. */

function d(p: Partial<DemandePrix>): DemandePrix {
  return {
    codeGamme: "1", largeur_mm: 287, hauteur_mm: 592, profondeur_mm: 48,
    classe: "G4", quantite: 10, ...p,
  };
}

describe("Cas limites", () => {
  it("dimension hors grille → hors_fabrication (méthode L×l directe, NETBAG)", () => {
    // NETPLY (méthode A) sait tout chiffrer via surface/hors-format ; on teste donc une
    // gamme à lecture L×l directe (NETBAG code 11) : hors grille = pas de prix.
    const r = calculerPrixHT(d({ codeGamme: "11", largeur_mm: 5000, hauteur_mm: 5000 }));
    expect(r.statut).toBe("hors_fabrication");
    expect(r.prixUnitaireHT).toBeUndefined();
  });

  it("classe non fabriquée → classe_indisponible (jamais un prix)", () => {
    expect(calculerPrixHT(d({ classe: "F7" })).statut).toBe("classe_indisponible");
  });

  it("dégressivité : le prix unitaire baisse du palier 0-5 au palier 6-19", () => {
    const q1 = calculerPrixHT(d({ quantite: 1 }));
    const q10 = calculerPrixHT(d({ quantite: 10 }));
    expect(q1.palierQuantite).toBe("0-5");
    expect(q10.palierQuantite).toBe("6-19");
    expect(q1.prixUnitaireHT!).toBeGreaterThan(q10.prixUnitaireHT!);
  });

  it("franchissement du franco 750 € → port offert", () => {
    const sous = calculerPrix(d({ departement: "35", quantite: 10 })); // total 126 €
    const au_dela = calculerPrix(d({ departement: "35", quantite: 100 })); // total 1260 €
    expect(sous.fraisPortHT).toBe(75);
    expect(sous.francoApplique).toBe(false);
    expect(au_dela.fraisPortHT).toBe(0);
    expect(au_dela.francoApplique).toBe(true);
  });

  it("département inconnu → prix conservé, port sur devis", () => {
    const r = calculerPrix(d({ departement: "971" }));
    expect(r.statut).toBe("ok");
    expect(r.prixUnitaireHT).toBe(12.6);
    expect(r.fraisPortHT).toBeUndefined();
    expect(r.message).toContain("971");
  });

  it("quantité invalide (0) → hors_fabrication (jamais un prix)", () => {
    expect(calculerPrixHT(d({ quantite: 0 })).statut).toBe("hors_fabrication");
  });

  // HORS-FORMAT (surface > 50 dm²) — règle = Prix_Surface(50) + Prix_Surface_HF × (⌈surf⌉−50).
  // Validée sur prix Excel réels fournis par Pierre-Alain.
  it("hors-format > 50 dm² : NETPLY 900×600 (54 dm²) = 37,67 € (validé sur Excel réel)", () => {
    const r = calculerPrixHT(d({ largeur_mm: 900, hauteur_mm: 600 }));
    expect(r.statut).toBe("ok");
    expect(r.prixUnitaireHT).toBe(37.67);
  });

  it("hors-format : NETPLY 1000×600 (60 dm²) = 46,03 € (validé sur Excel réel)", () => {
    const r = calculerPrixHT(d({ largeur_mm: 1000, hauteur_mm: 600 }));
    expect(r.prixUnitaireHT).toBe(46.03);
  });
});
