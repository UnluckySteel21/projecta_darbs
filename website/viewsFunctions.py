from flask import session
from datetime import datetime

def writeToDoc(error):
    with open('documentation\errorMessages.txt', 'r') as file:
        content = file.read()

    with open('documentation\errorMessages.txt', 'w') as file:
        file.write('-'*30 + '\n')
        # Check if 'name' and 'surname' exist in the session
        name = session.get('name', 'Name not found')
        surname = session.get('surname', 'Surname not found')
        file.write(name + ' ' + surname + '\n')
        file.write(str(datetime.now()) + '\n')
        file.write(f'{error}')
        file.write('\n' + '-'*30)
        file.write(content)
