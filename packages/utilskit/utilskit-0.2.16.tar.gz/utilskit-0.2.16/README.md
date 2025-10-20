# 0.2.16
- repeatutils 의 section_union 에서 mode 를 & 으로 하고 sub 또는 main section 이 빈 리스트인 경우 빈리스트 [] 를 리턴 하도록 수정
# 0.2.15
- repeatutils 의 section_union 에서 결과가 빈값일때 에러가 나는 현상 수정
# 0.2.14
- repeatutils 의 min_key 를 설정했을 때 min_equal=False 로 두는 경우 정상적인 구간 탐색을 못하는 현상 수정
# 0.2.13
- repeatutils 에 section_union 함수 추가
## 0.2.13.1
- rpu.get_section 을 써서 에러가 난 부분 수정
# 0.2.12
- dataframeutils 의 fill_repeat_nan 함수가 NaN 이 딱 하나만 있는 경우 보정하지 못하는 현상 수정
# 0.2.11
- dataframeutils 의 fill_repeat_nan 함수가 3 이하 반복되는 NaN 이 아닌 3 이상 반복되는 NaN 구간에 대해 보정하는 현상 수정
# 0.2.10
- repeatutils 에서 between 이 정상작동하지 않는 현상 수정
## 0.2.10.1
- 버전 업로드 에러 수정
## 0.2.10.2
- 함수 내부 print 제거
# 0.2.9
- repeatuils 에서 정수형 list 를 넣었을때 float 으로 변경되도록 수정
# 0.2.8
- dbutils 에서 db 의 컬럼명을 리스트로 추출하는 get_db_name 함수 추가
## 0.2.8.1
- __all__ 에 get_db_name 추가해서 사용가능하도록 설정
# 0.2.7
- repeatutils 에서 정수형 list 를 넣었을때 key 를 통한 구간 파악이 되지 않는 현상 수정
# 0.2.6
- dataframeutils 의 fill_repeat_nan 의 에러 수정
# 0.2.5
- xlsx 읽는 패키지 install 추가
# 0.2.4
- repeatutils 의 에러 제거
# 0.2.3
- dbutils 에 대한 업데이트 진행
# 0.2.2
- build 방식 변경
# 0.2.1
- repeatutila 에 get_section 함수 추가
# 0.2.0 
- 정식 최초 배포버전
- 각 함수의 사용성 강화 및 비활성 함수 지정
# 0.1.2
- repeatutils 의 get_repeat_section 에서 하나의 값이 여러 구간에서 반복될때 마지막 구간만 나오는 부분 수정
- repeatutils 의 get_repeat_section 및 get_stan_repeat_section 에서 추출되는 구간의 마지막 값이 +1 이 되는 부분 수정
# 0.1.1
- repeatutils.py 추가
- utils.py 에서 repeat 관련 함수 제거