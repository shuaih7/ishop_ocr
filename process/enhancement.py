import os
import sys
import cv2
from scipy.ndimage import *
from numpy import *
from PIL import Image
import matplotlib.pyplot as plt


class SNPatch():
    '''
    Get SN patches for OCR recognition
    '''
    # offset = (500, 300)  #(r,c)
    # width = 905
    # height = 683
    # row_nbr, col_nbr = 4, 5

    offset = (0, 0)  #(r,c)
    width = 905
    height = 683
    row_nbr, col_nbr = 5, 5

    def __init__(self):
        self.image_patches = []
        self.image_filtered = None
        self.rois = []  # list of r0,c0,r1,c1
        self.set_roi()

    # todo, roi setting for config files
    def set_roi(self):
        ''''''
        index = 0
        self.rois = []  # list of r0,c0,r1,c1
        for r in range(self.row_nbr):
            for c in range(self.col_nbr):
                r0, r1 = self.offset[0] + self.height * r, self.offset[0] + self.height * (r + 1)
                c0, c1 = self.offset[1] + self.width * c, self.offset[1] + self.width * (c + 1)
                self.rois.append([(r0,c0,r1,c1), index + 1])
                #print("r0,c0,r1,c1: ",r0, c0, r1, c1)
                index += 1

    # todo, multiprocessing
    def __call__(self, image):
        #self.image_filtered,_ = self.denoise(image,image)
        #return self.get_patches(self.image_filtered)
        #return self.rec_patches(image, engine, params, app)

        # todo , using numba.cuda
        # self.image_filtered = median_filter(image,8)
        # self.image_filtered = cv2.medianBlur(image,7)
        self.image_filtered = image
        return self.get_patches(self.image_filtered)

    def get_patches(self,img_filtered):
        image_patches = []
        for i,roi in enumerate(self.rois):
            r0,c0,r1,c1 = roi[0]
            img_patch= img_filtered[r0:r1, c0:c1]
            image_patches.append(img_patch)
        return image_patches
         

if __name__ =="__main__":
    import time
    import cv2
    sys.path.append(r"C:\Users\shuai\Documents\GitHub\ishop_ocr")
    from paddleocr.paddleocr import PaddleOCR
    
    patch = SNPatch()
    image_patches = []
    results = []
    ocr = PaddleOCR(use_angle_cls=True, use_gpu=True, gpu_mem=2000, lang="en") # need to run only once to download and load model into memory

    image_path = r"C:\Users\shuai\Documents\GitHub\ishop_ocr\data\imgs\2021-01-13_17_46_28_760.bmp"
    img = array(Image.open(image_path))
    
    t0 = time.time()
    image_patches = patch(img) #histeq(img)
    # result = ocr.ocr(image_patches, rec=True, det=True, cls=False)
    for img in image_patches:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        result = ocr.ocr(img, rec=True, det=True, cls=False)
        results.append(result)
    t1 = time.time()
    print("time elapsed:", t1-t0, "seconds.")
    """
    save_dir = r"E:\Projects\Part_Number\dataset\test_result"
    for i,img in enumerate(image_patches):
        cv2.imwrite(f"output/{i}_p.bmp", img)
        print(f"{i}_p.bmp saved!")
    """