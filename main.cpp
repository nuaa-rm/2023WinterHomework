//
// Created by stevegao on 23-1-4.
//
#include <iostream>
#include <opencv2/opencv.hpp>
#include <vector>
#include <cmath>

using namespace std;
using namespace cv;

std::vector<std::pair<cv::Point, cv::Point>>
paint_line_if_color(const cv::Mat &image, const cv::Point &point1, const cv::Point &point2, const cv::Vec3b &color) {
    std::vector<std::pair<cv::Point, cv::Point>> lines = {};
    // 获取直线的长度
    int length = (int) std::sqrt(std::pow(point1.x - point2.x, 2) + std::pow(point1.y - point2.y, 2));

    // 遍历直线上的每个像素
    for (int i = 16; i < length - 16; i++) {
        int x = point1.x + i * (point2.x - point1.x) / length;
        int y = point1.y + i * (point2.y - point1.y) / length;
        // 获取像素的颜色
        cv::Vec3b pixel_color = image.at<cv::Vec3b>(y, x);
        // 如果像素的颜色与特定的RGB颜色不同，则不涂色
        if (pixel_color[0] != color[0] || pixel_color[1] != color[1] || pixel_color[2] != color[2]) {
            return lines;
        }
    }

    // 如果所有像素的颜色都与特定的RGB颜色相同，则绘制蓝色的直线
    lines.emplace_back(point1, point2);
    return lines;
}

int main() {
    char img_path[80];
    cin >> img_path;
    Mat img = imread(img_path, IMREAD_UNCHANGED);
    int loc_max = 0;
    vector<Point> points;
    std::vector<std::pair<cv::Point, cv::Point>> p;

    Mat image = imread(img_path, IMREAD_GRAYSCALE);
    imshow("raw", image);
    Mat kernel = getStructuringElement(MORPH_RECT, Size(3, 3));
    Mat dilate_img;
    dilate(image, dilate_img, kernel);
    Mat erode_img;
    erode(image, erode_img, kernel);

    Mat absdiff_img;
    absdiff(dilate_img, erode_img, absdiff_img);
    Mat threshold_img;
    threshold(absdiff_img, threshold_img, 40, 255, THRESH_BINARY);
    Mat result;
    bitwise_not(threshold_img, result);
    imshow("circles", result);

    vector<Vec3f> circles;
    HoughCircles(result, circles, HOUGH_GRADIENT, 1, 10, 100, 15, 15, 30);
    // 绘制圆形包围框
    for (auto &i: circles) {
        // 圆的坐标
        int x = i[0];
        int y = i[1];
        int r = i[2];
        // 绘制圆形包围框
        if (x > loc_max) {
            loc_max = x;
        }
        if (y > loc_max) {
            loc_max = y;
        }
        int times = ceil(loc_max / 50);
        for (int tmp = 0; tmp < times + 1; tmp++) {
            if (x > 50 * tmp - 5 && x < 50 * tmp + 5) {
                x = 50 * tmp;
            }
            if (y > 50 * tmp - 5 && y < 50 * tmp + 5) {
                y = 50 * tmp;
            }
        }
        points.emplace_back(x, y);
        circle(img, Point(x, y), r + 2, Scalar(211, 204, 255), -1);
        circle(img, Point(x, y), 2, Scalar(255, 255, 255), -1);
    }
    //查询circles的个数
    int num = circles.size();
    cout << num << endl;
    //输出points元素x,y
    for (int i = 0; i < num; i++) {
        cout << points[i].x << " " << points[i].y << endl;
    }
    imshow("pink", img);

    auto processed_points = std::vector<pair<cv::Point, cv::Point>>();


    for (int i = 0; i < points.size(); ++i) {
        for (int j = i + 1; j < points.size(); ++j) {
            auto painted_lines = paint_line_if_color(img, points[i], points[j], Vec3b(211, 204, 255));
            p.insert(p.end(), painted_lines.begin(), painted_lines.end());
        }
    }
    int num_lines = p.size();
    cout << num_lines << endl;
    //输出p的所有元素
    for (auto &i: p) {
        for (int j = 0; j < num; ++j) {
            if (i.first.x == points[j].x && i.first.y == points[j].y) {
                cout << j << " ";
                break;
            }
        }
        for (int j = 0; j < num; ++j) {
            if (i.second.x == points[j].x && i.second.y == points[j].y) {
                cout << j << endl;
                break;
            }
        }
        // cout << i.first.x << " " << i.first.y << " " << i.second.x << " " << i.second.y << endl;
    }


    img = imread(img_path, IMREAD_UNCHANGED);
    for (auto &i: p) {
        line(img, i.first, i.second, Scalar(0, 255, 0), 2);
    }
    imshow("result", img);
    destroyAllWindows();
    return 0;
}