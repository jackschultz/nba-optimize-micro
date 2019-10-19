from flask import Flask, jsonify

from webargs import fields, validate
from webargs.flaskparser import use_args

from optimizers import standard as optimize_standard

app = Flask(__name__)

optimize_args = {
    "date": fields.Date(required=True),
    "site": fields.String(require=True, validate=validate.OneOf(["fd"])),
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
    tops = optimize_standard(args['date'], site=args['site'])
    return jsonify(tops)

if __name__ == '__main__':
    app.run(debug=True)
