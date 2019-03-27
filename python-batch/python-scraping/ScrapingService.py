import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from PIL import Image
import os

class ScrapingService():

	urlFF = []
	urlPJS = []
	extract_type_id_FF = []
	extract_type_id_PJS = []

	def __init__(self):
		self.driverPJS = webdriver.PhantomJS()
		self.driverFF = webdriver.Firefox()
		self.driverPJS.maximize_window()
		self.driverPJS.set_page_load_timeout(60)
		self.driverPJS.implicitly_wait(0.5)
		self.driverFF.maximize_window()
		self.driverFF.set_page_load_timeout(60)
		self.driverFF.implicitly_wait(0.5)

	def setURL(self,url):
		self.url = url

	def setExtractType(self,extract_type_id):
		self.extraxt_type_id = extract_type_id

	def setScreenShotType(self,screen_shot_type_id):
		self.screen_shot_type_id = screen_shot_type_id
		if self.screen_shot_type_id == 1:
			self.driver = self.driverPJS
		elif self.screen_shot_type_id == 2:
			self.driver = self.driverFF

	def openNewTab(self):
		self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')

	def switchToTabIndex(self,index):
		self.driver.switch_to_window(self.driver.window_handles[index])

	def scrap(self,tag = ''):
		print(self.url)
		try:
			self.driver.get(self.url)

			# time.sleep(10)

			if(self.extraxt_type_id == 2):
				self.all_required_tag = self.driver.find_elements_by_tag_name(tag)
				# run = 0
				# for i in self.all_required_tag:
				# 	print(str(run) + ' : ' + i.text)
				# 	run = run+1
			return True
		except:
			print('timeout triggered')
			return False

	def getField(self,cssSelector):
		print(cssSelector)
		if self.extraxt_type_id == 1:
			return self.__getFieldWithWebDriver(cssSelector)
		elif self.extraxt_type_id == 2:
			return self.__getFieldWithIndexOfTag(int(cssSelector))

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
			return 'None'

	def __getFieldWithIndexOfTag(self,cssSelector):
		all_td_text = []
		running_number = 0
		for i in self.all_required_tag:
			# print(i.text)
			if cssSelector == running_number:
				print(i.text)
				return i.text
			running_number = running_number + 1

		print('cant find')
		return 'None'

	def getScreenShot(self,fileName):
		if self.screen_shot_type_id == 1:
			return self.__getScreenShotFullPage(fileName)
		elif self.screen_shot_type_id == 2:
			return self.__getScreenShotScrollBar(fileName)

	def __getScreenShotFullPage(self, fileName):
		self.driver.execute_script("""(function() {
		    var style = document.createElement('style'), text = document.createTextNode('body { background: #fff }');
		    style.setAttribute('type', 'text/css');
		    style.appendChild(text);
		    document.head.insertBefore(style, document.head.firstChild);
		})();""")
		pathFile = 'tmp\\' + fileName + '.png'
		self.driver.save_screenshot(pathFile)
		return pathFile

	def __getScreenShotScrollBar(self, fileName):
		pathFile = 'tmp\\' + fileName
		pathFileWithExt = 'tmp\\' + fileName + '.png'
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

			if current_postion_y > temp_maxHeight - browser_height:
				current_postion_y = temp_maxHeight - browser_height
				self.driver.execute_script("window.scrollTo({0}, {1})".format(0, temp_maxHeight - browser_height))
			else:
				self.driver.execute_script("window.scrollTo({0}, {1})".format(0, current_postion_y))

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

	# def closeCurrentTab(self):
	# 	self.driver.close()

	def quit(self):
		self.driverFF.quit()
		self.driverPJS.quit()
		self.driver.quit()


