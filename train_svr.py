#!/usr/bin/env python3
import argparse
import os
import numpy as np
import joblib

from sklearn.svm import SVR
from constants import *
from segment_images import segment_image
import util

# RGB → YUV conversion matrix
YUV_FROM_RGB = np.array([
    [0.299, 0.587, 0.114],
    [-0.14713, -0.28886, 0.436],
    [0.615, -0.51499, -0.10001]
]).T


def retrieveYUV(img):
    return np.dot(img, YUV_FROM_RGB)


def generateSubsquares(path):
    img, segments = segment_image(path)
    yuv = retrieveYUV(img)

    n_segments = segments.max() + 1

    point_count = np.zeros(n_segments)
    centroids = np.zeros((n_segments, 2))
    U = np.zeros(n_segments)
    V = np.zeros(n_segments)

    # Compute centroids and average U,V
    for (i, j), seg_id in np.ndenumerate(segments):
        point_count[seg_id] += 1
        centroids[seg_id][0] += i
        centroids[seg_id][1] += j
        U[seg_id] += yuv[i, j, 1]
        V[seg_id] += yuv[i, j, 2]

    for k in range(n_segments):
        if point_count[k] == 0:
            continue
        centroids[k] /= point_count[k]
        U[k] /= point_count[k]
        V[k] /= point_count[k]

    # FFT feature extraction
    subsquares = np.zeros((n_segments, SQUARE_SIZE * SQUARE_SIZE))

    for k in range(n_segments):
        top = int(centroids[k][0])
        left = int(centroids[k][1])

        top = max(0, min(top, img.shape[0] - SQUARE_SIZE - 1))
        left = max(0, min(left, img.shape[1] - SQUARE_SIZE - 1))

        patch = yuv[
            top:top + SQUARE_SIZE,
            left:left + SQUARE_SIZE,
            0
        ]

        fft_patch = np.abs(np.fft.fft2(patch))
        subsquares[k] = fft_patch.flatten()

    return subsquares, U, V


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train the SVR.')
    parser.add_argument('-a', action='store_true', help='Train all models')
    parser.add_argument('-t', default='data/flickr/', help='Training dataset path')
    parser.add_argument('-f', default='svr.model', help='Output model filename')
    args = parser.parse_args()

    print("Training data set on files in:", args.t)

    X = np.empty((0, SQUARE_SIZE * SQUARE_SIZE))
    U_L = np.empty((0,))
    V_L = np.empty((0,))

    for root, _, files in os.walk(args.t):
        for file in files:
            if not file.lower().endswith('.jpg'):
                continue

            path = os.path.join(root, file)
            print("Training on", path)

            subsquares, U, V = generateSubsquares(path)

            X = np.vstack((X, subsquares))
            U_L = np.concatenate((U_L, U))
            V_L = np.concatenate((V_L, V))

    util.mkdirp('models')

    if args.a:
        model_count = 0
        for c in C_LIST:
            for epsilon in EPSILON_LIST:
                print(f"Fitting model C={c}, epsilon={epsilon}")
                u_svr = SVR(C=c, epsilon=epsilon)
                v_svr = SVR(C=c, epsilon=epsilon)
                u_svr.fit(X, U_L)
                v_svr.fit(X, V_L)
                joblib.dump(u_svr, f'models/u_svr{model_count}.model')
                joblib.dump(v_svr, f'models/v_svr{model_count}.model')
                model_count += 1
    else:
        print(f"Fitting model C={C}, epsilon={SVR_EPSILON}")
        u_svr = SVR(C=C, epsilon=SVR_EPSILON)
        v_svr = SVR(C=C, epsilon=SVR_EPSILON)
        u_svr.fit(X, U_L)
        v_svr.fit(X, V_L)
        joblib.dump(u_svr, 'models/u_' + args.f)
        joblib.dump(v_svr, 'models/v_' + args.f)

# #!/usr/bin/env python
# import argparse
# import os
# import code

# from sklearn.svm import SVR
# from skimage.segmentation import slic, mark_boundaries
# from skimage.data import imread
# from skimage.util import img_as_float
# from sklearn.externals import joblib

# import matplotlib.pyplot as plt
# import numpy as np

# from constants import *
# from segment_images import segment_image
# import util

# YUV_FROM_RGB = np.array([[0.299, 0.587, 0.114],
#                          [-0.14713, -0.28886, 0.436],
#                          [0.615, -0.51499, -0.10001]]).T

