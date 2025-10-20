import psycopg2
import os

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)
cursor = conn.cursor()

# 목동 관련 캠퍼스 검색
cursor.execute("""
    SELECT DISTINCT client_name_kr 
    FROM voca_wordit.tb_cla_client 
    WHERE client_name_kr LIKE '%목동%' 
    ORDER BY client_name_kr
""")

print('목동 관련 캠퍼스:')
for row in cursor.fetchall():
    print(f'  - {row[0]}')

cursor.close()
conn.close()
