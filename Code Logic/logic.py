import time
from ultralytics import YOLO
import cv2

# Assuming cap and model are defined and initialized before this code segment
# Also, make sure to import necessary libraries and classes

# Define a dictionary to store the last time each box was seen
model = YOLO("/content/drive/MyDrive/Apollo Tires/01 12 23/best (3).pt")
video_path = "/content/drive/MyDrive/Apollo Tires/videoTest1.ts"
cap = cv2.VideoCapture(video_path)
output_path = '/content/drive/MyDrive/Apollo Tires/3 12 23/output_video.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = cap.get(cv2.CAP_PROP_FPS)
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
last_seen_times = {}
start_time = time.time()
while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model.track(frame, persist=True)

        line_positions = [0, 100, 200, 300, 400, 500, 600, 700, 800]
        for pos in line_positions:
            cv2.line(frame, (0, pos), (frame.shape[1], pos), (0, 255, 0), 2)
        current_time = time.time();
        for result in results:
            for box in result.boxes:
                box_id = str(box.id.tolist()[0])
                box_coords = box.xyxy.tolist()

                cv2.rectangle(frame, (int(box_coords[0][0]), int(box_coords[0][1])),
                              (int(box_coords[0][2]), int(box_coords[0][3])), (0, 255, 0), 2)
                cv2.putText(frame, box_id, (int(box_coords[0][0]), int(box_coords[0][1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)





                if(box_id in last_seen_times):
                    if(box_coords[0][1] > line_positions[-1]):
                        del last_seen_times[box_id]
                        continue
                    if(last_seen_times[box_id][0] < box_coords[0][1]):
                        idx = line_positions.index(last_seen_times[box_id][0])
                        last_seen_times[box_id][0] = line_positions[idx + 1]
                        last_seen_times[box_id][1] = current_time
                    else:
                        if(current_time - last_seen_times[box_id][1] > 20):
                            cv2.rectangle(frame, (int(box_coords[0][0]), int(box_coords[0][1])),
                              (int(box_coords[0][2]), int(box_coords[0][3])), (0, 0, 255), 5)
                            pass
                        pass
                else:
                    for pos in line_positions:
                        if(box_coords[0][1] < pos):
                            last_seen_times[box_id] = [pos, current_time]
                            break



        # for box_id, last_seen_time in last_seen_times.items():
        #     if current_time - last_seen_time > 8:
        #         cv2.rectangle(frame, (int(box_coords[0][0]), int(box_coords[0][1])),
        #                       (int(box_coords[0][2]), int(box_coords[0][3])), (0, 0, 255), 3)

        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
out.release()
