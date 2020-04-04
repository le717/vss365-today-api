from flask import jsonify

from webargs import fields
from webargs.flaskparser import use_args

from src.blueprints import subscription
from src.core import database, email, helpers


# TODO This needs to be protected via @authorize_route
@subscription.route("/", methods=["GET"])
def get():
    """Retrieve the entire mailing list."""
    mailing_list = database.subscription_list_get()
    if mailing_list:
        return helpers.make_response(200, jsonify(mailing_list))
    return helpers.make_error_response(503, "Unable to get mailing list!")


@subscription.route("/", methods=["POST"])
@use_args({"email": fields.Email(required=True)}, location="query")
def post(args: dict):
    """Add an email to the mailing list."""
    result = database.subscription_email_create(args["email"])
    if result:
        return helpers.make_response(201)
    return helpers.make_error_response(503, "Unable to add email to mailing list!")


@subscription.route("/", methods=["DELETE"])
@use_args({"email": fields.Email(required=True)}, location="query")
def delete(args: dict):
    """Remove an email from the mailing list."""
    database.subscription_email_delete(args["email"])
    return helpers.make_response(204)


# TODO This needs to be protected via @authorize_route
@subscription.route("/broadcast/", methods=["POST"])
@use_args({"date": fields.DateTime()}, location="query")
def broadcast(args: dict):
    """Trigger an email broadcast for the given day's prompt."""
    # Put the date in the proper format
    date = helpers.format_datetime_iso(args["date"])

    # A prompt for that date doesn't exist
    prompt = database.prompts_get_by_date(date, date_range=False)
    if not prompt:
        return helpers.make_error_response(
            503, f"Unable to send out email broadcast for the {date} prompt!"
        )

    # Get the mailing list
    mailing_list = database.subscription_list_get()

    #  We couldn't get the mailing list
    if not mailing_list:
        return helpers.make_error_response(
            503, f"Unable to send email broadcast for date {args['date']}!"
        )

    # Render out the email template once
    email_content = email.render("email", **prompt[0])

    # Batch send out the emails
    # NOTE: According to the MG docs,
    # "The maximum number of recipients allowed for Batch Sending is 1,000."
    # This code may need to be updated to support that,
    # though hopefully that won't need to happen too soon
    email_msgs = email.batch_construct(
        mailing_list, helpers.format_datetime_pretty(prompt[0].date), email_content
    )
    email.send(email_msgs)

    # There's no easy way to tell if they all sent, so just pretend they did
    # TODO No easy way until I add some number tracking, that is
    return helpers.make_response(200)
