import json 
import os
import sys, getopt, traceback
import re
import fitz  # PyMuPDF library for PDF parsing
import pdfplumber
from PIL import Image
import io
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

'''Alter the below Regular expresssions to match the requirements of the document in hand.'''

re_q = r'(^[0-9]\.\s|^[0-9][0-9]\.\s)'    #regex to match the question (looks for a number in the start of the line)
re_o = r'^[a-z]\.'  #regex to match an option (looks for a lower case character followed by a period)
re_a = r'^\d+\. [A-Z]'#_?_?\)?\s?' #format for getting the Answer from answer.txt
re_h = r'(ECON|FOCUSED|QUIZ|DemiDec|DemiDEc|Science\sComprehensive)'   #regex for unique identifier (word) that signifies a new page/section
re_uniq = r'(PP\.\s?\d+|Science\sComprehensive\sExam\s\d+)'            #Pattern to look for to start a new Section.
re_skip = r'Page'           #The phrases to be skipped
re_start = r'^\d+'          #to check the start of a quesstion is with a digit
alpha = 1.5                 #Contrast Controller
beta = 50                    #Brightness Controller


#sets the questions in the final Dictionary
def set_questions(q_lines):
    Paper_Set= {}
    set = ''
    for index in range(len(q_lines)):
        line = q_lines[index]
        if re.search(re_uniq, line):
            if re_skip in line:
                continue
            set = re.findall(re_uniq, line)[0]
            Paper_Set[set] = []
            print(set)     
        
        if re.match(re_q, line):
            if len(line)==4:
                current_question =  q_lines[index]+ q_lines[index+1]
                for i in range(index+2, len(q_lines)):
                    if re.match(re_o,q_lines[i]):
                        break
                    else:
                        current_question += q_lines[i]
            else:
                current_question = line#[3:]
                for i in range(index+1, len(q_lines)):
                    if re.match(re_o,q_lines[i]):
                        break
                    else:
                        current_question += q_lines[i]
            current_options = {}
            for j in range(i, len(q_lines)):
                line = q_lines[j]
                if re.match(re_q, line):
                    break
                if re.match(re_o,line):
                    option = line
                    for k in range(j+1, len(q_lines)):
                        check = q_lines[k]
                        if re.search(re_o,check):
                            break
                        elif re.search(re_q,check):
                            break
                        elif re.findall(re_h,check):
                            break
                        else:
                            option+=check
                    option = "".join(option.split("\n"))
                    option = option.replace('\u2019', "'")
                    option = option.replace('\u201c', '"')
                    option = option.replace('\u201c', '"')
                    option = option.replace('\u2013', "-")
                    current_options[re.findall(re_o, option)[0][:1]] = option[3:]

                    #current_options.append(option)
                else:
                    continue
            current_question = "".join(current_question.split("\n"))
            current_question = current_question.replace('\u2019', "'")
            current_question = current_question.replace('\u201c', '"')
            current_question = current_question.replace('\u201d', '"')
            current_question = current_question.replace('\u2013', "-")
            question_dict = {"question" : current_question, "options" : current_options, "answer" : ""}
            Paper_Set[set].append(question_dict)

    return Paper_Set


#sets the Answers in the final dictionary according to the q_no
def set_answers(a_lines, Paper_Set):
    set = ""
    for index in range(len(a_lines)):
        line = a_lines[index]
        if re.search(re_uniq,line):
            if re_skip in line:
                continue
            set = re.findall(re_uniq, line)[0]
            print(set)
            if set not in Paper_Set:
                break

        if re.match(re_a,line):
            answers = re.findall(re_a, line)
            answer = re.findall(r'[A-Z]_?', answers[0])
            q_no = re.findall(r'\d+\.', line)
            if q_no:
                q_no = q_no[0]
            else:
                continue
            questions = [i["question"] for i in Paper_Set[set]]
            dict_index = 0
            for q in range(len(questions)):
                if q_no in questions[q]:
                    #print(q_no, line)
                    dict_index = q
                    break
            Paper_Set[set][dict_index]['answer'] = answer[0]
            #question+=1
    return Paper_Set


#writing to json
def preprocess_to_json(Paper_Set, json_filename):
    for set in Paper_Set:
        for val in Paper_Set[set]:
            val["question"] = val["question"][3:]
    with open(json_filename, "w") as f:
        json.dump(Paper_Set, f, indent = 4)


