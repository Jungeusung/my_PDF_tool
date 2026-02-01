import streamlit as st
from pypdf import PdfWriter, PdfReader
from PIL import Image, ImageOps
import io
from streamlit_sortables import sort_items # 순서 변경 도구 추가

# --- 페이지 설정 ---
st.set_page_config(page_title="드래그로 순서 변경", page_icon="🖱️")

st.title("🖱️ 진짜 PC처럼 합치기")
st.success("파일을 올린 뒤, 아래 생긴 박스를 마우스로 잡아 끌어서 순서를 바꾸세요!")

# --- 1. 파일 업로드 ---
uploaded_files = st.file_uploader(
    "파일 추가 (여러 개 선택 가능)", 
    type=["pdf", "png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    # 파일명과 실제 파일을 연결하는 딕셔너리 생성
    file_dict = {file.name: file for file in uploaded_files}
    original_filenames = list(file_dict.keys())
    
    st.write("---")
    st.subheader("📋 순서 변경 (드래그 앤 드롭)")
    
    # --- 2. 드래그 앤 드롭 인터페이스 (핵심 기능) ---
    # 마우스로 끌어서 순서를 바꿀 수 있는 리스트를 만듭니다.
    sorted_filenames = sort_items(original_filenames)

    # --- 3. 병합 실행 ---
    if st.button("✨ 이 순서대로 합치기", type="primary"):
        try:
            merger = PdfWriter()
            target_w, target_h = 595, 842 # 기본 A4
            
            # 기준 크기 잡기 (첫 번째 PDF 기준)
            for name in sorted_filenames:
                file = file_dict[name]
                if file.name.lower().endswith(".pdf"):
                    reader = PdfReader(file)
                    if len(reader.pages) > 0:
                        box = reader.pages[0].mediabox
                        target_w, target_h = int(box.width), int(box.height)
                        break
            
            # 진행바
            progress_text = "작업 중..."
            my_bar = st.progress(0, text=progress_text)
            
            # 사용자가 정한 순서(sorted_filenames)대로 합치기
            for i, name in enumerate(sorted_filenames):
                file = file_dict[name]
                file.seek(0) # 파일 초기화
                
                ext = name.split('.')[-1].lower()
                
                if ext == 'pdf':
                    merger.append(file)
                
                elif ext in ['png', 'jpg', 'jpeg']:
                    img = Image.open(file).convert('RGB')
                    canvas = Image.new('RGB', (target_w, target_h), (255, 255, 255))
                    img_fitted = ImageOps.contain(img, (target_w, target_h))
                    
                    paste_x = (target_w - img_fitted.width) // 2
                    paste_y = (target_h - img_fitted.height) // 2
                    canvas.paste(img_fitted, (paste_x, paste_y))
                    
                    img_bytes = io.BytesIO()
                    canvas.save(img_bytes, format='PDF')
                    merger.append(img_bytes)
                
                my_bar.progress((i + 1) / len(sorted_filenames), text=progress_text)

            # 결과 저장
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            my_bar.empty()
            
            st.balloons()
            st.success("완료! 순서대로 합쳐졌습니다.")
            
            st.download_button(
                label="📥 다운로드",
                data=output.getvalue(),
                file_name="merged_result.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"오류: {e}")
