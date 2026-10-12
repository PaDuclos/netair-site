<?php
// Netair : envoi par email des formulaires du site (devis, contact, rendez-vous).
// Tourne sur l'hébergement OVH et utilise la fonction mail() d'OVH : aucun mot de passe stocké.
// Le domaine autorise OVH à envoyer pour netair.fr (SPF : include:mx.ovh.com).

declare(strict_types=1);

ini_set('display_errors', '0');
date_default_timezone_set('Europe/Paris');
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');

const DESTINATAIRE = 'contact@netair.fr';
const EXPEDITEUR = 'contact@netair.fr';
const DELAI_MINIMUM_MS = 3000;
const ENVOIS_MAX = 5;
const FENETRE_S = 600;

function repondre(int $code, bool $ok): never
{
    http_response_code($code);
    echo json_encode(['ok' => $ok]);
    exit;
}

function ligne(mixed $valeur, int $max): string
{
    if (!is_string($valeur) && !is_int($valeur)) return '';
    $texte = preg_replace('/[\x00-\x1F\x7F]+/u', ' ', (string) $valeur) ?? '';
    return mb_substr(trim(preg_replace('/\s+/u', ' ', $texte) ?? ''), 0, $max);
}

function paragraphe(mixed $valeur, int $max): string
{
    if (!is_string($valeur)) return '';
    $texte = str_replace(["\r\n", "\r"], "\n", $valeur);
    $texte = preg_replace('/[\x00-\x08\x0B-\x1F\x7F]+/u', '', $texte) ?? '';
    return mb_substr(trim($texte), 0, $max);
}

function email(mixed $valeur): string
{
    $adresse = ligne($valeur, 254);
    return filter_var($adresse, FILTER_VALIDATE_EMAIL) ? $adresse : '';
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') repondre(405, false);

$origine = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origine !== '' && !preg_match('#^https://(www\.)?netair\.fr$#', $origine)) repondre(403, false);

$d = json_decode((string) file_get_contents('php://input', false, null, 0, 50000), true);
if (!is_array($d)) repondre(400, false);

// Pièges à robots : on fait croire que tout s'est bien passé, sans rien envoyer.
if (ligne($d['site_web'] ?? '', 200) !== '') repondre(200, true);
if ((int) ($d['duree'] ?? 0) < DELAI_MINIMUM_MS) repondre(200, true);

if (($d['rgpd'] ?? false) !== true) repondre(400, false);

$type = $d['type'] ?? '';
$nom = ligne($d['nom'] ?? '', 120);
$adresse = email($d['email'] ?? '');
$tel = ligne($d['tel'] ?? '', 30);
$message = paragraphe($d['message'] ?? '', 5000);
$lignes = [];

switch ($type) {
    case 'devis':
        $societe = ligne($d['societe'] ?? '', 120);
        if ($societe === '' || $nom === '' || $adresse === '') repondre(400, false);
        $filtres = [];
        foreach (array_slice(is_array($d['filtres'] ?? null) ? $d['filtres'] : [], 0, 200) as $f) {
            if (!is_array($f)) continue;
            $ref = ligne($f['ref'] ?? '', 80);
            if ($ref === '') continue;
            $qte = max(1, min(100000, (int) ($f['qty'] ?? 1)));
            $produit = ligne($f['produit'] ?? '', 80);
            $detail = ligne($f['detail'] ?? '', 200);
            $filtres[] = '- ' . $qte . ' u. · ' . ($produit !== '' ? $produit . ' · ' : '') . $ref
                . ($detail !== '' ? ' · ' . $detail : '');
        }
        if (!$filtres) repondre(400, false);
        $sujet = 'Demande de devis - ' . $societe;
        $lignes = ['Société : ' . $societe, 'Nom : ' . $nom, 'Email : ' . $adresse,
            'Téléphone : ' . ($tel ?: 'non renseigné')];
        if ($message !== '') array_push($lignes, '', 'Message :', $message);
        array_push($lignes, '', 'Filtres demandés (' . count($filtres) . ') :', ...$filtres);
        break;

    case 'contact':
        $objet = ligne($d['objet'] ?? '', 60) ?: 'Autre';
        if ($nom === '' || $adresse === '' || $message === '') repondre(400, false);
        $sujet = 'Contact - ' . $objet . ' - ' . $nom;
        $lignes = ['Nom / société : ' . $nom, 'Email : ' . $adresse,
            'Téléphone : ' . ($tel ?: 'non renseigné'), 'Objet : ' . $objet, '', 'Message :', $message];
        break;

    case 'rdv':
        $format = ligne($d['format'] ?? '', 60);
        $creneau = ligne($d['creneau'] ?? '', 60) ?: 'Peu importe';
        if ($nom === '' || $tel === '' || $format === '') repondre(400, false);
        $sujet = 'Rendez-vous - ' . $format . ' - ' . $nom;
        $lignes = ['Nom / société : ' . $nom, 'Téléphone : ' . $tel,
            'Email : ' . ($adresse ?: 'non renseigné'), '', 'Format souhaité : ' . $format,
            'Créneau préféré : ' . $creneau];
        if ($message !== '') array_push($lignes, '', 'Sujet :', $message);
        break;

    default:
        repondre(400, false);
}

// Frein anti-abus : 5 envois maximum par adresse IP sur 10 minutes (IP conservée sous forme hachée).
$journal = sys_get_temp_dir() . '/netair_envoi_' . hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . '|netair');
$maintenant = time();
$precedents = json_decode((string) @file_get_contents($journal), true);
$precedents = array_values(array_filter(is_array($precedents) ? $precedents : [],
    fn ($t) => is_int($t) && $t > $maintenant - FENETRE_S));
if (count($precedents) >= ENVOIS_MAX) repondre(429, false);

$lignes[] = '';
$lignes[] = '--';
$lignes[] = 'Demande envoyée depuis le site netair.fr le ' . date('d/m/Y à H:i') . '.';
if ($adresse !== '') $lignes[] = 'Pour répondre au client, utilisez simplement « Répondre ».';

$entetes = [
    'From: Site Netair <' . EXPEDITEUR . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
];
if ($adresse !== '') $entetes[] = 'Reply-To: ' . $adresse;

$envoye = mail(
    DESTINATAIRE,
    '=?UTF-8?B?' . base64_encode($sujet) . '?=',
    implode("\n", $lignes) . "\n",
    implode("\r\n", $entetes),
    '-f' . EXPEDITEUR
);

if (!$envoye) repondre(500, false);

$precedents[] = $maintenant;
@file_put_contents($journal, json_encode($precedents), LOCK_EX);
repondre(200, true);
