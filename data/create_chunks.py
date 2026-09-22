"""
Parteix el corpus (1 frase per línia) en fitxers .txt de N frases cadascun.

Per a cada mida N es genera la carpeta data/chunks/chunk_<N> amb 10000 / N fitxers:
    chunk_1   -> 10000 fitxers d'1 frase
    chunk_10  ->  1000 fitxers de 10 frases
    chunk_100 ->   100 fitxers de 100 frases
    chunk_500 ->    20 fitxers de 500 frases
    chunk_2k  ->     5 fitxers de 2000 frases
    chunk_5k  ->     2 fitxers de 5000 frases
    chunk_10k ->     1 fitxer de 10000 frases

Ús:  python data/create_chunks.py
"""

from pathlib import Path

CHUNKS_DIR = Path(__file__).resolve().parent / "chunks"
CORPUS_PATH = CHUNKS_DIR / "corpus_10k.txt"

# nom de la carpeta -> frases per fitxer
CHUNK_SIZES = {
    "chunk_1": 1,
    "chunk_10": 10,
    "chunk_100": 100,
    "chunk_500": 500,
    "chunk_2k": 2000,
    "chunk_5k": 5000,
    "chunk_10k": 10000,
}


def load_sentences(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def write_chunks(sentences: list[str], out_dir: Path, size: int) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Esborra els chunks d'execucions anteriors (no toca altres fitxers, p.ex. a.txt)
    for old in out_dir.glob("chunk_*.txt"):
        old.unlink()

    n_files = 0
    for i, start in enumerate(range(0, len(sentences), size)):
        chunk = sentences[start:start + size]
        (out_dir / f"chunk_{i:05d}.txt").write_text("\n".join(chunk) + "\n", encoding="utf-8")
        n_files += 1
    return n_files


def main() -> None:
    sentences = load_sentences(CORPUS_PATH)
    print(f"Corpus: {len(sentences)} frases ({CORPUS_PATH})")

    for name, size in CHUNK_SIZES.items():
        n_files = write_chunks(sentences, CHUNKS_DIR / name, size)
        print(f"  {name:<10} {size:>6} frases/fitxer -> {n_files:>6} fitxers")


if __name__ == "__main__":
    main()
