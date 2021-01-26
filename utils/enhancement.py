import os
import sys
import cv2
from scipy.ndimage import *
from numpy import *
from PIL import Image
import matplotlib.pyplot as plt
from .general import rotate_image, rotate_points


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
        self.roi = []  # list of r0,c0,r1,c1
        self.set_roi()

    # todo, roi setting for config files
    def set_roi(self):
        ''''''
        index = 0
        self.roi = []  # list of r0,c0,r1,c1
        for r in range(self.row_nbr):
            for c in range(self.col_nbr):
                r0, r1 = self.offset[0] + self.height * r, self.offset[0] + self.height * (r + 1)
                c0, c1 = self.offset[1] + self.width * c, self.offset[1] + self.width * (c + 1)
                self.roi.append([(r0,c0,r1,c1), index + 1])
                #print("r0,c0,r1,c1: ",r0, c0, r1, c1)
                index += 1
        return self.roi

    # todo, multiprocessing
    def __call__(self, image, angle, engine=None, params={}, app=None):
        #self.image_filtered,_ = self.denoise(image,image)
        #return self.get_patches(self.image_filtered)
        #return self.rec_patches(image, engine, params, app)

        # todo , using numba.cuda
        # self.image_filtered = median_filter(image,8)
        # self.image_filtered = cv2.medianBlur(image,7)
        self.image_filtered = image
        return self.rec_patches(self.image_filtered, angle, engine, params, app)

    def get_patches(self,img_filtered):
        image_patches = []
        for i,roi in enumerate(self.roi):
            r0,c0,r1,c1 = roi[0]
            img_patch= img_filtered[r0:r1, c0:c1]
            image_patches.append(img_patch)
        return image_patches
        
    def rec_patches(self, img_filtered, angle, engine=None, params={}, app=None):
        if engine is None: return []
        if angle not in [0, 90, -90, 180, -180]:
            raise ValueError("Rotate angle only support 0, 90, -90, 180.")
            
        offy, offx = self.offset
        results = []
        img_patches = self.get_patches(img_filtered)
        
        for i, img in enumerate(img_patches):
            cur_result = []
            img = rotate_image(img, angle)
            img_shape = img.shape[:2]
            loc_result = engine.ocr(img, **params)

            for label in loc_result:
                points = rotate_points(label[0], img_shape, -1*angle)
                text = label[1][0].upper()
                confidence = label[1][1]

                r0, c0, r1, c1 = self.roi[i][0]
                # print("r0,c0,r1,c1:", r0, c0, r1, c1)
                for point in points:
                    point[0] += c0
                    point[1] += r0
                cur_result.append([points, [text, confidence], self.roi[i][1], True])
            
            results += self._merge_results(cur_result)
            # results += cur_result

            if app is not None: app.processEvents()

        return results
        
    def _merge_results(self, results, conf_thresh=0.8, dir="hor"):
        if len(results) < 2: return results
        
        confidences = []
        for result in results:
            confidences.append(result[1][1])
            
        xs, ys = [], []
        for result in results:
            for pt in result[0]:
                xs.append(pt[0])
                ys.append(pt[1])

        xmin = min(xs)
        ymin = min(ys)
        xmax = max(xs)
        ymax = max(ys)
        roi = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]
    
        if len(results) != 2 or min(confidences) < conf_thresh:
            return [[roi, ["---", 0.0], results[0][2], False]]
        
        if dir == "hor":
            if results[0][0][0] < results[1][0][0]:
                text = results[0][1][0] + results[1][1][0]
            else:
                text = results[1][1][0] + results[0][1][0]
                
        elif dir == "ver":
            if results[0][0][1] < results[1][0][1]:
                text = results[0][1][0] + results[1][1][0]
            else:
                text = results[1][1][0] + results[0][1][0]
        
        conf = (results[0][1][1] + results[1][1][1]) / 2
        merge_result = [[roi, [text, conf], results[0][2], True]]
        
        return merge_result
        

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