from django.core.mail import EmailMultiAlternatives

def send(subject, text_content, html_content, to='james.bryan@kimley-horn.com'):
    from_email = 'council-insights@my-practice.herokuapp.com'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
