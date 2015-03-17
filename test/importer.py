#!/usr/bin/python

import os

class Main:

	def __init__(self):

		self.data = 'topolino'
		self.controller = None

	def run(self):

		module = __import__('imported')

		c = module.Controller(self)

		c.run()



if __name__ == '__main__':

	m = Main()
	print "data before run: ", m.data
	m.run()
	print "data after run: ", m.data

