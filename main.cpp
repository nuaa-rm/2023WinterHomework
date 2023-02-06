//
// Created by stevegao on 23-1-4.
//
#include <iostream>
#include <opencv2/opencv.hpp>
#include <vector>
#include <utility>

using namespace cv;
using namespace std;
Scalar nodeColor[2]{Scalar(100, 53, 241), Scalar(104, 57, 245)};
Scalar edgeColor[2]{Scalar(209, 202, 252), Scalar(213, 206, 255)};


double cross_product(const Point &A, const Point &B) {
    return A.x * B.y - A.y * B.x;
}

double distance_point_to_line(const Point &A, const Point &B, const Point &C) {
    Point BA, BC;
    BA.x = B.x - A.x;
    BA.y = B.y - A.y;
    BC.x = C.x - A.x;
    BC.y = C.y - A.y;
    return fabs(cross_product(BA, BC)) / sqrt(BA.x * BA.x + BA.y * BA.y);
}

bool
inParallelLines(const cv::Point2f &p1, const cv::Point2f &p2, float distance, const cv::Point &_point) {
    cv::Point2f direction = p2 - p1;
    Vec4f _line1, _line2;

    cv::Point2f perpendicular = cv::Point2f(direction.y, -direction.x);
    perpendicular = perpendicular / cv::norm(perpendicular) * distance;

    cv::Point2f l1_p1 = p1 + perpendicular;
    cv::Point2f l1_p2 = p2 + perpendicular;
    cv::Point2f l2_p1 = p1 - perpendicular;
    cv::Point2f l2_p2 = p2 - perpendicular;


    double d1 = distance_point_to_line(l1_p1, l1_p2, _point);
    double d2 = distance_point_to_line(l2_p1, l2_p2, _point);
    if (d1 + d2 < distance * 2 + 5) {
        return true;
    } else {
        return false;
    }
}

int nearest_multiple(int x) {
    int n = floor((x - 40) / 100);
    return 50 + 100 * n;
}

void add_to_vector_if_not_exists(vector<pair<Point, Point>> &lines,
                                 const pair<Point, Point> &element) {
    for (const auto &line: lines) {
        if (line == element) {
            return;
        }
    }
    lines.push_back(element);
}

void compare_and_swap(int &x_0, int &y_0, int &x_1, int &y_1, bool flag) {
    if (!flag) {
        if (y_0 < y_1) {
            swap(y_0, y_1);
            swap(x_0, x_1);
        }
    } else {
        if (x_0 < x_1) {
            swap(y_0, y_1);
            swap(x_0, x_1);
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
    Mat img;
    img = imread(img_path);
    int loc_max = 0;
    vector<Point> points;
    vector<pair<Point, Point>> lines;
    Vec4f line_1, line_2;
    Mat nodesMask, edgesMask;
    inRange(img, nodeColor[0], nodeColor[1], nodesMask);
    inRange(img, edgeColor[0], edgeColor[1], edgesMask);

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
    HoughLinesP(edge_s, line_s, 1, CV_PI / 1440, 50, 15, 10);
    // 在图像上绘制直线
    for (auto l: line_s) {
        line(img, Point(l[0], l[1]), Point(l[2], l[3]), Scalar(50, 100, 50), 2, LINE_AA);
    }
//    imshow("img", img);
    for (auto &l: line_s) {
        float minLength[6];
        for (float &i: minLength) {
            i = 999999;
        }
        Point matchedPoint[6];
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
            if (matchedPoint[0] != matchedPoint[1]) {
                line(img, matchedPoint[0], matchedPoint[1], Scalar(255, 0, 0), 1, LINE_AA);
                add_to_vector_if_not_exists(lines, make_pair(matchedPoint[0], matchedPoint[1]));
            }
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
            if (matchedPoint[2] != matchedPoint[3]) {
                line(img, matchedPoint[2], matchedPoint[3], Scalar(0, 200, 0), 1, LINE_AA);
                add_to_vector_if_not_exists(lines, make_pair(matchedPoint[2], matchedPoint[3]));
            }
        } else {
            compare_and_swap(l[0], l[1], l[2], l[3], true);
            for (auto &point: points) {
                if (inParallelLines(Point(l[0], l[1]), Point(l[2], l[3]), 20, point)) {
                    float tmp_length0 = point.x - l[0];
                    float tmp_length1 = point.x - l[2];
                    if (tmp_length0 >= -5) {
                        if (tmp_length0 < minLength[4]) {
                            minLength[4] = tmp_length0;
                            matchedPoint[4] = point;
                        }
                    } else if (tmp_length1 <= 5) {
                        if (abs(tmp_length1) < minLength[5]) {
                            minLength[5] = abs(tmp_length1);
                            matchedPoint[5] = point;
                        }
                    }
                }
            }
            if (matchedPoint[4] != matchedPoint[5]) {
                line(img, matchedPoint[4], matchedPoint[5], Scalar(0, 0, 200), 1, LINE_AA);
                add_to_vector_if_not_exists(lines, make_pair(matchedPoint[4], matchedPoint[5]));
            }
        }
    }
//    for (auto &l: lines) {
//        line(img, l.first, l.second, Scalar(0, 0, 255), thickness, LINE_AA);
//    }
    imshow("img1", img);
//    waitKey(0);

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
        std::cout << target_path[i] << " " << target_path[i + 1] << std::endl;
    }
    waitKey(0);
    return 0;
}