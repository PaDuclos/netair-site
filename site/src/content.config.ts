import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Collection « produits » — SOURCE UNIQUE.
 * Les fiches produit du générateur Python (../fiches-techniques/Generateur/produits/*.json)
 * sont lues telles quelles au build. Le gabarit Python n'est jamais modifié.
 * Le fichier _gabarit_ref.json (ancre du test d'identité) est exclu.
 */
const produits = defineCollection({
  loader: glob({
    pattern: ['*.json', '!_gabarit_ref.json'],
    base: '../fiches-techniques/Generateur/produits',
  }),
  // Schéma volontairement souple : les JSON varient (mono-classe / multi-classes,
  // dimensions / dimensions_multi…). Zod ignore les clés non listées sans casser.
  schema: z.object({
    slug: z.string().optional(),
    nom: z.string(),
    soustitre: z.string().optional(),
    description: z.string().optional(),
    points_cles: z.array(z.string()).optional(),
    specs: z.array(z.array(z.string())).optional(),
    photo: z.string().optional(),
    photo_alt: z.string().optional(),
    badges_p1: z.array(z.string()).optional(),
    fiche: z
      .object({
        num: z.string().optional(),
        version: z.string().optional(),
        date: z.string().optional(),
      })
      .optional(),
    // Structures de classes / dimensions tolérées telles quelles (variables).
    classes: z.any().optional(),
    classes_list: z.any().optional(),
    dimensions: z.any().optional(),
    dimensions_multi: z.any().optional(),
  }),
});

export const collections = { produits };
