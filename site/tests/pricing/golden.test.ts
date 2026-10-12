import { describe, it, expect } from "vitest";
import { calculerPrixHT, majorationSite } from "../../src/lib/pricing/engine";
import type { DemandePrix } from "../../src/lib/pricing/types";
import golden from "./golden-vectors.json";
import meta from "../../src/lib/pricing/data/tables.meta.json";

/**
 * Test de conformité « Excel = moteur » (T9, filet de sécurité n°1).
 *
 * Rejoue les vecteurs dorés (générés par scripts/generate_golden.py : géométrie
 * validée du calculateur de référence + charge corrigée = vraie formule Excel) et
 * vérifie que le moteur TypeScript donne le MÊME coût (PRU) et le MÊME prix tarif
 * (PTU) AU CENTIME près.
 */

const TOLERANCE = 0.01;

interface Vecteur {
  codeGamme: string;
  largeur_mm: number;
  hauteur_mm: number;
  profondeur_mm: number;
  classe: string;
  quantite: number;
  coutAttendu: number;
  prixAttendu: number;
}

describe("Conformité Excel = moteur (vecteurs dorés)", () => {
  it("garde anti-divergence : l'empreinte des données correspond aux vecteurs", () => {
    // Si tables.json change, ce test échoue tant que les vecteurs n'ont pas été
    // régénérés (npm run … generate_golden). Impossible d'oublier une MAJ tarif.
    expect(golden.tables_sha256).toBe(meta.tables_sha256);
  });

  it(`reproduit coût + prix au centime sur les ${golden.nb} vecteurs`, () => {
    const vecteurs = golden.vecteurs as Vecteur[];
    const echecs: string[] = [];

    for (const v of vecteurs) {
      const demande: DemandePrix = {
        codeGamme: v.codeGamme,
        largeur_mm: v.largeur_mm,
        hauteur_mm: v.hauteur_mm,
        profondeur_mm: v.profondeur_mm,
        classe: v.classe,
        quantite: v.quantite,
      };
      const r = calculerPrixHT(demande);
      const id = `code ${v.codeGamme} ${v.largeur_mm}×${v.hauteur_mm}×${v.profondeur_mm} ${v.classe} ×${v.quantite}`;

      if (r.statut !== "ok") {
        echecs.push(`${id} → statut ${r.statut} (attendu ok)`);
        continue;
      }
      if (Math.abs((r.detail?.coutHT ?? NaN) - v.coutAttendu) > TOLERANCE) {
        echecs.push(`${id} → coût ${r.detail?.coutHT} ≠ ${v.coutAttendu}`);
      }
      // Parité Excel : le prix tarif du calculateur, AVANT majoration site.
      if (Math.abs((r.detail?.prixCatalogueHT ?? NaN) - v.prixAttendu) > TOLERANCE) {
        echecs.push(`${id} → prix catalogue ${r.detail?.prixCatalogueHT} ≠ ${v.prixAttendu}`);
      }
      // Prix affiché = prix Excel × majoration site, arrondi au centime.
      const maj = majorationSite(v.codeGamme);
      const attenduSite = Math.round(v.prixAttendu * maj * 100) / 100;
      if (Math.abs((r.prixUnitaireHT ?? NaN) - attenduSite) > TOLERANCE) {
        echecs.push(`${id} → prix site ${r.prixUnitaireHT} ≠ ${attenduSite} (Excel × ${maj})`);
      }
    }

    if (echecs.length > 0) {
      throw new Error(
        `${echecs.length}/${vecteurs.length} vecteurs en écart :\n` + echecs.slice(0, 20).join("\n"),
      );
    }
    expect(echecs).toHaveLength(0);
  });
});
