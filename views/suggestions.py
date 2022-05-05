from flask import Response, request
from flask_restful import Resource
from models import User
from views import get_authorized_user_ids
import json
from sqlalchemy import and_

class SuggestionsListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # suggestions should be any user with an ID that's not in this list:
        # print(get_authorized_user_ids(self.current_user))
        authorized_users = get_authorized_user_ids(self.current_user)
        suggestions = User.query.filter(and_(User.id!=self.current_user.id, User.id.not_in(authorized_users))).limit(7).all()
        data = [suggestion.to_dict() for suggestion in suggestions] 
        return Response(json.dumps(data), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        SuggestionsListEndpoint, 
        '/api/suggestions', 
        '/api/suggestions/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
