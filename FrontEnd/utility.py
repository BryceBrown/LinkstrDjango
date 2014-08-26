from FrontEnd.models import *
from email.mime.text import MIMEText
import random, string, smtplib
from FrontEnd import constants

POSSIBLE_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
URL_LENGTH=6

def getUniqueRedirectKeyForDomain(domainId):
	urlKey = ""
	for i in range(URL_LENGTH):
		urlKey += random.choice(POSSIBLE_CHARS)
	if RedirectLink.objects.filter(Domain__id=domainId, UrlKey=urlKey).count() > 0:
		return getUniqueRedirectKeyForDomain(domainId)
	return urlKey

def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)


def sendEmail(toEmail, message, subject):
	try:
		from google.appengine.api import mail
		mail.send_mail("signup@golinkstr.com", toEmail, subject, message)
	except Exception, e:
		print(e)
		return

def string_generator(size=10):
	chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
	return ''.join(random.choice(chars) for x in range(size))

def sendUserInviteEmail(email, company):
	import thread
	#TODO Get email template
	emailMessage = "You have been invited to be a Linkstr user under the company {1} <br /> <a href='http://www.golinkstr.com/Signup?company={0}'>Activate</a>"
	thread.start_new_thread(sendEmail, (email, emailMessage.replace('{1}', company.Name).replace('{0}', str(company.id)), "Activation Link"))


def sendSignupEmail(email, authentication_code):
	import thread
	#TODO replace with 
	#handle = open(constants.SIGNUP_EMAIL_PATH)
	#emailMessage = handle.read()
	emailMessage = "Welcome to Linkstr! Click the link below to complete signup <br /> <a href='http://www.golinkstr.com/Activate?auth={0}'>Activate</a>"
	thread.start_new_thread(sendEmail, (email, emailMessage.replace('{0}', authentication_code), "Activation Link"))

def getSafeDomainNameForCompany(companyName):
	#TODO Refactor, this is super fucking ghetto
	safeValue = companyName.replace(' ', '_').replace('-', '_').replace("'", '').replace("!", "").lower()
	return safeValue + ".goli.us"