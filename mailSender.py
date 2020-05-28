import email, smtplib, ssl, os

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Trusted extension type
EXTENSIONS = ['pdf']

# Environment Variables created trough Google Cloud Function
MAIL = os.environ.get("MAIL")
PASSWORD = os.environ.get("PASSWORD") 
SMTPSERVER = os.environ.get("SMTPSERVER") 

# Main function
def main_func(request):
	# Checking if the file can be trusted
	trustedFile = get_secure_file(request.files['file'])
	if trustedFile == None:
		return {
			"body": "Há algo de errado no arquivo que você está tentando enviar"
		}, 404

	# Getting other kinds of information from the request
	name = request.form['name'] 
	area = request.form['area']
	message = request.form['message']

	# Sending mail through send_mail function
	response = send_mail(name, area, message, trustedFile)

	# JSON response
	if response == 0:
		return {
			"body": "Seu currículo foi enviado com sucesso"
		}, 200
	else: 
		return {
			"body": "Houve um problema ao enviar seu currículo. Tente novamente mais tarde"
		}, 503

# Effectively sends the e-mail and returns the status
def send_mail(name, area, message, trustedFile):

	# Body and subject layout
	subject = "Novo currículo de: {}, Área: {}".format(name, area)
	body = "Mensagem automatizada.\n\nTexto enviado por: {}\n\n{}".format(name, message)

	# Create a multipart message and set headers
	message = MIMEMultipart()
	message["From"] = MAIL
	message["To"] = MAIL
	message["Subject"] = subject

	# Add body to email
	message.attach(MIMEText(body, "plain"))

	# New filename. The join and split take care of any whitespace
	filename = "curriculum{}.pdf".format("".join(name.split())) 

	# Open PDF file in binary mode
	# Add file as application/octet-stream
	# Email client can usually download this automatically as attachment
	part = MIMEBase("application", "octet-stream")
	part.set_payload(trustedFile.read())

	# Encode file in ASCII characters to send by email    
	encoders.encode_base64(part)

	# Add header as key/value pair to attachment part
	part.add_header(
		"Content-Disposition",
		"attachment; filename= {}".format(filename),
	)

	# Add attachment to message and convert message to string
	message.attach(part)
	text = message.as_string()

	# Log in to server using secure context and send email
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(SMTPSERVER, 465, context=context) as server:
		server.login(MAIL, PASSWORD)
		server.sendmail(MAIL, MAIL, text)
	return 0

# Gets the file from the request and check for safety
def get_secure_file(trustedFile):
	# Check if the filename has a trusted extension
	if '.' in trustedFile.filename \
		and trustedFile.filename.rsplit(".", 1)[1].lower() in EXTENSIONS:
		return trustedFile

	# If there is any problem on the file, return None
	return None
