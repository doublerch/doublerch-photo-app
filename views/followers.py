from flask import Response, request
from flask_restful import Resource
from models import Following
import json
from views import get_authorized_user_ids
# from tests.utils import get_authorized_user_ids

def get_path():
    return request.host_url + 'api/posts/'

class FollowerListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        '''
        People who are following the current user.
        In other words, select user_id where following_id = current_user.id
        '''
        authorized_users = get_authorized_user_ids(self.current_user)
        followers = Following.query.filter(Following.following_id == self.current_user.id).all()
        # data = []
        #Need to check duplicates and authorized users?
        # existing_follower_ids = []
        # for follower in followers:
        #     if follower.id in authorized_users:
        #     # if follower.id not in existing_follower_ids and follower.id in authorized_users:
        #         data.append(follower.to_dict_follower())
            # existing_follower_ids.append(follower.id)

        data = [follower.to_dict_follower() for follower in followers] 
        return Response(json.dumps(data), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        FollowerListEndpoint, 
        '/api/followers', 
        '/api/followers/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
