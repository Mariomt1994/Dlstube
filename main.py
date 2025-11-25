import os
import sys
import re
from pathlib import Path
import yt_dlp
import imageio_ffmpeg
from colorama import Fore, Back, Style, init
from flask import Flask, request, render_template_string, send_from_directory, jsonify, redirect, url_for, Response
import threading
import uuid
import time
import subprocess
import webbrowser

# Inicializar colorama para Windows
init(autoreset=True)


# -----------------------------
# Plantillas HTML (webapp)
# -----------------------------

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
  <head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Media Downloader - Web</title>
   <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" />
   <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" />
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  <style>
    :root {
      --bg-start: #0b1220; --bg-end: #0e1a33; --card: #111827; --border: #1f2940;
      --text: #ffffff; --muted: #98a2b3; --brand: #7cc4ff; --brand-hover: #9ad2ff; --accent: #2563eb; --accent-2: #3b82f6; --accent-shadow: rgba(59,130,246,.35);
    }
    /* Tema claro: sobreescribe variables */
    .theme-light {
      --bg-start: #f6f7fb; --bg-end: #fbe4ff; --card: #ffffff; --border: #e6eaf2;
      --text: #152032; --muted: #5b6678; --brand: #2563eb; --brand-hover: #1f4bd8; --accent: #2563eb; --accent-2: #3b82f6; --accent-shadow: rgba(59,130,246,.35);
    }
    /* Paletas de color */
    .palette-blue { --brand: #7cc4ff; --brand-hover: #9ad2ff; --accent: #2563eb; --accent-2: #3b82f6; --accent-shadow: rgba(59,130,246,.35); }
    .palette-green { --brand: #7ce8c4; --brand-hover: #9af0d4; --accent: #10b981; --accent-2: #22c55e; --accent-shadow: rgba(16,185,129,.35); }
    .palette-purple { --brand: #c8a6ff; --brand-hover: #d7c1ff; --accent: #7c3aed; --accent-2: #8b5cf6; --accent-shadow: rgba(124,58,237,.35); }
    .palette-red { --brand: #ff9ea8; --brand-hover: #ffbcc3; --accent: #ef4444; --accent-2: #f43f5e; --accent-shadow: rgba(244,63,94,.35); }
    .palette-orange { --brand: #ff9f43; --brand-hover: #ffa85b; --accent: #ff7a00; --accent-2: #ff9e3d; --accent-shadow: rgba(255,122,0,.35); }
    .palette-pink { --brand: #ff6db3; --brand-hover: #ff8dc4; --accent: #ec4899; --accent-2: #f472b6; --accent-shadow: rgba(236,72,153,.35); }
    .palette-teal { --brand: #5eead4; --brand-hover: #7ef0df; --accent: #14b8a6; --accent-2: #06b6d4; --accent-shadow: rgba(20,184,166,.35); }
    * { font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
    body { background: radial-gradient(1200px 600px at 20% 0%, var(--bg-end) 0%, var(--bg-start) 35%), var(--bg-start); color: var(--text); }
    .navbar { background: rgba(17, 24, 39, 0.85); backdrop-filter: saturate(180%) blur(6px); border-bottom: 1px solid var(--border); position: relative; z-index: 1100; }
    .navbar .dropdown-menu { z-index: 1200; }
     .brand { color: var(--brand); font-weight: 700; letter-spacing: .2px; }
     .brand-logo { height: 64px; width: auto; border-radius: 12px; box-shadow: 0 6px 16px rgba(0,0,0,.45); object-fit: contain; image-rendering: -webkit-optimize-contrast; image-rendering: crisp-edges; }
    .hero { margin-top: 1.25rem; }
    .card { background: var(--card); border-color: var(--border); box-shadow: 0 10px 25px rgba(0,0,0,.35); }
    .form-label { color: #c8d0e0; }
    .text-muted { color: var(--muted) !important; }
    .theme-dark .text-muted { color: #ffffff !important; }
    a { color: var(--brand); text-decoration: none; }
    a:hover { color: var(--brand-hover); }
    .btn-primary { background: linear-gradient(135deg, var(--accent), var(--accent-2)); border: none; box-shadow: 0 8px 18px var(--accent-shadow); }
    .btn-primary:hover { filter: brightness(1.05); }
    .btn-secondary { background: #1f2937; border-color: #334155; }
    .btn-toggle { border-color: var(--border); }
    /* Animaciones suaves */
    .btn { transition: transform .1s ease, box-shadow .15s ease; }
    .btn:hover { transform: translateY(-1px); }
    .card { transition: transform .15s ease; }
    .card:hover { transform: translateY(-2px); }
    .theme-light .navbar { background: rgba(255,255,255,0.75); }
    .theme-light a:hover { color: var(--brand-hover); }
    .theme-light .btn-outline-light { color: #152032; border-color: #cbd5e1; }
    .pill { border: 1px solid var(--border); border-radius: 999px; overflow: hidden; display: inline-flex; justify-content: center; align-items: center; gap: 1.25rem; padding: .5rem 1rem; box-sizing: border-box; }
    .theme-light .pill { background: #f8fafc; }
    .theme-dark .pill { background: #0f172a; }
    .pill .form-check { padding: 0; margin: 0; display: inline-flex; align-items: center; }
    .pill .form-check-input { margin: 0 .5rem 0 0; flex-shrink: 0; }
    /* Botones MP3/MP4: texto negro por defecto */
    .pill .form-check-label { color: #000000; }
    .theme-dark .pill .form-check-label { color: #ffffff; }
    /* Cambia a azul solo cuando esté seleccionado */
    .pill input:checked + label { color: #2563eb; font-weight: 600; }
    .pill input:hover + label { filter: brightness(1.05); }
     /* Texto con degradado para Instagram */
     .insta-gradient { 
       background: linear-gradient(135deg,#f9a8d4,#f97316,#fb7185,#8b5cf6);
       -webkit-background-clip: text; background-clip: text; color: transparent; font-weight: 700;
     }
     /* TikTok: texto y chip con colores de marca */
     .tiktok-text {
       background: linear-gradient(90deg,#00f2ea,#ff0050);
       -webkit-background-clip: text; background-clip: text; color: transparent; font-weight: 700;
     }
     .tiktok-icon { color: #00f2ea; }
     .tiktok-chip {
       background: #0f0f0f;
       color: #ffffff;
       border: 1px solid #00f2ea;
       box-shadow: 0 4px 12px rgba(255,0,80,.25);
     }
    /* Chips estilizados para badges */
    .badge-chip { padding: .35rem .7rem; font-weight: 600; border: 1px solid var(--border); box-shadow: 0 4px 10px rgba(0,0,0,.25); transition: transform .15s ease, box-shadow .15s ease; }
    .badge-chip:hover { transform: translateY(-1px); box-shadow: 0 6px 14px rgba(0,0,0,.3); }
    /* Inputs: foco personalizado y colores de fondo según tema */
    .form-control, .form-select { background-color: #0f172a; color: var(--text); border-color: var(--border); }
    .theme-light .form-control, .theme-light .form-select { background-color: #ffffff; color: #152032; }
    .form-control:focus, .form-select:focus { border-color: var(--brand); box-shadow: 0 0 0 .2rem var(--accent-shadow); }
    .theme-dark .form-text { color: #ffffff !important; }
    .theme-dark .card h1, .theme-dark .card h2, .theme-dark .card h3, .theme-dark .card h4, .theme-dark .card h5, .theme-dark .card h6, .theme-dark .card p, .theme-dark label { color: #ffffff !important; }
    .theme-dark .card li { color: #ffffff !important; }
    .footer { color: var(--muted); }
    /* Badge de contador de descargas exitosas */
      .dl-badge { position:absolute; top:-8px; left:-8px; right:auto; font-size:11px; color:#16a34a; border:1px solid #000; border-radius:10px; padding:0 4px; background:#f0fff4; line-height:16px; min-width:16px; text-align:center; z-index: 10; }
    .d-none { display:none !important; }
    #globalProgressText { font-weight: 600; }
  </style>
  <script>
    function toggleQuality() {
      const format = document.querySelector('input[name="format"]:checked').value;
      document.getElementById('audio-quality').style.display = (format === 'mp3') ? 'block' : 'none';
      document.getElementById('video-quality').style.display = (format === 'mp4') ? 'block' : 'none';
    }
    let currentJobId = null;
    let successCount = 0;
    function stateText(s){
      switch(s){
        case 'pending': return 'Pendiente';
        case 'downloading': return 'Descargando';
        case 'processing': return 'Procesando';
        case 'completed': return 'Completado';
        case 'error': return 'Error';
        default: return 'Pendiente';
      }
    }
    function onSubmit(e) {
      e.preventDefault();
      const btn = document.getElementById('submitBtn');
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Descargando...';

      // Separar por líneas usando RegExp creado desde cadena para evitar CR/LF insertados
      const rawText = document.getElementById('urls').value;
      const urls = rawText.split(new RegExp('\\r?\\n')).map(s=>s.trim()).filter(s=>s && !s.startsWith('#'));
      if(urls.length === 0){
        alert('Añade al menos una URL');
        resetSubmitBtn();
        return;
      }
      const format = document.querySelector('input[name="format"]:checked').value;
      const audio_quality = document.getElementById('aq').value;
      const video_quality = document.getElementById('vq').value;

      fetch('/api/start_download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls, format, audio_quality, video_quality })
      }).then(r=>r.json()).then(data=>{
        currentJobId = data.id;
        const gpt = document.getElementById('globalProgressText');
        if(gpt){
          gpt.style.display = 'block';
          gpt.textContent = 'Descarga en progreso: 0%';
        }
        pollProgress();
      }).catch(err=>{
        console.error(err);
        alert('Error al iniciar la descarga');
        resetSubmitBtn();
      });
    }
    function resetSubmitBtn(){
      const btn = document.getElementById('submitBtn');
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-download me-2"></i>Descargar';
    }
    // Eliminado renderProgressArea: sin listas por ítem, solo porcentaje global
    function pollProgress(){
      if(!currentJobId) return;
      fetch('/api/progress/' + currentJobId)
        .then(r=>r.json())
        .then(job=>{
          // Calcula sólo porcentaje global y actualiza badge con completados
          var sum = 0;
          var completed = 0;
          job.items.forEach(function(it){
            var pct = it.progress || 0;
            sum += pct;
            if(it.status === 'completed') completed += 1;
          });
          var overall = job.items.length ? Math.round(sum / job.items.length) : 0;
          const gpt = document.getElementById('globalProgressText');
          if(gpt){
            gpt.textContent = 'Descarga en progreso: ' + overall + '%';
          }
          if(job.status === 'completed'){
            resetSubmitBtn();
            // Al terminar, muestra contador en el botón Descargas
            var finalCompleted = 0;
            job.items.forEach(function(it){ if(it.status === 'completed') finalCompleted += 1; });
            updateDownloadsBadge(finalCompleted);
            if(gpt){ gpt.textContent = 'Descarga completada: 100%'; }
            return;
          }
          setTimeout(pollProgress, 1000);
        })
        .catch(err=>{
          console.error(err);
          setTimeout(pollProgress, 1500);
        });
    }
    function updateDownloadsBadge(count){
      const badgeNav = document.getElementById('dlCountBadge');
      const badgeForm = document.getElementById('dlCountBadgeForm');
      // Actualiza ambos badges si existen
      [badgeNav, badgeForm].forEach(badge => {
        if(!badge) return;
        if(count > 0){
          badge.textContent = String(count);
          badge.classList.remove('d-none');
        } else {
          badge.classList.add('d-none');
        }
      });
    }
    function openDownloadsFolder(e){
      if(e && e.preventDefault) e.preventDefault();
      fetch('/api/open_downloads', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
          if(!data.ok){
            alert('No se pudo abrir la carpeta de Descargas');
          }
        })
        .catch(err => {
          console.error(err);
          alert('Error al abrir la carpeta de Descargas');
        });
    }
    function applySavedTheme() {
      const saved = localStorage.getItem('theme');
      const body = document.body;
      body.classList.remove('theme-dark','theme-light');
      body.classList.add(saved ? saved : 'theme-light');
      updateThemeIcon();
    }
    function toggleTheme() {
      const isLight = document.body.classList.contains('theme-light');
      const next = isLight ? 'theme-dark' : 'theme-light';
      document.body.classList.remove('theme-dark','theme-light');
      document.body.classList.add(next);
      localStorage.setItem('theme', next);
      updateThemeIcon();
    }
    function updateThemeIcon() {
      const icon = document.getElementById('themeIcon');
      if (!icon) return;
      const isLight = document.body.classList.contains('theme-light');
      icon.className = isLight ? 'bi bi-brightness-high' : 'bi bi-moon';
    }
    function applySavedPalette() {
      const p = localStorage.getItem('palette') || 'palette-purple';
      const body = document.body;
      body.classList.remove('palette-blue','palette-green','palette-purple','palette-red');
      body.classList.add(p);
    }
    function setPalette(p) {
      const body = document.body;
      body.classList.remove('palette-blue','palette-green','palette-purple','palette-red');
      body.classList.add(p);
      localStorage.setItem('palette', p);
    }
    window.addEventListener('DOMContentLoaded', () => { toggleQuality(); applySavedTheme(); applySavedPalette(); });
  </script>
  </head>
<body class="theme-light">
  <nav class="navbar navbar-expand-md">
    <div class="container">
      <a class="navbar-brand brand d-flex align-items-center" href="{{ url_for('index') }}">
        <img src="{{ url_for('static', filename='dls.png') }}" srcset="{{ url_for('static', filename='dls.png') }} 1x, {{ url_for('static', filename='dls@2x.png') }} 2x" alt="" class="brand-logo" decoding="async" onerror="this.style.display='none'" />
      </a>
      <div class="ms-auto">
        <a id="downloadsBtn" href="https://t.me/Marshallkss" class="btn btn-sm btn-primary" target="_blank" rel="noopener"><i class="bi bi-telegram me-1"></i>Dev</a>
        <button id="themeBtn" type="button" class="btn btn-sm btn-outline-light btn-toggle ms-2" onclick="toggleTheme()" aria-label="Cambiar tema">
          <i id="themeIcon" class="bi bi-moon"></i>
        </button>
        <div class="dropdown d-inline ms-2">
          <button class="btn btn-sm btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
            Colores
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="#" onclick="setPalette('palette-blue')">Azul</a></li>
            <li><a class="dropdown-item" href="#" onclick="setPalette('palette-green')">Verde</a></li>
            <li><a class="dropdown-item" href="#" onclick="setPalette('palette-purple')">Morado</a></li>
            <li><a class="dropdown-item" href="#" onclick="setPalette('palette-red')">Rojo</a></li>
            <li><a class="dropdown-item" href="#" onclick="setPalette('palette-orange')">Naranja</a></li>
            <li><a class="dropdown-item" href="#" onclick="setPalette('palette-pink')">Rosa</a></li>
            <li><a class="dropdown-item" href="#" onclick="setPalette('palette-teal')">Turquesa</a></li>
          </ul>
        </div>
      </div>
    </div>
  </nav>

  <div class="container hero py-4">
    <div class="row align-items-stretch g-4">
      <div class="col-12 col-lg-8">
        <div class="card p-4">
          <h2 class="mb-2">Descarga desde 
            <span class="text-danger"><i class="bi bi-youtube me-1"></i>YouTube</span>, 
            <i class="fa-brands fa-tiktok me-1 tiktok-icon"></i><span class="tiktok-text">TikTok</span>, 
            <span class="text-primary"><i class="bi bi-facebook me-1"></i>Facebook</span> 
            o 
            <span class="insta-gradient"><i class="bi bi-instagram me-1"></i>Instagram</span>
          </h2>
          <p class="text-muted mb-2">Pega las URLs y elige formato y calidad.</p>
          <div class="d-flex flex-wrap gap-2 mb-3">
            <span class="badge rounded-pill badge-chip bg-danger"><i class="bi bi-youtube me-1"></i>YouTube</span>
            <span class="badge rounded-pill badge-chip tiktok-chip"><i class="fa-brands fa-tiktok me-1"></i>TikTok</span>
            <span class="badge rounded-pill badge-chip bg-primary"><i class="bi bi-facebook me-1"></i>Facebook</span>
            <span class="badge rounded-pill badge-chip" style="background: linear-gradient(135deg,#f9a8d4,#f97316,#fb7185,#8b5cf6); color:#fff;"><i class="bi bi-instagram me-1"></i>Instagram</span>
          </div>
          <form method="post" action="#" onsubmit="onSubmit(event)">
            <div class="mb-3">
              <label for="urls" class="form-label"><i class="bi bi-link-45deg me-1"></i>URLs (una por línea)</label>
              <textarea id="urls" name="urls" class="form-control" rows="6" placeholder="https://www.youtube.com/...\nhttps://www.tiktok.com/...\nhttps://fb.watch/...\nhttps://www.instagram.com/reel/..." required></textarea>
              <div class="form-text">Se ignorarán líneas vacías y comentarios (#...)</div>
            </div>

            <div class="mb-3">
              <label class="form-label">Formato</label>
              <div class="d-flex justify-content-center">
                <div class="pill">
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="format" id="fmtMp3" value="mp3" checked onchange="toggleQuality()" />
                    <label class="form-check-label" for="fmtMp3"><i class="bi bi-music-note-beamed me-1"></i>MP3</label>
                  </div>
                  <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="format" id="fmtMp4" value="mp4" onchange="toggleQuality()" />
                    <label class="form-check-label" for="fmtMp4"><i class="bi bi-film me-1"></i>MP4</label>
                  </div>
                </div>
              </div>
            </div>

            <div id="audio-quality" class="mb-3">
              <label for="aq" class="form-label">Calidad de audio (MP3)</label>
              <select id="aq" name="audio_quality" class="form-select">
                <option value="320">320 kbps</option>
                <option value="256">256 kbps</option>
                <option value="192">192 kbps</option>
                <option value="128">128 kbps</option>
                <option value="96">96 kbps</option>
              </select>
            </div>

            <div id="video-quality" class="mb-3" style="display:none">
              <label for="vq" class="form-label">Calidad de video (YouTube)</label>
              <select id="vq" name="video_quality" class="form-select">
                <option value="best">Mejor disponible</option>
                <option value="2160p">4K (2160p)</option>
                <option value="1440p">2K (1440p)</option>
                <option value="1080p">Full HD (1080p)</option>
                <option value="720p">HD (720p)</option>
                <option value="480p">SD (480p)</option>
                <option value="360p">Baja (360p)</option>
              </select>
            </div>

            <div class="d-flex gap-2">
              <button id="submitBtn" type="submit" class="btn btn-primary"><i class="bi bi-download me-2"></i>Descargar</button>
              <a id="downloadsBtnForm" href="#" onclick="openDownloadsFolder(event)" class="btn btn-outline-light position-relative"><i class="bi bi-folder2-open me-2"></i>Ver Descargas<span id="dlCountBadgeForm" class="dl-badge d-none">0</span></a>
            </div>
            <div id="globalProgressText" class="mt-2" style="display:none">Descarga en progreso: 0%</div>
          </form>
          
        </div>
      </div>

      <div class="col-12 col-lg-4">
        <div class="card p-4 h-100">
          <h5 class="mb-3">Consejos</h5>
          <div class="mb-3 d-flex flex-wrap gap-2">
            <span class="badge rounded-pill bg-success"><i class="bi bi-music-note-beamed me-1"></i>MP3 hasta 320 kbps</span>
            <span class="badge rounded-pill bg-info text-dark"><i class="bi bi-film me-1"></i>MP4 hasta 4K</span>
            <span class="badge rounded-pill bg-warning text-dark"><i class="bi bi-shield-check me-1"></i>Seguro y rápido</span>
          </div>

          <ul class="mb-3">
            <li>Usa una URL por línea.</li>
            <li>En Facebook/Instagram, algunos videos requieren estar logueado.</li>
            <li>Selecciona formato y calidad según tus necesidades.</li>
          </ul>

          <h6 class="mt-2 mb-2">Sitios compatibles</h6>
          <div class="d-flex flex-wrap gap-2 mb-3">
            <span class="badge rounded-pill bg-dark">TikTok</span>
            <span class="badge rounded-pill bg-primary">Facebook</span>
            <span class="badge rounded-pill bg-danger">YouTube</span>
            <span class="badge rounded-pill" style="background: linear-gradient(135deg,#f9a8d4,#f97316,#fb7185,#8b5cf6); color:#fff;">Instagram</span>
          </div>

          <div class="mb-2">
            <p class="mb-1">DlsTube es una herramienta que te permitirá descargar videos sin límites.</p>
            <p class="text-muted mb-0">Un proyecto creado por un usuario para los usuarios — sabemos que lo necesitas.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Sección informativa al final -->
  <div class="container py-2">
    <div class="card p-4 mt-3">
      <h5 class="mb-2"><i class="bi bi-stars me-2"></i>Un conversor rápido, gratuito y seguro</h5>
      <p class="text-muted mb-3">Convierte y descarga videos de Youtube , Tiktok, Facebook,Instagram y más en MP3 o MP4, sin publicidad y compatible con todos tus dispositivos.</p>
      <div class="row g-3">
        <div class="col-md-6">
          <p><i class="bi bi-lightning-charge-fill me-2"></i><strong>Velocidad:</strong> Conversión en 2 clics, elige formato y listo.</p>
          <p><i class="bi bi-shield-check me-2"></i><strong>Asegurado:</strong> Nada se almacena en el servidor; descargas seguras.</p>
          <p><i class="bi bi-infinity me-2"></i><strong>Sin límites:</strong> Descarga todo lo que quieras, sin anuncios.</p>
        </div>
        <div class="col-md-6">
          <p><i class="bi bi-list-stars me-2"></i><strong>Playlist:</strong> Descarga listas de reproducción de hasta 100 videos.</p>
          <p><i class="bi bi-phone me-2"></i><strong>Compatibilidad:</strong> MP3 y MP4 para todos los dispositivos, incluidos Shorts.</p>
          <p><i class="bi bi-lightbulb me-2"></i><strong>Consejo:</strong> Cambia <code>youtube.com/watch?v=...</code> por <code>notube.lol/watch?v=...</code> y descarga al instante.</p>
        </div>
      </div>
    </div>
  </div>
 </body>
 </html>
"""

DOWNLOADS_TEMPLATE = """
<!DOCTYPE html>
<html lang=es>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Descargas</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
  <style>
    :root { --brand: #7cc4ff; --brand-hover: #9ad2ff; --accent: #2563eb; --accent-2: #3b82f6; --accent-shadow: rgba(59,130,246,.35); }
    body { background: #0b1220; color: #eaeef7; }
    .card { background: #121a2b; border-color: #1f2940; box-shadow: 0 8px 18px rgba(0,0,0,.35); }
    a { color: var(--brand); text-decoration: none; }
    body.theme-light { background: radial-gradient(900px 400px at 20% 0%, #fbe4ff 0%, #f6f7fb 40%), #f6f7fb; color: #152032; }
    .theme-light .card { background: #ffffff; border-color: #e6eaf2; }
    .theme-light .list-group-item { background:#ffffff !important; color:#152032 !important; border-color:#e6eaf2 !important; }
    .theme-light a { color: var(--brand); }
    .palette-blue { --brand: #7cc4ff; --brand-hover: #9ad2ff; --accent: #2563eb; --accent-2: #3b82f6; --accent-shadow: rgba(59,130,246,.35); }
    .palette-green { --brand: #7ce8c4; --brand-hover: #9af0d4; --accent: #10b981; --accent-2: #22c55e; --accent-shadow: rgba(16,185,129,.35); }
    .palette-purple { --brand: #c8a6ff; --brand-hover: #d7c1ff; --accent: #7c3aed; --accent-2: #8b5cf6; --accent-shadow: rgba(124,58,237,.35); }
    .palette-red { --brand: #ff9ea8; --brand-hover: #ffbcc3; --accent: #ef4444; --accent-2: #f43f5e; --accent-shadow: rgba(244,63,94,.35); }
    .palette-orange { --brand: #ff9f43; --brand-hover: #ffa85b; --accent: #ff7a00; --accent-2: #ff9e3d; --accent-shadow: rgba(255,122,0,.35); }
    .palette-pink { --brand: #ff6db3; --brand-hover: #ff8dc4; --accent: #ec4899; --accent-2: #f472b6; --accent-shadow: rgba(236,72,153,.35); }
    .palette-teal { --brand: #5eead4; --brand-hover: #7ef0df; --accent: #14b8a6; --accent-2: #06b6d4; --accent-shadow: rgba(20,184,166,.35); }
    .btn-primary { background: linear-gradient(135deg, var(--accent), var(--accent-2)); border: none; box-shadow: 0 8px 18px var(--accent-shadow); }
  </style>
  <script>
    window.addEventListener('DOMContentLoaded', () => {
      const theme = localStorage.getItem('theme') || 'theme-light';
      const palette = localStorage.getItem('palette') || 'palette-purple';
      document.body.className = theme + ' ' + palette;
    });
  </script>
</head>
<body class="theme-light">
  <div class="container py-4">
    <h1 class="mb-3"><i class="bi bi-folder2-open me-2"></i>Descargas</h1>
    <div class="card p-3">
      <ul class="list-group">
        {% for f in files %}
        <li class="list-group-item d-flex justify-content-between align-items-center" style="background:#0f172a;color:#cbd5e1;border-color:#1f2940;">
          <span>{{ f.name }}</span>
          <a class="btn btn-sm btn-outline-light" href="{{ f.url }}" download="{{ f.name }}"><i class="bi bi-download me-1"></i>Descargar</a>
        </li>
        {% endfor %}
      </ul>
      <div class="mt-3">
        <a href="{{ url_for('index') }}" class="btn btn-primary"><i class="bi bi-arrow-left me-2"></i>Volver</a>
      </div>
    </div>
  </div>
</body>
</html>
"""


class MediaDownloader:
    def __init__(self, output_dir=None):
        """
        Inicializa el descargador de YouTube, TikTok, Facebook e Instagram
        
        Args:
            output_dir: Directorio donde se guardarán los archivos
        """
        self.output_dir = Path(output_dir) if output_dir else (Path.home() / "Downloads")
        self.output_dir.mkdir(exist_ok=True)
        
        # Obtener la ruta de FFmpeg incluido con imageio-ffmpeg
        self.ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    def clean_facebook_title(self, title):
        """
        Limpia el título de Facebook eliminando estadísticas y metadata
        
        Args:
            title: Título original del video
            
        Returns:
            str: Título limpio sin estadísticas
        """
        # Eliminar patrones de vistas y reacciones (ej: "77K views · 9.4K reactions")
        # Patrón: número + K/M/B + views/reactions/likes/shares
        patterns_to_remove = [
            r'\d+[KMB]?\s*views?\s*[·•]?\s*',
            r'\d+[KMB]?\s*reactions?\s*[·•]?\s*',
            r'\d+[KMB]?\s*likes?\s*[·•]?\s*',
            r'\d+[KMB]?\s*shares?\s*[·•]?\s*',
            r'\d+[KMB]?\s*comments?\s*[·•]?\s*',
        ]
        
        for pattern in patterns_to_remove:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Eliminar símbolos separadores solos
        title = re.sub(r'^[·•\-\s]+', '', title)
        title = re.sub(r'[·•\-\s]+$', '', title)
        
        # Limpiar espacios múltiples
        title = ' '.join(title.split())
        
        return title.strip() if title.strip() else 'Facebook Video'
    
    def sanitize_filename(self, filename):
        """
        Limpia el nombre del archivo eliminando caracteres inválidos para Windows
        
        Args:
            filename: Nombre del archivo a limpiar
            
        Returns:
            str: Nombre de archivo válido
        """
        # Caracteres inválidos en Windows: < > : " / \ | ? * y caracteres de control
        # También eliminar caracteres Unicode problemáticos
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(invalid_chars, '', filename)
        
        # Reemplazar caracteres Unicode problemáticos comunes
        replacements = {
            '｜': '-',
            '：': '-',
            '？': '',
            '！': '',
            '＃': '',
            '＠': '',
            '＆': 'and',
            '％': 'percent',
        }
        
        for old, new in replacements.items():
            filename = filename.replace(old, new)
        
        # Eliminar espacios múltiples y recortar
        filename = ' '.join(filename.split())
        
        # Limitar longitud del nombre (Windows tiene límite de 260 caracteres para ruta completa)
        if len(filename) > 200:
            filename = filename[:200]
        
        # Eliminar puntos y espacios al final
        filename = filename.rstrip('. ')
        
        return filename if filename else 'video'
    
    def is_tiktok_url(self, url):
        """Verifica si la URL es de TikTok"""
        return 'tiktok.com' in url.lower()
    
    def is_facebook_url(self, url):
        """Verifica si la URL es de Facebook"""
        return 'facebook.com' in url.lower() or 'fb.watch' in url.lower()

    def is_instagram_url(self, url):
        """Verifica si la URL es de Instagram"""
        return 'instagram.com' in url.lower()

    def download_and_convert(self, url, quality='320', progress_hook=None):
        """
        Descarga un video de YouTube/TikTok/Facebook y lo convierte a MP3
        
        Args:
            url: URL del video de YouTube, TikTok o Facebook
            quality: Calidad del audio ('320', '256', '192', '128', '96')
            
        Returns:
            str: Ruta del archivo MP3 descargado o None si hay error
        """
        try:
            # Configuración base para descargar audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': True,
                'ffmpeg_location': self.ffmpeg_path,
            }
            # Hook de progreso si está disponible
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # Configuración adicional para TikTok
            if self.is_tiktok_url(url):
                ydl_opts['http_headers'] = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            
            # Configuración adicional para Facebook
            elif self.is_facebook_url(url):
                ydl_opts['http_headers'] = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }

            # Configuración adicional para Instagram
            elif self.is_instagram_url(url):
                ydl_opts['http_headers'] = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Obtener información del video
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                # Limpiar título de Facebook si es necesario
                if self.is_facebook_url(url):
                    title = self.clean_facebook_title(title)
                
                # Sanitizar el título
                clean_title = self.sanitize_filename(title)
                
                # Actualizar la plantilla de salida con el título limpio
                ydl_opts['outtmpl'] = str(self.output_dir / f'{clean_title}.%(ext)s')
                
                # Crear nuevo descargador con la plantilla actualizada
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    ydl2.download([url])

                output_file = self.output_dir / f"{clean_title}.mp3"
                if self.is_tiktok_url(url):
                    platform = "TikTok"
                elif self.is_facebook_url(url):
                    platform = "Facebook"
                elif self.is_instagram_url(url):
                    platform = "Instagram"
                else:
                    platform = "YouTube"
                quality_label = f" [{quality} kbps]" if quality != '320' else ""
                print(f"{Fore.GREEN}  ✓ {Fore.CYAN}[MP3]{Fore.MAGENTA} [{platform}]{Fore.YELLOW}{quality_label}{Fore.WHITE} {title[:40]}{Style.RESET_ALL}")
                return str(output_file)

        except Exception as e:
            print(f"\n❌ Error al descargar: {str(e)}")
            return None

    def download_video_mp4(self, url, quality='best', progress_hook=None):
        """
        Descarga un video de YouTube/TikTok/Facebook en formato MP4
        Para TikTok y Facebook: descarga sin marca de agua
        
        Args:
            url: URL del video de YouTube, TikTok o Facebook
            quality: Calidad del video para YouTube ('2160p', '1440p', '1080p', '720p', '480p', '360p', 'best')
            
        Returns:
            str: Ruta del archivo MP4 descargado o None si hay error
        """
        try:
            # Configuración base para video
            ydl_opts = {
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': True,
                'ffmpeg_location': self.ffmpeg_path,
                'merge_output_format': 'mp4',
            }
            # Hook de progreso si está disponible
            if progress_hook:
                ydl_opts['progress_hooks'] = [progress_hook]
            
            # Configuración específica según la plataforma
            if self.is_tiktok_url(url):
                # Para TikTok: descargar sin marca de agua
                # Respetar calidad seleccionada si no es 'best'
                if quality != 'best':
                    try:
                        res = int(re.sub(r'[^0-9]', '', quality))
                    except Exception:
                        res = None
                    if res:
                        # Preferir MP4 dentro del límite de altura, con fallback razonable
                        ydl_opts['format'] = (
                            f"bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/"
                            f"best[height<={res}][ext=mp4]/"
                            f"best[height<={res}]/best"
                        )
                    else:
                        ydl_opts['format'] = 'best[ext=mp4]/best'
                else:
                    ydl_opts['format'] = 'best[ext=mp4]/best'
                ydl_opts['http_headers'] = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            elif self.is_facebook_url(url):
                # Para Facebook: descargar sin marca de agua
                # Respetar calidad seleccionada si no es 'best'
                if quality != 'best':
                    try:
                        res = int(re.sub(r'[^0-9]', '', quality))
                    except Exception:
                        res = None
                    if res:
                        ydl_opts['format'] = (
                            f"bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/"
                            f"best[height<={res}][ext=mp4]/"
                            f"best[height<={res}]/best"
                        )
                    else:
                        ydl_opts['format'] = 'best[ext=mp4]/best'
                else:
                    ydl_opts['format'] = 'best[ext=mp4]/best'
                ydl_opts['http_headers'] = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Cookie': ''
                }
            elif self.is_instagram_url(url):
                # Para Instagram: normalmente hay un único stream MP4
                if quality != 'best':
                    try:
                        res = int(re.sub(r'[^0-9]', '', quality))
                    except Exception:
                        res = None
                    if res:
                        ydl_opts['format'] = (
                            f"bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/"
                            f"best[height<={res}][ext=mp4]/"
                            f"best[height<={res}]/best"
                        )
                    else:
                        ydl_opts['format'] = 'best[ext=mp4]/best'
                else:
                    ydl_opts['format'] = 'best[ext=mp4]/best'
                ydl_opts['http_headers'] = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            else:
                # Para YouTube: calidad seleccionada
                if quality == 'best':
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    # Formato específico por resolución
                    ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality[:-1]}][ext=mp4]/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Obtener información del video
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                # Limpiar título de Facebook si es necesario
                if self.is_facebook_url(url):
                    title = self.clean_facebook_title(title)
                
                # Sanitizar el título
                clean_title = self.sanitize_filename(title)
                
                # Actualizar la plantilla de salida con el título limpio
                ydl_opts['outtmpl'] = str(self.output_dir / f'{clean_title}.%(ext)s')
                
                # Crear nuevo descargador con la plantilla actualizada
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    ydl2.download([url])

                output_file = self.output_dir / f"{clean_title}.mp4"
                if self.is_tiktok_url(url):
                    platform = "TikTok"
                    watermark_status = " [Sin marca de agua]" + (f" [{quality.upper()}]" if quality != 'best' else "")
                elif self.is_facebook_url(url):
                    platform = "Facebook"
                    watermark_status = f" [{quality.upper()}]" if quality != 'best' else ""
                elif self.is_instagram_url(url):
                    platform = "Instagram"
                    watermark_status = f" [{quality.upper()}]" if quality != 'best' else ""
                else:
                    platform = "YouTube"
                    watermark_status = f" [{quality.upper()}]" if quality != 'best' else ""
                print(f"{Fore.GREEN}  ✓ {Fore.BLUE}[MP4]{Fore.MAGENTA} [{platform}]{Fore.CYAN}{watermark_status}{Fore.WHITE} {title[:30]}{Style.RESET_ALL}")
                return str(output_file)

        except Exception as e:
            print(f"\n❌ Error al descargar: {str(e)}")
            return None

    def read_urls_from_file(self, file_path="url.txt"):
        """
        Lee URLs desde un archivo de texto

        Args:
            file_path: Ruta del archivo con las URLs

        Returns:
            list: Lista de URLs válidas
        """
        urls = []
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"\n⚠️  El archivo {file_path} no existe.")
            print(f"Creando archivo {file_path}...")
            file_path.write_text("# Agrega las URLs de YouTube, TikTok o Facebook aquí, una por línea\n")
            print(f"✅ Archivo creado. Agrega las URLs y vuelve a ejecutar el programa.\n")
            return urls

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorar líneas vacías y comentarios
                    if line and not line.startswith('#'):
                        urls.append(line)

            print(f"{Fore.GREEN} 📄 Se encontraron {Fore.YELLOW}{Style.BRIGHT}{len(urls)}{Style.RESET_ALL}{Fore.GREEN} URL(s){Style.RESET_ALL}")
            return urls

        except Exception as e:
            print(f"\n❌ Error al leer el archivo: {str(e)}")
            return urls

    def remove_url_from_file(self, url_to_remove, file_path="url.txt"):
        """
        Elimina una URL del archivo de texto

        Args:
            url_to_remove: URL a eliminar
            file_path: Ruta del archivo con las URLs
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return

        try:
            # Leer todas las líneas del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Filtrar la URL completada
            new_lines = []
            for line in lines:
                # Mantener comentarios y líneas vacías
                if line.strip().startswith('#') or not line.strip():
                    new_lines.append(line)
                # Mantener URLs que no coincidan con la completada
                elif line.strip() != url_to_remove:
                    new_lines.append(line)

            # Escribir el archivo actualizado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            # URL eliminada silenciosamente

        except Exception as e:
            print(f"\n⚠️  Error al actualizar el archivo: {str(e)}")


def cli_main():
    """Modo consola interactivo"""
    try:
        print(f"{Fore.CYAN}╔{'═' * 58}╗")
        print(f"{Fore.CYAN}║{Fore.MAGENTA}{'★ ★ ★ By Marshall ★ ★ ★':^56}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║{Fore.YELLOW}{Style.BRIGHT}{'Media Downloader - MP3 & MP4':^58}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║{Fore.MAGENTA}{'YouTube • TikTok • Facebook':^58}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║{Fore.WHITE}{'Descarga música y videos en alta calidad':^58}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚{'═' * 58}╝{Style.RESET_ALL}")

        # Crear instancia del descargador
        downloader = MediaDownloader()

        # Leer URLs desde archivo url.txt
        urls = downloader.read_urls_from_file("url.txt")

        if not urls:
            print(f"{Fore.YELLOW}⚠️  No hay URLs para descargar.")
            print(
                f"{Fore.WHITE}Agrega URLs al archivo {Fore.CYAN}'url.txt'{Fore.WHITE} (una por línea) y vuelve a ejecutar.\n{Style.RESET_ALL}")
            return

        # Preguntar formato al inicio
        print(f"{Fore.CYAN}┌{'─' * 58}┐")
        print(
            f"{Fore.CYAN}│{Fore.MAGENTA}{Style.BRIGHT} Selecciona el formato de descarga{' ' * 24}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}├{'─' * 58}┤{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}│ {Fore.GREEN}[1]{Fore.WHITE} 🎵 MP3  {Fore.CYAN}│ {Fore.WHITE}Audio de alta calidad (320 kbps){' ' * 11}{Fore.CYAN}│")
        print(
            f"{Fore.CYAN}│ {Fore.GREEN}[2]{Fore.WHITE} 🎬 MP4  {Fore.CYAN}│ {Fore.WHITE}Video completo en mejor resolución{' ' * 9}{Fore.CYAN}│")
        print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")

        try:
            format_choice = input(f"{Fore.YELLOW}  ➤ Tu elección: {Style.RESET_ALL}").strip()
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⚠️  Proceso cancelado por el usuario.{Style.RESET_ALL}")
            return

        # Determinar función de descarga y calidad
        quality_choice = 'best'
        audio_quality = '320'
        
        if format_choice == '1':
            # Preguntar calidad de audio para MP3
            print(f"{Fore.CYAN}┌{'─' * 58}┐")
            print(
                f"{Fore.CYAN}│{Fore.MAGENTA}{Style.BRIGHT} Selecciona la calidad de audio{' ' * 27}{Fore.CYAN}│{Style.RESET_ALL}")
            print(f"{Fore.CYAN}├{'─' * 58}┤{Style.RESET_ALL}")
            print(
                f"{Fore.CYAN}│ {Fore.GREEN}[1]{Fore.WHITE} 320 kbps  {Fore.CYAN}│ {Fore.WHITE}Máxima calidad - Archivo más grande{' ' * 6}{Fore.CYAN}│")
            print(
                f"{Fore.CYAN}│ {Fore.GREEN}[2]{Fore.WHITE} 256 kbps  {Fore.CYAN}│ {Fore.WHITE}Muy buena calidad - Equilibrado{' ' * 10}{Fore.CYAN}│")
            print(
                f"{Fore.CYAN}│ {Fore.GREEN}[3]{Fore.WHITE} 192 kbps  {Fore.CYAN}│ {Fore.WHITE}Buena calidad - Tamaño moderado{' ' * 10}{Fore.CYAN}│")
            print(
                f"{Fore.CYAN}│ {Fore.GREEN}[4]{Fore.WHITE} 128 kbps  {Fore.CYAN}│ {Fore.WHITE}Calidad estándar - Archivo pequeño{' ' * 7}{Fore.CYAN}│")
            print(
                f"{Fore.CYAN}│ {Fore.GREEN}[5]{Fore.WHITE} 96 kbps   {Fore.CYAN}│ {Fore.WHITE}Calidad básica - Archivo muy pequeño{' ' * 5}{Fore.CYAN}│")
            print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")

            try:
                audio_input = input(f"{Fore.YELLOW}  ➤ Tu elección: {Style.RESET_ALL}").strip()
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}⚠️  Proceso cancelado por el usuario.{Style.RESET_ALL}")
                return

            audio_quality_map = {
                '1': '320',
                '2': '256',
                '3': '192',
                '4': '128',
                '5': '96'
            }

            audio_quality = audio_quality_map.get(audio_input, '320')
            
            download_func = lambda url: downloader.download_and_convert(url, audio_quality)
            format_name = "MP3"
        elif format_choice == '2':
            # Verificar si hay URLs de YouTube
            has_youtube = any(not downloader.is_tiktok_url(url) and not downloader.is_facebook_url(url) for url in urls)

            if has_youtube:
                # Preguntar calidad para YouTube
                print(f"{Fore.CYAN}┌{'─' * 58}┐")
                print(
                    f"{Fore.CYAN}│{Fore.MAGENTA}{Style.BRIGHT} Selecciona la calidad para YouTube{' ' * 23}{Fore.CYAN}│{Style.RESET_ALL}")
                print(f"{Fore.CYAN}├{'─' * 58}┤{Style.RESET_ALL}")
                print(
                    f"{Fore.CYAN}│ {Fore.GREEN}[1]{Fore.WHITE} 4K (2160p)       {Fore.CYAN}│ {Fore.WHITE}Ultra HD - Máxima calidad{' ' * 9}{Fore.CYAN}│")
                print(
                    f"{Fore.CYAN}│ {Fore.GREEN}[2]{Fore.WHITE} 2K (1440p)       {Fore.CYAN}│ {Fore.WHITE}Quad HD - Excelente calidad{' ' * 7}{Fore.CYAN}│")
                print(
                    f"{Fore.CYAN}│ {Fore.GREEN}[3]{Fore.WHITE} Full HD (1080p)  {Fore.CYAN}│ {Fore.WHITE}Alta definición completa{' ' * 10}{Fore.CYAN}│")
                print(
                    f"{Fore.CYAN}│ {Fore.GREEN}[4]{Fore.WHITE} HD (720p)        {Fore.CYAN}│ {Fore.WHITE}Alta definición estándar{' ' * 10}{Fore.CYAN}│")
                print(
                    f"{Fore.CYAN}│ {Fore.GREEN}[5]{Fore.WHITE} SD (480p)        {Fore.CYAN}│ {Fore.WHITE}Definición estándar{' ' * 15}{Fore.CYAN}│")
                print(
                    f"{Fore.CYAN}│ {Fore.GREEN}[6]{Fore.WHITE} Baja (360p)      {Fore.CYAN}│ {Fore.WHITE}Menor tamaño de archivo{' ' * 11}{Fore.CYAN}│")
                print(
                    f"{Fore.CYAN}│ {Fore.GREEN}[0]{Fore.WHITE} Mejor disponible {Fore.CYAN}│ {Fore.WHITE}Automático - Mejor calidad{' ' * 8}{Fore.CYAN}│")
                print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}")

                try:
                    quality_input = input(f"{Fore.YELLOW}  ➤ Tu elección: {Style.RESET_ALL}").strip()
                except KeyboardInterrupt:
                    print(f"\n\n{Fore.YELLOW}⚠️  Proceso cancelado por el usuario.{Style.RESET_ALL}")
                    return

                quality_map = {
                    '1': '2160p',
                    '2': '1440p',
                    '3': '1080p',
                    '4': '720p',
                    '5': '480p',
                    '6': '360p',
                    '0': 'best'
                }

                quality_choice = quality_map.get(quality_input, 'best')

            download_func = lambda url: downloader.download_video_mp4(url, quality_choice)
            format_name = "MP4"
        else:
            download_func = lambda url: downloader.download_and_convert(url, '320')
            format_name = "MP3"

        print(f"{Fore.CYAN}{'━' * 60}")
        if format_name == "MP4" and quality_choice != 'best':
            print(
                f"{Fore.GREEN}{Style.BRIGHT}  🚀 Iniciando descarga: {Fore.YELLOW}{len(urls)}{Fore.GREEN} archivo(s) → {Fore.MAGENTA}{format_name} {Fore.CYAN}[{quality_choice.upper()}]{Style.RESET_ALL}")
        elif format_name == "MP3" and audio_quality != '320':
            print(
                f"{Fore.GREEN}{Style.BRIGHT}  🚀 Iniciando descarga: {Fore.YELLOW}{len(urls)}{Fore.GREEN} archivo(s) → {Fore.MAGENTA}{format_name} {Fore.CYAN}[{audio_quality} kbps]{Style.RESET_ALL}")
        else:
            print(
                f"{Fore.GREEN}{Style.BRIGHT}  🚀 Iniciando descarga: {Fore.YELLOW}{len(urls)}{Fore.GREEN} archivo(s) → Formato: {Fore.MAGENTA}{format_name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}\n")

        # Descargar todas las URLs
        successful = 0
        failed = 0
        urls_to_keep = []  # URLs que fallaron y deben mantenerse

        for i, url in enumerate(urls, 1):
            try:
                result = download_func(url)

                if result:
                    successful += 1
                    # Eliminar URL del archivo si la descarga fue exitosa
                    downloader.remove_url_from_file(url, "url.txt")
                else:
                    failed += 1
                    urls_to_keep.append(url)

            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}⚠️  Descarga interrumpida por el usuario.{Style.RESET_ALL}")
                print(
                    f"{Fore.CYAN}📊 Descargados hasta ahora: {Fore.GREEN}{successful}{Fore.CYAN} exitosas, {Fore.RED}{failed}{Fore.CYAN} fallidas{Style.RESET_ALL}")
                return

        # Resumen final
        print(f"\n{Fore.CYAN}╔{'═' * 58}╗")
        print(f"{Fore.CYAN}║{Fore.YELLOW}{Style.BRIGHT}{'📊 RESUMEN DE DESCARGAS':^57}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'═' * 58}╣{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║ {Fore.GREEN}✓ Exitosas: {Fore.YELLOW}{successful}{Fore.GREEN} ✗ Fallidas: {Fore.YELLOW}{failed}{Fore.GREEN} ● Total: {Fore.YELLOW}{len(urls)}{' ' * (58 - len(f'✓ Exitosas: {successful} ✗ Fallidas: {failed} ● Total: {len(urls)}') - 1)}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'═' * 58}╣{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Fore.GREEN}{Style.BRIGHT}{'✨ ¡Proceso completado exitosamente! ✨':^56}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 58}╝{Style.RESET_ALL}\n")

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Programa terminado por el usuario.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error inesperado: {str(e)}{Style.RESET_ALL}")


# -----------------------------
# WebApp (Flask)
# -----------------------------
app = Flask(__name__)

# Estado en memoria de descargas con progreso
DOWNLOAD_JOBS = {}

def _build_hook(job_id, item_index):
    def hook(d):
        job = DOWNLOAD_JOBS.get(job_id)
        if not job:
            return
        try:
            item = job['items'][item_index]
        except Exception:
            return
        status = d.get('status')
        if status == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                try:
                    pct = int(downloaded * 100 / total)
                except Exception:
                    pct = item.get('progress', 0)
            else:
                pct = item.get('progress', 0)
            item['progress'] = max(0, min(100, pct))
            item['status'] = 'downloading'
        elif status == 'finished':
            item['progress'] = 100
            item['status'] = 'processing'
        elif status == 'error':
            item['status'] = 'error'
    return hook

def _run_job(job_id, urls, fmt, audio_quality, video_quality):
    job = DOWNLOAD_JOBS.get(job_id)
    if not job:
        return
    downloader = MediaDownloader()
    for idx, url in enumerate(urls):
        item = {
            'url': url,
            'progress': 0,
            'status': 'pending',
            'filename': None,
            'error': None,
        }
        job['items'].append(item)
        hook = _build_hook(job_id, idx)
        try:
            if fmt == 'mp3':
                out = downloader.download_and_convert(url, audio_quality, progress_hook=hook)
            else:
                out = downloader.download_video_mp4(url, video_quality, progress_hook=hook)
            if out:
                item['status'] = 'completed'
                item['progress'] = 100
                item['filename'] = Path(out).name
            else:
                item['status'] = 'error'
                item['error'] = 'Fallo en descarga'
        except Exception as e:
            item['status'] = 'error'
            item['error'] = str(e)
    job['status'] = 'completed'


@app.get('/')
def index():
    return render_template_string(INDEX_TEMPLATE)


@app.post('/download')
def download_route():
    # Esta ruta ya no muestra la página de resultados.
    # Se conserva sólo para compatibilidad y redirige al inicio.
    return redirect(url_for('index'))


@app.get('/downloads')
def list_downloads():
    folder = Path.home() / 'Downloads'
    files = []
    if folder.exists():
        for p in sorted(folder.iterdir()):
            if p.is_file():
                files.append({'name': p.name, 'url': url_for('serve_download', filename=p.name)})
    return render_template_string(DOWNLOADS_TEMPLATE, files=files)


@app.get('/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory(str(Path.home() / 'Downloads'), filename, as_attachment=True, download_name=filename)

# API para abrir la carpeta Descargas en el sistema
@app.post('/api/open_downloads')
def api_open_downloads():
    try:
        downloads_path = Path.home() / 'Downloads'
        # Si estamos en Windows, intentamos enfocar una ventana existente de Explorer en "Descargas"
        if os.name == 'nt':
            try:
                import ctypes
                from ctypes import wintypes
                user32 = ctypes.windll.user32

                SW_RESTORE = 9

                found = {'hwnd': None}

                def enum_callback(hwnd, lparam):
                    # Solo ventanas visibles
                    if not user32.IsWindowVisible(hwnd):
                        return True
                    # Clase de ventana de Explorer
                    class_name_buf = ctypes.create_unicode_buffer(256)
                    user32.GetClassNameW(hwnd, class_name_buf, 256)
                    if class_name_buf.value != 'CabinetWClass':
                        return True
                    # Título de la ventana (normalmente nombre de carpeta)
                    title_buf = ctypes.create_unicode_buffer(512)
                    user32.GetWindowTextW(hwnd, title_buf, 512)
                    title = (title_buf.value or '').strip().lower()
                    # Coincidimos "Descargas" o "Downloads"
                    if ('descargas' in title) or ('downloads' in title):
                        # Restaurar si está minimizada y llevar al frente
                        user32.ShowWindow(hwnd, SW_RESTORE)
                        user32.SetForegroundWindow(hwnd)
                        found['hwnd'] = hwnd
                        return False  # detener enumeración
                    return True

                EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                user32.EnumWindows(EnumProc(enum_callback), 0)

                if found['hwnd']:
                    return jsonify({'ok': True, 'focused': True})
            except Exception:
                # Si algo falla en el enfoque, continuamos con la apertura normal
                pass

            # No se encontró una ventana existente: abrir y traer al frente
            os.startfile(str(downloads_path))
            # Intento rápido de enfoque tras apertura
            try:
                import time as _time
                _time.sleep(0.6)
                import ctypes
                from ctypes import wintypes
                user32 = ctypes.windll.user32
                SW_RESTORE = 9
                found = {'hwnd': None}
                def enum_callback(hwnd, lparam):
                    if not user32.IsWindowVisible(hwnd):
                        return True
                    class_name_buf = ctypes.create_unicode_buffer(256)
                    user32.GetClassNameW(hwnd, class_name_buf, 256)
                    if class_name_buf.value != 'CabinetWClass':
                        return True
                    title_buf = ctypes.create_unicode_buffer(512)
                    user32.GetWindowTextW(hwnd, title_buf, 512)
                    title = (title_buf.value or '').strip().lower()
                    if ('descargas' in title) or ('downloads' in title):
                        user32.ShowWindow(hwnd, SW_RESTORE)
                        user32.SetForegroundWindow(hwnd)
                        found['hwnd'] = hwnd
                        return False
                    return True
                EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                user32.EnumWindows(EnumProc(enum_callback), 0)
            except Exception:
                pass
            return jsonify({'ok': True, 'opened': True})

        # macOS
        if sys.platform == 'darwin':
            subprocess.Popen(['open', str(downloads_path)])
            return jsonify({'ok': True})

        # Linux / otros
        subprocess.Popen(['xdg-open', str(downloads_path)])
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.post('/api/download')
def api_download():
    data = request.get_json(silent=True) or {}
    urls = data.get('urls', [])
    fmt = data.get('format', 'mp3')
    audio_quality = data.get('audio_quality', '320')
    video_quality = data.get('video_quality', 'best')
    downloader = MediaDownloader()
    items = []
    for url in urls:
        try:
            if fmt == 'mp3':
                out = downloader.download_and_convert(url, audio_quality)
            else:
                out = downloader.download_video_mp4(url, video_quality)
            items.append({'url': url, 'file': out, 'success': bool(out)})
        except Exception as e:
            items.append({'url': url, 'file': None, 'success': False, 'error': str(e)})
    return jsonify({'results': items})


def run_server():
    port = int(os.environ.get('PORT', 5000))
    host = '127.0.0.1'
    threading.Thread(target=lambda: (time.sleep(1), webbrowser.open(f'http://{host}:{port}/')), daemon=True).start()
    app.run(host=host, port=port, debug=False)

# API para progreso en tiempo real
@app.post('/api/start_download')
def api_start_download():
    data = request.get_json(silent=True) or {}
    urls = data.get('urls', [])
    fmt = data.get('format', 'mp3')
    audio_quality = data.get('audio_quality', '320')
    video_quality = data.get('video_quality', 'best')
    job_id = str(uuid.uuid4())
    DOWNLOAD_JOBS[job_id] = {'id': job_id, 'status': 'running', 'items': []}
    t = threading.Thread(target=_run_job, args=(job_id, urls, fmt, audio_quality, video_quality), daemon=True)
    t.start()
    return jsonify(DOWNLOAD_JOBS[job_id])

@app.get('/api/progress/<job_id>')
def api_progress(job_id):
    job = DOWNLOAD_JOBS.get(job_id)
    if not job:
        return jsonify({'error': 'not_found'}), 404
    return jsonify(job)


if __name__ == "__main__":
    # Por defecto, ejecuta la webapp. Para CLI, ejecutar con env MODE=cli
    if os.environ.get('MODE', 'web') == 'cli':
        cli_main()
    else:
        run_server()
 
