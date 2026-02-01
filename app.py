import streamlit as st
from pypdf import PdfWriter, PdfReader
from PIL import Image, ImageOps
import io

# 페이지 설정
st.set_page_config(page_title="내 친구를 위한 PDF 병합기", page_icon="📑")

# 제목
st.title("📑 PDF & 이미지 합치기")
st.success("친구야, 설치할 필요 없이 여기서 파일만 올리면 돼! (폰/PC 겸용)")

# 파일 업로드
uploaded_files = st.file_uploader(
    "여기에 파일을 드래그하거나 선택하세요 (순서대로 합쳐집니다)", 
    type=["pdf", "png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"총 {len(uploaded_files)}개의 파일이 대기 중입니다.")
    
    # 합치기 버튼
    if st.button("✨ 합치기 실행 (클릭)", type="primary"):
        try:
            merger = PdfWriter()
            target_w, target_h = 595, 842 # 기본 A4
            
            # 1. 기준 크기 찾기 (첫번째 PDF 기준)
            for file in uploaded_files:
                if file.name.lower().endswith(".pdf"):
                    reader = PdfReader(file)
                    if len(reader.pages) > 0:
                        box = reader.pages[0].mediabox
                        target_w, target_h = int(box.width), int(box.height)
                        break
            
            # 2. 병합 시작
            progress_text = "작업 진행 중..."
            my_bar = st.progress(0, text=progress_text)
            
            for i, file in enumerate(uploaded_files):
                ext = file.name.split('.')[-1].lower()
                
                if ext == 'pdf':
                    merger.append(file)
                
                elif ext in ['png', 'jpg', 'jpeg']:
                    img = Image.open(file).convert('RGB')
                    # 캔버스 생성 및 이미지 중앙 정렬
                    canvas = Image.new('RGB', (target_w, target_h), (255, 255, 255))
                    img_fitted = ImageOps.contain(img, (target_w, target_h))
                    
                    paste_x = (target_w - img_fitted.width) // 2
                    paste_y = (target_h - img_fitted.height) // 2
                    canvas.paste(img_fitted, (paste_x, paste_y))
                    
                    # PDF 변환 후 병합
                    img_bytes = io.BytesIO()
                    canvas.save(img_bytes, format='PDF')
                    merger.append(img_bytes)
                
                # 진행률 바 업데이트
                my_bar.progress((i + 1) / len(uploaded_files), text=progress_text)

            # 3. 결과 저장 및 다운로드 버튼 생성
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            my_bar.empty() # 진행바 숨기기
            
            st.balloons() # 풍선 효과 🎉
            st.success("완료되었습니다! 아래 버튼을 눌러 저장하세요.")
            
            st.download_button(
                label="📥 합쳐진 PDF 다운로드",
                data=output.getvalue(),
                file_name="merged_result.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"오류가 발생했어요: {e}")