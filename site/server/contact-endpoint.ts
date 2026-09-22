// ─────────────────────────────────────────────────────────────────────────────
// Point d'entrée serveur du formulaire de contact — MODÈLE PRÊT À ACTIVER.
//
// Aujourd'hui le site est 100 % statique : ce fichier n'est PAS branché (il vit
// hors de `src/pages/`, donc Astro ne le construit pas). Le formulaire de la page
// /contact tente d'appeler /api/contact ; tant que cette route n'existe pas, il
// retombe automatiquement sur l'ouverture de la messagerie du visiteur (mailto).
//
// POUR L'ACTIVER (après hébergement + immatriculation) :
//   1. Ajouter un adaptateur serveur à Astro (ex. @astrojs/netlify) dans
//      astro.config.mjs → `output: 'server'` ou `hybrid`.
//   2. Déplacer ce fichier vers `site/src/pages/api/contact.ts`.
//   3. Créer un compte chez un service d'envoi d'email (ex. Resend) et renseigner
//      les variables d'environnement RESEND_API_KEY et CONTACT_TO.
//   4. Vérifier l'envoi (test réel) puis déployer.
//
// Aucune donnée bancaire ni sensible ne transite ici — uniquement le message.
// ─────────────────────────────────────────────────────────────────────────────

import type { APIRoute } from 'astro';

export const prerender = false;

const CONTACT_TO = import.meta.env.CONTACT_TO ?? 'contact@netair.fr';
const CONTACT_FROM = import.meta.env.CONTACT_FROM ?? 'site@netair.fr';
const RESEND_API_KEY = import.meta.env.RESEND_API_KEY;

interface ContactPayload {
  nom?: string;
  email?: string;
  tel?: string;
  objet?: string;
  message?: string;
}

const clean = (v: unknown): string => (typeof v === 'string' ? v.trim() : '');

export const POST: APIRoute = async ({ request }) => {
  let data: ContactPayload;
  try {
    data = await request.json();
  } catch {
    return json({ ok: false, erreur: 'Requête invalide.' }, 400);
  }

  const nom = clean(data.nom);
  const email = clean(data.email);
  const tel = clean(data.tel);
  const objet = clean(data.objet);
  const message = clean(data.message);

  // Validation minimale (le navigateur valide déjà, mais on ne fait jamais confiance au client).
  // Un moyen de recontact au moins est requis : email OU téléphone (le formulaire de
  // rendez-vous impose le téléphone et rend l'email facultatif ; le contact, l'inverse).
  if (!nom || !objet || !message || (!email && !tel)) {
    return json({ ok: false, erreur: 'Champs obligatoires manquants.' }, 422);
  }
  if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return json({ ok: false, erreur: 'Adresse email invalide.' }, 422);
  }

  const sujet = `Contact — ${objet} — ${nom}`;
  const corps =
    `Nom / société : ${nom}\n` +
    `Email : ${email || '—'}\n` +
    `Téléphone : ${tel || '—'}\n` +
    `Objet : ${objet}\n\n` +
    `Message :\n${message}\n`;

  // Sécurité : si la clé d'envoi n'est pas configurée, on n'échoue pas en silence.
  if (!RESEND_API_KEY) {
    console.error('[contact] RESEND_API_KEY absente — message non envoyé :', sujet);
    return json({ ok: false, erreur: "Service d'envoi non configuré." }, 503);
  }

  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: `Netair <${CONTACT_FROM}>`,
        to: [CONTACT_TO],
        ...(email ? { reply_to: email } : {}),
        subject: sujet,
        text: corps,
      }),
    });
    if (!res.ok) throw new Error(`Resend a répondu ${res.status}`);
  } catch (err) {
    console.error('[contact] Échec de l’envoi :', err);
    return json({ ok: false, erreur: "L'envoi a échoué, réessayez plus tard." }, 502);
  }

  return json({ ok: true });
};

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
