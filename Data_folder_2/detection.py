import time
from ultralytics import YOLO
import cv2
import pandas as pd


model = YOLO("/content/drive/MyDrive/Apollo Tires/01 12 23/best (3).pt")
video_path = "/content/drive/MyDrive/Apollo Tires/videoTest1.ts"
cap = cv2.VideoCapture(video_path)
output_path = '/content/drive/MyDrive/Apollo Tires/16 02 2024/output1.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = cap.get(cv2.CAP_PROP_FPS)
frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
last_seen_times = {}
start_time = time.time()


report = {
    'tyre_management': [],
    'jam_management': [],
    'id_management': []
}
jam_confirmed_count = 0
id_check_time = 5
jam_check_time = 30
jam_confirm_time = 60
id_confirm_time = 30
tyre_management = {}
jam_management = {}
id_management = {}
last_frame = []
tracking_line = [0, 100, 200, 300, 400, 500, 600, 700, 800]


def delete_id(id):
    if id in id_management:
        del id_management[id]

def delete_jam(id):
    if id in jam_management:
        del jam_management[id]

def delete_tyre(id):
    del tyre_management[id]
    delete_id(id)
    delete_jam(id)

def jam_manager(current_time):
#if jam detected, insert the id in the jam management
    for i in tyre_management:
        if tyre_management[i]['is jam detected']:
            jam_management[i] = {}
            jam_management[i]['time when jam detected'] = current_time
            jam_management[i]['is jam confirmed'] = False
#if any jam is persisted more than 1 minute, then confirm the jam and incremented the jam count
    for i in jam_management:
        if current_time - jam_management[i]['time when jam detected'] > jam_confirm_time:
            jam_management[i]['is jam confirmed'] = True
            jam_confirmed_count += 1

    if jam_confirmed_count > 2:
        print("Signal")

def id_manager(current_time):
    #for removing the false detected id and unused id
#get the the currently stored id's
#current_frame_ids is the ids detected in the current frame or iteration
#if any stored id is not present in the current frame id, then insert the id in the id management with time
    if frame_number % (int(fps) * id_check_time) == 0:
        currently_stored_ids = list(tyre_management.keys())
        for i in currently_stored_ids:
            if i not in current_frame_ids:
                tyre_management[i]['is id present in the current frame'] = False
                id_management[i] = {}
                id_management[i]['time when id disappeared'] = current_time
                delete_jam(i)
            else:
                if not tyre_management[i]['is id present in the current frame']:
                    tyre_management[i]['is id present in the current frame'] = True
                    delete_id(i)
    id_manager_deletion(current_time)

def id_manager_deletion(current_time):
#if id is not present for more than 1 min, remove the id  from the id and tyre management
    id_to_be_removed = []
    for i in id_management:
        if current_time - id_management[i]['time when id disappeared'] > id_confirm_time:
            id_to_be_removed.append(i)
    for i in id_to_be_removed:
        delete_tyre(i)


while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model.track(frame, persist=True)

        for pos in tracking_line:
            cv2.line(frame, (0, pos), (frame.shape[1], pos), (0, 255, 0), 2)
        current_time = time.time()

        frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        for result in results:
            current_frame_ids = result.boxes.id.tolist()
            for box in result.boxes:
                box_id = str(box.id.tolist()[0])
                box_coords = box.xyxy.tolist()
                center_x = int((box_coords[0][0] + box_coords[0][2]) / 2)
                center_y = int((box_coords[0][1] + box_coords[0][3]) / 2)
                cv2.putText(frame, box_id, (center_x, center_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.rectangle(frame, (int(box_coords[0][0]), int(box_coords[0][1])),
                                            (int(box_coords[0][2]), int(box_coords[0][3])), (0, 255, 0), 1)
                #if box_id is already detected and present in the tyre managemet
                if box_id in tyre_management:
                    #if box has crossed the last tracking line, then del the id
                    if box_coords[0][1] > tracking_line[-1]:
                        delete_tyre(box_id)
                        continue
                    #if box has crossed the upcoming tracking line, then change the next line to be crossed and the time
                    if tyre_management[box_id]['next line to cross'] < box_coords[0][1]:
                        idx = tracking_line.index(tyre_management[box_id]['next line to cross'])
                        tyre_management[box_id]['next line to cross'] = tracking_line[idx + 1]
                        tyre_management[box_id]['time when the tyre cross the line'] = current_time
                        if tyre_management[box_id]['is jam detected']:
                            tyre_management[box_id]['is jam detected'] = False
                            delete_jam(box_id)
                    else:
                        if current_time - tyre_management[box_id]['time when the tyre cross the line'] > jam_check_time:
                            cv2.rectangle(frame, (int(box_coords[0][0]), int(box_coords[0][1])),
                                                (int(box_coords[0][2]), int(box_coords[0][3])), (0, 0, 255), 1)
                            if not tyre_management[box_id]['is jam detected']:
                                tyre_management[box_id]['is jam detected'] = True
                else:
                    for pos in tracking_line:
                        if box_coords[0][1] < pos:
                            tyre_management[box_id] = {}
                            tyre_management[box_id]['next line to cross'] = pos
                            tyre_management[box_id]['time when the tyre cross the line'] = current_time
                            tyre_management[box_id]['is jam detected'] = False
                            tyre_management[box_id]['is id present in the current frame'] = True
                            break
#fake detection also comes under the jam , if it comes to id, then jam should delete
#backup the data if any error occured and initialize
        jam_manager(current_time)
        id_manager(current_time)

        out.write(frame)
        if frame_number % (int(fps)) == 0:
            report['tyre_management'].append(list(tyre_management.keys()))
            report['jam_management'].append(list(jam_management.keys()))
            report['id_management'].append(list(id_management.keys()))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        print("video not detected")
        break

cap.release()
out.release()