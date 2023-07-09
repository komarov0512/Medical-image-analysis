import math
import os

import cv2 as cv2
import numpy as np
from skimage.draw import line


def getPerpCoord(aX, aY, bX, bY, length=1):
    vX = bX - aX
    vY = bY - aY
    mag = math.sqrt(vX * vX + vY * vY)
    if mag == 0:
        mag = 0.01
    vX = vX / mag
    vY = vY / mag
    temp = vX
    vX = 0 - vY
    vY = temp
    cX = bX + vX * length
    cY = bY + vY * length
    dX = bX - vX * length
    dY = bY - vY * length
    return int(cX), int(cY), int(dX), int(dY)


def findWidth(contours, img_with_contours):
    heights = []
    lengths = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        point_first = []
        point_end = []
        for dot in contour:
            if dot[0][0] == x and len(point_first) == 0:
                point_first = [dot[0][0], dot[0][1]]
            if dot[0][0] == x + w - 1 and len(point_end) == 0:
                point_end = [dot[0][0], dot[0][1]]
            if len(point_first) == 2 and len(point_end) == 2:
                break
        length = math.hypot(point_end[0] - point_first[0], point_end[1] - point_first[1])
        lengths.append(round(length, 1))
        cv2.circle(img_with_contours, point_first, 1, (0, 0, 255), 1)
        cv2.circle(img_with_contours, point_end, 1, (0, 0, 255), 1)
        cv2.line(img_with_contours, point_first, point_end, (255, 0, 0), 1)

        x1, y1, x2, y2 = getPerpCoord(point_first[0], point_first[1], point_end[0], point_end[1], w)
        point_max_start = []
        point_max_end = []
        max_lenght = -1

        for step in range(1, w):
            p1 = (x1 - step, y1)
            p2 = (x2 - step, y2)
            points_temp = []
            for pt in zip(*line(*p1, *p2)):
                pt = [int(pt[0]), int(pt[1])]
                if cv2.pointPolygonTest(contour, pt, False) == 0:  # On contour
                    points_temp.append(pt)

            if len(points_temp) < 2:
                continue
            for i in range(len(points_temp) - 1):
                for j in range(i + 1, len(points_temp)):
                    dist = math.hypot(points_temp[j][0] - points_temp[i][0], points_temp[j][1] - points_temp[i][1])
                    if dist > max_lenght:
                        max_lenght = dist
                        point_max_start = points_temp[i]
                        point_max_end = points_temp[j]
        heights.append(round(max_lenght, 1))
        if max_lenght == -1:
            continue
        cv2.circle(img_with_contours, point_max_start, 1, (0, 0, 255), 1)
        cv2.circle(img_with_contours, point_max_end, 1, (0, 0, 255), 1)
        cv2.line(img_with_contours, point_max_start, point_max_end, (255, 0, 0), 1)

    # lenghts = []
    # for contour in contours:
    #     point1_height = []
    #     point2_height = []
    #     max_height = 0
    #     x, y, w, h = cv2.boundingRect(contour)
    #     for x_temp in range(x, x+w):
    #         points_y = []
    #         for dot in contour:
    #             if dot[0][0] == x_temp:
    #                 points_y.append([dot[0][0], dot[0][1]])
    #         if len(points_y) < 2:
    #             continue
    #         else:
    #             for i in range(len(points_y)):
    #                 for j in range(i+1, len(points_y)):
    #                     lenght = abs(points_y[i][1] - points_y[j][1])
    #                     if lenght > max_height:
    #                         max_height = lenght
    #                         point1_height = points_y[i]
    #                         point2_height = points_y[j]
    #
    #     lenghts.append([w, max_height])
    #     cv2.line(img_with_counters, point1_height, point2_height, (255, 0, 0), 1)
    #     median_y = point1_height[1] - int((point1_height[1]-point2_height[1])/2)
    #     cv2.line(img_with_counters, (x, median_y), (x+w, median_y), (255, 0, 0), 1)

    # cv2.imshow("Image", img_with_contours)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return lengths, heights


