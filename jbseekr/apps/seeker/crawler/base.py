from driver import Driver

class BaseCrawler(Driver):

	def __init__(self, source):
		self.driver = Driver()
		self.source = source
		super().__init__()
