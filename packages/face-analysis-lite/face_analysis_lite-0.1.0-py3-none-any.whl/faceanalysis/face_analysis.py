#######################################################################################
#
# MIT License
#
# Copyright (c) [2025] [leonelhs@gmail.com]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
#######################################################################################
#
# FaceAnalysis is the core library used for facial region detection and extraction.
# Future contributors and maintainers should review the official or reference
# implementations for details and updates:
# https://github.com/deepinsight/insightface/blob/master/python-package/insightface/app/face_analysis.py
#
# The goal of this project is to enable quick integration into other systems
# while minimizing external library dependencies.
# For users who prefer a ready-to-use solution, consider installing the full package:
# pip install insightface
#
# Demo: https://huggingface.co/spaces/leonelhs/FaceAnalysis


# -*- coding: utf-8 -*-
# @Organization  : insightface.ai
# @Author        : Jia Guo
# @Time          : 2021-05-04
# @Function      : 


from __future__ import division

import cv2
import onnxruntime

__all__ = ['FaceAnalysis']

from faceanalysis.models import RetinaFace, Landmark, Attribute, ArcFaceONNX
from faceanalysis.utils.common import Face
from huggingface_hub import hf_hub_download

REPO_ID = "leonelhs/insightface"

model_detector_path = hf_hub_download(repo_id=REPO_ID, filename="det_10g.onnx")
model_landmark_3d_68_path = hf_hub_download(repo_id=REPO_ID, filename="1k3d68.onnx")
model_landmark_2d_106_path = hf_hub_download(repo_id=REPO_ID, filename="2d106det.onnx")
model_genderage_path = hf_hub_download(repo_id=REPO_ID, filename="genderage.onnx")
model_recognition_path = hf_hub_download(repo_id=REPO_ID, filename="w600k_r50.onnx")
meanshape_68_path = hf_hub_download(repo_id=REPO_ID, filename="meanshape_68.pkl")

class FaceAnalysis:
    def __init__(self):
        onnxruntime.set_default_logger_severity(3)

        self.detector = RetinaFace(model_file=model_detector_path, input_size=(640, 640), det_thresh=0.5)
        self.landmark_3d_68 = Landmark(model_file=model_landmark_3d_68_path, meanshape=meanshape_68_path)
        self.landmark_2d_106 = Landmark(model_file=model_landmark_2d_106_path, meanshape=meanshape_68_path)
        self.genderage = Attribute(model_file=model_genderage_path)
        self.recognition = ArcFaceONNX(model_file=model_recognition_path)

    def get(self, image_path, max_num=0):
        # FIXME: The gender/age detection model expects images in BGR format (as used by OpenCV).
        #  Using RGB input significantly reduces prediction accuracy.
        #  To maintain reliable results, all image reads must use OpenCV's `cv2.imread`,
        #  which loads images in BGR by default.
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        bboxes, kpss = self.detector.detect(img, max_num=max_num, metric='default')
        if bboxes.shape[0] == 0:
            return []
        ret = []
        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            kps = None
            if kpss is not None:
                kps = kpss[i]
            face = Face(bbox=bbox, kps=kps, det_score=det_score)
            self.landmark_3d_68.get(img, face)
            self.landmark_2d_106.get(img, face)
            self.genderage.get(img, face)
            self.recognition.get(img, face)
            ret.append(face)
        return ret