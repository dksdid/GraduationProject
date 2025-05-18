import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image, ImageOps
import io
import matplotlib.font_manager as fm
import subprocess

# 1. 폰트 설치 (Streamlit Cloud 런타임에서 매번 실행해야 할 수 있음)
subprocess.run(['apt-get', 'update'])
subprocess.run(['apt-get', 'install', '-y', 'fonts-nanum'])

# 2. matplotlib 폰트 캐시 재생성
fm._rebuild()

# 3. 폰트 설정
plt.rc('font', family='NanumGothic')
plt.rc('axes', unicode_minus=False)

# 음식 목록 (영어 이름, 한글 이름, 혈당 지수)
food_dict = {
    "Apple Pie": ("애플 파이", 70),
    "Baby Back Ribs": ("바비큐 등갈비", 35),
    "Baklava": ("바클라바", 70),
    "Beef Carpaccio": ("소고기 카르파초", 0),
    "Beef Tartare": ("소고기 타르타르", 0),
    "Beet Salad": ("비트 샐러드", 35),
    "Beignets": ("베녜", 75),
    "Bibimbap": ("비빔밥", 60),
    "Bread Pudding": ("브레드 푸딩", 60),
    "Breakfast Burrito": ("아침 부리또", 60),
    "Bruschetta": ("브루스케타", 60),
    "Caesar Salad": ("시저 샐러드", 20),
    "Cannoli": ("카놀리", 70),
    "Caprese Salad": ("카프레제 샐러드", 15),
    "Carrot Cake": ("당근 케이크", 56),
    "Ceviche": ("세비체", 5),
    "Cheesecake": ("치즈케이크", 56),
    "Cheese Plate": ("치즈 플래터", 60),
    "Chicken Curry": ("치킨 카레", 55),
    "Chicken Quesadilla": ("치킨 케사디야", 60),
    "Chicken Wings": ("치킨 윙", 25),
    "Chocolate Cake": ("초콜릿 케이크", 56),
    "Chocolate Mousse": ("초콜릿 무스", 50),
    "Churros": ("추로스", 70),
    "Clam Chowder": ("클램 차우더", 50),
    "Club Sandwich": ("클럽 샌드위치", 71),
    "Crab Cakes": ("크랩 케이크", 55),
    "Creme Brulee": ("크렘 브륄레", 50),
    "Croque Madame": ("크로크 마담", 65),
    "Cup Cakes": ("컵케이크", 46),
    "Deviled Eggs": ("데빌드 에그(속을 채운 삶은 달걀)", 10),
    "Donuts": ("도넛", 73),
    "Dumplings": ("만두", 28),
    "Edamame": ("에다마메(풋콩)", 15),
    "Eggs Benedict": ("에그 베네딕트", 60),
    "Escargots": ("에스카르고(달팽이 요리)", 5),
    "Falafel": ("팔라펠", 40),
    "Filet Mignon": ("필레미뇽(소고기 안심 스테이크)", 30),
    "Fish and Chips": ("피쉬 앤 칩스", 60),
    "Foie Gras": ("푸아그라", 0),
    "French Fries": ("감자튀김", 64),
    "French Onion Soup": ("프렌치 어니언 수프", 40),
    "French Toast": ("프렌치 토스트", 72),
    "Fried Calamari": ("오징어 튀김", 55),
    "Fried Rice": ("볶음밥", 80),
    "Frozen Yogurt": ("프로즌 요거트", 24),
    "Garlic Bread": ("마늘빵", 65),
    "Gnocchi": ("뇨끼", 67),
    "Greek Salad": ("그리스 샐러드", 20),
    "Grilled Cheese Sandwich": ("그릴드 치즈 샌드위치", 71),
    "Grilled Salmon": ("연어구이", 0),
    "Guacamole": ("과카몰리", 10),
    "Gyoza": ("교자(일본식 만두)", 38),
    "Hamburger": ("햄버거", 66),
    "Hot and Sour Soup": ("사천식 매운탕(신 라탕)", 35),
    "Hot Dog": ("핫도그", 62),
    "Huevos Rancheros": ("웨보스 란체로스(멕시코식 계란 요리)", 60),
    "Hummus": ("후무스", 13),
    "Ice Cream": ("아이스크림", 58),
    "Lasagna": ("라자냐", 50),
    "Lobster Bisque": ("랍스터 비스크(랍스터 크림 수프)", 37),
    "Lobster Roll Sandwich": ("랍스터 롤 샌드위치", 62),
    "Macaroni and Cheese": ("맥앤치즈(마카로니 앤 치즈)", 65),
    "Macarons": ("마카롱", 55),
    "Miso Soup": ("미소 된장국", 30),
    "Mussels": ("홍합찜", 0),
    "Nachos": ("나초", 65),
    "Omelette": ("오믈렛", 0),
    "Onion Rings": ("어니언 링", 75),
    "Oysters": ("굴", 0),
    "Pad Thai": ("팟타이", 65),
    "Paella": ("파에야(스페인식 해산물 볶음밥)", 57),
    "Pancakes": ("팬케이크", 46),
    "Panna Cotta": ("판나 코타", 35),
    "Peking Duck": ("베이징 덕(북경 오리구이)", 35),
    "Pho": ("쌀국수(포)", 52),
    "Pizza": ("피자", 80),
    "Pork Chop": ("포크찹(돼지갈비 스테이크)", 30),
    "Poutine": ("푸틴(캐나다식 감자튀김)", 64),
    "Prime Rib": ("프라임 립(소갈비 스테이크)", 5),
    "Pulled Pork Sandwich": ("풀드 포크 샌드위치(찢은 돼지고기 샌드위치)", 60),
    "Ramen": ("라멘(일본식 라면)", 50),
    "Ravioli": ("라비올리(이탈리아식 만두)", 50),
    "Red Velvet Cake": ("레드벨벳 케이크", 56),
    "Risotto": ("리소토", 65),
    "Samosa": ("사모사(인도식 튀김 만두)", 50),
    "Sashimi": ("사시미(회)", 0),
    "Scallops": ("가리비 요리", 0),
    "Seaweed Salad": ("해초 샐러드", 15),
    "Shrimp and Grits": ("새우와 그리츠(옥수수 죽)", 70),
    "Spaghetti Bolognese": ("스파게티 볼로네제(미트소스 스파게티)", 42),
    "Spaghetti Carbonara": ("스파게티 카르보나라", 42),
    "Spring Rolls": ("춘권(스프링 롤)", 62),
    "Steak": ("스테이크", 30),
    "Strawberry Shortcake": ("딸기 쇼트케이크", 56),
    "Sushi": ("초밥(스시)", 60),
    "Tacos": ("타코", 65),
    "Takoyaki": ("타코야키(문어볼)", 65),
    "Tiramisu": ("티라미수", 56),
    "Tuna Tartare": ("참치 타르타르", 10),
    "Waffles": ("와플", 76),

    # 필요하면 추가
}
food_list = sorted(list(food_dict.keys()))

