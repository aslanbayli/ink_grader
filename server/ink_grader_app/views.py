import json
from django.shortcuts import render
import pdfplumber
import requests
from .forms import UploadFileForm
from decouple import config
from google.cloud import vision
from skimage.color import rgb2gray
from skimage.transform import rotate
from deskew import determine_skew
from io import BytesIO
import numpy as np    
from PIL import Image
import cv2


SECRET_KEY1 = config("SECRET_KEY1")
SECRET_KEY2 = config("SECRET_KEY2")
RESOURCE_NAME = config("RESOURCE_NAME")
MODEL_NAME = config("MODEL_NAME")


def get_student_score(quiz, answer_key, student_answers):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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",
        "OpenAI-Organization": "org-jIj0K3kPqGQuXANsKVjVZc0k"
    }

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a professor who is grading a student's quiz. \
                The quiz questions, answer key, and student's answers are below:"},

            {"role": "user", "content": "In the quiz, the total number of points per question is \
                specified, and in the answer key, an explanation of what would be an acceptable \
                answer is described. Please evaluate the student's response and provide a score for \
                the quiz, with explanation on where the student went wrong in incorrect responses. \
                Give points awarded for each question. Keep in mind that the student answers will contain \
                only the answers in a numbered order where an answer number corresponds to the question \
                number from the quiz.\n" + "Quiz: " + quiz + "\n\nAnswer Key: " + answer_key + "\n\nStudent's Answers:" + student_answers},

            {"role": "assistant", "content": "Of course, here is the students responses structured in a \
                format as Quiz Name, and Total Points Possible on the quiz, followed by an array where each element is in form of  Question Nnumber, Points Scored per question \
                (if correct, full points; if partially correct, partial credit; if incorrect, 0 points), Feedback, Total Points scored where each line is separate by a new line:"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    
    return response.json()


def extract_text_from_pdf(file):
    # extract text from a PDF file using pdfplumber and an in-memory file
    with pdfplumber.open(file) as pdf:
        text = " ".join(page.extract_text() for page in pdf.pages)
    return text


def pre_process_image(img):
    img = rgb2gray(img) # convert image to grayscale
    angle = determine_skew(img) # determine skew angle
    img = rotate(img, angle, resize=True) * 255 # rotate image
    return img


def writing_to_text(image):
    client = vision.ImageAnnotatorClient() # create client for google vision api
    img = vision.Image(content=image) # create image object
    response = client.document_text_detection(image=img) # get response from google vision api

    return response.full_text_annotation.text


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():

            quiz = BytesIO((request.FILES['quiz_file']).read())
            answer_key = BytesIO((request.FILES['answer_key_file']).read())
            student_answers = (request.FILES['student_answers']).read()

            quiz_text = extract_text_from_pdf(quiz)
            answer_key_text = extract_text_from_pdf(answer_key)

            # convert the uploaded image data to a NumPy ndarray
            pil_image = Image.open(BytesIO(student_answers))
            pil_image_rgb = pil_image.convert('RGB')
            image_ndarray = np.array(pil_image_rgb)

            # pre-process the image
            image = pre_process_image(image_ndarray)

            # convert the image to bytes
            _, image = cv2.imencode('.png', image)
            image = image.tobytes()

            # get the text from hadwritten student answers
            student_text = writing_to_text(image)

            # get student score
            student_score = get_student_score(quiz_text, answer_key_text, student_text)

            temp = { 
                    "Quiz Title": "Loops in Python", 
                    "Total Points Possible": 10, 
                    "Question 1": { "Points Earned": 2, "Feedback": "The student correctly identified the output as '2 4 6 8 10.'" }, 
                    "Question 2": { "Points Earned": 2, "Feedback": "While the student's explanation was somewhat simplified, they clearly understand the key difference between a while loop and a for loop in Python." }, 
                    "Question 3": { "Points Earned": 2, "Feedback": "The student correctly identified that the output would be '[2, 4]'." }, 
                    "Question 4": { "Points Earned": 2, "Feedback": "Student provided the correct Python program using a while loop to print all even numbers from 1 to 10." }, 
                    "Question 5": { "Points Earned": 2, "Feedback": "The student understand when a break statement is used in a loop, the output is correctly identified as 'apple'." },
                    "Total Points Earned": 10 } 
                

            student_score = student_score['choices'][0]['message']['content']
            student_score = print_resp(student_score)

            return render(request, 'student_results.html', {'text': student_score})

    else:
        form = UploadFileForm()
        
    return render(request, 'upload_files.html', {'form': form})


def print_resp(input_string):
    arr = []
    first_question_index = input_string.find("Question")

    if first_question_index != -1:
        # Split the input_string into two parts: before and after the first "Question"
        before_question = input_string[:first_question_index].strip()
        after_question = input_string[first_question_index:].strip()

        arr.append(before_question)

        # Split the part after the first "Question" into smaller strings at each "Question"
        split_strings = after_question.split("Question")

        # Remove any leading or trailing whitespace from each split string
        split_strings = [f'Question {split_strings[s].strip()}' for s in range(1, len(split_strings))]

        # Filter out empty strings, if any
        split_strings = [s for s in split_strings if s]
        
        for i in range(len(split_strings)-1):
            arr.append(split_strings[i])

        temp = split_strings[-1].split("Quiz")
        arr.append(temp[0])
        
        if len(temp) > 1:
            arr.append("Quiz" + temp[1])

        temp = split_strings[-1].split("Total")
        if len(temp) > 1:
            arr.append("Total" + temp[1])
        

    return arr