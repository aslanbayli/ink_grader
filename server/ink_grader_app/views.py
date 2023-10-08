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
    url = f"https://{RESOURCE_NAME}.openai.azure.com/openai/deployments/{MODEL_NAME}/chat/completions?api-version=2023-05-15"

    headers = {
        "Content-Type": "application/json",
        "api-key": f"{SECRET_KEY1}"
    }

    data = {
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

            {"role": "assistant", "content": "Of course, here is the students responses structured as question, points scored \
                (if correct, full points; if partially correct, partial credit; if incorrect, 0 points), and feedback:"}
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
                    "quiz": "Loops in Python",
                    "total_points": 10,
                    "questions": [
                        {
                            "number": 1, 
                            "points": 2,            
                            "student_answer": "1 2 4 6 8 10",           
                            "feedback": "The correct answer is: 2 4 6 8 10. The student missed the loop declaration and did not use the variable \'i\' to index through the list."        
                        },        
                        {           
                            "number": 2,            
                            "points": 2,            
                            "student_answer": "20 A for loop is for a fixed number of\iterations, while a while loop is\for when you want to stop when\Some event occurs.",            
                            "feedback": "The response is partially correct, but lacks an example of when to use a for loop or a while loop."        
                        },        
                        {            
                            "number": 3,            
                            "points": 2,            
                            "student_answer": "[2, 4]",            
                            "feedback": "The student\'s answer is correct."        
                        },        
                        {            
                            "number": 4,            
                            "points": 2,            
                            "student_answer": "4 X=1\While x <= 10:\if x%2 == 0:\print (x)\X+ = 1",            
                            "feedback": "The student\'s answer is incorrect. It should be:\\x = 1\while x <= 10:\    if x % 2 == 0:\        print(x)\    x += 1"        
                        },        
                        {            
                            "number": 5,           
                            "points": 2,            
                            "student_answer": "apple",            
                            "feedback": "The student\'s answer is correct."        
                        }
                    ],    

                    "final_grade": 6
                }

            student_score = student_score['choices'][0]['message']['content']
            return render(request, 'student_results.html', {'text': temp})

    else:
        form = UploadFileForm()
        
    return render(request, 'upload_files.html', {'form': form})



