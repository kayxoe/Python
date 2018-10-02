#!/usr/bin/python
# -*- coding:utf-8 -*-

import urllib,requests,json,os
from xlwt import *

#去除重复数据
def getDictinctData(data):
	distinctdata=[]

	for dt in (data):
		if dt not in distinctdata:
			distinctdata.append(dt)

	return distinctdata

#获取全部城市
def getAllCity(cities):
	ak='2CKBZ-4S7WW-56RR3-OQJZU-UNKU6-SSFHW'
	url='https://apis.map.qq.com/ws/district/v1/list?key='+ak
	req=requests.get(url)
	content=req.content
	data=json.loads(content)
	#将城市列表存入list
	#返回的result信息中有三个元素，第一个为省份，第二个为市级，第三个为区县
	for i in range(len(data['result'][1])):
		cities.append(data['result'][1][i]['name'])

#过滤电话：筛选规则为11位数字且不含'-'字符
def getPhoneNumber(tel):
	phonenumber=''
	#切分电话字符串，逐个判断电话还是手机
	for i in range(len(tel.split(';'))):
		if (len(tel.split(';')[i])==11):
			if not ('-' in tel.split(';')[i]):
				phonenumber=phonenumber+tel.split(';')[i]+'\n'

	return phonenumber.strip()#去除尾行换行符

#数据写入Excel
def writeData2Excel(filename,tbname,data):
	#将Excel文件生成至当前文件同级的result目录下
	if not os.path.exists(os.getcwd()+'/result'):
		os.mkdir(os.getcwd()+'/result')

	#生成Excel文件
	file=Workbook(encoding = 'utf-8')
	tb=file.add_sheet(tbname)

	#设置自动换行
	style=easyxf('align:wrap on')

	#写入首行标题
	tb.write(0,0,'序号')
	tb.write(0,1,'地点')
	tb.write(0,2,'具体地址')
	tb.write(0,3,'联系电话')
	tb.write(0,4,'省份')
	tb.write(0,5,'城市')
	tb.write(0,6,'区县')

	#将数据写入对应列
	for i in range(len(data)):
		tb.write(i+1,0,i+1)
		tb.write(i+1,1,data[i][0],style)
		tb.write(i+1,2,data[i][1],style)
		tb.write(i+1,3,data[i][2],style)
		tb.write(i+1,4,data[i][3],style)
		tb.write(i+1,5,data[i][4],style)
		tb.write(i+1,6,data[i][5],style)
		print(i)

	#设置相应列宽
	tb.col(0).width=2000
	tb.col(1).width=5000
	tb.col(2).width=20000
	tb.col(3).width=5000
	tb.col(4).width=5000
	tb.col(5).width=5000
	tb.col(6).width=5000

	#输出Excel文件
	file.save(os.getcwd()+'/result/'+filename+'.xls')

#获取全国含关键词的地址及电话
ak='2CKBZ-4S7WW-56RR3-OQJZU-UNKU6-SSFHW'
methods=['search']#使用位置搜索
keywords=['酒店']#搜索关键词列表
filters=['tel<>null']#过滤掉没有电话的结果
page_size='20'#搜索结果每页数量
regions=[]#搜索范围
querydata=[]#查询结果

page_count=20
page_index='1'#默认展示搜索结果页

#获取全国城市列表
getAllCity(regions)

#遍历关键词及城市
for i in range(len(keywords)):
	for j in range(len(regions)):
		url='https://apis.map.qq.com/ws/place/v1/'+methods[0]+'?boundary=region('+regions[j]+')&keyword='+keywords[i]+'&filter='+filters[0]+'&page_size='+page_size+'&page_index='+str(page_index)+'&key='+ak
		req=requests.get(url)
		content=req.content
		data=json.loads(content)

		#将首页查询结果存入
		if ('data' in data):
			for k in range(len(data['data'])):
				if(getPhoneNumber(data['data'][k]['tel'])!=''):
					querydata.append([data['data'][k]['title'],\
						data['data'][k]['address'],\
						getPhoneNumber(data['data'][k]['tel']),\
						data['data'][k]['ad_info']['province'],\
						data['data'][k]['ad_info']['city'],\
						data['data'][k]['ad_info']['district']])

		#遍历全部页面结果存入
		if ('count' in data):
			page_count=int(int(data['count'])/20)
			for x in range(2,page_count):
				url='https://apis.map.qq.com/ws/place/v1/'+methods[0]+'?boundary=region('+regions[j]+')&keyword='+keywords[i]+'&filter='+filters[0]+'&page_size='+page_size+'&page_index='+str(x)+'&key='+ak
				req=requests.get(url)
				content=req.content
				data=json.loads(content)
				if ('data' in data):
					for m in range(len(data['data'])):
						if(getPhoneNumber(data['data'][m]['tel'])!=''):
							querydata.append([data['data'][m]['title'],\
								data['data'][m]['address'],\
								getPhoneNumber(data['data'][m]['tel']),\
								data['data'][m]['ad_info']['province'],\
								data['data'][m]['ad_info']['city'],\
								data['data'][m]['ad_info']['district']])

	#将结果写入Excel表中
	writeData2Excel(keywords[i],'data',getDictinctData(querydata))
	print("Serach finished .")