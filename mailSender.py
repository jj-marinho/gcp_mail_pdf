import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, request

MAIL = "vagas@alfadiagnostica.com.br"
EXTENSIONS = ['pdf']
app = Flask(__name__)

@app.route('/', methods=['POST'])
def main_func():

	# Getting the request information
	file = get_secure_file()	
	name = request.form['name'] 
	area = request.form['area']
	message = request.form['message']

	# Sending mail through send_mail function
	response = send_mail(name, area, message, file)

	# JSON response
	if response == 0:
		return {
			"status": 200,
			"body": "Seu currículo foi enviado com sucesso"
		}
	else: 
		return {
			"status": 503,
			"body": "Houve um problema ao enviar seu currículo"
		}



def send_mail(name, area, message, file):
	subject = "Novo currículo de: {}, Área: {}".format(name, area)
	body = "Mensagem automatizada.\n\nTexto enviado por: {}\n\n{}".format(name, message)
	password = input("Senha fora do GCP: ") # Alterar para variavel no GCP

	# Create a multipart message and set headers
	message = MIMEMultipart()
	message["From"] = MAIL 
	message["To"] = MAIL 
	message["Subject"] = subject

	# Add body to email
	message.attach(MIMEText(body, "plain"))

	# New filename, join and split take care of any whitespace
	filename = "curriculum{}.pdf".format("".join(name.split())) 

	# Open PDF file in binary mode
	# Add file as application/octet-stream
	# Email client can usually download this automatically as attachment
	part = MIMEBase("application", "octet-stream")
	part.set_payload(file.read())

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
	with smtplib.SMTP_SSL("echo.mxrouting.net", 465, context=context) as server:
		server.login(MAIL, password)
		server.sendmail(MAIL, MAIL, text)
	return 0

# Gets the file from the request
# Returns either a secure filename and the file
# Or a "" and None. Meaning there was an error in the file retrieval
def get_secure_file():
	file = request.files['file']

	if file and ('.' in file.filename and file.filename.rsplit(".", 1)[1].lower() in EXTENSIONS):
		return file
	
	return ("", None)
