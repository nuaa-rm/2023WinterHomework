#include <cmath>
#include <iostream>
#include <string>
#include <vector>

#include <opencv2/opencv.hpp>

#define FAST_MODE

cv::Scalar nodeColor[2]{cv::Scalar(100, 53, 241), cv::Scalar(104, 57, 245)};
cv::Scalar edgeColor[2]{cv::Scalar(209, 202, 252), cv::Scalar(213, 206, 255)};
struct edgeI {
    int start = -1, end = -1;
};

class edge {
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
        return abs((p.y - start.y) * cos(theta) - (p.x - start.x) * sin(theta));
    }

    double getLengthFromStart(cv::Point2i p) const {
        return (p.x - start.x) * cos(theta) + (p.y - start.y) * sin(theta);
    }

    double getLengthFromEnd(cv::Point2i p) const {
        return (p.x - end.x) * cos(theta) + (p.y - end.y) * sin(theta);
    }

    int getY(int x) {
        return (int)(((double)x - start.x) * sin(theta) + start.y);
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
//    cv::Mat ni{raw_image.size(), CV_8UC3, cv::Scalar(255, 255, 255)};
//    for (auto& node : nodes) {
//        cv::circle(ni, node, (int)nodeRadius, nodeColor[0], -1);
//    }
    findEdges(raw_image, nodes, edges, nodeRadius);

    cv::imshow("result", raw_image);
    cv::waitKey(0);

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

std::vector<std::vector<cv::Point2i>>
findEdgesImpl(const cv::Mat& img, const cv::Mat& edgeMaskR, const std::vector<std::vector<cv::Point2i>>& contours,
              float nodeRadius, const std::vector<cv::Point2i> &nodes, std::vector<edgeI> &edges, float thresh,
              cv::Scalar lineColor) {
    std::vector<edge> _edges;
    std::vector<std::vector<cv::Point2i>> re;
    for (const auto &contour: contours) {
        bool ok = false;
        for (int i = 0; i < contour.size(); i++) {
            int j = i + 1;
            if (j == contour.size()) {
                j = 0;
            }
//            cv::line(img, contour[i], contour[j], cv::Scalar(255, 0, 0), 5);
            cv::circle(img, contour[i], 2, cv::Scalar(255, 0, 0), -1);
            double len = getLength(contour[i], contour[j]);
            if (len < thresh) {
                continue;
            }
            cv::circle(img, contour[i], 1, cv::Scalar(0, 255, 0), -1);
            cv::circle(img, contour[j], 1, cv::Scalar(0, 255, 0), -1);
            _edges.emplace_back(contour[i], contour[j]);
            ok = true;
        }
        if (!ok) {
            re.push_back(contour);
        }
    }

    for (const auto &_e: _edges) {
        std::vector<int> starts, ends;
        for (int i = 0; i < nodes.size(); i++) {
            double length, l2s, l2e;
            length = _e.getLength(nodes[i]);
            l2s = _e.getLengthFromStart(nodes[i]);
            l2e = _e.getLengthFromEnd(nodes[i]);
            if (length < nodeRadius) {
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
                    if (length < nodeRadius * 0.1 && l2s > 0 && l2e < 0) {
                        ok = false;
                        break;
                    }
                }
                if (ok) {
                    cv::Mat em(edgeMaskR.size(), CV_8UC1, cv::Scalar(0));
                    cv::line(em, nodes[s] / 5, nodes[e] / 5, 255, 1);
                    int s1 = cv::countNonZero(em);
                    em &= edgeMaskR;
                    int s2 = cv::countNonZero(em);
                    if (s1 - s2 > 0) {
                        ok = false;
                    }
                }
                if (ok) {
                    for (const auto& edge: edges) {
                        if (edge.start == s && edge.end == e || edge.start == e && edge.end == s) {
                            ok = false;
                            break;
                        }
                    }
                }
                if (ok) {
                    edges.push_back({s, e});
                    std::cout << "[" << (nodes[s].x - 50) / 100 << ", " << (nodes[s].y - 50) / 100 << "] -> ["
                              << (nodes[e].x - 50) / 100 << ", " << (nodes[e].y - 50) / 100 << "]" << std::endl;
                    cv::line(img, nodes[s], nodes[e], lineColor, 2);
                }
            }
        }
    }
    return re;
}

void findEdges(const cv::Mat &img, const std::vector<cv::Point2i> &nodes, std::vector<edgeI> &edges, float nodeRadius) {
    cv::Mat edgesMask;
    cv::inRange(img, edgeColor[0], edgeColor[1], edgesMask);

    std::vector<std::vector<cv::Point2i>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(edgesMask, contours, hierarchy, cv::RETR_LIST, cv::CHAIN_APPROX_TC89_KCOS);
    cv::Mat edgeMaskR = edgesMask.clone();
    for (const auto& node: nodes) {
        cv::circle(edgeMaskR, node, (int)nodeRadius, 255, -1);
    }
    cv::resize(edgeMaskR, edgeMaskR, cv::Size(), 0.2, 0.2);

    auto re = findEdgesImpl(img, edgeMaskR, contours, nodeRadius, nodes, edges, nodeRadius * 0.5f, {0, 0, 0});

    cv::Mat em(edgesMask.size(), CV_8UC1, cv::Scalar(0));
    for (const auto& edge: edges) {
        cv::line(em, nodes[edge.start], nodes[edge.end], 255, (int)(nodeRadius * 0.8));
    }
    cv::Mat em2(edgesMask.size(), CV_8UC1, cv::Scalar(0));
    for (const auto& node: nodes) {
        cv::circle(em2, node, (int)nodeRadius, 255, -1);
    }
    em ^= edgesMask;
    em = em - em2 > 0;
    contours.clear();
    cv::imshow("em0", em);

    for (const auto& contour: re) {
        cv::Mat emc(em.size(), CV_8UC1, cv::Scalar(0));
        for (const auto& p: contour) {
            cv::circle(emc, p, 4, 255, -1);
        }
        emc &= em;
        if (cv::countNonZero(emc) > 5) {
            contours.push_back(contour);
        }
    }
    std::cout << "match2: " << std::endl;
    findEdgesImpl(img, edgeMaskR, contours, nodeRadius, nodes, edges, 3, {100, 100, 100});

    em = 0;
    for (const auto& edge: edges) {
        cv::line(em, nodes[edge.start], nodes[edge.end], 255, (int)(nodeRadius * 0.8));
    }
    for (const auto& node: nodes) {
        cv::circle(em2, node, (int)nodeRadius, 255, -1);
    }
    em ^= edgesMask;
    em = em - em2 > 0;

    cv::imshow("em", em);
}
