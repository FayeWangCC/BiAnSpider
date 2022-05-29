import time
import os
from lxml import etree
import requests
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.common.by import By


class GetBianImage(object):

	# 初始化
	def __init__(self, url):
		# 起始URL
		self.url = url
		# 请求头参数
		self.opt = webdriver.ChromeOptions()
		self.opt.add_argument('--headless')
		self.opt.add_argument('User_Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0')
		# 创建浏览器对象
		self.driver = webdriver.Chrome(options=self.opt)
		# requests请求参数
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
		}
		self.proxies = {
			'http': 'http://124.193.110.231:80'
		}

	# 获取图片名称及页面url
	def parser_data(self):
		li_list = self.driver.find_elements(by=By.XPATH, value='//div[@class="list"]/ul/li')
		self.image_list = []
		for li in li_list:
			temp = {}
			# 页面中插入的4k图片li标签内结构不同,使用异常处理过滤
			try:
				# 获取图片页面url\标题
				url = li.find_element(by=By.XPATH, value='./a').get_attribute('href')
				title = str(li.find_element(by=By.XPATH, value='./a').get_attribute('title'))
				# 通过url中是否包含index来判断该链接是否是下一页链接
				if 'index' in url:
					continue
				else:
					temp['image_url'] = url
					temp['image_name'] = title.split('更新时间')[0].replace(' ', '')
					self.image_list.append(temp)
			except:
				# 4k图片,页面结构不同,直接跳过
				continue

	# 打开图片页面获取图片的真实地址
	def get_real_image(self):
		self.real_image_list = []
		for image in self.image_list:
			temp = {}
			temp['image_name'] = image['image_name']
			image_url = image['image_url']
			try:
				# 使用requests获取图片页面内容
				response = requests.get(image_url, headers=self.headers, proxies=self.proxies, timeout=5)
				session = requests.Session()
				session.mount('http://', HTTPAdapter(pool_connections=5))
				# 解析HTML
				dom = etree.HTML(response.text)
				# 使用xpath获取图片真实地址
				temp['real_url'] = dom.xpath('//div[@class="pic"]/p/a/img/@src')[0]
				self.real_image_list.append(temp)
			except requests.exceptions.ConnectTimeout as connecttimeout:
				print('------\t\t------------------------')
				print(f'发生异常\t\t{connecttimeout}')
				print(f'URL地址\t\t{image_url}')
				print('------\t\t------------------------')
				continue
			except requests.exceptions.ConnectionError as connectionerror:
				print('------\t\t------------------------')
				print(f'发生异常\t\t{connectionerror}')
				print(f'URL地址\t\t{image_url}')
				print('------\t\t------------------------')
				continue
			except requests.exceptions.ReadTimeout as readtimeout:
				print('------\t\t------------------------')
				print(f'发生异常\t\t{readtimeout}')
				print(f'URL地址\t\t{image_url}')
				print('------\t\t------------------------')
				continue
			except IndexError:
				print('------\t\t------------------------')
				print(f'发生异常\t\t{IndexError}')
				print(f'URL地址\t\t{image_url}')
				print('------\t\t------------------------')
				continue
			except requests.exceptions.ChunkedEncodingError as chunkedEncodingError:
				print('------\t\t------------------------')
				print(f'发生异常\t\t{chunkedEncodingError}')
				print(f'URL地址\t\t{image_url}')
				print('------\t\t------------------------')
				continue

	# 使用requests打开图片真实路径并保存图片到本地
	def save_image(self):
		for image in self.real_image_list:
			image_name = image['image_name']
			real_url = image['real_url']
			# 拼接图片保存路径
			save_path = './meinv/' + str(image_name) + str(real_url)[-4:]
			if not os.path.exists(save_path):
				os.mkdir(save_path)
				try:
					# 使用requests获取图片并保存
					response = requests.get(real_url, headers=self.headers, proxies=self.proxies, timeout=5)
					session = requests.Session()
					# 设置该host下的最大链接数
					session.mount('http://', HTTPAdapter(pool_connections=5))
					with open(save_path, 'wb') as f:
						f.write(response.content)
					print(f'正在保存\t\t{image_name}')
				except requests.exceptions.ConnectTimeout as connecttimeout:
					print('------\t\t------------------------')
					print(f'发生异常\t\t{connecttimeout}')
					print(f'URL地址\t\t{real_url}')
					print('------\t\t------------------------')
					continue
				except requests.exceptions.ConnectionError as connectionerror:
					print('------\t\t------------------------')
					print(f'发生异常\t\t{connectionerror}')
					print(f'URL地址\t\t{real_url}')
					print('------\t\t------------------------')
					continue
				except requests.exceptions.ReadTimeout as readtimeout:
					print('------\t\t------------------------')
					print(f'发生异常\t\t{readtimeout}')
					print(f'URL地址\t\t{real_url}')
					print('------\t\t------------------------')
					continue
				except IndexError:
					print('------\t\t------------------------')
					print(f'发生异常\t\t{IndexError}')
					print(f'URL地址\t\t{real_url}')
					print('------\t\t------------------------')
					continue
				except requests.exceptions.ChunkedEncodingError as chunkedEncodingError:
					print('------\t\t------------------------')
					print(f'发生异常\t\t{chunkedEncodingError}')
					print(f'URL地址\t\t{real_url}')
					print('------\t\t------------------------')
					continue

	def run(self):
		# 1.网页URL
		self.driver.get(self.url)
		time.sleep(5)
		while True:
			# 3.解析响应内容得到图片信息
			self.parser_data()
			# 4.获取图片页面响应,并解析获取真实地址
			self.get_real_image()
			# 5.使用requests获取图片并保存图片到本地文件夹
			self.save_image()
			try:
				# 6.获取下一页元素
				next_el = self.driver.find_element(by=By.XPATH, value="//a[contains(text(),'下一页')]")
				next_el.click()
				print(f'正在保存\t\t{self.driver.current_url}页面的内容')
			except:
				print('----------------图片抓取完成----------------')
				break


if __name__ == '__main__':
	get_image = GetBianImage('http://www.netbian.com/meinv/index.htm')
	get_image.run()