#Converts PDF to Image
def pdf_to_image(pdf_path, folder):
    pages = convert_from_path(pdf_path)
    for i in range(len(pages)):
        page = pages[i]
        page.save(folder+"/page"+str(i+1)+'.png', 'PNG')
    return

#Extracts the text from the image and returns the lines
def image_to_text(folder_path):
    images = os.listdir(folder_path)
    text = []
    for i in range(len(images)):
        print(i)
        page_image = Image.open(folder_path+'/page'+str(i+1)+'.png')
        width, height = page_image.size
        split_width = width//2
        left_image = page_image.crop((0, 0, split_width, height))
        right_image = page_image.crop((split_width, 0, width, height))

        text_from_page_left = pytesseract.image_to_string(left_image, config= r'--psm 6')
        text_from_page_right = pytesseract.image_to_string(right_image, config= r'--psm 6')

        '''Uncomment the following lines for OTSU Thresholding to increase the contrast of the images
        (This is not adviced since, it might distrupt the appearance of the existing characters, giving unexpected results)'''

        # left_image_np = np.array(left_image)
        # right_image_np = np.array(right_image)
        # left_gray = cv2.cvtColor(left_image_np, cv2.COLOR_BGR2GRAY)
        # _, left_binary_image = cv2.threshold(left_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # left_enhanced_image = cv2.convertScaleAbs(left_binary_image, alpha=alpha, beta=beta)
        # right_gray = cv2.cvtColor(right_image_np, cv2.COLOR_BGR2GRAY)
        # _, right_binary_image = cv2.threshold(right_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # right_enhanced_image = cv2.convertScaleAbs(right_binary_image, alpha=alpha, beta=beta)
        # text_from_page_left = pytesseract.image_to_string(left_enhanced_image, config= r'--psm 6')
        # text_from_page_right = pytesseract.image_to_string(right_enhanced_image, config= r'--psm 6')


        #text.append(text_from_page)
        text+= text_from_page_left.split('\n')
        text+= text_from_page_right.split('\n')
    return text
    
#getting the liness from a text/pdf with no images
def get_lines(path, is_pdf):
    if is_pdf == 1:
        doc = fitz.open(path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text("text")
        doc.close()
        path = os.path.splitext(path)[0] +".txt"
        with open(path, 'w') as f:
           f.write(text)
    lines = ""
    with open(path, 'r') as f:
        lines = f.readlines()
    return lines


def usage():
    print ("\n\n" + sys.argv[0] + ' -q <QuestionFile> -a <AnswerFile> -m <pdf|txt>\n\n')
    sys.exit()


if __name__ == "__main__":

    argv = sys.argv[1:]
    q_path = ""
    a_path = ""
    is_pdf = 0
    try:
        opts, args = getopt.getopt(argv,"ha:q:m:",["qfile=","afile=","format="])
        for opt, arg in opts:
            if opt == '-h':
               usage()
            elif opt in ("-q", "--qfile"):
               q_path = arg
            elif opt in ("-a", "--afile"):
               a_path = arg
            elif opt in ("-m", "--mode"):
                if arg == "pdf":
                   is_pdf = 1
                elif arg == "pdf_img":
                    is_pdf = 2
                else:
                    is_pdf = 0
    except Exception as e:
        print(e)
        usage()
    if q_path == "" or a_path == "" :
        usage()
    print ("q_path:" + q_path)
    print ("a_path:" + a_path)
    print(is_pdf)
    if is_pdf == 2:
        pdf_to_image(q_path, "Text_to_Json/questions")
        q_text = image_to_text("Text_to_Json/questions")
        pdf_to_image(a_path, "Text_to_Json/answers")
        a_text = image_to_text("Text_to_Json/answers")
        Paper_set = set_questions(q_text)
        Paper_set = set_answers(a_text, Paper_set)
        preprocess_to_json(Paper_set, os.path.splitext(q_path)[0] +".json")
    else:
        q_text = get_lines(q_path, is_pdf)
        a_text = get_lines(a_path, is_pdf)
        Paper_set = set_questions(q_text)
        Paper_set = set_answers(a_text, Paper_set)
        preprocess_to_json(Paper_set, os.path.splitext(q_path)[0] +".json")