# def retrieveYUV(img):
#     return np.dot(img, YUV_FROM_RGB)

# # Given an image, return
# #    - An array of subsquares
# #    - An array containing the average U values for the subsquares
# #    - An array containing the average V values for the subsquares
# def generateSubsquares(path):
#     img, segments = segment_image(path)
#     yuv = retrieveYUV(img)
#     n_segments = segments.max() + 1
#     # code.InteractiveConsole(locals=locals()).interact()

#     # Compute the centroids/average U and V of each of the superpixels
#     point_count = np.zeros(n_segments)
#     centroids = np.zeros((n_segments, 2))
#     U = np.zeros(n_segments)
#     V = np.zeros(n_segments)
#     for (i,j), value in np.ndenumerate(segments):
#         point_count[value] += 1
#         centroids[value][0] += i
#         centroids[value][1] += j
#         U[value] += yuv[i][j][1]
#         V[value] += yuv[i][j][2]

#     for k in range(n_segments):
#         centroids[k] /= point_count[k]
#         U[k] /= point_count[k]
#         V[k] /= point_count[k]

#     # Generate the array of squares
#     subsquares = np.zeros((n_segments, SQUARE_SIZE * SQUARE_SIZE))
#     for k in range(n_segments):
#         # Check that the square lies completely within the image
#         top = max(int(centroids[k][0]), 0)
#         if top + SQUARE_SIZE >= img.shape[0]:
#             top = img.shape[0] - 1 - SQUARE_SIZE
#         left = max(int(centroids[k][1]), 0)
#         if left + SQUARE_SIZE >= img.shape[1]:
#             left = img.shape[1] - 1 - SQUARE_SIZE
#         for i in range(0, SQUARE_SIZE):
#             for j in range(0, SQUARE_SIZE):
#                 subsquares[k][i*SQUARE_SIZE + j] = yuv[i + top][j + left][0]
#         subsquares[k] = np.fft.fft2(subsquares[k].reshape(SQUARE_SIZE, SQUARE_SIZE)).reshape(SQUARE_SIZE * SQUARE_SIZE)

#     return subsquares, U, V

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Train the SVR.')
#     parser.add_argument('-a', help='Specify training all models.', action='store_true')
#     parser.add_argument('-t', metavar='training_set', help='The training set to be used for training', default='data/flickr/')
#     parser.add_argument('-f', metavar='output_file', help='Output file for model', default='svr.model')
#     args = parser.parse_args()
#     print ('Training data set on files in:', args.t)

#     for root, dirs, files in os.walk(args.t):
#         X = np.array([]).reshape(0, SQUARE_SIZE * SQUARE_SIZE)
#         U_L = np.array([])
#         V_L = np.array([])

#         for file in files:
#             path = os.path.join(root, file)
#             if not path.endswith(".jpg"):
#                 continue

#             print "Training on", path, "..."
#             subsquares, U, V = generateSubsquares(path)

#             X = np.concatenate((X, subsquares), axis=0)
#             U_L = np.concatenate((U_L, U), axis=0)
#             V_L = np.concatenate((V_L, V), axis=0)

#         util.mkdirp('models/')

#         if args.a:  # Train all of the data sets
#             model_count = 0
#             for c in C_LIST:
#                 for epsilon in EPSILON_LIST:
#                     u_path = 'models/u_svr' + str(model_count) + '.model'
#                     v_path = 'models/v_svr' + str(model_count) + '.model'
#                     if not os.path.isfile(u_path) or not os.path.isfile(v_path):
#                         print 'Fitting the model given by C =', c, ', epsilon =', epsilon
#                         u_svr = SVR(C=c, epsilon=epsilon)
#                         v_svr = SVR(C=c, epsilon=epsilon)
#                         u_svr.fit(X, U_L)
#                         v_svr.fit(X, V_L)
#                         joblib.dump(u_svr, u_path)
#                         joblib.dump(v_svr, v_path)
#                     model_count += 1

#         else:       # Only train the model given by the defaults
#             print 'Fitting the model given by C =', C, ', epsilon =', SVR_EPSILON
#             u_svr = SVR(C=C, epsilon=SVR_EPSILON)
#             v_svr = SVR(C=C, epsilon=SVR_EPSILON)
#             u_svr.fit(X, U_L)
#             v_svr.fit(X, V_L)
#             joblib.dump(u_svr, 'models/u_' + args.f)
#             joblib.dump(v_svr, 'models/v_' + args.f)
