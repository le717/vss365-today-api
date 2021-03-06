from requests import codes
from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import subscription
from src.core import database, helpers
from src.core.auth_helpers import authorize_route
from src.core.email import mailgun


@subscription.route("/", methods=["POST"])
@use_args({"email": fields.Email(required=True)}, location="query")
def post(args: dict):
    """Add an email to the mailing list."""
    # Add the address to the local database and Mailgun mailing list
    db_result = database.subscription.email_create(args["email"])
    mg_result = mailgun.subscription_email_create(args["email"])

    # The address was successfully recorded
    if db_result and (mg_result.status_code == codes.ok):
        return helpers.make_response(201)

    # ...Welllllll... actually it didn't...
    return helpers.make_error_response(503, "Unable to add email to mailing list!")


@authorize_route
@subscription.route("/", methods=["DELETE"])
@use_args({"email": fields.Email(required=True)}, location="query")
def delete(args: dict):
    """Remove an email from the mailing list."""
    mailgun.subscription_email_delete(args["email"])
    database.subscription.email_delete(args["email"])
    return helpers.make_response(204)
