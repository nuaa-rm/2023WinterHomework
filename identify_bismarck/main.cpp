#include <cmath>
#include <iostream>
#include <string>
#include <vector>

#include <opencv2/opencv.hpp>

#define FAST_MODE
#define RESIZE_RATE 0.5

cv::Scalar nodeColor[2]{cv::Scalar(100, 53, 241), cv::Scalar(104, 57, 245)};
cv::Scalar edgeColor[2]{cv::Scalar(209, 202, 252), cv::Scalar(213, 206, 255)};
struct edgeI {
    int start = -1, end = -1;
};

class edge {
private:
    int count = 1;
public:
    cv::Point2i start, end;
    double theta;

    edge(cv::Point2i p1, cv::Point2i p2) {
        if (p1.x < p2.x) {
            start = p1;
            end = p2;
        } else {
            start = p2;
            end = p1;
        }
        theta = atan2(end.y - start.y, end.x - start.x);
    }

    double getLength(cv::Point2i p) const {
        return abs(((p.y - start.y) * cos(theta) - (p.x - start.x) * sin(theta) +
                    (p.y - end.y) * cos(theta) - (p.x - end.x) * sin(theta)) / 2);
    }

    double getLengthFromStart(cv::Point2i p) const {
        return (p.x - start.x) * cos(theta) + (p.y - start.y) * sin(theta);
    }

    double getLengthFromEnd(cv::Point2i p) const {
        return (p.x - end.x) * cos(theta) + (p.y - end.y) * sin(theta);
    }

    int getY(int x) {
        return (int) (((double) x - start.x) * sin(theta) + start.y);
    }

    edge &operator+=(const cv::Point2i &p) {
        if (getLengthFromStart(p) < 0) {
            theta *= count;
            count++;
            start = p;
            theta += atan2(end.y - start.y, end.x - start.x);
            theta /= count;
        } else if (getLengthFromEnd(p) > 0) {
            theta *= count;
            count++;
            end = p;
            theta += atan2((end.y - start.y), end.x - start.x);
            theta /= count;
        }
        return *this;
    }
};

double getLength(cv::Point2i p1, cv::Point2i p2);

float findNodes(const cv::Mat &img, std::vector<cv::Point2i> &nodes);

void findEdges(const cv::Mat &img, const std::vector<cv::Point2i> &nodes, std::vector<edgeI> &edges, float nodeRadius);

int main() {
    std::string path;
    std::cin >> path;

    cv::Mat raw_image = cv::imread(path);
    std::vector<cv::Point2i> nodes;
    std::vector<edgeI> edges;

    float nodeRadius = findNodes(raw_image, nodes);
    findEdges(raw_image, nodes, edges, nodeRadius);

    std::cout << nodes.size() << std::endl;
    for (const auto &node : nodes) {
        std::cout << node.x << " " << node.y << std::endl;
    }

    std::cout << edges.size() << std::endl;
    for (const auto &edge : edges) {
        std::cout << edge.start << " " << edge.end << std::endl;
    }

#ifndef FAST_MODE
    cv::imwrite("result.png", raw_image);
#endif
    return 0;
}

float findNodes(const cv::Mat &img, std::vector<cv::Point2i> &nodes) {
    cv::Mat nodesMask;
    cv::inRange(img, nodeColor[0], nodeColor[1], nodesMask);

    std::vector<std::vector<cv::Point2i>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(nodesMask, contours, hierarchy, cv::RETR_TREE, cv::CHAIN_APPROX_NONE);

#ifdef FAST_MODE
    float mean = 0;
#else
    struct node {
        cv::Point2f center;
        float radius{};
    };
    std::vector<node> _nodes;
#endif


    for (int i = 0; i < contours.size(); i++) {
        if (hierarchy[i][2] >= 0) {
#ifdef FAST_MODE
            float radius;
            cv::Point2f center;
            cv::minEnclosingCircle(contours[i], center, radius);
            mean += radius;
            nodes.push_back(center);
#else
            node n;
            cv::minEnclosingCircle(contours[i], n.center, n.radius);
            _nodes.push_back(n);
#endif
        }
    }

#ifdef FAST_MODE
    mean /= (float) nodes.size();
#else
    float mean = 0;
    for (const auto& n: _nodes) {
        mean += n.radius;
    }
    mean /= (float)_nodes.size();

    for (const auto& n: _nodes) {
        if (abs(n.radius - mean) < 0.1 * mean) {
            nodes.push_back(n.center);
        }
    }
#endif
    return mean;
}

