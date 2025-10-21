import sys
from .notes import get_note  # 같은 폴더(.)의 notes.py에서 get_note 함수 가져오기

def main():
    try:
        # "my-notes lec1" 중 "lec1" 부분을 가져옴
        command = sys.argv[1]
    except IndexError:
        print("강의 번호를 입력하세요. (예: my-notes lec1)")
        sys.exit(1) # 오류로 종료
        
    note = get_note(command)
    print(note)
