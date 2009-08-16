#ifndef STILLPICTURE_H_
#define STILLPICTURE_H_

class eStillPicture
{
protected:
	static eStillPicture *instance;
	int m_video_clip_fd;
#ifdef SWIG
	eStillPicture();
	~eStillPicture();
#endif
public:
#ifndef SWIG
	eStillPicture();
	~eStillPicture();
#endif
	static eStillPicture* getInstance();

	int showSinglePic(const char *filename);
	void finishShowSinglePic();
};


#endif
