import urllib,requests,json,sqlite3,numpy,random
import matplotlib.pyplot as plt

# 获取指定地址的位置信息
def getLocations(keyword,region):
	ak='百度地图AK'
	url='http://api.map.baidu.com/place/v2/search?query='+keyword+'&region='+region+'&output=json&ak='+ak
	req=requests.get(url)
	content=req.content
	data=json.loads(content)

	return data['results']

# 创建数据库
conn=sqlite3.connect('result.db')
c=conn.cursor()
c.execute('''CREATE TABLE VILLAGE_TABLE(VILLAGE_NAME VARCHAR2(100),VILLAGE_ADDRESS VARCHAR2(200),\
ORGIN_PLACE VARCHAR2(100),RADIUS NUMBER(10),\
MIN_COSTTIME NUMBER(5),TRANS_SOLUTIONS VARCHAR2(2000));''')

ak='百度地图AK'
keyword='亚信科技'
region='南京'
query='房地产'
locations=[{'name':'亚信科技楼','location':'32.078131,118.760923'},\
	{'name':'亚信科技有限公司','location':'32.05056,118.769021'}]
radius='5000'

# locateinfo=getLocations(keyword,region)

# 亚信科技楼	32.078131,118.760923
# 亚信科技有限公司	32.05056,118.769021

# 生成公交方案
for location in locations:
	url='http://api.map.baidu.com/place/v2/search?&query='+query+'&location='+location['location']+'&radius='+radius+'&output=json&ak='+ak
	req=requests.get(url)
	content=req.content
	data=json.loads(content)

	# 获取周边指定范围小区信息
	for i in range(len(data['results'])):
		print('\n出发位置：'+data['results'][i]['name'])
		destin=str(data['results'][i]['location']['lat'])+','+str(data['results'][i]['location']['lng'])

		for village in locations:
			print('目标位置：'+village['name'])
			# 生成公交方案
			url_route='http://api.map.baidu.com/direction/v2/transit?origin='+village['location']+'&destination='+destin+'&ak='+ak
			req_route=requests.get(url_route)
			content_route=req_route.content
			data_route=json.loads(content_route)

			cost_time_solutions=[]

			for k in range(len(data_route['result']['routes'])):

				route_solution=''

				cost_time_solution=0

				for l in range(len(data_route['result']['routes'][k]['steps'])):

					route_solution+='	第'+str(l+1)+'步：'
					cost_time_steps=[]

					if len(data_route['result']['routes'][k]['steps'][l]) == 1:
						cost_time_steps.append(data_route['result']['routes'][k]['steps'][l][0]['duration'])
						route_solution += data_route['result']['routes'][k]['steps'][l][0]['instructions']+ \
							  ',耗时：' + str(data_route['result']['routes'][k]['steps'][l][0]['duration']) + 's\n'
					else:
						for m in range(len(data_route['result']['routes'][k]['steps'][l])):
							cost_time_steps.append(data_route['result']['routes'][k]['steps'][l][m]['duration'])
							route_solution +='	('+str(m+1)+')'+data_route['result']['routes'][k]['steps'][l][m]['vehicle_info']['detail']['on_station']\
								  +'-'+data_route['result']['routes'][k]['steps'][l][m]['vehicle_info']['detail']['name']\
								  +'>'+data_route['result']['routes'][k]['steps'][l][m]['vehicle_info']['detail']['off_station'] \
								  + ',耗时：' + str(data_route['result']['routes'][k]['steps'][l][m]['duration']) + 's\n'
					cost_time_solution+=min(cost_time_steps)
				c.execute('''INSERT INTO VILLAGE_TABLE VALUES(?,?,?,?,?,?);''', \
						  (data['results'][i]['name'],data['results'][i]['address'], \
						  village['name'],radius, \
						   round(cost_time_solution / 60, 2),route_solution))
				c.execute('''COMMIT;''')
				print('方案'+str(k+1)+':最短用时-'+str(round(cost_time_solution/60,2))+'分钟')
				print(route_solution)
c.close()
