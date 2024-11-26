import streamlit as st
import tempfile
import PyPDF2
import google.generativeai as genai
import fitz

genai.configure(api_key="AIzaSyD97oOcRVrj8-gs6Sp_KCgGu8nfdMZ5TWc")

generation_config = {
  "temperature": 0.01 ,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}
generation_config_text = {
  "temperature": 0.01,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}


safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

def get_ocr_response(file_bytes):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash",#extract
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    prompt_parts = []
    prompt_parts.append("###Instructions###\nYou are an expert OCR assistant.\nAccurately extract all text, including headings, paragraphs, and answers as it is given in the image.Do not extract questions.\nSerial numbers might not be in order in the image so make sure to retrieve as it is.\nNumbers that are mentioned outside the margin are not serial numbers, serial numbers are based on the position.\nmention serial numbers as \"Question_no_'Num'\" in output.\nUse bullets for clarity in the extracted text.\nPresent the extracted tables in Markdown format.\nDescribe the diagrams and flowcharts in a clear and concise textual format, capturing their essential elements and relationships.\n Question_no_'num':\n\n###Example output###\n#Answers(extract as it is)\nQuestion_no_1:\n(text extracted)\n\nYou should not make up any answer. Strictly follow the instructions and extract text as it is.\n")

    doc = fitz.open("pdf", file_bytes)

    for page_num, page in enumerate(doc):
        pix = page.get_pixmap()
        prompt_parts.append({"mime_type": "image/jpeg", "data": pix.tobytes()})

    response = model.generate_content(prompt_parts, stream=True)
    response.resolve()
    return response.text

def get_evaluation(answer_key, student_answer): 
    model = genai.GenerativeModel(
                              model_name="gemini-pro",
                              generation_config=generation_config_text,
                              safety_settings=safety_settings
                          )
    response = model.generate_content(contents="###Instruction###\nYou are a Grading expert, who assists teachers in evaluating answer sheets and providing feedback. Evaluate the given answer sheet.\nProvide marks with feedback for each answer compared with the key. Include overall marks, and feedback(with topics to focus).\n###Answer sheet:###\n" + student_answer + "\n###Answer key:###\n" + answer_key + "\n###Output format###You should provide marks for each question.\n Question_'num':\nMarks: __/(refer key)  \nFeedback:\n\noverall feedback: ... \ntotal marks: ..\n\n You should strictly follow the output format", stream=True)                 
    response.resolve()
    return response.text

def main():
    st.title("PDF Uploader")
    st.write("Upload a PDF file below:")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    answer_key = st.text_input("Type the evaluation criteria/key:","")

    if uploaded_file and answer_key is not None:
        pdf_bytes = uploaded_file.read()

        if st.button("Evaluate"):
            st.write("### Evaluation results:")
            ocr_result = get_ocr_response(pdf_bytes)
            evaluation_result = get_evaluation(answer_key, ocr_result)
            st.write(evaluation_result)

if __name__ == "__main__":
    main()