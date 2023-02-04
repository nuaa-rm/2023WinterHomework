//
// Created by stevegao on 23-1-4.
//
#include <iostream>
#include <opencv2/opencv.hpp>
#include <vector>
#include <utility>

using namespace std;
using namespace cv;

cv::Scalar nodeColor[2]{cv::Scalar(100, 53, 241), cv::Scalar(104, 57, 245)};
cv::Scalar edgeColor[2]{cv::Scalar(209, 202, 252), cv::Scalar(213, 206, 255)};

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

int matrix_size, num_lines;
vector<int> path;
vector<vector<int>> edges;
vector<vector<bool>> visited_edge;
vector<int> target_path;

bool backtrack(int u) {
    if (path.size() == num_lines + 1) {
        target_path = path;
        return true;
    }
    bool flag = false;
    for (int i = 0; i < matrix_size; i++) {
        if (edges[u][i] && !visited_edge[u][i] && !visited_edge[i][u]) {
            path.push_back(i);
            visited_edge[u][i] = true;
            visited_edge[i][u] = true;
            if (backtrack(i)) flag = true;
            visited_edge[u][i] = false;
            visited_edge[i][u] = false;
            path.pop_back();
        }
    }
    return flag;
}


int main() {
    char img_path[80];
    cin >> img_path;
    Mat img = cv::imread(img_path);
    int loc_max = 0;
    vector<Point> points;
    std::vector<std::pair<cv::Point, cv::Point>> lines;
    Mat nodesMask, edgesMask;
    cv::inRange(img, nodeColor[0], nodeColor[1], nodesMask);
    cv::inRange(img, edgeColor[0], edgeColor[1], edgesMask);
    imshow("nodes", nodesMask);
    imshow("edges", edgesMask);

    vector<Vec3f> circles;
    HoughCircles(nodesMask, circles, HOUGH_GRADIENT, 1, 10, 100, 15, 10, 40);
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
    int num_circles = circles.size();
    cout << num_circles << endl;

    matrix_size = num_circles;

    edges = vector<vector<int>>(matrix_size, vector<int>(matrix_size, 0));
    visited_edge = vector<vector<bool>>(matrix_size, vector<bool>(matrix_size, false));

    //输出points元素x,y
    for (int i = 0; i < num_circles; i++) {
        cout << points[i].x << " " << points[i].y << endl;
    }
    Mat edge_s;
    // 边缘检测
    Canny(edgesMask, edge_s, 50, 150);
    // 检测直线
    vector<Vec4i> line_s;
    HoughLinesP(edge_s, line_s, 1, CV_PI / 1440, 20, 30, 10);
    int thickness = 1;
    // 在图像上绘制直线
    for (auto l: line_s) {
        line(img, Point(l[0], l[1]), Point(l[2], l[3]), Scalar(0, 0, 255), thickness, LINE_AA);
    }

    // 显示图像
    imshow("Detected Lines", img);
    waitKey(0);

    for (int i = 0; i < points.size(); ++i) {
        for (int j = i + 1; j < points.size(); ++j) {
            auto painted_lines = paint_line_if_color(img, points[i], points[j], Vec3b(211, 204, 255));
            lines.insert(lines.end(), painted_lines.begin(), painted_lines.end());
        }
    }
    num_lines = lines.size();
    cout << num_lines << endl;
    //输出lines的所有元素
    vector<int> list_1, list_2;
    vector<int> list_num(num_circles, 0);
    for (auto &i: lines) {
        int tmp_1, tmp_2;
        for (int j = 0; j < num_circles; ++j) {
            if (i.first.x == points[j].x && i.first.y == points[j].y) {
                list_1.emplace_back(j);
                tmp_1 = j;
                break;
            }
        }
        for (int j = 0; j < num_circles; ++j) {
            if (i.second.x == points[j].x && i.second.y == points[j].y) {
                list_2.emplace_back(j);
                tmp_2 = j;
                break;
            }
        }
        edges[tmp_1][tmp_2] = 1;
        edges[tmp_2][tmp_1] = 1;
        list_num[tmp_1]++;
        list_num[tmp_2]++;
    }


    for (int i = 0; i < num_circles; ++i) {
        if (list_num[i] % 2 == 1 || i == num_circles - 1) {
            path.clear();
            path.push_back(i);
            backtrack(i);
            break;
        }
    }

    for (int i = 0; i < target_path.size() - 1; ++i) {
        cout << target_path[i] << " " << target_path[i + 1] << endl;
    }
    return 0;
}

