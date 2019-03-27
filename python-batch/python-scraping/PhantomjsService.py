from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image
from UtilityProvider import UtilityProvider
# from fake_useragent import UserAgent
import platform
import time
import os
import socket

class PhantomjsService():
	__current_window_index = 0

	__result_of_page = []

	def __init__(self, refDate, needCreate = True):

		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
		}

		cap = webdriver.DesiredCapabilities.PHANTOMJS

		# for key, value in enumerate(headers):
		# 	capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
		# 	webdriver.DesiredCapabilities.PHANTOMJS[capability_key] = value

		cap['phantomjs.page.settings.userAgent'] = headers['User-Agent']

		workingDirectory = os.path.dirname(os.path.abspath(__file__))

		# options = webdriver.ChromeOptions()
		# options.add_argument("--headless")
		# options.add_argument("--allow-running-insecure-content")
		# options.add_argument("--javascript-harmony")
		# ua = UserAgent()
		# userAgent = ua.random
		# print(userAgent)
		# options.add_argument(f'user-agent={userAgent}')

		tempPort = 10000
		for i in range(0,100):
			checkPort = tempPort + i
			isAvailable = UtilityProvider.checkPortAvailable(checkPort)
			if isAvailable:
				tempPort = checkPort
				break

		if platform.system() == 'Linux':
			#os.chmod(workingDirectory + '/driver/phantomjs', 0o777)
			self.driver = webdriver.PhantomJS(executable_path= workingDirectory + "/driver/phantomjs", port=tempPort, desired_capabilities=cap,
											  service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
			# self.driver = webdriver.Chrome(executable_path=workingDirectory + "/driver/chromedriver", chrome_options=options)
		else:
			self.driver = webdriver.PhantomJS(executable_path= workingDirectory + "/driver/phantomjs.exe", desired_capabilities=cap,
											  service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
			# self.driver = webdriver.Chrome(executable_path=workingDirectory + "/driver/chromedriver.exe", chrome_options=options)

		self.driver.maximize_window()
		# self.driver.set_window_position(1600,900)
		self.driver.set_page_load_timeout(1)
		self.driver.implicitly_wait(0.2)

		if not os.path.exists(workingDirectory + '/data_image') and needCreate:
			os.mkdir(workingDirectory + '/data_image')
			os.chmod(workingDirectory + '/data_image', 0o777)

		year = refDate.year
		month = refDate.month
		day = refDate.day

		sYear = str(year)
		if month < 10:
			sMonth = str(month).rjust(2, '0')
		else:
			sMonth = str(month)
		if day < 10:
			sDay = str(day).rjust(2, '0')
		else:
			sDay = str(day)

		if not os.path.exists(workingDirectory + '/data_image/' + sYear + sMonth) and needCreate:
			os.mkdir(workingDirectory + '/data_image/' + sYear + sMonth)
			os.chmod(workingDirectory + '/data_image/' + sYear + sMonth, 0o777)

		self.imagePath = workingDirectory + '/data_image/' + sYear + sMonth + '/'

	def setTimeout(self,timeout):
		self.driver.set_page_load_timeout(timeout)

	def setURL(self,url):
		if url.startswith('http'):
			self.url = url
		else:
			self.url = 'http://' + url

	def setExtractionType(self, extract_type_id, tag =''):
		self.extract_type_id = extract_type_id
		if self.extract_type_id == 2:
			self.all_required_tag = self.driver.find_elements_by_tag_name(tag)
			# self.all_required_tag = self.driver.find_elements_by_tag_name('body')
		elif self.extract_type_id == 1:
			self.all_required_tag = ''

	def getAllRequiredTag(self):
		return self.all_required_tag;

	def getExtractionType(self):
		return self.extract_type_id

	def getCurrentWindowIndex(self):
		return self.__current_window_index

	def getCountWindows(self):
		return len(self.driver.window_handles)

	def getCurrentResultOfPage(self):
		return self.__result_of_page[self.__current_window_index]

	def getTitleOfPage(self):
		return self.driver.title

	def openNewTab(self):
		# element = WebDriverWait(self.driver, 10).until(
		# 	EC.presence_of_element_located((By.TAG_NAME, 'html'))
		# )
		self.driver.execute_script("window.open('','_blank')")

	def switchToTabIndex(self,index):
		if index >= len(self.driver.window_handles):
			pass
		else:
			self.driver.switch_to_window(self.driver.window_handles[index])
			self.__current_window_index = index
			self.driver.maximize_window()

	def scrap(self):
		print(self.url)
		try:
			self.driver.get(self.url)
			return True
		except:
			print('timeout triggered')
			return False

	def getField(self,cssSelector):
		print(cssSelector)
		if self.extract_type_id == 1:
			return self.__getFieldWithWebDriver(cssSelector)
		elif self.extract_type_id == 2:
			return self.__getFieldWithIndexOfTag(cssSelector)

	def searchDateOnPage(self, targetDate):
		print(targetDate)
		if self.extract_type_id == 2:
			innerBody = self.driver.find_elements_by_tag_name('body')
			for i in innerBody:
				tagInnerValue = i.text.strip()
				if targetDate in tagInnerValue:
					return targetDate
			innerBody = self.driver.find_elements_by_tag_name('input')
			for i in innerBody:
				tagInputValue = i.get_attribute('value')
				if targetDate in tagInputValue:
					return targetDate
			return None
		elif self.extract_type_id == 1:
			return None

	def __getFieldWithWebDriver(self, cssSelector):
		element_text = ''

		try:
			myDynamicElement = self.driver.find_element_by_css_selector(cssSelector)

			if myDynamicElement.tag_name == 'input':
				print('input tag detected')
				element_text = myDynamicElement.get_attribute('value')
			else:
				element_text = myDynamicElement.text

			print(element_text)
			return element_text
		except NoSuchElementException:
			print('cant find step 1 begin step 2')

		try:
			iframe_tag = self.driver.find_element_by_tag_name("iframe")
			self.driver.switch_to_frame(iframe_tag)
			myDynamicElement = self.driver.find_element_by_css_selector(cssSelector)
			element_text = myDynamicElement.text
			self.driver.switch_to_default_content()
			print(element_text)
			return element_text
		except NoSuchElementException:
			print('cant find step 2')
			return None

	def __getFieldWithIndexOfTag(self,cssSelector):
		if self.all_required_tag == '':
			print('error all required tag is empty')
			return None

		running_number = 0
		for i in self.all_required_tag:
			tagInnerValue = i.text.strip()
			if cssSelector[1] == 0:
				if cssSelector[0] in tagInnerValue:
					print(tagInnerValue)
					return tagInnerValue
			elif cssSelector[0] == tagInnerValue and cssSelector[1] != 0:
				if len(self.all_required_tag) <= running_number + cssSelector[1]:
					print('over the length')
					return None
				else:
					rateValue = self.all_required_tag[running_number + cssSelector[1]].text.strip()
					print(rateValue)
					return rateValue
			running_number = running_number + 1

		print('cant find')
		return None

	def getScreenShot(self,fileName):

		if 'www.bot.or.th' in self.url:
			return self.__getScreenShotScrollBar(fileName)
		else:
			return self.__getScreenShotFullPage(fileName)

	def __getScreenShotFullPage(self, fileName):
		self.driver.execute_script("""(function() {
		    var style = document.createElement('style'), text = document.createTextNode('body { background: #fff }');
		    style.setAttribute('type', 'text/css');
		    style.appendChild(text);
		    document.head.insertBefore(style, document.head.firstChild);
		})();""")
		pathFile = self.imagePath + fileName
		pathFileWithExt = self.imagePath + fileName + '.png'
		self.driver.save_screenshot(pathFileWithExt)
		return pathFileWithExt

	def __getScreenShotScrollBar(self, fileName):

		self.driver.execute_script("""(function() {
				    var style = document.createElement('style'), text = document.createTextNode('body { background: #fff }');
				    style.setAttribute('type', 'text/css');
				    style.appendChild(text);
				    document.head.insertBefore(style, document.head.firstChild);
				})();""")

		pathFile = self.imagePath + fileName
		pathFileWithExt = self.imagePath + fileName + '.png'
		num_img = 0
		is_have_reminder = True

		page_width = self.driver.execute_script(
			"return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
		page_height = self.driver.execute_script(
			"return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
		browser_width = self.driver.execute_script(
			"return Math.max(document.documentElement.clientWidth, window.innerWidth);")
		browser_height = self.driver.execute_script(
			"return Math.max(document.documentElement.clientHeight, window.innerHeight);")

		page_height = self.driver.execute_script(
			"return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight, document.getElementById('s4-bodyContainer').scrollHeight);")

		print(str(page_height) + ', ' + str(browser_height))

		objectScroll = None

		objectScroll = 'document.getElementById("s4-workspace")'

		all_div_tag = self.driver.find_elements_by_tag_name('div')
		for item in all_div_tag:
			overflowy = item.value_of_css_property("overflow-y")
			sizey = item.size['height']

			if sizey > page_height:
				pass
				# page_height = int(sizey)

			if overflowy != 'visible' and overflowy != 'hidden' and sizey > 0:
				# bypass for now
				pass
			# objectScroll = item
			# print("object Scroll ID : " + item.get_attribute('id'))

		# print(str(page_width) + " " + str(page_height) + " " + str(browser_width) + " " + str(browser_height))

		temp_maxWidth = max([browser_width, page_width])
		temp_maxHeight = max([browser_height, page_height])
		reminder_height = temp_maxHeight % browser_height

		# we have consindered that no reminder screen
		if reminder_height <= 100:
			temp_maxHeight = temp_maxHeight - reminder_height
			is_have_reminder = False

		current_postion_y = 0
		while current_postion_y <= temp_maxHeight - browser_height:
			self.driver.save_screenshot(pathFile + str(num_img) + ".png")
			num_img = num_img + 1

			if current_postion_y == temp_maxHeight - browser_height:
				break;
			else:
				current_postion_y = current_postion_y + browser_height

			if objectScroll == None:
				if current_postion_y > temp_maxHeight - browser_height:
					current_postion_y = temp_maxHeight - browser_height
					self.driver.execute_script("window.scrollTo({0}, {1})".format(0, temp_maxHeight - browser_height))
				else:
					self.driver.execute_script("window.scrollTo({0}, {1})".format(0, current_postion_y))
			else:
				if current_postion_y > temp_maxHeight - browser_height:
					current_postion_y = temp_maxHeight - browser_height
					# self.driver.execute_script("arguments[0].scrollTop = {0}".format(temp_maxHeight - browser_height),
					# 						   objectScroll)
					tempVar = self.driver.execute_script("var targetX={0}; var targetY={1}; var targetEle=document.getElementById('s4-workspace'); targetEle.scrollTop=targetY; return targetY;".format(0, temp_maxHeight - browser_height))
				else:
					# self.driver.execute_script("arguments[0].scrollTop = {0}".format(current_postion_y), objectScroll)
					tempVar = self.driver.execute_script("var targetX={0}; var targetY={1}; var targetEle=document.getElementById('s4-workspace'); targetEle.scrollTop=targetY; return targetY;".format(0, current_postion_y))

			time.sleep(0.5)

		for i in range(0, num_img):
			im = Image.open(pathFile + str(i) + '.png')
			im.thumbnail((temp_maxWidth, browser_height), Image.ANTIALIAS)
			im.save(pathFile + str(i) + '.png')
			im.close()

		image_list = []
		image_width_list = []
		image_height_list = []

		for i in range(0, num_img):
			im = Image.open(pathFile + str(i) + '.png')
			image_list.append(im)
			image_width_list.append(im.size[0])
			if i == num_img - 1 and is_have_reminder:
				image_height_list.append(reminder_height)
			else:
				image_height_list.append(im.size[1])
			im.close()

		if os.path.exists(pathFileWithExt):
			os.remove(pathFileWithExt)

		# append image if scroll bar has been scrolled
		if (num_img > 1):
			result_image = Image.new('RGB', (max(image_width_list), sum(image_height_list)))
			y_offset = 0
			for i in range(0, num_img):
				if i == num_img - 1 and is_have_reminder:
					im = Image.open(pathFile + str(i) + ".png")
					im2 = im.crop((0, im.size[1] - reminder_height, im.size[0], im.size[1]))
					# im2.save(pathFile + str(i) + "_crop.png")
					result_image.paste(im2, (0, y_offset))
					y_offset = y_offset + im.size[1]
					im.close()
					im2.close()
				else:
					im = Image.open(pathFile + str(i) + ".png")
					result_image.paste(im, (0, y_offset))
					y_offset = y_offset + im.size[1]
					im.close()
			result_image.save(pathFileWithExt)
			result_image.close()
		else:
			result_image = Image.open(pathFile + "0.png")
			result_image.save(pathFileWithExt)
			result_image.close()

		for i in range(0, num_img):
			if os.path.exists(pathFile + str(i) + '.png'):
				os.remove(pathFile + str(i) + '.png')

		return pathFileWithExt

	def getPageSource(self):
		return self.driver.page_source

	def close(self):
		self.driver.close()

	def quit(self):
		self.driver.quit()


