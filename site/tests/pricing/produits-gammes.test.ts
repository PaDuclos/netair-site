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
import { efficaciteFigee, optionsDuCode } from "../../src/lib/pricing/options";
import { calculerPrix } from "../../src/lib/pricing/index";

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

describe("épaisseurs des produits sur devis", () => {
  // Ces épaisseurs ne viennent pas du calculateur (produits sur devis) : leur seule source de
  // vérité est la fiche technique. On la relit ici pour qu'elles ne puissent pas diverger en
  // silence — c'est exactement le genre d'écart fiche/boutique qui a produit le bug NETFIL.
  const ficheJson = (slug: string) =>
    JSON.parse(
      readFileSync(
        fileURLToPath(new URL(`../../../fiches-techniques/Generateur/produits/${slug}.json`, import.meta.url)),
        "utf8",
      ),
    );

  /** Épaisseurs annoncées par la ligne « Épaisseurs disponibles » d'une fiche, en mm. */
  const epaisseursDeLaFiche = (slug: string): number[] => {
    const lignes: unknown[] = [];
    const parcourir = (o: unknown) => {
      if (Array.isArray(o)) {
        if (o.length === 2 && typeof o[0] === "string" && typeof o[1] === "string") lignes.push(o);
        else o.forEach(parcourir);
      } else if (o && typeof o === "object") Object.values(o).forEach(parcourir);
    };
    parcourir(ficheJson(slug));
    const ligne = (lignes as [string, string][]).find(([k]) => /épaisseurs? disponibles?/i.test(k));
    return ligne ? [...ligne[1].matchAll(/\d+/g)].map((m) => Number(m[0])) : [];
  };

  it("NETMETAL propose exactement les épaisseurs de sa fiche", () => {
    const attendues = epaisseursDeLaFiche("netmetal");
    expect(attendues, "ligne « Épaisseurs disponibles » introuvable dans la fiche").not.toEqual([]);
    expect([...(GAMME_PRODUIT.netmetal.epaisseursDevis ?? [])].sort((a, b) => a - b)).toEqual(
      [...attendues].sort((a, b) => a - b),
    );
  });

  it.each(tousProduits)("%s : l'épaisseur par défaut est réellement proposée", (_id, gamme) => {
    // Un défaut absent du menu retomberait silencieusement sur la première valeur.
    if (gamme.epaisseurDefaut === undefined) return;
    // RÉPLIQUE EXACTE de la cascade `epaisseursAffichees` de [ref].astro (revue 27/07) :
    // épaisseurs de la variante par défaut (?? — une liste vide serait utilisée telle
    // quelle), sinon la grille tarifaire si non vide, sinon le stopgap « sur devis ».
    const grille = gamme.code ? optionsDuCode(gamme.code).epaisseurs : [];
    const menu =
      gamme.variantes?.[0]?.epaisseurs ??
      (grille.length > 0 ? grille : gamme.epaisseursDevis ?? []);
    expect(menu).toContain(gamme.epaisseurDefaut);
  });

  it.each(tousProduits)("%s : une variante à épaisseurs déclarées n'a jamais une liste vide", (_id, gamme) => {
    // `??` ne saute que null/undefined : une liste [] donnerait un menu d'épaisseurs vide
    // (et un readCfg sans épaisseur). On l'interdit à la source.
    for (const v of gamme.variantes ?? []) {
      if (v.epaisseurs !== undefined) expect(v.epaisseurs.length).toBeGreaterThan(0);
    }
  });
});

describe("NETBAG S (code 17) — statuts garantis sur les trous de la matrice", () => {
  // La divergence fiche ↔ tarif est ASSUMÉE (déc. PA 26/07/2026, arbitrage 8 de
  // netbag-s.json) : ces tests figent que les trous répondent par un STATUT, jamais un prix.
  it("M5 592×592×380 (courbe réelle, pas de prix au code 17) → classe_indisponible", () => {
    const r = calculerPrix({ codeGamme: "17", largeur_mm: 592, hauteur_mm: 592, profondeur_mm: 380, classe: "M5", quantite: 6 });
    expect(r.statut).toBe("classe_indisponible");
    expect(r.prixUnitaireHT).toBeUndefined();
  });

  it("F7 592×592×500 (longueur mesurée, non tarifée) → hors_fabrication", () => {
    const r = calculerPrix({ codeGamme: "17", largeur_mm: 592, hauteur_mm: 592, profondeur_mm: 500, classe: "F7", quantite: 6 });
    expect(r.statut).toBe("hors_fabrication");
    expect(r.prixUnitaireHT).toBeUndefined();
  });
});

