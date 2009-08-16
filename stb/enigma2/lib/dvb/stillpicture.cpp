#include <lib/base/ebase.h>
#include <lib/base/eerror.h>
#include <lib/dvb/stillpicture.h>

#include <linux/dvb/video.h>

#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>

#define VIDEO_STREAMTYPE_MPEG2 0

eStillPicture::eStillPicture()
{
	m_video_clip_fd = -1;
}

eStillPicture::~eStillPicture()
{
}

eStillPicture* eStillPicture::instance = NULL;

eStillPicture* eStillPicture::getInstance()
{
	if (instance == NULL)
		instance = new eStillPicture;
	return instance;
}

int eStillPicture::showSinglePic(const char *filename)
{
	{
		eDebug("showSinglePic %s", filename);
		int f = open(filename, O_RDONLY);
		if (f >= 0)
		{
			struct stat s;
			fstat(f, &s);

			//if (m_video_clip_fd >= 0) 
			//	finishShowSinglePic(); 

			if (m_video_clip_fd == -1) {
				m_video_clip_fd = open("/dev/dvb/adapter0/video0", O_WRONLY|O_NONBLOCK);

				int streamtype = VIDEO_STREAMTYPE_MPEG2;

				if (ioctl(m_video_clip_fd, VIDEO_SELECT_SOURCE, VIDEO_SOURCE_MEMORY) < 0)
					eDebug("VIDEO_SELECT_SOURCE MEMORY failed (%m)");
				if (ioctl(m_video_clip_fd, VIDEO_SET_STREAMTYPE, streamtype) < 0)
					eDebug("VIDEO_SET_STREAMTYPE failed(%m)");

			}
			if (m_video_clip_fd >= 0)
			{
				if (ioctl(m_video_clip_fd, VIDEO_STOP, 0) < 0)
					eDebug("VIDEO_STOP failed (%m)");
				if (ioctl(m_video_clip_fd, VIDEO_PLAY) < 0)
					eDebug("VIDEO_PLAY failed (%m)");
				if (ioctl(m_video_clip_fd, VIDEO_CONTINUE) < 0)
					eDebug("video: VIDEO_CONTINUE: %m");
				if (ioctl(m_video_clip_fd, VIDEO_CLEAR_BUFFER) < 0)
					eDebug("video: VIDEO_CLEAR_BUFFER: %m");

				bool seq_end_avail = false;
				size_t pos=0;
				unsigned char pes_header[] = { 0x00, 0x00, 0x01, 0xE0, 0x00, 0x00, 0x80, 0x00, 0x00 };
				unsigned char seq_end[] = { 0x00, 0x00, 0x01, 0xB7 };
				unsigned char iframe[s.st_size];
				unsigned char stuffing[8192];
				
				memset(stuffing, 0, 8192);
				read(f, iframe, s.st_size);
				
				while(pos <= (s.st_size-4) && !(seq_end_avail = (!iframe[pos] && !iframe[pos+1] && iframe[pos+2] == 1 && iframe[pos+3] == 0xB7)))
					++pos;
				if ((iframe[3] >> 4) != 0xE) // no pes header
					write(m_video_clip_fd, pes_header, sizeof(pes_header));
				else
					iframe[4] = iframe[5] = 0x00;
				write(m_video_clip_fd, iframe, s.st_size);
				if (!seq_end_avail)
					write(m_video_clip_fd, seq_end, sizeof(seq_end));
				write(m_video_clip_fd, stuffing, 8192);
			}
			close(f);
		}
		else
		{
			eDebug("couldnt open %s", filename);
			return -1;
		}
	}

	return 0;
}

void eStillPicture::finishShowSinglePic()
{
	if (m_video_clip_fd >= 0)
	{
		if (ioctl(m_video_clip_fd, VIDEO_STOP, 0) < 0)
			eDebug("VIDEO_STOP failed (%m)");
		if (ioctl(m_video_clip_fd, VIDEO_SELECT_SOURCE, VIDEO_SOURCE_DEMUX) < 0)
				eDebug("VIDEO_SELECT_SOURCE DEMUX failed (%m)");
		close(m_video_clip_fd);
		m_video_clip_fd = -1;
	}
}
