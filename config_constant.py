#-*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')




#标签分类
tag_list = [
			u'热门', u'最新', u'经典', u'可播放', u'豆瓣高分', u'冷门佳片', 
			u'华语', u'欧美', u'韩国', u'日本', u'动作', u'喜剧', u'爱情',
			u'科幻', u'悬疑', u'恐怖', u'成长'
		]

#时光网演职员标签
staff_list = {
				'Director': u'导演 Director', 
				'Writer': u'编剧 Writer', 
				'Produced_by': u'制作人 Produced by', 
				'Cinematography': u'摄影 Cinematography', 
				'Film_Edinting': u'剪辑 Film Editing', 
				'Original_Music': u'原创音乐 Original Music', 
				'Visual_Effects_Supervisor': u'视觉特效 Visual Effects Supervisor',
				'Art_Direction_by': u'美术设计 Art Direction by', 
				'Assistant_Director': u'副导演/助理导演 Assistant Director', 
				'Sound_Department': u'声音部门 Sound Department', 
				'Makeup_Department': u'化妆造型 Makeup Department', 
				'Choreographer': u'动作指导 Choreographer', 
			}

#时光网制作or发行公司标签
company_list = {
	
				'made_company': u'制作公司',
				'sale_company': u'发行公司'
			}

#IMDB演职人员标签
IMDB_staff_list = {
					'director': 'Directed by', 
					'editor': 'Writing Credits', 
					'produced_by': 'Produced by', 
					'Cinematography': 'Cinematography by', 
					'film_editing': 'Film Editing by', 
					'music': 'Music by', 
					'Visual_Effects_Supervisor': 'Visual Effects by',
					'art_design': 'Art Direction by', 
					'Assistant_Director': 'Second Unit Director or Assistant Director', 
					'Sound_Department': 'Sound Department', 
					'Makeup_Department': 'Makeup Department', 
					'Choreographer': 'Stunts', 
					'cloth_design': 'Costume Design by',
				}