double getLength(cv::Point2i p1, cv::Point2i p2) {
    return sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2));
}

int getEdgeFromContour(const cv::Mat img, const std::vector<cv::Point2i> &contour, std::vector<edge> &edges) {
    if (contour.size() <= 1) {
        return 0;
    }
    int start = 0, end = (int) contour.size() - 1, count = 0;
    edge e(contour[start], contour[end]);
    while (end != 0) {
        cv::circle(img, contour[end], 2, cv::Scalar(255, 0, 0), -1);
        end--;
        if (e.getLength(contour[end]) < 2) {
            e += contour[end];
        } else {
            break;
        }
    }
    while (start < end) {
        cv::circle(img, contour[start], 2, cv::Scalar(255, 0, 0), -1);
        start++;
        if (e.getLength(contour[start]) < 2) {
            e += contour[start];
        } else {
            break;
        }
    }
    if (getLength(e.start, e.end) > 3) {
        count++;
        edges.push_back(e);
    }
    if (start > 0) {
        int f = start - 1, t = start;
        cv::circle(img, contour[f], 2, cv::Scalar(255, 0, 0), -1);
        while (t <= end) {
            edge _e(contour[f], contour[t]);
            while (t <= end) {
                cv::circle(img, contour[t], 2, cv::Scalar(255, 0, 0), -1);
                t++;
                if (_e.getLength(contour[t]) < 2) {
                    _e += contour[t];
                } else {
                    break;
                }
            }
            f = t - 1;
            if (getLength(_e.start, _e.end) > 3) {
                count++;
                edges.push_back(_e);
            }
        }
    }
    return count;
}

void findEdgesImpl(const cv::Mat &img, const cv::Mat &edgeMaskR, const std::vector<edge>&_edges,
                   float nodeRadius, const std::vector<cv::Point2i> &nodes, std::vector<edgeI> &edges, float thresh,
                   const cv::Scalar& lineColor) {
    for (const auto &e: _edges) {
        cv::line(img, e.start, e.end, cv::Scalar(0, 255, 0), 1);
    }
    for (int i = 0; i < _edges.size(); i++) {
        cv::line(img, _edges[i].start, _edges[i].end, cv::Scalar(0, 255, 0), 1);
    }

    for (const auto &_e: _edges) {
        std::vector<int> starts, ends;
        for (int i = 0; i < nodes.size(); i++) {
            double length, l2s, l2e;
            length = _e.getLength(nodes[i]);
            l2s = _e.getLengthFromStart(nodes[i]);
            l2e = _e.getLengthFromEnd(nodes[i]);
            if (length < thresh) {
                if (l2s < 0) {
                    starts.push_back(i);
                } else if (l2e > 0) {
                    ends.push_back(i);
                }
            }
        }
        for (const auto &s: starts) {
            for (const auto &e: ends) {
                edge e1(nodes[s], nodes[e]);
                bool ok = true;
                for (int i = 0; i < _edges.size(); i++) {
                    if (i == s || i == e) {
                        continue;
                    }
                    double length, l2s, l2e;
                    length = e1.getLength(nodes[i]);
                    l2s = e1.getLengthFromStart(nodes[i]);
                    l2e = e1.getLengthFromEnd(nodes[i]);
                    if (length < nodeRadius * 0.05 && l2s > 0 && l2e < 0) {
                        ok = false;
                        break;
                    }
                }
                if (ok) {
                    cv::Mat em(edgeMaskR.size(), CV_8UC1, cv::Scalar(0));
                    cv::line(em, nodes[s] * RESIZE_RATE, nodes[e]  * RESIZE_RATE, 255,
                             (int)(nodeRadius * RESIZE_RATE * .8));
                    cv::Mat e2 = em - edgeMaskR > 0;
                    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(2, 2));
                    cv::erode(e2, e2, kernel);
                    if (cv::countNonZero(e2) > 0) {
                        ok = false;
                    }
                }
                if (ok) {
                    for (const auto &edge: edges) {
                        if (edge.start == s && edge.end == e || edge.start == e && edge.end == s) {
                            ok = false;
                            break;
                        }
                    }
                }
                if (ok) {
                    edges.push_back({s, e});
                    cv::line(img, nodes[s], nodes[e], lineColor, 2);
                }
            }
        }
    }
}

void findEdgesImpl(const cv::Mat &img, const cv::Mat &edgeMaskR, const std::vector<std::vector<cv::Point2i>> &contours,
                   float nodeRadius, const std::vector<cv::Point2i> &nodes, std::vector<edgeI> &edges, float thresh,
                   const cv::Scalar& lineColor) {
    std::vector<edge> _edges;
    for (const auto &contour: contours) {
        getEdgeFromContour(img, contour, _edges);
    }
    findEdgesImpl(img, edgeMaskR, _edges, nodeRadius, nodes, edges, thresh, lineColor);
}

