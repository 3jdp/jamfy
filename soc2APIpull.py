#!/usr/local/bin/python3

# soc2APIpull.py -
#
# github.com/3jdp, 28 March, 2018
#
# A script to automatically create CSV files containing
# which computers are non-compliant for FileVault, Sophos install, or haven't
# checked in in 21 days.

# This needs some further work


import re, os, datetime
import xml.etree.ElementTree as ET

JSSAPIuser = 
JSSpass = 
JSSUrl = 

# Number of records to pull
records = 100

formattedDate = datetime.datetime.today().strftime('%Y%m%d')

def createCSVs(formattedDate):
	# Create 3 CSV files with the current date prepended

	filenames = ['noFileVault','greaterThan21Days','noSophos']
	for fn in filenames:
		file_name = formattedDate + '-' + fn + '.csv'
		f = open(file_name, 'w')
		f.close()

def pullURL(JSSAPIuser,JSSpass,JSSUrl,loopz):
	return os.popen('curl -k -u %s:%s %s/JSSResource/computers/id/{%d}' % (JSSAPIuser,JSSpass,JSSUrl,loopz)).read()

def getComputerNameSN(root):
	# Grabs the current computer name to write to a CSV if needed.

	computerName = root[0][1].text
	serialNumber = root[0][6].text
	return computerName, serialNumber

def getFileVault(computerName,serialNumber,root):

	# Checks for "!= FILEVAULT" Smart Group membership, writes to the CSV if so.

	for i in range(0,100):
		try:
			service = root[8][0][i].text
		except IndexError:
			break
		p = re.compile(r'!= FILEVAULT',re.IGNORECASE)
		m = p.match(service)
		if m:
			f = open(formattedDate + '-noFilevault.csv', 'a')
			f.write('%s , %s\n' % (computerName, serialNumber))
			f.close()
			return
		else:
			i += 1

def get21DayCheckIn(computerName,serialNumber,root):

	# Checks for "> 21 days since last Check-in" Smart Group membership,
	# writes to the CSV if so.


	for i in range(0,100):
		try:
			service = root[8][0][i].text
		except IndexError:
			break
		checkInTime = root[0][19].text
		p = re.compile(r'greater than 21 days since last Check-in',re.IGNORECASE)
		m = p.match(service)
		if m:
			f = open(formattedDate + '-greaterThan21Days.csv', 'a')
			f.write('%s , %s, %s\n' % (computerName, serialNumber,str(checkInTime)))
			f.close()
			return
		else:
			i += 1

def getSophos(computerName,serialNumber,root):

	# Checks for "No Sophos" Smart Group membership, writes to the CSV if so.

	for i in range(0,100):
		try:
			service = root[8][0][i].text
		except IndexError:
			break
		p = re.compile(r'No Sophos',re.IGNORECASE)
		m = p.match(service)
		if m:
			f = open(formattedDate + '-noSophos.csv', 'a')
			f.write('%s , %s\n' % (computerName, serialNumber))
			f.close()
			return
		else:
			i += 1


def getRecord(JSSAPIuser, JSSpass, JSSUrl, loopz):

	# Pulls in computer record from JSS API and verifies that it's a computer
	# record and not a deleted record or beyond the index for current records.

	rawURL = pullURL(JSSAPIuser, JSSpass, JSSUrl, loopz)
	p = re.compile(r'^<html>',re.IGNORECASE)
	m = p.match(rawURL)
	if m:
		return
	else:
		root = ET.fromstring(rawURL)
		computerName,serialNumber = getComputerNameSN(root)
		getFileVault(computerName,serialNumber,root)
		get21DayCheckIn(computerName,serialNumber,root)
		getSophos(computerName,serialNumber,root)

createCSVs(formattedDate)

for loopz in range(1,records):

	getRecord(JSSAPIuser, JSSpass, JSSUrl, loopz)
	loopz += 1

print('done!!')
