# SQL AI Agent for Analytics in Odoo
## Config cho Chatbot   
Ta thêm dữ liệu vào bảng *res.config.settings* trong file ```res_config_settings.py```

![Configuration](assets/config.jfif)

## Nhận prompt từ người dùng và gửi lại answer

![Config use](assets/setup_from_config.jfif)

Chatbot không được nhận tin nhắn từ bản thân và phải nhận tin nhắn từ chat riêng tư. 

![Mesage setup](assets/prompt_setup.jfif)

Gọi chatbot và đẩy tin nhắn xuống cơ sở dữ liệu

![Call chatbot and receive answer](assets/call_post_answer.jfif)

## Phía chatbot (AI Agent)

<img width="1193" height="842" alt="image" src="https://github.com/user-attachments/assets/29ca9e1b-65e1-45b1-bffd-a21efd038823" />

Tạo config để gọi chatbot từ Mistral AI, cho chatbot kết nối với cơ sở dữ liệu thông qua user (set up trên pgadmin) chỉ được quyền đọc (tránh nguy cơ chatbot vô tình thay đổi database) trên cơ sở dữ liệu
và giới hạn các bảng mà chatbot có thể đọc.

<img width="1155" height="880" alt="image" src="https://github.com/user-attachments/assets/0b52945b-99ea-476f-b416-9d520f49853c" />
<img width="1121" height="328" alt="image" src="https://github.com/user-attachments/assets/333fc7c7-ed71-4d2f-8889-475b1a4aff3d" />

Sử dụng SQL toolkit từ Langchain để tạo ra AI Agent có khả năng viết query và đọc kết quả từ Database.

<img width="955" height="574" alt="image" src="https://github.com/user-attachments/assets/1b5f9dc4-0c4a-401a-8b2b-0b2521569490" />

Viết endpoint cho Agent để Odoo gọi tới.

<img width="1113" height="419" alt="image" src="https://github.com/user-attachments/assets/7186aa2d-1873-47ad-99ec-89e3c8de2988" />

<img width="665" height="706" alt="image" src="https://github.com/user-attachments/assets/b753967b-44fe-4562-8049-2b610b9f8c24" />



