import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import {
  GAMME_PRODUIT,
  CADRE_SUFFIXE,
  casCadreDeclares,
  produitsSansCadresDeclares,
} from "../../src/lib/pricing/produits-gammes";
import type { GammeProduit } from "../../src/lib/pricing/produits-gammes";

/**
 * Garde-fou sur les cadres proposés par le configurateur.
 *
 * Historique : le configurateur retombait sur un défaut « acier galvanisé + polypropylène »
 * quand un produit ne déclarait pas `cadres`. Ce défaut n'était juste que pour 2 produits
 * sur 18 → NETFIL était proposé en polypropylène (sa fiche dit « fil acier galvanisé
 * Ø 4,5 mm ») et générait des références fantômes NETFIL-…-P. Le défaut a été supprimé ;
 * ces tests empêchent qu'il revienne par la petite porte.
 */

const tousProduits = Object.entries(GAMME_PRODUIT);
const calculables = tousProduits.filter(([, g]) => g.mode === "calcul");

describe("cadres du configurateur", () => {
  it("il y a bien des produits calculables à contrôler", () => {
    expect(calculables.length).toBeGreaterThan(0);
  });

  it("aucun produit calculable ne compte sur un cadre par défaut", () => {
    expect(produitsSansCadresDeclares()).toEqual([]);
  });

  it.each(calculables)("%s déclare exactement un cas de cadre", (_id, gamme) => {
    // Les 3 cas s'excluent : un choix (`cadres`), un cadre imposé (`cadreFixe`), ou rien
    // (`sansCadre`). Deux à la fois = on ne sait plus quel cadre part dans la référence.
    // On interroge la fonction de production, sans recopier son calcul ici.
    expect(casCadreDeclares(gamme), "aucun cadre par défaut : cf. la fiche du produit").toBe(1);
  });

  it.each(calculables)("%s : un cadre imposé n'est pas un menu à une option", (_id, gamme) => {
    // Un menu à une seule option ferait croire à un choix inexistant → `cadreFixe`.
    if (!gamme.cadreFixe) expect(gamme.cadres?.length ?? 0).not.toBe(1);
  });

  it.each(tousProduits)("%s n'utilise que des cadres ayant un suffixe de référence", (_id, gamme) => {
    // Un matériau hors table perdrait SILENCIEUSEMENT son suffixe dans la référence : il doit
    // d'abord être tranché côté codification. Vaut aussi pour les produits sur devis, qui
    // affichent une référence même sans prix (ex. NETMETAL).
    for (const c of [...(gamme.cadres ?? []), ...(gamme.cadreFixe ? [gamme.cadreFixe] : [])]) {
      expect(Object.keys(CADRE_SUFFIXE)).toContain(c.valeur);
      expect(c.libelle.trim().length).toBeGreaterThan(0);
    }
  });

  it.each(calculables)("%s ne propose pas deux fois le même cadre", (_id, gamme) => {
    const valeurs = (gamme.cadres ?? []).map((c) => c.valeur);
    expect(new Set(valeurs).size).toBe(valeurs.length);
  });
});

describe("le garde-fou détecte réellement une déclaration fautive", () => {
  // Sans ces cas fabriqués, la suite ne tournerait que sur un catalogue déjà valide : elle
  // prouverait que les données sont bonnes, jamais que le détecteur fonctionne.
  const acier = { valeur: "galva", libelle: "Acier galvanisé" } as const;

  it("laisse passer un catalogue sain", () => {
    expect(produitsSansCadresDeclares({ ok: { code: "1", mode: "calcul", cadreFixe: acier } })).toEqual([]);
  });

  it("signale un produit calculable sans aucun cas (le bug d'origine)", () => {
    const fautif: Record<string, GammeProduit> = { orphelin: { code: "1", mode: "calcul" } };
    expect(produitsSansCadresDeclares(fautif)).toEqual(["orphelin (0 cas déclarés, attendu exactement 1)"]);
  });

  it("signale un produit qui déclare deux cas contradictoires", () => {
    const fautif: Record<string, GammeProduit> = {
      ambigu: { code: "1", mode: "calcul", cadres: [acier], cadreFixe: acier },
    };
    expect(produitsSansCadresDeclares(fautif)).toEqual(["ambigu (2 cas déclarés, attendu exactement 1)"]);
  });

  it("signale aussi un produit sur devis contradictoire, mais tolère qu'il n'ait rien", () => {
    const devisAmbigu: Record<string, GammeProduit> = {
      ambigu: { code: "29", mode: "devis", cadres: [acier], sansCadre: true },
    };
    expect(produitsSansCadresDeclares(devisAmbigu)).toEqual(["ambigu (2 cas déclarés, attendu au plus 1)"]);
    // Un produit sur devis sans cadre déclaré n'affiche simplement pas le champ : c'est valide.
    expect(produitsSansCadresDeclares({ muet: { code: "29", mode: "devis" } })).toEqual([]);
  });

  it("compte les 3 cas, et ignore une liste de cadres vide", () => {
    expect(casCadreDeclares({ code: "1", mode: "calcul" })).toBe(0);
    expect(casCadreDeclares({ code: "1", mode: "calcul", cadres: [] })).toBe(0);
    expect(casCadreDeclares({ code: "1", mode: "calcul", cadres: [acier] })).toBe(1);
    expect(casCadreDeclares({ code: "1", mode: "calcul", cadreFixe: acier })).toBe(1);
    expect(casCadreDeclares({ code: "1", mode: "calcul", sansCadre: true })).toBe(1);
  });
});

describe("suffixes de référence", () => {
  it("chaque cadre a un suffixe unique et non ambigu", () => {
    const suffixes = Object.values(CADRE_SUFFIXE);
    // Deux cadres au même suffixe rendraient deux produits différents indiscernables.
    expect(new Set(suffixes).size).toBe(suffixes.length);
    // 1 lettre = 1 composant (A/P) · 2 lettres = couple cadre+tricot NETMETAL (AA/AL/II).
    for (const s of suffixes) expect(s).toMatch(/^[A-Z]{1,2}$/);
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
    // `?? []` est le repli légitime (aucun cadre) ; `?? [{ … }]` réintroduirait un défaut.
    expect(page).not.toMatch(/cadres\s*\?\?\s*\[\s*\{/);
    expect(page).not.toMatch(/cadreFixe\s*\?\?\s*\{/);
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
