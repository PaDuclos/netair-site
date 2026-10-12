// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import { VENTE_EN_LIGNE } from './src/lib/site-config.ts';

// https://astro.build/config
export default defineConfig({
  site: 'https://netair.fr',

  vite: {
    plugins: [tailwindcss()],
    // Remplacé par une valeur fixe AVANT l'assemblage : en mode vitrine, le moteur de
    // prix et ses grilles tarifaires ne sont même pas fabriqués.
    define: { __VENTE_EN_LIGNE__: JSON.stringify(VENTE_EN_LIGNE) }
  },

  // Les pages de redirection (panier, compte) n'ont rien à faire dans le plan du site.
  integrations: [sitemap({ filter: (page) => !/\/(panier|compte)\/?$/.test(page) })]
});