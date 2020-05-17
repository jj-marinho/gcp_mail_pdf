import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask
from werkzeug.utils import secure_filename

MAIL = "vagas@alfadiagnostica.com.br"
EXTENSIONS = ['pdf']

app = Flask(__name__)

@app.route('/', methods=['POST'])
def main_func():
	# GetData

	nome = "Joao Guilherme"
	area = "Informatica"
	corpo = "Ola, aqui esta meu curriculo, espero que me contratem"

	response = send_mail(nome, area, corpo)

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

def get_pdf(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in EXTENSIONS


def send_mail(nome, area, corpo):
	subject = "Novo currículo de: {}, Área: {}".format(nome, area)
	body = "Mensagem automatizada.\n\nTexto enviado por: {}\n\n{}".format(nome, corpo)
	password = input("Senha fora do GCP: ") # Alterar para variavel no GCP

	# Create a multipart message and set headers
	message = MIMEMultipart()
	message["From"] = MAIL 
	message["To"] = MAIL 
	message["Subject"] = subject

	# Add body to email
	message.attach(MIMEText(body, "plain"))

	# Definindo nome do arquivo sem espaçamentos
	filename = "curriculo{}.pdf".format("".join(nome.split())) 

	# Open PDF file in binary mode
	with open(filename, "rb") as attachment:
		# Add file as application/octet-stream
		# Email client can usually download this automatically as attachment
		part = MIMEBase("application", "octet-stream")
		part.set_payload(attachment.read())

	# Encode file in ASCII characters to send by email    
	encoders.encode_base64(part)

	# Add header as key/value pair to attachment part
	part.add_header(
		"Content-Disposition",
		f"attachment; filename= {filename}",
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
