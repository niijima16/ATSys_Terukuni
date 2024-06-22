from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create user groups and users in MySQL and grant permissions'

    def handle(self, *args, **kwargs):
        # Define user groups and users
        user_groups = [
            {'group': 'group1', 'user': 'user1', 'password': 'password1'},
            {'group': 'group2', 'user': 'user2', 'password': 'password2'},
        ]

        # SQL statements
        create_user_sql = "CREATE USER IF NOT EXISTS '{user}'@'%' IDENTIFIED BY '{password}';"
        create_group_sql = "CREATE ROLE IF NOT EXISTS '{group}';"
        grant_role_sql = "GRANT '{group}' TO '{user}'@'%';"
        grant_permissions_sql = "GRANT SELECT, INSERT, UPDATE, DELETE ON your_database_name.* TO '{group}';"

        with connection.cursor() as cursor:
            for entry in user_groups:
                group = entry['group']
                user = entry['user']
                password = entry['password']

                # Create group
                cursor.execute(create_group_sql.format(group=group))
                # Create user
                cursor.execute(create_user_sql.format(user=user, password=password))
                # Assign user to group
                cursor.execute(grant_role_sql.format(group=group, user=user))
                # Grant permissions to group
                cursor.execute(grant_permissions_sql.format(group=group))

        self.stdout.write(self.style.SUCCESS('Successfully created user groups, users, and granted permissions'))
