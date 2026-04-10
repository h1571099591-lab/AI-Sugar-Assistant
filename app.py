import streamlit as st
import base64
from openai import OpenAI
from dotenv import load_dotenv
import os

# 1. 加载 .env 文件中的API密钥
api_key = st.secrets["SILICONFLOW_API_KEY"]

# 2. 初始化硅基流动的客户端
client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")

# 3. 设置网页标题
st.set_page_config(page_title="AI控糖助手", page_icon="🥗")
st.title("🥗 AI控糖助手")
st.caption("拍照识别食物，获取热量分析和控糖建议")

# 4. 创建文件上传组件
uploaded_file = st.file_uploader("上传你的餐食照片", type=["jpg", "jpeg", "png"])

# 5. 核心逻辑：如果用户上传了照片，就进行分析
if uploaded_file is not None:
    # 显示上传的图片
    st.image(uploaded_file, caption='上传的餐食', use_container_width=True)
    
    with st.spinner('AI营养师正在分析中，请稍等...'):
        try:
            # 读取图片并转为 Base64 格式
            img_bytes = uploaded_file.read()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # 构造发送给大模型的消息
            response = client.chat.completions.create(
                model="Qwen/Qwen2.5-VL-72B-Instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": """
                                请分析这张餐食图片，并严格按照以下 JSON 格式返回结果：
                                {
                                    "food_items": [{"name": "食物名称", "calories_kcal": 预估热量(kcal)}],
                                    "total_calories": 总热量,
                                    "is_diabetic_friendly": true/false,
                                    "analysis": "简短的分析",
                                    "suggestion": "一条具体的、可执行的控糖饮食建议"
                                }
                                """
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            # 解析返回的内容并展示
            result_text = response.choices[0].message.content
            st.success("分析完成！")
            st.markdown(result_text)
            
            # 添加医学依据引用
            with st.expander("📖 医学依据与免责声明"):
                st.markdown("""
                - 热量估算参考《中国食物成分表》。
                - 控糖建议参考《中国2型糖尿病防治指南》。
                - ⚠️ 本结果由AI生成，仅供参考，不能替代专业医生的诊断和治疗建议。
                """)
                
        except Exception as e:
            st.error(f"哎呀，分析出错了: {e}")
