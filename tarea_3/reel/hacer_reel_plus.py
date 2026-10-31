"""Reel con imágenes por escena y música de fondo, sobre el pipeline de la sesión 15.

    python hacer_reel_plus.py --voz mi_voz.m4a --autor "Renato Gates Rojas" \
        --fuente "SBS, Reporte de Indicadores de Inclusion Financiera, junio 2026" \
        --tts Qwen/Qwen3-TTS-12Hz-0.6B-Base

Reutiliza reel.py del curso para la voz clonada, los subtítulos y el control de calidad.
Lo único que cambia es el dibujo del cuadro (ahora con una imagen por escena) y el audio
(narración + cama musical).
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image

AQUI = Path(__file__).resolve().parent

p = argparse.ArgumentParser()
p.add_argument("--voz", required=True)
p.add_argument("--autor", required=True)
p.add_argument("--fuente", required=True)
p.add_argument("--sesion", default=None, help="carpeta sessions/15-texto-a-reel del curso")
p.add_argument("--recursos", default=str(AQUI / "recursos"))
p.add_argument("--salidas", default=str(AQUI / "salidas"))
p.add_argument("--device", default="cpu")
p.add_argument("--tts", default="Qwen/Qwen3-TTS-12Hz-0.6B-Base")
p.add_argument("--musica", type=float, default=0.10, help="volumen de la cama musical, 0 la apaga")
p.add_argument("--velocidad", type=float, default=1.0)
a = p.parse_args()

sesion = Path(a.sesion) if a.sesion else (
    AQUI.parents[2] / "Data-Science-Python" / "sessions" / "15-texto-a-reel"
)
if not (sesion / "reel.py").exists():
    sys.exit(f"No encontré reel.py en {sesion}. Pásame la ruta con --sesion.")
sys.path.insert(0, str(sesion))
import reel  # noqa: E402

RECURSOS = Path(a.recursos)
SALIDAS = Path(a.salidas)
SALIDAS.mkdir(parents=True, exist_ok=True)
IMG_Y, IMG_ALTO = 410, 520
BLOQUE_Y0, BLOQUE_Y1 = 960, 1240


def escena_con_imagen(e, indice):
    """Capa con la imagen de la escena arriba y la cifra con su etiqueta abajo."""
    capa = Image.new("RGBA", (reel.ANCHO, reel.ALTO), (0, 0, 0, 0))
    ruta = RECURSOS / f"escena_{indice + 1}.png"
    if ruta.exists():
        img = Image.open(ruta).convert("RGBA")
        if img.height != IMG_ALTO:
            img = img.resize((round(img.width * IMG_ALTO / img.height), IMG_ALTO), Image.LANCZOS)
        capa.paste(img, ((reel.ANCHO - img.width) // 2, IMG_Y), img)

    d = reel.ImageDraw.Draw(capa)
    ancho = reel.ANCHO - 2 * reel.MARGEN

    def alto(texto, f):
        return -d.textbbox((0, 0), texto, font=f, anchor="ls")[1]

    lineas = []
    if e.get("cifra"):
        f = reel._ajustar(d, e["cifra"], "Oswald", 700, ancho, 190, minimo=90)
        lineas.append((e["cifra"], f, reel.TEXTO, alto(e["cifra"], f), 34))
        fe, color = reel._fuente("PublicSans", 46, 600), reel.SUAVE
    else:
        fe, color = reel._fuente("Oswald", 86, 600), reel.TEXTO
    lineas += [(x, fe, color, alto("H", fe), int(fe.size * 0.42))
               for x in reel._envolver(d, e["etiqueta"], fe, ancho)]

    y = (BLOQUE_Y0 + BLOQUE_Y1 - sum(h + g for *_, h, g in lineas) + lineas[-1][4]) / 2
    for texto, f, color, h, g in lineas:
        y += h
        d.text((reel.MARGEN, y), texto, font=f, fill=color, anchor="ls")
        y += g
    return capa


def video_con_musica(guion, narracion, ruta, fuente_datos, autor, volumen):
    ruta = Path(ruta)
    wav = ruta.with_suffix(".wav")
    sf.write(wav, narracion.audio, narracion.sr)

    base = reel._base(guion["titulo"], fuente_datos, autor)
    capas = [escena_con_imagen(e, i) for i, e in enumerate(guion["escenas"])]
    bloques = reel._bloques(narracion.palabras)
    fuente_sub = reel._fuente("PublicSans", 62, 800)

    musica = RECURSOS / "musica.wav"
    usar_musica = volumen > 0 and musica.exists()
    dur = narracion.duracion

    cmd = [reel.FFMPEG, "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{reel.ANCHO}x{reel.ALTO}",
           "-r", str(reel.FPS), "-i", "-", "-i", str(wav)]
    if usar_musica:
        cmd += ["-i", str(musica),
                "-filter_complex",
                f"[2:a]volume={volumen},afade=t=in:d=2,"
                f"afade=t=out:st={max(0, dur - 3):.2f}:d=3[m];"
                f"[1:a][m]amix=inputs=2:duration=first:dropout_transition=0,"
                f"loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
            "-shortest", "-movflags", "+faststart", str(ruta)]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(dur * reel.FPS)):
        proc.stdin.write(reel._cuadro(base, capas, narracion, k / reel.FPS,
                                      bloques, fuente_sub).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg falló al escribir el video")
    return ruta


if __name__ == "__main__":
    t0 = time.time()
    archivo_guion = SALIDAS / "guion.json"
    if not archivo_guion.exists():
        sys.exit(f"Falta {archivo_guion}. Copia ahí tu guion.json antes de correr esto.")
    guion = json.loads(archivo_guion.read_text(encoding="utf-8"))

    faltan = [i + 1 for i in range(len(guion["escenas"]))
              if not (RECURSOS / f"escena_{i + 1}.png").exists()]
    if faltan:
        print(f"   Aviso: sin imagen para las escenas {faltan}; saldrán solo con la cifra.")

    voz = reel.Voz(a.voz, modelo=a.tts, device=a.device)
    reel._reloj(f"voz cargada; referencia: «{voz.texto_ref}»", t0)

    narracion = reel.narrar(voz, guion, velocidad=a.velocidad)
    archivo_guion.write_text(json.dumps(guion, ensure_ascii=False, indent=2), encoding="utf-8")
    reel._reloj(f"narración: {narracion.duracion:.1f} s; WER por escena: "
                + ", ".join(f"{e['wer']:.2f}" for e in guion["escenas"]), t0)

    reel.subtitulos(narracion, guion)
    reel.a_srt(narracion, SALIDAS / "reel.srt")
    reel._reloj(f"subtítulos: {len(narracion.palabras)} palabras", t0)

    video_con_musica(guion, narracion, SALIDAS / "reel.mp4", a.fuente, a.autor, a.musica)

    capas = [escena_con_imagen(e, i) for i, e in enumerate(guion["escenas"])]
    reel._cuadro(reel._base(guion["titulo"], a.fuente, a.autor), capas, narracion,
                 narracion.escenas[1][0] + 1.0, reel._bloques(narracion.palabras),
                 reel._fuente("PublicSans", 62, 800)).save(SALIDAS / "portada.png")
    reel.posts(guion, SALIDAS / "posts.md")
    reel._reloj(f"listo: {SALIDAS / 'reel.mp4'} ({narracion.duracion:.0f} s)", t0)
