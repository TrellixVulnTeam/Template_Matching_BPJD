'''Here we will crop the template from the image to be searched, in practice it is not a realistic scenario, one would would usually have a generic template different from the searched image.'''
''' Multi-Template-Matching: 
https://github.com/multi-template-matching/MultiTemplateMatching-Python '''
# import MTM
# # print("MTM version: ", MTM.__version__)
# from MTM import matchTemplates, drawBoxesOnRGB
# import cv2
# from skimage.data import coins
# import matplotlib.pyplot as pl
#
# image = cv2.imread('medidor_template.jpg')
# # plt.imshow(image, cmap="gray")
# borne = cv2.imread('bornera_template.jpg')
# # plt.imshow(smallCoin, cmap="gray")
# capacitor = cv2.imread('cap.jpg')
# res = cv2.imread('res_template.jpg')
# display = cv2.imread('display_template.jpg')
#
# # 1st format the template into a list of tuple (label, templateImage)
# listTemplate = [('Bornera', borne), ("Capacitor", capacitor), ("Resistencia", res), ("display", display)]
# # Then call the function matchTemplates (here a single template)
# Hits = matchTemplates(listTemplate, image, score_threshold=0.6, method=cv2.TM_CCOEFF_NORMED, maxOverlap=0)
# print("Found {} hits".format(len(Hits.index)))
#
# Overlay = drawBoxesOnRGB(image, Hits, showLabel=True)
# plt.imshow(Overlay)
# plt.show()

'''Multi-Template-Matching - Template augmentation: The additional templates can be generated by rotation or flipped (mirroring) of the initial template.
This is a bit like doing data-augmentation with the template.
https://github.com/multi-template-matching/MultiTemplateMatching-Python/blob/master/tutorials/Tutorial2-Template_Augmentation.ipynb'''

# import MTM
# from MTM import matchTemplates, drawBoxesOnRGB
# import cv2
# from skimage import io
# import matplotlib.pyplot as plt
# import numpy as np
#
# image = cv2.imread('embriones.jpg')
# template = image[784:784+400, 946:946+414]
# # plt.axis("off")
# # plt.imshow(image, cmap="gray")
# # plt.imshow(template, cmap="gray")
# # plt.show()
#
# # 1st format the template into a list of tuple (label, templateImage)
# # listTemplate = [('Embrion', template)]
# ## Perform rotation of the initial template
# listTemplate = [("Embrion", template)]
# # Initialise figure
# f, axarr = plt.subplots(1, 3)
# axarr[0].imshow(template, cmap="gray")
#
# for i, angle in enumerate([90, 180]):
#     rotated = np.rot90(template, k=i + 1)  # NB: np.rotate not good here, turns into float!
#     listTemplate.append((str(angle), rotated))
#     axarr[i + 1].imshow(rotated, cmap="gray")
#     # We could also do some flipping with np.fliplr, flipud
#
# # Then call the function matchTemplates (here a single template)
# Hits = matchTemplates(listTemplate, image, score_threshold=0.5, N_object=4, method=cv2.TM_CCOEFF_NORMED, maxOverlap=0.1)
# print("Found {} hits".format( len(Hits.index)))
#
# Overlay = drawBoxesOnRGB(image, Hits, boxThickness=5)
# plt.figure(figsize = (10,10))
# plt.axis("off")
# plt.imshow(Overlay)
# plt.show()

'''
Multi-Template Matching - Speed up the execution :
https://github.com/multi-template-matching/MultiTemplateMatching-Python/blob/master/tutorials/Tutorial3-SpeedingUp.ipynb
1- Baseline execution
2- Using a limited search region
3- Downscaling the image
'''

from time import time
import MTM
from MTM import matchTemplates, drawBoxesOnRGB
import cv2
from skimage.data import coins
import matplotlib.pyplot as plt
import gluoncv as gcv
import numpy as np

image = cv2.imread('Fish.jpg', -1)

# 1- Baseline execution

