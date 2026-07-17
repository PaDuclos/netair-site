import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  GAMME_PRODUIT,
  CADRE_SUFFIXE,
  produitsSansCadresDeclares,
} from "../../src/lib/pricing/produits-gammes";

/**
 * Garde-fou sur les cadres proposés par le configurateur.
 *
 * Historique : le configurateur retombait sur un défaut « acier galvanisé + polypropylène »
 * quand un produit ne déclarait pas `cadres`. Ce défaut n'était juste que pour 2 produits
 * sur 18 → NETFIL était proposé en polypropylène (sa fiche dit « fil acier galvanisé
 * Ø 4,5 mm ») et générait des références fantômes NETFIL-…-P. Le défaut a été supprimé ;
 * ces tests empêchent qu'il revienne par la petite porte.
 */

const calculables = Object.entries(GAMME_PRODUIT).filter(([, g]) => g.mode === "calcul");

describe("cadres du configurateur", () => {
  it("il y a bien des produits calculables à contrôler", () => {
    expect(calculables.length).toBeGreaterThan(0);
  });

  it("aucun produit calculable ne compte sur un cadre par défaut", () => {
    expect(produitsSansCadresDeclares()).toEqual([]);
  });

  it.each(calculables)("%s déclare ses cadres (ou est explicitement sansCadre)", (_id, gamme) => {
    if (gamme.sansCadre) {
      // Cadre unique/absent : rien à offrir, et surtout pas de liste de cadres contradictoire.
      expect(gamme.cadres).toBeUndefined();
      return;
    }
    expect(gamme.cadres, "aucun cadre par défaut : à renseigner d'après la fiche").toBeDefined();
    expect(gamme.cadres!.length).toBeGreaterThan(0);
  });

  it.each(calculables)("%s n'utilise que des cadres ayant un suffixe de référence", (_id, gamme) => {
    for (const c of gamme.cadres ?? []) {
      // Un matériau hors table (cellulose, polyester, inox…) perdrait SILENCIEUSEMENT son
      // suffixe dans la référence : sa lettre doit d'abord être tranchée (codification).
      expect(Object.keys(CADRE_SUFFIXE)).toContain(c.valeur);
      expect(c.libelle.trim().length).toBeGreaterThan(0);
    }
  });

  it.each(calculables)("%s ne propose pas deux fois le même cadre", (_id, gamme) => {
    const valeurs = (gamme.cadres ?? []).map((c) => c.valeur);
    expect(new Set(valeurs).size).toBe(valeurs.length);
  });
});

describe("suffixes de référence", () => {
  it("chaque cadre a une lettre unique et non vide", () => {
    const lettres = Object.values(CADRE_SUFFIXE);
    expect(new Set(lettres).size).toBe(lettres.length);
    for (const l of lettres) expect(l).toMatch(/^[A-Z]$/);
  });
});

describe("garde-fou anti-retour du défaut", () => {
  // Le bug d'origine est né DANS la page, pas dans les données : un repli
  // `gamme?.cadres ?? CADRES_DEFAUT`. Les tests sur GAMME_PRODUIT ne peuvent pas le voir,
  // d'où ce contrôle sur la source de la page elle-même.
  const page = readFileSync(
    fileURLToPath(new URL("../../src/pages/produits/[ref].astro", import.meta.url)),
    "utf8",
  );

  it("la page ne réintroduit pas de liste de cadres par défaut", () => {
    expect(page).not.toMatch(/CADRES_DEFAUT/);
    expect(page).not.toMatch(/cadres\s*\?\?\s*\[\s*\{/);
  });

  it("la page ne recopie pas le mapping cadre → suffixe", () => {
    // Le suffixe doit venir de CADRE_SUFFIXE, jamais d'un ternaire local sur 'pp'/'galva'.
    expect(page).toMatch(/CADRE_SUFFIXE/);
    expect(page).not.toMatch(/===\s*'pp'\s*\?\s*'P'/);
  });

  it("la page appelle le contrôle des cadres déclarés", () => {
    expect(page).toMatch(/produitsSansCadresDeclares\(\)/);
  });
});
