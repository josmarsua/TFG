import cv2
import numpy as np

class ViewTransformer:
    def __init__(self, source: np.ndarray, target: np.ndarray):
        if source.shape != target.shape:
            raise ValueError("Las matrices de puntos deben tener la misma forma.")
        if source.shape[1] != 2:
            raise ValueError("Las matrices de puntos deben ser coordenadas 2D.")
        
        source = source.astype(np.float32)
        target = target.astype(np.float32)

        # Calcular la matriz de homografía
        self.H, _ = cv2.findHomography(source, target)
        if self.H is None:
            raise ValueError("No se pudo calcular la matriz de homografía.")
        
    def transform_points(self, points: np.ndarray) -> np.ndarray:
        """
        Transforma un conjunto de puntos usando la matriz de homografía.
        """
        if points.size == 0:
            return points
        
        if points.shape[1] != 2:
            raise ValueError("Los puntos deben ser coordenadas 2D.")
        
        points = points.reshape(-1, 1, 2).astype(np.float32)
        points = cv2.perspectiveTransform(points, self.H)
        return points.reshape(-1,2).astype(np.float32)


