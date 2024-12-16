import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, render_template, request
import random

app = Flask(__name__, template_folder='templates')


def get_all_messages(url):
    messages = []
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            forum_container = soup.find(class_='block-body js-replyNewMessageContainer')
            articles = forum_container.find_all(class_="message message--post js-post js-inlineModContainer")

            for article in articles:
                username_element = article.find('a', class_="username")
                if username_element:
                    username = username_element.get_text(strip=True)
                else:
                    username = "לא נמצא משתמש"

                message_element = article.find('div', class_='bbWrapper')
                if message_element:
                    message = message_element.get_text(strip=True)
                else:
                    message = "לא נמצא תוכן"

                numbers = re.findall(r'\d+', message)
                number = numbers[0] if numbers else 'לא נמצא מספר'

                messages.append({
                    'username': username,
                    'number': number
                })

            next_page = soup.find('a', class_='pageNav-jump pageNav-jump--next')
            if next_page:
                url = 'https://www.prog.co.il' + next_page['href']
                print(url)
            else:
                url = None
        else:
            break
    return messages



@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    winner = ''
    if request.method == 'POST':
        url = request.form['url']
        results = get_all_messages(url)
        if 'draw' in request.form:
            draw_candidates = []
            excluded_users = request.form.getlist('exclude')  # משתמשים להסרה
            for result in results:
                if result['username'] not in excluded_users:  # לא להכניס משתמשים שהוסרו להגרלה
                    if result['number'] != 'לא נמצא מספר':
                        draw_candidates.extend(
                            [result['username']] * int(result['number']))  # הכנס את הניק לפי מספר הפעמים
                    else:
                        draw_candidates.append(result['username'])  # הכנס את הניק פעם אחת אם המספר לא נמצא
            if draw_candidates:
                print(draw_candidates)
                winner = random.choice(draw_candidates)  # בחר זוכה אקראי

    return render_template('index.html', results=results, winner=winner)


if __name__ == '__main__':
    app.run(debug=True)
