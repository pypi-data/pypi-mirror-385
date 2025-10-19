/*
	AUTHOR:
	Qiang Zhao, email: qiangzhao@tju.edu.cn
	Copyright (C) 2014 Tianjin University
	School of Computer Software
	School of Computer Science and Technology

	LICENSE:
	SPHORB is distributed under the GNU General Public License.  For information on 
	commercial licensing, please contact the authors at the contact address below.

	REFERENCE:
	Qiang Zhao, Wei Feng, Liang Wan and Jiawan Zhang. SPHORB: A Fast and Robust Binary 
	Feature on the Sphere. International Journal of Computer Vision, preprint, 2014.
*/

#ifndef _SPHORB_H
#define _SPHORB_H

#include <opencv2/opencv.hpp>		
#include <vector>
using namespace cv;
using namespace std;

namespace cv
{
	class CV_EXPORTS SPHORB : public cv::Feature2D
	{
	public:
		enum { kBytes = 32, SFAST_EDGE = 3, SPHORB_EDGE = 15};
	
		explicit SPHORB(int nfeatures = 500, int nlevels = 7, int b=20);
		~SPHORB();
	
		// returns the descriptor size in bytes
		int descriptorSize() const;
		// returns the descriptor type
		int descriptorType() const;
	
		// Compute the ORB features and descriptors on an image
		void operator()(InputArray image, InputArray mask, vector<KeyPoint>& keypoints) const;
		void operator()( InputArray image, InputArray mask, vector<KeyPoint>& keypoints,
						 OutputArray descriptors, bool useProvidedKeypoints=false ) const;
	
	protected:
		int barrier;
		int nfeatures;
		int nlevels;

		// Instance-specific data (previously global)
		std::vector<float*> geoinfos;
		std::vector<Mat> maskes;
		std::vector<std::vector<float*>> imgInfos;
		int levels;

		void initSORB();
		void uninitSORB();

		void computeImpl( const Mat& image, vector<KeyPoint>& keypoints, Mat& descriptors ) const;
		void detectImpl( const Mat& image, vector<KeyPoint>& keypoints, const Mat& mask=Mat() ) const;	};

}

#endif