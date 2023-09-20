import os
import requests
import jinja2 # flask comes with this
from dotenv import load_dotenv # a separate process than app.py

load_dotenv()
domain = os.getenv("MAILGUN_DOMAIN")
template_loader = jinja2.FileSystemLoader("templates") # under the folder templates/
template_env = jinja2.Environment(loader=template_loader) # put variables into the template to render the template correctly

def render_template(template_filename, **variables): # variables as a dictionary (kwargs)
    return template_env.get_template(template_filename).render(**variables) # use get_template() to locate files


def send_simple_message(to, subject, body, html):
    return requests.post(
	    f"https://api.mailgun.net/v3/{domain}/messages",
		auth=("api", os.getenv("MAILGUN_API_KEY")),
		data={"from": f"Kalvin <mailgun@{domain}>",
			"to": [to],
			"subject": subject,
			"text": body,
            "html": html}
    )

# this is wrapper for a task in taskqueue
def send_email(email, username):
    # if not string, the object user(schema) will be turned into string using pickle 
    return send_simple_message(
        to=email, 
        subject='Successfully signed up the REST store', 
        body=f"Hi {username}, you have successfully signed up UwU",
        html=render_template("emails/action.html")
    )