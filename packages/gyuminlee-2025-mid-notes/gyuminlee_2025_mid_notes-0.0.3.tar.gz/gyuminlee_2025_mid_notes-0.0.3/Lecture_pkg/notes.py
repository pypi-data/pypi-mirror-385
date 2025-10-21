LECTURE_DATA = {
    "inverse": """
def inverse():
  str=input("Input :") #User input
  print() #한줄 띄우기
  for i in range(len(str)):
    print(str[i::-1]) #inverse the output, str 거꾸로
inverse()

    """,
    
    "fibo": """
def fibo(n):
    if n <= 1: #피보나치 0,1번째는 그냥 0,1 임
        return n #그래서 N 그래도 출력
        
    a, b = 0,1 

    for _ in range(n-1): # n-1 번 반복
        a,b = b, a+b # b - 현재 숫자를 a+b. 근데 b = a+b 에서 a 값은 라인 끝나고 적용. 라인 끝나기 전에는 a 안바뀜
    return b

if __name__ == "__main__":
    try:
        num = int(input("input: "))
        result = fibo(num)
        print(result)
    except ValueError:
        print("정수만 입력")
    """,

    "NaA": """
def func():
    print("function A.py!") 
print("top-level A.py") #이건 NaA.py 열리면 실행 됨

if __name__ == "__main__": #이건 직접 실행 될때
    print("A.py 직접실행") 
else: 
    print("A.py import 되어 실행 중") #이건 직접 X
    print(__name__)

import NaA #NaA 직접 실행 X

print("top-level B.py") #NaB 열리니까 일단 실행
NaA.func() #NaA import 해서 func() 실행, 

if __name__ == "__main__":
    print("B.py 직접 실행") #NaB 직접 실행
else:
    print("B.py import 되어 실행중")
    
    """,

    "undefined1": """
def crcl_area_undefi(radius, *pi, **info):
    for item in pi:
        area = item*(radius **2)
        print("반지름:", radius, "PI:", item,"Area:",round(area,2))
    for key in info:
        print(key, ":", info[key]) #dictionary, key = line color, area color
if __name__ =="__main__":
    crcl_area_undefi(3,3.14,3.1415,line_color="blue",area_color = "yellow")
    print()

    """,

    "undefined2": """
def add_undefi(x,y,*args,**kargs):
    print("local variables", locals())
    sum = sumj = 0
    sum = x+y
    for i in args:
        sum += i
    for k,j in kargs.items():
        sumj += j
    return sum + sumj

print(add_undefi(10,20,3,4,5,k1=1,k2=2))
print(add_undefi(10,20,*(3,4,5),**dict(k1=1,k2=2)))
print(add_undefi(10,20))

    """,

    "change": """
#change
def count_characters(input_string):
    char_counts = {}
    for char in input_string:
        lower_char = char.lower()
        char_counts[lower_char] = char_counts.get(lower_char, 0) + 1
    return char_counts

def swap_case_custom(input_string):
    result = ""
    for char in input_string:
        if char.islower():
            result += char.upper()
        elif char.isupper():
            result += char.lower()
        else:
            result += char
    return result

while True:
    try:
        user_input = input("Input:")
    except EOFError:
        break

    if user_input == "STOP":
        print("Bye")
        break

    #각 문자의 개수 세기 및 출력
    counts = count_characters(user_input)
    
    #출력 순서를 입력 순서에 맞게 처리하기 위한 리스트
    printed_chars = []
    
    for char in user_input:
        lower_char = char.lower()
        if lower_char not in printed_chars:
            print(f"({lower_char} : {counts[lower_char]})", end=" ")
            printed_chars.append(lower_char)
    print() #개수 출력 후 줄바꿈

    #대소문자 변환하여 출력
    swapped_string = swap_case_custom(user_input)
    print(swapped_string)

    """,

    "leap": """
#LEAP
def is_leap(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def input_date():
    year = int(input("__년도를 입력하시오: "))
    month = int(input("__월을 입력하시오: "))
    day = int(input("__일을 입력하시오: "))
    return year, month, day

def get_day_name(year, month, day):
    # 1. 1년 1월 1일부터 (year-1)년 12월 31일까지의 총일수 계산
    total_days = 0
    for y in range(1, year):
        if is_leap(y):
            total_days += 366  # 윤년은 366일
        else:
            total_days += 365  # 평년은 365일

    # 2. 올해의 (month-1)월까지의 총일수 계산
    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # 올해가 윤년이면 2월은 29일
    if is_leap(year):
        days_in_month[2] = 29
        
    for m in range(1, month):
        total_days += days_in_month[m]

    # 3. 입력된 일(day)을 더함
    total_days += day

    # 4. 요일 계산 (1년 1월 1일은 월요일 -> 나머지 1)
    day_names = ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"]
    remainder = total_days % 7
    
    return day_names[remainder]


if __name__ == "__main__":
    # 날짜 입력 받기
    year, month, day = input_date()
    
    # 요일 구하기
    day_name = get_day_name(year, month, day)
    
    # 요일 출력
    print(day_name)
    
    # 윤년 여부 확인 및 출력
    if is_leap(year):
        print("입력하신 %s은 윤년입니다" % year)

    """,

    "lambda": """
import random

# iter() 함수는 첫 번째 인자(lambda)를 계속 호출하다가,
# 그 결과가 두 번째 인자(sentinel 값, 2)와 같아지면 반복을 멈춥니다.
random_iterator = iter(lambda: random.randint(0, 5), 2)

print("2가 나올 때까지 생성된 난수:")

# for 루프를 이용해 이터레이터에서 값을 하나씩 꺼내 출력합니다.
for num in random_iterator:
    print(num, end=" ")

    """,

    "fourcal": """
class FourCal:
    # 객체가 생성될 때 숫자 두 개를 받아 인스턴스 변수에 저장하는 초기화 메서드
    def __init__(self, num1, num2):
        self.num1 = num1
        self.num2 = num2

    # 더하기 기능을 하는 메서드
    def sum(self):
        result = self.num1 + self.num2
        return result

    # 빼기 기능을 하는 메서드
    def sub(self):
        result = self.num1 - self.num2
        return result

    # 곱하기 기능을 하는 메서드
    def mul(self):
        result = self.num1 * self.num2
        return result

    # 나누기 기능을 하는 메서드
    def div(self):
        result = self.num1 / self.num2
        return result

    """,

    "oop1": """
#OOP1
class verbose:

  def __init__(self, f):
    print("Initializing Verbose.")
    self.func = f

  def __call__(self, *args, **kwargs):

    print("\nBegin", self.func.__name__)
    self.func(*args, **kwargs)
    print("End", self.func.__name__)

@verbose
def my_function(name):

  print(f"hello, {name}!")

# Main execution block
if __name__ == "__main__":
  print("Program start")
  my_function("Mickey")
  my_function("Minnie")
  my_function("Donald")

    """,

    "oop2": """
#OOP2
import time
import datetime

def checkTime(func):

  def wrapper(*args, **kwargs):

    # 현재 날짜와 시간을 출력합니다. [cite: 1353]
    start_time_str = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M]')
    print(start_time_str)

    # 실행 시간을 측정하기 위해 시작 시간을 기록합니다.
    start_time = time.time()

    # 원래 함수를 실행합니다.
    func(*args, **kwargs)

    # 실행이 끝난 후의 시간을 기록합니다.
    end_time = time.time()

    # 실행 시간을 계산하고 출력합니다. [cite: 1353]
    print(f"실행시간은: {end_time - start_time}")

  return wrapper

@checkTime
def aFunc():

  for i in range(1, 101):
    print(i, end=' ')
  print() # 줄바꿈

@checkTime
def bFunc(start, end):
  for i in range(start, end + 1):
    print(i, end=' ')
  print() # 줄바꿈

# --- 메인 실행 부분 ---
aFunc()
print("-------------------------")
bFunc(101, 202)

    """,

    "fibo2": """
def fibo(n):
    if n == 1:
        return 1
    elif n == 2:
        return 1
    else:
        return fibo(n-2) + fibo(n-1)

if __name__ =="__main__":
    print("7th fibonacci: %d" %fibo(7))


    """,

    "fibo3": """
def fibonacci():
    a,b = 0,1 #피보나치 초기값 설정 like 재귀함수하듯이
    while 1: #무한 루프
        yield a
        a,b = b, a+b
for i, ret in enumerate(fibonacci()):
    if i<20: print(i, ret)
    else:
        break

    """,

    "fibo4": """
#Fibo4
def fibo_func(n):
    a,b = 0,1
    count = 0
    while count < n:
        yield a
        a, b = b, a+b
        count += 1
try: 
    n = int(input("how many fibonacci? "))
    if n<=0:
        print("number should be more than 1")
    else: 
        print(f"Total {n} fibonacci:")

        fibo_sequence = fibo_func(n+1)
        for number in fibo_sequence: #yield 하나씩 꺼내서 number 에 담음. count < n 까지
            print(number, end=" ")
        print()
except ValueError:
    print("Wrong input")

    """,

    "AI": """ 
    [Settings]
    !pip install google
    !pip install -q -U google-genai

    import os
    os.environ['GEMINI_API_KEY'] = "AIzaSyAofx7yVVhnr59u5Q6X0RaRFtrubfwJwhQ"

    from google import genai

    [API Calls]
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=" 이 문제야. 나는 Jupyter Notebook 사용하고 있어. 코딩 해줘",
    )

    print(response.text)

    """
}

def get_note(lecture_name):
    return LECTURE_DATA.get(lecture_name, "해당 강의 노트를 찾을 수 없습니다. (예: 함수, lec)")
