// Envoi des formulaires au programme d'envoi hébergé chez OVH (public/api/envoi.php).
const ouverture = Date.now();

export const TELEPHONE = '04 82 53 37 17';
export const TELEPHONE_HREF = 'tel:+33482533717';

export async function envoyerFormulaire(
  type: 'devis' | 'contact' | 'rdv',
  form: HTMLFormElement,
  donnees: Record<string, unknown>,
): Promise<boolean> {
  const piege = form.querySelector<HTMLInputElement>('input[name="site_web"]')?.value || '';
  try {
    const res = await fetch('/api/envoi.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, duree: Date.now() - ouverture, site_web: piege, ...donnees }),
    });
    if (!res.ok) return false;
    const reponse = await res.json().catch(() => null);
    return reponse?.ok === true;
  } catch {
    return false;
  }
}
