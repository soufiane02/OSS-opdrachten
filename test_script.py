#!/usr/bin/python3
import csv
import argparse
import subprocess

def create_users(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Openen van de CSV file
            student_id = row['studentid']
            full_name = row['full name']
            email = row['email']
            class_group = row['class group']
            password = row['password']
            ssh_public_key = row['ssh public key']
            username = 's' + student_id
            home_directory = '/home/' + email.split('@')[0]

            # Controleer of de users al bestaan
            if check_user_exists(username):
                print(f"Gebruiker '{username}' bestaat al. ")
                continue

            # Maak de gebruiker aan met behulp van useradd command
            subprocess.run(['useradd', '-m', '-d', home_directory, username])

            # Het wachtwoord configureren als deze is gegeven het CSV bestand
            if password:
                subprocess.run(['chpasswd'], input=f"{username}:{password}\n", encoding='utf-8', check=True)

            # De gebruikers toevoegen aan de groep 'Students'
            add_user_to_group(username, 'students')

            # De gebruikers toevoegen aan de specifieke klasgroep die in het CSV bestand staan
            add_user_to_group(username, class_group)

            # De SSH public keys toevoegen aan het authorized_keys bestand
            if ssh_public_key:
                add_ssh_public_key(username, ssh_public_key)


def create_group(group_name, user_file=None):
    # Controleren of de groep bestaat
    if check_group_exists(group_name):
        print(f"Groep '{group_name}' Bestaat al.")
    else:
        # Maakt de groep door behulp van het groupadd command 
        subprocess.run(['groupadd', group_name])

    # Voeg de gebruikers toe aan de groep
    if user_file:
        with open(user_file, 'r') as file:
            for line in file:
                user = line.strip()
                add_user_to_group(user, group_name)
    else:
        print("Geen gebruiker gespecificeerd.")


def delete_users(user_file, interactive=False):
    # Inlezen van de txt file met de gebruikers opgesomd (in mijn geval is dit usernames.txt)
    with open(user_file, 'r') as file:
        users_to_delete = [line.strip() for line in file if line.strip()]

    # Print een lijst van de gebruikers
    print("Gebruikers om te verwijderen")
    for user in users_to_delete:
        print(user)

    # Bevestig bij elke gebruiker of deze moet verwijderd worden in geval van -d -i
    if interactive:
        choice = input("Wilt u deze gebruiker verwijderen? (y/n): ")
        if choice.lower() != 'y':
            print("Verwijderen van gebruikers is stop gezet.")
            return

    # Verwijder de gebruikers
    for user in users_to_delete:
        choice = input(f"Wilt u de gebruiker '{user}' verwijderen? (y/n): ")
        if choice.lower() == 'y':
            subprocess.run(['userdel', '-r', user])
            print(f"Gebruiker '{user}' verwijderd.")
        else:
            print(f"Gebruiker '{user}' niet verwijderd.")

# functie die controleert of de gebruiker bestaat
def check_user_exists(username):
    try:
        subprocess.run(['id', username], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# functie die controleert of de groep bestaat
def check_group_exists(group_name):
    try:
        subprocess.run(['getent', 'group', group_name], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# functie die de gebruiker toevoegt aan de groep
def add_user_to_group(username, group_name):
    # Controleer of de group reeds bestaat
    if not check_group_exists(group_name):
        # Maak de groep als deze niet bestaat
        subprocess.run(['groupadd', group_name], check=True)

    # Toevoegen van de gebruiker aan de groep
    subprocess.run(['usermod', '-a', '-G', group_name, username], check=True)

# functie die de ssh directory en een bestand authorized_keys aanmaakt en daar in dan de public ssh key in write
def add_ssh_public_key(username, ssh_public_key):
    ssh_directory = f'/home/{username}/.ssh'
    authorized_keys_file = f'{ssh_directory}/authorized_keys'

    # Maak de .ssh-directory aan als deze niet bestaat
    subprocess.run(['mkdir', '-p', ssh_directory], check=True)

    # Voeg de openbare sleutel toe aan het bestand authorized_keys
    with open(authorized_keys_file, 'a') as file:
        file.write(ssh_public_key + '\n')


def get_users_to_delete():
    # Een list met de gebruikers die moeten worden verwijderd
    users_to_delete = []

    # List met de gebruikers in de Students groep
    students_group = 'students'
    try:
        output = subprocess.check_output(['getent', 'group', students_group]).decode().strip()
        users = output.split(':')[3].split(',')
        users_to_delete.extend(users)
    except subprocess.CalledProcessError:
        pass

    # List met alle usernames die beginnen met de letter 's'
    try:
        output = subprocess.check_output(['getent', 'passwd']).decode().strip()
        lines = output.split('\n')
        for line in lines:
            username = line.split(':')[0]
            if username.startswith('s'):
                users_to_delete.append(username)
    except subprocess.CalledProcessError:
        pass

    return users_to_delete


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-c', '--create')
group.add_argument('-g', '--group')
group.add_argument('-d', '--delete', nargs='?', const='usernames.txt')
parser.add_argument('-f', '--file')
parser.add_argument('-i', '--interactive', action='store_true')
args = parser.parse_args()

if args.create:
    create_users(args.create)
elif args.group:
    create_group(args.group, args.file)
elif args.delete:
    delete_users(args.delete, args.interactive)
