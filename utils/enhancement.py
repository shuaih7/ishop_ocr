import os
import sys
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
        self.roi = []  # list of r0,c0,r1,c1
        self.set_roi()

    # todo, roi setting for config files
    def set_roi(self):
        ''''''
        for r in range(self.row_nbr):
            for c in range(self.col_nbr):
                r0, r1 = self.offset[0] + self.height * r, self.offset[0] + self.height * (r + 1)
                c0, c1 = self.offset[1] + self.width * c, self.offset[1] + self.width * (c + 1)
                self.roi.append((r0,c0,r1,c1))
                print("r0,c0,r1,c1: ",r0, c0, r1, c1)

    #
    def __call__(self, image, engine=None, params={}, app=None):
        #self.image_filtered,_ = self.denoise(image,image)
        #return self.get_patches(self.image_filtered)
        #return self.rec_patches(image, engine, params, app)

        self.image_filtered = median_filter(image,8)
        return self.rec_patches(self.image_filtered , engine, params, app)

    def histeq(self,im,nbr_bins=256):
        imhist,bins = histogram(im.flatten(),nbr_bins,normed=True)
        cdf = imhist.cumsum()
        cdf = 255*cdf/cdf[-1]
        im2 = interp(im.flatten(),bins[:-1],cdf)
        return im2.reshape(im.shape),cdf


    def denoise(self, im, U_init, tolerance=0.1, tau=0.125, tv_weight=100):
        """ An implementation of the Rudin-Osher-Fatemi (ROF) denoising model
            using the numerical procedure presented in Eq. (11) of A. Chambolle
            (2005). Implemented using periodic boundary conditions.
            Args:
                im: noisy input image (grayscale),
                U_init: initial guess for U,
                tv_weight: weight of the TV-regularizing term,
                tau: steplength,
                tolerance: tolerance for the stop criterion

            Returns:
                denoised and detextured image, texture residual. """

        m, n = im.shape  # size of noisy image

        # initialize
        U = U_init
        Px = zeros((m, n))  # x-component to the dual field
        Py = zeros((m, n))  # y-component of the dual field
        error = 1

        while (error > tolerance):
            Uold = U

            # gradient of primal variable
            GradUx = roll(U, -1, axis=1) - U  # x-component of U's gradient
            GradUy = roll(U, -1, axis=0) - U  # y-component of U's gradient

            # update the dual varible
            PxNew = Px + (tau / tv_weight) * GradUx  # non-normalized update of x-component (dual)
            PyNew = Py + (tau / tv_weight) * GradUy  # non-normalized update of y-component (dual)
            NormNew = maximum(1, sqrt(PxNew ** 2 + PyNew ** 2))

            Px = PxNew / NormNew  # update of x-component (dual)
            Py = PyNew / NormNew  # update of y-component (dual)

            # update the primal variable
            RxPx = roll(Px, 1, axis=1)  # right x-translation of x-component
            RyPy = roll(Py, 1, axis=0)  # right y-translation of y-component

            DivP = (Px - RxPx) + (Py - RyPy)  # divergence of the dual field.
            U = im + tv_weight * DivP  # update of the primal variable

            # update of error
            error = linalg.norm(U - Uold) / sqrt(n * m);

        return U, im - U  # denoised image and texture residual

    def get_patches(self,img_filtered):
        row_nbr,col_nbr = self.row_nbr, self.col_nbr
        offset = self.offset
        height,width = self.height,self.width
        
        image_patches = []
        # for r in range(row_nbr):
        #     for c in range(col_nbr):
        #         r0, r1 = offset[0] + height * r, offset[0] + height * (r + 1)
        #         c0, c1 = offset[1] + width * c, offset[1] + width * (c + 1)
        #         print(r0, r1, c0, c1)
        for roi in self.roi:
            r0,c0,r1,c1 = roi
            img_patch= img_filtered[r0:r1, c0:c1]
            image_patches.append(img_patch)
        return image_patches
        
    def rec_patches(self, img_filtered, engine=None, params={}, app=None):
        if engine is None: return []
            
        row, col = 0, 0
        offy, offx = self.offset
        results = []
        img_patches = self.get_patches(img_filtered)
        i = 0
        for img in img_patches:
            loc_result = engine.ocr(img, **params)

            for label in loc_result:
                points = label[0]
                text = label[1][0]
                confidence = label[1][1]
                
                #for point,roi in zip(points,self.roi):
                r0, c0, r1, c1 = self.roi[i]
                print("r0,c0,r1,c1:", r0, c0, r1, c1)
                for point in points:
                    point[0] += c0
                    point[1] += r0
                    # point[0] += offx + col*self.width
                    # point[1] += offy + row*self.height
                results.append(self.merge_results([points, [text, confidence]]))
            i += 1
            # col += 1
            # if col == self.col_nbr:
            #     col = 0
            #     row += 1
            if app is not None: app.processEvents()

        return results
        
    def merge_results(self, results):
        if len(results) != 2: return results
        
        xs, ys = [], []
        for pt in results[0][0] + results[1][0]:
            xs.append(pt[0])
            ys.append(pt[1])
        
        min = min(xs)
        ymin = min(ys)
        xmax = max(xs)
        ymax = max(ys)
        
        # Clock-wise         
        roi = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]

        if len(results[0][1][0]) >= len(results[1][1][0]):
            text = results[0][1][0] + results[1][1][0]
        else:
            text = results[1][1][0] + results[0][1][0]
        confidence = (results[0][1][1] + results[1][1][1])/2
        
        mresult = [roi, [text, confidence]]
        
        return mresult


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