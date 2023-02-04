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

cv::Vec4f get_line(const cv::Point &point1, const cv::Point &point2) {
    float k, b;
    if (point1.x == point2.x) {
        k = 0;
        b = point1.x;
        return {1, 0, -b, 0};
    } else {
        k = (float) (point2.y - point1.y) / (point2.x - point1.x);
        b = point1.y - k * point1.x;
        return {k, -1, 0, b};
    }
}

cv::Vec4f line_1, line_2;

void get_parallel_lines(cv::Vec4f line, float distance) {
    cv::Point point1, point2;
    float k = line[0] / line[1];
    float b = line[3] / line[1];
    if (k == 0) {
        point1 = cv::Point(b - distance, 0);
        point2 = cv::Point(b + distance, 500);
    } else if (std::abs(k) > 9999) {
        point1 = cv::Point(0, b - distance);
        point2 = cv::Point(500, b + distance);
    } else {
        point1 = cv::Point(0, b - distance * k);
        point2 = cv::Point(500, (b + distance) * k);
    }
    line_1 = get_line(point1, point2);
    line_2 = get_line(point2, point1);
}

bool is_in_area(cv::Point point, cv::Vec4f line1, cv::Vec4f line2) {
    float x = point.x, y = point.y;
    float a1 = line1[1] / line1[0], b1 = line1[3] / line1[0];
    float a2 = line2[1] / line2[0], b2 = line2[3] / line2[0];
    if (a1 > 9999 || a1 < -9999) {
        float value2 = y - a2 * x - b2;
        if (value2 >= 0) {
            return true;
        } else {
            return false;
        }
    } else if (a2 > 9999 || a2 < -9999) {
        float value1 = y - a1 * x - b1;
        if (value1 >= 0) {
            return true;
        } else {
            return false;
        }
    } else {
        float value1 = y - a1 * x - b1;
        float value2 = y - a2 * x - b2;
        if (value1 * value2 >= 0) {
            return true;
        } else {
            return false;
        }
    }
}

int nearest_multiple(int x) {
    int n = floor((x - 40) / 100);
    return 50 + 100 * n;
}


std::vector<std::pair<cv::Point, cv::Point>> lines;

void add_to_vector_if_not_exists(const std::pair<cv::Point, cv::Point> &element) {
    for (const auto &line: lines) {
        if (line == element) {
            return;
        }
    }
    lines.push_back(element);
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
    Mat img_COPY = img;
    int loc_max = 0;
    vector<Point> points;
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
    HoughLinesP(edge_s, line_s, 1, CV_PI / 1440, 50, 30, 15);
    int thickness = 1;
    // 在图像上绘制直线
    for (auto l: line_s) {
        line(img_COPY, Point(l[0], l[1]), Point(l[2], l[3]), Scalar(0, 0, 0), thickness, LINE_AA);
    }
    // 显示图像
    imshow("Detected Lines", img_COPY);
    for (auto &l: line_s) {
        int minLength[6];
        for (int &i: minLength) {
            i = 999999;
        }
        Point matched_point_1_1, matched_point_1_2, matched_point_2_1, matched_point_2_2, matched_point_3_1, matched_point_3_2;
        if (abs(l[0] - l[2]) <= 10) {
            l[0] = nearest_multiple(l[0]);
            for (auto &point: points) {
                if (point.x == l[0]) {
                    if (abs(point.y - l[1]) < minLength[0]) {
                        minLength[0] = abs(point.y - l[1]);
                        matched_point_1_1 = point;
                    }
                    if (abs(point.y - l[3]) < minLength[1]) {
                        minLength[1] = abs(point.y - l[3]);
                        matched_point_1_2 = point;
                    }
                }
            }
            if (matched_point_1_1 != matched_point_1_2)
                add_to_vector_if_not_exists(make_pair(matched_point_1_1, matched_point_1_2));
        } else if (abs(l[1] - l[3]) <= 10) {
            l[1] = nearest_multiple(l[1]);
            for (auto &point: points) {
                if (point.y == l[1]) {
                    if (abs(point.x - l[0]) < minLength[2]) {
                        minLength[2] = abs(point.x - l[0]);
                        matched_point_2_1 = point;
                    }
                    if (abs(point.x - l[2]) < minLength[3]) {
                        minLength[3] = abs(point.x - l[2]);
                        matched_point_2_2 = point;
                    }
                }
            }
            if (matched_point_2_1 != matched_point_2_2)
                add_to_vector_if_not_exists(make_pair(matched_point_2_1, matched_point_2_2));
        } else {
            get_parallel_lines(l, 20);
            for (auto &point: points) {
                if (is_in_area(point, line_1, line_2)) {
                    if (sqrt((point.x - l[0]) * (point.x - l[0]) + (point.y - l[1]) * (point.y - l[1])) <
                        minLength[4]) {
                        minLength[4] = sqrt((point.x - l[0]) * (point.x - l[0]) + (point.y - l[1]) * (point.y - l[1]));
                        matched_point_3_1 = point;
                    }
                    if (sqrt((point.x - l[2]) * (point.x - l[2]) + (point.y - l[3]) * (point.y - l[3])) <
                        minLength[5]) {
                        minLength[5] = sqrt((point.x - l[2]) * (point.x - l[2]) + (point.y - l[3]) * (point.y - l[3]));
                        matched_point_3_2 = point;
                    }
                }
            }
            if (matched_point_3_1 != matched_point_3_2)
                add_to_vector_if_not_exists(make_pair(matched_point_3_1, matched_point_3_2));
        }
    }



//    for (int i = 0; i < points.size(); ++i) {
//        for (int j = i + 1; j < points.size(); ++j) {
//            auto painted_lines = paint_line_if_color(img, points[i], points[j], Vec3b(211, 204, 255));
//            lines.insert(lines.end(), painted_lines.begin(), painted_lines.end());
//        }
//    }

    num_lines = lines.size();
    cout << num_lines << endl;
    //输出lines的所有元素
    vector<int> list_num(num_circles, 0);
    for (auto &i: lines) {
        int tmp_1, tmp_2;
        for (int j = 0; j < num_circles; ++j) {
            if (i.first.x == points[j].x && i.first.y == points[j].y) {
                tmp_1 = j;
                break;
            }
        }
        for (int j = 0; j < num_circles; ++j) {
            if (i.second.x == points[j].x && i.second.y == points[j].y) {
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

