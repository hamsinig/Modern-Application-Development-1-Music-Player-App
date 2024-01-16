# Importing the create_app function from the website package
from website import create_app

# Creating the Flask app using the create_app function
app = create_app()

# Checking if the script is being run directly (not imported)
if __name__ == '__main__':
    # Running the app in debug mode
    app.run(debug=True)
