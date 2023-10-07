from django.shortcuts import render, redirect
from django.http import HttpResponse
import pdfplumber
import requests
from .forms import UploadFileForm
from decouple import config
from io import BytesIO

SECRET_KEY1 = config("SECRET_KEY1")
SECRET_KEY2 = config("SECRET_KEY2")
RESOURCE_NAME = config("RESOURCE_NAME")
MODEL_NAME = config("MODEL_NAME")

def get_student_score(quiz, answer_key, student_answers):
    url = f"https://{RESOURCE_NAME}.openai.azure.com/openai/deployments/{MODEL_NAME}/chat/completions?api-version=2023-05-15"

    headers = {
        "Content-Type": "application/json",
        "api-key": f"{SECRET_KEY1}"
    }

    data = {
        "messages": [
            {"role": "system", "content": "You are a professor who is grading a student's quiz. The quiz questions, answer key, and student's answers are below:"},
            {"role": "user", "content": "In the quiz, the total number of points per question is specified, and in the answer key, an explanation of what would be an acceptable answer is described. Please evaluate the student's response and provide a score for the quiz, with explanation on where the student went wrong in incorrect responses. Give points awarded for each question. Keep in mind that the student answers will contain the question as well as it is a scanned copy of their quiz.\n" + "Quiz: " + quiz + "\n\nAnswer Key: " + answer_key + "\n\nStudent's Answers: " + student_answers},
            {"role": "assistant", "content": "Of course, here is the students responses along with a total number of points awarded for the quiz, with points awarded per question shown, and comments on where the student went wrong on questions they didn't score full points:"}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def extract_text_from_pdf(file):
    # Extract text from a PDF file using pdfplumber and an in-memory file
    with pdfplumber.open(file) as pdf:
        text = " ".join(page.extract_text() for page in pdf.pages)
    return text

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():

            quiz = BytesIO((request.FILES['quiz_file']).read())
            answer_key = BytesIO((request.FILES['answer_key_file']).read())

            quiz_text = extract_text_from_pdf(quiz)
            answer_key_text = extract_text_from_pdf(answer_key)

            # Extract text from image
            student_text = "" #hand_to_text(request.FILES['student_answers'])

            # Get student score
            student_score = get_student_score(quiz_text, answer_key_text, student_text)
            
            
            return render(request, 'student_results.html', {'text': student_score})
    else:
        form = UploadFileForm()
    return render(request, 'upload_files.html', {'form': form})
