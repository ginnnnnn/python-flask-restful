from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from security import authenticate, identity

app = Flask(__name__)
# secret_key is for JWT
app.secret_key = 'jose'
api = Api(app)
jwt = JWT(app, authenticate, identity)  # /auth

items = []


# for get post put delete item


class Item(Resource):
    # this is the validator in flask ,which validate request body by add requirment args
    parser = reqparse.RequestParser()
    # if request has other arguments not added here, it won't show in data (parser.parse_args())
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="this field can not be left blank"
                        )

    @jwt_required()
    def get(self, name):
        # target is an filter object
        target = next(filter(lambda item: item["name"] == name, items), None)
        return target, 200 if target else 404

    @jwt_required()
    def post(self, name):
      # .get_json(force=True) will not check the content-type equal to json
      # .get_json(silce=True) will not return error if request body is not json but it return none
        if next(filter(lambda item: item["name"] == name, items), None) is not None:
          # 400 is bad request
            return {'message': f"An item with '{name}' already exist."}, 400
        data = Item.parser.parse_args()
        # data = request.get_json()
        item = {'name': name, 'price': data["price"]}
        items.append(item)
        # 201 new content created,202 request accepted means content take time to be created
        return item, 201

    @jwt_required()
    def delete(self, name):
      # filter out name exist
        global items
        updated_items = list(filter(lambda item: item["name"] != name, items))
        items = updated_items
        return {"message": "item deleted!"}

    @jwt_required()
    def put(self, name):

        data = Item.parser.parse_args()
        target = next(filter(lambda item: item["name"] == name, items), None)
        if target is None:
          # create one
            to_add_item = {"name": name, "price": data["price"]}
            items.append(to_add_item)
            return to_add_item
        else:
            target.update(data)
            return target

            # for get items


class ItemList(Resource):
    def get(self):
        return items


# http://120.0.0.1:5000/student/Rolf
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')


app.run(port=5000, debug=True)
