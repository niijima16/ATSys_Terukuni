-- Create the group (role)
CREATE ROLE IF NOT EXISTS 'DEV_G';

-- Create the user and assign the password
CREATE USER IF NOT EXISTS 'dev01'@'%' IDENTIFIED BY 'dev01';

-- Grant the role to the user
GRANT 'DEV_G' TO 'dev01'@'%';

-- Grant administrative privileges to the group
GRANT ALL PRIVILEGES ON *.* TO 'DEV_G' WITH GRANT OPTION;

-- Apply the changes
FLUSH PRIVILEGES;