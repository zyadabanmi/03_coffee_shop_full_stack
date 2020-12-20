import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
 
 
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    try:
      dri = [drink.short() for drink in Drink.query.all()]
      return jsonify({
        "successd": True,
        "drinks": dri
    })
    except:
        abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def get_drinks_details(item):
    try:
      dri = [drink.long() for drink in Drink.query.all()]
      return jsonify({
        "success": True,
        "drinks": dri
    })
    except:
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(item):
     try:
         new_drink = request.get_json()
         dri = Drink(new_drink['title'], json.dumps(new_drink['recipe']))
         dri.insert()
         return jsonify({
        'success': True,
        'drinks': [dri.long()]
      })
     except:
         abort(AuthError)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(item, drink_id):
     print(request.get_json())
     updated_drink = request.get_json()
     dri = Drink.query.filter(Drink.id == drink_id).one_or_none()
     if dri is None:
           abort(404)
           
     dri.title = updated_drink['title'] if updated_drink['title'] else dri.title
     dri.update()
     
     return jsonify({
        'success': True,
        'drinks': [dri.long()]
      })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(item, drink_id):
     dri = Drink.query.filter(Drink.id == drink_id).one_or_none()
     if dri is None:
           abort(404)
     dri.delete()
     return jsonify({
        'success': True,
        'delete': drink_id
      })


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(400)
def bad_request(error):
      return jsonify({'success': False,'error': 400,'message': 'Bad request'}), 400
      
@app.errorhandler(404)
def not_found(error):
      return jsonify({'success': False,'error': 404,'message': 'resource not found'}), 404
      
@app.errorhandler(422)
def unprocessable_entity(error):
      return jsonify({'success': False,'error': 422,'message': 'unprocessable entity'}), 422
  
@app.errorhandler(500)
def internal_server_error(error):
      return jsonify({'success': False,'error': 500,'message': 'Internal server error'}), 500

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''



'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def authError(AuthError):
    return jsonify({"success": False, "error": AuthError.status_code,"message": AuthError.error}), AuthError.status_code

