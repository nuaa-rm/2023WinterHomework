//
// Created by stevegao on 23-1-4.
//
#include <iostream>
#include <opencv2/opencv.hpp>
#include <vector>
#include <utility>


cv::Scalar nodeColor[2]{cv::Scalar(100, 53, 241), cv::Scalar(104, 57, 245)};
cv::Scalar edgeColor[2]{cv::Scalar(209, 202, 252), cv::Scalar(213, 206, 255)};

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


void add_to_vector_if_not_exists(std::vector<std::pair<cv::Point, cv::Point>> &lines,
                                 const std::pair<cv::Point, cv::Point> &element) {
    for (const auto &line: lines) {
        if (line == element) {
            return;
        }
    }
    lines.push_back(element);
}

void compare_and_swap(int &x_0, int &y_0, int &x_1, int &y_1, bool flag) {
    if (flag == 0) {
        if (y_0 < y_1) {
            std::swap(y_0, y_1);
            std::swap(x_0, x_1);
        }
    } else {
        if (x_0 < x_1) {
            std::swap(y_0, y_1);
            std::swap(x_0, x_1);
        }
    }
}

float get_length(int &x_0, int &y_0, int &x_1, int &y_1, int flag) {
    if (flag == 0) {
        return (y_1 - y_0);
    } else if (flag == 1) {
        return (x_1 - x_0);
    } else {
        return sqrt((x_1 - x_0) * (x_1 - x_0) + (y_1 - y_0) * (y_1 - y_0));
    }
}

int matrix_size, num_lines;
std::vector<int> path;
std::vector<std::vector<int>> edges;
std::vector<std::vector<bool>> visited_edge;
std::vector<int> target_path;

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
    std::cin >> img_path;
    cv::Mat img = cv::imread(img_path);
    int loc_max = 0;
    std::vector<cv::Point> points;
    std::vector<std::pair<cv::Point, cv::Point>> lines;
    cv::Mat nodesMask, edgesMask;
    cv::inRange(img, nodeColor[0], nodeColor[1], nodesMask);
    cv::inRange(img, edgeColor[0], edgeColor[1], edgesMask);

    std::vector<cv::Vec3f> circles;
    HoughCircles(nodesMask, circles, cv::HOUGH_GRADIENT, 1, 10, 100, 15, 10, 40);
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
    std::cout << num_circles << std::endl;

    matrix_size = num_circles;

    edges = std::vector<std::vector<int>>(matrix_size, std::vector<int>(matrix_size, 0));
    visited_edge = std::vector<std::vector<bool>>(matrix_size, std::vector<bool>(matrix_size, false));

    //输出points元素x,y
    for (int i = 0; i < num_circles; i++) {
        std::cout << points[i].x << " " << points[i].y << std::endl;
    }
    cv::Mat edge_s;
    // 边缘检测
    Canny(edgesMask, edge_s, 50, 150);
    // 检测直线
    std::vector<cv::Vec4i> line_s;
    HoughLinesP(edge_s, line_s, 1, CV_PI / 1440, 50, 30, 15);
    int thickness = 1;
//    // 在图像上绘制直线
//    for (auto l: line_s) {
//        line(img, cv::Point(l[0], l[1]), cv::Point(l[2], l[3]), cv::Scalar(0, 0, 0), thickness, cv::LINE_AA);
//    }
    imshow("img", img);
    for (auto &l: line_s) {
        int minLength[6];
        for (int &i: minLength) {
            i = 999999;
        }
        cv::Point matchedPoint[6];
        if (abs(l[0] - l[2]) <= 10) {
            l[0] = nearest_multiple(l[0]);
            l[2] = l[0];
            compare_and_swap(l[0], l[1], l[2], l[3], false);
            for (auto &point: points) {
                if (point.x == l[0]) {
                    float tmp_length = get_length(l[0], l[1], point.x, point.y, 0);
                    if (tmp_length > 0) {
                        if (tmp_length < minLength[0]) {
                            minLength[0] = tmp_length;
                            matchedPoint[0] = point;
                        }
                    } else {
                        if (abs(tmp_length) < minLength[1]) {
                            minLength[1] = abs(tmp_length);
                            matchedPoint[1] = point;
                        }
                    }
                }
            }
            if (matchedPoint[0] != matchedPoint[1])
                add_to_vector_if_not_exists(lines, std::make_pair(matchedPoint[0], matchedPoint[1]));
        } else if (abs(l[1] - l[3]) <= 10) {
            l[1] = nearest_multiple(l[1]);
            l[3] = l[1];
            compare_and_swap(l[0], l[1], l[2], l[3], true);
            for (auto &point: points) {
                if (point.y == l[1]) {
                    float tmp_length = get_length(l[0], l[1], point.x, point.y, 1);
                    if (tmp_length > 0) {
                        if (tmp_length < minLength[2]) {
                            minLength[2] = tmp_length;
                            matchedPoint[2] = point;
                        }
                    } else {
                        if (abs(tmp_length) < minLength[3]) {
                            minLength[3] = abs(tmp_length);
                            matchedPoint[3] = point;
                        }
                    }
                }
            }
            if (matchedPoint[2] != matchedPoint[3])
                add_to_vector_if_not_exists(lines, std::make_pair(matchedPoint[2], matchedPoint[3]));
        } else {
            compare_and_swap(l[0], l[1], l[2], l[3], true);
            get_parallel_lines(l, 20);
            for (auto &point: points) {
                if (is_in_area(point, line_1, line_2)) {
                    float tmp_length = get_length(l[0], l[1], point.x, point.y, 2);
                    if (point.x >= l[0]) {
                        if (tmp_length < minLength[4]) {
                            minLength[4] = tmp_length;
                            matchedPoint[4] = point;
                        }
                    } else if (point.x <= l[2]) {
                        if (abs(tmp_length) < minLength[5]) {
                            minLength[5] = abs(tmp_length);
                            matchedPoint[5] = point;
                        }
                    }
                }
            }
            if (matchedPoint[4] != matchedPoint[5])
                add_to_vector_if_not_exists(lines, std::make_pair(matchedPoint[4], matchedPoint[5]));
        }
    }
    for (auto &l: lines) {
        line(img, l.first, l.second, cv::Scalar(0, 0, 255), thickness, cv::LINE_AA);
    }
//    imshow("img1",img);
//    cv::waitKey(0);

    num_lines = lines.size();
    std::cout << num_lines << std::endl;
    //输出lines的所有元素
    std::vector<int> list_num(num_circles, 0);
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
        std::cout << target_path[i] << " " << target_path[i + 1] << std::endl;
    }
    return 0;
}

