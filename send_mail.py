import smtplib
from email.mime.text import MIMEText


def send_mail(student_id, selected_subject,rating,comments):
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = '7a18a790ef9b5d'
    password = 'd69ed8a44906d7'
    message = f"<h3>New Feedback Submission</h3> <ul>\
        <li>student_id : {student_id}</li>\
        <li>selected_subject : {selected_subject}</li>\
        <li>rating : {rating}</li>\
        <li>comments : {comments}</li>\</ul>"

    sender_email = 'libertycrown@gmail.com'
    receiver_email = 'libertycrown@gmail.com'
    msg = MIMEText(message, 'html')
    msg['Subject'] = 'Subject Feedback'
    msg['From']  = sender_email
    msg['To'] = receiver_email

    #send email
    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
