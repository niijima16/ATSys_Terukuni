from django.core.management.base import BaseCommand
from django.db import connection, DatabaseError


class Command(BaseCommand):
    help = 'Create user groups and users in MySQL and grant permissions'

    def handle(self, *args, **kwargs):
        # Define the user group and user
        user_groups = [
            {'group': 'DEV_G', 'user': 'dev01', 'password': 'dev01'},
        ]

        # SQL statements
        create_user_sql = "CREATE USER IF NOT EXISTS '{user}'@'%' IDENTIFIED BY '{password}';"
        create_group_sql = "CREATE ROLE IF NOT EXISTS '{group}';"
        grant_role_sql = "GRANT '{group}' TO '{user}'@'%';"
        grant_permissions_sql = "GRANT SELECT, INSERT, UPDATE, DELETE ON `django-db`.* TO '{group}';"

        with connection.cursor() as cursor:
            for entry in user_groups:
                group = entry['group']
                user = entry['user']
                password = entry['password']

                try:
                    # Create group
                    cursor.execute(create_group_sql.format(group=group))
                    # Create user
                    cursor.execute(create_user_sql.format(user=user, password=password))
                    # Assign user to group
                    cursor.execute(grant_role_sql.format(group=group, user=user))
                    # Grant permissions to group
                    cursor.execute(grant_permissions_sql.format(group=group))
                except DatabaseError as e:
                    self.stdout.write(self.style.ERROR(f"Error occurred: {e}"))

        self.stdout.write(self.style.SUCCESS('Successfully created user groups, users, and granted permissions'))