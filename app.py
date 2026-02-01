import streamlit as st
from pypdf import PdfWriter, PdfReader
from PIL import Image, ImageOps
import io

# --- 페이지 설정 ---
st.set_page_config(page_title="순서 변경 가능한 PDF 병합기", page_icon="📑")

st.title("📑 PDF & 이미지 합치기 (순서 변경 가능)")
st.info("파일을 업로드한 뒤, 아래 '순서 지정 박스'에서 순서를 바꿀 수 있습니다.")

# --- 1. 파일 업로드 ---
uploaded_files = st.file_uploader(
    "여기에 파일을 드래그하거나 선택하세요", 
    type=["pdf", "png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    # 파일명과 파일 객체를 매칭하는 딕셔너리 생성
    file_dict = {file.name: file for file in uploaded_files}
    
    # --- 2. 순서 변경 기능 (핵심) ---
    st.write("---")
    st.subheader("🔄 병합 순서 확인 및 변경")
    st.caption("아래 박스 안의 이름 순서대로 합쳐집니다. 순서를 바꾸려면 x를 눌러 뺐다가 원하는 순서대로 다시 선택하세요.")
    
    # 멀티셀렉트 박스를 통해 순서 재배열
    selected_order = st.multiselect(
        "최종 병합 순서:",
        options=file_dict.keys(),
        default=file_dict.keys() # 기본값은 업로드 순서
    )
    
    # --- 3. 병합 실행 ---
    if st.button("✨ 이 순서대로 합치기", type="primary"):
        if not selected_order:
            st.warning("합칠 파일이 선택되지 않았습니다.")
        else:
            try:
                merger = PdfWriter()
                target_w, target_h = 595, 842 # 기본 A4
                
                # 기준 크기 잡기 (선택된 파일 중 첫 번째 PDF 기준)
                for name in selected_order:
                    file = file_dict[name]
                    if file.name.lower().endswith(".pdf"):
                        reader = PdfReader(file)
                        if len(reader.pages) > 0:
                            box = reader.pages[0].mediabox
                            target_w, target_h = int(box.width), int(box.height)
                            break
                
                # 진행률 바
                progress_text = "파일 합치는 중..."
                my_bar = st.progress(0, text=progress_text)
                
                # 사용자가 지정한 순서(selected_order)대로 반복
                for i, name in enumerate(selected_order):
                    file = file_dict[name]
                    file.seek(0) # 파일 포인터 초기화 (중요)
                    
                    ext = name.split('.')[-1].lower()
                    
                    if ext == 'pdf':
                        merger.append(file)
                    
                    elif ext in ['png', 'jpg', 'jpeg']:
                        img = Image.open(file).convert('RGB')
                        # 캔버스 생성 및 중앙 정렬
                        canvas = Image.new('RGB', (target_w, target_h), (255, 255, 255))
                        img_fitted = ImageOps.contain(img, (target_w, target_h))
                        
                        paste_x = (target_w - img_fitted.width) // 2
                        paste_y = (target_h - img_fitted.height) // 2
                        canvas.paste(img_fitted, (paste_x, paste_y))
                        
                        img_bytes = io.BytesIO()
                        canvas.save(img_bytes, format='PDF')
                        merger.append(img_bytes)
                    
                    # 진행률 업데이트
                    my_bar.progress((i + 1) / len(selected_order), text=progress_text)

                # 결과 저장
                output = io.BytesIO()
                merger.write(output)
                merger.close()
                my_bar.empty()
                
                st.balloons()
                st.success("완료! 순서대로 합쳐졌습니다.")
                
                st.download_button(
                    label="📥 결과물 다운로드",
                    data=output.getvalue(),
                    file_name="merged_ordered.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
