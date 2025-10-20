LECTURE_DATA = {
    "lec1": """
    [1강: 파이썬 기초]
    - 파이썬은 1991년에 귀도 반 로섬이 개발한 언어입니다.
    - 문법이 간결하고 읽기 쉽습니다.
    """,
    
    "lec2": """
    [2강: 변수와 자료형]
    - 변수: 데이터를 저장하는 공간 (예: a = 10)
    - 자료형: 숫자(int, float), 문자열(str) 등이 있습니다.
    """
}

def get_note(lecture_name):
    return LECTURE_DATA.get(lecture_name, "해당 강의 노트를 찾을 수 없습니다. (예: lec1, lec2)")
