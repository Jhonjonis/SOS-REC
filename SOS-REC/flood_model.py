import os
import numpy as np
from typing import List, Optional, Dict, Any
from joblib import load


class FloodPredictor:
    """Classe simples para estimar risco de inundação.

    Estratégia:
    - Se existir um modelo treinado (joblib), usa-o para predizer com features simples.
    - Caso contrário, aplica uma heurística baseada em sensores de distância (nivel d'água) e
      condições meteorológicas (chuva, umidade).
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        if model_path and os.path.exists(model_path):
            try:
                self.model = load(model_path)
            except Exception:
                self.model = None

    def _heuristic_score(self, distances: List[float], weather: Dict[str, Any]) -> float:
        # features
        if len(distances) == 0:
            mean_dist = 9999.0
            last = mean_dist
        else:
            arr = np.array(distances)
            mean_dist = float(np.mean(arr))
            last = float(arr[-1])

        rain_1h = 0.0
        if isinstance(weather, dict):
            # OpenWeatherMap may include 'rain': {'1h': value}
            rain = weather.get('rain') or {}
            rain_1h = float(rain.get('1h', 0.0)) if isinstance(rain, dict) else 0.0
            humidity = float(weather.get('main', {}).get('humidity', 0))
            temp = float(weather.get('main', {}).get('temp', 0))
        else:
            humidity = 0.0
            temp = 0.0

        score = 0.0
        # nível d'água baixo (valor de distância pequeno) aumenta risco
        if mean_dist < 30:  # cm threshold (ajustável)
            score += 0.5
        elif mean_dist < 80:
            score += 0.2

        # se o nível caiu rapidamente (última leitura muito menor que média)
        if mean_dist < 9999 and last < (mean_dist * 0.6):
            score += 0.15

        # chuva recente aumenta risco (mm/h)
        if rain_1h >= 20:
            score += 0.3
        elif rain_1h >= 5:
            score += 0.1

        # umidade alta contribui
        if humidity >= 85:
            score += 0.05

        # temperatura muito baixa/alta - efeito pequeno (placeholder)
        # normaliza e limita em [0,1]
        score = max(0.0, min(1.0, score))
        return score

    def _risk_level(self, score: float) -> str:
        if score >= 0.65:
            return 'alto'
        if score >= 0.35:
            return 'médio'
        return 'baixo'

    def predict(self, distances: List[float], weather: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna um dicionário com `score` (0-1), `nivel` e `recomendacao`.

        Se um modelo sklearn estiver carregado, tenta usar `model.predict_proba`.
        """
        features = {
            'mean_distance': float(np.mean(distances)) if len(distances) else None,
            'last_distance': float(distances[-1]) if len(distances) else None,
            'rain_1h': float((weather.get('rain') or {}).get('1h', 0.0)) if isinstance(weather, dict) else 0.0,
            'humidity': float(weather.get('main', {}).get('humidity', 0)) if isinstance(weather, dict) else 0.0,
            'temp': float(weather.get('main', {}).get('temp', 0)) if isinstance(weather, dict) else 0.0,
        }

        if self.model is not None:
            try:
                # Modelo espera um vetor 2D
                X = [
                    [
                        features['mean_distance'] or 9999.0,
                        features['last_distance'] or 9999.0,
                        features['rain_1h'],
                        features['humidity'],
                        features['temp'],
                    ]
                ]
                if hasattr(self.model, 'predict_proba'):
                    proba = self.model.predict_proba(X)[0]
                    # assume classe 1 é inundação
                    score = float(proba[1])
                else:
                    pred = self.model.predict(X)[0]
                    score = float(pred)
            except Exception:
                score = self._heuristic_score(distances, weather)
        else:
            score = self._heuristic_score(distances, weather)

        nivel = self._risk_level(score)
        recomendacao = self._recommendation(nivel)

        return {
            'score': round(score, 3),
            'nivel': nivel,
            'recomendacao': recomendacao,
            'features': features,
        }

    def _recommendation(self, nivel: str) -> str:
        if nivel == 'alto':
            return 'Risco alto: acionar alertas, evacuar áreas baixas e interromper tráfego.'
        if nivel == 'médio':
            return 'Risco médio: monitorar, preparar equipes e alertar população.'
        return 'Risco baixo: situação estável, continue monitorando.'

    def predict_from_db(self, conn, limit: int = 10, weather: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Busca as últimas `limit` leituras da tabela `distancias` e prediz usando `predict`."""
        distances = []
        try:
            cur = conn.cursor()
            cur.execute("SELECT valor FROM distancias ORDER BY timestamp DESC LIMIT %s;", (limit,))
            rows = cur.fetchall()
            # rows estão em ordem decrescente — reverte para cronológica
            distances = [float(r[0]) for r in reversed(rows)]
            cur.close()
        except Exception:
            distances = []

        weather = weather or {}
        return self.predict(distances, weather)