# cabeza = image[842:842+184, 528:528+196]
# listTemplate = [('head', cabeza)]
# start_time = time()
# Hits = matchTemplates(listTemplate, image, N_object=1, method=cv2.TM_CCOEFF_NORMED)
# elapsed_time = time() - start_time
# # Aprox. 204ms
# print("Elapsed time: %0.10f seconds." % elapsed_time)
# print("Found {} hits".format( len(Hits.index)))
# Overlay = drawBoxesOnRGB(image, Hits, showLabel=True)
# plt.figure(figsize = (10,10))
# plt.axis("off")
# plt.imshow(Overlay)
# plt.show()

# 2- Using a limited search region: We get about 5x speed improvement !
# The reason is simple, the comparison between the pixel intesities is now performed only for regions within the green area. Which is a fraction of the original image size.
# Notice that the coordinates of the hit are still expressed in the full-size image coordinate system (no need to recaclulate)
# Using a search region is an easy way to speed up the algorithm if you have some a priori knowledge about the position of the object in the image.

# # Overlay = image.copy()
# # cv2.rectangle(Overlay, (76, 781), (76+1856, 781+353), 255, 2)
# # plt.figure(figsize = (10,10))
# # plt.imshow(Overlay, cmap="gray")
# # plt.show()
# cabeza = image[842:842+184, 528:528+196]
# listTemplate = [('head', cabeza)]
# start_time = time()
# # The search region is provided by the searchBox argument in format (x,y,width,height)
# Hits = matchTemplates(listTemplate, image, N_object=1, method=cv2.TM_CCOEFF_NORMED, searchBox=(76,781,1856,353))
# elapsed_time = time() - start_time
# # Aprox. 27ms
# print("Elapsed time: %0.10f seconds." % elapsed_time)
# Overlay = drawBoxesOnRGB(image, Hits, showLabel=True)
# plt.figure(figsize = (10,10))
# plt.axis("off")
# plt.imshow(Overlay)
# plt.show()

# # 3- Downscaling the image
# Using a search region is an easy way to speed up the algorithm if you have some a priori knowledge about the position of the object in the image.
# Yet it's not always the case you might still want to search the full region of a large image, and this quickly.
# Well many computer vision algorithm do not work on the full resolution image, to limit memory consumption.
# We can do the same for multi-template-matching.
# We can reduce the size from 2048x2048 to 512x512 for instance.

print("Original image size:", image.shape)

# Resize the image to 512x512
smallDim = 512,512
smallImage = cv2.resize(image, smallDim, interpolation = cv2.INTER_AREA)
print("New image size: ", smallImage.shape)

# Now that the image is smaller we need to redefine the template as well, by cropping the downsampled image for instance.
# The image being downsample by 4, we keep the same ratio for the new template size.
# the resolution is worse, but it is still sufficient for the object-detection.
smallCabeza = smallImage[210:210+46, 131:131+49]

# One thing to keep in mind is that the downsampling factor depends on the size of the object to find.
# Imagine we would downsample by a factor of 10 or 100, then the head region would be just a few pixel in the downsampled image
# and such that the chance to find it by template matching would decrease.
start_time = time()
Hits = matchTemplates([("downsampled", smallCabeza)], smallImage, N_object=1, method=cv2.TM_CCOEFF_NORMED)
elapsed_time = time() - start_time
# Aprox: 15ms
print("Elapsed time: %0.10f seconds." % elapsed_time)

# And now comes the major trick: because we performed the detection on downscale images, we have to scale up the detected bounding-boxes.
# Fortunately, there are such utilitary functions for bounding boxes in the gluoncv library.
# To install gluoncv, open a terminal in your active python environment and type pip install gluoncv.

# Before upscaling the bounding boxes, we need to convert them from the x,y,width,height format to xmin,ymin,xmax,ymax
# There is also a function for that
BBoxes_xywh = np.array( Hits["BBox"].tolist() )
BBoxes_xyxy = gcv.utils.bbox.bbox_xywh_to_xyxy(BBoxes_xywh)

# Now we can rescale it
BBoxes = gcv.data.transforms.bbox.resize(BBoxes_xyxy, smallDim, image.shape[::-1] )

# And display it on top of the full resolution image
Overlay = gcv.utils.viz.cv_plot_bbox(cv2.cvtColor(image, cv2.COLOR_GRAY2RGB), BBoxes, scores=Hits["Score"].to_numpy(), thresh=0  )
plt.figure(figsize = (10,10))
plt.imshow(Overlay)
plt.show()