class ImageAnaliz(object):
    def __init__(self):
        """Constructor"""
        self.path = ''
        self.name = ''
        self.img = np.zeros((1, 1, 1), np.uint8)

    def set_image(self, path):
        self.path = path
        self.img = cv2.imread(path)
        self.img = cv2.medianBlur(self.img, 5)
        self.name = str.split(str.split(path, '/')[-1], '.')[0]

    def getThreshold(self, v: float):
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        ret, th1 = cv2.threshold(img_gray, v, 255, cv2.THRESH_BINARY)
        title = 'Global Thresholding (v = ' + str(v) + ")"
        return self.img, th1, title

    def getArea(self, th, check1, check2):
        # Find the contours using binary image
        contours, hierarchy = cv2.findContours(th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[1:]
        contoursSorted = sorted(contours, key=lambda k: cv2.contourArea(k))[::-1]

        # Count areas
        areas = []
        for i in range(len(contours)):
            area: float = cv2.contourArea(contoursSorted[i])
            areas.append(area)

        # Find sum of areas
        allArea = int(sum(areas))

        # # Also you can find perimeter if you need
        # perimeters = []
        # for i in range(len(contours)):
        #     perimeter: float = cv2.arcLength(contours[i], True)
        #     perimeters.append(round(perimeter, 4))
        #     print(i, 'Perimeter:', perimeter)

        # Draw contours
        color_green = (0, 255, 0)
        color_blue = (255, 0, 0)
        if check1:
            if check2:
                self.img = cv2.drawContours(self.img, contours, -1, color_blue, 1)
            else:
                self.img = cv2.drawContours(self.img, contours, -1, color_green, 1)
        img_temp = self.img.copy()
        img_with_counters_and_areas = cv2.drawContours(img_temp, contours, -1, color_green, 1)

        if check2:
            for j in range(len(contours)):
                x, y = contoursSorted[j][0][0][0], contoursSorted[j][0][0][1]
                cv2.putText(img_with_counters_and_areas, f'{j + 1}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 255, 255), 1)
        return img_with_counters_and_areas, allArea, contoursSorted, areas

    def mainFunc(self, val1, val2):
        _, allArea, _, _ = self.getArea(self.getThreshold(250)[1], False, False)
        img_with_counters_and_areas1, allArea1, contours, areas = self.getArea(self.getThreshold(val1)[1], True, True)
        lengths, heights = findWidth(contours, img_with_counters_and_areas1)
        _, allArea2, _, _ = self.getArea(self.getThreshold(val2)[1], True, False)

        if not os.path.isdir(self.name + ' result'):
            os.mkdir(self.name + ' result')

        # Save images
        path1 = str(self.name + ' result/contours ulcers.png')
        cv2.imwrite(path1, img_with_counters_and_areas1)
        path2 = str(self.name + ' result/contours of brown areas.png')
        cv2.imwrite(path2, self.img)

        # Write info about area in the txt file
        data_file = open(self.name + ' result/data.txt', "w+")
        data_file.write('Вся площадь: ' +
                        str(allArea) + '\n')
        data_file.write('Сумарная площадь язв: ' +
                        str(allArea1) + '\n')
        data_file.write('Сумарная коричневых участков: ' +
                        str(allArea2 - allArea1) + '\n')
        data_file.write('Отношение площади язв к всей площади: ' +
                        str(round(allArea1 / allArea, 3)) + '\n')
        data_file.write('Отношение площади язв к коричневым участкам: ' +
                        str(round(allArea1 / (allArea2 - allArea1), 3)) + '\n')
        data_file.write('Отношение площади коричневых участков к всей площади: ' +
                        str(round((allArea2 - allArea1) / allArea, 3)) + '\n')
        data_file.write('Отношение площади язв и коричневых участков к всей площади: ' +
                        str(round(allArea2 / allArea, 3)) + '\n')
        data_file.write(' Площадь и размер каждого контура языв:\n')
        for k in range(len(contours)):
            data_file.write("Площадь контура " + str(k + 1) + ": " + str(round(areas[k])) +
                            ", длина " + str(lengths[k]) + ', высота ' + str(heights[k]) + '\n')
        data_file.close()
        return img_with_counters_and_areas1, allArea1
