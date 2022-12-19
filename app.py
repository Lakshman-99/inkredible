from flask import Flask, render_template, request, session, abort, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from docx import Document
from fpdf import FPDF
from pathlib import Path
from pdf2image import convert_from_path as CFP
from support.logic import find_text
import requests, os, uuid, json, sys, torch
from support import main as ms
from PIL import Image
import numpy as np
from support.digitModel import Model, Predict


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['UPLOAD_FOLDER2'] = 'static/saves/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'pdf'])
predict = Predict()

#remove files in uploads & pdf_img
[f.unlink() for f in Path("static/uploads/").glob("*") if f.is_file()]
[f.unlink() for f in Path("static/saves/").glob("*") if f.is_file()]

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

#Home page of the app
@app.route('/home')
@app.route('/')
def home():
	return render_template("home.html")

#Login page of the app
@app.route('/login')
def login():
	return render_template("login.html")

#==> Image & PDF to text OCR
@app.route('/imagetotext')
def imagetotext():
	return render_template('imgtotxt.html')

@app.route('/pdftotext')
def pdftotext():
	return render_template('pdftotxt.html')

@app.route('/upload', methods=['POST'])
def upload():
	uploaded_files = request.files.getlist("file[]")
	if not any(f for f in uploaded_files):
		return redirect(url_for('index'))
	file_details = []
	for file in uploaded_files:
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(filepath)
			text = find_text(filepath)
			file_details.append([filename, text])

	return render_template('imgtotxt_disp.html', files=file_details)

@app.route('/upload2', methods=['POST'])
def upload2():
	uploaded_files = request.files.getlist("file[]")
	if not any(f for f in uploaded_files):
		return redirect(url_for('index'))
	file_details = []
	for file in uploaded_files:
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filepath = os.path.join(app.config['UPLOAD_FOLDER2'], filename)
			file.save(filepath)
			img = CFP(filepath, poppler_path = os.getcwd() + r'\poppler-0.68.0\bin')
			for i in range(len(img)):
				fname = 'page'+ str(i) +'.jpg'
				fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
				img[i].save(fpath, 'JPEG')
				text = find_text(fpath)
				file_details.append([fname, text])

	return render_template('imgtotxt_disp.html', files=file_details)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download', methods=['POST'])
def save_file():
	option = request.form['action']
	texts = request.form.getlist("message[]")

	if option == "word":
		document = Document()
		for text in texts:
			document.add_paragraph(text.replace("\n", ""))
		document.save(os.path.join(app.config['UPLOAD_FOLDER2'], 'extracted_text.docx'))
		return send_file(os.path.join(app.config['UPLOAD_FOLDER2'], 'extracted_text.docx'),as_attachment=True)

	elif option == "pdf":
		texts = "\n".join(texts)
		pdf = FPDF()
		pdf.alias_nb_pages()
		pdf.add_page()
		pdf.set_font('Times', '', 10)
		for text in texts.split("\n"):
			pdf.cell(0, 8, text.encode('utf-8').decode('latin-1'), 0, 1)
		pdf.output(os.path.join(app.config['UPLOAD_FOLDER2'], 'extracted_text.pdf'), 'F')
		return send_file(os.path.join(app.config['UPLOAD_FOLDER2'], 'extracted_text.pdf'),as_attachment=True)

	elif option == "txt":
		with open(os.path.join(app.config['UPLOAD_FOLDER2'], "extracted_text.txt"), "w") as f:
			for text in texts:
				f.write(text.replace("\n", ""))
		return send_file(os.path.join(app.config['UPLOAD_FOLDER2'], "extracted_text.txt"),as_attachment=True)

	return ""

#mathematical expression
@app.route('/mathematicalexpression')
def mathematicalexpression():
	return render_template('maths.html')

@app.route('/math_uploader', methods=['POST'])  # uploader
def math_uploader():
	f = request.files['file']
	f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
	ms.my_func()
	h = open('static/results/calculationResult.txt', 'r')
	content = h.readlines()
	mynum = "No result available"
	for line in content:
		mynum = line # int(line)

	f = open('static/results/MathJaxResult.txt', 'r')
	cont = f.readlines()
	mylatex = "No latex output available"
	for line in cont:
		mylatex = line # int(line)

	return render_template("math_result.html", user_number = mynum, user_latex = mylatex)

@app.route('/reset')
def remove():
	[f.unlink() for f in Path("static/uploads/").glob("*") if f.is_file()]
	[f.unlink() for f in Path("static/results/").glob("*") if f.is_file()]
	return redirect('mathematicalexpression')

#language translator
@app.route('/translation', methods=['GET'])
def translation():
    return render_template('translation.html')

@app.route('/translation_result', methods=['POST'])
def translation_result():
	original_text = request.form['text']
	target_language = request.form['language']

	key = "d6095aa6be8448c4ab075ec8a0840137"
	endpoint = "https://api.cognitive.microsofttranslator.com/"
	location = "westus2"

	path = '/translate?api-version=3.0'
	target_language_parameter = '&to=' + target_language
	constructed_url = endpoint + path + target_language_parameter

	headers = {
	    'Ocp-Apim-Subscription-Key': key,
	    'Ocp-Apim-Subscription-Region': location,
	    'Content-type': 'application/json',
	    'X-ClientTraceId': str(uuid.uuid4())
	}

	body = [{ 'text': original_text }]

	translator_request = requests.post(constructed_url, headers=headers, json=body)
	translator_response = translator_request.json()
	translated_text = translator_response[0]['translations'][0]['text']

	return render_template('translation_result.html', translated_text=translated_text, original_text=original_text, target_language=target_language)

#text to speech
@app.route('/texttospeech', methods=['GET','POST'])
def texttospeech():
    return render_template('texttospeech.html')

#digit recognition
@app.route("/digitrecognition", methods=['GET','POST'])
def digitrecognition():
	if(request.method == 'POST'):
		img = Image.open(request.files["img"]).convert("L")
		res_json = {"pred": "Err", "probs": []}
		if predict is not None:
			res = predict(img)
			res_json["pred"] = str(np.argmax(res))
			res_json["probs"] = [p * 100 for p in res]
		return json.dumps(res_json)

	return render_template("digit.html")

if __name__ == '__main__':
	app.run(host="0.0.0.0", debug=True, use_reloader=True)
