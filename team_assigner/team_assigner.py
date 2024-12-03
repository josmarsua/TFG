from sklearn.cluster import KMeans
import numpy as np
import cv2

class TeamAssigner:
    def __init__(self):
        self.team_colors = {}      # team_id : color
        self.player_team_dict = {} # player_id : team_id
        self.kmeans = None

    def get_clustering_model(self, image, n_clusters=3):
        # Convert image to 2D
        image_2d = image.reshape(-1, 3)

        # K-means with customizable clusters
        kmeans = KMeans(n_clusters=n_clusters, init="k-means++", n_init=10, random_state=42)
        kmeans.fit(image_2d)

        return kmeans

    def get_player_color(self, frame, bbox):
        image = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]  # Image of a player
        height, width, _ = image.shape

        # Define crop size dynamically based on bbox size
        crop_size = min(height, width) // 3  # Use 1/3 of the bounding box for better representation

        # Calculate crop coordinates centered in the bbox
        center_x, center_y = width // 2, height // 2
        start_x = max(center_x - crop_size // 2, 0)
        end_x = min(center_x + crop_size // 2, width)
        start_y = max(center_y - crop_size // 2, 0)
        end_y = min(center_y + crop_size // 2, height)

        # Crop the image
        cropped_image = image[start_y:end_y, start_x:end_x]

        # Apply KMeans to identify dominant colors
        kmeans = self.get_clustering_model(cropped_image, n_clusters=3)

        # Determine the most frequent cluster
        labels, counts = np.unique(kmeans.labels_, return_counts=True)
        dominant_cluster = labels[np.argmax(counts)]

        # Get the dominant color
        dominant_color = kmeans.cluster_centers_[dominant_cluster]

        return dominant_color

    def assign_team_color(self, frame, player_detections):
        player_colors = []
        for _, player_detection in player_detections.items():
            bbox = player_detection['bbox']
            player_color = self.get_player_color(frame, bbox)
            player_colors.append(player_color)

        player_colors = np.array(player_colors)

        # Assign a color for each team using KMeans
        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=10, random_state=42)
        kmeans.fit(player_colors)

        self.kmeans = kmeans

        self.team_colors[1] = kmeans.cluster_centers_[0]
        self.team_colors[2] = kmeans.cluster_centers_[1]

    def get_player_team(self, frame, player_bbox, player_id):
        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]

        player_color = self.get_player_color(frame, player_bbox)

        # Predict team using KMeans, with tolerance for color matching
        team_id = self.kmeans.predict(player_color.reshape(1, -1))[0] + 1

        self.player_team_dict[player_id] = team_id

        return team_id
