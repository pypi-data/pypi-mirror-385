import argparse
from . import train_default_model, predict_labels

def main():
    p = argparse.ArgumentParser(description="Classificador simples de Pressão Arterial (didático)")
    p.add_argument("--pares", nargs="+", required=True,
                   help="Pares sistolica,diastolica. Ex.: --pares 120,80 140,90 100,70")
    args = p.parse_args()

    afericoes = []
    for par in args.pares:
        try:
            s, d = par.split(",")
            afericoes.append((int(s), int(d)))
        except Exception:
            raise SystemExit(f"Par inválido: {par}. Use o formato sistolica,diastolica (ex.: 120,80)")

    model = train_default_model()
    rotulos = predict_labels(model, afericoes)
    for (s, d), r in zip(afericoes, rotulos):
        print(f"{s}/{d} => {r}")

if __name__ == "__main__":
    main()
