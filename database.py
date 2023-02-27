# import psycopg2
# from config import localhost, user, db_name, password
#
# try:
#     connection = psycopg2.connect(
#         host=localhost,
#         user=user,
#         password=password,
#         database=db_name
#     )
#     # cursor = connection.cursor()
#     # with connection.cursor() as cursor:
#     #     cursor.execute("""SELECT version()""")
#     #     print(cursor.fetchall())
# except Exception as ex:
#     print('[INFO] error', ex)
#
#
#
#
#
# def user_question():
#     with connection.cursor() as cursor:
#         cursor.execute('''CREATE TABLE IF NOT EXISTS user_question(
#         message_id serial PRIMARY KEY ,
#         user_id bigint references users(user_id),
#         question VARCHAR(20000),
#         chat_id bigint references users(chat_id),
#         qabul int DEFAULT 0,
#         answer int DEFAULT 0
#
#         )''')
#         connection.commit()
#
#
# user_question()