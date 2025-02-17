from ultralytics import YOLO
import supervision as sv
import sys 
import pickle
import os
sys.path.append('../')


class CourtKeypointDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
    
    def get_court_keypoints(self, frames,read_from_stub=False, stub_path=None):

        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                court_keypoints = pickle.load(f)
            return court_keypoints
        
        batch_size=20
        court_keypoints = []
        for i in range(0,len(frames),batch_size):
            detections_batch = self.model.predict(frames[i:i+batch_size],conf=0.5)
            for detection in detections_batch:
                court_keypoints.append(detection.keypoints)

        if stub_path is not None:
            with open(stub_path,'wb') as f:
                pickle.dump(court_keypoints,f)
        
        return court_keypoints
    
    def draw_court_keypoints(self, frames, court_keypoints):
        vertex_annotator = sv.VertexAnnotator(
            color=sv.Color.from_hex('#d313a2'),
            radius=5)
        
        output_frames = []
        for index,frame in enumerate(frames):
            annotated_frame = frame.copy()

            keypoints = court_keypoints[index]
            annotated_frame = vertex_annotator.annotate(
                scene=annotated_frame,
                key_points=keypoints)
            output_frames.append(annotated_frame)

        return output_frames