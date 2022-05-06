from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json
from views import get_authorized_user_ids
from sqlalchemy import and_
from views import can_view_post

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # return all of the "following" records that the current user is following
        authorized_users = get_authorized_user_ids(self.current_user)
        following = Following.query.filter(and_(Following.user_id==self.current_user.id, Following.user_id.in_(authorized_users))).all()
        data = [follow.to_dict_following() for follow in following] 

        return Response(json.dumps(data), mimetype="application/json", status=200)

    def post(self):
        # create a new "following" record based on the data posted in the body 
        body = request.get_json()
        try:
            uid = int(body.get('user_id'))
        except:
            return Response(json.dumps({'message': 'User id must be int'}), mimetype="application/json",status=400)
        # if not body.get('user_id') or not can_view_post(body.get('post_id'), self.current_user):

        authorized_users = get_authorized_user_ids(self.current_user)
        if body.get('user_id') in authorized_users:
            return Response(json.dumps({'message': 'already following user'}), mimetype="application/json", status=400)

        if not body.get('user_id') or not can_view_post(body.get('post_id'), self.current_user) and body.get('user_id') != self.current_user.id:
            return Response(json.dumps({'message': 'user not found'}), mimetype="application/json", status=404)

        # following = Following.query.filter(Following.user_id == self.current_user.id)
        # following = Following.query.filter(and_(Following.user_id==self.current_user.id, Following.user_id.in_(authorized_users))).all()
        # already_followed = []
        # for follow in following:
        #     already_followed.append(follow.following.id)
        #     if follow.following.id in already_followed:
        #         return Response(json.dumps({'message': 'already following user'}), mimetype="application/json", status=400)


        follow = Following(
            following_id = body.get('following_id'), 
            user_id = self.current_user.id
        )
        db.session.add(follow)
        db.session.commit()
        return Response(json.dumps(follow.to_dict_following()), mimetype="application/json", status=201)

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "following" record where "id"=id
        print(id)
        return Response(json.dumps({}), mimetype="application/json", status=200)




def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<int:id>', 
        '/api/following/<int:id>/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
