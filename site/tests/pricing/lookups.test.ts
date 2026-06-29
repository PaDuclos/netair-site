import { describe, it, expect } from "vitest";
import {
  tables,
  trouverGamme,
  trouverLigneLxL,
  trouverLignePiece,
  trouverLigneSurface,
  trouverLigneSurfaceHF,
  trouverPoids,
  prixPourClasse,
  getParam,
  libellePalier,
  ordonnerDimensions,
} from "../../src/lib/pricing/lookups";

/**
 * Tests unitaires de T3 — lookups.ts.
 * Les valeurs attendues proviennent DIRECTEMENT de tables.json (donc de l'Excel),
 * pas du moteur. Référence NETPLY (code "1", ep 48).
 */

describe("trouverGamme", () => {
  it("retrouve NETPLY par son code", () => {
    const g = trouverGamme("1");
    expect(g?.nom).toBe("NETPLY");
    expect(g?.ratio).toBeCloseTo(3.3333, 3);
  });

  it("renvoie undefined pour un code inconnu", () => {
    expect(trouverGamme("999")).toBeUndefined();
  });

  it("porte la méthode de calcul (aiguillage) : NETPLY = A", () => {
    expect(trouverGamme("1")?.methode).toBe("A");
  });

  it("une gamme hors calculateur est marquée sur_devis (NETMETAL, code 29)", () => {
    expect(trouverGamme("29")?.methode).toBe("sur_devis");
  });
});

describe("trouverLigneLxL — case dimension + palier de quantité", () => {
  it("287×592, qté 10 → palier 6-19 (G4 = 3,44)", () => {
    const r = trouverLigneLxL("1", 48, 287, 592, 10);
    expect(r?.index).toBe(2);
    expect(r?.prix.G4).toBe(3.44);
  });

  it("qté 3 → palier 0-5 (G4 = 4,128)", () => {
    const r = trouverLigneLxL("1", 48, 287, 592, 3);
    expect(r?.index).toBe(1);
    expect(r?.prix.G4).toBe(4.128);
  });

  it("qté 500 → palier 500+ (sentinelle haute)", () => {
    const r = trouverLigneLxL("1", 48, 287, 592, 500);
    expect(r?.index).toBe(4);
  });

  it("L et H inversés donnent la même case (petit × grand)", () => {
    const direct = trouverLigneLxL("1", 48, 287, 592, 10);
    const inverse = trouverLigneLxL("1", 48, 592, 287, 10);
    expect(inverse?.index).toBe(direct?.index);
  });

  it("dimension hors des cases connues → undefined (repli surface attendu)", () => {
    expect(trouverLigneLxL("1", 48, 350, 350, 10)).toBeUndefined();
  });
});

describe("gamme à épaisseur null (NETFIL, code 2)", () => {
  it("se retrouve en passant ep = null ; qté 10 → palier 6-99 (G3 = 1,06)", () => {
    const r = trouverLigneLxL("2", null, 500, 500, 10);
    expect(r?.index).toBe(4);
    expect(r?.prix.G3).toBe(1.06);
  });
});

describe("trouverLignePiece — prix à la pièce (CILIA, code 7)", () => {
  it("287×500, ep 48 → case prix pièce (pu = 5,5)", () => {
    const r = trouverLignePiece("7", 48, 287, 500, 1);
    expect(r?.index).toBe(2);
    expect(r?.pu).toBe(5.5);
  });
});

describe("trouverLigneSurface — repli par tranche de surface", () => {
  it("surface 5 dm², qté 10 → palier 6-20 (G4 = 3,07)", () => {
    const r = trouverLigneSurface("1", 48, 5, 10);
    expect(r?.index).toBe(2);
    expect(r?.prix.G4).toBe(3.07);
  });
});

describe("trouverLigneSurfaceHF — supplément hors format", () => {
  it("qté 3 → palier 0-5 (G4 = 0,456 / dm²)", () => {
    const r = trouverLigneSurfaceHF("1", 48, 3);
    expect(r?.index).toBe(1);
    expect(r?.prix.G4).toBe(0.456);
  });
});

describe("trouverPoids", () => {
  it("NETPLY ep 48 → 4,5 kg/m²", () => {
    expect(trouverPoids("1", 48)?.poids).toBe(4.5);
  });
});

describe("prixPourClasse — trois issues distinctes", () => {
  const prix = { G4: 4.128 as number | null, F7: null as number | null };

  it("classe fabriquée → nombre", () => {
    expect(prixPourClasse(prix, "G4")).toBe(4.128);
  });

  it("classe présente mais non fabriquée → null", () => {
    expect(prixPourClasse(prix, "F7")).toBeNull();
  });

  it("classe absente de la grille → undefined", () => {
    expect(prixPourClasse(prix, "Z9")).toBeUndefined();
  });
});

describe("constantes & paramètres", () => {
  it("franco = 750 et validité = 30 (clés directes)", () => {
    expect(tables.franco).toBe(750);
    expect(tables.validite_jours).toBe(30);
  });

  it("getParam lit une constante par libellé exact", () => {
    expect(getParam("Seuil franco :")).toBe(750);
  });

  it("getParam renvoie undefined pour un libellé inconnu", () => {
    expect(getParam("Libellé inexistant")).toBeUndefined();
  });
});

describe("aides de présentation", () => {
  it("libellePalier formate les tranches et la sentinelle", () => {
    expect(libellePalier({ qmin: 6, qmax: 19 })).toBe("6-19");
    expect(libellePalier({ qmin: 500, qmax: 1_000_000_000 })).toBe("500+");
  });

  it("ordonnerDimensions range en petit × grand", () => {
    expect(ordonnerDimensions(592, 287)).toEqual({ petite: 287, grande: 592 });
  });
});
