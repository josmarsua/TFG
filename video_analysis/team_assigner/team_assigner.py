from sklearn.cluster import KMeans
import numpy as np
import cv2

class TeamAssigner:
    def __init__(self):
        self.team_colors = {}      # team_id : color
        self.player_team_dict = {} # player_id : team_id
        self.kmeans = None

    def get_clustering_model(self, image, n_clusters=3):
        image_2d = image.reshape(-1, 3)
        image_2d = np.unique(image_2d, axis=0)
        n_clusters = min(n_clusters, len(image_2d))
        if n_clusters < 2:
            return None
        kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init=10, random_state=42)
        kmeans.fit(image_2d)
        return kmeans

    def get_player_color(self, frame, bbox):
        image = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
        height, width, _ = image.shape

        crop_size = min(height, width) // 3
        center_x, center_y = width // 2, height // 2
        start_x = max(center_x - crop_size // 2, 0)
        end_x = min(center_x + crop_size // 2, width)
        start_y = max(center_y - crop_size // 2, 0)
        end_y = min(center_y + crop_size // 2, height)

        cropped_image = image[start_y:end_y, start_x:end_x]

        if cropped_image.size == 0:
            return None

        kmeans = self.get_clustering_model(cropped_image, n_clusters=3)
        if not kmeans:
            return None

        labels, counts = np.unique(kmeans.labels_, return_counts=True)
        dominant_cluster = labels[np.argmax(counts)]
        dominant_color = kmeans.cluster_centers_[dominant_cluster]

        return dominant_color

    def assign_team_color(self, frame, player_detections):
        player_colors = []
        for _, player_detection in player_detections.items():
            bbox = player_detection['bbox']
            color = self.get_player_color(frame, bbox)
            if color is not None:
                player_colors.append(color)

        if len(player_colors) < 2:
            return
        
        player_colors = np.array(player_colors)

        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=10, random_state=42)
        kmeans.fit(player_colors)
        centers = kmeans.cluster_centers_

        self.kmeans = kmeans
        self.team_colors[1] = centers[0]
        self.team_colors[2] = centers[1]

    def get_player_team(self, frame, bbox, player_id):
        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]

        if self.kmeans is None:
            return 0

        color = self.get_player_color(frame, bbox)
        if color is None:
            return 0

        team_id = self.kmeans.predict([color])[0] + 1
        self.player_team_dict[player_id] = team_id

        return team_id
