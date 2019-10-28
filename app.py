from flask import Flask, jsonify, abort

from webargs import fields, validate
from webargs.flaskparser import use_args


from optimizers import standard as optimize_standard, OptimizeError

app = Flask(__name__)

version_types = ['0.1-avg-05', '0.1-avg-08', '0.1-std-ceil-05']

optimize_args = {
    "date":    fields.Date(required=True),
    "site":    fields.String(require=True, validate=validate.OneOf(["fd"])),
    "exclude": fields.List(fields.Int(), missing=[]),
    "include": fields.List(fields.Int(), missing=[]),
    "version": fields.String(require=True, validate=validate.OneOf(version_types)),
}


# Return validation errors as JSON
@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code


@app.errorhandler(OptimizeError)
def optimize_error_handler(err):
    return jsonify({"errors": err.errvals}), err.code


@app.route('/optimize')
@use_args(optimize_args)
def optimize(args):
    try:
        tops = optimize_standard(args['date'], projection_version=args['version'],
                                 site=args['site'], exclude=args['exclude'], include=args['include'])
    except OptimizeError as err:
        raise err
    else:
        return jsonify(tops)


if __name__ == '__main__':
    app.run(debug=True)
