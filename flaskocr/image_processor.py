import numpy as np
import cv2 
from PIL import Image
from sklearn.mixture import GaussianMixture

class ShadowRemover():

    def __init__(self):
        # Default algorithmic parameters
        self.stride = 20;                 # Number of pixels to skip when performing local analysis
        self.blockSize = self.stride;     # Size of overlapping blocks in local analysis
        self.numOfClusters = 4;           # Number of clusters used for local analysis
        self.maxIters = 100;              # Maximum number of iterations used as stopping condition for GMM clustering. 
        self.emEps = 0.1;                # Epsilon threshold used as stopping condition for GMM clustering.
        self.diffThres = 30;
        self.clearThres = 40;


    def GetBlock(self, x, y, dsImage, width, height):
        minX = x
        maxX = min(width, x + self.blockSize)
        minY = y
        maxY = min(height, y + self.blockSize)
        block = np.array([dsImage[y][minX:maxX] for y in range(minY, maxY)])
        return block;

    def PutBlock(self, x, y, newImg, newBlock):
        for i in range(y, y + len(newBlock)):
            newImg[i][x:x+len(newBlock[i - y])] = newBlock[i - y]

    def ClusterBlock(self, block):
    #     X,Y = make_blobs(cluster_std=0.5,random_state=20,n_samples=1000,centers=5)
        # Stratch dataset to get ellipsoid data
        emModel = GaussianMixture(n_components=self.numOfClusters, covariance_type= 'diag', max_iter=self.maxIters, tol=self.emEps)
        originalShape = (len(block), -1)
        block_flat = block.reshape((-1, 1))

        if len(block_flat) < self.numOfClusters:
            dst = np.zeros_like(block)
            cv2.normalize(block, dst, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            return None, None, dst

        samples = block_flat.copy()
        samples = np.array(samples)
        emModel.fit(samples)
        predict_probs = emModel.predict_proba(samples)

        means = emModel.means_ 
        covariances = emModel.covariances_

        order = sorted(range(len(means)), key = lambda x : means[x])
        means = np.array(sorted(means))
        predict_probs = np.array([[p[o] for o in order] for p in predict_probs])

        if (abs(means[0] - means[-1]) < self.clearThres):
            predicts = np.ones(len(predict_probs))
        else:
            lowest = means[0]
            highest = means[-1]
            values = np.array([int(abs(m - lowest) >= self.diffThres) * 1 * int(abs(m - highest) < self.diffThres) + min(1, 1.1 * (m - lowest) / (highest - lowest)) * int(abs(m - highest) >= self.diffThres and abs(m - lowest) >= self.diffThres) for m in means])
            predicts = []
            for p in predict_probs:
                predicts.append(np.dot(p, values))
            predicts = np.array(predicts)

        predicts = np.array([predicts * 255])
        return means, covariances, predicts.reshape(originalShape)

    # main function
    def RemoveShadow(self, image):
        width = len(image[0])
        height = len(image)

        newImg = image.copy()
        i = 0
        while i < height:
            j = 0
            while j < width:
                block = self.GetBlock(j, i, image, width, height)
                means, covariances, newBlock = self.ClusterBlock(block)
                self.PutBlock(j, i, newImg, newBlock)
                
                j += self.stride
            i += self.stride
        return newImg


class ImageProcessor():

    def __init__(self):
        self.shadowRemover = ShadowRemover()

    def findMatrices(self, matrix, edge):
        matrices = [matrix]
        left = [matrix]
        right = [matrix]
        bot = [matrix]
        top = [matrix]
        
        moveRight = lambda m: np.insert(np.delete(m,0,1), -1, 0, axis=1)
        moveLeft = lambda m: np.insert(np.delete(m,-1,1), 0, 0, axis=1)
        moveTop = lambda m: np.insert(np.delete(m,-1,0), 0, 0, axis=0)
        moveBot = lambda m: np.insert(np.delete(m,0,0), -1, 0, axis=0)

        def loop_side(l, f):
            for _ in range(len(l)):
                m = l.pop(0)
                m = f(m)
                l.append(m)
                matrices.append(m)

        for i in range(1, edge + 1):
            loop_side(right, moveRight)
            loop_side(left, moveLeft)
            loop_side(top, moveTop)
            loop_side(bot, moveBot)

            leftTop = moveTop(left[0])
            left.insert(0, leftTop)
            top.insert(0, leftTop)
            matrices.append(leftTop)
            
            rightTop = moveTop(right[0])
            right.insert(0, rightTop)
            top.append(rightTop)
            matrices.append(rightTop)
            
            leftBot = moveBot(left[-1])
            left.append(leftBot)
            bot.insert(0, leftBot)
            matrices.append(leftBot)
            
            rightBot = moveTop(right[-1])
            right.append(rightBot)
            top.append(rightBot)
            matrices.append(rightBot)

        return matrices
        
    def contrast_img(self, matrix):
        
        dst = np.zeros_like(matrix)
        cv2.normalize(matrix, dst, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        matrix = dst
        
        edge = 2
        matrices = self.findMatrices(matrix, edge)
        
        mean_matrix = np.sum(matrices, axis=0) / len(matrices)
        demean_matrices = np.array(matrices) - mean_matrix
        std_matrix = np.sum(demean_matrices ** 2, axis=0) ** 0.5
        mean_std = np.mean(std_matrix)
        
        judge_matrix_dark = np.where((matrix < mean_matrix) & (std_matrix > 0.8 * mean_std), matrix, 0)
        matrix = (matrix - 0.5 * judge_matrix_dark).astype('uint8')
        
        return matrix

    def init_resize(self, img):
        while len(img) > 1500 or len(img[0]) > 1500:
            img = cv2.resize(img, (int(len(img[0]) / 1.5), int(len(img) / 1.5)))
        return img

    def denoiseOnce(self, matrix, e):
        matrices = self.findMatrices(matrix, e)
        count_black = np.zeros_like(matrix).astype('int64')
        thres = min(e * 2, len(matrices) // 8)
        for m in matrices:
            count_black += np.where(m.astype('int64') < 200, 1, 0)

        matrix = np.where(count_black > thres, matrix, 255).astype('uint8')
    #     Image.fromarray(matrix).show()
        return matrix

    def denoise(self, matrix, edge = 2):
        for e in range(1, edge + 1):
            matrix = self.denoiseOnce(matrix, e)
        for e in range(edge - 1, 0, -1):
            matrix = self.denoiseOnce(matrix, e)
        rt = np.zeros_like(matrix).astype('int64')
        while not np.array_equal(rt, matrix):
            rt = matrix
            matrix = self.denoiseOnce(matrix, 1)
        return matrix
        

    def generateGray(self, img):
        img = self.init_resize(img)
        matrix = np.array(img) 
        matrix = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        matrix = cv2.GaussianBlur(matrix, (7, 7), 0.6)
        matrix = self.contrast_img(matrix)
        # matrix = self.shadowRemover.RemoveShadow(matrix)
        matrix = cv2.adaptiveThreshold(matrix, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY,
                                     self.shadowRemover.blockSize // 2 * 2 + 1,
                                     25)
        rt = np.zeros_like(matrix).astype('int64')
        edge = min(min(len(matrix), len(matrix[0])) // 100, 3)
        print(edge)
        matrix = self.denoise(matrix, edge)

        varM = cv2.Laplacian(matrix, cv2.CV_64F)
        rt = np.array(matrix).astype('uint8')

        return rt

    def process_image(self, scr_path, dst_path, dpi = 70):
        img_ori = cv2.imread(scr_path)
        result = self.generateGray(img_ori)
        Image.fromarray(result).save(dst_path, dpi=(dpi, dpi))
        return result