edge getEdgeByPCA(const std::vector<cv::Point2i> &contour) {
    cv::Mat data = cv::Mat((int)contour.size(), 2, CV_16UC1);
    for (int i = 0; i < contour.size(); i++) {
        data.at<short>(i, 0) = contour[i].x;
        data.at<short>(i, 1) = contour[i].y;
    }
    cv::PCA pca(data, cv::Mat(), cv::PCA::DATA_AS_ROW);
    cv::Mat data_p = pca.project(data);
    int s, e;
    float sMin = 1e10, eMax = -1e10;
    for (int i = 0; i < data_p.rows; i++) {
        if (data_p.at<float>(i, 0) < sMin) {
            sMin = data_p.at<float>(i, 0);
            s = i;
        }
        if (data_p.at<float>(i, 0) > eMax) {
            eMax = data_p.at<float>(i, 0);
            e = i;
        }
    }
    return edge(contour[s], contour[e]);
}

cv::Mat getEdgeCompare(const cv::Mat& edgesMask, const std::vector<cv::Point2i> &nodes, std::vector<edgeI> &edges,
                       float nodeRadius) {
    cv::Mat em(edgesMask.size(), CV_8UC1, cv::Scalar(0));
    for (const auto &edge: edges) {
        cv::line(em, nodes[edge.start], nodes[edge.end], 255, (int)(nodeRadius * 0.8));
    }
    cv::Mat em2(edgesMask.size(), CV_8UC1, cv::Scalar(0));
    for (const auto &node: nodes) {
        cv::circle(em2, node, (int)nodeRadius, 255, -1);
    }
    em ^= edgesMask;
    em = em - em2 > 0;
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_ELLIPSE, {(int)nodeRadius, (int)nodeRadius});
    cv::Mat kernel2 = cv::getStructuringElement(cv::MORPH_ELLIPSE, {(int)(nodeRadius*.4), (int)(nodeRadius*.4)});
    cv::dilate(em, em, kernel);
    cv::erode(em, em, kernel2);
    return em;
}

void findEdges(const cv::Mat &img, const std::vector<cv::Point2i> &nodes, std::vector<edgeI> &edges, float nodeRadius) {
    cv::Mat edgesMask;
    cv::inRange(img, edgeColor[0], edgeColor[1], edgesMask);

    std::vector<std::vector<cv::Point2i>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(edgesMask, contours, hierarchy, cv::RETR_LIST, cv::CHAIN_APPROX_TC89_KCOS);
    cv::Mat edgeMaskR = edgesMask.clone();
    for (const auto &node: nodes) {
        cv::circle(edgeMaskR, node, (int) nodeRadius, 255, -1);
    }
    cv::resize(edgeMaskR, edgeMaskR, cv::Size(), RESIZE_RATE, RESIZE_RATE);

    findEdgesImpl(img, edgeMaskR, contours, nodeRadius, nodes, edges, nodeRadius, {0, 0, 0});

    cv::Mat em;
    std::vector<edge> _edges;

    contours.clear();
    hierarchy.clear();
    em = getEdgeCompare(edgesMask, nodes, edges, nodeRadius);
    cv::findContours(em, contours, hierarchy, cv::RETR_LIST, cv::CHAIN_APPROX_NONE);
    for (const auto& contour: contours) {
        edge _e = getEdgeByPCA(contour);
        _edges.push_back(_e);
        cv::line(img, _e.start, _e.end, cv::Scalar(255, 0, 0), 1);
    }
    findEdgesImpl(img, edgeMaskR, _edges, nodeRadius, nodes, edges, nodeRadius * 3, {255, 0, 0});

    contours.clear();
    hierarchy.clear();
    _edges.clear();
    em = getEdgeCompare(edgesMask, nodes, edges, nodeRadius);
    cv::findContours(em, contours, hierarchy, cv::RETR_LIST, cv::CHAIN_APPROX_NONE);
    for (const auto& contour: contours) {
        edge _e = getEdgeByPCA(contour);
        _edges.push_back(_e);
        cv::line(img, _e.start, _e.end, cv::Scalar(255, 0, 0), 1);
    }
    findEdgesImpl(img, edgeMaskR, _edges, nodeRadius, nodes, edges, nodeRadius * 3, {150, 150, 150});
}
