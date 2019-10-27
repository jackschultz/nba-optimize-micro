from flask import Flask, jsonify

from webargs import fields, validate
from webargs.flaskparser import use_args

from optimizers import standard as optimize_standard

app = Flask(__name__)

version_types = ['0.1-avg-5', '0.1-avg-8']

optimize_args = {
    "date":    fields.Date(required=True),
    "site":    fields.String(require=True, validate=validate.OneOf(["fd"])),
    "exclude": fields.List(fields.Int(), missing=[]),
    "include": fields.List(fields.Int(), missing=[]),
    "version": fields.String(require=True, validate=validate.OneOf(version_types)),
    }

@app.errorhandler(422)
def handle_unprocessable_entity(err):
    exc = getattr(err, 'exc')
    if exc:
        messages = exc.messages
    else:
        messages = ['Invalid request']
    return jsonify({
        'status': 'error',
        'result': messages
        }), 422

@app.route('/optimize')
@use_args(optimize_args)
def optimize(args):
    tops = optimize_standard(args['date'], projection_version=args['version'], site=args['site'], exclude=args['exclude'], include=args['include'])
    return jsonify(tops)

if __name__ == '__main__':
    app.run(debug=True)