describe("étiquettes ISO par produit (etiquettesIso)", () => {
  // L'override n'existe que parce que la fiche fait foi contre la table ISO globale de
  // l'Excel (BORA : média spécial → ePM1 50 %, décision PA 18/07/2026). On relit la fiche
  // pour que l'étiquette ne puisse pas diverger en silence à la resynchro Excel.
  const ficheJson = (slug: string) =>
    JSON.parse(
      readFileSync(
        fileURLToPath(new URL(`../../../fiches-techniques/Generateur/produits/${slug}.json`, import.meta.url)),
        "utf8",
      ),
    );

  it("NETPAK S BORA affiche « ePM1 50 % (F7) » — l'ISO de sa fiche, pas la table globale", () => {
    const etiquette = GAMME_PRODUIT["netpak-s-bora"].etiquettesIso?.F7;
    // L'ISO de la fiche ("ePM1 50%") normalisé à la charte ("ePM1 50 %") + la classe.
    const isoFiche = String(ficheJson("netpak-s-bora").classes.low.iso).replace(/\s*%/, " %");
    expect(etiquette).toBe(`${isoFiche} (F7)`);
  });

  it.each(tousProduits)("%s : chaque clé d'etiquettesIso vise une classe réellement proposée", (_id, gamme) => {
    // Une clé orpheline (faute de frappe, classe retirée) serait un override mort : le menu
    // repasserait silencieusement sur la table globale. On l'attrape ici.
    const cles = Object.keys(gamme.etiquettesIso ?? {});
    if (cles.length === 0) return;
    const proposees = [
      ...(gamme.efficacitesDevis ?? []),
      ...optionsDuCode(gamme.code).classes.map((c) => c.valeur),
    ];
    for (const cle of cles) expect(proposees, `clé « ${cle} » sans classe proposée`).toContain(cle);
  });
});

describe("les produits à efficacité figée gardent un prix", () => {
  // Figer l'affichage ne doit RIEN changer au prix : la classe reste transmise au moteur.
  // Ancre chiffrée, indépendante du navigateur — si un jour le champ caché cesse d'envoyer
  // la classe, le statut passera à `classe_indisponible` et ces tests tomberont.
  it.each([
    ["netfil", { codeGamme: "2", largeur_mm: 592, hauteur_mm: 592, profondeur_mm: 48, classe: "G3", quantite: 6 }, 7.89],
    ["netfibre panneau", { codeGamme: "4", largeur_mm: 592, hauteur_mm: 592, profondeur_mm: 48, classe: "G4", quantite: 6 }, 8.57],
    ["netcel-v-lam", { codeGamme: "14", largeur_mm: 305, hauteur_mm: 305, profondeur_mm: 68, classe: "H14", quantite: 6 }, 71.37],
  ])("%s : prix au centime", (_nom, demande, attendu) => {
    const r = calculerPrix(demande as never);
    expect(r.statut).toBe("ok");
    expect(r.statut === "ok" && r.prixUnitaireHT).toBe(attendu);
  });
});

describe("efficacité figée quand il n'y a qu'une classe", () => {
  // Règle PA : pas de choix quand il n'y en a qu'un. La classe restant une entrée du moteur,
  // elle continue d'être transmise — mais l'affichage ne doit pas simuler un choix inexistant.
  const G4 = { valeur: "G4", libelle: "Coarse 65 % (G4)" };
  const F7 = { valeur: "F7", libelle: "ePM1 55 % (F7)" };

  it("fige la classe unique d'un produit sans conditionnement (cas NETFIL)", () => {
    expect(efficaciteFigee([G4])).toEqual(G4);
  });

  it("garde le menu dès qu'il y a un vrai choix", () => {
    expect(efficaciteFigee([G4, F7])).toBeNull();
  });

  it("fige si tous les conditionnements partagent la même classe unique (cas NETFIBRE)", () => {
    expect(efficaciteFigee([G4], [[G4], [G4]])).toEqual(G4);
  });

  it("garde le menu si deux conditionnements ont chacun une classe UNIQUE mais DIFFÉRENTE", () => {
    // Le piège : chaque conditionnement n'a qu'une classe, mais changer de conditionnement
    // changerait la filtration → c'est bien un choix, il doit rester ouvert.
    expect(efficaciteFigee([G4], [[G4], [F7]])).toBeNull();
  });

  it("ne fige rien quand aucune classe n'est tarifée", () => {
    expect(efficaciteFigee([])).toBeNull();
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

  it("la page ne propose pas de menu d'efficacité à une seule option", () => {
    // Règle PA : pas de choix quand il n'y en a qu'un. Une efficacité unique s'affiche figée
    // (`effFixe`) — mais elle reste une entrée du moteur, d'où le champ caché qui la transmet.
    expect(page).toMatch(/const effFixe =/);
    expect(page).toMatch(/!effFixe &&/);
    expect(page).toMatch(/<input id="inEff" type="hidden"/);
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
