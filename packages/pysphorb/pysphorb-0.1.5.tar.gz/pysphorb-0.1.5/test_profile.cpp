#include <opencv2/opencv.hpp>
#include <iostream>
#include "src/SPHORB.h"

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <image_path>" << std::endl;
        return 1;
    }

    // Load image
    cv::Mat img = cv::imread(argv[1]);
    if (img.empty()) {
        std::cerr << "Error: Could not load image " << argv[1] << std::endl;
        return 1;
    }

    std::cout << "Image loaded: " << img.cols << "x" << img.rows << std::endl;

    // Create SPHORB detector
    cv::SPHORB detector(500, 7, 20);

    // Detect and compute
    std::vector<cv::KeyPoint> keypoints;
    cv::Mat descriptors;

    std::cout << "Running SPHORB detectAndCompute..." << std::endl;
    detector(img, cv::Mat(), keypoints, descriptors);

    std::cout << "Found " << keypoints.size() << " keypoints" << std::endl;

    return 0;
}
