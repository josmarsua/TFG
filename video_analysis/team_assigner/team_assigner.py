from sklearn.cluster import KMeans
import numpy as np
import supervision as sv

class TeamAssigner:
    def __init__(self):
        self.team_colors = {}      # team_id : color
        self.player_team_dict = {} # player_id : team_id
        self.kmeans = None

    def get_player_color(self, frame, bbox):
        cropped = sv.crop_image(frame, np.array(bbox, dtype=int))
        if cropped is None or cropped.size == 0:
            return None

        h, w, _ = cropped.shape
        crop_size = min(h, w) // 3
        cx, cy = w // 2, h // 2
        start_x, end_x = max(cx - crop_size // 2, 0), min(cx + crop_size // 2, w)
        start_y, end_y = max(cy - crop_size // 2, 0), min(cy + crop_size // 2, h)
        center_crop = cropped[start_y:end_y, start_x:end_x]

        if center_crop.size == 0:
            return None

        image_2d = center_crop.reshape(-1, 3)
        image_2d = np.unique(image_2d, axis=0)
        if len(image_2d) < 2:
            return None

        kmeans = KMeans(n_clusters=min(3, len(image_2d)), random_state=42).fit(image_2d)
        labels, counts = np.unique(kmeans.labels_, return_counts=True)
        dominant_cluster = labels[np.argmax(counts)]

        return kmeans.cluster_centers_[dominant_cluster]

    def assign_team_color(self, frame, player_detections):
        player_colors = []
        for _, detection in player_detections.items():
            bbox = detection.get("bbox")
            color = self.get_player_color(frame, bbox)
            if color is not None:
                player_colors.append(color)

        if len(player_colors) < 2:
            return

        kmeans = KMeans(n_clusters=2, random_state=42)
        kmeans.fit(np.array(player_colors))
        self.kmeans = kmeans
        self.team_colors[1], self.team_colors[2] = kmeans.cluster_centers_

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
