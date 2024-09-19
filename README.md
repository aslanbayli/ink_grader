# InkGrader - "More time teaching, less time grading"

#### InkGrader is a tool for educators to streamline their grading process. Using InkGrader you can scan both typed text and handwritten text, and thanks to the Google Cloud Vision API. For convenience, educators can upload their exam questions and answer sheet to InkGrader which uses OpenAI API under the hood to check the uploaded exam. 

## How to use
1. Clone the project from github

2. Navigate into the project directory using your terminal

3. Run the following command to install all dependencies (optionally create a venv)
    ```
    pip install -r requirements.txt
    ```

4. Navigate into the `ink_grader` directory

5. Run the following command to launch the app
    ```
    python manage.py runserver
    ```

___Note: if you encounter any issues, make sure you have a working Python interpreter installed on your system.___
___In addition, you will need an OpenAI API key and Google Cloud vision API key run the application.___

## Home screen
![image](https://github.com/Aslanbayli/ink_grader/assets/48028559/edeb6007-2a32-4656-a354-69dfd38da5a0)

## Results
![image](https://github.com/Aslanbayli/ink_grader/assets/48028559/0f959f89-661f-4804-9a13-98962b620d28)