# 모델 로드
model = load_model("model_trained3_extended4.h5")

# 제목
st.title("🍽️ 당뇨병 환자를 위한 음식 분류 모델")

# 이미지 업로더
uploaded_file = st.file_uploader("이미지를 업로드해주세요", type=["jpg", "png", "jpeg"])

# 이미지 처리 및 예측
if uploaded_file is not None:
    img_bytes = uploaded_file.getvalue()
    st.image(img_bytes, caption="업로드한 이미지", use_column_width=True)

    img = Image.open(uploaded_file)

    # 전처리
    img_resized = ImageOps.fit(img, (299, 299), Image.Resampling.LANCZOS)
    img_array = image.img_to_array(img_resized)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    
    # 예측
    pred = model.predict(img_array)

    # 상위 3개 클래스 가져오기
    top_3_indices = np.argsort(pred[0])[::-1][:3]  # 확률이 높은 순서대로 정렬된 인덱스
    top_3_results = [(food_list[i], pred[0][i] * 100) for i in top_3_indices]

    # 1순위 결과로 상세 정보 추출
    top1_class = top_3_results[0][0]
    korean_name, gi_value = food_dict.get(top1_class, ("알 수 없음", "-"))

    # GI 분류
    if gi_value != "-":
        gi_value = int(gi_value)
        if gi_value >= 70:
            gi_category = "(고GI 식품입니다.)"
            gi_color = 'red'
        elif 56 <= gi_value <= 69:
            gi_category = "(중간GI 식품입니다.)"
            gi_color = 'orange'
        else:
            gi_category = "(저GI 식품입니다.)"
            gi_color = 'green'
    else:
        gi_category = ""
        gi_color = 'black'

    result_text = f"{korean_name} ({top1_class})\n혈당 지수: {gi_value} {gi_category}"

    # Matplotlib 시각화
    fig, ax = plt.subplots()
    ax.imshow(img_resized)
    ax.axis('off')
    ax.set_title(result_text, color=gi_color, fontsize=14)
    st.pyplot(fig)

    # 예측 결과 출력
    st.success(f"✅ 예측 결과: {result_text}")

    # Top-3 예측 확률 출력
    st.subheader("📊 상위 3개 예측 결과")
    for rank, (label, confidence) in enumerate(top_3_results, start=1):
        kr_label = food_dict.get(label, ("알 수 없음", "-"))[0]
        st.write(f"{rank}위: {kr_label} ({label}) - {confidence:.2f}%")

else:
    st.info("👆 위에 이미지를 업로드해주세요.")
