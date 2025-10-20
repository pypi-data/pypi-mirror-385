from typing import Iterable, List, Tuple
from sklearn.svm import LinearSVC

_LABEL_MAP = {'N': 'NORMAL', 'B': 'BAIXA', 'A': 'ALTA'}

def train_default_model() -> LinearSVC:
    """Treina e retorna um modelo LinearSVC com exemplos didáticos.

    Retorna
    -------
    LinearSVC
        Modelo treinado com rótulos 'N', 'B', 'A'.
    """
    dados_treino = [
        [120, 80],[140, 90],[100, 70],[120, 85],[100, 70],
        [140, 91],[120, 80],[140, 90],[100, 70],[120, 85],
        [100, 70],[140, 91],[120, 80],[140, 90],[100, 70],
        [120, 85],[121, 83],[140, 91],[140, 91],[100, 70],[100, 70]
    ]
    rotulos_treino = ['N','A','B','N','B','A','N','A','B','N','B','A','N','A','B','N','N','A','A','B','B']
    model = LinearSVC()
    model.fit(dados_treino, rotulos_treino)
    return model


def predict_labels(model: LinearSVC, afericoes: Iterable[Tuple[int, int]]) -> List[str]:
    """Classifica uma sequência de aferições (sistólica, diastólica).

    Parâmetros
    ---------
    model: LinearSVC
        Modelo treinado.
    afericoes: iterable de (int, int)
        Pares (sistólica, diastólica).

    Retorna
    -------
    List[str]
        Lista com rótulos em português: 'BAIXA' | 'NORMAL' | 'ALTA'.
    """
    pares = list(afericoes)
    y_pred = model.predict(pares)
    return [_LABEL_MAP[y] for y in y_pred]
