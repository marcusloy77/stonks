import config
import smtplib


def stockMail(subject, msg):
    
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
		
    server.login(config.EMAIL_ADDRESS, config.PASSWORD)
    message = 'Subject: {}\n\n{}'.format(subject, msg)
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, message)
    server.quit()
    print("Email Sent")


subject = "test"
msg = "tesssst"
stockMail(subject,msg)