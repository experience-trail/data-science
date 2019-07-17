import argparse
from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView
import os

# Inner imports
from src.graphql.schemas import schema

# Create and configure an instance of the Flask application.
application = app = Flask(__name__)
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY", default=False)
CORS(app)

application.add_url_rule('/graphql',
                         view_func=GraphQLView.as_view('graphql',
                                                       schema=schema,
                                                       graphiql=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("""
    Creates a flask.Flask instance and runs it. Parses
    command-line flags to configure the app.
    """)
    msg = 'Hostname of Flask app [{}]'.format("0.0.0.0")
    parser.add_argument("-H", "--host",
                        help=msg,
                        default="0.0.0.0")
    msg = 'Port for Flask app [{}]'.format("80")
    parser.add_argument("-P", "--port",
                        help=msg,
                        default="5000")
    parser.add_argument("-d", "--debug",
                        action="store_true", dest="debug")

    args = parser.parse_args()

    app.run(
        debug=args.debug,
        host=args.host,
        port=int(args.port)
    )
