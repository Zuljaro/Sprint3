# Demo Flask
This project uses Python 3.6.
se debe instalar anaconda y en el promt de ella escribir
conda create -n ambiente_flask python=3.6.9  // crea ambiente
conda activate ambiente_flask   // activo el ambiente

## Dependencies
To install the required dependencies, please follow these steps:
se cambia en los requirements la dataclass == 0.6

1. Open a console.
2. Go to the project directory (with `cd` command).
3. Write and execute `pip3 install -r requirements.txt`.

## Initializate DB
To run the app, you need to provide a Microsoft account for the app to send/receive emails. To add this account follow these steps:

1. Open the file `schema.sql`.
2. Locate the line `INSERT INTO credentials (name,user,password) VALUES ('EMAIL_APP','developmentcapstone', '$TR41NC0URS3R4$')`.
3. Replace `developmentcapstone` with the email address.
4. Replace `$TR41NC0URS3R4$` with a password to access the email account.
5. Run `flask init-db` on the project directory.

## Run application
For run the app you need to use `flask run` on the project directory.
