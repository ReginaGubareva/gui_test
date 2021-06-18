import time
from pathlib import Path
import numpy as np

import cv2
import torch

from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, set_logging, increment_path, save_one_box
from utils.plots import colors, plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized
from utils.datasets import LoadImages


def centroid_detection(image, counter):
    centroids = []
    weights = fr'weights/last.pt'
    save_dir = increment_path(Path(fr'runs/detect/exp'))
    device = ''  # device can be '' cuda device, i.e. 0 or 0,1,2,3 or cpu
    imgsz = 640
    conf_thres = 0.25  # object confidence threshold
    iou_thres = 0.45  # IOU threshold for NMS
    augment = 'store_true'  # augmented inference
    classes = ['button', 'text', 'image', 'link', 'heading', 'field', 'iframe', 'label']
    agnostic_nms = 'store_true'
    max_det = 1000
    save_crop = 'store_true'
    save_txt = 'store_true'
    save_conf = 'store_true'
    save_crop = 'store_true'
    save_img = 'store_true'
    view_img = 'store_true'
    hide_labels = False
    hide_conf = False
    line_thickness = 3

    print(type(image))

    # Initialize
    set_logging()
    device = select_device(device)
    # print('device:', device)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    # print('image shape:', image.shape)
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    names = model.module.names if hasattr(model, 'module') else model.names  # get class names
    if half:
        model.half()  # to FP16

    # Run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
    t0 = time.time()

    filename = "%d" % counter
    image_path = fr"D:\projects\gui_test\resources\learning_screens\{filename}.jpg"
    img = cv2.imwrite(image_path, image)
    # Data Loader
    dataset = LoadImages(image_path, img_size=imgsz, stride=stride)

    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment=augment)[0]
        # print('pred:', pred)

        # Apply NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, None, agnostic_nms,
                                   max_det=max_det)
        t2 = time_synchronized()
        # print('pred:', pred)


        # Process detections
        for i, det in enumerate(pred):  # detections per image
            p, s, im0, frame = path, '', im0s.copy(), getattr(dataset, 'frame', 0)

            s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            # print('gn:', gn)

            imc = im0.copy() if save_crop else im0  # for opt.save_crop
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                        # print(('%g ' * len(line)).rstrip() % line + '\n')

                        c1, c2 = (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))
                        centroid = int((c2[0] + c1[0]) / 2), int((c2[1] + c1[1]) / 2)
                        centroids.append(centroid)

    return centroids
