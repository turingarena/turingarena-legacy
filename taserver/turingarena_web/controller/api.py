from flask import Blueprint, request, jsonify
from turingarena_web.model.contest import Contest
from turingarena_web.model.evaluate import evaluate
from turingarena_web.model.submission import Submission
from turingarena_web.model.user import User
from turingarena_web.controller.session import get_current_user, set_current_user

api_bp = Blueprint("api", __name__)


def error(status_code, message):
    response = jsonify(
        status=status_code,
        message=message,
    )
    response.status_code = status_code
    return response


@api_bp.route("/events", methods=("POST",))
def evaluation_event():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    if "id" not in args:
        return error(400, "you must specify a submission id")

    user = get_current_user()
    if user is None:
        return error(401, "authentication required")

    submission = Submission.from_id(args["id"])

    if submission is None:
        return error(400, "you provided an invalid submission id")

    if submission.user != user:
        return error(403, "you are trying to access a submission that is not yours")

    after = 0
    if "after" in args:
        after = args["after"]
        if not isinstance(after, int):
            return error(400, "the after parameter must be an integer")

    events = [
        event.as_json_data()
        for event in submission.events(after)
    ]

    return jsonify(events=events)


@api_bp.route("/submission", methods=("POST",))
def submission_api():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    user = get_current_user()
    if user is None:
        return error(401, "authentication required")

    if "id" not in args:
        return error(401, "missing required argument id")

    submission = Submission.from_id(args["id"])
    if submission is None:
        return error(404, f"no submission with id {args['id']}")

    if submission.user != user:
        return error(403, f"you are trying to get information on a submission that is not yours")

    return jsonify(submission.as_json_data())


@api_bp.route("/contest", methods=("POST",))
def contest_api():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    user = get_current_user()
    if user is None:
        return error(401, "authentication required")

    if "name" not in args:
        return error(400, "missing required parameter name")

    contest = Contest.contest(args["name"])

    if contest is None:
        return error(404, f"contest {args['name']} not found")

    if contest not in user.contests:
        return error(403, f"you have not the permission to view this contest")

    return jsonify(contest.as_json_data())


@api_bp.route("/problem", methods=("POST",))
def problem_api():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    user = get_current_user()
    if user is None:
        return error(401, "authentication required")

    if "name" not in args:
        return error(400, "missing required parameter name")
    if "contest" not in args:
        return error(400, "missing required parameter contest")

    contest = Contest.contest(args["contest"])
    if contest is None:
        return error(404, f"contest {args['contest']} not found")

    if contest not in user.contests:
        return error(403, f"you have not the permission to view this contest")

    problem = contest.problem(args["name"])
    if problem is None:
        return error(404, f"problem {args['name']} not found in contest {contest.name}")

    return jsonify(problem.as_json_data())


@api_bp.route("/evaluate", methods=("POST",))
def evaluate_api():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    user = get_current_user()
    if user is None:
        return error(401, "authentication required")

    if "problem" not in args:
        return error(400, "missing required parameter name")
    if "contest" not in args:
        return error(400, "missing required parameter contest")

    contest = Contest.contest(args["contest"])
    if contest is None:
        return error(404, f"contest {args['contest']} not found")

    if contest not in user.contests:
        return error(403, "you have not the permission to submit in this contest")

    problem = contest.problem(args["problem"])
    if problem is None:
        return error(404, f"problem {args['name']} not found in contest {contest.name}")

    if "files" not in args:
        return error(400, "missing parameter files")

    if not isinstance(args["files"], dict):
        return error(400, "files parameter must be a dict")

    files = args["files"]

    if "source" not in files:
        return error(400, "missing source file")

    source = files["source"]
    if not isinstance(source, dict):
        return error(400, "source parameter must be a dict")

    if "filename" not in source:
        return error(400, "missing filename for source file")
    if "content" not in source:
        return error(400, "missing content for source file")

    submission = evaluate(user, problem, contest, source)

    return jsonify(submission.as_json_data())


@api_bp.route("/user", methods=("POST",))
def user_api():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    if "username" not in args:
        return error(400, "missing required argument username")

    current_user = get_current_user()
    if current_user is None:
        return error(401, "authentication required")

    user = User.from_username(args["username"])
    if user is None:
        return error(404, f"user {args['username']} does not exist")

    if current_user != user:
        return error(403, f"you are trying to access information of another user")

    return jsonify(user.as_json_data())


@api_bp.route("/auth", methods=("POST",))
def auth_api():
    args = request.json
    if args is None:
        return error(400, "missing request JSON arguments")

    if "username" not in args:
        return error(400, "missing required parameter username")
    if "password" not in args:
        return error(400, "missing required parameter password")

    user = User.from_username(args["username"])
    if user is None or not user.check_password(args["password"]):
        return error(401, "wrong username or password")

    set_current_user(user)
    return jsonify(status="OK")
